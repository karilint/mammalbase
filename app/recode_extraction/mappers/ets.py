from __future__ import annotations
from django.conf import settings


class EtsMapper:
    LEGACY_TRAIT_ID_MAP = {
        'body mass': 'T:body_mass',
    }

    def candidate_to_ets(self, candidate: dict, *, default_reference: str, default_author: str, source_document_id: int, extraction_run_id: int) -> dict:
        trait_text = candidate.get('trait_text', '')
        mapped = ''
        if getattr(settings, 'RECODE_ENABLE_LEGACY_TRAIT_MAP', False):
            mapped = self.LEGACY_TRAIT_ID_MAP.get(trait_text.strip().lower(), '')

        snippet = (candidate.get('snippet') or '')[:500]
        remarks = (
            f"candidate_id={candidate.get('candidate_id','')} "
            f"page={candidate.get('page_number')} "
            f"token_ids={candidate.get('token_ids', [])} "
            f"snippet={snippet}"
        )
        return {
            'references': default_reference,
            'verbatimScientificName': candidate.get('species_text', ''),
            'taxonRank': 'species',
            'verbatimTraitName': trait_text,
            'verbatimTraitUnit': candidate.get('unit_text') or 'NA',
            'individualCount': 0,
            'measurementValue_min': float(candidate.get('value_text') or 0),
            'measurementValue_max': float(candidate.get('value_text') or 0),
            'dispersion': 0,
            'statisticalMethod': 'point estimate',
            'verbatimTraitValue': candidate.get('value_text') or candidate.get('traitval_text', ''),
            'sex': candidate.get('sex_text') or 'nan',
            'lifeStage': candidate.get('lstage_text') or 'nan',
            'measurementMethod': 'RECODE NE/RE graph extraction',
            'measurementRemarks': remarks,
            'measurementAccuracy': '',
            'measurementDeterminedBy': 'RECODE extraction engine',
            'verbatimLocality': candidate.get('locality_text', ''),
            'author': default_author,
            'associatedReferences': default_reference,
            'source_document_id': source_document_id,
            'mapped_trait_suggestion': mapped,
            'source_extraction_run_id': extraction_run_id,
        }
