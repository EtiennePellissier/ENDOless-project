import datetime as dt, json, pathlib
from bench.validate import validate
from bench.evaluate import score
from bench.rules_baseline import extract

REF = dt.date(2026, 11, 6)

def obs(**kw):
    base = dict(concept_key="pain", assertion="reported", value=5,
                event_date="2026-11-06", time_label=None, source_excerpt="")
    return {**base, **kw}

def test_rejects_out_of_range():
    ok, issues = validate([obs(value=14)], REF)
    assert ok == [] and issues

def test_rejects_future_date():
    assert validate([obs(event_date="2026-11-07")], REF)[0] == []

def test_absence_cannot_have_value():
    assert validate([obs(assertion="explicitly_absent", value=3)], REF)[0] == []

def test_zero_is_not_missing():
    assert validate([obs(value=0)], REF)[0][0]["value"] == 0

def test_score_strict():
    assert score([obs()], [obs(value=6)]) == (0, 1, 1)

def test_red_wine_single_concept():
    o = extract("Last evening I had pain after a glass of red wine.", REF)
    assert [x["value"] for x in o if x["concept_key"] == "context_note"] == ["red wine"]

def test_dev_cases_all_ids_unique():
    p = pathlib.Path("cases/dev_cases.jsonl")
    ids = [json.loads(l)["id"] for l in p.read_text().splitlines() if l.strip()]
    assert len(ids) == len(set(ids))
