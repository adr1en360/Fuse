# Src Workspace

## What This Workspace Is For
All application code for Jev — the proxy, anomaly detector, classifier, simulator, and dashboard.

## Process
1. Build in the order specified in the PRD (proxy → simulator → classifier → dashboard → rehearsal).
2. Each component must pass its own test before the next one starts.
3. Follow Karpathy guidelines: simplicity first, surgical changes, verifiable goals.
4. No speculative abstractions — this is a one-day build.

## Files In Here
- `proxy.py` — FastAPI proxy skeleton + sliding-window anomaly detector + hard ceiling.
- `simulator.py` — Runaway-agent simulator (normal + 3 burst patterns).
- `classifier.py` — Tier 1 fast classifier + Tier 2 escalation logic.
- `dashboard.py` — Live dashboard (terminal-first via `rich`, web if time permits).
- `config.py` — All thresholds, timeouts, model endpoints in one place.
- `models.py` — Pydantic models for call records, classifications, verdicts.

## What Good Output Looks Like
`python simulator.py` triggers all three burst patterns → proxy catches each one → classifier labels each correctly → dashboard shows state changes → hard ceiling fires when model is killed.

## Constraints
- Python only. No framework hopping under time pressure.
- No raw payload logging. Metadata + arg hashes only.
- Hard ceiling logic NEVER depends on model output. It fires on its own numbers.
- No premature web dashboard. Terminal (rich) first, web only if sprints 1–3 are done.

_Last updated: 2026-09-27_
