import csv
import json
import re
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
    _documents_cache: dict[tuple[str, int], list[AnnotatedDocument]] = {}
    _SPAN_RE = re.compile(r'^(?P<label>[^\[]+?)(?:\[(?P<idx>\d+)\])?$')

    def __init__(self, index_path: str | Path):
        self.index_path = Path(index_path)
        self.assets_root = self.index_path.parent

    def load_documents(self) -> list[AnnotatedDocument]:
        cache_key = self._cache_key()
        cached = self._documents_cache.get(cache_key)
        if cached is not None:
            return cached

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

        self._documents_cache[cache_key] = documents
        return documents

    def _cache_key(self) -> tuple[str, int]:
        stat = self.index_path.stat()
        return str(self.index_path.resolve()), stat.st_mtime_ns

    def _parse_tsv(self, tsv_path: Path, default_doc_id: str) -> tuple[list[Entity], list[Relation]]:
        text = tsv_path.read_text(encoding='utf-8')
        if '#FORMAT=WebAnno TSV' in text:
            return self._parse_webanno_tsv(text, default_doc_id)
        return self._parse_flat_tsv(tsv_path, default_doc_id)

    def _parse_flat_tsv(self, tsv_path: Path, default_doc_id: str) -> tuple[list[Entity], list[Relation]]:
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

    def _parse_webanno_tsv(self, payload: str, default_doc_id: str) -> tuple[list[Entity], list[Relation]]:
        span_layers = 0
        relation_layers = 0
        token_rows: list[dict] = []

        for raw_line in payload.splitlines():
            line = raw_line.strip('\n')
            if not line:
                continue
            if line.startswith('#T_SP='):
                span_layers += 1
                continue
            if line.startswith('#T_RL='):
                relation_layers += 1
                continue
            if line.startswith('#'):
                continue

            cols = line.split('\t')
            if len(cols) < 4:
                continue
            token_id = cols[0]
            start, end = self._parse_offsets(cols[1])
            token = cols[2]
            span_cols = cols[3:3 + span_layers]
            rel_cols = cols[3 + span_layers:3 + span_layers + relation_layers * 2]
            token_rows.append(
                {
                    'token_id': token_id,
                    'start': start,
                    'end': end,
                    'token': token,
                    'span_cols': span_cols,
                    'rel_cols': rel_cols,
                }
            )

        entities_by_key: dict[tuple[str, str | None], Entity] = {}
        token_to_entities: dict[str, list[str]] = {}

        for row in token_rows:
            token_entities: list[str] = []
            for span_col in row['span_cols']:
                for ann in [x.strip() for x in span_col.split('|') if x.strip() and x.strip() != '_']:
                    label, idx = self._parse_span_annotation(ann)
                    key = (label, idx)
                    entity = entities_by_key.get(key)
                    if entity is None:
                        entity_id = f'{label}:{idx}' if idx else f'{label}:{len(entities_by_key) + 1}'
                        entity = Entity(
                            entity_id=entity_id,
                            entity_type=label,
                            text=row['token'],
                            doc_id=default_doc_id,
                            start=row['start'],
                            end=row['end'],
                        )
                        entities_by_key[key] = entity
                    else:
                        if entity.text:
                            entity.text = f"{entity.text} {row['token']}"
                        else:
                            entity.text = row['token']
                        entity.start = min(entity.start, row['start']) if entity.start is not None else row['start']
                        entity.end = max(entity.end, row['end']) if entity.end is not None else row['end']
                    token_entities.append(entity.entity_id)
            token_to_entities[row['token_id']] = token_entities

        relations: list[Relation] = []
        for row in token_rows:
            rel_cols = row['rel_cols']
            if not rel_cols:
                continue
            for i in range(0, len(rel_cols), 2):
                rel_type_col = rel_cols[i]
                rel_target_col = rel_cols[i + 1] if i + 1 < len(rel_cols) else '_'
                rel_types = [x.strip() for x in rel_type_col.split('|') if x.strip() and x.strip() != '_']
                rel_targets = [x.strip() for x in rel_target_col.split('|') if x.strip() and x.strip() != '_']
                for rel_type, rel_target in zip(rel_types, rel_targets):
                    source_entity = self._first_entity_for_token(token_to_entities, row['token_id'])
                    target_token_id = rel_target.split('[')[0]
                    target_entity = self._first_entity_for_token(token_to_entities, target_token_id)
                    if not source_entity or not target_entity:
                        continue
                    relations.append(
                        Relation(
                            relation_type=rel_type.split('[')[0],
                            head_entity_id=source_entity,
                            tail_entity_id=target_entity,
                            doc_id=default_doc_id,
                        )
                    )

        return list(entities_by_key.values()), relations

    @staticmethod
    def _first_entity_for_token(token_lookup: dict[str, list[str]], token_id: str) -> str | None:
        values = token_lookup.get(token_id) or []
        return values[0] if values else None

    def _parse_span_annotation(self, raw: str) -> tuple[str, str | None]:
        matched = self._SPAN_RE.match(raw)
        if not matched:
            return raw, None
        return matched.group('label'), matched.group('idx')

    @staticmethod
    def _parse_offsets(offset_cell: str) -> tuple[int | None, int | None]:
        first = offset_cell.split(';')[0]
        if '-' not in first:
            return None, None
        start, end = first.split('-', 1)
        return RecodeTsvReader._to_int(start), RecodeTsvReader._to_int(end)

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
