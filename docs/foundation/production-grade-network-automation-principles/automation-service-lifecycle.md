---
title: Automation Service Lifecycle
description: Treating automation as a supported service with named owners, lifecycle gates, and a retirement path — not as a script that exists until it breaks.
tags:
  - Production Principles
  - Governance
  - Lifecycle
  - Ownership
  - Enterprise
---

## Automation Service Lifecycle

Most automation governance stops at go-live. There is a design review, a test cycle, an approval, a deployment — and then nothing, for years, until something breaks or the person who wrote it leaves.

The result is familiar: a portfolio nobody can inventory, scripts running on schedules nobody remembers setting, and credentials belonging to services whose purpose is no longer clear. Every organisation with more than about two years of automation has some of this. It is not a discipline failure so much as a framing failure — the work was treated as a project, and projects end.

Automation is a **service**. Services have owners, reviews, and an end.

---

## Where This Sits Alongside Delivery

The [PRIME Framework](../../prime-framework/index.md) describes how automation gets delivered: opportunities identified, workflows redesigned, code built, value measured, the team empowered to own it.

This page describes what happens to it afterwards, and it is deliberately a separate concern. Delivery ends. Operation does not.

| | PRIME Framework | Service lifecycle |
|---|---|---|
| **Question answered** | How does this get built well? | How does this stay worth running? |
| **Ends when** | The team owns the automation | The service is retired |
| **Failure mode if skipped** | Brittle scripts, no measured value, consultant dependency | Portfolio sprawl, orphaned services, unreviewed risk |

---

## Three Owners, Not One

The single highest-value idea here, and the cheapest to adopt: **"the automation team owns it" is not an ownership model.** It names a group, which means it names nobody in particular at the moment something goes wrong.

Three distinct accountabilities, which may or may not be three different people:

| Role | Accountable for | The question they answer |
|---|---|---|
| **Service owner** | Value, scope, prioritisation, risk acceptance, lifecycle decisions | *Should this still exist?* |
| **Technical owner** | Architecture, implementation quality, dependencies, technical direction | *Is this still well built?* |
| **Operational owner** | Support, monitoring, incidents, runbooks, service reviews | *Is this healthy right now?* |

In a small team one engineer may hold all three, and that is fine — provided it is recorded, because the day they leave you need to know there are three things to reassign rather than one.

Recording them is also what makes ["no hero automation"](../../prime-framework/philosophy.md) enforceable rather than aspirational. A named technical owner who is not the original author is the strongest evidence you have that knowledge actually transferred.

---

## Lifecycle Gates

Eight decision points. The depth of evidence at each should scale with the [risk class](./enterprise-control-matrix.md#automation-risk-classification) — an R0 report does not need what an R3 change service needs, and pretending otherwise is how governance gets a reputation for obstruction.

| Gate | Question | Evidence |
|---|---|---|
| **G1 — Intake** | Is the problem real, and is there an owner? | Problem statement, affected users, current manual effort, named sponsor |
| **G2 — Assessment** | Is it valuable and feasible? | Value estimate, data quality check, risk class, reusability, decision to proceed or defer |
| **G3 — Design** | Is the architecture safe and supportable? | Solution design, target resolution, identity and authorisation model, failure behaviour, rollback approach |
| **G4 — Build** | Does the implementation meet standards? | Peer review, tests, documentation produced alongside the code |
| **G5 — Readiness** | Can it operate safely in production? | Test results, security review, monitoring and audit in place, deployment and rollback tested, owners confirmed |
| **G6 — Transition** | Has ownership actually transferred? | Deployment record, handover completed, runbooks in the hands of the operational owner |
| **G7 — Review** | Is it still delivering value and still healthy? | Service review against adoption, reliability, and governance measures |
| **G8 — Retirement** | Has it been safely decommissioned? | Retirement record, access revoked, dependencies confirmed clear |

G2 deserves particular attention, because it is the gate teams skip. It is the only place where **"no" is a good outcome** — and a portfolio where nothing is ever declined at G2 is a portfolio that will need pruning at G8 instead, more expensively.

---

## Assessment Criteria at G2

| Criterion | The question |
|---|---|
| **Value** | Will this reduce delay, manual effort, error, risk, or inconsistency by an amount worth the build? |
| **Repeatability** | Is the process stable enough to automate, or is it still changing shape monthly? |
| **Data quality** | Are the authoritative inputs available and trustworthy today? |
| **Risk** | Can the effects be bounded, tested, verified, and reversed? |
| **Reusability** | Will this serve more than one workflow or team? |
| **Complexity** | What integrations and support skills does it require, and do we have them? |
| **Strategic fit** | Does it match where the platform is going, or does it entrench something we are trying to replace? |
| **Ownership** | Can it be supported for its whole life, not just built? |

If [knowing when not to automate](./knowing-when-not-to-automate.md) is the principle, G2 is where the principle gets a decision date.

---

## The Minimum Service Record

One record per service. A table in a wiki is enough — the point is that it exists and is findable, not that it lives in a CMDB.

- **Identity** — name, purpose, version, lifecycle status
- **Ownership** — service, technical, and operational owners
- **Scope** — users, environments, sites, device roles, and explicit exclusions
- **Risk** — classification and the controls that class requires
- **Implementation** — repository, pipeline, artifact, dependencies
- **Operation** — monitoring, support route, runbook, recovery, escalation
- **Governance** — approvals, open [exceptions](./exception-and-waiver-process.md), review history, audit location
- **Retirement** — trigger conditions, replacement, archive location

The test of this record is not completeness. It is whether an engineer who has never seen the service can answer *what does it do, who owns it, and what happens if it stops* in under five minutes.

---

## Retirement

The stage nobody plans, and the one that quietly accumulates risk. A service that no longer runs but was never decommissioned still holds credentials, still has network access, and still appears in an audit.

- Approve the retirement decision and set an effective date
- Identify users, integrations, schedules, credentials, and data
- Communicate the replacement or the process change
- Disable triggers, endpoints, and access
- Revoke secrets and service identities
- Archive source, documentation, decisions, and audit records to the retention period required
- Confirm no dependent workflow still calls it
- Record completion and where residual ownership sits

The dependency check matters more than it looks. Automation that calls other automation is common and rarely documented, and the failure mode — a scheduled job silently producing nothing after a dependency is switched off — can go unnoticed for months.

---

## Portfolio Review

Individual service reviews at G7 keep each service healthy. A periodic look across the whole portfolio catches what per-service review cannot:

- **Duplication** — two teams solving the same problem twice, usually discovered during an incident
- **Orphans** — services whose named owner has changed roles or left
- **Retirement candidates** — low adoption, superseded by a platform feature, or the underlying manual process no longer exists
- **Concentration risk** — several critical services sharing one technical owner
- **Exception accumulation** — see the [exception register](./exception-and-waiver-process.md); repeated waivers against one control usually mean the control needs changing, not the services

Annually is enough for most teams. The output is a list of decisions, not a report.

---

## Adopting This Without a Programme

If this reads as heavier than your organisation is ready for, the useful subset is small. In order:

1. **Write down three owners for every automation you currently run.** Most of the value is here, and it takes an afternoon.
2. **Add G2 and G7.** A decision before you build, and a review afterwards.
3. **Start the service record** for new services only. Do not attempt to backfill the portfolio; it never finishes.
4. **Add retirement** the first time you switch something off, and use that as the template.

Everything else can wait until the portfolio is large enough to need it.

---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Exception and Waiver Process](./exception-and-waiver-process.md)
- Next: [Implementation Roadmap (30/60/90 Days)](./implementation-roadmap-30-60-90-days.md)
