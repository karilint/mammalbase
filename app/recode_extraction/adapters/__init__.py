"""Adapters for RECODE corpus/model assets."""

from .assets import RecodeAssetManager, RecodeAssetPaths
from .corpus import CorpusAssetAdapter
from .recode_tsv_reader import AnnotatedDocument, Entity, RecodeTsvReader, Relation

__all__ = [
    'AnnotatedDocument',
    'CorpusAssetAdapter',
    'Entity',
    'RecodeAssetManager',
    'RecodeAssetPaths',
    'RecodeTsvReader',
    'Relation',
]
