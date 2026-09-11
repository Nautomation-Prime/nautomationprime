---
title: Detecting and Handling Configuration Drift Safely
description: Detect drift, classify risk, and decide when to report, defer, or enforce without creating avoidable outages.
tags:
  - Production Principles
  - Drift
  - Compliance
  - Risk Management
  - Network Automation
---

## Drift Is Not Always Wrong

Drift means actual state differs from intended state. It does not always mean "fix immediately."

Some drift is:

- Legitimate but undocumented
- Temporary and operationally necessary
- A result of emergency response

Automatic enforcement without context can break healthy systems.

---

## Drift Handling Model

Classify drift before action:

- Critical drift: security or policy violation, immediate attention
- Functional drift: service-impacting mismatch, controlled remediation
- Cosmetic drift: naming or formatting differences, report-only

This classification should be codified, not ad hoc.

---

## Reporting-First Pattern

Start with a non-enforcing phase:

1. Detect drift and generate structured diff
2. Tag drift with severity and ownership
3. Publish report and review queue
4. Enforce only approved classes of drift

This approach builds operator confidence and reduces accidental over-correction.

---

## Conditional Enforcement

Useful production rule:

- Enforce automatically only when all are true:
  - Drift class is approved for automation
  - Change is low-risk and reversible
  - Device passes all pre-flight gates
  - Change window policy allows remediation

Else: create a tracked remediation task for human decision.

---

## Production Checklist

- Drift is severity-classified before any write
- Reports include context, owner, and recommended action
- Automatic enforcement is limited to approved drift categories
- Emergency-change drift has an exception path
- Drift trends are reviewed weekly for systemic issues

---

## Anti-Patterns

- "Drift equals immediate overwrite"
- One global remediation policy for all device roles
- No traceability of why drift was accepted or deferred
- Conflating compliance drift with functional breakage

---

## Key Takeaway

Safe drift management is a decision system, not a force-sync loop. Detection is easy; correct action selection is the real engineering work.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 3 - Trust Boundaries Around Your Source of Truth](./trust-boundaries-around-your-source-of-truth.md)
- Next: [Part 5 - Real-World Idempotency in Network Automation](./real-world-idempotency-in-network-automation.md)
