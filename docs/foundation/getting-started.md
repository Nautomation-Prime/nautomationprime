---
title: Getting Started
description: Learn what Nautomation Prime offers and find the right path for your network automation journey. Quick start guide for deep dives, scripts, and services.
tags:
  - Getting Started
  - Guide
  - Tutorial
  - Onboarding
---

Welcome! This guide will help you understand what Nautomation Prime offers and how to get started.

---

## What is Nautomation Prime?

**Nautomation Prime** bridges the gap between complex Cisco infrastructure and streamlined Python-driven automation. We provide:

- **[Tutorials](tutorials/index.md)** — Step-by-step practical guides for learning automation skills
- **[Deep Dives](deep-dives/index.md)** — Production-ready scripts explained line-by-line
- **[Script Library](../scripts/index.md)** — Premium automation tools for common tasks
- **[PRIME Framework Services](../prime-framework/index.md)** — Proven five-stage methodology for automation projects
- **[Professional Services](../services.md)** — Custom automation tailored to your topology

!!! warning "Important"
    This site does **not contain Python tutorials.** We assume you already know Python basics (variables, functions, loops, exceptions, file I/O). Our goal is to teach you how to apply Python to network automation and provide a foundation you can transfer into your own scripts or learning journey.

---

## 🚀 Quick Start Paths

### I want to learn network automation

Start with our **[Tutorials](tutorials/index.md)**. We provide hands-on, step-by-step guides for beginner, intermediate, and expert levels.

**Recommended Learning Path:**

1. **[Beginner Tutorials](tutorials/beginner/index.md)** — Your first Netmiko scripts
   - [Show Command to Excel](tutorials/beginner/netmiko-show-command-to-excel.md) — Start here
   - [Multi-Device Automation](tutorials/beginner/multi-device-show-command.md) — Scale to multiple devices

2. **[Intermediate Topics](tutorials/intermediate/index.md)** — Configuration management, validation, templating

3. **[Expert Topics](tutorials/expert/index.md)** — Nornir, AsyncIO, advanced patterns

4. **[Deep Dives](deep-dives/index.md)** — Production-grade code walkthroughs
   - [CDP Network Audit](deep-dives/cdp-audit.md) — Threading, security, enterprise design

### I want to use pre-built scripts

Check out our **[Script Library](../scripts/index.md)**. Each tool comes with full documentation and a setup runbook, and can be purchased as-is or customised to your environment.

**Popular Scripts:**

- [CDP Network Audit Tool](../scripts/index.md) — Discover your Cisco topology with line-by-line transparency
- [Access Switch Audit](deep-dives/access-switch-audit.md) — Port health and compliance checking

### I need custom automation for my environment (Services)

We deliver automation projects through the **[PRIME Framework](../prime-framework/index.md)**—a proven five-stage methodology:

**[Pinpoint](../prime-framework/pinpoint.md)** → **[Re-engineer](../prime-framework/re-engineer.md)** → **[Implement](../prime-framework/implement.md)** → **[Measure](../prime-framework/measure.md)** → **[Empower](../prime-framework/empower.md)**

**Services include:**

- Full PRIME Framework engagements (discovery to team capability)
- Individual stages (à la carte services)
- Custom Python automation (VLAN provisioning, fleet upgrades, ISE integration)
- Optional code-signing and software integrity controls for delivered Python automation
- Deployment options (standard scripts, portable bundles, Docker containers)

**[View Services](../services.md)** | **[Code-Signing Service](../services.md#code-signing-software-integrity-new)** | **[Request Discovery Call](../contact.md)**

---

## 📋 Prerequisites

**Python Knowledge (Important!):**

- **This site assumes you already know Python.** We teach you how to apply Python to network automation, not how to learn Python itself.
- If you're new to Python, we recommend completing a Python fundamentals course first (Codecademy, Real Python, W3Schools, or similar).
- You should understand: variables, functions, loops, conditionals, exceptions, and basic file I/O.
- Our code is written for clarity (not brevity), so intermediate Python developers will follow along easily.

**Technical Requirements:**

- **Python 3.8+** (or use our [portable bundles](../services.md#zero-install-portable-bundles) if Python isn't available)
- **Network access** to your Cisco devices
- **Credentials** for device authentication
- **SSH enabled** on target Cisco devices

---

## Our Engineering Philosophy

!!! tip "The Foundation Behind Everything We Build"
    Every tool, script, and service at Nautomation Prime is guided by the **[PRIME Philosophy](../prime-framework/philosophy.md)**—five core principles that ensure transparency, measurability, ownership, safety, and empowerment.

    These values define **how** we build (pragmatic, transparent, reliable), while the **[PRIME Framework](../prime-framework/index.md)** defines **what** we deliver (structured methodology).
    
    **[Read the complete PRIME Philosophy →](../prime-framework/philosophy.md)**

---

## 🛠️ Common Tasks

### Get the CDP Network Audit Tool

1. Read the [Deep Dive guide](deep-dives/cdp-audit.md) to see exactly how it works
2. [Request the tool](../contact.md) — buy it as-is or have it customised to your estate
3. Receive the licensed package and setup runbook on purchase

### Request Custom Automation (PRIME Framework)

For structured automation projects with proven ROI:

1. **[Request Discovery Call](../contact.md)**—free 30-60 minute discussion
2. Receive [Pinpoint stage](../prime-framework/pinpoint.md) roadmap with ROI calculations
3. Choose full [PRIME Framework](../prime-framework/index.md) or individual stages (à la carte)
4. Deliverables: Production code, documentation, ROI metrics, team capability

**[Learn about PRIME Framework](../prime-framework/index.md)** | **[View Services](../services.md)**

### Request Bespoke Automation

For custom automation tailored to your specific topology:

1. Review available [services and deployment options](../services.md)
2. Contact us via [email](mailto:enquiries@nautomationprime.io) or [LinkedIn](https://www.linkedin.com/company/nautomationprime)
3. Describe your requirements and any constraints (e.g., restricted environments, specific platforms)
4. Receive a detailed proposal and timeline

### Use Portable Bundles (No Python Installation)

1. Request a custom bundle through our [services page](../services.md#zero-install-portable-bundles)
2. Download the bundle to your workstation or USB drive
3. Extract and run directly—no installation needed
4. Full source code is included for auditing

---

!!! success "Want this implemented in your environment?"
    If you already know which workflow needs attention, move from learning into delivery with our [Enterprise Automation Services](../services.md), the [PRIME Framework](../prime-framework/index.md), or a [Discovery Call](mailto:enquiries@nautomationprime.io).

---

## ❓ Frequently Asked Questions

??? question "Do I need Python installed to use Nautomation Prime tools?"

    Not necessarily! We offer [portable bundles](../services.md#zero-install-portable-bundles) that run without Python installation. These are ideal for restricted enterprise environments where Python may not be permitted. However, if you want to modify or extend our scripts, you'll need Python 3.8 or higher.

??? question "What's the difference between tutorials, deep dives, and services?"

    **[Tutorials](tutorials/index.md)** teach you to build automation yourself with step-by-step guides. **[Deep Dives](deep-dives/index.md)** explain production-grade scripts line-by-line so you understand how they work. **[Services](../services.md)** deliver complete automation projects through the **[PRIME Framework](../prime-framework/index.md)** with ROI proof and team empowerment.

??? question "Can you automate my specific network topology?"

    Absolutely! Our bespoke services cover custom scripting for any topology. Contact us via [email](mailto:enquiries@nautomationprime.io) or [LinkedIn](https://www.linkedin.com/company/nautomationprime) to discuss your specific requirements.

??? question "Are these tools vendor-locked to Cisco?"

    Our tools are built on vendor-neutral libraries like **Netmiko**, **Nornir**, and **NAPALM**. While designed for Cisco, the patterns and concepts apply across other vendors (Juniper, Arista, Palo Alto, etc.). Your skills remain portable across platforms.

??? question "How do I secure my credentials?"

    We leverage native OS credential managers (Windows Credential Manager, Keychain on macOS, pass on Linux). Passwords are never stored in plaintext files or hardcoded in scripts. When you run a script like CDP Network Audit for the first time, it will prompt you to save your credentials to Windows Credential Manager—just enter your username and password, and the script will store them securely. Future runs will use the stored credentials automatically.

??? question "What if I don't have Python experience?"

    This site assumes you already know Python basics (variables, functions, loops, exceptions). If you're new to Python, we recommend completing a Python fundamentals course first (Codecademy, Real Python, or similar), then return to apply those skills to network automation. Our code is written for clarity, so even beginners with solid fundamentals will be able to follow along.

??? question "Do your scripts work in production environments?"

    Yes! All our scripts are production-grade with robust error handling, pre-flight safety checks, thread-safe concurrent operations, and comprehensive logging. We follow the [PRIME Philosophy](../prime-framework/philosophy.md) principles—transparency, measurability, ownership, safety, and empowerment. Many organisations use our scripts in live production environments.

??? question "What network devices do your scripts support?"

    Our scripts primarily target Cisco devices (IOS, IOS-XE, NX-OS, IOS-XR) but the underlying libraries (Netmiko, Nornir, NAPALM) support many vendors including Juniper, Arista, Palo Alto Networks, F5, and more. The patterns and techniques we teach are transferable across vendors.

??? question "Can I customise the tools for my own environment?"

    Yes. Each tool can be bought as-is or customised to your environment, and is delivered with licensed source so your team can audit, learn from, and adapt it. [Request a tool or a quote](../contact.md) to discuss licensing and customisation.

??? question "What's included in the PRIME Framework?"

    The [PRIME Framework](../prime-framework/index.md) is our proven five-stage methodology: **Pinpoint** (identify opportunities), **Re-engineer** (design solutions), **Implement** (build automation), **Measure** (prove ROI), and **Empower** (transfer knowledge). Each stage delivers specific outcomes with measurable value. You can engage for the full framework or individual stages à la carte.

---

## Ready to Get Started?

Whether you're learning automation, deploying tools, or need bespoke services—we're here to help.

### For Custom Automation & Services

**[Book a Discovery Call](../contact.md)** (Free, 30-60 minutes)

No obligation. We'll discuss your goals, timeline, and answer any questions about the PRIME Framework.

### For Questions or Discussions

- **Email:** [enquiries@nautomationprime.io](mailto:enquiries@nautomationprime.io)
- **LinkedIn:** [Nautomation Prime](https://www.linkedin.com/company/nautomationprime)

---

- **Learn Network Automation:** Start with [Tutorials](tutorials/index.md) or study [Deep Dives](deep-dives/index.md)
- **Deploy Tools:** Browse the [Script Library](../scripts/index.md)
- **Professional Services:** Explore [PRIME Framework](../prime-framework/index.md) for structured automation delivery
- **Custom Solutions:** View [Services](../services.md) for bespoke automation options
- **Connect:** Contact us via [email](mailto:enquiries@nautomationprime.io) or [LinkedIn](https://www.linkedin.com/company/nautomationprime)

---

> **Mission:** To empower network engineers through the **[PRIME Framework](../prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](../prime-framework/philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.
