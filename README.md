# ENDOless PRIM - Sprint 1 kit (23 Oct - 6 Nov 2026)

Role covered here: **technical lead** (extraction benchmark, validation) + the **UX state catalogue** the UX lead owns.
Everything is synthetic. The catalogue in `bench/validate.py` is PROVISIONAL (Andrei's real field dictionary is not received yet).

## What is in the box
| Path | What it is |
|---|---|
| `bench/run_benchmark.py` | Runs a system on the dev cases, prints precision / recall per family, latency p50/p95, saves JSON |
| `bench/rules_baseline.py` | Regex baseline = the floor a model must beat |
| `bench/model_adapter.py` | Calls any OpenAI-compatible local server (llama.cpp, vLLM, Ollama). **Untested until we get an endpoint** |
| `bench/validate.py` | Independent validator: unknown concept, value outside 0-10, future date... rejected, never "repaired" |
| `bench/evaluate.py` | Strict match on concept + assertion + value + date + time label |
| `cases/dev_cases.jsonl` | 15 English development cases with gold annotations (NOT a held-out test set) |
| `prompts/extraction_system.txt` | Same prompt for every model |
| `schema/observation.schema.json` | Draft observation format (proposed, not the real DB) |
| `planning/decision_log.csv`, `planning/backlog.csv` | 11 decisions with owner/fallback; 24 backlog tasks mapped to R01-R15 |
| `ux/ux_states.csv` | 18 interface states with copy, test fixture and accessibility check |
| `templates/` | Model record sheet and results sheet to fill with the real runs |

## How it works (the pipeline)
```
message --> [extractor: rules OR model] --> raw proposals --> [validator] --> validated draft --> [evaluate vs gold]
```
1. The extractor proposes observations (it never writes anything).
2. The validator checks them against the catalogue. Invalid items are dropped and listed, not corrected.
3. We score **raw** and **validated** separately so validation cannot hide extraction errors.
4. Strict match: a prediction is correct only if concept, assertion (reported / explicitly_absent), value, date and time label all match.
   - precision = correct / all proposed ; recall = correct / all gold.
5. "Unsupported observations" counts proposals for a concept absent from the gold: target is zero.

## Run
```
python3 -m bench.run_benchmark --system rules --model baseline
python3 -m bench.run_benchmark --system model --endpoint http://HOST:8080 --model ministral-3-3b --repeats 5
```
Start each model with its own server (same prompt, temperature 0), then fill `templates/model_record_template.csv`.

## Honest limits
- The baseline was written while looking at these 15 cases: its score is optimistic. Real numbers need the locked set.
- Targets (95% precision / 90% recall) are proposed acceptance criteria, not results.
- 15 cases is a smoke test, not evidence. The plan is 48 dev cases then 80 locked cases.
