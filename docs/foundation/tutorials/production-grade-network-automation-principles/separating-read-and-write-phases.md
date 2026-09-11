---
title: Separating Read and Write Phases in Automation Workflows
description: Separate discovery, validation, planning, and execution to improve safety, debuggability, and operator trust.
tags:
  - Production Principles
  - Workflow Design
  - Read Write Separation
  - Reliability
  - Network Automation
---

## Why Phase Separation Matters

Mixed read/write scripts are hard to reason about under failure.

When discovery, planning, and execution are blended:

- Operators cannot review intended changes clearly
- Debugging is harder after partial execution
- It becomes difficult to reproduce run decisions

Phase separation makes behaviour inspectable and controllable.

---

## Recommended Workflow Stages

1. Discovery: collect live facts
2. Validation: enforce policy and prerequisites
3. Planning: compute diff and proposed actions
4. Approval: optional human gate
5. Execution: apply approved plan only
6. Verification: confirm intended state and service health

Each stage should emit structured artifacts.

---

## Plan Artifact Pattern

Before any write, produce a plan document containing:

- Target list and scope constraints
- Pre-flight status per target
- Intended changes per target
- Risk classification and rollback option
- Approval metadata (if required)

Execution then consumes this immutable plan.

---

## Operational Benefits

Phase separation improves:

- Safety: easier to block unsafe writes
- Explainability: clear reason for each action
- Repeatability: same plan can be re-run predictably
- Auditability: artifacts show what was intended vs applied

---

## Production Checklist

- Read and write logic are implemented as separate phases
- Plan output is reviewable before execution
- Execution is blocked without a valid plan artifact
- Verification runs after writes and is persisted
- Operators can replay a run from artifacts

---

## Anti-Patterns

- Auto-generating and applying plan in one opaque function
- No durable plan artifact
- Mutating target scope during execution phase
- Skipping verification due to time pressure

---

## Key Takeaway

Separating read and write phases turns automation from a script into a reliable operational system.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 8 - Rollback Strategies: What Works and What Doesn't](./rollback-strategies-what-works-and-what-doesnt.md)
- Next: [Part 10 - Making Automation Output Operator-Friendly](./making-automation-output-operator-friendly.md)
