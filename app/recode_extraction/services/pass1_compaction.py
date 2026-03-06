from __future__ import annotations

import re

EXCLUDE_PATTERNS = [
    r'\bprincipal\s+component\b',
    r'\bPCA\b',
    r'\bPC\d+\b',
    r'\beigenvalue',
    r'\bvariance\s+explained\b',
    r'\bK2P\b',
    r'\bgenetic\s+distance\b',
    r'\bphylogenetic\b',
    r'\bmtDNA\b',
    r'\bCyt\s*b\b',
    r'\bCO[ⅠI]\b',
]

TABLE_SIGNAL_PATTERNS = [
    r'\b(mm|cm|m|g|kg|mg)\b',
    r'\b(mean|sd|std|range|±)\b',
    r'\b(BW|HB|TL|HF|EL|GLS|ZB|BH|PL|NL|ML|UTL|LTL|UMRL|LMRL|IOB|LAB)\b',
]

SENTENCE_SIGNAL_PATTERNS = [
    r'\b(body|tail|head|cranial|skull|length|width|height|weight|morpholog|trait|diagnostic|subspecies)\w*\b',
    r'\b\d+(?:\.\d+)?\s*(mm|cm|m|g|kg|mg)\b',
    r'\b\d+(?:\.\d+)?\s*[–-]\s*\d+(?:\.\d+)?\b',
]


def compact_pass1_evidence(
    evidence: dict,
    *,
    max_items_per_bucket: int = 300,
    max_chars_per_item: int = 2500,
    max_table_chars_per_item: int = 50000,
) -> tuple[dict, dict]:
    compacted = {'measurement_tables': [], 'trait_sentences': [], 'trait_paragraphs': []}
    stats = {'removed': 0, 'kept': 0}

    for bucket in compacted:
        items = evidence.get(bucket, []) or []
        for item in items:
            item_max_chars = max_table_chars_per_item if bucket == 'measurement_tables' else max_chars_per_item
            normalized = _normalize_item(item, max_chars=item_max_chars)
            if not normalized:
                stats['removed'] += 1
                continue
            if _should_exclude(normalized):
                stats['removed'] += 1
                continue
            if bucket == 'measurement_tables' and not _has_any_signal(normalized, TABLE_SIGNAL_PATTERNS):
                stats['removed'] += 1
                continue
            if bucket in {'trait_sentences', 'trait_paragraphs'} and not _has_any_signal(normalized, SENTENCE_SIGNAL_PATTERNS):
                stats['removed'] += 1
                continue
            compacted[bucket].append(normalized)
            stats['kept'] += 1
            if len(compacted[bucket]) >= max_items_per_bucket:
                break

    return compacted, stats


def _normalize_item(text: str, *, max_chars: int) -> str:
    if not text:
        return ''
    cleaned = re.sub(r'\s+', ' ', text).strip()
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rstrip()
    return cleaned


def _has_any_signal(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _should_exclude(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in EXCLUDE_PATTERNS)
