---
title: Knowing When Not to Automate
description: Identify scenarios where automation increases risk and build a framework for deciding what should remain manual.
tags:
  - Production Principles
  - Strategy
  - Risk Management
  - Governance
  - Network Automation
---

## Automation Is Not Always the Right Answer

Automation is powerful, but not universally beneficial.

In some scenarios, forcing automation creates risk:

- Rare changes with high ambiguity
- Environments with poor source-of-truth quality
- Unstable operational ownership models
- One-off migrations where reusable logic is minimal

Mature teams automate intentionally, not reflexively.

---

## Decision Framework

Evaluate candidate tasks using five questions:

1. Is the task frequent enough to justify investment?
2. Is the intent explicit and machine-evaluable?
3. Can failure be detected quickly and safely?
4. Is rollback or containment realistic?
5. Is organisational ownership clear end to end?

If most answers are "no", do not automate yet.

---

## Readiness Signals Before Automation

Strong readiness indicators:

- Reliable inventory and naming standards
- Stable policy definitions
- Repeatable manual runbook with low ambiguity
- Monitoring and audit controls in place
- Clear service ownership and escalation path

Automation should follow operational maturity, not replace it.

---

## Safe Alternatives

When full automation is premature, use staged options:

- Assisted automation (generate plan, human executes)
- Report-only drift and compliance checks
- Partial automation on low-risk domains only
- Runbook standardisation before coding

These approaches deliver value while reducing premature risk.

---

## Production Checklist

- Automation candidates are scored with a readiness rubric
- High-ambiguity tasks remain manual or assisted
- Reassessment cadence exists for deferred candidates
- Teams document why a task is not automated yet
- Stakeholders align on conditions required for future automation

---

## Anti-Patterns

- Automating to satisfy a maturity metric
- Building complex workflows for rare one-off actions
- Ignoring ownership gaps because tooling exists
- Treating manual execution as failure by default

---

## Key Takeaway

Choosing not to automate can be a mark of engineering maturity. The right decision is the one that minimises risk while preserving long-term operability.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 13 - Human-in-the-Loop Automation Design](./human-in-the-loop-automation-design.md)
- Next: [End of series](../index.md)
