---
title: "Pre-Flight Checks: Failing Fast Before Making Changes"
description: Use reachability, auth, read-only, and environmental checks to stop unsafe runs early and protect production.
tags:
  - Production Principles
  - Pre-Flight
  - Validation
  - Safety
  - Network Automation
---

## Why Pre-Flight Exists

Automation fails expensively when it discovers basic problems too late. Pre-flight checks move failure to the earliest possible point.

Goal: spend seconds validating, not hours recovering.

---

## Baseline Pre-Flight Control Set

Before writing anything, validate:

- Reachability to management endpoint
- Authentication and authorisation scope
- Device in expected mode and software train
- Read-only command sanity checks
- Change window and maintenance-state flags
- Platform-specific constraints (CPU, memory, disk, control-plane health)

---

## Layered Validation Model

Use progressive gates:

1. Connectivity gate: ping or TCP reachability
2. Session gate: login and privilege verification
3. State gate: read-only health and policy checks
4. Intent gate: confirm prerequisites for this specific change

Do not skip to step 4 if earlier gates fail.

---

## Pattern: Fast Abort With Clear Reason

```python
checks = [
    check_reachability,
    check_authz,
    check_platform_state,
    check_change_window,
    check_change_prerequisites,
]

for check in checks:
    result = check(device)
    if not result.ok:
        record_preflight_failure(device=device, check=check.__name__, reason=result.reason)
        raise RuntimeError(f"Pre-flight failed: {check.__name__}: {result.reason}")
```

Critical implementation detail:

- Return machine-readable reasons, not only free-text strings
- Aggregate failures for reporting in read-only mode
- Enforce immediate abort for write mode

---

## Pre-Flight Operating Modes

Useful modes:

- Report-only: collect failures without write attempts
- Enforced: block writes on any critical pre-flight failure
- Scoped override: allow specific exception IDs only

This makes testing safer while preserving strict production behaviour.

---

## Production Checklist

- Pre-flight runs for every target in every execution
- Critical checks are consistent across sites
- Failures are categorised by severity and reason code
- Writes are blocked when critical checks fail
- Operators receive actionable failure summaries

---

## Anti-Patterns

- Pre-flight only in CI but not at runtime
- Warnings with no enforcement path
- One giant opaque check instead of layered checks
- Continuing on auth or privilege mismatch

---

## Key Takeaway

Pre-flight checks are a control plane for risk. If pre-flight is weak, every downstream safeguard is weaker.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 1 - Validating Device Identity Before Automation Runs](./validating-device-identity-before-automation-runs.md)
- Next: [Part 3 - Trust Boundaries Around Your Source of Truth](./trust-boundaries-around-your-source-of-truth.md)
