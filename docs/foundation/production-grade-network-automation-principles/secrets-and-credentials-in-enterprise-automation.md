---
title: Secrets and Credentials in Enterprise Automation
description: Handle credentials safely with vault integration, environment isolation, rotation controls, and least-privilege access.
tags:
  - Production Principles
  - Security
  - Secrets Management
  - Credentials
  - Network Automation
---

## Why Secret Hygiene Is Critical

Automation amplifies both good and bad practices. Poor secret handling can turn one mistake into organisation-wide compromise.

High-risk patterns include:

- Credentials embedded in code or YAML
- Shared admin credentials across environments
- Long-lived tokens with broad scope
- Logging secrets in exceptions or debug output

---

## Core Secret Management Principles

- Never store raw secrets in source control
- Use least-privilege accounts per workflow function
- Separate credentials by environment (dev, test, prod)
- Rotate secrets on schedule and after incidents
- Use short-lived credentials where possible

---

## Runtime Retrieval Pattern

Preferred flow:

1. Workflow authenticates to vault using workload identity
2. Retrieves scoped credential just-in-time
3. Uses credential in memory only
4. Clears sensitive objects after use
5. Emits redacted logs and metadata

Avoid writing secrets to local temp files or artifacts.

---

## Access Model

Strong enterprise model:

- Distinct read-only and write credentials
- Role-based secret paths
- Approval for privileged secret access
- Alerting on unusual retrieval patterns

Credential strategy should align with blast-radius controls.

---

## Production Checklist

- No secrets in code, templates, or inventory files
- Vault integration is used for runtime retrieval
- Environment boundaries are strictly enforced
- Secret rotation is automated and audited
- Logging policy guarantees redaction of sensitive values

---

## Anti-Patterns

- "Temporary" passwords committed to private repos
- Single shared credential for all devices and environments
- Hardcoded fallbacks when vault is unavailable
- Debug logging with full connection objects

---

## Key Takeaway

Secret management is not a security add-on. It is a foundational reliability and trust requirement for enterprise automation.
---

## Continue the Series

- Series Index: [Production-Grade Network Automation Principles](./index.md)
- Previous: [Part 11 - Building Audit-Ready Automation](./building-audit-ready-automation.md)
- Next: [Part 13 - Human-in-the-Loop Automation Design](./human-in-the-loop-automation-design.md)
