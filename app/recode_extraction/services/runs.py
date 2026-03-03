from .pdf_text import PdfToTextService
from .pipeline import PipelineContext
from ..models import SourceDocument, SourceExtractionRun


DEFAULT_MODEL_VERSION = 'recode-v1-placeholder'


def create_extraction_run(source: SourceDocument, *, actor_id: int | None = None) -> SourceExtractionRun:
    """Create an extraction run and persist the canonical text package."""
    context = PipelineContext(
        upload_id=str(source.pk),
        pdf_path=source.pdf_file.path,
        actor_id=actor_id,
        metadata={'source_document_id': source.pk},
    )

    run = SourceExtractionRun.objects.create(
        source=source,
        status=SourceExtractionRun.Status.RUNNING,
        model_version=DEFAULT_MODEL_VERSION,
        parameters={
            'pipeline_context': {
                'upload_id': context.upload_id,
                'pdf_path': str(context.pdf_path),
                'actor_id': context.actor_id,
                'metadata': context.metadata,
            }
        },
        logs='Extraction run started.',
    )

    service = PdfToTextService()
    try:
        package = service.extract(context.pdf_path)
        run.extracted_text_package = package
        warnings = package.get('extraction_warnings', [])
        run.logs = f"Text extraction completed with {len(warnings)} warning(s)."
        run.status = SourceExtractionRun.Status.COMPLETED
    except Exception as exc:
        run.logs = f'Text extraction failed: {exc}'
        run.status = SourceExtractionRun.Status.FAILED

    run.save(update_fields=['extracted_text_package', 'logs', 'status'])
    return run
