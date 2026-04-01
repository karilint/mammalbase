from recode_extraction.models import SourceDocument, SourceExtractionRun

from .orchestrator import RecodePipelineRunner


def create_extraction_run(
    source: SourceDocument,
    *,
    actor_id: int | None = None,
    dry_run: bool = False,
    extraction_backend: str = 'baseline',
    confidence_threshold: float = 0.0,
    mapping_version: str = 'v1',
    pass1_model: str | None = None,
    pass2_model: str | None = None,
) -> SourceExtractionRun:
    """Compatibility wrapper around the orchestrator."""
    return RecodePipelineRunner().run(
        source_document_id=source.pk,
        run_params={
            'actor_id': actor_id,
            'dry_run': dry_run,
            'extraction_backend': extraction_backend,
            'confidence_threshold': confidence_threshold,
            'mapping_version': mapping_version,
            'pass1_model': pass1_model,
            'pass2_model': pass2_model,
        },
    )
