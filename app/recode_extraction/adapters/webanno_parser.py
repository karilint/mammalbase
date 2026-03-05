"""WebAnno TSV 3.3 parser for RECODE.
References: WebAnno TSV 3.3 user guide, RECODE Zenodo (15254437), and arete::webanno_open/labels.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Token:
    token_id: str
    sent_token: str
    start_offset_utf16: int
    end_offset_utf16: int
    text: str
    page_number: int | None = None


@dataclass(slots=True)
class Span:
    external_id: str
    label: str
    text: str
    token_ids: list[str] = field(default_factory=list)
    start_offset_utf16: int | None = None
    end_offset_utf16: int | None = None
    disambig: int | None = None


@dataclass(slots=True)
class RelationArc:
    label: str
    head_external_id: str
    tail_external_id: str
    drawn_from_token_id: str | None = None
    endpoint_disambig: tuple[int | None, int | None] | None = None


@dataclass(slots=True)
class ParsedWebAnnoDoc:
    tokens: list[Token] = field(default_factory=list)
    spans: list[Span] = field(default_factory=list)
    relations: list[RelationArc] = field(default_factory=list)
    text_blocks: list[str] = field(default_factory=list)


def utf16_offset_to_py_index(text: str, utf16_offset: int) -> int:
    count = 0
    for idx, ch in enumerate(text):
        count += 2 if ord(ch) > 0xFFFF else 1
        if count > utf16_offset:
            return idx
    return len(text)


def parse_webanno_tsv33(path: str) -> ParsedWebAnnoDoc:
    doc = ParsedWebAnnoDoc()
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    if not any(line.startswith('#FORMAT=WebAnno TSV 3.3') for line in lines):
        logger.warning('Skipping non-WebAnno TSV 3.3 file: %s', path)
        return doc

    span_layers: list[str] = []
    rel_layers: list[str] = []
    for line in lines:
        if line.startswith('#T_SP='):
            span_layers.append(line.split('=', 1)[1].split('|')[0].strip())
        elif line.startswith('#T_RL='):
            rel_layers.append(line.split('=', 1)[1].split('|')[0].strip())
        elif line.startswith('#Text='):
            doc.text_blocks.append(line.split('=', 1)[1])

    span_by_external: dict[str, Span] = {}
    token_to_spans: dict[str, list[str]] = {}
    rel_columns = len(rel_layers)

    for line in lines:
        if not line or line.startswith('#'):
            continue
        cols = line.split('\t')
        if len(cols) < 3:
            continue
        token_id = cols[0]
        sent_tok = cols[1]
        if '-' not in cols[2]:
            continue
        start, end = cols[2].split('-', 1)
        token = Token(token_id=token_id, sent_token=sent_tok, start_offset_utf16=int(start), end_offset_utf16=int(end), text=cols[3] if len(cols) > 3 else '')
        doc.tokens.append(token)

        feature_cols = cols[4:len(cols)-rel_columns] if rel_columns else cols[4:]
        for layer_idx, raw in enumerate(feature_cols):
            if raw in {'*', '_', ''}:
                continue
            layer = span_layers[layer_idx] if layer_idx < len(span_layers) else f'layer_{layer_idx}'
            for part in raw.split('|'):
                match = re.match(r'(?P<label>[^\[]+)(?:\[(?P<dis>\d+)\])?', part.strip())
                if not match:
                    continue
                label = match.group('label')
                dis = int(match.group('dis')) if match.group('dis') else None
                external_id = f'{token_id}:{layer}:{part.strip()}'
                span = span_by_external.get(external_id)
                if not span:
                    span = Span(
                        external_id=external_id,
                        label=label,
                        text=token.text,
                        token_ids=[token_id],
                        start_offset_utf16=token.start_offset_utf16,
                        end_offset_utf16=token.end_offset_utf16,
                        disambig=dis,
                    )
                    span_by_external[external_id] = span
                token_to_spans.setdefault(token_id, []).append(external_id)

        if rel_columns:
            rel_parts = cols[-rel_columns:]
            for idx, rel_raw in enumerate(rel_parts):
                if rel_raw in {'*', '_', ''}:
                    continue
                for rel_seg in rel_raw.split('|'):
                    rel_name, _, target = rel_seg.partition('->')
                    rel_name = rel_name.strip()
                    m = re.match(r'(?P<token>\d+-\d+)(?:\[(?P<src>\d+)_(?P<tgt>\d+)\])?', target.strip())
                    if not m:
                        continue
                    target_token = m.group('token')
                    src_dis = int(m.group('src')) if m.group('src') else None
                    tgt_dis = int(m.group('tgt')) if m.group('tgt') else None
                    src_spans = token_to_spans.get(token_id, [])
                    tgt_spans = token_to_spans.get(target_token, [])
                    if not src_spans or not tgt_spans:
                        logger.warning('Skipping unresolved relation %s in %s', rel_seg, path)
                        continue
                    head = _pick_span(src_spans, span_by_external, src_dis)
                    tail = _pick_span(tgt_spans, span_by_external, tgt_dis)
                    if not head or not tail:
                        continue
                    doc.relations.append(
                        RelationArc(
                            label=rel_name,
                            head_external_id=head,
                            tail_external_id=tail,
                            drawn_from_token_id=token_id,
                            endpoint_disambig=(src_dis, tgt_dis) if (src_dis or tgt_dis) else None,
                        )
                    )

    doc.spans = list(span_by_external.values())
    return doc


def _pick_span(candidates: list[str], spans: dict[str, Span], disambig: int | None) -> str | None:
    if disambig is None:
        return candidates[0] if candidates else None
    for key in candidates:
        if spans[key].disambig == disambig:
            return key
    return candidates[0] if candidates else None
