from __future__ import annotations
from celery import shared_task

from recode_extraction.models import SourceExtractionRun
from recode_extraction.services.orchestrator import RecodePipelineRunner


@shared_task(bind=True, autoretry_for=(OSError, RuntimeError), retry_backoff=True, retry_kwargs={'max_retries': 3})
def recode_extract_pdf(self, run_id: int):
    run = SourceExtractionRun.objects.get(pk=run_id)
    run.status = 'running'
    run.save(update_fields=['status'])
    result = RecodePipelineRunner().run(run.source_id, run_params={})
    return result.pk


@shared_task(bind=True)
def run_recode_pipeline(self, source_document_id: int, run_params: dict | None = None):
    return RecodePipelineRunner().run(source_document_id, run_params or {}).pk
