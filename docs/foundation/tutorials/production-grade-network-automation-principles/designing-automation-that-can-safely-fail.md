---
title: Designing Automation That Can Safely Fail
description: Build workflows that fail closed when needed, fail open when justified, and stop safely before causing compounded damage.
tags:
  - Production Principles
  - Failure Handling
  - Reliability Engineering
  - Safety
  - Network Automation
---

## Failure Is Not Optional

All production automation eventually encounters:

- Device timeouts
- Partial command execution
- Upstream dependency outages
- Unexpected platform behaviour

The core question is not whether failure occurs. It is whether your workflow fails in a safe direction.

---

## Fail-Closed vs Fail-Open

Use policy-driven choices:

- Fail-closed for change correctness, identity checks, and security controls
- Fail-open only for non-critical observability or advisory outputs

If uncertain, default to fail-closed for write paths.

---

## Safe Abort Conditions

Define clear hard-stop triggers:

- Identity mismatch
- Privilege mismatch
- Pre-flight critical failure
- Unexpected parser ambiguity in required checks
- Error-rate threshold exceeded in current batch

Hard stops should be deterministic and tested.

---

## Degradation Pattern

When non-critical components fail:

1. Continue only if risk model allows it
2. Mark run state as degraded
3. Increase logging and operator visibility
4. Block promotion to broader scope

Graceful degradation is useful only when safety invariants still hold.

---

## Production Checklist

- Failure policy is explicit per workflow phase
- Hard-stop triggers are codified and versioned
- Error-rate thresholds are enforced in runtime
- Degraded mode behaviour is documented and observable
- Human escalation paths are clear and tested

---

## Anti-Patterns

- Catch-all exception handling that suppresses critical faults
- Continuing writes after parser uncertainty
- Defining failure policy only in runbooks, not code
- Treating failed post-validation as minor warning

---

## Key Takeaway

Reliable automation is not code that never fails. It is code that fails predictably, safely, and early enough to prevent larger harm.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 6 - Scoping Automation to Reduce Blast Radius](./scoping-automation-to-reduce-blast-radius.md)
- Next: [Part 8 - Rollback Strategies: What Works and What Doesn't](./rollback-strategies-what-works-and-what-doesnt.md)
