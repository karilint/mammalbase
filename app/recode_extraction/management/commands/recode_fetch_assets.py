from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recode_extraction.adapters.assets import (
    DEFAULT_RECODE_MD5,
    DEFAULT_RECODE_URL,
    RecodeAssetManager,
    RecodeAssetPaths,
)


class Command(BaseCommand):
    help = 'Download, verify, unpack, and index RECODE assets from Zenodo.'

    def add_arguments(self, parser):
        parser.add_argument('--url', default=DEFAULT_RECODE_URL)
        parser.add_argument('--md5', default=DEFAULT_RECODE_MD5)
        parser.add_argument(
            '--assets-root',
            default=str(Path(settings.BASE_DIR) / 'var' / 'recode_assets'),
            help='Root directory for recode.zip, unpacked assets, and index.json',
        )
        parser.add_argument(
            '--skip-download',
            action='store_true',
            help='Skip download and use an existing archive at <assets-root>/recode.zip',
        )

    def handle(self, *args, **options):
        assets_root = Path(options['assets_root'])
        paths = RecodeAssetPaths(
            root=assets_root,
            archive_path=assets_root / 'recode.zip',
            unpacked_path=assets_root / 'unpacked',
            index_path=assets_root / 'index.json',
        )
        manager = RecodeAssetManager(paths)
        manager.ensure_directories()

        if not options['skip_download']:
            self.stdout.write(f"Downloading RECODE archive from {options['url']} ...")
            manager.download_archive(options['url'])
        elif not paths.archive_path.exists():
            raise CommandError(f'Archive not found: {paths.archive_path}')

        self.stdout.write('Verifying archive checksum ...')
        try:
            manager.verify_archive_md5(options['md5'])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write('Unpacking archive ...')
        manager.unpack_archive()

        self.stdout.write('Building index ...')
        entries = manager.build_index()

        self.stdout.write(self.style.SUCCESS(
            f'RECODE assets ready: archive={paths.archive_path}, unpacked={paths.unpacked_path}, '
            f'index={paths.index_path}, entries={len(entries)}'
        ))
