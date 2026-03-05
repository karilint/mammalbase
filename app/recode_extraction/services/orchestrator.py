from __future__ import annotations
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from imports.importers.ets_importer import EtsImporter
from recode_extraction.mappers.ets import EtsMapper
from recode_extraction.models import ExtractedAssertionModel, SourceDocument, SourceExtractionRun
from recode_extraction.services.baseline_spanrel_extractor import extract_spanrel
from recode_extraction.services.candidate_builder import build_graph, build_measurement_candidates
from recode_extraction.services.pdf_text import PdfToTextService
from recode_extraction.services.persistence import persist_parsed_doc


class RecodePipelineRunner:
    def run(self, source_document_id: int, run_params: dict | None = None) -> SourceExtractionRun:
        run_params = run_params or {}
        source = SourceDocument.objects.get(pk=source_document_id)
        run = SourceExtractionRun.objects.create(source=source, status='running', started_at=timezone.now())
        try:
            package = PdfToTextService().extract(source.pdf_file.path)
            run.extracted_text_package = package
            for page in package.get('pages', []):
                parsed = extract_spanrel(page.get('text', ''), page.get('page_number'))
                persist_parsed_doc(run, parsed, page_number=page.get('page_number'), snippet_source_text=page.get('text', '')[:500])

            graph = build_graph(run)
            candidates = build_measurement_candidates(graph, relation_config={})
            for cand in candidates:
                ExtractedAssertionModel.objects.create(
                    extraction_run=run,
                    subject_taxon=cand['species_text'],
                    trait_name=cand['trait_text'],
                    value_raw=cand['value_text'],
                    unit_text=cand.get('unit_text', ''),
                    unit=cand.get('unit_text', ''),
                    sex_text=cand.get('sex_text', ''),
                    lstage_text=cand.get('lstage_text', ''),
                    count_text=cand.get('count_text', ''),
                    page_number=cand.get('page_number'),
                    token_ids=cand.get('token_ids', []),
                    snippet=cand.get('snippet', ''),
                    status='pending',
                )

            run.status = 'succeeded'
            run.finished_at = timezone.now()
            run.save(update_fields=['status', 'finished_at', 'extracted_text_package'])
        except Exception as exc:
            run.status = 'failed'
            run.logs = str(exc)
            run.finished_at = timezone.now()
            run.save(update_fields=['status', 'logs', 'finished_at', 'extracted_text_package'])
        return run


def import_approved_candidates(run: SourceExtractionRun):
    mapper = EtsMapper()
    importer = EtsImporter()
    ref = f"{run.source.title} ({run.source.year or datetime.now().year}) automated extraction reference"
    with transaction.atomic():
        for cand in run.assertions.filter(status='approved'):
            payload = mapper.candidate_to_ets(
                {
                    'candidate_id': cand.pk,
                    'species_text': cand.subject_taxon,
                    'trait_text': cand.trait_name,
                    'value_text': cand.edited_value or cand.value_raw,
                    'unit_text': cand.edited_unit or cand.unit_text,
                    'sex_text': cand.sex_text,
                    'lstage_text': cand.lstage_text,
                    'token_ids': cand.token_ids,
                    'snippet': cand.snippet,
                    'page_number': cand.page_number,
                    'locality_text': cand.locality_text,
                },
                default_reference=ref,
                default_author='0000-0000-0000-0000',
                source_document_id=run.source_id,
                extraction_run_id=run.pk,
            )
            importer.importRow(type('Row', (), payload))
            cand.status = 'imported'
            cand.ets_payload = payload
            cand.ets_persisted = True
            cand.save(update_fields=['status', 'ets_payload', 'ets_persisted'])
