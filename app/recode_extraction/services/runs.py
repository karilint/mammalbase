from .pipeline import PipelineContext
from ..models import SourceDocument, SourceExtractionRun


DEFAULT_MODEL_VERSION = 'recode-v1-placeholder'


def create_extraction_run(source: SourceDocument, *, actor_id: int | None = None) -> SourceExtractionRun:
    """Create a queued extraction run placeholder for a stored source document."""
    context = PipelineContext(
        upload_id=str(source.pk),
        pdf_path=source.pdf_file.path,
        actor_id=actor_id,
        metadata={'source_document_id': source.pk},
    )

    return SourceExtractionRun.objects.create(
        source=source,
        status=SourceExtractionRun.Status.QUEUED,
        model_version=DEFAULT_MODEL_VERSION,
        parameters={
            'pipeline_context': {
                'upload_id': context.upload_id,
                'pdf_path': str(context.pdf_path),
                'actor_id': context.actor_id,
                'metadata': context.metadata,
            }
        },
        logs='Extraction queued. Pipeline execution not implemented yet.',
    )
