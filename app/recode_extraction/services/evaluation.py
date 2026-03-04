import json
from dataclasses import dataclass
from pathlib import Path

from recode_extraction.adapters import RecodeTsvReader
from recode_extraction.services.extraction import ExtractionEngine


@dataclass(slots=True)
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def as_metrics(self) -> dict[str, float | int]:
        precision = self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0
        recall = self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        return {
            'tp': self.tp,
            'fp': self.fp,
            'fn': self.fn,
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1': round(f1, 4),
        }


class RecodeEvaluationService:
    def __init__(self, index_path: str | Path, text_root: str | Path | None = None, subset: int | None = None):
        self.index_path = Path(index_path)
        self.text_root = Path(text_root) if text_root else None
        self.subset = subset

    def evaluate(self) -> dict:
        reader = RecodeTsvReader(self.index_path)
        documents = reader.load_documents()
        if self.subset:
            documents = documents[: self.subset]

        engine = ExtractionEngine()
        entity_metrics: dict[str, Counts] = {}
        relation_metrics: dict[str, Counts] = {}

        for doc in documents:
            text = self._load_text(doc.doc_id, doc)
            predicted_assertions = engine.extract(text)

            gold_entity_items = {
                (entity.entity_type.lower(), entity.text.strip().lower()) for entity in doc.entities
            }
            predicted_entity_items = set()
            for assertion in predicted_assertions:
                predicted_entity_items.add(('taxon', assertion.subject_taxon.strip().lower()))
                predicted_entity_items.add(('trait', assertion.trait_name.strip().lower()))
                predicted_entity_items.add(('value', assertion.value.strip().lower()))

            self._accumulate_by_type(entity_metrics, gold_entity_items, predicted_entity_items)

            gold_rel_items = {
                (
                    relation.relation_type.lower(),
                    relation.head_entity_id.strip().lower(),
                    relation.tail_entity_id.strip().lower(),
                )
                for relation in doc.relations
            }
            predicted_rel_items = {
                ('has_trait', assertion.subject_taxon.strip().lower(), assertion.trait_name.strip().lower())
                for assertion in predicted_assertions
            }
            self._accumulate_relations(relation_metrics, gold_rel_items, predicted_rel_items)

        result = {
            'documents_evaluated': len(documents),
            'entity_type_metrics': {key: counts.as_metrics() for key, counts in sorted(entity_metrics.items())},
            'relation_type_metrics': {key: counts.as_metrics() for key, counts in sorted(relation_metrics.items())},
        }
        return result

    def _load_text(self, doc_id: str, doc) -> str:
        if self.text_root:
            candidate = self.text_root / f'{doc_id}.txt'
            if candidate.exists():
                return candidate.read_text(encoding='utf-8')

        # fallback fixture synthesis from entity mentions
        mentions = [entity.text for entity in doc.entities if entity.text]
        return '. '.join(mentions)

    @staticmethod
    def _accumulate_by_type(metrics: dict[str, Counts], gold_items: set[tuple[str, str]], pred_items: set[tuple[str, str]]):
        for entity_type, _ in pred_items - gold_items:
            metrics.setdefault(entity_type, Counts()).fp += 1
        for entity_type, _ in gold_items - pred_items:
            metrics.setdefault(entity_type, Counts()).fn += 1
        for entity_type, _ in pred_items & gold_items:
            metrics.setdefault(entity_type, Counts()).tp += 1

    @staticmethod
    def _accumulate_relations(metrics: dict[str, Counts], gold_items: set[tuple[str, str, str]], pred_items: set[tuple[str, str, str]]):
        for rel_type, _, _ in pred_items - gold_items:
            metrics.setdefault(rel_type, Counts()).fp += 1
        for rel_type, _, _ in gold_items - pred_items:
            metrics.setdefault(rel_type, Counts()).fn += 1
        for rel_type, _, _ in pred_items & gold_items:
            metrics.setdefault(rel_type, Counts()).tp += 1


def dump_eval_json(result: dict, output_path: str | Path | None = None) -> str:
    payload = json.dumps(result, indent=2, sort_keys=True)
    if output_path:
        Path(output_path).write_text(payload, encoding='utf-8')
    return payload
