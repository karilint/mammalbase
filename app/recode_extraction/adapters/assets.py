import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import requests


DEFAULT_RECODE_URL = 'https://zenodo.org/records/15254437/files/recode.zip?download=1'
DEFAULT_RECODE_MD5 = '6a371db866c1589d5711ac00797767ad'


@dataclass(slots=True)
class RecodeAssetPaths:
    root: Path
    archive_path: Path
    unpacked_path: Path
    index_path: Path


class RecodeAssetManager:
    _index_cache: dict[tuple[str, int], list[dict]] = {}

    def __init__(self, paths: RecodeAssetPaths):
        self.paths = paths

    def ensure_directories(self):
        self.paths.root.mkdir(parents=True, exist_ok=True)
        self.paths.unpacked_path.mkdir(parents=True, exist_ok=True)

    def download_archive(self, url: str = DEFAULT_RECODE_URL, chunk_size: int = 8192):
        response = requests.get(url, stream=True, timeout=(10, 300))
        response.raise_for_status()

        with self.paths.archive_path.open('wb') as out_file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    out_file.write(chunk)

    def compute_md5(self, file_path: Path | None = None) -> str:
        path = file_path or self.paths.archive_path
        md5 = hashlib.md5()
        with path.open('rb') as handle:
            while True:
                block = handle.read(1024 * 1024)
                if not block:
                    break
                md5.update(block)
        return md5.hexdigest()

    def verify_archive_md5(self, expected_md5: str = DEFAULT_RECODE_MD5):
        actual = self.compute_md5(self.paths.archive_path)
        if actual != expected_md5:
            raise ValueError(f'Recode asset checksum mismatch: expected {expected_md5}, got {actual}')

    def unpack_archive(self):
        with ZipFile(self.paths.archive_path, 'r') as zip_file:
            zip_file.extractall(self.paths.unpacked_path)

    def build_index(self) -> list[dict]:
        cached = self._get_cached_index()
        if cached is not None:
            return cached

        recode_root = self.paths.unpacked_path / 'recode'
        metadata_path = recode_root / 'metadata.csv'
        metadata_rows = self._read_metadata(metadata_path)
        metadata_lookup = self._build_metadata_lookup(metadata_rows)

        entries = []
        for taxon_group in ('araneae', 'insecta'):
            group_dir = recode_root / taxon_group
            if not group_dir.exists():
                continue

            for tsv_file in group_dir.rglob('*.tsv'):
                rel_parts = tsv_file.relative_to(group_dir).parts
                annotator = rel_parts[0] if rel_parts and rel_parts[0] != 'all' else None
                focus_taxon, doc_id = self._parse_filename(tsv_file.stem)
                metadata = metadata_lookup.get(doc_id) or metadata_lookup.get(tsv_file.stem) or {}

                entries.append({
                    'doc_id': doc_id,
                    'focus_taxon': focus_taxon,
                    'taxon_group': taxon_group,
                    'annotator': annotator,
                    'tsv_path': str(tsv_file.relative_to(self.paths.unpacked_path)),
                    'metadata': metadata,
                })

        entries.sort(key=lambda item: (item['taxon_group'], item['tsv_path']))

        with self.paths.index_path.open('w', encoding='utf-8') as index_file:
            json.dump(entries, index_file, indent=2, ensure_ascii=False)

        self._store_cached_index(entries)
        return entries

    def _get_cached_index(self) -> list[dict] | None:
        if not self.paths.index_path.exists():
            return None
        key = self._index_cache_key(self.paths.index_path)
        return self._index_cache.get(key)

    def _store_cached_index(self, entries: list[dict]):
        key = self._index_cache_key(self.paths.index_path)
        self._index_cache[key] = entries

    @staticmethod
    def _index_cache_key(index_path: Path) -> tuple[str, int]:
        stat = index_path.stat()
        return str(index_path.resolve()), stat.st_mtime_ns

    @staticmethod
    def _parse_filename(stem: str) -> tuple[str, str]:
        if '_' not in stem:
            return stem, stem
        parts = stem.split('_')
        return '_'.join(parts[:-1]), parts[-1]

    @staticmethod
    def _read_metadata(metadata_path: Path) -> list[dict]:
        if not metadata_path.exists():
            return []

        with metadata_path.open('r', encoding='utf-8') as metadata_file:
            return list(csv.DictReader(metadata_file))

    @staticmethod
    def _build_metadata_lookup(rows: list[dict]) -> dict[str, dict]:
        lookup = {}
        candidate_columns = ('doc_id', 'document_id', 'docid', 'id', 'file_id', 'filename')
        for row in rows:
            for column in candidate_columns:
                value = row.get(column)
                if value:
                    normalized = Path(value).stem if column == 'filename' else value
                    lookup[normalized] = row
        return lookup
