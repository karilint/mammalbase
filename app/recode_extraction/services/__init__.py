"""Service interfaces for RECODE extraction orchestration.

Keep this module lightweight to avoid import cycles.
"""

from .extraction import (
    BaselineRuleExtractor,
    EvidenceSpan,
    ExtractedAssertion,
    ExtractionEngine,
    LlmAssistedExtractor,
)
from .pdf_text import PdfToTextService
from .pipeline import (
    ExtractionPipeline,
    PipelineContext,
    PipelineResult,
)


def create_extraction_run(*args, **kwargs):
    from .runs import create_extraction_run as _create_extraction_run

    return _create_extraction_run(*args, **kwargs)


__all__ = [
    'BaselineRuleExtractor',
    'EvidenceSpan',
    'ExtractedAssertion',
    'ExtractionEngine',
    'ExtractionPipeline',
    'LlmAssistedExtractor',
    'PdfToTextService',
    'PipelineContext',
    'PipelineResult',
    'create_extraction_run',
]
