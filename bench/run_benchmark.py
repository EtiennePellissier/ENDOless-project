"""Usage:
  python -m bench.run_benchmark --system rules
  python -m bench.run_benchmark --system model --endpoint http://HOST:8080 --model ministral-3-3b --repeats 5
"""
import argparse, json, time, platform, sys, pathlib, datetime as dt
from collections import defaultdict
from .rules_baseline import extract as rules_extract
from .model_adapter import extract as model_extract
from .validate import validate
from .evaluate import score, unsupported, multiword_violations, prf

ROOT = pathlib.Path(__file__).resolve().parent.parent


def pct(v, q):
    s = sorted(v)
    return s[min(len(s) - 1, round(q * (len(s) - 1)))]


def fmt(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", choices=["rules", "model"], required=True)
    ap.add_argument("--endpoint"); ap.add_argument("--model", default="unnamed")
    ap.add_argument("--cases", default=str(ROOT / "cases" / "dev_cases.jsonl"))
    ap.add_argument("--repeats", type=int, default=1)
    a = ap.parse_args()
    cases = [json.loads(l) for l in open(a.cases, encoding="utf-8") if l.strip()]
    tot = {"raw": [0, 0, 0], "validated": [0, 0, 0]}
    fam = defaultdict(lambda: [0, 0, 0])
    lat, invalid, mw, unsup, fails = [], 0, 0, 0, []
    for c in cases:
        ref = dt.date.fromisoformat(c.get("reference_date", "2026-11-06"))
        for _ in range(a.repeats):
            t = time.perf_counter()
            if a.system == "rules":
                raw, ok = rules_extract(c["message"], ref), True
            else:
                raw, ok = model_extract(a.endpoint, a.model, c["message"], ref, "Europe/Paris")
            lat.append(time.perf_counter() - t)
        invalid += (not ok)
        val, issues = validate(raw, ref)
        for name, pred in (("raw", raw), ("validated", val)):
            s = score(pred, c["gold"])
            tot[name] = [x + y for x, y in zip(tot[name], s)]
            if name == "validated":
                fam[c["family"]] = [x + y for x, y in zip(fam[c["family"]], s)]
        mw += multiword_violations(val, c.get("forbidden_values", []))
        unsup += unsupported(val, c["gold"])
        if score(val, c["gold"])[1:] != (0, 0) or issues:
            fails.append({"id": c["id"], "message": c["message"], "predicted": val, "gold": c["gold"], "validator_issues": issues})
    print(f"\nSystem: {a.system} {a.model if a.system == 'model' else ''} | {len(cases)} dev cases | invalid outputs: {invalid}")
    for name in tot:
        p, r = prf(*tot[name]); print(f"  {name:<10} TP/FP/FN={tot[name]}  precision={fmt(p)}  recall={fmt(r)}")
    print(f"  unsupported saved observations (validated): {unsup}  | multiword violations: {mw}")
    print(f"  latency p50={pct(lat, .5)*1000:.1f} ms  p95={pct(lat, .95)*1000:.1f} ms  (n={len(lat)})")
    print("  by family (validated):")
    for f, s in sorted(fam.items()):
        p, r = prf(*s); print(f"    {f:<12} P={fmt(p):>4} R={fmt(r):>4}  TP/FP/FN={s}")
    for f in fails:
        print(f"  FAIL/ISSUE {f['id']}: {f['message']}  issues={f['validator_issues']}")
    out = ROOT / "results" / f"{a.system}_{a.model}_{dt.datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps({"system": a.system, "model": a.model, "python": sys.version, "platform": platform.platform(),
                               "totals": tot, "invalid": invalid, "unsupported": unsup, "multiword": mw,
                               "latency_ms": {"p50": pct(lat, .5) * 1000, "p95": pct(lat, .95) * 1000, "n": len(lat)},
                               "failures": fails}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  saved: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
