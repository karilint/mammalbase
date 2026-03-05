from __future__ import annotations
from nervaluate import Evaluator


def _to_bio(spans: list[tuple[str, int, int]]) -> list[str]:
    length = max([e for _, _, e in spans], default=0)
    tags = ['O'] * max(length, 1)
    for label, start, end in spans:
        if start >= len(tags):
            continue
        tags[start] = f'B-{label}'
        for i in range(start + 1, min(end, len(tags))):
            tags[i] = f'I-{label}'
    return tags


def span_f1(gold: list[tuple[str, int, int]], pred: list[tuple[str, int, int]]) -> float:
    evaluator = Evaluator([_to_bio(gold)], [_to_bio(pred)], tags=list({x[0] for x in gold + pred}), loader='list')
    overall, _, _, _ = evaluator.evaluate()
    return float(overall['strict']['f1'])


def relation_f1(gold: set[tuple], pred: set[tuple]) -> float:
    tp = len(gold & pred)
    if not gold and not pred:
        return 1.0
    p = tp / len(pred) if pred else 0
    r = tp / len(gold) if gold else 0
    return (2 * p * r / (p + r)) if (p + r) else 0.0


def measurement_f1(gold: set[tuple[str, str, str]], pred: set[tuple[str, str, str]]) -> float:
    norm = lambda x: tuple(' '.join(part.split()) for part in x)
    return relation_f1({norm(x) for x in gold}, {norm(x) for x in pred})
