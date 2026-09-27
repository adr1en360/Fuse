# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
AI engineers, agent developers, and platform operators who deploy autonomous LLM agents that invoke external tools and HTTP APIs.

## Product Purpose
Fuse is an inline reverse proxy and circuit breaker for AI agents. It protects downstream APIs and agent budgets by detecting and breaking retry storms, error loops, and runaway token consumption before damage occurs.

## Positioning
Static HTTP rate limiters only count raw requests per minute. Fuse analyzes agent execution context through a multi-tier confidence pipeline:
1. Layer 1: Deterministic ceilings for burst limits and token quotas.
2. Layer 2: Fast typed classification for repeated failure signatures and loop patterns.
3. Layer 3: Gemini 3.8 Flash semantic investigation for root-cause diagnosis when confidence is ambiguous.
Every decision is written to an append-only, SHA-256 hash-chained audit ledger.

## Operating Context
- Deployed as a transparent reverse proxy between AI agent runtimes and upstream HTTP services.
- Inspected and managed through a browser-based developer console on port 5173.
- Runs locally or on cloud container infrastructure with minimal latency overhead.

## Capabilities and Constraints
- Intercepts inbound and outbound agent HTTP requests on port 8000.
- Applies service profiles: read_intensive, standard_api, high_consequence.
- Maintains a cryptographic SHA-256 hash-chained JSONL audit trail in audit.jsonl.
- Simulates and verifies 4 operational scenarios (Acts 1 to 4): normal traffic, retry storms, state drift loops, and token runaways.
- Requires Python 3.10+ and a valid Gemini API key for Layer 3 LLM semantic analysis.

## Brand Commitments
- Name: Fuse
- Tagline: Agent Circuit Breaker & Gateway
- Vector Logo: Geometric dual-circuit fuse mark (logo.svg)
- Color Palette: Electric Cyan (#74cfd8), Deep Dark (#05080e), White (#fefefe)

## Evidence on Hand
- Passing automated test suite covering proxy routing, circuit state transitions, and cryptographic audit hashing in tests/.
- Working 4-act scenario simulator in demo/mock_server.py and demo/demo_runner.py.
- Single-page React console with live telemetry, request sandbox, audit forensics, and policy configuration in frontend/.

## Product Principles
- Deterministic rules run first: block obvious failures immediately without calling an LLM.
- Cryptographic accountability: every trip, bypass, and throttle must verify against a tamper-evident hash chain.
- Explain every decision: operators must see why a request was blocked, which layer triggered it, and what policy threshold was crossed.
- Zero agent code changes: agents point their base URL to the proxy without modifying tool calling logic.

## Accessibility & Inclusion
- High-contrast dark theme meeting WCAG AA standards.
- Semantic HTML navigation, readable monospace code displays, and keyboard-accessible controls.
