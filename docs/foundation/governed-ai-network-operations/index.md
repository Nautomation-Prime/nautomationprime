---
title: Governed AI for Network Operations
description: How to let AI help engineers operate a network without giving a language model an execution path to your infrastructure.
tags:
  - Governed AI
  - AI Governance
  - Network Automation
  - Risk Management
  - Enterprise
---

## Governed AI for Network Operations

Most network teams are being asked the same question right now, usually by someone above them: *what is our AI plan?*

The tempting answer is a demo. Connect a language model to a device, ask it something in plain English, watch it run a command and summarise the output. It takes an afternoon and it looks remarkable.

It is also the single most dangerous thing you can build on a production network, because it makes the model an execution path. Everything downstream of that decision — audit, approval, scope, rollback — becomes advisory.

This track is about the other answer: AI that genuinely helps engineers, with no route from a generated token to a configuration line.

---

## The Boundary Rule

One sentence carries most of the weight:

!!! quote "The boundary"
    **AI interprets intent. Deterministic services enforce policy and execute.**

The model is allowed to be uncertain, creative, and occasionally wrong — because nothing it produces reaches the network directly. Validation, authorisation, scope, approval, and execution all live in ordinary code that you can test, review, and reason about.

This is not a limitation you accept reluctantly. It is what makes the capability approvable at all. Security teams do not object to AI reading inventory data. They object to unbounded execution, and they are right to.

---

## Why "Give the Model SSH Access" Fails

It is worth being specific about the failure modes, because they are not the ones people expect.

**It is not mainly about hallucination.** A model that invents an interface name usually produces a command that fails harmlessly. The dangerous outputs are the *plausible* ones — a syntactically perfect command aimed at the wrong device, or the right command with a subtly wrong scope.

**Prompt instructions are not a control.** "Never run configuration commands" in a system prompt is a request, not an enforcement boundary. It can be argued with, worked around, or simply lost in a long conversation. A control that can be talked out of is not a control.

**The audit trail dissolves.** When the model composes the command, there is no stable artifact to approve. You cannot attach a ticket to something that will be regenerated slightly differently next time. This is the same problem the [read/write phase separation](../production-grade-network-automation-principles/separating-read-and-write-phases.md) principle solves in conventional automation, and it applies with more force here.

**Scope becomes unbounded by default.** A general command tool works on every device the credential can reach. Restricting it means parsing intent out of free text — which puts the model back in the enforcement path.

---

## Operating Principles

| Principle | What it requires |
|---|---|
| **Human accountable** | A named person or role remains accountable for every decision and change. The agent is never the accountable party |
| **Deterministic execution** | The model may interpret intent; approved services enforce validation, policy, scope, and execution |
| **Evidence before opinion** | Operational claims are supported by retrieved evidence, with the source named. No assertion without provenance |
| **Read-only by default** | Requests are observational unless change intent *and* change authority are both explicit |
| **Least privilege** | Agents and tools receive only the access their approved use cases require — see [Safety Over Speed](../../prime-framework/philosophy.md) |
| **Fail closed** | Ambiguous targets, unsupported actions, and missing controls result in no action, not a best guess |
| **Transparency** | Responses state sources, scope, uncertainty, validation results, and whether anything changed |
| **Auditability** | User, conversation, tool invocation, target, approval, and result are correlated into one traceable record |

---

## What AI Is Genuinely Good At Here

The governance framing above is restrictive on purpose, but it leaves a large and genuinely useful surface area:

| Use case | What the model does |
|---|---|
| **Discovery** | Finds and presents approved inventory records without the engineer learning a query syntax |
| **Health assessment** | Coordinates approved health and diagnostic tools across several systems in one request |
| **Incident triage** | Gathers, correlates, and summarises evidence from monitoring, controllers, and inventory |
| **Compliance** | Presents deterministic policy findings, grouped and explained by severity |
| **Configuration comparison** | Explains a structured diff against an approved baseline in language a duty engineer can act on |
| **Reporting** | Summarises approved operational data with source references and timestamps |
| **Change preparation** | Assembles a proposed remediation pack from an approved template — proposed, never applied |
| **Readiness assessment** | Runs approved pre-change checks and returns pass, fail, or manual review |

Notice what these have in common: the model is doing **retrieval, correlation, and explanation**. That is what language models are actually good at. It is also, not coincidentally, the part of an engineer's day that involves the most tab-switching and the least judgement.

---

## What Stays Off the Table

- Direct model access to network devices
- Arbitrary CLI, script, or API execution
- Invented device state, commands, results, tickets, or approvals
- Unrestricted configuration generation and application
- Bypassing identity, scope, ticket, approval, or change controls
- Exposure of passwords, tokens, or complete sensitive configuration
- Autonomous production remediation without explicit, recorded governance approval
- Treating user or model input directly as a connection target

!!! danger "Non-negotiable"
    Freeform AI-generated configuration must not be applied directly to network infrastructure. If a change reaches a device, it came from an approved template, through a validation path, with an approval attached.

---

## Where This Sits in Your Capability Ladder

Governed AI is levels 4 and 5 of the [Automation Capability Model](../../prime-framework/empower.md#automation-capability-model). That ordering matters: an organisation without reliable inventory, tested workflows, and audit evidence at levels 2 and 3 does not get to skip to level 4 because the demo was impressive.

If your source of truth is not trusted today, AI will confidently report incorrect things faster than a human could. Fix the foundation first — the [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md) track is that foundation.

---

## In This Track

1. [AI Risk Classification](./ai-risk-classification.md) — A five-level scale for what the model is permitted to do, and how it relates to workflow risk
2. [Why Your Agent Must Not Have an execute_command Tool](./why-your-agent-must-not-have-execute-command.md) — The single most important design decision, argued properly
3. [From Script to Tool](./from-script-to-tool.md) — Turning automation you already have into something an agent can safely call
4. [Agent Review Checklist](./agent-review-checklist.md) — Ten questions to answer before an agent goes anywhere near production

---

## Getting Help With This

The standard above is free and complete — you do not need us to apply it. If you would rather have the review done with you, and the findings written up in a form your security and change governance teams will accept, that is the [AI Agent Governance Review](../../services.md#individual-services).

---

## Continue the Series

- Next: [AI Risk Classification](./ai-risk-classification.md)
- Related: [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md)
