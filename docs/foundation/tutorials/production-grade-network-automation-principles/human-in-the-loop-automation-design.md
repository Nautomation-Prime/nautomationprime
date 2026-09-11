---
title: Human-in-the-Loop Automation Design
description: Keep humans in critical decision points with approval gates, dry-run reviews, and clear intervention pathways.
tags:
  - Production Principles
  - Human in the Loop
  - Change Governance
  - Safety
  - Network Automation
---

## Why Humans Still Matter

Automation improves speed and consistency, but not all decisions are deterministic.

Human judgment remains essential when:

- Business impact is high
- Data confidence is low
- Multiple valid remediation options exist
- Context exists outside machine-readable systems

The goal is not manual work everywhere. The goal is human authority at the right decision points.

---

## Where To Place Approval Gates

Typical gate locations:

- After plan generation, before write execution
- Before scope expansion beyond canary or first batch
- Before rollback in ambiguous failure states
- Before applying changes flagged as high risk

Approval should be role-based and traceable.

---

## Effective Dry-Run Reviews

A useful dry-run should include:

- Proposed change diff per device
- Risk classification per target
- Confidence indicators and parser quality
- Expected service impact statements

If dry-run output is unclear, operators will either reject safe changes or approve risky ones blindly.

---

## Intervention Design

Human intervention should be explicit:

- Pause points with timeout policy
- "Approve", "reject", and "defer" outcomes
- Escalation target when no decision is made
- Safe default behaviour on timeout (usually abort)

---

## Production Checklist

- Human approval gates are defined for high-risk operations
- Dry-run artifacts are easy to review and compare
- Approval decisions are logged with identity and timestamp
- Timeout behaviour is deterministic and safe
- Operators can pause or stop execution at controlled points

---

## Anti-Patterns

- Human approval as a rubber-stamp with poor context
- Approval required for every trivial operation
- No owner assigned to pending approval actions
- Auto-approve behaviour on gate timeout

---

## Key Takeaway

Human-in-the-loop design is about targeted control, not friction. Place humans where ambiguity and impact are highest.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 12 - Secrets and Credentials in Enterprise Automation](./secrets-and-credentials-in-enterprise-automation.md)
- Next: [Part 14 - Knowing When Not to Automate](./knowing-when-not-to-automate.md)
