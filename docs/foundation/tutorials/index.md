---
title: Tutorials
description: Step-by-step tutorials for network automation with Python, organized by skill level from beginner to expert.
tags:
  - Tutorials
  - Python
  - Network Automation
  - Education
  - Hands-On
---

## Tutorials

## "Learn by Doing — Build Production Skills One Script at a Time"

Welcome to the **Nautomation Prime Tutorials**! This section is your hands-on laboratory for developing real-world network automation skills. Each tutorial provides complete, working code with line-by-line explanations so you understand *exactly* what every line does and why.

!!! warning "Python Prerequisite"
    This site focuses on applying Python to network automation. We assume familiarity with core Python concepts (variables, functions, loops, exceptions, and file I/O). If you're new to Python, complete a fundamentals course first, then return here.

---

## 📚 Tutorial Paths

Our tutorials are organized by skill level to match your Python experience:

### 🟢 [Beginner](./beginner/index.md)

Perfect if you're new to network automation or want to master the fundamentals.

- **Focus**: Core concepts, simple workflows, fundamental libraries
- **Prerequisites**: Basic Python knowledge (variables, functions, loops)
- **Topics**: Netmiko basics, TextFSM parsing, Excel exports, basic error handling

**Start Here**: [Send a Show Command and Export to Excel](./beginner/netmiko-show-command-to-excel.md)

---

### 🟡 [Intermediate](./intermediate/index.md)

Ready to handle more complex scenarios and multi-device operations.

- **Focus**: Multi-threading, advanced parsing, data aggregation, professional development practices
- **Prerequisites**: Comfortable with beginner concepts, understand functions and data structures
- **Topics**: Threading & concurrency, custom TextFSM templates, Jinja2 templating, structured logging, argparse CLIs, retry logic, code organisation

**New Production Patterns Available:**

- [Testing Automation Scripts](./intermediate/testing-network-automation.md)
- [Credential Management for Network Automation](./intermediate/credential-management-network-automation.md)
- [Error Recovery and Rollback](./intermediate/error-recovery-rollback-network-automation.md)
- [State Management and Idempotency](./intermediate/state-management-idempotency-network-automation.md)
- [Structured Logging for Network Automation](./intermediate/structured-logging-network-automation.md)
- [Health Checks and Pre-Flight Validation](./intermediate/health-checks-pre-flight-validation.md)

---

### 🔴 [Expert](./expert/index.md)

Production-grade automation with enterprise patterns and advanced techniques.

- **Focus**: Scalability, fault tolerance, security, enterprise framework integration
- **Prerequisites**: Strong Python skills, experience with intermediate tutorials
- **Topics**: **Nornir framework**, asyncio, NAPALM, PyATS, database integration, credential vaulting, API development, GitOps, CI/CD, containerization, observability

**New Production Patterns Available:**

- [Circuit Breakers and Backpressure](./expert/circuit-breakers-backpressure-network-automation.md)
- [Dependency Management and Task Orchestration](./expert/dependency-ordering-task-orchestration.md)
- [Incident Response Automation](./expert/incident-response-automation.md)

---

### ⚙️ [Production-Grade Network Automation Principles](../production-grade-network-automation-principles/index.md)

This track focuses on how to run automation safely in enterprise production environments.

- **Focus**: Risk reduction, validation strategy, failure handling, governance, and operational trust
- **Prerequisites**: Working knowledge of network automation and change control processes
- **Topics**: Identity validation, pre-flight enforcement, trust boundaries, drift handling, idempotency, blast radius control, safe failure, rollback strategy, workflow phase separation, operator-friendly output, audit evidence, secret hygiene, human approval gates, and deciding when not to automate

**Start Here**: [Production-Grade Network Automation Principles Index](../production-grade-network-automation-principles/index.md)

---

### 🤖 [Governed AI for Network Operations](../governed-ai-network-operations/index.md)

This track covers how to let AI help engineers operate a network without giving a language model an execution path to your infrastructure.

- **Focus**: Tool boundary design, AI risk classification, evidence requirements, and agent review
- **Prerequisites**: Familiarity with the production-grade principles above; a trusted source of truth
- **Topics**: The interpret-versus-execute boundary, why prompt instructions are not controls, narrow typed tools, AI-0 to AI-4 risk classes, refactoring existing scripts into governed tools, and a ten-question agent review checklist

**Start Here**: [Governed AI for Network Operations](../governed-ai-network-operations/index.md)

---

## 🎯 Tutorial Philosophy

Every tutorial follows these principles:

1. **Complete & Runnable** — All code is fully functional. No "TODO" sections or pseudocode.
2. **Line-by-Line Explanation** — We explain what each line does, not just the overall concept.
3. **Production-Aware** — Even beginner tutorials introduce best practices you'll use in production.
4. **Copy-Paste Friendly** — Code is formatted for easy copying and immediate use.

---

## 🚀 How to Use These Tutorials

1. **Choose Your Level** — Start with beginner if you're new to network automation
2. **Follow Along** — Type or paste the code into your own environment
3. **Experiment** — Modify the examples to work with your own network devices
4. **Build Up** — Each tutorial introduces concepts used in more advanced lessons

---

## 💡 Prerequisites

All tutorials assume you have:

- **Python 3.8+** installed
- **Basic Python knowledge** (variables, functions, loops, dictionaries)
- **Access to Cisco devices** (physical or virtual like CML, EVE-NG, or GNS3)
- **pip** for installing required libraries

---

!!! tip "Not Sure Where to Start?"
    If you're new to Python network automation, begin with our [Beginner Tutorial Index](./beginner/index.md) and work through the scripts in order. Each one builds on concepts from the previous tutorial.

---

## 📖 Related Resources

- **[Deep Dives](../deep-dives/index.md)** — In-depth technical analysis of production automation
- **[Scripts](../../scripts/index.md)** — Ready-to-deploy automation tools
- **[Getting Started](../../getting-started.md)** — New to Nautomation Prime? Start here

---

!!! tip "Need help applying this beyond the lab?"
  If you're moving from tutorials to governed production automation, review our [Enterprise Automation Services](../../services.md) or the [PRIME Framework](../../prime-framework/index.md).
