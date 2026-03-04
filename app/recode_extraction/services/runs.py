from dataclasses import asdict
from datetime import datetime
from types import SimpleNamespace

from django.db import transaction
from django.utils import timezone

from imports.importers.ets_importer import EtsImporter
from imports.validation_lib.ets_validation import Ets_validation
from recode_extraction.mappers.ets import EtsMapper

from .extraction import ExtractionEngine
from .pdf_text import PdfToTextService
from .pipeline import PipelineContext
from ..models import (
    ExtractedAssertionModel,
    ExtractedEntity,
    SourceDocument,
    SourceExtractionRun,
)


DEFAULT_MODEL_VERSION = 'recode-v1-placeholder'
DEFAULT_ORCID = '0000-0000-0000-0000'


def create_extraction_run(
    source: SourceDocument,
    *,
    actor_id: int | None = None,
    dry_run: bool = False,
) -> SourceExtractionRun:
    """Create an extraction run, persist extracted entities/assertions, and optionally ETS rows."""
    context = PipelineContext(
        upload_id=str(source.pk),
        pdf_path=source.pdf_file.path,
        actor_id=actor_id,
        metadata={'source_document_id': source.pk, 'dry_run': dry_run},
    )

    run = SourceExtractionRun.objects.create(
        source=source,
        status=SourceExtractionRun.Status.RUNNING,
        model_version=DEFAULT_MODEL_VERSION,
        started_at=timezone.now(),
        parameters={
            'pipeline_context': {
                'upload_id': context.upload_id,
                'pdf_path': str(context.pdf_path),
                'actor_id': context.actor_id,
                'metadata': context.metadata,
            },
            'dry_run': dry_run,
        },
        logs='Extraction run started.',
    )

    try:
        package = PdfToTextService().extract(context.pdf_path)
        run.extracted_text_package = package

        assertions = ExtractionEngine().extract(package.get('full_text', ''))
        _persist_extracted_entities_and_assertions(run, assertions)

        mapper = EtsMapper()
        mapping_result = mapper.map_assertions(
            assertions,
            source_document=source,
            extraction_run=run,
            default_reference=_build_default_reference(source),
            default_author=DEFAULT_ORCID,
            page_number=1,
        )

        run.unmapped_traits = [
            {
                'trait_name': item.trait_name,
                'reason': item.reason,
                'assertion': asdict(item.assertion),
            }
            for item in mapping_result.unmapped_traits
        ]

        _attach_mapping_to_assertions(run, mapping_result.records, mapping_result.unmapped_traits)

        if not dry_run and mapping_result.records:
            _persist_ets_records_atomic(run, mapping_result.records)

        run.status = SourceExtractionRun.Status.COMPLETED
        run.logs = (
            f"Extraction completed. assertions={len(assertions)} "
            f"ets_records={len(mapping_result.records)} dry_run={dry_run}."
        )
    except Exception as exc:
        run.status = SourceExtractionRun.Status.FAILED
        run.logs = f'Pipeline failed: {exc}'
    finally:
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                'status',
                'logs',
                'finished_at',
                'extracted_text_package',
                'unmapped_traits',
            ]
        )

    return run


def _persist_extracted_entities_and_assertions(run: SourceExtractionRun, assertions):
    entity_rows = []
    assertion_rows = []

    for item in assertions:
        span = item.evidence_spans[0] if item.evidence_spans else None

        entity_rows.extend(
            [
                ExtractedEntity(
                    extraction_run=run,
                    entity_type=ExtractedEntity.EntityType.TAXON,
                    text=item.subject_taxon,
                    start_offset=None,
                    end_offset=None,
                    page_number=1,
                    confidence=item.confidence,
                ),
                ExtractedEntity(
                    extraction_run=run,
                    entity_type=ExtractedEntity.EntityType.TRAIT,
                    text=item.trait_name,
                    start_offset=span.start if span else None,
                    end_offset=span.end if span else None,
                    page_number=1,
                    confidence=item.confidence,
                ),
                ExtractedEntity(
                    extraction_run=run,
                    entity_type=ExtractedEntity.EntityType.VALUE,
                    text=item.value,
                    start_offset=span.start if span else None,
                    end_offset=span.end if span else None,
                    page_number=1,
                    confidence=item.confidence,
                ),
            ]
        )

        assertion_rows.append(
            ExtractedAssertionModel(
                extraction_run=run,
                subject_taxon=item.subject_taxon,
                trait_name=item.trait_name,
                value_raw=item.value,
                unit=item.unit or '',
                context=item.context,
                confidence=item.confidence,
                evidence_start=span.start if span else None,
                evidence_end=span.end if span else None,
                page_number=1,
            )
        )

    if entity_rows:
        ExtractedEntity.objects.bulk_create(entity_rows)
    if assertion_rows:
        ExtractedAssertionModel.objects.bulk_create(assertion_rows)


def _attach_mapping_to_assertions(run: SourceExtractionRun, records, unmapped_traits):
    assertions = list(run.assertions.all())
    # naive pairing by trait/value ordering (sufficient for current deterministic baseline output)
    for index, record in enumerate(records):
        if index >= len(assertions):
            break
        assertions[index].mapped_trait_id = record.get('traitID', '')
        assertions[index].ets_payload = record

    start = len(records)
    for offset, unmapped in enumerate(unmapped_traits):
        idx = start + offset
        if idx >= len(assertions):
            break
        assertions[idx].unmapped_reason = unmapped.reason

    if assertions:
        ExtractedAssertionModel.objects.bulk_update(
            assertions,
            ['mapped_trait_id', 'ets_payload', 'unmapped_reason'],
        )


def _persist_ets_records_atomic(run: SourceExtractionRun, records: list[dict]):
    with transaction.atomic():
        validator = Ets_validation()
        importer = EtsImporter()
        for record in records:
            errors = validator.validate(record, validator.rules)
            if errors:
                raise ValueError(f'ETS validation failed: {errors}')
            _persist_single_ets_record(importer, record)

        run.assertions.filter(mapped_trait_id__gt='').update(ets_persisted=True)


def _persist_single_ets_record(importer: EtsImporter, record: dict):
    importer.importRow(SimpleNamespace(**record))


def _build_default_reference(source: SourceDocument) -> str:
    year = source.year or datetime.now().year
    return f'{source.title} ({year}) automated extraction reference'
