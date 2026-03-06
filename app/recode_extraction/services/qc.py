from __future__ import annotations

import hashlib
import re
from decimal import Decimal, InvalidOperation

from imports.validation_lib.ets_validation import Ets_validation

YEAR_RE = re.compile(r'.*([1-2][0-9]{3})')
SCI_NAME_RE = re.compile(r'\b([A-Z][a-z]+(?:\s+[a-z]{2,}){1,2})\b')


def normalize_and_validate_trait_records(pass2, *, run, default_reference: str, default_author_orcid: str):
    validator = Ets_validation()
    normalized_records = []
    top_errors: dict[str, int] = {}
    dedupe = set()
    full_text = ((run.extracted_text_package or {}).get('full_text') or '')
    name_candidates = set(SCI_NAME_RE.findall(full_text))

    for trait_record in pass2.traitRecords:
        raw = trait_record.model_dump(exclude_none=True)
        reference_value = _coalesce_reference(raw.get('references'), default_reference)
        scientific_name = _expand_scientific_name(raw.get('verbatimScientificName') or 'Unknown taxon', name_candidates)
        record = {
            'references': reference_value,
            'verbatimScientificName': scientific_name,
            'taxonRank': raw.get('taxonRank') or 'species',
            'verbatimTraitName': raw.get('verbatimTraitName') or '',
            'verbatimTraitUnit': raw.get('verbatimTraitUnit') or '',
            'individualCount': raw.get('individualCount') or 0,
            'measurementValue_min': raw.get('measurementValue_min') or 0,
            'measurementValue_max': raw.get('measurementValue_max') or 0,
            'dispersion': raw.get('dispersion') or 0,
            'statisticalMethod': raw.get('statisticalMethod') or '',
            'verbatimTraitValue': raw.get('verbatimTraitValue') or '',
            'sex': raw.get('sex') or 'nan',
            'lifeStage': raw.get('lifeStage') or 'nan',
            'measurementMethod': raw.get('measurementMethod') or 'OpenAI two-pass extraction',
            'measurementRemarks': raw.get('measurementRemarks') or '',
            'measurementAccuracy': raw.get('measurementAccuracy') or '',
            'measurementDeterminedBy': raw.get('measurementDeterminedBy') or 'OpenAI two-pass extraction',
            'verbatimLocality': raw.get('verbatimLocality') or '',
            'author': raw.get('author') or default_author_orcid,
            'associatedReferences': raw.get('associatedReferences') or 'Original study',
        }
        normalize_numeric_fields(record)

        key_input = f"{record['verbatimScientificName']}|{record['verbatimTraitName']}|{record['verbatimTraitValue']}|{record['verbatimTraitUnit']}"
        key_hash = hashlib.md5(key_input.encode('utf-8')).hexdigest()[:12]
        if key_hash in dedupe:
            continue
        dedupe.add(key_hash)

        page_match = re.search(r'page\s*=\s*(\d+)', record['measurementRemarks'], flags=re.IGNORECASE)
        page_token = f" page={page_match.group(1)}" if page_match else ''
        snippet = (record.get('measurementRemarks') or '')[:300]
        record['measurementRemarks'] = f"{snippet} candidate_key={key_hash} run_id={run.pk}{page_token}".strip()

        errors = validator.validate(record, validator.rules)
        record['_qc_errors'] = errors
        for error in errors:
            top_errors[error] = top_errors.get(error, 0) + 1
        normalized_records.append(record)

    qc_summary = {
        'total_records': len(normalized_records),
        'records_with_errors': sum(1 for r in normalized_records if r['_qc_errors']),
        'error_categories': top_errors,
    }
    return normalized_records, qc_summary


def _coalesce_reference(reference_value: str | None, default_reference: str) -> str:
    candidate = (reference_value or '').strip()
    if candidate and YEAR_RE.match(candidate):
        return candidate
    return default_reference


def _expand_scientific_name(name: str, candidates: set[str]) -> str:
    cleaned = (name or '').strip()
    if not cleaned:
        return 'Unknown taxon'
    if '.' not in cleaned:
        return cleaned
    tokens = cleaned.split()
    if len(tokens) < 2:
        return cleaned.replace('.', '')
    initials = [t[0].lower() for t in tokens[:-1]]
    epithet = tokens[-1].replace('.', '').lower()
    for candidate in sorted(candidates, key=len, reverse=True):
        cand_tokens = candidate.split()
        if len(cand_tokens) < len(tokens):
            continue
        if cand_tokens[-1].lower() != epithet:
            continue
        if [t[0].lower() for t in cand_tokens[: len(initials)]] == initials:
            return candidate
    return cleaned.replace('.', '')


def normalize_numeric_fields(record: dict):
    raw = (record.get('verbatimTraitValue') or '').strip()
    if not raw:
        return
    range_match = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*[\-–]\s*(-?\d+(?:\.\d+)?)', raw)
    if range_match:
        first = _to_decimal(range_match.group(1))
        second = _to_decimal(range_match.group(2))
        if first is not None and second is not None:
            record['measurementValue_min'] = float(min(first, second))
            record['measurementValue_max'] = float(max(first, second))
            record['statisticalMethod'] = 'range'
            return

    mean_sd = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*±\s*(-?\d+(?:\.\d+)?)\s*$', raw)
    if mean_sd:
        mean = _to_decimal(mean_sd.group(1))
        sd = _to_decimal(mean_sd.group(2))
        if mean is not None and sd is not None:
            record['measurementValue_min'] = float(mean)
            record['measurementValue_max'] = float(mean)
            record['dispersion'] = float(sd)
            record['statisticalMethod'] = 'mean ± SD'
            return

    number = _to_decimal(raw)
    if number is not None:
        value = float(number)
        record['measurementValue_min'] = value
        record['measurementValue_max'] = value
        record['statisticalMethod'] = record.get('statisticalMethod') or 'point estimate'


def _to_decimal(value: str):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None
