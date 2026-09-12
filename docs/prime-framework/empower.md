---
title: Empower
description: Stage 5 of the PRIME Framework - Building internal capability through knowledge transfer, training, and sustainable automation practices.
tags:
  - PRIME Framework
  - Empower
  - Knowledge Transfer
  - Training
---

## Empower Your Team

## Stage 5 of the PRIME Framework

> **"The best automation is the automation your team can maintain and extend. The Empower stage ensures long-term success through knowledge transfer and capability building."**

!!! success "Stage Outcome"
    **Deliverable:** Trained team with full understanding of codebase, runbooks for operation/troubleshooting, and capability to extend automation independently.
  
    **Typical Result:** Your team achieves (Prime Capability)—zero dependency on consultants, ability to modify and scale automation, sustainable long-term value.

    ```mermaid
    graph LR
        A[🏛️ Training] --> B[📚 Documentation]
        B --> C[🔧 Practice]
        C --> D[🎓 Prime Capability]
        D -->|Independent| E[🚀 Scale]
        
        style A fill:#FF6B9D
        style B fill:#FF7BAD
        style C fill:#FF8BBD
        style D fill:#FF9BCD
        style E fill:#FFABDD
    ```

**Prime Terminology Used:** Prime Capability achievement, Prime Workflows extension, Prime Agents maintenance

---

## 🎯 Objective

Transfer knowledge and build internal capability so your team can maintain, troubleshoot, and extend automation without ongoing external dependency.

---

## 🚀 What Happens During Empower

### 1. Knowledge Transfer Sessions

Comprehensive handoff of developed automation:

!!! success "Building Prime Capability"
    Prime Capability means your team can modify, troubleshoot, and extend automation without consulting us. These sessions build exactly that—transferable understanding, not just operational knowledge. Your team leaves knowing not just *what* the code does, but *why* it does it that way.

#### Session 1: Architecture Overview (2 hours)

**Topics Covered:**

- **Project Goals Review:** What problem does this solve?
- **Workflow Design:** How does data flow through the automation?
- **Component Architecture:** What libraries/tools are used and why?
- **File Structure:** Where to find code, configs, templates, outputs
- **Integration Points:** External systems (DNS, IPAM, ticketing)

**Deliverable:** Architecture diagram with narrative documentation

---

#### Session 2: Code Walkthrough (2-3 hours)

**Topics Covered:**

- **Main execution flow:** Step-by-step through the code
- **Key functions:** Purpose and parameters for each
- **Configuration files:** What settings can be changed
- **Templates:** How to modify Jinja2 configs for new scenarios
- **Error handling:** What each exception handles and why

**Format:** Live screen share with Q&A, recorded for reference

**Example Walkthrough:**

    ```python
    # START: Main execution
    def main():
        """
        WHY THIS EXISTS:
        Entry point for VLAN provisioning automation.
        
        WHAT IT DOES:
        1. Loads device inventory from CSV
        2. Connects to each device
        3. Applies VLAN config with validation
        4. Generates Excel report
        
        HOW TO MODIFY:
        - Change inventory source: Edit load_device_inventory()
        - Add validation steps: Modify verify_vlan_creation()
        - Change report format: Edit generate_report()
        """
        logger.info("=== VLAN Provisioning Started ===")
        
        # STEP 1: Load devices
        # WHY: CSV allows non-Python staff to manage inventory
        # HOW TO CHANGE: Swap to Netbox API in load_device_inventory()
        devices = load_device_inventory("inventory.csv")
    ```

---

#### Session 3: Operations & Troubleshooting (2 hours)

**Topics Covered:**

- **How to run the automation:** Command-line arguments, config files
- **How to read the logs:** What INFO/WARNING/ERROR mean
- **Common failure scenarios:** Device unreachable, auth failure, config rejected
- **How to troubleshoot:** Enabling debug mode, reading stack traces
- **How to rollback:** Manual rollback procedures if auto-rollback fails

**Hands-On Exercise:**

Team members run automation in lab environment with deliberately introduced failures:

- Device with wrong IP (unreachable)
- Device with wrong credentials (auth failure)
- Device with conflicting VLAN ID (config validation failure)

Practice reading logs and identifying root cause.

---

#### Session 4: Modification & Extension (2-3 hours)

**Topics Covered:**

- **Making common changes:** Add new device types, modify templates
- **Adding new features:** Example walkthrough of small enhancement
- **Testing changes:** How to test in lab before production
- **Git workflow:** Branching, committing, merging (if using source control)
- **When to ask for help:** Complexity boundaries

**Hands-On Exercise:**

Modify automation for new use case:

- Example: "Add capability to remove VLANs (not just create)"
- Walk through: Update template, add validation, test in lab

---

### 2. Documentation Package

Comprehensive written materials for long-term reference:

#### User Guide

**Target Audience:** Network engineers who will run the automation

**Contents:**

    ```markdown
    # VLAN Provisioning Automation - User Guide

    ## Quick Start
    1. Copy `inventory_template.csv` and add your devices
    2. Run: `python provision_vlan.py --vlan 150 --name "Guest_WiFi"`
    3. Check `outputs/` folder for Excel report

    ## Detailed Usage
    ### Command-Line Arguments

    - `--vlan` : VLAN ID to create (required)
    - `--name` : VLAN name (required)
    - `--inventory` : Path to device CSV (default: inventory.csv)
    - `--dry-run` : Validate without applying changes

    ### Example Commands
    ```bash
    # Normal execution
    python provision_vlan.py --vlan 150 --name "Guest_WiFi"

    # Dry-run (validation only)
    python provision_vlan.py --vlan 150 --name "Guest_WiFi" --dry-run

    # Custom inventory file
    python provision_vlan.py --vlan 150 --name "Guest_WiFi" --inventory devices_dc1.csv
    ```

## Understanding the Output

### Log Files

- `vlan_provisioning.log` : Detailed execution log
    - **INFO**: Normal operations
    - **WARNING**: Devices skipped (with reason)
    - **ERROR**: Failures requiring attention

### Excel Reports

Generated in `outputs/vlan_provisioning_TIMESTAMP.xlsx`

Columns:

- Device: Switch hostname
- IP: Management IP
- Status: success/failed
- Duration: Seconds to process
- Error: Reason if failed

---

#### Technical Reference

**Target Audience:** Engineers who will modify/extend the automation

**Contents:**

- **Code architecture:** Component diagram w/ descriptions
- **Function reference:** Purpose, parameters, return values for each function
- **Configuration files:** What each setting controls
- **Template syntax:** How to modify Jinja2 templates
- **Adding new device types:** Step-by-step guide
- **Testing procedures:** Lab setup, test cases
- **Troubleshooting guide:** Common issues & solutions

---

#### Runbook

**Target Audience:** Operations team for incident response

**Contents:**

    ```markdown
    # VLAN Provisioning Automation - Runbook

    ## Emergency Procedures

    ### Automation Failed Mid-Execution
    **Symptoms:** Some devices configured, others not
    **Resolution:**
    1. Check log file for last successful device
    2. Update inventory.csv to include only failed devices
    3. Re-run automation with updated inventory

    ### All Devices Failing with Auth Error
    **Symptoms:** "Authentication failed" for all devices
    **Resolution:**
    1. Verify credentials in `.env` file unchanged
    2. Test manual SSH to one device
    3. Check account lockout in authentication system
    4. If credential rotation, update `.env` file

    ### VLAN Created but Validation Failed
    **Symptoms:** Config applied but post-flight check failed
    **Resolution:**
    1. Manual verification: ssh to device, `show vlan brief`
    2. If VLAN exists: False alarm, check parsing logic
    3. If VLAN missing: Check `show running-config` for rejected config
    ```

---

### 3. Self-Service Resources

We provide pathways for continued learning:

**Curated Learning Path:**

1. **Start Here:** [Nautomation Prime Beginner Tutorials](../foundation/tutorials/beginner/index.md)
2. **Next Steps:** [Intermediate Topics](../foundation/tutorials/intermediate/index.md)
3. **Advanced:** [Expert-Level Patterns](../foundation/tutorials/expert/index.md)
4. **Deep Dives:** [Real-World Scripts](../foundation/deep-dives/index.md)

**External Resources:**

- Recommended books (Python for network engineers)
- Online courses (Udemy, Pluralsight, CBT Nuggets)
- Community forums (Network to Code Slack, Reddit r/networking)
- Vendor documentation (Netmiko, Nornir, NAPALM)

---

### 4. Ongoing Support Transition

Structured handoff from full support to self-sufficiency:

#### Support Tiers

### Months 1-2: Full Support

- Unlimited email/Slack support
- 4-hour response time for issues
- Troubleshooting assistance
- Code modification help

### Months 3-4: Guided Support**

- Email support (next business day)
- Weekly office hours (30-min video call)
- Review of team modifications
- Guidance on extension projects

### Months 5-6: Advisory Support**

- Ad-hoc consultation (scheduled)
- Code review on request
- Architecture guidance for major extensions

### *Post-6 Months: Self-Sufficient + Retainer (Optional)**

- Team operates independently
- Optional retainer for complex enhancements
- Priority support if needed

---

### 5. Community of Practice

We help establish internal momentum:

#### Automation Guild (Optional)

For organisations with multiple network engineers:

**Structure:**

- Monthly 1-hour meeting
- Demo recent automations
- Share lessons learned
- Collaborate on new use cases
- Review code together

**Benefits:**

- Cross-pollination of ideas
- Peer learning
- Consistent code standards
- Shared troubleshooting knowledge

---

### 6. Success Metrics for Empowerment

We measure knowledge transfer effectiveness:

#### Capability Milestones

| Milestone | Target Timeline | How We Measure |
| :--- | :---: | :--- |
| **Team can run automation independently** | Week 2 | Executed without assistance |
| **Team can troubleshoot common issues** | Week 4 | Resolved issue from logs without escalation |
| **Team can modify existing automation** | Week 6 | Changed template/config successfully |
| **Team can extend automation** | Week 10 | Added new feature (e.g., new device type) |
| **Team builds new automation** | Week 16 | Created automation using similar pattern |

#### Knowledge Retention Assessment

At 30, 60, 90 days post-handoff:

**Quick Survey:**

1. How confident are you running this automation? (1-5)
2. How confident troubleshooting issues? (1-5)
3. How confident making modifications? (1-5)
4. What additional training would be helpful?

**Goal:** Average 4+ on all questions by day 90

---

## 📊 Deliverable: Empowered Team

At the end of the Empower stage, your team has:

### 1. Knowledge Transfer Complete

- ✅ Architecture understanding
- ✅ Code walkthrough completed
- ✅ Operational procedures trained
- ✅ Modification/extension demonstrated

### 2. Comprehensive Documentation

- ✅ User guide (how to run)
- ✅ Technical reference (how it works)
- ✅ Runbook (how to troubleshoot)
- ✅ Modification guide (how to extend)

### 3. Self-Sufficiency

- ✅ Team operating automation independently
- ✅ Troubleshooting issues without escalation
- ✅ Making modifications confidently
- ✅ Building new automations using established patterns

---

## 💡 Why Empower Matters

### Sustainability

Without empowerment:

- ❌ Vendor lock-in (can't change code without consultant)
- ❌ Fragility (breaks when engineer leaves)
- ❌ Stagnation (automation doesn't evolve with needs)

With empowerment:

- ✅ Team autonomy (independent capability)
- ✅ Resilience (knowledge distributed across team)
- ✅ Evolution (automation grows with the organisation)

### ROI Multiplication

Empowered teams:

- **Build additional automations** using patterns learned (5x ROI)
- **optimise existing automations** continuously (ongoing value)
- **Respond faster to changes** (no waiting for external help)
- **Transfer knowledge** to new team members (sustainable)

---

## 🚀 Beyond PRIME: What's Next

After completing all five stages:

### Automation Capability Model

Capability is not the same as effort. This ladder describes what your automation can safely *do*, and what has to be true at each level for it to stay safe.

| Level | Capability | What must be in place |
| :--- | :--- | :--- |
| **0 — Manual** | Human execution throughout | Candidate tasks documented and standardised (you were here) |
| **1 — Assisted** | Reports, dashboards and utilities | Validation, named ownership, documentation |
| **2 — Automated** | Repeatable, defined workflows | Testing, logging, scoping, repeatability |
| **3 — Orchestrated** | Workflows spanning multiple systems | End-to-end assurance and audit evidence |
| **4 — AI-assisted** | Natural-language use of approved tools | Strong identity, tool allow-lists, evidence on every response |
| **5 — Governed autonomy** | Bounded automatic action | Explicit risk acceptance, rollback, kill controls, enhanced monitoring |

**Post-PRIME, you're at Level 2–3.**

Levels 4 and 5 are a governance problem before they are a technology problem. See [Governed AI for Network Operations](../foundation/governed-ai-network-operations/index.md) for what has to be true before an agent touches your estate.

---

### What Happens After Empower

PRIME ends when your team owns the automation. The automation does not end there — it runs for years, accumulates dependencies, and eventually should be switched off.

That is a separate discipline from delivery, and skipping it is how organisations end up with a portfolio nobody can inventory: scheduled jobs whose purpose is unclear, services whose owner has left, credentials belonging to scripts that stopped being useful two years ago.

The [Automation Service Lifecycle](../foundation/production-grade-network-automation-principles/automation-service-lifecycle.md) covers what to put in place: three named owners per service rather than "the automation team", decision gates before you build and after you ship, a minimum service record, and a retirement path.

If you adopt one thing from it, adopt the three owners. It takes an afternoon and it is what makes team ownership survive a resignation.

---

### Scaling Automation

**Next Automations:**

- Refer back to Pinpoint roadmap (#2, #3 priorities)
- Team can now implement independently or with advisory support
- Reuse patterns from first automation

**Building Automation Portfolio:**

- Consistent code standards (established)
- Shared libraries (extract common functions)
- Git repository organisation
- CI/CD for testing (advanced)

---

## 📋 Empower Checklist

Ensure knowledge transfer success:

- [ ] All knowledge transfer sessions completed
- [ ] Documentation reviewed and understood
- [ ] Team has run automation in lab independently
- [ ] Team has troubleshot simulated failure scenarios
- [ ] Team has made successful modification
- [ ] Support transition plan agreed
- [ ] Learning resources provided
- [ ] 30-day check-in scheduled
- [ ] Success metrics baseline captured

---

## 💼 Engagement Options

### Empower as Part of Full PRIME Engagement

Included as Stage 5 when you engage for the complete framework. Typically 2-4 weeks over 3 months (knowledge transfer sessions + ongoing support).

### Standalone Empowerment Service

For organisations with existing automation needing knowledge transfer:

**Fixed Fee:** £3,000 - £5,000 (depending on complexity)

**Includes:**

- 4 knowledge transfer sessions
- Complete documentation package
- 8 weeks of transition support
- 90-day success tracking

---

## 🎓 Learn More

- **[PRIME Framework Overview](./index.md)** — See how all five stages work together
- **[Previous Stage: Measure](./measure.md)** — Proving the value we've delivered
- **[Beginner Tutorials](../foundation/tutorials/beginner/index.md)** — Start building Python skills
- **[Services](../services.md)** — Explore engagement options
- **[Request Discovery Call](../contact.md)** — Discuss your automation needs

---

## 🎉 Congratulations

By completing the PRIME Framework—**Pinpoint, Re-engineer, Implement, Measure, Empower**—your organisation has:

✅ **Identified high-value automation opportunities** (Pinpoint)  
✅ **Designed optimised, scalable workflows** (Re-engineer)  
✅ **Built production-ready, maintainable automation** (Implement)  
✅ **Proven ROI and demonstrated value** (Measure)  
✅ **Built internal capability for sustained success** (Empower)

**You're now equipped to scale automation across your network operations.**

---

> **Mission:** To empower network engineers through the **[PRIME Framework](./index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](./philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.

---

[← Previous: Measure](./measure.md) | [Back to PRIME Framework](./index.md) | [View All Services →](../services.md)
