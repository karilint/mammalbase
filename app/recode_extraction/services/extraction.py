import re
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class EvidenceSpan:
    start: int
    end: int


@dataclass(slots=True)
class ExtractedAssertion:
    subject_taxon: str
    trait_name: str
    value: str
    unit: str | None
    context: str
    confidence: float
    evidence_spans: list[EvidenceSpan] = field(default_factory=list)


class ExtractionBackend(Protocol):
    def extract(self, text: str, *, subject_taxon: str | None = None) -> list[ExtractedAssertion]:
        ...


class BaselineRuleExtractor:
    TRAIT_PATTERNS = [
        (r'body mass\s*(?:is|was|=)?\s*(\d+(?:\.\d+)?)\s*(kg|g|mg)', 'body mass'),
        (r'adult mass\s*(?:is|was|=)?\s*(\d+(?:\.\d+)?)\s*(kg|g|mg)', 'adult mass'),
        (r'length\s*(?:is|was|=)?\s*(\d+(?:\.\d+)?)\s*(mm|cm|m)', 'length'),
        (r'litter size\s*(?:is|was|=)?\s*(\d+(?:\.\d+)?)', 'litter size'),
        (r'zygomatic breadth\s*(?:is|was|=)?\s*(\d+(?:\.\d+)?)\s*(mm|cm)', 'zygomatic breadth'),
        (r'dietary class\s*(?:is|was|=)?\s*([A-Za-z\- ]+)', 'dietary class'),
    ]

    TAXON_PATTERNS = [
        re.compile(r'\b([A-Z][a-z]+\s+[a-z]{2,})\b'),
    ]

    def extract(self, text: str, *, subject_taxon: str | None = None) -> list[ExtractedAssertion]:
        assertions: list[ExtractedAssertion] = []
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

        inferred_taxon = subject_taxon or self._infer_taxon(text)

        for sentence in sentences:
            for pattern, trait_name in self.TRAIT_PATTERNS:
                for match in re.finditer(pattern, sentence, flags=re.IGNORECASE):
                    value = match.group(1).strip()
                    unit = match.group(2).strip() if len(match.groups()) > 1 else None
                    if trait_name == 'dietary class' and unit:
                        value = f'{value} {unit}'.strip()
                        unit = None

                    sentence_start = text.find(sentence)
                    start = sentence_start + match.start() if sentence_start >= 0 else match.start()
                    end = sentence_start + match.end() if sentence_start >= 0 else match.end()

                    assertions.append(
                        ExtractedAssertion(
                            subject_taxon=inferred_taxon,
                            trait_name=trait_name,
                            value=value,
                            unit=unit,
                            context=sentence,
                            confidence=0.60,
                            evidence_spans=[EvidenceSpan(start=start, end=end)],
                        )
                    )

        return assertions

    def _infer_taxon(self, text: str) -> str:
        for pattern in self.TAXON_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return 'Unknown taxon'


class LlmAssistedExtractor:
    """Stub backend for future LLM extraction integration."""

    def extract(self, text: str, *, subject_taxon: str | None = None) -> list[ExtractedAssertion]:
        # Intentionally stubbed: integration should be configured via env and injected client.
        return []


class ExtractionEngine:
    def __init__(self, backend: ExtractionBackend | None = None):
        self.backend = backend or BaselineRuleExtractor()

    def extract(self, text: str, *, subject_taxon: str | None = None) -> list[ExtractedAssertion]:
        return self.backend.extract(text, subject_taxon=subject_taxon)
