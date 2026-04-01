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
MEAN_TOKEN_RE = re.compile(r'(-?\d+(?:\.\d+)?\s*±\s*-?\d+(?:\.\d+)?)|(-?\d+(?:\.\d+)?)')


def extract_trait_records_from_measurement_tables(measurement_tables: list[str], abbr_dict: dict[str, dict]) -> list[dict]:
    records: list[dict] = []
    merged_abbr = {**DEFAULT_ABBR_MAP, **(abbr_dict or {})}
    abbrs = sorted(merged_abbr.keys(), key=len, reverse=True)

    for table_text in measurement_tables or []:
        species = _extract_species_list(table_text)
        for abbr, row_text in _split_rows(table_text, abbrs):
            mean_values = _extract_mean_values(row_text, expected_count=len(species))
            ranges = RANGE_WITH_N_RE.findall(row_text)
            if not mean_values and not ranges:
                continue
            trait_meta = merged_abbr.get(abbr, {'trait_name': abbr, 'unit': ''})
            trait_name = _trait_name_with_abbr(trait_meta.get('trait_name') or abbr, abbr)
            for idx, sci_name in enumerate(species):
                mean_data = mean_values[idx] if idx < len(mean_values) else None
                range_data = ranges[idx] if idx < len(ranges) else None
                if not mean_data and not range_data:
                    continue

                method_parts = []
                mean_value = ''
                dispersion = None
                value_min = None
                value_max = None
                n_val = None

                if mean_data:
                    mean_value = str(mean_data['mean'])
                    sd = mean_data.get('sd')
                    if sd is not None:
                        dispersion = float(sd)
                        method_parts.append('mean ± SD')
                    else:
                        method_parts.append('mean')

                if range_data:
                    min_v, max_v, n = range_data
                    value_min = float(min_v)
                    value_max = float(max_v)
                    n_val = int(n)
                    method_parts.append('range')

                records.append(
                    {
                        'verbatimScientificName': sci_name,
                        'taxonRank': 'subspecies' if len(sci_name.split()) == 3 else 'species',
                        'verbatimTraitName': trait_name,
                        'verbatimTraitUnit': trait_meta.get('unit') or '',
                        'individualCount': n_val,
                        'measurementValue_min': value_min,
                        'measurementValue_max': value_max,
                        'dispersion': dispersion,
                        'statisticalMethod': ', '.join(method_parts),
                        'verbatimTraitValue': mean_value,
                        'measurementRemarks': '',
                        'associatedReferences': 'Original study',
                    }
                )

    return _dedupe_records(records)


def _trait_name_with_abbr(trait_name: str, abbr: str) -> str:
    trait_name = (trait_name or '').strip()
    if not trait_name:
        return abbr
    if f'({abbr})' in trait_name:
        return trait_name
    return f'{trait_name} ({abbr})'


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


def _extract_mean_values(row_text: str, *, expected_count: int) -> list[dict[str, str | None]]:
    if expected_count <= 0:
        return []
    first_range = RANGE_WITH_N_RE.search(row_text)
    prefix = row_text[:first_range.start()] if first_range else row_text
    values: list[dict[str, str | None]] = []
    for match in MEAN_TOKEN_RE.finditer(prefix):
        pair = match.group(1)
        single = match.group(2)
        if pair:
            pair_match = MEAN_SD_RE.match(pair)
            if pair_match:
                values.append({'mean': pair_match.group(1), 'sd': pair_match.group(2)})
        elif single is not None:
            values.append({'mean': single, 'sd': None})
        if len(values) >= expected_count:
            break
    return values


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
            rec.get('measurementValue_min'),
            rec.get('measurementValue_max'),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out
