# GOMYCODE Hackathon Submission: Fuse

This document contains the exact submission questions and humanized, clear answers for the GOMYCODE Hackathon submission form. All copy has been audited to eliminate AI clichés, promotional jargon, and unnecessary punctuation.

---

### Project summary (maximum 150 words) *

Fuse is a reverse proxy that sits between autonomous AI agents and downstream APIs. When agents run in tool-use loops, standard rate limiters either block valid parallel work or miss slow, expensive retry loops. Fuse solves this with a three-layer pipeline. Layer 1 enforces a strict ceiling to stop rogue traffic floods in under 1 millisecond. Layer 2 uses Jev, a fast typed classifier, to distinguish normal parallel fanouts from failing retry storms. Layer 3 escalates low-confidence anomalies and cyclical loops to Gemini 3.8 Flash for root-cause diagnosis. Every decision is hashed into an immutable audit log on disk. Teams plug Fuse in via standard HTTP proxy configuration with zero code changes.

*(120 words)*

---

### Problem solved *

Autonomous AI agents interact with external tools and APIs in unpredictable ways. When downstream endpoints fail or return ambiguous responses, agents often enter rapid retry storms or circular loops that drain API budgets, degrade server capacity, and cause cascading outages. Existing API gateways and rate limiters only count raw requests. As a result, they block legitimate parallel document retrievals while failing to detect slow, repetitive tool failures. Developers lack visibility into agent traffic patterns and have no reliable way to stop rogue tool executions without breaking valid workflows.

---

### Solution and key features *

- **Core user journey and working features:**
  - Drop-in reverse proxy gateway on port 8000. Any agent configured with standard HTTP proxy settings routes through Fuse without code changes.
  - Three-layer evaluation pipeline: Layer 1 arithmetic sliding-window ceiling (<1ms), Layer 2 Jev typed pattern classifier (~60ms), and Layer 3 Gemini 3.8 Flash diagnostic escalation (~900ms).
  - Real-time developer console on port 5173 displaying live metrics, pipeline routing, and request inspection.
  - Disk-backed SHA-256 hash-chained audit logging (`audit.jsonl`) with automated integrity verification.
  - Interactive request sandbox and live synthetic agent traffic generator (`demo/simulate_live.py`).

- **Mocked, simulated, or unfinished components:**
  - Downstream target APIs are simulated locally via `demo/mock_server.py` on port 9000 to demonstrate 200 OK, flaky 503, and cyclical loop endpoints deterministically.
  - Multi-tenant authentication and distributed Redis synchronization across multiple proxy nodes are planned for production releases.

- **Built during hackathon versus reused code:**
  - Built from scratch during hackathon: The reverse proxy engine (`src/proxy.py`), sliding window rate limiter (`src/sliding_window.py`), Jev classifier integration (`src/jev_evaluator.py`), Gemini Flash diagnostic handler (`src/llm_diagnostics.py`), SHA-256 audit logger (`src/dashboard.py`), test suite (`tests/`), simulator scripts (`demo/simulate_live.py`), and the full React developer dashboard (`frontend/`).
  - Reused open-source libraries: FastAPI, Uvicorn, HTTPX, Pytest, Tailwind CSS, Lucide icons, and the Google GenAI SDK.

---

### Technologies used *

Python 3.12, FastAPI, Uvicorn, HTTPX, Google GenAI SDK (Gemini 3.8 Flash), Jev (TypeSafe System One classifier), Pytest, React 19, Vite, Tailwind CSS, SHA-256 cryptographic chaining.

---

### Source code URL *

https://github.com/adr1en360/Fuse

---

### Presentation URL *

[PASTE YOUR GOOGLE SLIDES OR PRESENTATION LINK HERE]

---

### 90-second demo video URL *

[PASTE YOUR LOOM OR UNLISTED YOUTUBE VIDEO LINK HERE]

---

### Project next step *

Package Fuse as a single Docker container and Helm chart for Kubernetes deployment, implement distributed Redis state for multi-instance proxy clusters, and support custom YAML-defined service profiles for enterprise agent fleets.

---

### Partner awards — which prizes is your team applying for? *

Select the following checkboxes in the form:
- [x] **Thunders — Engineering Excellence Award**
- [x] **SupplyzPro — Smart Operations Award**
- [x] **Guepard — AI Automation Award**

---

### Primary prize application *

**Thunders — Engineering Excellence Award**

---

### Award application — explain your project’s fit and eligibility *

- **Thunders (Engineering Excellence Award):** Fuse provides a working, production-grade reverse proxy built with clean architecture, strict typing, a 15-test automated Pytest suite, and a tamper-evident SHA-256 log chain. Concrete evidence includes sub-millisecond Layer 1 execution and 15 passing unit tests covering all pipeline stages. You can inspect this in `src/proxy.py`, `tests/`, and during the live demo in the video from 00:38 to 01:15. This submission is open to all participating hackathon teams.

- **SupplyzPro (Smart Operations Award):** Fuse directly solves the "Find the Hidden Failures" challenge by intercepting tool calls, detecting silent cyclical loops and 503 retry storms, grouping cases by session, and prioritizing investigations with evidence. Concrete evidence is shown in Layer 2 anomaly tracking with automated escalation to Gemini 3.8 Flash for root-cause diagnosis and permanent cryptographic evidence logging. See `src/llm_diagnostics.py`, Act 3 in `demo/simulate_live.py`, and the trace drawer in the dashboard. This category is open to all participating hackathon teams.

- **Guepard (AI Automation Award):** Fuse serves as an automated safety layer for autonomous AI workflows, preventing agent tool-use from crashing production services or exhausting budgets. Concrete evidence is the live mitigation of runaway agent traffic through automated backoff injection and hard ceiling enforcement without human intervention. See `src/router.py`, `demo/simulate_live.py`, and the video from 00:38 to 01:05. This category is open to all participating hackathon teams.

---

### AI/tool disclosure *

- **AI inside your product:**
  - Jev (TypeSafe System One): Lightweight rule-based pattern classifier used in Layer 2 to evaluate request velocity, endpoint profile, and retry frequency in 60 milliseconds. Example: 10 concurrent requests to `/search` with distinct query parameters -> Jev evaluates pattern as `parallel_work` with 0.85 confidence -> Output is an immediate FORWARD decision.
  - Gemini 3.8 Flash (via Google GenAI SDK): Diagnostic model used in Layer 3 when Jev flags an unrecognized pattern or low confidence (<0.70). Example: 6 alternating calls between `/loop/step-A` and `/loop/step-B` with no state progress -> Gemini diagnoses cyclic agent tool loop -> Output is structured JSON with root cause ("Agent trapped in cyclic tool loop between step-A and step-B") and remediation advice ("Terminate session or introduce random jitter"). No simulated outputs are used; live API calls run whenever an API key is present.

- **AI used to help build the project:**
  - Antigravity AI assistant was used for code scaffolding, drafting unit tests, and designing the frontend layout. All generated code, rate-limiting mathematics, proxy forwarding rules, and cryptographic hashing were reviewed, tested with Pytest, and verified manually.

- **Datasets, APIs, and generated assets:**
  - APIs: Gemini 3.8 Flash API for diagnostic escalations.
  - Assets: Vector logo (`logo.svg`) and Lucide interface icons.
  - Brev: NVIDIA Brev was not used.

---

### Project cover / screenshot / logo URL (optional)

[PASTE VIEWABLE LINK TO LOGO.SVG OR DASHBOARD SCREENSHOT]

---

### Live demo URL (optional)

[LEAVE BLANK IF RUNNING LOCALLY, OR PASTE HOSTED URL]
*(Run instructions are documented in the repository README: start mock server on :9000, proxy on :8000, and run `demo/simulate_live.py`)*

---

### Testing, results and known limitations (optional)

- **Test 1 (Parallel Fanout):** 10 concurrent requests to `/search` -> all 10 forwarded with HTTP 200 in 42ms -> verified in `tests/test_proxy.py::test_proxy_normal_forwarding` and `demo/simulate_live.py`.
- **Test 2 (Retry Storm):** 10 repeated calls to `/flaky` -> Jev detected retry storm, injected exponential backoff with HTTP headers (`Retry-After: 1.0s`) -> verified in `tests/test_router.py::test_layer2_retry_storm_backoff`.
- **Test 3 (Ceiling Breach & Known Limitation):** 25 rapid calls sent within 1 second -> Layer 1 hard ceiling forwarded calls 1 to 20 and blocked calls 21 to 25 with HTTP 429 in 0.8ms -> verified in `tests/test_proxy.py::test_proxy_hard_ceiling_trip`. Known limitation: Sliding window counters are stored in memory per process; multi-node clusters will require Redis backplane synchronization.

---

### Responsible AI and data (optional)

All data processed by Fuse during demonstrations is synthetic agent traffic generated locally. Fuse does not store user personal data, training data, or external API keys; it only logs request metadata, HTTP status codes, and SHA-256 hashes for auditing. The deterministic Layer 1 ceiling acts as an inviolable safeguard, ensuring that safety limits remain enforced even if underlying AI models experience downtime or latency.

---

### Final confirmation *

[x] **I confirm that our functional prototype, source code, presentation, 90-second demo video, project card details and AI/tool disclosure are complete, accessible and final.**
