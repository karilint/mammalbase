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
    mapped_indices: list[tuple[int, dict[str, Any]]] = field(default_factory=list)
    unmapped_indices: list[tuple[int, str]] = field(default_factory=list)


class EtsMapper:
    """Map extracted assertions into MammalBase ETS import-like records."""

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

        for index, assertion in enumerate(assertions):
            record, error = self.map_single_assertion_data(
                subject_taxon=assertion.subject_taxon,
                trait_name=assertion.trait_name,
                value=assertion.value,
                unit=assertion.unit,
                context=assertion.context,
                confidence=assertion.confidence,
                evidence_offsets=[{'start': span.start, 'end': span.end} for span in assertion.evidence_spans],
                source_document_id=source_document.pk,
                extraction_run_id=extraction_run.pk,
                default_reference=default_reference,
                default_author=default_author,
                default_taxon_rank=default_taxon_rank,
                page_number=page_number,
            )
            if error:
                result.unmapped_traits.append(
                    UnmappedTrait(trait_name=assertion.trait_name, reason=error, assertion=assertion)
                )
                result.unmapped_indices.append((index, error))
                continue
            result.records.append(record)
            result.mapped_indices.append((index, record))

        return result

    def map_single_assertion_data(
        self,
        *,
        subject_taxon: str,
        trait_name: str,
        value: str,
        unit: str | None,
        context: str,
        confidence: float,
        evidence_offsets: list[dict[str, int]] | None,
        source_document_id: int,
        extraction_run_id: int,
        default_reference: str,
        default_author: str,
        default_taxon_rank: str = 'species',
        page_number: int | None = None,
        mapped_trait_id_override: str | None = None,
    ) -> tuple[dict[str, Any] | None, str | None]:
        trait_name_key = trait_name.strip().lower()
        mapped_trait_suggestion = mapped_trait_id_override or ''
        normalized = self._normalize_value(value)
        if not normalized['is_valid']:
            return None, f'invalid numeric value: {value}'

        normalized_unit = unit.strip().lower() if unit else None
        allowed_units = self.ALLOWED_UNITS_BY_TRAIT.get(trait_name_key, set())
        if normalized_unit and allowed_units and normalized_unit not in allowed_units:
            normalized_unit = None

        record = {
            'references': default_reference,
            'verbatimScientificName': subject_taxon,
            'taxonRank': default_taxon_rank,
            'verbatimTraitName': trait_name,
            'verbatimTraitUnit': normalized_unit or 'NA',
            'individualCount': normalized['individual_count'],
            'measurementValue_min': normalized['minimum'],
            'measurementValue_max': normalized['maximum'],
            'dispersion': normalized['dispersion'],
            'statisticalMethod': normalized['statistical_method'],
            'verbatimTraitValue': normalized['mean'],
            'sex': 'nan',
            'lifeStage': 'nan',
            'measurementMethod': 'Automated RECODE extraction',
            'measurementRemarks': f"confidence={confidence:.2f}",
            'measurementAccuracy': '',
            'measurementDeterminedBy': 'RECODE extraction engine',
            'verbatimLocality': '',
            'author': default_author,
            'associatedReferences': default_reference,
            'source_document_id': source_document_id,
            'mapped_trait_suggestion': mapped_trait_suggestion,
            'source_extraction_run_id': extraction_run_id,
            'evidence_snippet': context,
            'evidence_page_number': page_number,
            'evidence_offsets': evidence_offsets or [],
        }
        return record, None

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
