from pathlib import Path
from typing import Any


class CorpusAssetAdapter:
    """Interface for loading RECODE corpus and model resources."""

    def load_corpus(self) -> Any:
        """Return a loaded corpus object used by candidate extraction."""
        raise NotImplementedError

    def resolve_model_path(self) -> Path:
        """Return the filesystem path to the selected extraction model assets."""
        raise NotImplementedError
