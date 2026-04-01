from celery import shared_task

from recode_extraction.services.orchestrator import RecodePipelineRunner


@shared_task
def run_recode_pipeline(source_document_id: int, run_params: dict | None = None) -> int:
    run = RecodePipelineRunner().run(source_document_id=source_document_id, run_params=run_params or {})
    return run.pk
