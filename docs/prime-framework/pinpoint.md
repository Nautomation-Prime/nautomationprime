---
title: Pinpoint
description: Stage 1 of the PRIME Framework - Identifying high-impact automation opportunities through workflow analysis and ROI estimation.
tags:
  - PRIME Framework
  - Pinpoint
  - Discovery
  - ROI
---

## Pinpoint Inefficiencies

## Stage 1 of the PRIME Framework

> **"You can't improve what you don't measure. The Pinpoint stage ensures we're automating the right things, not just the easy things."**

!!! success "Stage Outcome"
    **Deliverable:** Prioritised roadmap of automation opportunities with ROI estimates, risk assessment, and 12-month implementation plan.

    **Typical Result:** Identify £50k-£500k annual value in automation opportunities that increase efficiency, reduce errors, and improve compliance.

    ```mermaid
    graph LR
        A[🔍 Discovery] --> B[📊 Analysis]
        B --> C[🎯 Prioritisation]
        C --> D[📝 Roadmap]
        
        style A fill:#4A90E2
        style B fill:#5BA3E8
        style C fill:#6CB5EE
        style D fill:#7DC8F4
    ```

**Prime Terminology Used:** Prime Workflows identification, Prime Efficiency Stack opportunities

---

## 🎯 Objective

Identify and prioritise automation opportunities that deliver maximum value with acceptable risk and effort.

---

## 🔍 What Happens During Pinpoint

### 1. Discovery Workshop (1-2 hours)

We conduct a structured interview with your network operations team to understand:

**Operational Pain Points:**

- Which tasks consume the most time?
- Where do errors occur most frequently?
- What processes require "heroic efforts"?
- Which workflows block other work?

**Technical Landscape:**

- Device inventory (counts, platforms, OS versions)
- Existing automation (if any)
- Integration points (monitoring, CMDB, ticketing)
- Change management processes

**Constraint Mapping:**

- Regulatory requirements (PCI-DSS, HIPAA, etc.)
- Security policies and approval workflows
- Available lab/dev environments
- Team Python proficiency

---

### 2. Workflow Time-Motion Study

For each identified pain point, we quantify:

| Metric | Purpose |
| :--- | :--- |
| **Frequency** | How often does this task occur? |
| **Duration** | How long does it take manually? |
| **Error Rate** | What percentage require rework? |
| **Dependencies** | What does this task block? |
| **Risk Level** | What's the impact if it fails? |

**Example:**

    ```text
    Task: Add VLANs to access switches
    Frequency: 40 times/month
    Duration: 15 minutes per switch (average 5 switches/change)
    Error Rate: 12% require config rollback
    Dependencies: Blocks user onboarding, new site deployments
    Risk: Low (access layer, easy rollback)
    ```

**Annual Impact:** 40 × 5 × 15 minutes = **50 hours/year** of manual effort

---

### 3. Automation Feasibility Assessment

Not all tasks are good automation candidates. We evaluate each opportunity against:

#### ✅ Good Automation Candidates

- **High frequency, low complexity** — VLAN adds, port configurations
- **Error-prone** — Repetitive config with variation (easy to fat-finger)
- **Time-sensitive** — Changes needed outside business hours
- **Blocked by availability** — Tasks requiring specific engineer knowledge
- **Audit-heavy** — Compliance checks, configuration validation

#### ❌ Poor Automation Candidates

- **Rarely performed** — One-off migrations, infrequent changes
- **Highly variable** — Every instance is completely different
- **Requires judgment** — Troubleshooting, design decisions
- **Political/organisational** — Automation won't solve process problems
- **Already solved** — Don't reinvent vendor tools

---

### 4. ROI Estimation

For each feasible automation, we calculate:

!!! info "Why ROI Estimation Matters"
    This is how we prove the business case. Leadership doesn't invest in automation out of principle—they invest because the financial case is clear. Every recommended automation has a payback period estimate.

**Time Savings:**

    ```text
    Annual Time Saved = Frequency × Duration × (1 - Automation Time Ratio)

    Example (VLAN provisioning):
    = 40/month × 12 months × 15 mins × (1 - 0.1)
    = 480 changes × 15 mins × 0.9
    = 108 hours/year saved
    ```

**Error Reduction:**

    ```text
    Annual Errors Avoided = Frequency × Error Rate × Remediation Time

    Example:
    = 480 changes × 12% × 45 mins (avg rollback time)
    = 57.6 errors × 45 mins
    = 43 hours/year saved from error remediation
    ```

**Total Annual Savings:** 108 + 43 = **151 hours/year**

**Financial Impact:** 151 hours × £50/hour = **£7,550/year**

!!! success "Output: Prioritised Roadmap"
    All opportunities are ranked by ROI. Your leadership sees:

    - Which automations save the most money (top 5, top 10, etc.)
    - When each will pay back (weeks, months, or years)
    - Risk level for each (low, medium, high)
    - Required team effort and dependencies
    
    This roadmap guides the entire PRIME Framework engagement.

---

### 5. Effort Estimation

We estimate the implementation effort for each automation:

| Complexity | Typical Effort | Examples |
| :--- | :---: | :--- |
| **Simple** | 1-2 weeks | Single-device show command collection, basic config backups |
| **Medium** | 3-5 weeks | Multi-device config changes with validation, inventory audits |
| **Complex** | 6-12 weeks | Multi-stage workflows, external integrations, stack/chassis awareness |

---

### 6. Prioritisation Matrix

We plot each opportunity on an impact/effort matrix:

    ```mermaid
    quadrantChart
        title Automation Prioritisation Matrix
        x-axis Low Effort --> High Effort
        y-axis Low Impact --> High Impact
        quadrant-1 Major Projects
        quadrant-2 Quick Wins
        quadrant-3 Avoid
        quadrant-4 Hard Pass
    ```

**Prioritisation Criteria:**

1. **Quick Wins** (High Impact, Low Effort) — **Start here**
2. **Major Projects** (High Impact, High Effort) — Schedule after quick wins
3. **Hard Pass** (Low Impact, High Effort) — Defer indefinitely
4. **Avoid** (Low Impact, Low Effort) — Only if spare capacity

---

## 📊 Deliverable: Automation Roadmap

At the end of the Pinpoint stage, you receive:

### 1. Prioritised Automation Backlog

A ranked list of automation opportunities with:

- Detailed task description
- Estimated time savings (hours/year)
- Financial impact (£/year)
- Implementation effort (weeks)
- Risk assessment
- Dependencies and prerequisites
- Recommended implementation order

**Example Extract:**

| Priority | Automation | Annual Savings | Effort | ROI |
| :---: | :--- | ---: | :---: | ---: |
| 1 | VLAN provisioning | £7,550 | 3 weeks | 12 months |
| 2 | Config compliance audits | £8,000 | 4 weeks | 8 months |
| 3 | Port health monitoring | £4,200 | 2 weeks | 6 months |

---

### 2. Executive Summary

One-page business case including:

- Total annual savings potential
- Recommended Phase 1 automations
- Investment required
- Expected payback period
- Risk mitigation approach

---

### 3. Technical Feasibility Notes

For each automation:

- Platform compatibility (IOS, IOS-XE, NX-OS)
- Required libraries (Netmiko, Nornir, NAPALM)
- Integration points (DNS, IPAM, CMDB)
- Test environment requirements

---

## 💡 Why Pinpoint Matters

### Prevents Common Mistakes

❌ **Automating low-value tasks** — "We automated config backups but still spend 90% of time on changes"  
✅ **Focus on bottlenecks** — Identify what actually blocks work

❌ **Underestimating complexity** — "It's just a simple script" becomes a 6-month project  
✅ **Honest effort estimates** — Set realistic expectations upfront

❌ **No business case** — Can't justify continued investment without ROI data  
✅ **Clear financial impact** — Speak the language of decision-makers

---

## 🚀 What Happens Next

After the Pinpoint stage, you can:

### Option 1: Proceed to Re-engineer

Move to [Stage 2: Re-engineer Workflows](./re-engineer.md) for your top-priority automations. Design optimised processes before coding begins.

### Option 2: Internal Implementation

Use the roadmap to guide your own internal automation efforts. Our [Tutorials](../foundation/tutorials/index.md) and [Deep Dives](../foundation/deep-dives/index.md) provide the technical skills.

### Option 3: Assessment Only

Some clients use Pinpoint as a standalone service to understand their automation opportunities before committing to implementation.

---

## 📋 Pinpoint Checklist

Before moving to the Re-engineer stage, ensure:

- [ ] All major operational workflows have been examined
- [ ] Time-motion data collected for top pain points
- [ ] ROI calculations validated with finance/leadership
- [ ] Technical feasibility confirmed for priority items
- [ ] Test/lab environment availability confirmed
- [ ] Team capacity and timeline agreed
- [ ] Executive sponsorship secured

---

## 💼 Engagement Options

### Pinpoint as Part of Full PRIME Engagement

Included as Stage 1 when you engage for the complete framework. Typically 1 week duration.

### Standalone Pinpoint Assessment

**Fixed Fee:** £2,500 - £4,000 (depending on network size)

**Includes:**

- Discovery workshop
- Prioritised automation roadmap
- ROI analysis
- Executive summary
- Technical feasibility notes

**Timeline:** 1-2 weeks from kickoff to delivery

**Perfect for:** Organisations exploring automation maturity or building internal business cases

---

## 🎓 Learn More

- **[PRIME Framework Overview](./index.md)** — See how all five stages work together
- **[Next Stage: Re-engineer](./re-engineer.md)** — Process optimisation before automation
- **[View Services](../services.md)** — Engagement models and pricing
- **[Request Discovery Call](../contact.md)** — Discuss your automation needs

---

> **Mission:** To empower network engineers through the **[PRIME Framework](./index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](./philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.

---

[← Back to PRIME Framework](./index.md) | [Next Stage: Re-engineer →](./re-engineer.md)
