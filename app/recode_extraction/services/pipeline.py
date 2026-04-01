from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PipelineContext:
    """Input envelope for a RECODE extraction run."""

    upload_id: str
    pdf_path: Path
    actor_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineResult:
    """Output envelope for a RECODE extraction run."""

    upload_id: str
    persisted_record_ids: list[int] = field(default_factory=list)
    qc_summary: dict[str, Any] = field(default_factory=dict)


class ExtractionPipeline:
    """Contract for orchestrating the RECODE extraction pipeline.

    Planned stages:
    1) text extraction
    2) trait candidate extraction
    3) ETS mapping
    4) persistence
    5) quality control checks
    """

    def run(self, context: PipelineContext) -> PipelineResult:
        """Execute the extraction workflow for one uploaded PDF."""
        raise NotImplementedError
