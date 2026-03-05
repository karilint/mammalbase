from dataclasses import asdict
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from imports.importers.ets_importer import EtsImporter
from imports.validation_lib.ets_validation import Ets_validation
from recode_extraction.adapters.openai_client import OpenAITwoPassClient, Pass1Evidence
from recode_extraction.mappers.ets import EtsMapper
from recode_extraction.models import ExtractedAssertionModel, ExtractedEntity, SourceDocument, SourceExtractionRun
from recode_extraction.services.extraction import BaselineRuleExtractor, ExtractionEngine, LlmAssistedExtractor
from recode_extraction.services.pdf_text import PdfToTextService
from recode_extraction.services.pipeline import PipelineContext
from recode_extraction.services.qc import normalize_and_validate_trait_records
from recode_extraction.services.trait_vocabulary import TraitVocabularyService

DEFAULT_MODEL_VERSION = 'recode-v1-placeholder'
DEFAULT_ORCID = '0000-0000-0000-0000'
DEFAULT_MAPPING_VERSION = 'v1'


class RecodePipelineRunner:
    def run(self, source_document_id: int, run_params: dict[str, Any] | None = None) -> SourceExtractionRun:
        run_params = run_params or {}
        source = SourceDocument.objects.get(pk=source_document_id)
        actor_id = run_params.get('actor_id')
        dry_run = bool(run_params.get('dry_run', False))
        extraction_backend = run_params.get('extraction_backend', 'baseline')
        confidence_threshold = float(run_params.get('confidence_threshold', 0.0))
        mapping_version = run_params.get('mapping_version', DEFAULT_MAPPING_VERSION)

        context = PipelineContext(upload_id=str(source.pk), pdf_path=source.pdf_file.path, actor_id=actor_id, metadata={'source_document_id': source.pk, 'dry_run': dry_run})

        run = SourceExtractionRun.objects.create(
            source=source,
            status=SourceExtractionRun.Status.RUNNING,
            current_stage='initializing',
            progress_percent=0,
            model_version=DEFAULT_MODEL_VERSION,
            started_at=timezone.now(),
            parameters={
                'pipeline_context': {'upload_id': context.upload_id, 'pdf_path': str(context.pdf_path), 'actor_id': context.actor_id, 'metadata': context.metadata},
                'dry_run': dry_run,
                'extraction_backend': extraction_backend,
                'confidence_threshold': confidence_threshold,
                'mapping_version': mapping_version,
            },
            logs='Run initialized.',
        )

        try:
            self._update_stage(run, 'pdf_text_extraction', 20, 'Extracting text from PDF.')
            package = PdfToTextService().extract(context.pdf_path)
            run.extracted_text_package = package

            if extraction_backend == 'openai_two_pass':
                self._run_openai_two_pass(run, source, package)
            else:
                self._run_legacy_pipeline(run, source, package, extraction_backend, confidence_threshold, dry_run)

            run.status = SourceExtractionRun.Status.COMPLETED
            run.current_stage = 'completed'
            run.progress_percent = 100
            run.logs = f'Run completed backend={extraction_backend} dry_run={dry_run}.'
        except Exception as exc:
            run.status = SourceExtractionRun.Status.FAILED
            run.current_stage = 'failed'
            run.logs = f'Pipeline failed: {exc}'
        finally:
            run.finished_at = timezone.now()
            run.save()

        return run

    def _run_openai_two_pass(self, run: SourceExtractionRun, source: SourceDocument, package: dict):
        if not settings.RECODE_ENABLE_OPENAI_BACKEND:
            raise ValueError('OpenAI extraction backend is disabled by RECODE_ENABLE_OPENAI_BACKEND=0.')

        self._update_stage(run, 'information_extraction', 45, 'OpenAI PASS1 evidence detection.')
        vocab = TraitVocabularyService().get_vocab()
        client = OpenAITwoPassClient(max_retries=settings.RECODE_OPENAI_MAX_RETRIES)
        max_chars = settings.RECODE_OPENAI_MAX_PAGE_CHARS

        merged = {'measurement_tables': [], 'trait_sentences': [], 'trait_paragraphs': []}
        seen = {k: set() for k in merged}

        for page in package.get('pages', []):
            page_number = page.get('page_number')
            page_text = (page.get('text') or '')[:max_chars]
            try:
                evidence = client.extract_pass1(
                    page_text,
                    model=settings.RECODE_OPENAI_MODEL_PASS1,
                    vocab=vocab,
                    timeout_s=settings.RECODE_OPENAI_TIMEOUT_SECONDS,
                    page_number=page_number,
                    run_id=run.pk,
                )
            except Exception as exc:
                run.logs = f'{run.logs}\nPASS1 warning page={page_number}: {exc}'
                continue

            if not isinstance(evidence, Pass1Evidence):
                continue
            for key in merged:
                for snippet in getattr(evidence, key):
                    prefixed = snippet if snippet.startswith('PAGE ') else f'PAGE {page_number}: {snippet}'
                    if prefixed not in seen[key]:
                        seen[key].add(prefixed)
                        merged[key].append(prefixed)

        run.pass1_evidence_package = merged

        self._update_stage(run, 'ets_mapping', 70, 'OpenAI PASS2 ETS structuring + QC.')
        pass2 = client.extract_pass2(
            merged,
            model=settings.RECODE_OPENAI_MODEL_PASS2,
            vocab=vocab,
            timeout_s=settings.RECODE_OPENAI_TIMEOUT_SECONDS,
            run_id=run.pk,
        )
        run.pass2_structured_package = pass2.model_dump()

        normalized_records, qc_summary = normalize_and_validate_trait_records(
            pass2,
            run=run,
            default_reference=self._build_default_reference(source),
            default_author_orcid=DEFAULT_ORCID,
        )
        run.qc_summary = qc_summary

        for record in normalized_records:
            page_number = _extract_page_number(record.get('measurementRemarks', ''))
            errors = record.pop('_qc_errors', [])
            confidence = 0.8 if not errors else 0.4
            ExtractedAssertionModel.objects.create(
                extraction_run=run,
                subject_taxon=record.get('verbatimScientificName', ''),
                trait_name=record.get('verbatimTraitName', ''),
                value_raw=str(record.get('verbatimTraitValue', '')),
                unit=record.get('verbatimTraitUnit', '') or '',
                context=(record.get('measurementRemarks', '') or '')[:300],
                page_number=page_number,
                confidence=confidence,
                ets_payload=record,
                review_status=ExtractedAssertionModel.ReviewStatus.PENDING,
                ets_persisted=False,
                unmapped_reason='; '.join(errors),
                qc_errors=errors,
            )

    def _run_legacy_pipeline(self, run: SourceExtractionRun, source: SourceDocument, package: dict, extraction_backend: str, confidence_threshold: float, dry_run: bool):
        self._update_stage(run, 'information_extraction', 45, 'Extracting entities/assertions.')
        extraction_engine = self._build_extraction_engine(extraction_backend)
        assertions = extraction_engine.extract(package.get('full_text', ''))
        assertions = [item for item in assertions if item.confidence >= confidence_threshold]
        self._persist_extracted_entities_and_assertions(run, assertions)

        self._update_stage(run, 'ets_mapping', 70, 'Mapping assertions to ETS records.')
        mapper = EtsMapper()
        mapping_result = mapper.map_assertions(
            assertions,
            source_document=source,
            extraction_run=run,
            default_reference=self._build_default_reference(source),
            default_author=DEFAULT_ORCID,
            page_number=1,
        )

        run.unmapped_traits = [{'trait_name': item.trait_name, 'reason': item.reason, 'assertion': asdict(item.assertion)} for item in mapping_result.unmapped_traits]
        self._attach_mapping_to_assertions(run, mapping_result)

        if not dry_run and mapping_result.records:
            self._update_stage(run, 'ets_persistence', 90, 'Persisting ETS records.')
            self._persist_ets_records_atomic(run, mapping_result.records)

    def _build_extraction_engine(self, extraction_backend: str) -> ExtractionEngine:
        if extraction_backend == 'baseline':
            return ExtractionEngine(backend=BaselineRuleExtractor())
        if extraction_backend == 'llm':
            if not settings.RECODE_ENABLE_LLM_BACKEND:
                raise ValueError('LLM extraction backend is disabled by RECODE_ENABLE_LLM_BACKEND=0.')
            return ExtractionEngine(backend=LlmAssistedExtractor())
        raise ValueError(f"Unsupported extraction backend '{extraction_backend}'.")

    def _update_stage(self, run: SourceExtractionRun, stage: str, progress_percent: int, log_message: str):
        run.current_stage = stage
        run.progress_percent = progress_percent
        run.logs = log_message
        run.save(update_fields=['current_stage', 'progress_percent', 'logs'])

    def _persist_extracted_entities_and_assertions(self, run: SourceExtractionRun, assertions):
        entity_rows, assertion_rows = [], []
        for item in assertions:
            span = item.evidence_spans[0] if item.evidence_spans else None
            page_number = getattr(item, 'page_number', None) or 1
            entity_rows.extend([
                ExtractedEntity(extraction_run=run, entity_type=ExtractedEntity.EntityType.TAXON, text=item.subject_taxon, page_number=page_number, confidence=item.confidence),
                ExtractedEntity(extraction_run=run, entity_type=ExtractedEntity.EntityType.TRAIT, text=item.trait_name, start_offset=span.start if span else None, end_offset=span.end if span else None, page_number=page_number, confidence=item.confidence),
                ExtractedEntity(extraction_run=run, entity_type=ExtractedEntity.EntityType.VALUE, text=item.value, start_offset=span.start if span else None, end_offset=span.end if span else None, page_number=page_number, confidence=item.confidence),
            ])
            assertion_rows.append(ExtractedAssertionModel(extraction_run=run, subject_taxon=item.subject_taxon, trait_name=item.trait_name, value_raw=item.value, unit=item.unit or '', context=item.context, confidence=item.confidence, evidence_start=span.start if span else None, evidence_end=span.end if span else None, page_number=page_number))

        if entity_rows:
            ExtractedEntity.objects.bulk_create(entity_rows)
        if assertion_rows:
            ExtractedAssertionModel.objects.bulk_create(assertion_rows)

    def _attach_mapping_to_assertions(self, run: SourceExtractionRun, mapping_result):
        assertions = list(run.assertions.all())
        for index, record in mapping_result.mapped_indices:
            if index < len(assertions):
                assertions[index].mapped_trait_id = record.get('mapped_trait_suggestion', '')
                assertions[index].ets_payload = record
        for index, reason in mapping_result.unmapped_indices:
            if index < len(assertions):
                assertions[index].unmapped_reason = reason
        if assertions:
            ExtractedAssertionModel.objects.bulk_update(assertions, ['mapped_trait_id', 'ets_payload', 'unmapped_reason'])

    def _persist_ets_records_atomic(self, run: SourceExtractionRun, records: list[dict]):
        with transaction.atomic():
            validator = Ets_validation()
            importer = EtsImporter()
            for record in records:
                errors = validator.validate(record, validator.rules)
                if errors:
                    raise ValueError(f'ETS validation failed: {errors}')
                importer.importRow(SimpleNamespace(**record))
            run.assertions.filter(mapped_trait_id__gt='').update(ets_persisted=True)

    def _build_default_reference(self, source: SourceDocument) -> str:
        year = source.year or datetime.now().year
        return f'{source.title} ({year}) automated extraction reference'


def _extract_page_number(text: str):
    import re

    match = re.search(r'page\s*=\s*(\d+)', text or '', flags=re.IGNORECASE)
    return int(match.group(1)) if match else None
