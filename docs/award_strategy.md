# Award Strategy — Thunders + NVIDIA Brev

## Primary Target: Thunders Engineering Excellence Award

| Detail | Value |
|--------|-------|
| **Prize** | One Mac mini |
| **Scope** | One team selected globally (all 8 countries) |
| **Criteria** | "Strongest reliable, functional and technically well-executed prototype" |
| **Judge** | Issam Allani — Founding Engineer at Thunders |

### What Thunders Values (from research)
Thunders (formerly Thunder Code) builds AI-native automated software testing.
Their engineering culture values:
1. **Reliability over cleverness** — they ship testing tools, they hate flaky systems
2. **Automation that removes grunt work** — not more abstraction, less manual intervention
3. **Rapid iteration** — MVP in 6 weeks is their origin story
4. **Real-world problem solving** — end-to-end workflows, not toy demos
5. **Human-centric AI** — AI as partner, not replacement; transparent and auditable

### How Jev Maps to Thunders' Values
| Thunders Value | Jev Feature |
|----------------|-------------|
| Reliability | Hard deterministic ceiling fires regardless of model output |
| Removes grunt work | Automates agent monitoring that devs currently do manually |
| Rapid iteration | One-day build, working end-to-end |
| Real-world | Named scenario: WhatsApp Business API suspension |
| Human-centric AI | AI classifies but never overrides the safety floor; human escalation built in |

### Demo Moment That Wins Thunders
**Kill the model mid-demo.** Show the hard ceiling catch the burst anyway.
This is the single most powerful 10 seconds for Issam Allani.
It says: "Our safety doesn't depend on the AI working."

---

## Secondary Target: NVIDIA Brev Breakthrough Award

| Detail | Value |
|--------|-------|
| **Prize** | 2nd place Nigeria: GOMYCODE vouchers ≤ $1,250 + $200 NVIDIA Brev credits |
| **Scope** | 2nd place in Nigeria only |
| **Criteria** | "Purposeful technical use of AI models and workflows, regardless of provider" |
| **Note** | Brev use is NOT required. Tool-neutral judging. |

### How Jev Wins the NVIDIA Brev Criterion
The two-tier AI cascade is the story:
1. **Tier 1 (fast classifier):** Every flagged anomaly → small model → JSON verdict in <1s
2. **Tier 2 (thinking model):** Escalation only → full context → root-cause analysis
3. **Purposeful:** AI makes a *decision* (allow/backoff/kill), not just a label
4. **Workflow:** Tier 1 → escalation trigger → Tier 2 → verdict → enforcement

The AI use is integral to the product, not bolted on. Without the classifier, Jev is just a rate limiter. With it, Jev understands *what kind* of failure is happening and responds differently.

### What NOT to Do
- Don't mention Brev credits unless we actually use Brev
- Don't fake GPU usage — judges see through it
- Focus on *quality of AI contribution*, not *quantity of API calls*

---

## Prize Selection Strategy (Submission Form)
- **Primary dropdown:** Thunders Engineering Excellence Award
- **Checkboxes:** Also select NVIDIA Brev Breakthrough (covered via country podium 2nd place)
- **Evidence of fit (2-3 sentences each):**
  - Thunders: "Jev's hard deterministic ceiling fires independently of any model output, ensuring reliability even when the AI fails. This is demonstrated live by killing the model mid-demo and showing the ceiling still catches the burst."
  - NVIDIA Brev: "Jev uses a two-tier AI cascade where a fast classifier triages every anomaly and a thinking model performs root-cause analysis on escalation. The AI makes actionable decisions, not just labels."

_Last updated: 2026-09-27_
