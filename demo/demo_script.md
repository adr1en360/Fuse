# Fuse — 90-Second Demo Video Script & Battle Plan

> **Target Awards:**
> 1. 🏆 **Mac Mini** (Thunders Engineering Excellence Award)
> 2. ⚡ **NVIDIA Brev Breakthrough Award** (Responsible AI / Innovation)
> **Total Length:** Exactly 90 seconds (Submission Form Requirement).

---

## Video Timeline Breakdown

```
[00:00 - 00:15]  PROBLEM: Autonomous agents run wild on tools (retry storms, loops, cost).
[00:15 - 00:38]  SOLUTION: Meet Fuse — the confidence-gated proxy with Jev & Gemini.
[00:38 - 01:15]  LIVE DEMO: 4 Acts (Burst, Retry Storm, Escape Hatch, Hard Ceiling).
[01:15 - 01:30]  PROOF & AWARDS FIT: Engineering excellence, tamper-evident audit logs.
```

---

## Teleprompter Voiceover Script

### [00:00 - 00:15] The Hook & The Problem
> *"Autonomous AI agents are powerful, but when tools fail, agents panic. They trigger retry storms, get trapped in circular loops, burn through API credits, and trigger downstream rate limits. Traditional rate limiters are dumb—they block legitimate parallel work. Hardcoded rules can't differentiate between an agent reading 10 documents at once and an agent stuck in a death loop."*

### [00:15 - 00:38] The Solution: Fuse + 3-Layer Hierarchy
> *"Enter **Fuse** — an intelligent circuit breaker proxy that sits between your AI agent and external services. Fuse uses a strict 3-layer safety hierarchy:*
> *Layer 1 is an inviolable deterministic ceiling—no AI can bypass it.*
> *Layer 2 is **Jev**, TypeSafe AI's System One model. Instead of slow text prompts, Jev evaluates typed Choice, Score, and Noul questions with calibrated confidence in milliseconds.*
> *Layer 3 is **Gemini 3.8 Flash**, serving as our deep root-cause doctor when Jev triggers its escape hatch."*

### [00:38 - 01:15] Live Demonstration (Screen Recording of Terminal)
> *(Cut to Terminal running `python demo/run_demo.py`)*
> 
> **Act 1 (Parallel Work):**
> *"Here, an agent fires 10 concurrent document searches. A dumb proxy blocks this. Fuse recognizes `parallel_work` with high confidence and forwards it seamlessly."*
> 
> **Act 2 (Stuck Retry Storm):**
> *"Now the agent hits a failing 503 endpoint repeatedly with identical arguments. Fuse detects a `retry_storm`, applies exponential backoff, and saves the downstream API from crashing."*
> 
> **Act 3 (Loop Bug & Escape Hatch):**
> *"In Act 3, the agent gets stuck alternating between tools. Jev recognizes an unmodeled pattern, triggers its `unrecognized` escape hatch, and routes to Gemini 3.8 Flash, which diagnoses the root cause and provides auto-remediation advice."*
> 
> **Act 4 (Hard Ceiling Block):**
> *"Finally, a catastrophic rogue burst trips Layer 1. Pure counting enforces a hard 429 block. Zero AI bypass."*

### [01:15 - 01:30] The Closer: Engineering Excellence
> *"Every single event is cryptographically hashed into a tamper-evident audit log. Fuse proves that responsible AI infrastructure doesn't have to choose between safety and agent velocity. Thank you."*

---

## Instructions to Run the Live Demo

In three separate terminal tabs (or split screen):

### Tab 1: Start Mock Downstream Server
```powershell
.venv\Scripts\python demo\mock_server.py
```

### Tab 2: Start Fuse Proxy
```powershell
.venv\Scripts\python -m uvicorn src.proxy:app --port 8000
```

### Tab 3: Run the 4-Act Demo Runner
```powershell
.venv\Scripts\python demo\run_demo.py
```
