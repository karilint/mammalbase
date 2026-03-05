from __future__ import annotations

import logging
from django.db import transaction

from recode_extraction.adapters.webanno_parser import ParsedWebAnnoDoc
from recode_extraction.models import ExtractedEntity, ExtractedRelation, SourceExtractionRun

logger = logging.getLogger(__name__)


def persist_parsed_doc(
    run: SourceExtractionRun,
    parsed_doc: ParsedWebAnnoDoc,
    *,
    page_number: int | None,
    snippet_source_text: str | None,
) -> dict[str, int]:
    mapping: dict[str, int] = {}
    with transaction.atomic():
        for span in parsed_doc.spans:
            entity, _ = ExtractedEntity.objects.get_or_create(
                extraction_run=run,
                span_external_id=span.external_id,
                defaults={
                    'entity_type': span.label,
                    'text': span.text,
                    'token_ids': span.token_ids,
                    'start_offset_utf16': span.start_offset_utf16,
                    'end_offset_utf16': span.end_offset_utf16,
                    'page_number': page_number,
                    'snippet': snippet_source_text or '',
                },
            )
            mapping[span.external_id] = entity.pk

        for rel in parsed_doc.relations:
            head_id = mapping.get(rel.head_external_id)
            tail_id = mapping.get(rel.tail_external_id)
            if not head_id or not tail_id:
                logger.warning('Skipping relation with missing endpoint: %s', rel)
                continue
            ExtractedRelation.objects.get_or_create(
                extraction_run=run,
                relation_type=rel.label,
                head_entity_id=head_id,
                tail_entity_id=tail_id,
                drawn_from_token_id=rel.drawn_from_token_id,
                defaults={
                    'page_number': page_number,
                    'snippet': snippet_source_text or '',
                },
            )
    return mapping
