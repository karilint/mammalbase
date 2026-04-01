import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.cache import cache


@dataclass(slots=True)
class DocumentTextPackage:
    pages: list[dict[str, Any]]
    full_text: str
    extraction_warnings: list[str]
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'pages': self.pages,
            'full_text': self.full_text,
            'extraction_warnings': self.extraction_warnings,
            'backend': self.backend,
        }


class PdfToTextService:
    def __init__(self, prefer_system_tool: bool = False):
        self.prefer_system_tool = prefer_system_tool

    def extract(self, pdf_path: str | Path) -> dict[str, Any]:
        path = Path(pdf_path)
        cache_key = self._cache_key(path)
        cached_payload = cache.get(cache_key)
        if cached_payload is not None:
            return cached_payload

        backend = self._select_backend()

        if backend == 'pdftotext':
            package = self._extract_with_pdftotext(path)
        else:
            package = self._extract_with_pypdf(path)

        payload = package.to_dict()
        cache_timeout = max(int(getattr(settings, 'RECODE_TIMEOUT_SECONDS', 120)), 1)
        cache.set(cache_key, payload, timeout=cache_timeout)
        return payload

    def _cache_key(self, path: Path) -> str:
        stat = path.stat()
        return f'recode:pdf_text:{path}:{stat.st_mtime_ns}:{stat.st_size}'

    def _select_backend(self) -> str:
        if self.prefer_system_tool and shutil.which('pdftotext'):
            return 'pdftotext'

        try:
            import pypdf  # noqa: F401
            return 'pypdf'
        except ImportError:
            if shutil.which('pdftotext'):
                return 'pdftotext'
            raise RuntimeError('No PDF text backend available. Install pypdf or pdftotext.')

    def _extract_with_pypdf(self, pdf_path: Path) -> DocumentTextPackage:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        pages: list[dict[str, Any]] = []
        warnings: list[str] = []

        for index, page in enumerate(reader.pages, start=1):
            text = ''
            try:
                text = (page.extract_text() or '').strip()
            except Exception as exc:  # broad on purpose to collect warnings and continue
                warnings.append(f'pypdf failed on page {index}: {exc}')

            if not text:
                warnings.append(f'No text extracted on page {index}.')

            pages.append({'page_number': index, 'text': text})

        full_text = '\n\n'.join(page['text'] for page in pages).strip()
        return DocumentTextPackage(
            pages=pages,
            full_text=full_text,
            extraction_warnings=warnings,
            backend='pypdf',
        )

    def _extract_with_pdftotext(self, pdf_path: Path) -> DocumentTextPackage:
        warnings: list[str] = []

        cmd = [
            'pdftotext',
            '-enc',
            'UTF-8',
            '-layout',
            str(pdf_path),
            '-',
        ]

        timeout = max(int(getattr(settings, 'RECODE_TIMEOUT_SECONDS', 120)), 1)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            raise RuntimeError(f'pdftotext failed: {result.stderr.strip()}')

        raw_pages = [chunk for chunk in result.stdout.split('\f') if chunk is not None]
        pages: list[dict[str, Any]] = []
        for index, raw_page in enumerate(raw_pages, start=1):
            text = raw_page.strip()
            if not text:
                warnings.append(f'No text extracted on page {index}.')
            pages.append({'page_number': index, 'text': text})

        if not pages:
            warnings.append('pdftotext produced no page output.')

        full_text = '\n\n'.join(page['text'] for page in pages).strip()
        return DocumentTextPackage(
            pages=pages,
            full_text=full_text,
            extraction_warnings=warnings,
            backend='pdftotext',
        )



def serialize_text_package(package: dict[str, Any]) -> str:
    return json.dumps(package, ensure_ascii=False)
