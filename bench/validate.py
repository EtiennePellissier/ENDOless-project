"""Independent validator: the model proposes, this code disposes. No silent repair."""
import datetime as dt

CATALOGUE = {  # PROVISIONAL: replace with Andrei's real field dictionary
    "pain": {"numeric": True}, "fatigue": {"numeric": True},
    "sleep_disturbance": {}, "mood": {}, "menstrual_bleeding": {},
    "daily_impact": {}, "context_note": {},
}
ASSERTIONS = {"reported", "explicitly_absent", "unknown"}
TIME_LABELS = {None, "morning", "afternoon", "evening", "night"}
ALLOWED_KEYS = ["concept_key", "assertion", "value", "unit", "event_date", "time_label", "source_excerpt"]


def validate(observations, ref_date):
    accepted, issues = [], []
    for i, o in enumerate(observations):
        def bad(msg):
            issues.append({"index": i, "issue": msg})
        if not isinstance(o, dict):
            bad("not an object"); continue
        c = o.get("concept_key")
        if c not in CATALOGUE:
            bad(f"unknown concept {c!r}"); continue
        if o.get("assertion") not in ASSERTIONS:
            bad("bad assertion"); continue
        v = o.get("value")
        if CATALOGUE[c].get("numeric"):
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 10):
                bad(f"value {v!r} outside 0-10 for {c}"); continue
        elif v is not None and not isinstance(v, str):
            bad(f"non-text value for {c}"); continue
        if o["assertion"] == "explicitly_absent" and v is not None:
            bad("explicit absence cannot carry a value"); continue
        d = o.get("event_date")
        if d is not None:
            try:
                if dt.date.fromisoformat(d) > ref_date:
                    bad("date in the future"); continue
            except (TypeError, ValueError):
                bad("invalid date"); continue
        if o.get("time_label") not in TIME_LABELS:
            bad("bad time_label"); continue
        accepted.append({k: o.get(k) for k in ALLOWED_KEYS})
    return accepted, issues
