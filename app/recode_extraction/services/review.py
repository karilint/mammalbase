import csv
import re
from io import StringIO
from types import SimpleNamespace

from django.db import connection, transaction
from django.utils import timezone

from imports.importers.ets_importer import EtsImporter
from imports.validation_lib.ets_validation import Ets_validation
from recode_extraction.mappers.ets import EtsMapper
from recode_extraction.models import ExtractedAssertionModel, SourceExtractionRun
from recode_extraction.services.qc import (
    _coalesce_reference,
    _infer_taxon_rank,
    _normalize_associated_reference,
    _normalize_scientific_name_text,
    normalize_numeric_fields,
)

DEFAULT_ORCID = '0000-0000-0000-0000'



def _ensure_review_columns_exist():
    table = ExtractedAssertionModel._meta.db_table
    with connection.cursor() as cursor:
        columns = {c.name for c in connection.introspection.get_table_description(cursor, table)}
    if 'review_status' not in columns:
        raise ValueError('Missing recode review columns (review_status). Please run database migrations for recode_extraction.')

def apply_assertion_review(assertion: ExtractedAssertionModel, *, reviewer, review_status: str, edited_value: str = '', edited_unit: str = '', mapped_trait_id: str = '', reviewer_note: str = ''):
    _ensure_review_columns_exist()
    assertion.review_status = review_status
    if edited_value:
        assertion.edited_value = edited_value
    if edited_unit:
        assertion.edited_unit = edited_unit
    if mapped_trait_id:
        assertion.mapped_trait_id = mapped_trait_id
    if reviewer_note:
        assertion.reviewer_note = reviewer_note
    assertion.reviewed_by = reviewer
    assertion.reviewed_at = timezone.now()
    assertion.save(update_fields=['review_status', 'edited_value', 'edited_unit', 'mapped_trait_id', 'reviewer_note', 'reviewed_by', 'reviewed_at'])


def bulk_approve_above_threshold(run: SourceExtractionRun, *, reviewer, threshold: float):
    _ensure_review_columns_exist()
    assertions = run.assertions.filter(confidence__gte=threshold, review_status=ExtractedAssertionModel.ReviewStatus.PENDING)
    now = timezone.now()
    assertions.update(review_status=ExtractedAssertionModel.ReviewStatus.APPROVED, reviewed_by=reviewer, reviewed_at=now)


def persist_approved_assertions_to_ets(run: SourceExtractionRun):
    _ensure_review_columns_exist()
    mapper = EtsMapper()
    validator = Ets_validation()
    importer = EtsImporter()

    approved = run.assertions.filter(review_status=ExtractedAssertionModel.ReviewStatus.APPROVED, ets_persisted=False)

    with transaction.atomic():
        for assertion in approved:
            stored_payload = assertion.ets_payload or (
                ExtractedAssertionModel.objects
                .filter(pk=assertion.pk)
                .values_list('ets_payload', flat=True)
                .first()
                or {}
            )
            if stored_payload:
                record = dict(stored_payload)
                if assertion.edited_value:
                    record['verbatimTraitValue'] = assertion.edited_value
                if assertion.edited_unit:
                    record['verbatimTraitUnit'] = assertion.edited_unit
                _normalize_prefilled_record(record, run)
                normalize_numeric_fields(record)
            else:
                value = assertion.edited_value or assertion.value_raw
                unit = assertion.edited_unit or assertion.unit
                offsets = []
                if assertion.evidence_start is not None and assertion.evidence_end is not None:
                    offsets = [{'start': assertion.evidence_start, 'end': assertion.evidence_end}]

                record, error = mapper.map_single_assertion_data(
                    subject_taxon=assertion.subject_taxon,
                    trait_name=assertion.trait_name,
                    value=value,
                    unit=unit,
                    context=assertion.context,
                    confidence=assertion.confidence,
                    evidence_offsets=offsets,
                    source_document_id=run.source_id,
                    extraction_run_id=run.pk,
                    default_reference=_build_default_reference(run),
                    default_author=DEFAULT_ORCID,
                    page_number=assertion.page_number,
                    mapped_trait_id_override=assertion.mapped_trait_id or None,
                )
                if error:
                    raise ValueError(error)

            validation_errors = validator.validate(record, validator.rules)
            if validation_errors:
                raise ValueError(f'ETS validation failed: {validation_errors}')

            importer.importRow(SimpleNamespace(**record))
            assertion.ets_payload = record
            assertion.ets_persisted = True
            assertion.save(update_fields=['ets_payload', 'ets_persisted'])


def export_assertions_csv(run: SourceExtractionRun, queryset=None) -> str:
    queryset = queryset or run.assertions.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'subject_taxon', 'trait_name', 'value_raw', 'edited_value', 'unit', 'edited_unit', 'confidence', 'page_number', 'review_status', 'ets_persisted', 'mapped_trait_id', 'unmapped_reason', 'context'])

    for item in queryset:
        writer.writerow([item.pk, item.subject_taxon, item.trait_name, item.value_raw, item.edited_value, item.unit, item.edited_unit, item.confidence, item.page_number, item.review_status, item.ets_persisted, item.mapped_trait_id, item.unmapped_reason, item.context])
    return output.getvalue()


def _build_default_reference(run: SourceExtractionRun) -> str:
    return (run.source.citation or '').strip() or run.source.build_citation()


def _normalize_prefilled_record(record: dict, run: SourceExtractionRun):
    default_reference = _build_default_reference(run)
    scientific_name = _normalize_scientific_name_text(record.get('verbatimScientificName') or '')
    record['verbatimScientificName'] = scientific_name
    inferred_taxon_rank = _infer_taxon_rank(scientific_name)
    raw_taxon_rank = (record.get('taxonRank') or '').strip()
    record['taxonRank'] = inferred_taxon_rank if inferred_taxon_rank == 'subspecies' else (raw_taxon_rank or inferred_taxon_rank)

    reference_value = _coalesce_reference(record.get('references') or default_reference)
    if not re.search(r'([1-2][0-9]{3})', reference_value):
        reference_value = default_reference
    record['references'] = reference_value

    author = (record.get('author') or DEFAULT_ORCID)
    if not isinstance(author, str) or not author.strip():
        author = DEFAULT_ORCID
    record['author'] = author.strip()

    record['associatedReferences'] = _normalize_associated_reference(record.get('associatedReferences'))

