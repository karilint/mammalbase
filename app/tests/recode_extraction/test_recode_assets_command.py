import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from recode_extraction.adapters.assets import RecodeAssetManager, RecodeAssetPaths


class RecodeAssetsTests(SimpleTestCase):
    def _build_fixture_zip(self, root: Path) -> tuple[Path, str]:
        archive_path = root / 'recode.zip'
        with ZipFile(archive_path, 'w') as zip_file:
            zip_file.writestr(
                'recode/metadata.csv',
                'doc_id,title,authors,year\n'
                'DOC001,Spider paper,A. Author,2024\n'
                'DOC002,Insect paper,B. Author,2023\n',
            )
            zip_file.writestr('recode/araneae/all/wolfspider_DOC001.tsv', 'trait\tvalue\nsize\t12\n')
            zip_file.writestr('recode/insecta/annotator_jane/beetle_DOC002.tsv', 'trait\tvalue\nsize\t3\n')
            zip_file.writestr('recode/r/script_publish.R', 'print("ok")\n')
            zip_file.writestr('recode/plots/figure1.png', 'PNG')

        md5 = hashlib.md5(archive_path.read_bytes()).hexdigest()
        return archive_path, md5

    def test_md5_verification_and_unpack_and_index(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            archive_path, md5 = self._build_fixture_zip(root)

            paths = RecodeAssetPaths(
                root=root,
                archive_path=archive_path,
                unpacked_path=root / 'unpacked',
                index_path=root / 'index.json',
            )
            manager = RecodeAssetManager(paths)
            manager.ensure_directories()
            manager.verify_archive_md5(md5)
            manager.unpack_archive()
            entries = manager.build_index()

            assert (paths.unpacked_path / 'recode' / 'r' / 'script_publish.R').exists()
            assert (paths.unpacked_path / 'recode' / 'plots' / 'figure1.png').exists()
            assert len(entries) == 2

            by_doc = {entry['doc_id']: entry for entry in entries}
            assert by_doc['DOC001']['taxon_group'] == 'araneae'
            assert by_doc['DOC001']['annotator'] is None
            assert by_doc['DOC001']['focus_taxon'] == 'wolfspider'
            assert by_doc['DOC001']['metadata']['title'] == 'Spider paper'

            assert by_doc['DOC002']['taxon_group'] == 'insecta'
            assert by_doc['DOC002']['annotator'] == 'annotator_jane'
            assert by_doc['DOC002']['focus_taxon'] == 'beetle'
            assert by_doc['DOC002']['metadata']['year'] == '2023'

            written_index = json.loads(paths.index_path.read_text(encoding='utf-8'))
            assert len(written_index) == 2

    def test_md5_mismatch_raises(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            archive_path, _ = self._build_fixture_zip(root)
            paths = RecodeAssetPaths(
                root=root,
                archive_path=archive_path,
                unpacked_path=root / 'unpacked',
                index_path=root / 'index.json',
            )
            manager = RecodeAssetManager(paths)

            with self.assertRaises(ValueError):
                manager.verify_archive_md5('00000000000000000000000000000000')

    def test_management_command_skip_download(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self._build_fixture_zip(root)
            md5 = hashlib.md5((root / 'recode.zip').read_bytes()).hexdigest()

            call_command(
                'recode_fetch_assets',
                '--assets-root',
                str(root),
                '--skip-download',
                '--md5',
                md5,
            )

            index_path = root / 'index.json'
            assert index_path.exists()
            entries = json.loads(index_path.read_text(encoding='utf-8'))
            assert {entry['doc_id'] for entry in entries} == {'DOC001', 'DOC002'}

    def test_management_command_missing_archive_with_skip_download(self):
        with TemporaryDirectory() as tmp_dir:
            with self.assertRaises(CommandError):
                call_command('recode_fetch_assets', '--assets-root', tmp_dir, '--skip-download')

    @override_settings(RECODE_ASSETS_DIR='/tmp/recode-assets-default-test')
    def test_management_command_uses_recode_assets_dir_default(self):
        command = __import__('recode_extraction.management.commands.recode_fetch_assets', fromlist=['Command']).Command()
        parser = command.create_parser('manage.py', 'recode_fetch_assets')
        options = parser.parse_args([])
        self.assertEqual(options.assets_root, '/tmp/recode-assets-default-test')
