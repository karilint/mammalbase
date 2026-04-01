from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from recode_extraction.services.openai_two_pass_prompts import (
    PASS1_SYSTEM_PROMPT,
    PASS2_SYSTEM_PROMPT,
    build_pass1_user_prompt,
    build_pass2_user_prompt,
)
if TYPE_CHECKING:
    from recode_extraction.services.trait_vocabulary import TraitVocabulary


class Pass1Evidence(BaseModel):
    model_config = ConfigDict(extra='forbid')
    measurement_tables: list[str] = Field(default_factory=list)
    trait_sentences: list[str] = Field(default_factory=list)
    trait_paragraphs: list[str] = Field(default_factory=list)


class TraitRecord(BaseModel):
    model_config = ConfigDict(extra='forbid')
    verbatimScientificName: str | None = None
    taxonRank: str | None = None
    verbatimTraitName: str | None = None
    verbatimTraitUnit: str | None = None
    individualCount: int | None = None
    measurementValue_min: float | None = None
    measurementValue_max: float | None = None
    dispersion: float | None = None
    statisticalMethod: str | None = None
    verbatimTraitValue: str | None = None
    sex: str | None = None
    lifeStage: str | None = None
    measurementMethod: str | None = None
    measurementRemarks: str | None = None
    measurementAccuracy: str | None = None
    measurementDeterminedBy: str | None = None
    verbatimLocality: str | None = None
    associatedReferences: str | None = None


class Pass2Metadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    citation: str | None = None
    author: str | None = None


class Pass2Output(BaseModel):
    model_config = ConfigDict(extra='forbid')
    metadata: Pass2Metadata = Field(default_factory=Pass2Metadata)
    traitRecords: list[TraitRecord] = Field(default_factory=list)


class OpenAITwoPassClient:
    def __init__(self, *, max_retries: int = 5):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.max_retries = max_retries

    def extract_pass1(self, page_text: str, *, model: str, vocab: 'TraitVocabulary', timeout_s: int, page_number: int = 0, run_id: int | None = None) -> Pass1Evidence:
        prompt = build_pass1_user_prompt(page_text, vocab.abbr_dict, vocab.trait_names, page_number)
        response = self._parse_with_retry(
            model=model,
            timeout_s=timeout_s,
            text_format=Pass1Evidence,
            input_payload=[
                {'role': 'system', 'content': PASS1_SYSTEM_PROMPT},
                {'role': 'user', 'content': f'run_id={run_id} page={page_number}\n{prompt}'},
            ],
        )
        return response.output_parsed

    def extract_pass2(self, evidence_json: dict, *, model: str, vocab: 'TraitVocabulary', timeout_s: int, run_id: int | None = None, citation: str = '', author_orcid: str = '') -> Pass2Output:
        prompt = build_pass2_user_prompt(evidence_json, vocab.abbr_dict, vocab.trait_names, citation=citation, author_orcid=author_orcid)
        response = self._parse_with_retry(
            model=model,
            timeout_s=timeout_s,
            text_format=Pass2Output,
            input_payload=[
                {'role': 'system', 'content': PASS2_SYSTEM_PROMPT},
                {'role': 'user', 'content': f'run_id={run_id}\n{prompt}'},
            ],
        )
        return response.output_parsed

    def _parse_with_retry(self, *, model: str, timeout_s: int, text_format: type[BaseModel], input_payload: list[dict]):
        for attempt in range(1, self.max_retries + 1):
            try:
                return self.client.responses.parse(
                    model=model,
                    input=input_payload,
                    text_format=text_format,
                    timeout=timeout_s,
                )
            except Exception:
                if attempt == self.max_retries:
                    raise
                time.sleep(min(2 ** (attempt - 1), 8))
