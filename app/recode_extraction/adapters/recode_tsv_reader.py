import csv
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Entity:
    entity_id: str
    entity_type: str
    text: str
    doc_id: str
    start: int | None = None
    end: int | None = None


@dataclass(slots=True)
class Relation:
    relation_type: str
    head_entity_id: str
    tail_entity_id: str
    doc_id: str


@dataclass(slots=True)
class AnnotatedDocument:
    doc_id: str
    focus_taxon: str
    taxon_group: str
    annotator: str | None
    tsv_path: str
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class RecodeTsvReader:
    def __init__(self, index_path: str | Path):
        self.index_path = Path(index_path)
        self.assets_root = self.index_path.parent

    def load_documents(self) -> list[AnnotatedDocument]:
        index_entries = json.loads(self.index_path.read_text(encoding='utf-8'))
        documents: list[AnnotatedDocument] = []

        for entry in index_entries:
            tsv_file = self.assets_root / entry['tsv_path']
            entities, relations = self._parse_tsv(tsv_file, entry['doc_id'])
            documents.append(
                AnnotatedDocument(
                    doc_id=entry['doc_id'],
                    focus_taxon=entry.get('focus_taxon', ''),
                    taxon_group=entry.get('taxon_group', ''),
                    annotator=entry.get('annotator'),
                    tsv_path=entry['tsv_path'],
                    entities=entities,
                    relations=relations,
                    metadata=entry.get('metadata', {}),
                )
            )

        return documents

    def _parse_tsv(self, tsv_path: Path, default_doc_id: str) -> tuple[list[Entity], list[Relation]]:
        entities: list[Entity] = []
        relations: list[Relation] = []

        with tsv_path.open('r', encoding='utf-8') as handle:
            reader = csv.DictReader(handle, delimiter='\t')
            for row in reader:
                normalized = {self._normalize_key(k): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                if self._looks_like_relation_row(normalized):
                    relations.append(
                        Relation(
                            relation_type=self._get_first(normalized, ['relation_type', 'relation', 'label'], 'unknown_relation'),
                            head_entity_id=self._get_first(normalized, ['head_entity', 'head', 'arg1', 'source_id', 'entity1_id'], ''),
                            tail_entity_id=self._get_first(normalized, ['tail_entity', 'tail', 'arg2', 'target_id', 'entity2_id'], ''),
                            doc_id=self._get_first(normalized, ['doc_id', 'document_id'], default_doc_id),
                        )
                    )
                elif self._looks_like_entity_row(normalized):
                    entities.append(
                        Entity(
                            entity_id=self._get_first(normalized, ['entity_id', 'id', 'span_id'], ''),
                            entity_type=self._get_first(normalized, ['entity_type', 'type', 'label'], 'unknown_entity'),
                            text=self._get_first(normalized, ['text', 'mention', 'entity_text', 'span_text'], ''),
                            doc_id=self._get_first(normalized, ['doc_id', 'document_id'], default_doc_id),
                            start=self._to_int(self._get_first(normalized, ['start', 'start_offset', 'span_start'], None)),
                            end=self._to_int(self._get_first(normalized, ['end', 'end_offset', 'span_end'], None)),
                        )
                    )

        return entities, relations

    @staticmethod
    def _normalize_key(key: str) -> str:
        return key.strip().lower().replace(' ', '_')

    @staticmethod
    def _get_first(row: dict, keys: list[str], default):
        for key in keys:
            if key in row and row[key] not in (None, ''):
                return row[key]
        return default

    @staticmethod
    def _to_int(value):
        if value in (None, ''):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _looks_like_relation_row(self, row: dict) -> bool:
        relation_cols = {'relation_type', 'relation', 'head_entity', 'tail_entity', 'arg1', 'arg2'}
        return any(col in row for col in relation_cols) and (
            any(col in row and row[col] for col in ('head_entity', 'head', 'arg1', 'source_id', 'entity1_id'))
            or any(col in row and row[col] for col in ('tail_entity', 'tail', 'arg2', 'target_id', 'entity2_id'))
        )

    def _looks_like_entity_row(self, row: dict) -> bool:
        return any(col in row for col in ('entity_type', 'type', 'text', 'mention', 'entity_text', 'span_text'))
