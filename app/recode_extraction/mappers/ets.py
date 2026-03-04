from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from recode_extraction.models import SourceDocument, SourceExtractionRun


@dataclass(slots=True)
class UnmappedTrait:
    trait_name: str
    reason: str
    assertion: Any


@dataclass(slots=True)
class EtsMappingResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    unmapped_traits: list[UnmappedTrait] = field(default_factory=list)


class EtsMapper:
    """Map extracted assertions into MammalBase ETS import-like records."""

    TRAIT_ID_MAP = {
        'body mass': 'MB:TRAIT:BODY_MASS',
        'adult mass': 'MB:TRAIT:ADULT_MASS',
        'length': 'MB:TRAIT:LENGTH',
        'litter size': 'MB:TRAIT:LITTER_SIZE',
        'zygomatic breadth': 'MB:TRAIT:ZYGOMATIC_BREADTH',
        'dietary class': 'MB:TRAIT:DIETARY_CLASS',
    }

    ALLOWED_UNITS_BY_TRAIT = {
        'body mass': {'kg', 'g', 'mg'},
        'adult mass': {'kg', 'g', 'mg'},
        'length': {'m', 'cm', 'mm'},
        'zygomatic breadth': {'cm', 'mm'},
        'litter size': set(),
        'dietary class': set(),
    }


    def map_candidates(self, extraction_payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Backward-compatible interface from earlier scaffolding phases."""
        raise NotImplementedError('Use map_assertions(...) for ETS assertion mapping.')

    def map_assertions(
        self,
        assertions: list[Any],
        *,
        source_document: SourceDocument,
        extraction_run: SourceExtractionRun,
        default_reference: str,
        default_author: str,
        default_taxon_rank: str = 'species',
        page_number: int | None = None,
    ) -> EtsMappingResult:
        result = EtsMappingResult()

        for assertion in assertions:
            trait_name_key = assertion.trait_name.strip().lower()
            trait_id = self.TRAIT_ID_MAP.get(trait_name_key)
            if not trait_id:
                result.unmapped_traits.append(
                    UnmappedTrait(
                        trait_name=assertion.trait_name,
                        reason='unmapped trait_name',
                        assertion=assertion,
                    )
                )
                continue

            normalized = self._normalize_value(assertion.value)
            if not normalized['is_valid']:
                result.unmapped_traits.append(
                    UnmappedTrait(
                        trait_name=assertion.trait_name,
                        reason=f"invalid numeric value: {assertion.value}",
                        assertion=assertion,
                    )
                )
                continue

            unit = assertion.unit.strip().lower() if assertion.unit else None
            allowed_units = self.ALLOWED_UNITS_BY_TRAIT[trait_name_key]
            if unit and allowed_units and unit not in allowed_units:
                unit = None

            record = {
                # Existing ETS import path fields
                'references': default_reference,
                'verbatimScientificName': assertion.subject_taxon,
                'taxonRank': default_taxon_rank,
                'verbatimTraitName': assertion.trait_name,
                'verbatimTraitUnit': unit or 'NA',
                'individualCount': normalized['individual_count'],
                'measurementValue_min': normalized['minimum'],
                'measurementValue_max': normalized['maximum'],
                'dispersion': normalized['dispersion'],
                'statisticalMethod': normalized['statistical_method'],
                'verbatimTraitValue': normalized['mean'],
                'sex': 'nan',
                'lifeStage': 'nan',
                'measurementMethod': 'Automated RECODE extraction',
                'measurementRemarks': f"confidence={assertion.confidence:.2f}",
                'measurementAccuracy': '',
                'measurementDeterminedBy': 'RECODE extraction engine',
                'verbatimLocality': '',
                'author': default_author,
                'associatedReferences': default_reference,
                # ETS-ish trait definition mapping
                'traitID': trait_id,
                # provenance mapping
                'source_document_id': source_document.pk,
                'source_extraction_run_id': extraction_run.pk,
                'evidence_snippet': assertion.context,
                'evidence_page_number': page_number,
                'evidence_offsets': [
                    {'start': span.start, 'end': span.end} for span in assertion.evidence_spans
                ],
            }
            result.records.append(record)

        return result

    def _normalize_value(self, value: str) -> dict[str, Any]:
        raw = (value or '').strip()
        if not raw:
            return self._invalid_result()

        # mean ± sd
        if '±' in raw:
            mean_raw, sd_raw = [chunk.strip() for chunk in raw.split('±', maxsplit=1)]
            mean = self._to_decimal(mean_raw)
            sd = self._to_decimal(sd_raw)
            if mean is None or sd is None:
                return self._invalid_result()
            return {
                'is_valid': True,
                'minimum': float(mean),
                'maximum': float(mean),
                'mean': float(mean),
                'dispersion': float(sd),
                'statistical_method': 'mean ± sd',
                'individual_count': 0,
            }

        # numeric range min-max
        if '-' in raw:
            pieces = [piece.strip() for piece in raw.split('-', maxsplit=1)]
            first = self._to_decimal(pieces[0])
            second = self._to_decimal(pieces[1])
            if first is not None and second is not None:
                minimum = min(first, second)
                maximum = max(first, second)
                mean = (minimum + maximum) / Decimal('2')
                return {
                    'is_valid': True,
                    'minimum': float(minimum),
                    'maximum': float(maximum),
                    'mean': float(mean),
                    'dispersion': 0,
                    'statistical_method': 'range',
                    'individual_count': 0,
                }

        number = self._to_decimal(raw)
        if number is None:
            return self._invalid_result()

        return {
            'is_valid': True,
            'minimum': float(number),
            'maximum': float(number),
            'mean': float(number),
            'dispersion': 0,
            'statistical_method': 'point estimate',
            'individual_count': 0,
        }

    @staticmethod
    def _to_decimal(raw: str) -> Decimal | None:
        try:
            return Decimal(raw)
        except (InvalidOperation, TypeError):
            return None

    @staticmethod
    def _invalid_result() -> dict[str, Any]:
        return {
            'is_valid': False,
            'minimum': 0,
            'maximum': 0,
            'mean': 0,
            'dispersion': 0,
            'statistical_method': '',
            'individual_count': 0,
        }
