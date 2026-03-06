from __future__ import annotations

import re

DEFAULT_ABBR_MAP: dict[str, dict[str, str]] = {
    'BW': {'trait_name': 'Body Mass', 'unit': 'g'},
    'HB': {'trait_name': 'Head-Body Length', 'unit': 'mm'},
    'TL': {'trait_name': 'Tail Length', 'unit': 'mm'},
    'HF': {'trait_name': 'Hind Foot Length', 'unit': 'mm'},
    'EL': {'trait_name': 'Ear Length', 'unit': 'mm'},
    'TL/HB': {'trait_name': 'Tail-to-Body Length Ratio', 'unit': ''},
    'GLS': {'trait_name': 'Greatest Length of Skull', 'unit': 'mm'},
    'ZB': {'trait_name': 'Zygomatic Breadth', 'unit': 'mm'},
    'BH': {'trait_name': 'Braincase Height', 'unit': 'mm'},
    'UTL': {'trait_name': 'Upper Toothrow Length', 'unit': 'mm'},
    'UMRL': {'trait_name': 'Upper Molar Row Length', 'unit': 'mm'},
    'SBL': {'trait_name': 'Skull Basal Length', 'unit': 'mm'},
    'PL': {'trait_name': 'Palatal Length', 'unit': 'mm'},
    'IF': {'trait_name': 'Incisive Foramina Length', 'unit': 'mm'},
    'IOB': {'trait_name': 'Interorbital Breadth', 'unit': 'mm'},
    'LTL': {'trait_name': 'Lower Toothrow Length', 'unit': 'mm'},
    'LMRL': {'trait_name': 'Lower Molar Row Length', 'unit': 'mm'},
    'ML': {'trait_name': 'Mandibular Length', 'unit': 'mm'},
    'LAB': {'trait_name': 'Length of Auditory Bulla', 'unit': 'mm'},
    'FL': {'trait_name': 'Frontal Length', 'unit': 'mm'},
    'NL': {'trait_name': 'Nasal Length', 'unit': 'mm'},
    'HL': {'trait_name': 'Head Length', 'unit': 'mm'},
}

SPECIES_RE = re.compile(r'M\.\s*p\.\s*[A-Za-z\-]+')
MEAN_SD_RE = re.compile(r'(-?\d+(?:\.\d+)?)\s*±\s*(-?\d+(?:\.\d+)?)')
RANGE_WITH_N_RE = re.compile(r'(-?\d+(?:\.\d+)?)\s*[–-]\s*(-?\d+(?:\.\d+)?)\s*\((\d+)\)')


def extract_trait_records_from_measurement_tables(measurement_tables: list[str], abbr_dict: dict[str, dict]) -> list[dict]:
    records: list[dict] = []
    merged_abbr = {**DEFAULT_ABBR_MAP, **(abbr_dict or {})}
    abbrs = sorted(merged_abbr.keys(), key=len, reverse=True)

    for table_text in measurement_tables or []:
        species = _extract_species_list(table_text)
        for abbr, row_text in _split_rows(table_text, abbrs):
            mean_sd = MEAN_SD_RE.findall(row_text)
            ranges = RANGE_WITH_N_RE.findall(row_text)
            if not mean_sd and not ranges:
                continue
            trait_meta = merged_abbr.get(abbr, {'trait_name': abbr, 'unit': ''})
            for idx, sci_name in enumerate(species):
                n_val = int(ranges[idx][2]) if idx < len(ranges) else None
                if idx < len(mean_sd):
                    mean, sd = mean_sd[idx]
                    records.append(
                        {
                            'references': '',
                            'verbatimScientificName': sci_name,
                            'taxonRank': 'subspecies' if len(sci_name.split()) == 3 else 'species',
                            'verbatimTraitName': trait_meta.get('trait_name') or abbr,
                            'verbatimTraitUnit': trait_meta.get('unit') or '',
                            'individualCount': n_val,
                            'measurementValue_min': None,
                            'measurementValue_max': None,
                            'dispersion': float(sd),
                            'statisticalMethod': 'mean ± SD',
                            'verbatimTraitValue': f'{mean} ± {sd}',
                            'measurementRemarks': f'orig_abbr={abbr}',
                            'associatedReferences': 'Original study',
                        }
                    )
                if idx < len(ranges):
                    min_v, max_v, n = ranges[idx]
                    records.append(
                        {
                            'references': '',
                            'verbatimScientificName': sci_name,
                            'taxonRank': 'subspecies' if len(sci_name.split()) == 3 else 'species',
                            'verbatimTraitName': trait_meta.get('trait_name') or abbr,
                            'verbatimTraitUnit': trait_meta.get('unit') or '',
                            'individualCount': int(n),
                            'measurementValue_min': float(min_v),
                            'measurementValue_max': float(max_v),
                            'dispersion': None,
                            'statisticalMethod': 'range',
                            'verbatimTraitValue': f'{min_v}–{max_v}',
                            'measurementRemarks': f'orig_abbr={abbr}',
                            'associatedReferences': 'Original study',
                        }
                    )

    return _dedupe_records(records)


def _split_rows(table_text: str, abbrs: list[str]) -> list[tuple[str, str]]:
    text = re.sub(r'\s+', ' ', table_text or ' ').strip()
    for abbr in abbrs:
        text = re.sub(rf'(?<!\S){re.escape(abbr)}(?=\s)', f'\n{abbr}', text)
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(' ', 1)
        if len(parts) < 2:
            continue
        abbr = parts[0]
        if abbr not in abbrs:
            continue
        rows.append((abbr, parts[1]))
    return rows


def _extract_species_list(table_text: str) -> list[str]:
    short_names = []
    seen = set()
    for item in SPECIES_RE.findall(table_text or ''):
        cleaned = re.sub(r'\s+', ' ', item).strip().replace(' -', '-').replace('- ', '-')
        if cleaned not in seen:
            seen.add(cleaned)
            short_names.append(cleaned)
    expanded = [_expand_subspecies_name(name) for name in short_names]
    return expanded[:3]


def _expand_subspecies_name(short_name: str) -> str:
    m = re.match(r'M\.\s*p\.\s*([A-Za-z\-]+)', short_name)
    if m:
        return f"Mus pahari {m.group(1).lower()}"
    return short_name.replace('.', '').strip()


def _dedupe_records(records: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for rec in records:
        key = (
            rec.get('verbatimScientificName', ''),
            rec.get('verbatimTraitName', ''),
            rec.get('statisticalMethod', ''),
            rec.get('verbatimTraitValue', ''),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out
