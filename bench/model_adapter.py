"""One internal interface for any OpenAI-compatible local server (llama.cpp, vLLM, Ollama).
Same prompt, same schema, temperature 0 for every candidate model. UNTESTED until Andrei gives an endpoint."""
import json
import pathlib
import urllib.request

SYSTEM = (pathlib.Path(__file__).resolve().parent.parent / "prompts" / "extraction_system.txt").read_text(encoding="utf-8")


def extract(endpoint, model, message, ref_date, tz, timeout=60):
    body = {"model": model, "temperature": 0, "max_tokens": 600,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": f"Reference date: {ref_date.isoformat()} ({tz}).\nMessage: {message}"}]}
    req = urllib.request.Request(endpoint.rstrip("/") + "/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = json.load(r)["choices"][0]["message"]["content"]
        data = json.loads(text.strip().removeprefix("```json").removesuffix("```"))
        obs = data["observations"]
        return (obs, True) if isinstance(obs, list) else ([], False)
    except Exception:
        return [], False  # counted as invalid output, never silently excluded
