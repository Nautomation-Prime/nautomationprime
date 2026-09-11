---
title: From Script to Tool
description: How to turn an existing Python automation script into a narrow, typed, governed tool an AI agent can safely call — using a real compliance audit as the worked example.
tags:
  - Governed AI
  - Tool Design
  - Python
  - Refactoring
  - Enterprise
---

## From Script to Tool

The previous page argued that agents need narrow typed tools rather than a general command tool. The obvious next question is where those tools come from — and the answer is usually less work than teams expect, because most of it is already written.

If you have production automation, you have most of a tool. What you do not have yet is the boundary around it.

This page uses the [Cisco IOS-XE Compliance Audit](../../deep-dives/cisco-compliance-audit.md) as the worked example, because it is already close: config-driven checks, a structured parser, categorised results. The refactor below applies to any script with a clear job.

---

## What Actually Changes

Here is the whole idea in one line, and everything else on this page follows from it:

!!! quote "The shift"
    **A CLI is called by an engineer who chose the arguments. A tool is called by a model that inferred them.**

That single change reclassifies every input. When an engineer types `--site MAN-DC1`, they know what that site is, they meant to type it, and they will notice if the output looks wrong. When a model supplies `site="MAN-DC1"`, it inferred that value from a conversation, possibly from a user's typo, possibly from something it read in a device banner.

Nothing about your check logic needs to change. Everything about how the arguments arrive does.

---

## The Five Changes

### 1. Separate the callable from the command line

Most scripts fuse three jobs into `main()`: parsing arguments, doing the work, and deciding an exit code. A tool needs the middle one on its own.

In the compliance audit, `main()` handles CLI parsing and exit behaviour, while the orchestrator does the actual work. That separation is already most of the way there — the goal is a function you can call with values rather than with `sys.argv`, that returns a result rather than printing one and exiting.

If your script cannot be imported and called without side effects, start here. This is also the point where [never connecting to devices at import time](../production-grade-network-automation-principles/pre-flight-checks-failing-fast-before-making-changes.md) stops being a style preference and becomes structural.

### 2. Make the input a schema, not a string

Command-line arguments are strings by convention. Tool inputs must be typed, bounded, and rejected when unrecognised.

The rule from the [tool boundary](./why-your-agent-must-not-have-execute-command.md) applies directly: anything that selects *what runs* becomes an enumeration. Anything that selects *what it runs against* becomes an identifier resolved through your source of truth. Free text survives only where it genuinely cannot affect behaviour — a ticket reference, a comment.

For a compliance audit that means the check category is an enum drawn from your policy model, not a string the model composes. The set of valid categories is knowable at build time. Make the schema say so.

### 3. Enforce scope inside the function

A CLI inherits its scope from the engineer's judgement and the credential they are using. A tool cannot.

Scope enforcement belongs inside the callable, before any device is contacted: is this target in the permitted set for this caller, this environment, this lifecycle state? Rejecting out-of-scope targets is not the agent's job and it is definitely not the prompt's job. It is a function that returns a decision, and it is testable.

### 4. Return structured results, not printed output

Scripts print. Tools return.

This is more than formatting. Printed output forces the model to parse prose to work out what happened, which is exactly where confident misreadings come from. A structured result says what was checked, what passed, what failed, at what severity, with what evidence, and against what baseline — and the model's job becomes explaining it rather than inferring it.

The compliance audit already produces categorised findings. Returning them as data rather than a report is a serialisation change, not a redesign.

### 5. Categorise the errors

"It failed" is not a result a model can reason about safely. The difference between *device unreachable*, *target not in scope*, *check unsupported on this platform*, and *authentication rejected* determines whether retrying is sensible, whether to escalate, and whether to tell the user something is wrong with their request rather than with the network.

Give errors a category and let the agent's behaviour depend on it. This is the same reasoning as [designing automation that can safely fail](../production-grade-network-automation-principles/designing-automation-that-can-safely-fail.md), applied at the boundary.

---

## What You Do Not Change

Worth stating plainly, because "make it AI-ready" invites over-engineering:

- **The check logic stays as it is.** If your compliance rules are correct today, they are correct when a model asks for them.
- **The parser stays as it is.** Structured collection and config parsing are unaffected by who calls them.
- **The policy model stays as it is.** Checks defined in configuration rather than code were already the right design, and they are what makes the enumeration in change 2 possible.

The refactor is a boundary, not a rewrite. If it is turning into a rewrite, the script probably had a design problem that the AI work has usefully surfaced.

---

## The Shape You End Up With

```python
def check_compliance(
    device_id: DeviceId,          # resolved through the source of truth, not a hostname string
    category: CheckCategory,      # enumeration from the policy model
    caller: CallerContext,        # identity and permitted scope
) -> ComplianceResult:            # structured findings, severity, evidence, baseline reference
    """Evaluate one approved check category against one in-scope device."""
```

Four things are true of that signature that were not true of the CLI:

- The model cannot express an operation that does not exist
- The model cannot reach a device it is not permitted to reach
- The result cannot be misread, because it is not prose
- Every call can be logged with its inputs, its caller, and its outcome

None of that depends on the model behaving well.

---

## Where This Leaves You

A tool boundary is one half of a governed agent. The other half — transport, identity, authorisation, audit correlation — is a platform concern and is deliberately out of scope here, because it depends heavily on what your organisation already runs.

What this refactor gives you is the part that is yours regardless of platform: capabilities that are narrow by construction, and that stay safe no matter what calls them. Build them for the agent if that is what justifies the work. You will find they also make your existing automation easier to test, reuse, and hand over.

Before any of it goes near production, run the [Agent Review Checklist](./agent-review-checklist.md).

---

## Continue the Series

- Series Index: [Governed AI for Network Operations](./index.md)
- Previous: [Why Your Agent Must Not Have an execute_command Tool](./why-your-agent-must-not-have-execute-command.md)
- Next: [Agent Review Checklist](./agent-review-checklist.md)
