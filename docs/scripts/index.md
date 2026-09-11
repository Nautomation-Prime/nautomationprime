---
title: Script Library
description: Premium, production-ready Python automation tools for Cisco infrastructure. Buy them ready-to-run or have them customised to your environment.
tags:
  - Scripts
  - Tools
  - Premium Tools
  - Production Ready
---

## Script Library

### Production-Ready Automation for Cisco Infrastructure

Welcome to the **Nautomation Prime Script Library**. Here you'll find production-grade, hardened Python automation tools designed for enterprise Cisco deployments.

!!! abstract "Premium tools — available on request"
    These tools are premium Nautomation Prime products, not free downloads. Each one can be **bought as-is (unmodified)** for a one-time licence, or **customised to your estate** as a focused bespoke engagement. Indicative prices are shown per tool below — [request a tool or a quote](../contact.md) to get started.

!!! warning "Python Prerequisite"
    This site focuses on applying Python to network automation. We assume familiarity with core Python concepts (variables, functions, loops, exceptions, and file I/O). If you're new to Python, complete a fundamentals course first, then return here.

---

## 📚 Available Scripts

### CDP Network Audit Tool

**Status:** 💼 Premium — available on request
**Description:** A threaded discovery utility that starts from seed Cisco devices and crawls the network using Cisco Discovery Protocol (CDP), producing structured Excel reports with professional formatting.

**Features:**

- Parallel discovery with configurable worker pool (via config.py or environment variable overrides)
- Centralised configuration with comprehensive config.py (200+ documented settings)
- Two-tier authentication (primary user with customisable fallback username)
- Jump server / bastion support (Paramiko channel + Netmiko sock)
- DNS enrichment for discovered hostnames
- Excel reporting from pre-formatted templates with multiple sheets
- Hybrid logging with optional logging.conf
- Up to 3 automatic retries for transient connectivity issues
- Comprehensive error tracking (authentication failures, connection errors)
- Extensive customisation options (credentials, paths, Excel formatting, DNS, logging, and more)

**Pricing:** £795 as-is (unmodified) · £2,000–£5,000 customised

[📖 View Deep Dive Documentation](../foundation/deep-dives/cdp-audit.md) | [💬 Request this tool](../contact.md)

---

### Access Switch Port Audit Tool

**Status:** 💼 Premium — available on request
**Description:** A production-hardened collector designed to map interface health and utilisation across your access layer.

**Features:**

- Parallel device SSH connections for high-speed audits
- Conservative "Stale Port" detection logic using PoE, neighbours, and input timers
- Multi-source port classification (Access vs. Trunk vs. Routed)
- Professional Excel workbooks with automated conditional formatting
- Full Jump-Host (Bastion) integration for restricted environments

**Pricing:** £795 as-is (unmodified) · £2,000–£5,000 customised

[📖 View Deep Dive Documentation](../foundation/deep-dives/access-switch-audit.md) | [💬 Request this tool](../contact.md)

---

### Cisco IOS-XE Compliance Audit

**Status:** 💼 Premium — available on request
**Description:** A policy-driven compliance auditor with 90+ role-aware checks, automated remediation generation, and multi-format reporting for enterprise Cisco switches.

**Features:**

- Split YAML config directories plus separate inventory for reusable policy
- Role-aware port classification (uplink, downlink, access, routed, unused)
- 90+ toggleable checks across management, control, and data planes
- Multi-format reporting (HTML dashboards, JSON, CSV, remediation scripts)
- Severity/tag filtering with a governed remediation lifecycle
- Interactive operator modes with approval-governed change execution
- Jump host / bastion support for restricted environments
- Concurrent device auditing for large-scale operations

**Pricing:** £1,495 as-is (unmodified) · £3,500–£8,000 customised

[📖 View Deep Dive Documentation](../foundation/deep-dives/cisco-compliance-audit.md) | [💬 Request this tool](../contact.md)

---

### Cisco Config Generator

**Status:** 💼 Premium — available on request  
**Description:** Turns structured Excel intent into per-device Cisco IOS-XE configuration files using a reusable Python core and Jinja2 templates, with a validation-first workflow and a pack architecture that keeps customer rules in data and templates rather than hardcoded logic.

**Features:**

- Intent modelling via a structured Excel workbook
- Validation-first processing before any rendering
- Template-driven Jinja2 rendering with a reusable core engine
- Pack architecture that separates policy-as-data from logic
- Dual execution modes (interactive TUI and headless CLI)
- Deterministic per-device Cisco IOS-XE configuration output

**Pricing:** £595 as-is (unmodified) · £1,500–£4,000 customised

[📖 View Deep Dive Documentation](../foundation/deep-dives/cisco-config-generator.md) | [💬 Request this tool](../contact.md)

---

## 🧭 Learning Paths

**Unsure where to start?** These learning paths connect scripts to tutorials and deep dives based on your experience level:

### 📖 Beginner Path

Start here if you're new to network automation:

1. Learn Python fundamentals (external resources)
2. Read [Multi-Device Show Command Collection](../foundation/tutorials/beginner/multi-device-show-command.md) — learn Netmiko basics
3. Try [Configuration Backup Tutorial](../foundation/tutorials/beginner/multi-device-config-backup.md) — understand backup patterns
4. Explore [CDP Network Audit Deep Dive](../foundation/deep-dives/cdp-audit.md) — see how threading and configuration work at scale

### 🛠️ Intermediate Path

Ready to understand production patterns:

1. Read [Nornir Fundamentals](../foundation/tutorials/intermediate/nornir-fundamentals.md) — multi-device automation framework
2. Read [Enterprise Config Backup with Nornir](../foundation/tutorials/intermediate/enterprise-config-backup-nornir.md) — scalable patterns
3. Study [Access Switch Audit Deep Dive](../foundation/deep-dives/access-switch-audit.md) — parallel collection and intelligent parsing
4. Study [CDP Network Audit Deep Dive](../foundation/deep-dives/cdp-audit.md) — threading, configuration, and jump hosts

### 🚀 Advanced Path

Ready to build custom solutions:

1. Review all [Deep Dives](../foundation/deep-dives/index.md) for architectural patterns
2. Study [Cisco Compliance Audit Deep Dive](../foundation/deep-dives/cisco-compliance-audit.md) — policy-driven compliance with remediation generation
3. Purchase a tool and customise it for your environment (licensed source included)
4. Integrate with [PRIME Framework](../prime-framework/index.md) methodology
5. Contact us for [consulting services](../services.md) on bespoke automation

---

## 🔄 Coming Soon

### Zero Touch Provisioning (ZTP) Tool

**Status:** 🚧 In Development  
**Description:** Automated deployment solution for Cisco devices that streamlines initial configuration and reduces deployment time from hours to minutes.

**Planned Features:**

- Automated device configuration from templates
- DHCP option integration for network-based provisioning
- Email notifications for deployment status and errors
- HTTP server integration for configuration and log file management
- Pre-flight validation and rollback capabilities
- Multi-device orchestration with dependency management
- Comprehensive logging with remote log collection

**Current Status:** Core functionality tested and validated. Additional features (email notifications, HTTP log server integration) under active development.

---

### IOS-XE Software Upgrade Orchestrator

**Status:** 🚧 In Development  
**Description:** Automated, intelligent firmware management for Cisco IOS-XE switch stacks that eliminates manual upgrade errors and reduces downtime through comprehensive pre-flight validation.

**Planned Features:**

- Pre-flight validation (disk space, compatibility, current version checks)
- Binary integrity verification (MD5/SHA checksums)
- Automated file transfer to target devices (SCP/TFTP/HTTP)
- Stack-aware upgrade orchestration with rolling restarts
- Version compliance reporting across the estate
- Rollback capability for failed upgrades
- Parallel upgrade support for multiple stacks
- Email notifications and comprehensive logging
- Integration with maintenance windows and change control systems

**Current Status:** Architecture and design phase. Feature set being finalised based on enterprise deployment requirements.

---

## 🛠️ Getting Started with Scripts

### Prerequisites

- Python 3.8+
- Netmiko or equivalent SSH library
- Network access to target devices
- Appropriate credentials/permissions

### Installation & Setup

Each tool is delivered as a licensed package with a setup runbook. Typical workflow once you have the package:

```bash
# Unpack the licensed tool package
cd <tool-name>

# Install dependencies
pip install -r requirements.txt

# Run with --help to see options
python main.py --help
```

### Credential Management

Scripts use your operating system's native credential manager for secure authentication:

- **Windows:** CDP Network Audit prompts you to save credentials to Windows Credential Manager on first run. Enter your username and password when prompted, and the script will store them securely. Future runs use the stored credentials automatically.  
- **macOS:** Credentials are stored in Keychain - Upcoming  
- **Linux:** Credentials are stored in `pass` or similar managers - Upcoming  

Credentials are never stored in plaintext files or hardcoded in scripts.

See the setup runbook included with each tool for platform-specific instructions.

### Configuration

All scripts follow the **Nautomation Prime** philosophy of transparency and security:

- Credentials are stored in OS credential managers (Windows Credential Manager, etc.)
- Configuration files are well-documented with inline comments.  
- Pre-flight validation checks prevent unsafe deployments.  

### Support & Questions

For issues, feature requests, or questions about any script:  

- Check the **Deep Dives** documentation for detailed explanations.  
- [Request a tool, a quote, or post-purchase support](../contact.md) for licensing and customisation.  
- Contact us via [email](mailto:enquiries@nautomationprime.io) or [LinkedIn](https://www.linkedin.com/company/nautomationprime) for consulting services.  

---

!!! success "Need one of these patterns tailored to your environment?"
  If you want these scripts adapted, extended, or rolled out across a live estate, review our [Enterprise Automation Services](../services.md), the [PRIME Framework](../prime-framework/index.md), or [request a Discovery Call](mailto:enquiries@nautomationprime.io).

---

## Resources by Topic

**Quick access to find what you need:**

| Topic | Resources |
| :--- | :--- |
| **Network Discovery** | [📖 CDP Network Audit Deep Dive](../foundation/deep-dives/cdp-audit.md) • [💬 Request the tool](../contact.md) |
| **Port & Interface Health** | [📖 Access Switch Audit Deep Dive](../foundation/deep-dives/access-switch-audit.md) • [💬 Request the tool](../contact.md) |
| **Compliance & Governance** | [📖 Cisco Compliance Audit Deep Dive](../foundation/deep-dives/cisco-compliance-audit.md) • [💬 Request the tool](../contact.md) |
| **Configuration Management** | [🎓 Configuration Backup (Beginner)](../foundation/tutorials/beginner/multi-device-config-backup.md) • [🎓 Enterprise Backup with Nornir (Intermediate)](../foundation/tutorials/intermediate/enterprise-config-backup-nornir.md) |
| **Data Collection & Reporting** | [🎓 Show Commands to Excel (Beginner)](../foundation/tutorials/beginner/netmiko-show-command-to-excel.md) • [🎓 Multi-Device Collection (Beginner)](../foundation/tutorials/beginner/multi-device-show-command.md) |
| **Automation Frameworks** | [🎓 Nornir Fundamentals](../foundation/tutorials/intermediate/nornir-fundamentals.md) • [📖 Advanced Patterns](../foundation/tutorials/intermediate/advanced-nornir-patterns.md) |
| **Automation Methodology** | [🚀 PRIME Framework](../prime-framework/index.md) • [ℹ️ Philosophy & Approach](../prime-framework/philosophy.md) |

---

## The "Prime" Philosophy

All scripts in this library adhere to three core principles:

1. **Line-by-Line Transparency** - Every function is documented, every decision explained  
2. **Hardened for Production** - Robust error handling, security best practices, pre-flight checks  
3. **Vendor-Neutral** - Built on industry-standard libraries like Netmiko, Nornir, and TextFSM  

> **Mission:** To empower network engineers through the **[PRIME Framework](../prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](../prime-framework/philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.
