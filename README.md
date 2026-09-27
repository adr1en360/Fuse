# Jev — Agent Traffic Circuit Breaker

> Instead of your AI quietly getting your WhatsApp Business account suspended, it stops itself and says why — before the provider notices.

## What It Is

A proxy that sits between an AI agent and whatever it calls (APIs, databases, services). It watches outbound call patterns in real time. When it detects a fanout, retry storm, or looping bug, a fast LLM classifier identifies what's happening and picks a response — backed by a hard deterministic ceiling that trips regardless of the model's decision.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env with your Gemini API key

# 3. Start the proxy
python src/proxy.py

# 4. Run the simulator (separate terminal)
python src/simulator.py
```

## Architecture

```
AI Agent → Jev Proxy → Downstream API
              │
              ├─ Sliding-window anomaly detector
              ├─ Tier 1: Fast LLM classifier (allow/backoff/kill)
              ├─ Tier 2: Thinking model (root-cause on escalation)
              └─ Hard deterministic ceiling (always wins)
```

## Stack

- **Language:** Python
- **Proxy:** FastAPI
- **LLM:** Gemini (default), Groq (fallback) — configurable via `.env`
- **Dashboard:** Rich (terminal), web UI if time permits

## Project Structure

```
├── AGENT.md              # AI agent routing file
├── docs/                 # Rules, metrics, strategy
├── src/                  # Application code
│   ├── proxy.py          # FastAPI proxy + anomaly detector
│   ├── simulator.py      # Runaway-agent simulator
│   ├── classifier.py     # Two-tier LLM classifier
│   ├── dashboard.py      # Live dashboard
│   ├── config.py         # All thresholds and settings
│   └── models.py         # Pydantic data models
└── demo/                 # Submission materials
```

## Built for

- [GOMYCODE × NVIDIA "Come Build with AI" Hackathon](https://hackathon.gomycode.com/) — 27 Sep 2026
- 🏆 Primary: Thunders Engineering Excellence Award
- 🎯 Secondary: NVIDIA Brev Breakthrough Award

## License

MIT
