from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta

from django.core.cache import cache

from mb.models import MasterAttribute, SourceAttribute

CACHE_KEY = 'recode:trait_vocabulary:v1'
CACHE_TTL_SECONDS = int(timedelta(hours=6).total_seconds())
BOOTSTRAP_ABBREVIATIONS = [
    'BW', 'HB', 'TL', 'HF', 'EL', 'GLS', 'ZB', 'BH', 'PL', 'NL', 'ML', 'UTL', 'LTL', 'UMRL', 'LMRL', 'IOB', 'LAB'
]


@dataclass(slots=True)
class TraitVocabulary:
    abbr_dict: dict[str, dict]
    trait_names: list[str]


class TraitVocabularyService:
    def get_vocab(self) -> TraitVocabulary:
        cached = cache.get(CACHE_KEY)
        if cached:
            return cached

        abbr_dict = self._build_abbreviation_dictionary()
        trait_names = self._build_trait_names()
        if len(abbr_dict) < 20:
            for abbr in BOOTSTRAP_ABBREVIATIONS:
                abbr_dict.setdefault(abbr, {'trait_name': abbr, 'unit': ''})

        vocab = TraitVocabulary(abbr_dict=abbr_dict, trait_names=trait_names)
        cache.set(CACHE_KEY, vocab, CACHE_TTL_SECONDS)
        return vocab

    def _build_abbreviation_dictionary(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for row in MasterAttribute.objects.select_related('unit').only('name', 'unit__print_name'):
            self._extract_from_name(row.name, result, getattr(row.unit, 'print_name', '') or '')

        for name in SourceAttribute.objects.values_list('name', flat=True):
            cleaned = (name or '').strip()
            if cleaned and len(cleaned) <= 8 and cleaned.upper() == cleaned and cleaned.replace('-', '').isalpha():
                result.setdefault(cleaned, {'trait_name': cleaned, 'unit': ''})
            self._extract_from_name(cleaned, result, '')

        return result

    def _build_trait_names(self) -> list[str]:
        traits = list(
            MasterAttribute.objects.filter(entity__name__iexact='Taxon').values_list('name', flat=True).distinct()[:500]
        )
        source_traits = list(
            SourceAttribute.objects.filter(entity__name__iexact='Taxon').values_list('name', flat=True).distinct()[:300]
        )
        seen = set()
        merged = []
        for trait in [*traits, *source_traits]:
            if trait not in seen:
                seen.add(trait)
                merged.append(trait)
        return merged

    def _extract_from_name(self, name: str, output: dict[str, dict], unit: str):
        match = re.search(r'\(([^)]+)\)\s*$', name or '')
        if not match:
            return
        abbr = match.group(1).strip()
        if len(abbr) <= 12 and re.fullmatch(r'[A-Za-z][A-Za-z0-9\- ]*', abbr):
            output.setdefault(abbr, {'trait_name': re.sub(r'\s*\([^)]+\)\s*$', '', name).strip(), 'unit': unit})
