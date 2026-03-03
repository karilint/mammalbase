from typing import Any


class EtsMapper:
    """Interface for mapping extracted candidates to ETS-like structures."""

    def map_candidates(self, extraction_payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Map model output into ETS-compatible dictionaries."""
        raise NotImplementedError
