from collections import Counter


def _n(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return v.strip().lower() if isinstance(v, str) else v


def key(o):
    return (o.get("concept_key"), o.get("assertion"), _n(o.get("value")), o.get("event_date"), o.get("time_label"))


def score(pred, gold):
    p, g = Counter(map(key, pred)), Counter(map(key, gold))
    tp = sum((p & g).values())
    return tp, sum(p.values()) - tp, sum(g.values()) - tp


def unsupported(pred, gold):
    concepts = {o["concept_key"] for o in gold}
    return sum(1 for o in pred if o.get("concept_key") not in concepts)


def multiword_violations(pred, forbidden):
    return sum(1 for o in pred if isinstance(o.get("value"), str) and o["value"].strip().lower() in forbidden)


def prf(tp, fp, fn):
    return (tp / (tp + fp) if tp + fp else None, tp / (tp + fn) if tp + fn else None)
