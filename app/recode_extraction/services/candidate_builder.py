from __future__ import annotations

from django.conf import settings
import networkx as nx

from recode_extraction.models import SourceExtractionRun


DEFAULT_RELATION_CONFIG = {
    'traitval_label': 'TraitVal',
    'mandatory': {'trait': ['meas_Trait'], 'species': ['meas_Species']},
    'optional': {
        'unit': ['meas_Unit'],
        'sex': ['meas_Sex'],
        'lstage': ['meas_LStage'],
        'count': ['meas_Count'],
        'ref': ['meas_Ref'],
        'locality': ['meas_Loc'],
        'coord': ['meas_Coord'],
        'date': ['meas_Date'],
    },
}


def build_graph(run: SourceExtractionRun) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    for entity in run.entities.all():
        g.add_node(entity.pk, label=entity.entity_type, text=entity.text, token_ids=entity.token_ids, page_number=entity.page_number, snippet=entity.snippet)
    for rel in run.relations.select_related('head_entity', 'tail_entity'):
        g.add_edge(rel.head_entity_id, rel.tail_entity_id, key=rel.pk, label=rel.relation_type, confidence=rel.confidence)
    return g


def build_measurement_candidates(g: nx.MultiDiGraph, *, relation_config: dict | None = None) -> list[dict]:
    cfg = DEFAULT_RELATION_CONFIG | (getattr(settings, 'RECODE_RELATION_CONFIG', {}) or {})
    if relation_config:
        cfg = cfg | relation_config
    out = []
    for node, data in g.nodes(data=True):
        if data.get('label') != cfg['traitval_label']:
            continue
        trait = _first_related(g, node, cfg['mandatory']['trait'])
        species = _first_related(g, node, cfg['mandatory']['species'])
        if not trait or not species:
            continue
        candidate = {
            'value_text': data.get('text', ''),
            'traitval_text': data.get('text', ''),
            'trait_text': g.nodes[trait].get('text', ''),
            'species_text': g.nodes[species].get('text', ''),
            'page_number': data.get('page_number'),
            'token_ids': data.get('token_ids', []),
            'snippet': data.get('snippet', ''),
            'confidence': 1.0,
        }
        for key, labels in cfg['optional'].items():
            rel_node = _first_related(g, node, labels)
            candidate[f'{key}_text'] = g.nodes[rel_node].get('text', '') if rel_node else ''
        out.append(candidate)
    return out


def _first_related(g, node, labels):
    for _, tail, attrs in g.out_edges(node, data=True):
        if attrs.get('label') in labels:
            return tail
    for head, _, attrs in g.in_edges(node, data=True):
        if attrs.get('label') in labels:
            return head
    return None
