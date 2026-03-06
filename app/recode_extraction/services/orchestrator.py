from dataclasses import asdict
from datetime import datetime
import time
from types import SimpleNamespace
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from imports.importers.ets_importer import EtsImporter
from imports.validation_lib.ets_validation import Ets_validation
from recode_extraction.adapters.openai_client import OpenAITwoPassClient
from recode_extraction.mappers.ets import EtsMapper
from recode_extraction.models import ExtractedAssertionModel, ExtractedEntity, SourceDocument, SourceExtractionRun
from recode_extraction.services.extraction import BaselineRuleExtractor, ExtractionEngine, LlmAssistedExtractor
from recode_extraction.services.pass1_compaction import compact_pass1_evidence
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

        perf: dict[str, float] = {}
        started = time.monotonic()
        try:
            self._update_stage(run, 'pdf_text_extraction', 20, 'Extracting text from PDF.')
            t0 = time.monotonic()
            package = PdfToTextService().extract(context.pdf_path)
            perf['pdf_text_extraction_s'] = round(time.monotonic() - t0, 3)
            run.extracted_text_package = package

            t0 = time.monotonic()
            if extraction_backend == 'openai_two_pass':
                self._run_openai_two_pass(run, source, package)
                perf['openai_two_pass_pipeline_s'] = round(time.monotonic() - t0, 3)
            else:
                self._run_legacy_pipeline(run, source, package, extraction_backend, confidence_threshold, dry_run)
                perf['legacy_pipeline_s'] = round(time.monotonic() - t0, 3)

            run.status = SourceExtractionRun.Status.COMPLETED
            run.current_stage = 'completed'
            run.progress_percent = 100
            perf['total_s'] = round(time.monotonic() - started, 3)
            timing_lines = '\n'.join(f'{k}={v}s' for k, v in sorted(perf.items()))
            run.logs = f'Run completed backend={extraction_backend} dry_run={dry_run}.\nTiming summary:\n{timing_lines}\n{run.logs}'
        except Exception as exc:
            run.status = SourceExtractionRun.Status.FAILED
            run.current_stage = 'failed'
            perf['total_s'] = round(time.monotonic() - started, 3)
            timing_lines = '\n'.join(f'{k}={v}s' for k, v in sorted(perf.items()))
            run.logs = f'Pipeline failed: {exc}\nTiming summary:\n{timing_lines}\n{run.logs}'
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

        pass1_total_start = time.monotonic()
        pass1_page_calls = 0
        pass1_page_failures = 0

        for page in package.get('pages', []):
            page_number = page.get('page_number')
            page_text = (page.get('text') or '')[:max_chars]
            try:
                pass1_page_calls += 1
                evidence = client.extract_pass1(
                    page_text,
                    model=settings.RECODE_OPENAI_MODEL_PASS1,
                    vocab=vocab,
                    timeout_s=settings.RECODE_OPENAI_TIMEOUT_SECONDS,
                    page_number=page_number,
                    run_id=run.pk,
                )
            except Exception as exc:
                pass1_page_failures += 1
                run.logs = f'{run.logs}\nPASS1 warning page={page_number}: {exc}'
                continue

            for key in merged:
                snippets = getattr(evidence, key, None)
                if snippets is None and isinstance(evidence, dict):
                    snippets = evidence.get(key)
                if not snippets:
                    continue
                for snippet in snippets:
                    prefixed = snippet if snippet.startswith('PAGE ') else f'PAGE {page_number}: {snippet}'
                    if prefixed not in seen[key]:
                        seen[key].add(prefixed)
                        merged[key].append(prefixed)

        pass1_elapsed = round(time.monotonic() - pass1_total_start, 3)

        compacted_evidence, compact_stats = compact_pass1_evidence(
            merged,
            max_items_per_bucket=getattr(settings, 'RECODE_OPENAI_PASS1_MAX_ITEMS_PER_BUCKET', 300),
            max_chars_per_item=getattr(settings, 'RECODE_OPENAI_PASS1_MAX_ITEM_CHARS', 2500),
            max_table_chars_per_item=getattr(settings, 'RECODE_OPENAI_PASS1_MAX_TABLE_ITEM_CHARS', 50000),
        )
        run.logs = (
            f"{run.logs}\nPASS1 kept={compact_stats['kept']} removed={compact_stats['removed']} "
            f"calls={pass1_page_calls} failures={pass1_page_failures} duration={pass1_elapsed}s"
        )
        run.pass1_evidence_package = compacted_evidence

        self._update_stage(run, 'ets_mapping', 70, 'OpenAI PASS2 ETS structuring + QC.')
        t0 = time.monotonic()
        pass2 = client.extract_pass2(
            compacted_evidence,
            model=settings.RECODE_OPENAI_MODEL_PASS2,
            vocab=vocab,
            timeout_s=settings.RECODE_OPENAI_TIMEOUT_SECONDS,
            run_id=run.pk,
        )
        run.pass2_structured_package = pass2.model_dump()
        pass2_elapsed = round(time.monotonic() - t0, 3)

        t0 = time.monotonic()
        normalized_records, qc_summary = normalize_and_validate_trait_records(
            pass2,
            run=run,
            default_reference=self._build_default_reference(source),
            default_author_orcid=DEFAULT_ORCID,
        )
        run.qc_summary = qc_summary
        qc_elapsed = round(time.monotonic() - t0, 3)

        t0 = time.monotonic()
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
        candidate_elapsed = round(time.monotonic() - t0, 3)
        run.logs = f"{run.logs}\nPASS2 duration={pass2_elapsed}s QC duration={qc_elapsed}s candidate_persist duration={candidate_elapsed}s"

    def _run_legacy_pipeline(self, run: SourceExtractionRun, source: SourceDocument, package: dict, extraction_backend: str, confidence_threshold: float, dry_run: bool):
        self._update_stage(run, 'information_extraction', 45, 'Extracting entities/assertions.')
        t0 = time.monotonic()
        extraction_engine = self._build_extraction_engine(extraction_backend)
        assertions = extraction_engine.extract(package.get('full_text', ''))
        assertions = [item for item in assertions if item.confidence >= confidence_threshold]
        self._persist_extracted_entities_and_assertions(run, assertions)
        extraction_elapsed = round(time.monotonic() - t0, 3)

        self._update_stage(run, 'ets_mapping', 70, 'Mapping assertions to ETS records.')
        t0 = time.monotonic()
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
        mapping_elapsed = round(time.monotonic() - t0, 3)

        if not dry_run and mapping_result.records:
            self._update_stage(run, 'ets_persistence', 90, 'Persisting ETS records.')
            t0 = time.monotonic()
            self._persist_ets_records_atomic(run, mapping_result.records)
            persistence_elapsed = round(time.monotonic() - t0, 3)
            run.logs = f"{run.logs}\nlegacy extraction={extraction_elapsed}s mapping={mapping_elapsed}s ets_persistence={persistence_elapsed}s"
        else:
            run.logs = f"{run.logs}\nlegacy extraction={extraction_elapsed}s mapping={mapping_elapsed}s"

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
        authors = (source.authors or 'Unknown').strip()
        title = (source.title or 'Untitled').strip().rstrip('.')
        return f'{authors}, {year}. {title}.'


def _extract_page_number(text: str):
    import re

    match = re.search(r'page\s*=\s*(\d+)', text or '', flags=re.IGNORECASE)
    return int(match.group(1)) if match else None
