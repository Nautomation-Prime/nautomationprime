---
title: Validating Device Identity Before Automation Runs
description: Confirm hostname, serial, model, role, and site before any change. Fail fast when targets do not match trusted intent.
tags:
  - Production Principles
  - Validation
  - Source of Truth
  - Risk Reduction
  - Network Automation
---

## Why Identity Validation Matters

Many production incidents are not caused by bad templates. They are caused by targeting the wrong device.

Common causes:

- Reused IP addresses after hardware replacement
- DNS drift or stale inventory
- Hostname collisions in legacy environments
- Devices moved between roles or sites without inventory updates

If identity is uncertain, your automation should stop before write operations begin.

---

## What To Validate Before Any Change

Minimum identity tuple:

- Hostname
- Serial number
- Platform or model family
- Intended role (core, access, WAN edge, etc.)
- Site or location code

Optional but useful:

- Software train or major version
- Management VRF and source interface
- Ownership metadata (team or service)

---

## Practical Pattern: Identity Gate

Use a dedicated read-only gate that runs before pre-flight and before planning.

```python
identity_expected = {
    "hostname": "lon-core-01",
    "serial": "FTX1234ABC",
    "role": "core",
    "site": "LON1",
    "model": "C9500"
}

identity_live = collect_device_identity(conn)

def identity_matches(expected, live):
    keys = ["hostname", "serial", "role", "site", "model"]
    mismatches = {k: (expected[k], live.get(k)) for k in keys if expected[k] != live.get(k)}
    return len(mismatches) == 0, mismatches

ok, mismatches = identity_matches(identity_expected, identity_live)
if not ok:
    raise RuntimeError(f"Identity gate failed: {mismatches}")
```

Design notes:

- Treat serial mismatch as hard fail
- Treat role mismatch as hard fail
- Treat hostname mismatch as hard fail unless approved rename workflow exists
- Persist mismatch details for audit

---

## Failure Policy

Recommended default:

- Fail closed for all writes
- Mark target as unsafe
- Require human approval to override
- Never auto-correct identity data during a write run

---

## Production Checklist

- Identity is validated in a dedicated read-only phase
- Validation compares against a versioned source of truth
- Workflow aborts if serial or role differs
- Exceptions require explicit approval and ticket reference
- All mismatches are written to structured logs

---

## Anti-Patterns

- Trusting only management IP
- Matching only on hostname
- Auto-overwriting source-of-truth identity from live data during execution
- Continuing with warning-only identity mismatches in production

---

## Key Takeaway

Identity checks are not optional hygiene. They are a critical control that prevents high-impact, wrong-target changes.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Start of series](./index.md)
- Next: [Part 2 - Pre-Flight Checks: Failing Fast Before Making Changes](./pre-flight-checks-failing-fast-before-making-changes.md)
