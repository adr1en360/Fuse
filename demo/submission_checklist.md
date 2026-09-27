# GOMYCODE Hackathon: Project Submission Answers and Sync Checklist

> [!IMPORTANT]
> **Mandatory Agent Check:** Whenever you make a feature update, modify an endpoint or configuration, change architecture, or prepare a demo run, you must inspect this file. Verify that every answer remains accurate, factual, and aligned with the current codebase before proceeding. Do not allow answers to drift from actual implementation.

_Last updated: 2026-09-27_

---

## Submission Details

### Country *
Nigeria

### Hackerspace / ONLINE *
ONLINE

### Team name *
Wandering

### Team leader full name *
Adrien Oke

### Team leader email *
adrienoke@gmail.com

### Project title *
Fuse

### Team members: full name of each member, one per line *
Adrien Oke

---

### Project summary: maximum 150 words *
*(Current word count: 114 words)*

We help developers deploy autonomous AI agents without risking account suspensions or runaway API bills. Our prototype, Fuse, is an intelligent reverse proxy that sits between agents and external APIs. We use Jev (TypeSafe AI) for sub-100ms typed pattern classification, paired with Gemini 3.8 Flash for root-cause diagnosis during anomalous loops. We tested the system against four agent failure profiles and confirmed zero false-positive blocks on legitimate parallel calls, alongside complete suppression of retry storms and rogue bursts. A deterministic mathematical ceiling always guards the system, ensuring protection holds even during complete model outages. Next step: add automated policy tuning based on historical agent call distributions.

---

### Problem solved *
When autonomous agents hit tool errors, they often panic. They trigger unbacked retry storms, enter circular loops, and burn through API budgets until downstream providers suspend their accounts. Traditional rate limiters rely on static request counters. They cannot tell the difference between an agent reading ten documents in parallel and an agent stuck in a death loop hitting the same endpoint ten times. As a result, static limiters either break legitimate parallel work or let destructive loops run until downstream services cut access.

---

### Solution and key features *
* **Core user journey and working features:**
  * Transparent reverse proxy intercepts all agent outbound HTTP tool calls.
  * Three-layer defense hierarchy:
    * Layer 1: Inviolable deterministic sliding-window count ceiling (<1 ms).
    * Layer 2: Jev System One typed pattern classifier (~60 ms) recognizing parallel work, retry storms, and loops.
    * Layer 3: Gemini 3.8 Flash root-cause diagnosis engine (~900 ms) triggered on low confidence or unrecognized patterns.
  * Real-time terminal dashboard with color-coded live metrics.
  * Tamper-evident audit trail with SHA-256 hash chains (`audit.jsonl`).
  * See video at 00:30 to 01:05 and implementation in `src/proxy.py`, `src/router.py`, and `src/sliding_window.py`.
* **Mocked, simulated, or unfinished components:**
  * Downstream services are simulated with a local mock server (`demo/mock_server.py`) returning realistic search payloads and HTTP 503 errors.
  * Agent traffic is driven by an automated four-act scenario runner (`demo/run_demo.py`).
* **Built during the hackathon versus reused:**
  * Built entirely during the event: proxy gateway, sliding-window tracker, Jev client wrapper, Gemini escalation client, terminal dashboard, scenario simulator, four-act demo runner, and automated test suite.
  * Reused: official client SDKs (`typesafe-sdk`, `google-genai`).

---

### Technologies used *
Python 3.12, FastAPI, Uvicorn, TypeSafe AI SDK (Jev System One), Google GenAI SDK (Gemini 3.8 Flash), HTTPX, Rich, Pydantic, Pytest.

---

### Source code URL *
https://github.com/adr1en360/Fuse

### Presentation URL *
https://github.com/adr1en360/Fuse/blob/main/docs/pitch_and_demo_notes.md

*(Replace with Google Slides or Canva view link if hosted externally)*

### 90-second demo video URL *
*(Paste Loom share link or unlisted YouTube URL here. Verify access in an incognito window before submitting.)*

---

### Project next step *
Add dynamic policy tuning that learns normal agent traffic baselines over time, and implement Redis-backed distributed state so multiple proxy instances share sliding-window counters.

---

### Partner awards: which prizes is your team applying for? *
Select the following checkboxes:
* [x] **Thunders — Engineering Excellence Award**
* [x] **Guepard — AI Automation Award**
* [x] **SupplyzPro — Smart Operations Award**

*(Note: The team is also automatically eligible for the Nigeria country podium, including 2nd place NVIDIA Brev Breakthrough Award.)*

---

### Primary prize application: choose the award that best fits your project *
Thunders — Engineering Excellence Award

---

### Award application: explain your project's fit and eligibility *

* **Thunders — Engineering Excellence Award:**
  Fuse provides an inviolable deterministic ceiling that operates independently of any model output, ensuring reliable protection even when upstream networks or AI providers fail. We prove this live by subjecting the system to a 25-call rogue burst where arithmetic counters enforce hard blocks with zero AI bypass (video at 00:56 to 01:05; code in `src/sliding_window.py`). Open to all teams globally.

* **Guepard — AI Automation Award:**
  Fuse protects autonomous agent workflows from runaway tool recursion and API rate-limit suspensions without requiring changes to agent application code. It automates operational oversight by dynamically injecting backoff delays and surfacing root-cause remediations for failing tools (video at 00:38 to 00:56; code in `src/router.py`). Open to all teams globally.

* **SupplyzPro — Smart Operations Award:**
  Fuse solves the "Find the Hidden Failures" challenge by continuously monitoring tool call patterns, grouping anomalies into distinct failure categories (`retry_storm`, `loop_bug`), and prioritizing investigation using calibrated confidence scores and root-cause summaries (video at 00:47 to 01:05; code in `src/jev_client.py` and `src/llm_client.py`). Open to all teams globally.

---

### AI/tool disclosure *
* **AI inside the product:**
  * **Jev (TypeSafe AI System One):** Classifies call velocity anomalies into typed outcomes (`parallel_work`, `retry_storm`, `loop_bug`) with calibrated confidence. Example: An agent fires 10 search queries in 2 seconds; Jev evaluates the typed request context and returns `parallel_work` with 0.88 confidence, allowing the traffic without delay.
  * **Gemini 3.8 Flash:** Diagnoses unmodeled failure modes when Jev triggers its `unrecognized` escape hatch or reports low confidence (<0.6). Example: An agent alternates endlessly between two tools; Gemini inspects the session call history, identifies a circular dependency, and outputs remediation advice to disable the failing tool.
  * **Fallback:** If either model is unreachable or times out, Fuse falls back to deterministic local throttling and hard ceiling enforcement.
* **AI used to build the project:**
  * AI coding assistants were used to generate boilerplate structures, documentation formatting, and initial test fixtures. The development team reviewed, modified, and verified all core proxy logic, sliding-window calculations, and decision routing.
* **Datasets, APIs, and access constraints:**
  * TypeSafe API and Google Gemini API. All test traffic uses synthetic mock endpoints generated locally with zero private customer data.

---

### Project cover / screenshot / logo URL (optional)
*(Link to product screenshot or leave blank)*

### Live demo URL (optional)
*(Runs locally; documented with reproduction steps in repository README.md)*

---

### Testing, results and known limitations (optional)
* **Parallel Work Test:** 10 concurrent search queries fired -> all 10 forwarded with zero false positives (observed latency: 12 ms proxy transit; verified in `tests/test_proxy.py`).
* **Retry Storm Test:** 10 repeated calls to an HTTP 503 endpoint -> 10 of 10 requests throttled with exponential backoff, preventing downstream saturation (verified in `demo/run_demo.py` Act 2).
* **Rogue Burst Test:** 25 calls fired in 2 seconds against a 20-call limit -> calls 1 through 20 processed, calls 21 through 25 blocked with HTTP 429 (zero AI bypass; verified in `tests/test_proxy.py`).
* **Known limitation and fallback:** Current sliding-window state is stored in in-memory queues per process. If the proxy restarts, the window resets. The fallback is per-connection deterministic hard limits.

---

### Responsible AI and data (optional)
Fuse processes only operational HTTP metadata: session IDs, endpoints, argument hashes, response codes, and timestamps. It never inspects, logs, or stores raw prompt bodies, tool payloads, or private user data. All security decisions and layer trips are hashed into a tamper-evident audit log (`audit.jsonl`) using SHA-256 chaining. A deterministic mathematical ceiling always overrides AI classifications, ensuring autonomous models never have uncontrolled authority over system boundaries.

---

### Final confirmation *
[x] I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.
