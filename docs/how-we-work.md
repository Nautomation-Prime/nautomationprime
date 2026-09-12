---
title: How We Work
description: Step-by-step guide to how Nautomation Prime delivers automation. From discovery to team empowerment, here's what your engagement looks like.
tags:
  - PRIME Framework
  - Process
  - Methodology
  - How To Work With Us
---

<div class="np-hero" markdown>

<p class="np-eyebrow">Founder-led delivery from discovery to handover</p>

## See exactly what a PRIME Framework engagement looks like

This page shows how Nautomation Prime takes a network automation engagement from first conversation to team ownership. The goal is not just to deliver working code, but to build a delivery path your team can understand, approve, and sustain after handover.

<div class="np-action-row" markdown>

[Request Discovery Call](./contact.md){.md-button .md-button--primary}
[View Services](./services.md){.md-button}
[See Investment Ranges](./services.md#typical-investment-ranges){.md-button}

</div>

<ul class="np-signal-list">
  <li>Typical engagement: 6-12 weeks</li>
  <li>Staged rollout, not blind deployment</li>
  <li>ROI tracking built in</li>
  <li>Knowledge transfer included</li>
</ul>

</div>

## What to expect from working together

<div class="grid cards" markdown>

-   ### Structured discovery first

  We start by clarifying the operational problem, constraints, risks, and business case before any build work begins.

-   ### Safety before speed

  Workflow design, validation, rollback, and pilot thinking are built in before production rollout.

-   ### Measured delivery

  Success is tracked with actual before-and-after metrics, not vague claims that automation "feels faster".

-   ### Ownership at the end

  The process includes documentation, workshops, and support so your team can run and extend the automation with confidence.

</div>

---

## The Five Stages at a Glance

| Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
| :--- | :--- | :--- | :--- | :--- |
| Pinpoint | Re-engineer | Implement | Measure | Empower |
| Week 1 | Weeks 2-3 | Weeks 4-8 | Weeks 9-12 | Weeks 10-16 |
| Discovery | Design | Build | Track ROI | Transfer Ownership |

---

## Stage 1: Pinpoint (Discovery & Roadmap) — Week 1

### What Happens (Pinpoint)

You're drowning in network operational tasks. Some feel painful. Some seem obvious to automate. But which ones actually deserve automation?

**The Pinpoint stage answers that question with data.**

### Your Experience (Pinpoint)

#### 1. Discovery Workshop (4 hours)

We sit with your network operations team and document:

- Current operational workflows
- Pain points and frustration areas
- Time spent on each task (daily/weekly/monthly)
- Constraints and dependencies (compliance, legacy systems, team skills)
- Success criteria (how will we know this worked?)

#### 2. Time-Motion Analysis (1–2 weeks background work)

We analyse operational logs, ticket systems, and team feedback to build accurate time estimates.

#### 3. ROI Calculation

We calculate the payback period for each automation opportunity:

- Time savings per task
- Annual operational cost reduction
- Risk reduction (compliance, outages)
- Capital freed up for other priorities

#### 4. Automated Roadmap Delivery (Week 1 conclusion)

You receive a **prioritised automation roadmap** with:

- Top 3–5 automation opportunities ranked by ROI
- Timeline and effort estimates for each
- Risk assessment and feasibility notes
- Business case (you'll know exactly why we recommended these)

### The Guarantee (Pinpoint)

You walk away with a clear roadmap of what to automate and why—**even if you decide not to proceed with us.**

**Investment:** £2,500–£4,000

**Deliverable:** Prioritised roadmap with ROI projections

**[Learn more about Pinpoint →](./prime-framework/pinpoint.md)**

---

## Stage 2: Re-engineer (Workflow Design) — Weeks 2-3

### What Happens (Re-engineer)

You've decided what to automate. Now we optimise the *workflow itself* before writing a single line of code.

Most automation fails because teams automate broken processes. We fix the process first.

### Your Experience (Re-engineer)

#### 1. Current State Documentation

We map the current workflow in detail:

- Steps (in order)
- Decision points ("If this, then that")
- Edge cases ("What if this happens?")
- Validation and rollback procedures
- Team handoffs and communication

#### 2. Future State Design

We design the optimised workflow:

- Eliminate unnecessary steps
- Add safety checkpoints (pre-flight, post-flight validation)
- Design rollback procedures (what happens if automation fails?)
- Plan error alerting (who gets notified if something goes wrong?)

#### 3. Technical Architecture Blueprint

We design how the code will be structured:

- Library choices (Netmiko, Nornir, etc.)
- Execution model (serial vs. parallel)
- Credential management (secure, no plaintext)
- Logging and reporting strategy
- Deployment constraints (Windows workstation, Linux server, Docker, etc.)

#### 4. Safety & Validation Specifications

Before coding, we document:

- Pre-flight checks ("Verify device is reachable before attempting config")
- Validation tests ("Confirm config was actually applied")
- Rollback triggers ("Automatically undo if validation fails")
- Error handling ("If device X fails, should we continue with device Y?")

### The Deliverable (Re-engineer)

You receive detailed **architecture documents** that show:

- How the workflow will be automated
- Safety mechanisms to prevent mistakes
- How to modify it later (important for future team members)

**You review and approve before Stage 3 begins.**

**Investment:** £3,000–£6,000 per automation

**Deliverable:** Architecture blueprint + safety specifications

**[Learn more about Re-engineer →](./prime-framework/re-engineer.md)**

---

## Stage 3: Implement (Development & Testing) — Weeks 4-8

### What Happens (Implement)

Now we build the automation—with transparency, safety, and maintainability as first-class requirements (not afterthoughts).

### Your Experience (Implement)

#### 1. Development with Transparency

We code according to the **PRIME Philosophy**:

- **Line-by-line documentation** — Why we chose each library, why this approach, what this function does
- **Verbose logging** — When the code runs, it tells you exactly what it's doing
- **Pragmatic design** — Simple, direct solutions over over-engineered frameworks
- **Hardened error handling** — Code doesn't crash; it fails gracefully with clear errors

#### 2. Lab Testing (Week 6)

We test in a sandboxed environment:

- Does the code do what it's supposed to do?
- Do error handlers work ("What happens if a device is unreachable?")
- Does rollback work ("Can we undo if something goes wrong?")
- Does logging work ("Can we understand what happened if it fails?")

#### 3. Code Review & Documentation

We document everything:

- README (how to install and run the code)
- Technical reference (what each function does)
- Troubleshooting guide ("If X error appears, do Y")
- Optional code-signing and verification guide for security assurance workflows
- Line-by-line comments in the code itself

#### 4. Pilot Deployment (Week 7-8)

We deploy to a small subset of your network:

- A few test devices first
- Measure actual time savings
- Verify zero unintended side effects
- Gather feedback from your operations team

#### 5. Full Production Rollout (End of Stage 3)

Once pilot is successful, we deploy to your full environment with:

- Live monitoring (we watch the first few runs)
- Direct support (if issues arise, we're available)
- Handoff documentation (everything your team needs to run it independently)

### The Deliverable (Implement)

You receive:

✅ **Production-ready Python code** with [PRIME Philosophy](./prime-framework/philosophy.md) principles  
✅ **Comprehensive documentation** (README, technical reference, runbooks)  
✅ **Full source code** (you own it, can modify it, understand every line)  
✅ **Line-by-line code comments** explaining the *why* behind each decision  
✅ **Optional software integrity controls** (code-signing + signature verification guidance for client security teams)  
✅ **Testing results** (lab testing, pilot testing, measured outcomes)  

**Investment:** £6,000–£18,000

**Timeline:** 2–6 weeks (depending on complexity)

**Deliverable:** Production-ready code + documentation + pilot validation

**[Learn more about Implement →](./prime-framework/implement.md)**

---

## Stage 4: Measure (ROI Tracking) — Weeks 9-12 (Ongoing)

### What Happens (Measure)

Now we prove the value.

This is where most automation consulting falls short—they deliver code and disappear. We quantify the business impact.

### Your Experience (Measure)

#### 1. Baseline Reconstruction (Week 9)

We reconstruct pre-automation metrics:

- Historical task duration (from logs, timesheets, ticket systems)
- Manual effort required
- Errors or incidents caused by manual processes
- Operational cost

#### 2. Instrumentation (Week 10)

We add lightweight tracking to your automation:

- Execution time
- Tasks completed
- Errors caught and handled
- Time saved per run

#### 3. 3–6 Months of Tracking (Weeks 10-22)

Real-world data collection:

- How often is the automation run?
- How many tasks does it complete per run?
- How much time does it save each time it runs?
- What errors did it catch that would have become incidents?

#### 4. Executive Reporting (Month 4–6)

You receive a formal **ROI Report** with:

- Baseline metrics vs. post-automation metrics
- Time savings quantified in hours
- Operational cost reduction (£)
- Risk reduction (incidents prevented, compliance violations avoided)
- ROI calculation (savings ÷ investment = payback period)
- Recommendations for the next automation opportunity

### Example Report

**Before Automation:** VLAN provisioning took 15 minutes per VLAN (average across 2020-2023)  
**After Automation:** Automated provisioning takes 30 seconds per VLAN

**Time Savings:** 14.5 minutes per VLAN × 80 VLANs annually = 1,160 hours  
**Cost Savings:** 1,160 hours × £25 hourly rate = £29,000  
**ROI:** £29,000 savings ÷ £15,000 investment = 193% ROI in Year 1

### The Deliverable (Measure)

You receive a formal **ROI Report** suitable for:

- Finance/CFO reviews
- Board-level reporting
- Budget justification for future automation
- Stakeholder communication

**Investment:** £2,000–£3,500

**Timeline:** 3–6 months (ongoing measurement)

**Deliverable:** ROI metrics + executive report

**[Learn more about Measure →](./prime-framework/measure.md)**

---

## Stage 5: Empower (Knowledge Transfer) — Weeks 10-16

### What Happens (Empower)

We transfer full ownership of the automation to your team.

After engagement ends, your network engineers can maintain, modify, and extend the automation independently. You're not dependent on us forever.

### Your Experience (Empower)

#### 1. Knowledge Transfer Workshops (4 sessions, usually 2-3 hours each)

**Session 1: Architecture & Design** (Week 10)

- How the automation is structured
- Why we chose each library (Netmiko, Nornir, etc.)
- How data flows through the system
- Where validation and error handling happen

**Session 2: Code Deep-Dive** (Week 11)

- Reading through the actual source code line-by-line
- Understanding the logic and decision points
- Explaining error handling and edge cases
- Q&A on any confusing parts

**Session 3: Operations & Troubleshooting** (Week 12)

- How to run the automation day-to-day
- What to do if something fails
- How to read logs and understand what went wrong
- Common issues and their solutions

**Session 4: Modification & Extension** (Week 13)

- How to add features to the automation
- Where to make changes and how to test them
- How to add new device types or workflows
- Building confidence to extend the code independently

#### 2. Documentation Package

You receive a complete knowledge base:

- **User Guide** — For network ops running the automation
- **Technical Reference** — For engineers modifying the code
- **Runbooks** — Step-by-step procedures for specific scenarios
- **Architecture Diagrams** — Visual system design
- **FAQ & Troubleshooting** — Common questions answered

#### 3. 8 Weeks of Support (Post-engagement)

After we step back, you can still reach out:

- Questions about the code ("Why did we do it this way?")
- Bugs or edge cases you discover
- Modification assistance ("How do I add support for device Y?")
- Confidence building ("Is my proposed change safe?")

### The Deliverable (Empower)

Your team walks away with:

✅ **Deep understanding** of how the automation works  
✅ **Confidence** to maintain it independently  
✅ **Capability** to extend it with new features  
✅ **Documentation** for future team members  
✅ **Support line** for 8 weeks post-engagement  

**Investment:** £3,000–£5,000

**Timeline:** 6 weeks of workshops + 8 weeks of support

**Deliverable:** Knowledge transfer workshops + documentation package + post-engagement support

**[Learn more about Empower →](./prime-framework/empower.md)**

---

## The Full Timeline

| Timeline | Stage | Typical Duration | Primary Outputs |
| :--- | :--- | :--- | :--- |
| Week 1 | Pinpoint | 1 week | Discovery workshop, ROI roadmap |
| Weeks 2-3 | Re-engineer | 2 weeks | Architecture blueprint, safety plan |
| Weeks 4-8 | Implement | 4 weeks | Development, testing, pilot, full deploy |
| Weeks 9-12+ | Measure | 4+ weeks | ROI tracking, executive reporting |
| Weeks 10-16 | Empower | 6 weeks workshops + 8 weeks support | Knowledge transfer, documentation |

## Total engagement: 6–12 weeks (typical medium-complexity automation)

---

## Engagement Models

### Full PRIME Framework

**All five stages from Pinpoint through Empower.**

**Best for:** Organisations serious about sustainable automation capability

**Investment:** £12,000–£28,000 (depending on complexity)

**Timeline:** 6–12 weeks

**What you get:**

- Proven ROI before committing to development
- Optimised workflows (not just faster bad processes)
- Production-ready code with zero mystery
- Concrete ROI metrics
- Full team capability to extend independently

---

### À La Carte Services

**Pick individual stages based on your needs.**

| Stage | Investment | Timeline | Red Flag If Skipped |
| :--- | :--- | :--- | :--- |
| **Pinpoint Only** | £2,500–£4,000 | 1 week | You might automate the wrong thing |
| **Re-engineer Only** | £3,000–£6,000 | 1–2 weeks | Code might be brittle/unmaintainable |
| **Implement Only** | £6,000–£18,000 | 2–6 weeks | Team won't understand the code |
| **Measure Only** | £2,000–£3,500 | 3–6 months | Leadership questions ROI existence |
| **Empower Only** | £3,000–£5,000 | 6 weeks | Automation dies when consultant leaves |

---

## What Happens After Engagement Ends

You own the automation completely:

✅ **Full source code ownership** (or exclusive licence, your choice)  
✅ **Ability to modify** — Your team understands the code, can make changes  
✅ **Ability to extend** — Add new features, support new device types  
✅ **No vendor lock-in** — Code uses industry-standard libraries (Netmiko, Nornir, NAPALM)  
✅ **8 weeks of support** — Post-engagement questions answered  
✅ **30-day bug fix guarantee** — If critical issues arise, we fix them free  

**After 8 weeks:** You're completely independent. If you want future automation projects, we're happy to help—but you're not dependent on us.

---

## Why This Process Works

**Most automation consulting skips structure:**

- "Here's code." (Skips Pinpoint—you automate the wrong thing)
- "Here's documentation." (Skips Re-engineer—code doesn't handle edge cases)
- "Build it yourself." (Skips Implement—gets brittle)
- "Deploy it." (Skips Measure—nobody proves ROI)
- "Goodbye!" (Skips Empower—automation dies when consultant leaves)

**The PRIME Framework doesn't skip anything:**

1. **Pinpoint** ensures you automate the *right* thing (high ROI)
2. **Re-engineer** ensures the solution is *safe* and *scalable*
3. **Implement** ensures the code is *transparent* and *maintainable*
4. **Measure** ensures you have *proof of value* for leadership
5. **Empower** ensures your team can *sustain and extend* it

**Result:** Automation that works, that your team understands, that delivers measurable ROI, and that your team can own and evolve.

---

## Ready to start the process?

<div class="np-cta-strip" markdown>

### Start with a discovery conversation, not a hard sell

The first step is a low-pressure conversation about your operational bottlenecks, constraints, likely ROI, and whether the PRIME Framework is the right fit. If it is not, that will be made clear early.

<div class="np-action-row" markdown>

[Book a Discovery Call](./contact.md){.md-button .md-button--primary}
[View Services](./services.md){.md-button}
[Contact & Discovery](./contact.md#what-to-include-in-your-message){.md-button}

</div>

</div>

### Typical next steps

1. Discovery conversation to understand your environment and goals.
2. If the fit is right, a paid [Pinpoint](./prime-framework/pinpoint.md) engagement defines priorities and ROI.
3. From there, proceed with the full PRIME Framework or the specific stages you need.

---

## Learn More

**[PRIME Framework Overview](./prime-framework/index.md)** — Full methodology documentation

**Individual Stages:**

- [Pinpoint](./prime-framework/pinpoint.md) — Discovery & ROI
- [Re-engineer](./prime-framework/re-engineer.md) — Design & Safety
- [Implement](./prime-framework/implement.md) — Development & Testing
- [Measure](./prime-framework/measure.md) — ROI Tracking
- [Empower](./prime-framework/empower.md) — Knowledge Transfer

**[Services & Pricing](./services.md)** — Investment and deliverables

**[Production-Grade Network Automation Principles](./foundation/production-grade-network-automation-principles/index.md)** — Understand the operating patterns PRIME applies in practice

---

> The best automation isn't the most elegant code—it's the code your team understands, owns, maintains confidently, and extends independently. That's what the PRIME Framework delivers.
