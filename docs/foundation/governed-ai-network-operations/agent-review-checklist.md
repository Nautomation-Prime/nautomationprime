---
title: Agent Review Checklist
description: Ten questions to answer before an AI agent is allowed near production network operations, with the evidence each answer requires.
tags:
  - Governed AI
  - AI Governance
  - Checklist
  - Change Review
  - Enterprise
---

## Agent Review Checklist

Use this during design review and again before production approval. It is deliberately answerable in one sitting — if a question cannot be answered in a sentence, that is the finding.

Every question below has a required answer. A deviation is not a discussion; it is an [exception](../production-grade-network-automation-principles/exception-and-waiver-process.md) with an owner, a compensating control, and an expiry date.

---

## 1) Purpose and Scope

- Agent name and owner:
- Documented operational purpose:
- Intended users and how access is granted:
- Sites, device roles, and environments in scope:
- Explicit exclusions:
- [AI risk class](./ai-risk-classification.md) (AI-0 to AI-4):

| Question | Required answer | Evidence |
|---|---|---|
| Does the agent have a narrow, documented purpose? | **Yes** | Purpose statement in the service record |
| Is the user population defined and access controlled? | **Yes** | Identity group or role mapping |

---

## 2) Tool Boundary

- Enabled tools (complete list):
- Tools available on the platform but deliberately not enabled:
- Who can change the enabled set, and through what process:

| Question | Required answer | Evidence |
|---|---|---|
| Are only approved tools enabled? | **Yes** | Enabled-tool inventory, reviewed |
| Can it execute arbitrary commands, scripts, or API calls? | **No** | Tool schemas showing enumerations, not free text |
| Does every tool have a strict typed input schema? | **Yes** | Schema definitions |
| Are unknown parameters rejected rather than ignored? | **Yes** | Validation tests |

If any tool accepts free-text that reaches a device, stop here. See [Why Your Agent Must Not Have an execute_command Tool](./why-your-agent-must-not-have-execute-command.md).

---

## 3) Targeting and Scope Enforcement

- How a user request is resolved to a device:
- Source of truth used:
- What happens on an ambiguous or unknown target:

| Question | Required answer | Evidence |
|---|---|---|
| Does it resolve targets through an authoritative source rather than trusting user input? | **Yes** | Resolution path documented |
| Does it display the resolved target before acting? | **Yes** | Sample transcripts |
| Are out-of-scope and unknown targets rejected? | **Yes** | Negative test results |
| Is scope enforced in the service rather than the prompt? | **Yes** | Authorisation code and tests |

---

## 4) Evidence and Response Quality

- How sources are cited in responses:
- How uncertainty is expressed:

| Question | Required answer | Evidence |
|---|---|---|
| Are observed facts separated from recommendations? | **Yes** | Sample transcripts |
| Does every operational claim name its source and timestamp? | **Yes** | Sample transcripts |
| Does the response state whether anything changed? | **Yes** | Sample transcripts for both read and change paths |

---

## 5) Change Path (If Any)

Skip this section only if no enabled tool can alter device state — and confirm that by reading the tool list, not by assumption.

- Templates a proposal can be built from:
- Approval mechanism and approver population:
- Verification performed after a change:
- Rollback path:

| Question | Required answer | Evidence |
|---|---|---|
| Are write controls deterministic and external to the model? | **Yes** | Service code and tests |
| Is freeform generated configuration prevented from reaching a device? | **Yes** | Design review record |
| Does execution require an unmodified approved artifact? | **Yes** | Checksum and expiry enforcement tests |
| Is post-change verification mandatory rather than optional? | **Yes** | Verification code path with no bypass |
| Is there a tested rollback or escalation path? | **Yes** | Rollback test evidence |

---

## 6) Secrets and Data Protection

| Question | Required answer | Evidence |
|---|---|---|
| Are secrets absent from prompts, instructions, schemas, code, and images? | **Yes** | Repository and image scan results |
| Are credentials and sensitive configuration redacted from responses? | **Yes** | Redaction tests |
| Is the operational data returned to the model minimised to what the task needs? | **Yes** | Data flow review |

---

## 7) Audit and Monitoring

| Question | Required answer | Evidence |
|---|---|---|
| Is every tool invocation auditable and correlated to a user and conversation? | **Yes** | Audit records from a test run |
| Are attempts to use disabled tools logged? | **Yes** | Log samples |
| Is agent usage, latency, failure rate, and dependency health monitored? | **Yes** | Dashboard or alert definitions |

---

## 8) Failure Behaviour

- Behaviour on downstream timeout:
- Behaviour on partial failure across multiple targets:
- Behaviour when identity cannot be established:

| Question | Required answer | Evidence |
|---|---|---|
| Does it fail closed on ambiguity, mismatch, or missing controls? | **Yes** | Negative test results |
| Does it avoid converting uncertainty into a speculative action? | **Yes** | Adversarial prompt test results |

---

## 9) Ownership and Support

| Question | Required answer | Evidence |
|---|---|---|
| Is ownership defined for the service, its technical implementation, and its operation? | **Yes** | Named owners in the service record |
| Is there a support and escalation route for users? | **Yes** | Runbook |
| Are documented limitations published to users? | **Yes** | User-facing guidance |

---

## 10) Approval

- Reviewers (security, architecture, operations):
- Pilot audience and duration, if applicable:
- Open exceptions and their expiry dates:

Outcome:

- [ ] Approved for production
- [ ] Approved for pilot with named users and scope
- [ ] Returned for remediation
- [ ] Rejected

Approver name, role, and date:

---

## Re-Review Triggers

Re-run this checklist, in full, when any of the following happen. Each can change the agent's risk class without any visible change to how it behaves day to day.

- A tool is added or its schema is widened
- Scope expands to new sites, device roles, or environments
- The underlying model or platform version changes
- An incident involves the agent, or a near miss is reported
- An exception expires
- Twelve months pass with none of the above

---

## Continue the Series

- Series Index: [Governed AI for Network Operations](./index.md)
- Previous: [From Script to Tool](./from-script-to-tool.md)
- Next: [End of track](../index.md)
