---
title: Exception and Waiver Process
description: How to record, approve, and expire a deliberate deviation from a production automation control without quietly losing the control altogether.
tags:
  - Production Principles
  - Governance
  - Exceptions
  - Risk Management
  - Enterprise
---

## Exception and Waiver Process

Every control in the [Enterprise Control Matrix](./enterprise-control-matrix.md) will, at some point, be inconvenient. A device family will not support a pre-flight check. A vendor API will not return the evidence your audit trail expects. A legacy platform will refuse the credential model you standardised on.

The failure mode is not that teams grant exceptions. It is that they grant them **informally** — a comment in a pull request, a verbal "just this once", a hardcoded skip that nobody revisits. Three years later, nobody can say which controls are actually running.

An exception process exists to make the deviation **visible, owned, and temporary**.

---

## When an Exception Is the Right Answer

An exception is appropriate when all of the following hold:

- The control genuinely cannot be met, for a reason that is technical rather than convenient
- The residual risk is understood and can be described in a sentence
- Something else reduces that risk in the meantime
- Someone with the authority to accept the risk is willing to put their name to it

An exception is **not** the right answer when the real reason is schedule pressure, when nobody can articulate the risk, or when the request has no end date. Those are decisions to descope or delay the automation, not to waive the control.

---

## Required Fields

A waiver is only useful if it captures enough to be reviewed later by someone who was not in the room.

| Field | What it must record |
|---|---|
| **Requirement waived** | The specific control, part number, or standard clause — not "some of the pre-flight checks" |
| **Scope** | Which services, sites, device roles, or platforms the waiver covers, and what it explicitly does not |
| **Rationale** | Why the control cannot be met, in terms a reviewer outside the team can follow |
| **Residual risk** | What could go wrong while the waiver is in force, and how bad it would be |
| **Compensating controls** | What reduces that risk in the meantime — manual review, tighter scope, additional monitoring, a longer soak period |
| **Owner** | The named person accountable for closing the exception |
| **Approver** | The named person accepting the risk, at an authority level matching the risk class |
| **Expiry or review date** | A date, not a condition. "Until the vendor fixes it" is not an expiry |

---

## Approval Authority by Risk Class

Match the approver to the [risk class](./enterprise-control-matrix.md#automation-risk-classification) of the automation, not to the seniority of whoever is asking.

| Risk class | Appropriate approver | Maximum initial term |
|---|---|---|
| **R0 — Informational** | Automation team lead | 12 months |
| **R1 — Advisory** | Automation team lead | 12 months |
| **R2 — Controlled execution** | Operations engineering manager | 6 months |
| **R3 — Change automation** | Change manager plus security reviewer | 3 months |
| **R4 — High-impact or autonomous** | Formal risk acceptance at engineering leadership level | 1 month, renewable only with evidence |

An exception that has been renewed three times is not an exception. It is either a control your environment cannot support — in which case change the control — or work nobody has funded. Both are decisions worth surfacing.

---

## The Exception Register

Waivers that live in individual tickets are waivers nobody can count. Keep a single register — a table in your program documentation is enough to start — recording every open exception with its owner, class, and expiry.

Review it on the cadence your [Program Charter](./program-charter.md) already sets:

- **Weekly:** newly raised exceptions and anything expiring inside 30 days
- **Monthly:** total open count and trend by risk class
- **Quarterly:** exceptions renewed more than once, and controls that generate exceptions repeatedly

A rising exception count is not automatically bad — it often means a control has just been introduced and reality is catching up. A *flat* count with no closures is the warning sign.

---

## Expiry Behaviour

Decide in advance what happens when a waiver lapses, and write it down:

- **Fail closed** — the automation stops running until the exception is renewed or the control is met. Appropriate for R3 and R4.
- **Fail loud** — the automation continues but raises a visible alert on every run. Acceptable for R0 to R2 where stopping causes more harm than continuing.

What should never happen is silent expiry, where the waiver record lapses but the code keeps skipping the control indefinitely.

---

## Anti-Patterns

- **The permanent temporary waiver** — no expiry date, or an expiry that has been extended so often it has become the policy
- **The blanket waiver** — one exception covering "all legacy devices", with no list of what that actually includes
- **The self-approved waiver** — the engineer who wants the exception is also the person accepting the risk
- **The undocumented skip** — a conditional in the code that bypasses a control with no corresponding register entry
- **Compensating controls that do not exist** — "the team will check manually" with no owner, no cadence, and no evidence

---

## Worksheet

Copy this into the ticket or design record when raising an exception:

```text
Requirement waived:
Part / control reference:
Scope (in):
Scope (out):
Risk class of the automation:
Rationale:
Residual risk:
Compensating controls:
Owner:
Approver and date:
Expiry or review date:
Behaviour on expiry:  [ ] Fail closed   [ ] Fail loud
```

---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Enterprise Control Matrix](./enterprise-control-matrix.md)
- Next: [Automation Service Lifecycle](./automation-service-lifecycle.md)
