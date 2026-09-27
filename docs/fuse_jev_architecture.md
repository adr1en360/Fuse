# Fuse Architecture — Intelligent Circuit Breaker with Jev & Gemini

> **Executive Overview:** Fuse is an intelligent, confidence-gated proxy that sits between autonomous AI agents and downstream APIs.
> It uses a strict 3-tier safety hierarchy:
> 1. **Layer 1: Deterministic Hard Ceiling** — pure sliding-window counting, inviolable, zero AI override.
> 2. **Layer 2: Jev (TypeSafe AI System One)** — fast typed primitives (`Choice`, `Score`, `Noul`) with calibrated confidence, context-aware service profiling, and an `unrecognized` escape hatch.
> 3. **Layer 3: Gemini 3.8 Flash (Deep Root-Cause Engine)** — invoked only when Jev escapes or is uncertain, conserving API quotas while diagnosing complex failures.

---

## 1. High-Level System Context

```mermaid
graph LR
    subgraph CLIENT["Agent Space"]
        AGENT["🤖 Autonomous Agent<br/>(LangChain / AutoGen / Claude / etc.)"]
    end

    subgraph FUSE_SYSTEM["🛡️ Fuse Proxy (localhost:8000)"]
        PROXY["Reverse Proxy Gateway<br/>(FastAPI / HTTPX)"]
        CACHE["⚡ In-Flight Burst Cache<br/>(De-duplicates concurrent calls)"]
        TRACKER["⏱️ Sliding Window Tracker<br/>(Deterministic L1 Counting)"]
        ROUTER["🔀 Confidence Router<br/>(Escape Hatch & Decision Gate)"]
        DASH["📊 Live Rich Dashboard<br/>(Operational Metrics)"]
        AUDIT["🔐 Audit Engine<br/>(SHA-256 Tamper-Evident Chain)"]
    end

    subgraph DECISION_ENGINES["AI Safety Hierarchy"]
        JEV["⚡ Jev System One<br/>(TypeSafe AI API)<br/>Choice / Score / Noul"]
        GEMINI["🧠 Gemini 3.8 Flash<br/>(Google GenAI API)<br/>Root-Cause & Remediation"]
        HUMAN["👤 Human-in-the-Loop<br/>(Critical Incident Alert)"]
    end

    subgraph TARGETS["External Services (:9000)"]
        API1["🌐 Search / Vector DB<br/>(Read-Intensive)"]
        API2["💳 Stripe / Billing API<br/>(High-Consequence)"]
        API3["🛠️ General REST Endpoints<br/>(Standard)"]
    end

    AGENT -->|"HTTP Outbound Tool Calls"| PROXY
    PROXY --> TRACKER
    TRACKER --> CACHE
    CACHE -->|"Anomaly Detected"| JEV
    JEV -->|"Typed Decisions + Confidence"| ROUTER
    ROUTER -.->|"Escape: 'unrecognized' OR Low Conf"| GEMINI
    ROUTER -.->|"Severity=2 & Anomaly > 0.85"| HUMAN
    ROUTER -->|"FORWARD / BACKOFF"| PROXY
    PROXY -->|"Allowed Traffic"| API1 & API2 & API3
    API1 & API2 & API3 -->|"Downstream Response"| PROXY
    PROXY -->|"Transparent Response or 429"| AGENT
    PROXY --> DASH
    PROXY --> AUDIT
```

---

## 2. End-to-End Decision Flowchart

This flowchart illustrates every branch a call can take, including the **Service Profile Injection**, the **Burst Cache**, the **Layer 2 Escape Hatch**, and the **Deterministic Layer 1 Hard Ceiling**.

```mermaid
flowchart TD
    START(["🤖 Agent makes API Request"]) --> PARSE["📝 Inspect Request<br/>Extract session_id, endpoint, method, arg_hash"]
    PARSE --> PROFILE["🏷️ Infer Service Profile<br/>read_intensive / standard / high_consequence"]
    
    PROFILE --> L1_CHECK{"🔴 LAYER 1: Hard Ceiling?<br/>≥ 20 calls in 10s?<br/>(Pure Counting)"}
    
    L1_CHECK -->|"YES (Tripped)"| L1_BLOCK["🚫 429 Hard Block<br/>Inviolable ceiling enforced.<br/>Zero AI model bypass."]
    L1_BLOCK --> LOG_AUDIT["🔐 Cryptographic Audit Log<br/>(SHA-256 chained entry)"]
    L1_BLOCK --> RESP_429(["Return 429 to Agent<br/>Retry-After header attached"])

    L1_CHECK -->|"NO (Under Ceiling)"| ANOM_CHECK{"🟡 Anomaly Threshold?<br/>≥ 8 calls in 5s?<br/>(Call Velocity Spike)"}

    ANOM_CHECK -->|"NO (Normal Rate)"| FWD_NORMAL["✅ FORWARD directly to target<br/>Zero AI overhead, zero latency"]
    FWD_NORMAL --> LOG_AUDIT
    FWD_NORMAL --> RESP_200(["Return Downstream Response"])

    ANOM_CHECK -->|"YES (Velocity Spike)"| CACHE_CHECK{"⚡ Session Burst Cache?<br/>Decision evaluated in last 3s?"}

    CACHE_CHECK -->|"Cache Hit"| REUSE["♻️ Reuse Cached Decision<br/>Saves API credits on parallel bursts"]
    CACHE_CHECK -->|"Cache Miss"| BUILD_STATE["📦 Build Jev State<br/>- service_profile (category, cost)<br/>- call_window (last 10 calls)<br/>- ceiling_usage (e.g. 8/20)"]

    BUILD_STATE --> JEV_CALL["⚡ Jev System One Evaluation<br/>(3 Typed Questions in Parallel)"]

    subgraph JEV_EVAL["Jev 3-Primitive Evaluation"]
        Q1["<b>Choice:</b> pattern_type<br/>parallel_work / retry_storm /<br/>loop_bug / <i>unrecognized</i>"]
        Q2["<b>Noul:</b> is_genuine_anomaly<br/>Calibrated probability (0.0 to 1.0)"]
        Q3["<b>Score:</b> severity<br/>0=harmless / 1=concerning / 2=dangerous"]
    end

    JEV_CALL --> JEV_EVAL
    JEV_EVAL --> ROUTE_GATE{"🔀 Confidence Router"}

    REUSE --> ROUTE_GATE

    ROUTE_GATE -->|"High Conf (≥ 0.7)<br/>+ parallel_work"| ACT_FORWARD["✅ FORWARD Burst<br/>Legitimate concurrent retrieval"]
    ROUTE_GATE -->|"High Conf (≥ 0.7)<br/>+ retry_storm"| ACT_BACKOFF["⏳ BACKOFF Enforced<br/>Inject exponential sleep & Retry-After"]
    ROUTE_GATE -->|"High Conf (≥ 0.7)<br/>+ loop_bug"| ACT_TRIP["🛑 TRIP Circuit Breaker<br/>Stop runaway loop token burn"]
    ROUTE_GATE -->|"Severity ≥ 1.5<br/>AND Anomaly > 0.85"| ACT_HUMAN["👤 ESCALATE TO HUMAN<br/>Emergency alert with Jev context"]

    ROUTE_GATE -->|"Choice == 'unrecognized'<br/>(Escape Hatch)<br/>OR Confidence < 0.7"| ESCAPE_LLM["🧠 LAYER 3: Gemini 3.8 Flash<br/>Full session history & payload diffs<br/>Root-cause diagnosis & remediation"]

    ESCAPE_LLM --> LLM_VERDICT["Synthesize Gemini Verdict<br/>FORWARD / BACKOFF / BLOCK / AUTO_REMEDIATE"]

    ACT_FORWARD --> FWD_DOWNSTREAM["🌐 Forward to Downstream API"]
    ACT_BACKOFF --> FWD_DOWNSTREAM
    ACT_TRIP --> RESP_429
    ACT_HUMAN --> RESP_429
    LLM_VERDICT --> FWD_DOWNSTREAM
    LLM_VERDICT --> RESP_429

    FWD_DOWNSTREAM --> LOG_AUDIT
    LOG_AUDIT --> RESP_200

    style L1_CHECK fill:#ff4757,color:#fff
    style L1_BLOCK fill:#ff4757,color:#fff
    style ANOM_CHECK fill:#ffa502,color:#000
    style JEV_CALL fill:#E551BA,color:#fff
    style Q1 fill:#E551BA,color:#fff
    style Q2 fill:#E551BA,color:#fff
    style Q3 fill:#E551BA,color:#fff
    style ESCAPE_LLM fill:#2ed573,color:#000
    style ROUTE_GATE fill:#1e90ff,color:#fff
    style ACT_FORWARD fill:#2ed573,color:#000
    style ACT_BACKOFF fill:#ffa502,color:#000
    style ACT_TRIP fill:#ff4757,color:#fff
    style ACT_HUMAN fill:#3742fa,color:#fff
```

---

## 3. The 3-Tier Layered Architecture

```mermaid
graph TB
    subgraph L1["Tier 1: Deterministic Hard Ceiling (Strict Counting)"]
        direction LR
        L1_DESC["• Pure sliding-window arithmetic<br/>• Zero AI model intervention<br/>• Guarantees absolute safety floor<br/>• Cannot be overridden by agent or model"]
    end

    subgraph L2["Tier 2: Jev System One (Fast Typed Decision Engine)"]
        direction LR
        L2_CHOICE["<b>Choice (pattern_type):</b><br/>• parallel_work<br/>• retry_storm<br/>• loop_bug<br/>• <i>unrecognized (Escape)</i>"]
        L2_NOUL["<b>Noul (is_anomaly):</b><br/>• Calibrated probability [0.0 - 1.0]<br/>• Differentiates safe bursts from abuse"]
        L2_SCORE["<b>Score (severity):</b><br/>• 0: Harmless<br/>• 1: Concerning<br/>• 2: Dangerous"]
        L2_CONF["<b>Confidence Gating:</b><br/>• Conf ≥ 0.7 → Act directly in ms<br/>• Conf < 0.7 → Escalate to Layer 3"]
    end

    subgraph L3["Tier 3: Gemini 3.8 Flash (Deep Root-Cause Reasoning)"]
        direction LR
        L3_DIAG["<b>Session Inspection:</b><br/>• Analyzes full call sequence<br/>• Payload & hash diffs<br/>• Pinpoints root cause"]
        L3_REM["<b>Actionable Remediation:</b><br/>• Auto-remediation advice<br/>• Prompt error feedback<br/>• Circuit trip recommendation"]
    end

    L1 -->|"Under ceiling & velocity spike"| L2
    L2 -->|"Choice == 'unrecognized' OR Low Confidence"| L3
    L2 -->|"High Confidence Decision"| ENFORCE["Action Enforced"]
    L3 --> ENFORCE

    style L1 fill:#ff475715,stroke:#ff4757,stroke-width:2px
    style L2 fill:#E551BA15,stroke:#E551BA,stroke-width:2px
    style L3 fill:#2ed57315,stroke:#2ed573,stroke-width:2px
```

---

## 4. Context-Aware Service Profile Injection

Why can Jev distinguish between safe bursts and dangerous storms? Because **State is Context**. Fuse injects downstream service characteristics into Jev's evaluation:

```mermaid
graph LR
    subgraph REQUEST["Inbound Request"]
        REQ["Method: POST<br/>Path: /charge<br/>Header: X-Fuse-Service: payments"]
    end

    subgraph PROFILER["Service Profiler"]
        INFER["Automatic Inference Engine"]
    end

    subgraph PROFILES["Service Archetypes"]
        P1["<b>read_intensive</b><br/>• High concurrency tolerance<br/>• Low cost sensitivity<br/>• Safe parallel retrieval"]
        P2["<b>standard_api</b><br/>• Balanced REST tolerance<br/>• Medium retry sensitivity"]
        P3["<b>high_consequence</b><br/>• Zero retry tolerance on errors<br/>• High financial / side-effect risk<br/>• Immediate backoff enforcement"]
    end

    subgraph JEV_INPUT["Jev State"]
        STATE["service_profile: {<br/>  name: 'payments_api',<br/>  category: 'high_consequence',<br/>  is_mutating: true,<br/>  cost_tier: 'high'<br/>}<br/>call_window: [...]<br/>ceiling_usage: '8/20'"]
    end

    REQ --> INFER
    INFER --> P3
    P3 --> STATE
    STATE --> JEV["⚡ Jev System One Model"]
```

---

## 5. Quota-Protective Burst De-Duplication Cache

To guarantee that autonomous agents executing concurrent parallel bursts do not burn through model API quotas, Fuse deploys an in-flight burst cache:

```mermaid
sequenceDiagram
    autonumber
    actor Agent as 🤖 Agent
    participant Proxy as 🛡️ Fuse Proxy
    participant Cache as ⚡ Burst Cache
    participant Jev as ⚡ Jev (TypeSafe)
    participant Target as 🌐 Downstream API

    Note over Agent,Proxy: Parallel Burst (10 concurrent requests arrive at t=0ms)
    Agent->>Proxy: Request #1 (query=doc1)
    Proxy->>Cache: Check session decision
    Cache-->>Proxy: Miss (First call of burst)
    Proxy->>Jev: Evaluate state (1 API call)
    Jev-->>Proxy: Choice: parallel_work (conf: 0.85)
    Proxy->>Cache: Store decision (valid for 3.0s)
    Proxy->>Target: Forward Request #1
    Target-->>Proxy: 200 OK
    Proxy-->>Agent: 200 OK

    Note over Agent,Proxy: Concurrent Requests #2 through #10 arrive immediately
    loop Requests #2 to #10
        Agent->>Proxy: Request #N (query=docN)
        Proxy->>Cache: Check session decision
        Cache-->>Proxy: HIT! (Reuses parallel_work verdict)
        Note over Proxy: ZERO calls to Jev! Zero model quota consumed!
        Proxy->>Target: Forward Request #N
        Target-->>Proxy: 200 OK
        Proxy-->>Agent: 200 OK
    end
```

---

## 6. The 4 Live Demonstration Acts (How They Map to the Layers)

```mermaid
graph TD
    subgraph ACT1["Act 1: Parallel Work Burst"]
        A1["10 concurrent RAG searches<br/>(Diverse arg hashes)"] --> A1_RES["Layer 2 (Jev System One)<br/>Choice: <b>parallel_work</b> (conf: 0.85)<br/>Action: <b>FORWARD</b> (Safe Burst)"]
    end

    subgraph ACT2["Act 2: Stuck Retry Storm"]
        A2["10 identical calls to failing 503<br/>(Identical arg hash)"] --> A2_RES["Layer 2 (Jev System One)<br/>Choice: <b>retry_storm</b> (conf: 0.92)<br/>Action: <b>BACKOFF</b> (4.0s Sleep + Header)"]
    end

    subgraph ACT3["Act 3: Loop Bug & Escape Hatch"]
        A3["Alternating tool cycle<br/>(step-A -> step-B with no progress)"] --> A3_RES["Layer 2 triggers <b>'unrecognized' Escape</b><br/>→ Layer 3 (Gemini 3.8 Flash)<br/>Action: <b>CIRCUIT TRIP (429)</b> with advice"]
    end

    subgraph ACT4["Act 4: Catastrophic Rogue Burst"]
        A4["25 rapid calls in < 1 second<br/>(Exceeds ceiling of 20)"] --> A4_RES["Layer 1 (Deterministic Ceiling)<br/>Arithmetic: 25 ≥ 20<br/>Action: <b>HARD 429 BLOCK</b> (Zero AI bypass)"]
    end

    style ACT1 fill:#2ed57315,stroke:#2ed573
    style ACT2 fill:#ffa50215,stroke:#ffa502
    style ACT3 fill:#E551BA15,stroke:#E551BA
    style ACT4 fill:#ff475715,stroke:#ff4757
```

---

## 7. Cryptographic Tamper-Evident Audit Trail

Every event processed by Fuse is appended to `audit.jsonl` with SHA-256 chain hashing, ensuring accountability for responsible AI operations:

```mermaid
graph LR
    subgraph RECORD_N_MINUS_1["Audit Record #1"]
        D1["Data: Session test-session<br/>Action: FORWARD<br/>Layer: LAYER_1_NORMAL"]
        H1["chain_hash: 0e3febcbb11e..."]
    end

    subgraph RECORD_N["Audit Record #2"]
        D2["Data: Session test-ceiling<br/>Action: BACKOFF<br/>Layer: LAYER_2_JEV_DIRECT"]
        P2["prev_hash: 0e3febcbb11e..."]
        H2["chain_hash: SHA256(prev_hash + JSON)"]
    end

    subgraph RECORD_N_PLUS_1["Audit Record #3"]
        D3["Data: Session test-loop<br/>Action: BLOCK<br/>Layer: LAYER_3_GEMINI"]
        P3["prev_hash: 9fa980f2322f..."]
        H3["chain_hash: SHA256(prev_hash + JSON)"]
    end

    H1 --> P2
    H2 --> P3
```

---

## 8. Codebase Topology & Component Map

```mermaid
graph TB
    subgraph "src/"
        CFG["config.py<br/>Loads .env & thresholds"]
        MOD["models.py<br/>Pydantic schemas & ServiceProfile"]
        WIN["sliding_window.py<br/>Layer 1 Sliding Window Tracker"]
        JEV_CLI["jev_client.py<br/>TypeSafe SDK client (Choice, Score, Noul)"]
        LLM_CLI["llm_client.py<br/>Gemini 3.8 Flash root cause doctor"]
        ROUT["router.py<br/>Confidence gating & escape logic"]
        DASH_MOD["dashboard.py<br/>Rich UI & SHA-256 audit logger"]
        PROXY_MOD["proxy.py<br/>FastAPI reverse proxy gateway"]
        SIM_MOD["simulator.py<br/>Synthetic agent traffic generator"]
    end

    subgraph "demo/"
        MOCK["mock_server.py<br/>Port 9000 downstream target"]
        RUN["run_demo.py<br/>4-act automated runner"]
        SCR["demo_script.md<br/>90-second video voiceover"]
    end

    subgraph "tests/"
        T_WIN["test_sliding_window.py"]
        T_ROUT["test_router.py"]
        T_PROXY["test_proxy.py"]
    end

    PROXY_MOD --> WIN
    PROXY_MOD --> JEV_CLI
    PROXY_MOD --> ROUT
    ROUT --> LLM_CLI
    PROXY_MOD --> DASH_MOD
    RUN --> SIM_MOD
    SIM_MOD --> PROXY_MOD
    PROXY_MOD --> MOCK
```
