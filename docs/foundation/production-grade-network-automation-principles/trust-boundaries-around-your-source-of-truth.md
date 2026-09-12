---
title: Trust Boundaries Around Your Source of Truth
description: Decide when inventory data is authoritative, advisory, or stale, and design workflows that reconcile intent with live state safely.
tags:
  - Production Principles
  - Source of Truth
  - Data Governance
  - Reliability
  - Network Automation
---

## Why Trust Boundaries Matter

A source of truth is powerful, but dangerous when treated as infallible.

Production reality:

- Inventory can lag real changes
- Device metadata can be incomplete
- Field operations may introduce temporary deviations

Blindly trusting stale intent can create outages faster than manual operations.

---

## Three Trust Modes

Define trust mode per data field, not globally.

- Authoritative: must match exactly (for example serial, role)
- Advisory: used for defaults but validated against live state
- Observational: tracked for reporting only, never used to drive writes directly

Example policy:

- Serial: authoritative
- Site code: authoritative
- Interface descriptions: advisory
- Optional tags: observational

---

## Reconciliation Pattern

Use explicit merge logic between intent and live state:

1. Load source-of-truth intent
2. Collect live state
3. Classify differences by trust mode
4. Block, warn, or annotate based on policy
5. Generate plan only from reconciled state

---

## Governance Controls

Minimum controls for trusted inventory use:

- Versioned inventory changes
- Peer review for critical metadata edits
- Change provenance (who, when, why)
- Drift dashboards for stale records
- SLA for metadata correction after incidents

---

## Production Checklist

- Trust mode is defined per key field
- Authoritative fields block execution on mismatch
- Advisory fields require live confirmation before writes
- Reconciliation output is stored per run
- Inventory update workflow exists and is auditable

---

## Anti-Patterns

- Treating all YAML fields as equally trusted
- Auto-patching inventory from live state during emergency runs
- Ignoring unknown fields or null values silently
- Allowing write workflows when critical metadata is missing

---

## Key Takeaway

A reliable source of truth is not just a database. It is a governance model that defines what must be trusted, what must be validated, and what must never directly drive production writes.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 2 - Pre-Flight Checks: Failing Fast Before Making Changes](./pre-flight-checks-failing-fast-before-making-changes.md)
- Next: [Part 4 - Detecting and Handling Configuration Drift Safely](./detecting-and-handling-configuration-drift-safely.md)
