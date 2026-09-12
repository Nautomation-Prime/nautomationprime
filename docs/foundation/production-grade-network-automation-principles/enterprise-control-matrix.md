---
title: Enterprise Control Matrix
description: Map each production-grade automation principle to control objectives, evidence artifacts, and ownership for enterprise operations.
tags:
  - Production Principles
  - Governance
  - Control Matrix
  - Audit
  - Enterprise
---

## Enterprise Control Matrix

Use this matrix to align the tutorial principles with operational controls, ownership, and evidence requirements.

---

## Control Mapping

| Part | Principle | Primary Risk Addressed | Control Objective | Evidence to Capture | Typical Owner |
|---|---|---|---|---|---|
| 1 | Device identity validation | Wrong-target change | Verify target authenticity before write actions | Identity check results, mismatch logs | Network Automation Team |
| 2 | Pre-flight checks | Unsafe execution environment | Block changes when prerequisites fail | Pre-flight report, failure reason codes | Operations Engineering |
| 3 | Source-of-truth trust boundaries | Stale or incorrect intent data | Enforce field-level trust policy | Reconciliation artifact, policy decision log | Platform Engineering |
| 4 | Drift handling safety | Over-enforcement and outages | Classify drift before remediation | Drift diff, severity, disposition record | Compliance + NetOps |
| 5 | Real-world idempotency | Non-convergent changes | Ensure predictable convergence with bounded retries | Planned diff, post-check outcomes | Automation Engineering |
| 6 | Blast-radius scoping | Large-scale failure impact | Restrict rollout scope and batch expansion | Canary results, batch promotion approvals | Change Manager |
| 7 | Safe failure design | Cascading automation errors | Define deterministic abort conditions | Abort triggers, degraded-mode logs | SRE / NetOps |
| 8 | Rollback strategy realism | Unsafe or ineffective rollback | Choose context-appropriate recovery path | Rollback decision, pre/post validation | Incident Response Lead |
| 9 | Read/write phase separation | Opaque execution behaviour | Require reviewable plan before execution | Plan artifact, execution artifact linkage | Platform Engineering |
| 10 | Operator-friendly output | Slow triage and misinterpretation | Present actionable, structured run output | Run summaries, reason-code statistics | NOC / Operations |
| 11 | Audit-ready automation | Incomplete evidence trail | Capture end-to-end run artifacts | Manifest, before/after snapshots, run metadata | Governance / Audit |
| 12 | Secrets and credentials | Credential exposure and misuse | Enforce least-privilege and secure secret handling | Vault access logs, rotation records | Security Engineering |
| 13 | Human-in-the-loop design | Unreviewed high-risk actions | Insert approvals at ambiguity and impact gates | Approval records, gate decisions | Change Advisory Board |
| 14 | When not to automate | Premature automation risk | Use readiness criteria before automation | Readiness rubric, deferment rationale | Engineering Leadership |

---

## Automation Risk Classification

Not every control applies to every workflow. Classify what the automation *does*, then apply the control set for that class and everything below it.

| Class | What the automation does | Examples | Controls that become mandatory |
|---|---|---|---|
| **R0 — Informational** | Retrieves and presents approved information | Inventory reports, interface state summaries, capacity extracts | Device identity validation (1), source-of-truth trust boundaries (3), operator-friendly output (10), audit-ready evidence (11), secrets handling (12) |
| **R1 — Advisory** | Analyses state and proposes action, without executing any | Compliance findings, drift reports, remediation proposals | Everything in R0, plus drift classification (4) and explicit separation of observed facts from recommendations |
| **R2 — Controlled execution** | Runs bounded activity that does not change configuration | Allow-listed diagnostics, state snapshots, path traces | Everything in R1, plus pre-flight checks (2) and safe failure design (7) |
| **R3 — Change automation** | Changes device state | Approved template deployment, port configuration, scheduled remediation | Everything in R2, plus idempotency (5), blast-radius scoping (6), rollback strategy (8), read/write separation (9), human-in-the-loop approval (13) |
| **R4 — High-impact or autonomous** | Acts at scale, or acts on events without a human initiating each run | Fleet-wide remediation, automatic recovery, closed-loop enforcement | Everything in R3, plus formal risk acceptance, a documented kill control, deliberately narrowed scope, enhanced monitoring, and a recorded answer to *when not to automate* (14) |

### Using the classification

- Classify at design time, not after the incident. The class determines how much assurance the work needs before it ships.
- A workflow takes the class of its **highest-risk step**. A read-only report that ends by opening a change ticket is still R1, not R0.
- Re-classify when scope changes. Widening a script from one site to the whole estate can move it from R3 to R4 without a single line of logic changing.
- Anything above R3 should be a deliberate, approved decision with a named owner — not somewhere a workflow drifted to over time.

---

## Control Quality Criteria

A control is usually production-ready when it is:

- Preventive or detective by design
- Enforced by code, not policy text alone
- Observable with machine-readable evidence
- Owned by a named team and reviewed on cadence

---

## Suggested Review Cadence

- Weekly: control failures and exception trends
- Monthly: drift, rollback, and gate quality analysis
- Quarterly: control ownership review and evidence retention audit

---

## Quick Adoption Sequence

1. Implement controls for Parts 1, 2, and 6 first
2. Add Parts 9, 10, and 11 to improve observability and auditability
3. Mature governance with Parts 12, 13, and 14

---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Program Charter for Production-Grade Automation](./program-charter.md)
- Next: [Exception and Waiver Process](./exception-and-waiver-process.md)
