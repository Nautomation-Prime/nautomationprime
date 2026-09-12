---
title: Why Your Agent Must Not Have an execute_command Tool
description: The case against giving an AI agent a general command tool, and how to design narrow typed tools that keep enforcement out of the model.
tags:
  - Governed AI
  - AI Governance
  - Tool Design
  - Network Automation
  - Enterprise
---

## Why Your Agent Must Not Have an execute_command Tool

Every AI network automation project reaches the same fork, usually in week one.

You have an agent. You have devices. The fastest way to connect them is one tool:

```python
def execute_command(device: str, command: str) -> str:
    """Run a command on a device and return the output."""
```

It is four lines. It works immediately. It handles every use case you have thought of and every one you have not. It is also the decision that determines whether the rest of the project is governable, and it is almost always made by an engineer at a terminal rather than in a design review.

This page argues the other path properly, because "our security team wouldn't like it" is not an argument that survives contact with a deadline.

---

## What That Tool Actually Delegates

A general command tool does not give the model the ability to run commands. It gives the model the ability to **decide what should be run**, which is a much larger transfer of authority than it appears.

Every constraint you care about now lives inside a generated string:

| Constraint | Where it lives with `execute_command` |
|---|---|
| Which device | A hostname in a generated string |
| Which operation | A command in a generated string |
| Whether it is a read or a write | Implied by the command in a generated string |
| Whether it is in scope | Nowhere |
| Whether it needs approval | Nowhere |
| What "success" means | Whatever the model concludes from the output |

You cannot enforce any of those by inspecting the string afterwards. Blocklists fail because there are more ways to change a device than you can enumerate — and because `show running-config` is a read that can leak every credential on the box. Allowlisting command prefixes fails on arguments: `show tech-support` is a read that can take a device out of service on a busy platform.

The problem is structural. Free text as an interface means the enforcement point is inside the model.

---

## Prompt Instructions Are Not Controls

The usual mitigation is to write rules into the system prompt:

> Never run configuration commands. Only run show commands. Always confirm the device before proceeding.

This is a request. It works most of the time, which is precisely what makes it dangerous — it produces the operational confidence of a control with none of the properties of one.

A control has to be:

- **Enforced somewhere the model cannot reach.** A system prompt is in the conversation. Long contexts, unusual phrasings, and multi-step reasoning all erode it.
- **Testable in isolation.** You can unit-test an authorisation function. You cannot unit-test a paragraph of English.
- **Auditable after the fact.** "The prompt said not to" is not evidence that it did not.

This is the same reasoning as the [Enterprise Control Matrix](../production-grade-network-automation-principles/enterprise-control-matrix.md) quality criterion: *enforced by code, not policy text alone*. The rule does not change because the policy text is now being read by a model instead of a person.

---

## Required Versus Not Permitted

| Required | Not permitted |
|---|---|
| Narrow operational capability, one job per tool | A general `execute_command` or `run_script` tool |
| Strict typed input schema | Unbounded free-text command or query parameters |
| Required fields and enumerations | Unknown parameters accepted or silently ignored |
| Structured results with explicit error categories | Unstructured success text with no evidence |
| Authorisation and scope enforced in the service | Reliance on prompt instructions alone |
| Every invocation correlated for audit | Untraceable tool calls |

---

## What Narrow Tools Look Like

The replacement is not one tool with guardrails. It is several tools that each do one thing and cannot do anything else.

```python
def run_diagnostic(device_id: str, diagnostic_id: DiagnosticId) -> DiagnosticResult:
    """Run one pre-approved diagnostic against one resolved device.

    diagnostic_id is an enumeration, not command text. The mapping from
    identifier to the commands it runs lives in reviewed code, not in the
    model's output.
    """
```

The important detail is `DiagnosticId`. The model chooses *which approved diagnostic is appropriate* — a genuinely useful judgement, and one it is good at. It does not choose *what runs*. That mapping was written by an engineer, reviewed in a pull request, and tested.

A working tool set looks roughly like this:

| Tool class | Examples | What keeps it bounded |
|---|---|---|
| **Discovery** | `find_devices` | Searches the source of truth, returns records and their provenance |
| **State** | `get_device_health`, `get_interface_status` | Read-only, scoped to permitted devices |
| **Diagnostics** | `run_diagnostic` | Diagnostic identifier from an enumeration, never command text |
| **Compliance** | `check_compliance`, `compare_configuration` | Deterministic policy evaluation, structured findings |
| **Proposal** | `create_remediation_pack` | Builds from an approved template, returns an immutable artifact, cannot apply it |
| **Approval and execution** | `validate_pack`, `apply_pack` | Requires ticket, checksum, scope, window, and expiry |
| **Verification** | `verify_change`, `rollback_change` | Verification mandatory after any change; rollback path predefined |

Note the shape of the change path. The model can *assemble* a proposal and *explain* it. Applying it requires an unmodified pack with a checksum, an approval, and a window — none of which the model can manufacture.

---

## The Objection: "This Is Much More Work"

It is more work, and the objection deserves a straight answer rather than a governance lecture.

Three things make it smaller than it looks:

**You have already written most of it.** Every tool above is a function your automation codebase either has or should have. If `check_compliance` does not already exist as a callable unit, the AI project has surfaced a gap that was going to hurt you anyway.

**The tool count converges fast.** Teams expect to need dozens. In practice a useful operations agent runs on eight to twelve tools, because the model composes them — it does not need a tool per scenario, it needs the right primitives.

**Narrow tools are the only version that gets approved.** A general command tool will spend six months in security review and may never emerge. A typed tool boundary with enforced authorisation and audit correlation is a conversation your security team already knows how to have. The slower-looking path ships first.

---

## The Test

If you take one thing from this page, take this question, and ask it of any agent design:

!!! question "The test"
    **If the model produced the worst possible output on its next call, what would happen?**

With a general command tool, the honest answer involves your change control process and possibly your incident bridge.

With narrow typed tools, the answer is that a schema validation fails, or an unapproved diagnostic identifier is rejected, or a proposal is generated that a human declines to approve. The model is allowed to be wrong, because being wrong is contained.

That containment is the entire design goal. Everything else is detail.

---

## Continue the Series

- Series Index: [Governed AI for Network Operations](./index.md)
- Previous: [AI Risk Classification](./ai-risk-classification.md)
- Next: [From Script to Tool](./from-script-to-tool.md)
