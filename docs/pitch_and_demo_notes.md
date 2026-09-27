# Pitch Structure, Demo Metrics, and UX Notes

This document connects the hackathon pitch deck template, mentor feedback from the kickoff session, and the Fuse architecture into an actionable demo plan.

_Last updated: 2026-09-27_

---

## 1. Insights from the Mentor Session and Pitch Template

### Mentor Session Context
* **Session mentor:** Safae from EY Studio+ (Innovation and Experience Design).
* **Core feedback:** Technical capability alone does not win. The jury evaluates clarity, user experience, and practical relevance. Non-technical judges must immediately understand what broke and how the system reacted.
* **Format constraints:** Exactly 90 seconds for the demo video. The pacing must remain tight without dead air.
* **The boundary concept:** The mentor session discussed how to explain system boundaries to clients. For Fuse, the reverse proxy creates that boundary between an autonomous agent and external services.

### Pitch Template Alignment (Kawasaki 10-Slide Structure)
* **Slide 1 (Title):** Fuse. Intelligent circuit breaker for autonomous agents.
* **Slide 2 (Problem):** Autonomous agents panic on tool failures. They trigger unbacked retry storms, enter circular loops, and run up thousands of dollars in API bills or get accounts suspended.
* **Slide 3 (Value Proposition):** A transparent reverse proxy that stops destructive agent loops while passing legitimate parallel work.
* **Slide 4 (Underlying Technology):** Three-layer defense. Layer 1 hard counting ceiling, Layer 2 Jev typed classification, Layer 3 Gemini 3.8 Flash root-cause diagnosis.
* **Slide 5 (Business Value):** Prevents account bans (such as WhatsApp Business API or payment gateways) and protects API budgets without breaking agent workflows.
* **Slide 6 (Integration):** Zero code changes to downstream APIs. Configured as standard HTTP proxy middleware.
* **Slide 7 (Competitive Positioning):** Traditional rate limiters use static counters that block valid parallel bursts. Hard iteration caps kill long-running agent tasks. Fuse classifies intent before acting.
* **Slide 8 (Team):** Engineering and product roles.
* **Slide 9 (Key Metrics):** Latency overhead, false-positive rate, storm suppression percentage, and failsafe catch rate.
* **Slide 10 (Current Status):** Working prototype, passing test suite, 4-act live demo script, and SHA-256 audit logging.

---

## 2. Defined Demo Metrics

The demo video displays five concrete metrics on the terminal dashboard to give judges immediate proof:

| Metric | Measured Target | Significance |
|---|---|---|
| Decision Latency | Layer 1: <1 ms<br>Layer 2 (Jev): ~60 ms<br>Layer 3 (Gemini): ~900 ms | Proves Fuse introduces negligible delay to standard agent traffic. |
| False-Positive Rate | 0% (10 of 10 parallel search requests allowed) | Demonstrates that legitimate RAG fanouts run without interruption. |
| Storm Suppression | 100% (10 repeated 503 errors throttled with backoff) | Protects downstream APIs from cascading outages and prevents account suspensions. |
| Diagnostic Accuracy | 1 loop bug caught with root cause and remediation | Shows targeted use of generative AI for debugging rather than fixed rule matching. |
| Failsafe Catch Rate | 100% (calls 21 to 25 blocked at Layer 1) | Proves safety holds even if model calls fail or experience latency. |

---

## 3. User Experience and Screen Design

### Screen Layout for Recording
* **Left half of screen:** Agent simulator terminal executing requests.
* **Right half of screen:** Real-time Fuse dashboard displaying request counters, layer status, and decisions.

### Visual State Colors
Judges should follow the demo by color without needing to read small log text:
* **Green:** Parallel work forwarded directly.
* **Yellow:** Retry storm detected, backoff injected.
* **Blue:** Escape hatch triggered, Gemini diagnosing root cause.
* **Red:** Layer 1 hard ceiling tripped, HTTP 429 returned.

---

## 4. 90-Second Demo Storyboard

```
[00:00 - 00:15]  Problem: Agent tool panic, account bans, and blunt rate limiters.
[00:15 - 00:30]  Architecture: The 3-layer proxy boundary.
[00:30 - 01:05]  Live 4-Act Execution: Burst, storm, loop escape, and hard ceiling.
[01:05 - 01:20]  Proof: Dashboard metrics table and SHA-256 audit log.
[01:20 - 01:30]  Conclusion: Award fit and repository link.
```

### Cue Sheet

#### 00:00 to 00:15: The Problem Hook
* **Visual:** Code editor or terminal showing an agent looping on a failed tool call.
* **Spoken Cue:** "When autonomous agents encounter tool errors, they panic. They retry constantly, get trapped in loops, and burn API budgets until services ban their account. Standard rate limiters are blunt counters: they block legitimate parallel work and miss dangerous loops entirely."

#### 00:15 to 00:30: The Architecture
* **Visual:** Architecture graphic showing Agent -> Fuse Proxy (:8000) -> External APIs (:9000).
* **Spoken Cue:** "Fuse fixes this as an intelligent circuit breaker. Layer 1 is a deterministic hard ceiling. Layer 2 is Jev, classifying request patterns in milliseconds. Layer 3 is Gemini 3.8 Flash, diagnosing root causes when an unmodeled pattern appears."

#### 00:30 to 01:05: The Four Live Acts
* **Visual:** Screen switches to live terminal running `python demo/run_demo.py`.
* **Act 1 (0:30 to 0:38):** Agent fires 10 simultaneous searches. Dashboard lights green. Jev recognizes `parallel_work` and forwards all ten calls.
* **Act 2 (0:38 to 0:47):** Agent hits a broken 503 endpoint 10 times. Dashboard lights yellow. Jev flags `retry_storm` and injects exponential backoff.
* **Act 3 (0:47 to 0:56):** Agent alternates tools without making progress. Jev triggers the `unrecognized` escape hatch. Gemini 3.8 Flash returns the root cause and remediation advice.
* **Act 4 (0:56 to 0:65):** Rogue burst fires 25 rapid calls. Layer 1 hard ceiling activates. Pure arithmetic blocks calls 21 to 25 with HTTP 429. Zero AI bypass possible.

#### 01:05 to 01:20: Proof and Metrics
* **Visual:** Terminal prints the summary table from `/metrics`, followed by a fast view of `audit.jsonl`.
* **Spoken Cue:** "The live metrics confirm zero false positives on parallel work and complete downstream protection. Every event is hashed into a tamper-evident audit log."

#### 01:20 to 01:30: Wrap-up
* **Visual:** Title card with GitHub repository link and team contact details.
* **Spoken Cue:** "Fuse proves safety does not require sacrificing agent speed. Built for the Thunders Engineering Excellence and NVIDIA Brev awards. Thank you."

---

## 5. Submission Form Text

### Project Summary (116 words, under 150-word limit)
We help developers deploy autonomous AI agents without risking account suspensions or budget runaways. Our prototype, Fuse, is an intelligent reverse proxy that sits between agents and external APIs. We use Jev (TypeSafe AI) for sub-100ms typed pattern classification, paired with Gemini 3.8 Flash for deep root-cause diagnosis during anomalous loops. We tested the system against four agent failure profiles and confirmed zero false-positive blocks on legitimate parallel calls, alongside complete suppression of retry storms and rogue bursts. A deterministic mathematical ceiling always guards the system, ensuring protection holds even during complete model outages. Next step: add automated policy tuning based on historical agent call distributions.

### Prize Application Justifications (2-3 sentences each)

* **Thunders Engineering Excellence Award:**
  Fuse provides an inviolable deterministic ceiling that operates independently of any model output, ensuring reliable protection even when upstream networks or AI providers fail. We prove this live by subjecting the system to a 25-call rogue burst where arithmetic counters enforce hard blocks with zero AI bypass.

* **NVIDIA Brev Breakthrough Award:**
  Fuse implements a two-tier AI cascade where a fast classifier handles millisecond anomaly triage and Gemini 3.8 Flash conducts deep root-cause diagnosis upon escalation. The AI makes actionable operational decisions (allow, backoff, trip, and remediate) rather than returning passive text labels.
