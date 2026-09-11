---
title: Implement
description: Stage 3 of the PRIME Framework - Building production-ready, maintainable automation guided by PRIME Philosophy principles.
tags:
  - PRIME Framework
  - Implement
  - Development
  - PRIME Philosophy
---

## Implement Solutions

## Stage 3 of the PRIME Framework

> **"Code is a liability, not an asset. The Implement stage focuses on building *just enough* automation—maintainable, documented, and built to last."**

!!! success "Stage Outcome"
    **Deliverable:** Production-ready Python scripts with line-by-line documentation, comprehensive error handling, and pre/post-flight validation.

    **Typical Result:** Hardened automation that runs reliably in production, with complete audit trails and the ability for your team to modify and extend it independently.

    ```mermaid
    graph LR
        A[🛠️ Setup] --> B[📝 Code]
        B --> C[✅ Test]
        C --> D[📦 Deploy]
        
        style A fill:#50C878
        style B fill:#60D388
        style C fill:#70DE98
        style D fill:#80E9A8
    ```

**Prime Terminology Used:** Prime Agents development, PRIME Philosophy principles, Prime Efficiency Stack

---

## 🎯 Objective

Transform designs from the [Re-engineer](./re-engineer.md) stage into production-ready automation that aligns with the [PRIME Philosophy](./philosophy.md).

---

## ⚙️ What Happens During Implement

### 1. Development Environment Setup

Before writing code, we establish consistent tooling:

#### Local Development Standards

**Python Environment:**

    ```text
    Python 3.9+ (avoid cutting edge, prefer stability)
    Virtual environment (venv or conda)
    requirements.txt with pinned versions
    ```

**Essential Libraries:**

    ```python
    netmiko==4.1.2      # SSH connections
    textfsm==1.1.3      # Output parsing
    jinja2==3.1.2       # Config templating
    pandas==2.0.3       # Data manipulation
    openpyxl==3.1.2     # Excel reporting
    pyyaml==6.0.1       # Config files
    python-dotenv==1.0.0 # Environment variables
    ```

**Code Quality Tools:**

    ```text
    black                # Code formatting
    pylint               # Linting
    pytest               # Testing
    ```

#### Source Control

All automation projects use Git from day one:

    ```text
    automation-project/
    ├── .gitignore       # Exclude credentials, outputs
    ├── README.md        # Project documentation
    ├── requirements.txt # Dependencies
    ├── config/          # YAML configs (NOT in git)
    ├── templates/       # Jinja2 templates
    ├── scripts/         # Python scripts
    ├── tests/           # Unit tests
    └── outputs/         # Generated reports (NOT in git)
    ```

---

### 2. Implementation Guided by PRIME Philosophy

Every line of code reflects our five core principles. Here are key implementation patterns:

!!! warning "Production Safety is Non-Negotiable"
    Most scripts fail in production because they were written for happy-path scenarios. We build every script assuming:

    - Connection timeouts will happen
    - Authentication will fail on some devices
    - Config tasks will raise exceptions
    - Partially-completed operations must be detected
    - Human visibility into failures is essential
    
    These aren't edge cases—they're baseline requirements.

#### 🔍 Principle 1: Transparency Over Obscurity

**What This Means in Practice:**

❌ **Avoid:** Over-engineering  

    ```python
    # DON'T: Abstract factory pattern for 2 device types
    class DeviceFactory:
        @staticmethod
        def create_device(device_type):
            if device_type == "cisco_ios":
                return CiscoIOSDevice()
            elif device_type == "cisco_nxos":
                return CiscoNXOSDevice()
    ```

✅ **Prefer:** Simple, direct solutions  

    ```python
    # DO: Simple conditional logic
    device_type = "cisco_ios" if "IOS" in version else "cisco_nxos"
    connection = ConnectHandler(device_type=device_type, **device)
    ```

**When to Choose Pragmatic:**

- You're solving a single use case (don't abstract prematurely)
- The "perfect" solution adds 40% complexity for 5% benefit
- The simpler approach will work for 12-24 months

**When to Add Complexity:**

- You're solving the same problem the 3rd time (DRY principle)
- Complexity reduction elsewhere outweighs local increase
- Scalability requirements are certain, not speculative

---

#### �️ Principle 2: Safety Over Speed

**What This Means in Practice:**

✅ **Verbose Logging:**

    ```python
    # Track progress for multi-device operations
    logger.info(f"Starting VLAN provisioning for {len(devices)} devices")

    for device in devices:
        logger.info(f"Connecting to {device['hostname']} ({device['ip']})")
        try:
            connection = ConnectHandler(**device)
            logger.info(f"✓ Connected to {device['hostname']}")
            
            output = connection.send_config_set(config_commands)
            logger.info(f"✓ Config applied to {device['hostname']}")
            
            # Validation
            verify = connection.send_command("show vlan brief")
            if new_vlan_id in verify:
                logger.info(f"✓ VLAN {new_vlan_id} verified on {device['hostname']}")
            else:
                logger.warning(f"✗ VLAN {new_vlan_id} NOT found on {device['hostname']}")
                
        except NetmikoTimeoutException:
            logger.error(f"✗ Timeout connecting to {device['hostname']}")
            failed_devices.append(device['hostname'])
        except NetmikoAuthenticationException:
            logger.error(f"✗ Authentication failed for {device['hostname']}")
            failed_devices.append(device['hostname'])

    logger.info(f"Completed: {len(devices) - len(failed_devices)}/{len(devices)} successful")
    ```

**Output Example:**

    ```text
    2024-01-15 10:30:22 INFO Starting VLAN provisioning for 12 devices
    2024-01-15 10:30:23 INFO Connecting to SW-ACCESS-01 (192.168.1.10)
    2024-01-15 10:30:24 INFO ✓ Connected to SW-ACCESS-01
    2024-01-15 10:30:26 INFO ✓ Config applied to SW-ACCESS-01
    2024-01-15 10:30:27 INFO ✓ VLAN 150 verified on SW-ACCESS-01
    2024-01-15 10:30:27 INFO Connecting to SW-ACCESS-02 (192.168.1.11)
    ...
    2024-01-15 10:31:45 INFO Completed: 11/12 successful
    ```

✅ **Human-Readable Output:**

    ```python
    # Generate Excel reports, not just terminal output
    df = pd.DataFrame(results)
    df.to_excel("vlan_provisioning_report.xlsx", index=False)

    # Include summary statistics
    summary = {
        "Total Devices": len(devices),
        "Successful": len(success_devices),
        "Failed": len(failed_devices),
        "Duration": f"{duration:.1f} seconds"
    }
    ```

---

#### � Principle 3: Empowerment Through Documentation

**What This Means in Practice:**

✅ **Validate Before Changing:**

    ```python
    # PRE-FLIGHT CHECKS
    def pre_flight_checks(device):
        """
        Verify device is safe to modify.
        Returns (bool, str): (is_safe, failure_reason)
        """
        # Check reachability
        if not ping_device(device['ip']):
            return False, "Device unreachable"
        
        # Verify no existing config session
        output = send_command("show configuration sessions")
        if "Session" in output:
            return False, "Active config session detected"
        
        # Check VLAN ID isn't already used
        vlans = send_command("show vlan brief")
        if new_vlan_id in parse_vlans(vlans):
            return False, f"VLAN {new_vlan_id} already exists"
        
        return True, "All checks passed"

    # Only proceed if safe
    is_safe, reason = pre_flight_checks(device)
    if not is_safe:
        logger.warning(f"Skipping {device['hostname']}: {reason}")
        continue
    ```

✅ **Verify After Changing:**

    ```python
    # POST-FLIGHT VALIDATION
    def verify_vlan_creation(connection, vlan_id, vlan_name):
        """
        Confirm VLAN was actually created.
        """
        output = connection.send_command("show vlan brief")
        
        if str(vlan_id) in output and vlan_name in output:
            return True
        else:
            # VLAN creation failed - trigger rollback
            logger.error(f"VLAN {vlan_id} not found after creation")
            rollback_vlan(connection, vlan_id)
            return False
    ```

✅ **Automatic Rollback:**

    ```python
    # CHECKPOINT BEFORE CHANGE
    checkpoint_name = f"before_vlan_{vlan_id}_{timestamp}"
    connection.send_command(f"archive config")

    try:
        # Apply change
        connection.send_config_set(config_commands)
        
        # Verify
        if not verify_vlan_creation(connection, vlan_id, vlan_name):
            raise ValidationError("VLAN verification failed")
            
    except Exception as e:
        logger.error(f"Change failed: {e}. Rolling back...")
        connection.send_command(f"configure replace flash:checkpoint")
        raise
    ```

---

### 3. Code Structure Standards

All implemented automation follows a consistent structure:

#### Main Script Template

    ```python
    #!/usr/bin/env python3
    """
    VLAN Provisioning Automation

    Description:
        Provisions VLANs across multiple access switches with validation.

    Usage:
        python provision_vlan.py --vlan 150 --name "Guest_WiFi"

    Author: Nautomation Prime
    Created: 2024-01-15
    """

    import logging
    from netmiko import ConnectHandler, NetmikoTimeoutException
    import pandas as pd
    from datetime import datetime

    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vlan_provisioning.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # ============================================================================
    # CORE FUNCTIONS
    # ============================================================================

    def load_device_inventory(csv_file):
        """Load device list from CSV file."""
        pass

    def pre_flight_checks(connection, vlan_id):
        """Validate device is safe to modify."""
        pass

    def apply_vlan_config(connection, vlan_id, vlan_name):
        """Apply VLAN configuration to device."""
        pass

    def verify_vlan_creation(connection, vlan_id):
        """Verify VLAN was successfully created."""
        pass

    def generate_report(results, output_file):
        """Create Excel report of provisioning results."""
        pass

    # ============================================================================
    # MAIN EXECUTION
    # ============================================================================

    def main():
        """Main automation workflow."""
        logger.info("=== VLAN Provisioning Started ===")
        
        # Load devices
        devices = load_device_inventory("inventory.csv")
        logger.info(f"Loaded {len(devices)} devices from inventory")
        
        # Results tracking
        results = []
        
        # Process each device
        for device in devices:
            result = process_device(device)
            results.append(result)
        
        # Generate report
        generate_report(results, "vlan_report.xlsx")
        
        logger.info("=== VLAN Provisioning Completed ===")

    if __name__ == "__main__":
        main()
    ```

---

### 4. Testing Strategy

All automation is tested before production deployment:

#### Lab Testing

**Requirements:**  
Minimum 3 lab devices matching production platforms

**Test Cases:**

- ✅ Normal operation (happy path)
- ✅ Device unreachable
- ✅ Invalid credentials
- ✅ Config rejected (syntax error)
- ✅ Partial failure (some devices succeed, others fail)
- ✅ Network interruption mid-execution

#### Staging Environment

For high-risk changes:

1. **Dry-run mode** — Validate without applying
2. **Pilot group** — 2-3 production devices, off-hours
3. **Phased rollout** — 25% → 50% → 100% over days

---

### 5. Documentation Standards

Every script includes:

#### README.md

    ```markdown
    # VLAN Provisioning Automation

    ## Purpose
    Provisions VLANs to access switches with pre-flight validation.

    ## Prerequisites

    - Python 3.9+
    - Network connectivity to devices
    - Credentials in `.env` file

    ## Installation
    ```bash
    pip install -r requirements.txt
    ```

## Usage

    ```bash
    python provision_vlan.py --vlan 150 --name "Guest_WiFi"
    ```

## Configuration

Edit `inventory.csv` with target devices.

## Troubleshooting

- **"Device unreachable"** — Verify ICMP/SSH connectivity
- **"Authentication failed"** — Check credentials in `.env`

### Inline Comments

Focus on **why**, not **what**:

    ```python
    # DON'T: State the obvious
    x = x + 1  # Increment x

    # DO: Explain the reasoning
    x = x + 1  # Account for 1-based VLAN IDs in UI vs 0-based array
    ```

---

## 📊 Deliverable: Production-Ready Automation

At the end of the Implement stage, you receive:

### 1. Tested Python Scripts

- Fully functional automation
- Error handling for all failure modes
- Logging throughout execution
- Command-line arguments or config files

### 2. Supporting Files

- **requirements.txt** — Pinned dependencies
- **inventory.csv** — Device list template
- **config_templates/** — Jinja2 templates
- **.env.example** — Environment variable template

### 3. Documentation

- **README.md** — Installation, usage, troubleshooting
- **CHANGELOG.md** — Version history
- **Inline comments** — Explaining complex logic

### 4. Test Results

- Lab test report
- Pilot deployment summary (if applicable)
- Known limitations documented

---

## 💡 Why Implement with PRIME Philosophy Matters

### Long-Term Maintainability

Code written with Pragmatic/Transparent/Reliable principles:

- **6 months later:** You (or teammate) can understand and modify
- **12 months later:** Still works without updates (stable dependencies)
- **24 months later:** Easy to extend for new use cases

### Operational Confidence

When automation runs in production:

- **Transparency:** Logs show exactly what happened
- **Reliability:** Pre/post-flight checks catch issues early
- **Pragmatic:** Simple code means faster troubleshooting

---

## 🚀 What Happens Next

After implementation, proceed to [Stage 4: Measure](./measure.md) to track performance and ROI.

---

## 📋 Implement Checklist

Before deploying to production:

- [ ] Code follows PRIME Philosophy principles
- [ ] All error conditions handled gracefully
- [ ] Logging provides visibility into execution
- [ ] Pre-flight and post-flight validation implemented
- [ ] Rollback mechanism tested
- [ ] Lab testing completed for all scenarios
- [ ] Documentation complete (README + inline comments)
- [ ] Credentials secured (not hardcoded)
- [ ] Pilot deployment successful (if high-risk)
- [ ] Handoff training scheduled (if external development)

---

## 💼 Engagement Options

### Implementation as Part of Full PRIME Engagement

Included as Stage 3 when you engage for the complete framework. Typically 2-6 weeks per automation (depending on complexity from Re-engineer phase).

### Standalone Implementation Service

For organisations with designs but need development help:

**Pricing:** £120-£150/hour or fixed-fee based on Re-engineer specs

**Includes:**

- Production-ready Python scripts
- Comprehensive testing
- Full documentation
- Knowledge transfer session

---

## 🎓 Learn More

- **[PRIME Framework Overview](./index.md)** — See how all five stages work together
- **[Previous Stage: Re-engineer](./re-engineer.md)** — Design blueprints implemented here
- **[Next Stage: Measure](./measure.md)** — Tracking performance and ROI
- **[View Tutorials](../foundation/tutorials/index.md)** — Learn implementation techniques
- **[Request Discovery Call](../contact.md)** — Discuss your automation needs

---

> **Mission:** To empower network engineers through the **[PRIME Framework](./index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](./philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.

---

[← Previous: Re-engineer](./re-engineer.md) | [Back to PRIME Framework](./index.md) | [Next: Measure →](./measure.md)
