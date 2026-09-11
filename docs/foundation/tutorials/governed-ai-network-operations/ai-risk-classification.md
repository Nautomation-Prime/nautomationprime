---
title: AI Risk Classification
description: A five-level scale for what an AI agent is permitted to do in network operations, and how it relates to the risk class of the workflow underneath it.
tags:
  - Governed AI
  - AI Governance
  - Risk Management
  - Controls
  - Enterprise
---

## AI Risk Classification

"Is it safe to let AI do this?" is not one question. It is two, and teams get into trouble by answering only one of them.

The first question is about the **workflow**: what does this automation do to the network? That is answered by the [risk classification](../production-grade-network-automation-principles/enterprise-control-matrix.md#automation-risk-classification) — R0 to R4.

The second is about the **model's role in it**: how much authority does the agent itself hold? That is what this scale answers.

---

## The Scale

| Class | What the agent does | Minimum controls |
|---|---|---|
| **AI-0 — Informational** | Retrieves and presents existing approved information | Authentication, scope enforcement, evidence with sources, logging |
| **AI-1 — Analytical** | Analyses retrieved evidence without proposing any change | Source traceability, stated uncertainty, deterministic calculations performed outside the model |
| **AI-2 — Advisory** | Recommends actions or assembles a proposal | Human review before anything proceeds, proposals built only from approved templates, no execution path |
| **AI-3 — Controlled execution** | Invokes a bounded, approved operation | Strong authorisation, ticket or approval where required, mandatory post-action verification, full audit correlation |
| **AI-4 — Governed autonomy** | Acts within predefined event and policy boundaries without a human initiating each run | Formal risk acceptance, deliberately narrow scope, rollback path, enhanced monitoring, documented kill control |

Most production value sits at **AI-0 to AI-2**. That is not a consolation prize — retrieval, correlation, and explanation across fragmented tooling is where engineers actually lose their day.

---

## The Two Scales Are Not the Same Thing

This is the distinction worth getting right, because conflating them produces either paralysis or false comfort.

**The R class describes the workflow. The AI class describes the agent's authority within it.**

An **AI-2 advisory agent** can quite legitimately participate in an **R3 change workflow**. The agent assembles a remediation pack from an approved template and explains it; a human reviews and approves it; a deterministic service applies it and verifies the result. The workflow changes device state, so it is R3 and needs every R3 control. The agent never executes anything, so it is AI-2.

That combination — high workflow risk, low model authority — is the target for almost everything worth building. It is how you get AI involved in change work without AI being in the execution path.

The combination to be suspicious of is the reverse: **high model authority over a low-risk workflow**. An AI-3 agent that runs read-only diagnostics sounds harmless, and mostly is, but it means you have built an execution path and pointed it somewhere safe. Execution paths get reused.

---

## Choosing a Class

Work down the list and stop at the first honest "yes":

1. **Does the agent cause anything to happen without a human deciding?** → AI-4. This needs formal risk acceptance, not a design review.
2. **Does the agent invoke an operation that touches infrastructure, even a read?** → AI-3. Authorisation and audit must be enforced by the service, not the prompt.
3. **Does the agent produce something a human is expected to act on?** → AI-2. The proposal must be an artifact, not a paragraph of prose.
4. **Does the agent interpret or analyse evidence?** → AI-1. Every conclusion needs a traceable source.
5. **Does it only fetch and present?** → AI-0.

Classify by what the agent *can* do, not what you expect it to do. An agent with a change tool enabled is AI-3 even if nobody has used that tool yet.

---

## Escalation Between Classes

Moving an agent up a class is a governance decision with a paper trail, not a configuration change.

| Move | What must happen first |
|---|---|
| **AI-0 → AI-1** | Agree how uncertainty is expressed and how sources are cited in every response |
| **AI-1 → AI-2** | Define the approved templates a proposal can be built from, and who reviews proposals |
| **AI-2 → AI-3** | Security review of the tool boundary, authorisation model, and audit correlation. Verification must be mandatory, not optional |
| **AI-3 → AI-4** | Formal risk acceptance at leadership level, a documented and tested kill control, narrowed scope, and enhanced monitoring |

Each step up should also narrow scope. An agent gaining authority should simultaneously lose reach — fewer sites, fewer device roles, fewer tools. Authority and breadth expanding together is how a useful assistant becomes an incident.

---

## Recording the Classification

Put the class in the agent's service record alongside its enabled tools, and revisit it whenever a tool is added. Enabling one new tool can move an agent from AI-2 to AI-3 without anyone noticing that the governance requirements changed with it.

Where a class cannot be met in full, that is an [exception](../production-grade-network-automation-principles/exception-and-waiver-process.md) with an owner and an expiry — not an informal allowance.

---

## Continue the Series

- Series Index: [Governed AI for Network Operations](./index.md)
- Previous: [Governed AI for Network Operations](./index.md)
- Next: [Why Your Agent Must Not Have an execute_command Tool](./why-your-agent-must-not-have-execute-command.md)
