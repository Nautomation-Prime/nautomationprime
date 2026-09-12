---
title: Operator Review Worksheet
description: A practical review checklist for validating readiness, risk, and evidence before approving production automation changes.
tags:
  - Production Principles
  - Operations
  - Worksheet
  - Change Review
  - Enterprise
---

## Operator Review Worksheet

Use this worksheet during dry-runs, approval gates, and change windows to make operator decisions explicit and consistent.

---

## 1) Scope and Intent Validation

- Change request ID:
- Service or domain impacted:
- Target scope (sites, roles, count):
- Out-of-scope exclusions confirmed:
- Business impact statement reviewed:

Decision:

- [ ] Approved
- [ ] Needs clarification
- [ ] Rejected

---

## 2) Pre-Flight and Identity Gate Results

- Identity validation passed for all targets:
- Critical pre-flight checks passed:
- Warning checks reviewed and accepted:
- Any parser ambiguity in required checks:

Decision:

- [ ] Proceed to plan review
- [ ] Hold for remediation
- [ ] Abort change

---

## 3) Plan and Risk Review

- Plan artifact generated and immutable:
- Diff reviewed for representative targets:
- Rollback or containment path documented:
- Batch strategy and abort threshold confirmed:

Risk classification ([see scale](./enterprise-control-matrix.md#automation-risk-classification)):

- [ ] R0 — Informational
- [ ] R1 — Advisory
- [ ] R2 — Controlled execution
- [ ] R3 — Change automation
- [ ] R4 — High-impact or autonomous

---

## 4) Approval Gate (If Required)

- Approver name and role:
- Approval timestamp:
- Conditions or constraints attached:
- Escalation contact identified:

Outcome:

- [ ] Approved for execution
- [ ] Deferred
- [ ] Rejected

---

## 5) Post-Execution Verification

- Verification checks passed:
- Drift status reviewed:
- Evidence artifacts captured and retained:
- Follow-up actions created (if any):

Run quality summary:

- [ ] Successful
- [ ] Successful with exceptions
- [ ] Failed with safe abort
- [ ] Failed and escalated

---

## 6) Lessons and Control Improvements

- Which control prevented risk in this run:
- Which control underperformed:
- Required updates to policy or code:
- Owner and due date for improvements:

---

## Recommended Storage

Store completed worksheets with run artifacts so review decisions are traceable during audits and incident retrospectives.

---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Implementation Roadmap (30/60/90 Days)](./implementation-roadmap-30-60-90-days.md)
- Next: [End of series](../index.md)
