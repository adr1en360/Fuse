# Evaluation Metrics — 100-Point Rubric + Jev Strategy

Source: [hackathon.gomycode.com/onboarding#judging](https://hackathon.gomycode.com/onboarding#judging)

## Rubric

| # | Category | Points | What Judges Want | How Jev Wins It |
|---|----------|--------|------------------|-----------------|
| 1 | **Problem + User Value** | 20 | Clear need, credible user, practical value | "Your AI agent quietly gets your WhatsApp Business account suspended." Name a real, named scenario — not abstract "DDoS prevention." |
| 2 | **Functional Execution** | 20 | Core experience works live, beyond a slide deck | Live proxy intercepts calls. Real trigger fires. Breaker trips visibly on dashboard. No slides, no screenshots. |
| 3 | **Quality of AI Use** | 20 | Quality and relevance of actual AI contribution | Tier 1 fast classifier choosing between 3 remediations, not a fixed rule. Tier 2 thinking model for root-cause analysis on escalation. AI makes a *decision*, not just a label. |
| 4 | **Testing + Reliability** | 15 | Failure modes, cost, speed, fallbacks considered | Hard deterministic ceiling fires regardless of model output. Demo it: kill the model, ceiling still catches the burst. This is the Thunders story. |
| 5 | **Experience + Demo** | 15 | Understandable, usable, clearly demonstrated in 90s | Scripted demo: normal → burst → catch → fallback → circle back. Dashboard reacts in <1s. No narration needed to understand what happened. |
| 6 | **Responsible AI + Data** | 10 | Privacy, bias, consent, safety, human oversight | Metadata only (never payload content). Logged and auditable. AI never has the final word — hard ceiling always overrides. |

## Point Allocation Strategy

**Must-win categories (60 pts):** Functional Execution (20) + Quality of AI Use (20) + Testing + Reliability (20→15, but the extra 5 comes from actually demoing the fallback).

**High-confidence categories (25 pts):** Problem + User Value (20) + Responsible AI (10→5 easy points by design).

**Demo polish (15 pts):** Experience + Demo — this is the 90-second video. Script it, rehearse it, time it.

## Minimum Viable Score Target
- 18/20 Problem (clear, named scenario)
- 18/20 Functional (live demo, no faking)
- 16/20 AI Quality (two-tier cascade, real decisions)
- 14/15 Testing (hard ceiling demo, model-failure demo)
- 12/15 Experience (scripted, rehearsed, timed)
- 8/10 Responsible AI (metadata-only by design)
- **Total: 86/100** — competitive for top 3 in Nigeria and global partner awards

_Last updated: 2026-09-27_
