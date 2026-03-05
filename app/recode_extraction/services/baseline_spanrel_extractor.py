from __future__ import annotations
import re
from recode_extraction.adapters.webanno_parser import ParsedWebAnnoDoc, Span, RelationArc


def extract_spanrel(page_text: str, page_number: int | None = None) -> ParsedWebAnnoDoc:
    doc = ParsedWebAnnoDoc(tokens=[])
    spans = []
    rels = []
    species = re.search(r'([A-Z][a-z]+\s+[a-z]+)', page_text)
    trait = re.search(r'(body mass|adult mass|length|litter size)', page_text, re.IGNORECASE)
    val = re.search(r'(\d+(?:\.\d+)?)', page_text)
    unit = re.search(r'\b(kg|g|cm|mm)\b', page_text)
    sex = re.search(r'\b(male|female)\b', page_text, re.IGNORECASE)
    lstage = re.search(r'\b(adult|juvenile)\b', page_text, re.IGNORECASE)
    count = re.search(r'\bn\s*=\s*(\d+)\b', page_text, re.IGNORECASE)

    def add(label, m, idx):
        if not m:
            return None
        ext = f'p{page_number or 1}:{label}:{idx}'
        spans.append(Span(external_id=ext, label=label, text=m.group(0), token_ids=[ext], start_offset_utf16=m.start(), end_offset_utf16=m.end()))
        return ext

    s_sp = add('Species', species, 1)
    t_sp = add('Trait', trait, 1)
    v_sp = add('TraitVal', val, 1)
    u_sp = add('Unit', unit, 1)
    sx_sp = add('Sex', sex, 1)
    ls_sp = add('LStage', lstage, 1)
    c_sp = add('Count', count, 1)

    if v_sp and t_sp:
        rels.append(RelationArc(label='meas_Trait', head_external_id=v_sp, tail_external_id=t_sp))
    if v_sp and s_sp:
        rels.append(RelationArc(label='meas_Species', head_external_id=v_sp, tail_external_id=s_sp))
    if v_sp and u_sp:
        rels.append(RelationArc(label='meas_Unit', head_external_id=v_sp, tail_external_id=u_sp))
    if v_sp and sx_sp:
        rels.append(RelationArc(label='meas_Sex', head_external_id=v_sp, tail_external_id=sx_sp))
    if v_sp and ls_sp:
        rels.append(RelationArc(label='meas_LStage', head_external_id=v_sp, tail_external_id=ls_sp))
    if v_sp and c_sp:
        rels.append(RelationArc(label='meas_Count', head_external_id=v_sp, tail_external_id=c_sp))

    doc.spans = spans
    doc.relations = rels
    doc.text_blocks = [page_text]
    return doc
