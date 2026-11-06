"""Simple regex baseline (the 'floor' the models must beat). Intentionally naive on hard negation."""
import re
import datetime as dt

NUM = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten".split())}
DATES = [(r"\b(?:yesterday|last)\s+evening\b", -1, "evening"), (r"\byesterday\b", -1, None), (r"\btoday\b", 0, None)]
OTHER = r"\bmy (sister|mother|friend|colleague|daughter|partner)\b"


def _num(s):
    s = s.lower()
    return int(s) if s.isdigit() else NUM.get(s)


def _date(c, ref):
    for pat, off, label in DATES:
        if re.search(pat, c, re.I):
            return ref + dt.timedelta(days=off), label
    return None


def _clauses(text):
    out = []
    for s in re.split(r"(?<=[.!?])\s+", text.strip()):
        if len({x.lower() for x in re.findall(r"\b(today|yesterday)\b", s, re.I)}) > 1:
            out += re.split(r"\s+and\s+(?=.*\b(?:today|yesterday)\b)", s)
        else:
            out.append(s)
    return out


def extract(msg, ref):
    obs, cur = [], None
    for c in _clauses(msg):
        cur = _date(c, ref) or cur
        if re.search(r"\b(usually|always|generally)\b", c, re.I) or re.search(OTHER, c, re.I):
            continue
        date, label = cur if cur else (None, None)
        m = re.search(r"(\w+)\s*(?:out of|/)\s*(?:10|ten)\b", c, re.I)
        n = _num(m.group(1)) if m else None
        if n is None:  # bare score such as "pain was 7"
            m4 = re.search(r"\b(?:pain|fatigue)\b\D{0,12}(\d+)\b", c, re.I)
            n = int(m4.group(1)) if m4 else None

        def add(concept, assertion="reported", value=None):
            obs.append({"concept_key": concept, "assertion": assertion, "value": value,
                        "unit": "0-10" if isinstance(value, int) and concept in ("pain", "fatigue") else None,
                        "event_date": date.isoformat() if date else None, "time_label": label, "source_excerpt": c})
        if re.search(r"\bno pain\b", c, re.I):
            add("pain", "explicitly_absent")
        elif re.search(r"\bpain\b", c, re.I):
            add("pain", value=n)
        if re.search(r"\b(tired|fatigue|exhausted)\b", c, re.I):
            add("fatigue", value=n)
        if re.search(r"slept (badly|poorly)|sleep(ing)? (badly|poorly)|poor sleep", c, re.I):
            add("sleep_disturbance")
        if re.search(r"\bmood\b.*\blow\b|\blow mood\b|\bfeel(ing)? low\b", c, re.I):
            add("mood")
        if re.search(r"\bperiod\b.*\b(started|began|arrived)\b|\bbleeding\b", c, re.I):
            add("menstrual_bleeding")
        m2 = re.search(r"left work early|missed work|stayed in bed|cancelled plans", c, re.I)
        if m2:
            add("daily_impact", value=m2.group(0).lower())
        m3 = re.search(r"\b(red wine|white wine|wine|coffee|alcohol)\b", c, re.I)
        if m3:
            add("context_note", value=m3.group(1).lower())
    fix = re.search(r"\bactually\s+(\w+)", msg, re.I)
    if fix and _num(fix.group(1)) is not None:
        for o in reversed(obs):
            if isinstance(o["value"], int):
                o["value"] = _num(fix.group(1)); break
    return obs
