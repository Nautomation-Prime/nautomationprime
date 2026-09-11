---
title: Error Recovery & Rollback Patterns
description: Safe network changes with automated rollback. Capture pre-state, validate post-state, and automatically undo failures. Production-grade deployment patterns.
tags:
  - Error Recovery
  - Rollback
  - Safety
  - Network Automation
  - Intermediate
  - Reliability
  - Design Patterns
---

## Why Rollback Matters

You're deploying a critical configuration change to 50 devices. On device 45, the change causes an unexpected failure.

**Two scenarios:**

**Scenario A (No Rollback):**

- Devices 1-44: Changed successfully
- Device 45: Failed (now in broken state)
- Devices 46-50: Partially changed (inconsistent)
- Result: **Entire network is broken, manual recovery required**

**Scenario B (With Rollback):**

- Devices 1-44: Changed successfully
- Device 45: Change detected as bad → **Automatically reverts**
- Devices 46-50: Never attempted (deployment stopped early)
- Result: **Partial success visible, easy to retry**

**Rollback transforms catastrophic failure into controlled, reversible change.**

---

## The Business Case: Safe Deployment

### The Cost of Uncontrolled Changes

```text
Without Rollback:
✓ Change starts
✓ Device 1: Success
✓ Device 2: Success
...
✓ Device 44: Success
✗ Device 45: FAILURE (now in unknown state)
✗ Device 46-50: Partially changed (inconsistent)
→ Manual remediation (2-4 hours)
→ Customer SLA breach ($$$)
→ Lost trust in automation
```

### With Automated Rollback

```text
With Rollback:
✓ Capture pre-state
✓ Change starts
✓ Device 1-44: Success
✓ Validate device 45 post-state
✗ Post-state invalid
→ Rollback device 45 automatically
→ Stop deployment loop
✓ Manual inspection
→ Fix root cause
→ Retry (now succeeds)
```

---

## Architecture: Rollback Strategy

```text
Step 1: Capture Pre-State
┌────────────────────┐
│ Device             │
│ Config: VLAN 100   │
│ Routes: 10 BGP     │
└────────────────────┘
       ↓
Step 2: Make Change
┌────────────────────┐
│ Device             │
│ Config: VLAN 100,  │
│          101, 102  │
│ Routes: 12 BGP     │
└────────────────────┘
       ↓
Step 3: Validate Post-State
┌─────────────────────────────┐
│ Expected: VLAN 100, 101, 102 │
│ Actual:   VLAN 100, 101, 102 │
│ → PASS ✓                     │
└─────────────────────────────┘
       ↓
Step 4: If Validation Fails
┌────────────────────┐
│ Expected: VLAN ... │
│ Actual: VLAN...    │
│ → FAIL ✗           │
└────────────────────┘
       ↓
Step 4b: Rollback to Pre-State
┌────────────────────┐
│ Device config:     │
│ → Restore from     │
│   pre-state backup │
│ → Verify success   │
└────────────────────┘
```

---

## Pattern 1: State Capture & Comparison

### The Implementation

```python
# src/state_management.py
import json
from datetime import datetime, timezone
from netmiko import ConnectHandler
from pathlib import Path

class DeviceStateManager:
    """Capture and compare device states."""
    
    def __init__(self, device):
        """
        Initialize with a connected device.
        
        Args:
            device: Netmiko ConnectHandler instance
        """
        self.device = device
        self.state_history = {}
    
    def capture_state(self, state_name="current", commands=None):
        """
        Capture current device configuration state.
        
        Args:
            state_name: Label for this state (e.g., "pre_change", "post_change")
            commands: List of commands to run (default: common show commands)
        
        Returns:
            dict: Device state snapshot
        """
        if commands is None:
            commands = [
                "show ip route summary",
                "show ip interface brief",
                "show running-config | include vlan",
                "show ip bgp summary",
            ]
        
        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device": self.device.host,
            "outputs": {}
        }
        
        for command in commands:
            try:
                output = self.device.send_command(command)
                state["outputs"][command] = output
            except Exception as e:
                state["outputs"][command] = f"ERROR: {str(e)}"
        
        # Store in history
        self.state_history[state_name] = state
        
        return state
    
    def compare_states(self, state1_name, state2_name):
        """
        Compare two captured states.
        
        Args:
            state1_name: Name of first state (e.g., "pre_change")
            state2_name: Name of second state (e.g., "post_change")
        
        Returns:
            dict: Differences between states
        """
        state1 = self.state_history.get(state1_name)
        state2 = self.state_history.get(state2_name)
        
        if not state1 or not state2:
            raise ValueError("Both states must be captured first")
        
        differences = {
            "state1": state1_name,
            "state2": state2_name,
            "changes": {}
        }
        
        # Compare command outputs
        for command in state1["outputs"]:
            output1 = state1["outputs"].get(command, "")
            output2 = state2["outputs"].get(command, "")
            
            if output1 != output2:
                differences["changes"][command] = {
                    "before": output1[:200] + "..." if len(output1) > 200 else output1,
                    "after": output2[:200] + "..." if len(output2) > 200 else output2,
                }
        
        return differences
    
    def save_state_to_file(self, state_name, filename):
        """
        Save state snapshot to file for recovery.
        
        Args:
            state_name: Name of state to save
            filename: File path
        """
        state = self.state_history.get(state_name)
        if not state:
            raise ValueError(f"State '{state_name}' not found")
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"✓ State saved to {filename}")
    
    def load_state_from_file(self, filename):
        """Load previously saved state."""
        with open(filename, 'r') as f:
            state = json.load(f)
        
        self.state_history["loaded"] = state
        return state
```

### Usage Example

```python
from netmiko import ConnectHandler
from state_management import DeviceStateManager

# Connect to device
device = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    password="password"
)

# Initialize state manager
state_mgr = DeviceStateManager(device)

# Step 1: Capture pre-change state
print("Capturing pre-change state...")
state_mgr.capture_state("pre_change")
state_mgr.save_state_to_file("pre_change", "pre_change_backup.json")

# Step 2: Make changes
print("Deploying changes...")
device.send_command("configure terminal")
device.send_command("vlan 100")
device.send_command("name DATA")
device.send_command("exit")
device.send_command("end")

# Step 3: Capture post-change state
print("Capturing post-change state...")
state_mgr.capture_state("post_change")

# Step 4: Compare states
print("Analyzing changes...")
diff = state_mgr.compare_states("pre_change", "post_change")
print(json.dumps(diff, indent=2))

device.disconnect()
```

---

## Pattern 2: Validation-Driven Rollback

### The Implementation

```python
# src/validation.py
from dataclasses import dataclass
from typing import Callable, Any, List

@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    details: dict = None

class DeviceValidator:
    """Validate device state and trigger rollback if needed."""
    
    def __init__(self, device, state_manager):
        """
        Initialize validator.
        
        Args:
            device: Netmiko device
            state_manager: DeviceStateManager instance
        """
        self.device = device
        self.state_manager = state_manager
        self.validators = []
    
    def add_validator(self, name: str, validation_func: Callable):
        """
        Register a validation function.
        
        Args:
            name: Validator name
            validation_func: Function that returns ValidationResult
        """
        self.validators.append((name, validation_func))
    
    def validate_all(self) -> List[ValidationResult]:
        """
        Run all registered validators.
        
        Returns:
            list: Validation results
        """
        results = []
        
        for name, validator_func in self.validators:
            try:
                result = validator_func()
                results.append(result)
                
                status = "✓" if result.passed else "✗"
                print(f"{status} {name}: {result.message}")
            
            except Exception as e:
                result = ValidationResult(
                    passed=False,
                    message=f"Validator failed: {str(e)}",
                    details={"error": str(e)}
                )
                results.append(result)
        
        return results
    
    def all_passed(self, results: List[ValidationResult]) -> bool:
        """Check if all validations passed."""
        return all(r.passed for r in results)


# Example validators for common checks

def validate_no_config_errors(device) -> ValidationResult:
    """Check device has no syntax errors."""
    output = device.send_command("show running-config")
    
    if "ERROR" in output or "invalid" in output.lower():
        return ValidationResult(
            passed=False,
            message="Configuration contains errors"
        )
    
    return ValidationResult(
        passed=True,
        message="No configuration errors detected"
    )


def validate_interfaces_up(device, min_interfaces=2) -> ValidationResult:
    """Check minimum number of interfaces are up."""
    output = device.send_command("show ip interface brief")
    
    # Count 'up' interfaces
    up_count = output.count(" UP ")
    
    if up_count < min_interfaces:
        return ValidationResult(
            passed=False,
            message=f"Only {up_count} interfaces up (expected {min_interfaces})",
            details={"up_interfaces": up_count, "required": min_interfaces}
        )
    
    return ValidationResult(
        passed=True,
        message=f"{up_count} interfaces up (required {min_interfaces})"
    )


def validate_bgp_neighbors_established(device, min_neighbors=1) -> ValidationResult:
    """Check BGP neighbors are established."""
    output = device.send_command("show ip bgp summary")
    
    # Count 'Established' neighbors
    established = output.count("Established")
    
    if established < min_neighbors:
        return ValidationResult(
            passed=False,
            message=f"Only {established} BGP neighbors established (expected {min_neighbors})"
        )
    
    return ValidationResult(
        passed=True,
        message=f"{established} BGP neighbors established"
    )


def validate_vlans_created(device, expected_vlans: List[int]) -> ValidationResult:
    """Check expected VLANs exist."""
    output = device.send_command("show vlan brief")
    
    missing = []
    for vlan_id in expected_vlans:
        vlan_exists = any(
            line.split() and line.split()[0] == str(vlan_id)
            for line in output.splitlines()
        )
        if not vlan_exists:
            missing.append(vlan_id)
    
    if missing:
        return ValidationResult(
            passed=False,
            message=f"VLANs missing: {missing}",
            details={"missing_vlans": missing}
        )
    
    return ValidationResult(
        passed=True,
        message=f"All {len(expected_vlans)} expected VLANs created"
    )
```

---

## Pattern 3: Automatic Rollback

### The Implementation

```python
# src/rollback.py
from state_management import DeviceStateManager
from validation import DeviceValidator

class RollbackManager:
    """Manage configuration rollback."""
    
    def __init__(self, device):
        """Initialize rollback manager."""
        self.device = device
        self.state_manager = DeviceStateManager(device)
        self.rollback_config = None
    
    def safe_config_deploy(self, change_func, validators: list) -> bool:
        """
        Apply configuration changes with automatic rollback on failure.
        
        Args:
            change_func: Function that applies changes (takes device as arg)
            validators: List of (validator_name, validator_func) tuples
        
        Returns:
            bool: True if successful, False if rolled back
        """
        print("Step 1: Capturing pre-change configuration...")
        self.state_manager.capture_state("pre_change")
        self.state_manager.save_state_to_file("pre_change", "pre_change.json")
        
        print("\nStep 2: Applying configuration changes...")
        try:
            change_func(self.device)
        except Exception as e:
            print(f"✗ Configuration deployment failed: {str(e)}")
            print("Performing emergency rollback...")
            self._rollback_to_saved_state()
            return False
        
        print("\nStep 3: Capturing post-change configuration...")
        self.state_manager.capture_state("post_change")
        
        print("\nStep 4: Validating changes...")
        validator = DeviceValidator(self.device, self.state_manager)
        
        # Register all validators
        for validator_name, validator_func in validators:
            validator.add_validator(
                validator_name,
                lambda vf=validator_func: vf(self.device)
            )
        
        results = validator.validate_all()
        
        if not validator.all_passed(results):
            print("\n✗ Post-deployment validation FAILED")
            print("Performing automatic rollback...")
            self._rollback_to_saved_state()
            return False
        
        print("\n✓ All validations PASSED")
        print("Configuration change successful!")
        return True
    
    def _rollback_to_saved_state(self):
        """Rollback to pre-change state."""
        print("Loading pre-change configuration...")
        
        # Get running config from before change
        # This is device-specific; example for Cisco IOS:
        pre_state = self.state_manager.state_history.get("pre_change")
        
        if not pre_state:
            print("✗ ERROR: No pre-change state available!")
            return
        
        # For full rollback, reload from backup or use NVRAM
        print("Reloading from startup configuration...")
        output = self.device.send_command_timing(
            "reload",
            strip_prompt=False,
            strip_command=False
        )
        if "confirm" in output.lower() or "proceed" in output.lower():
            self.device.send_command_timing(
                "yes",
                strip_prompt=False,
                strip_command=False
            )
        
        # Wait for reload (in production, use proper wait logic)
        import time
        time.sleep(60)
        
        print("✓ Rollback to pre-change state...")
```

### Production Usage

```python
# src/deploy.py
from netmiko import ConnectHandler
from rollback import RollbackManager
from validation import (
    validate_no_config_errors,
    validate_interfaces_up,
    validate_vlans_created
)

def deploy_vlan_config(device):
    """Apply VLAN configuration."""
    device.send_command("configure terminal")
    device.send_command("vlan 100")
    device.send_command("name DATA")
    device.send_command("exit")
    device.send_command("vlan 101")
    device.send_command("name VOICE")
    device.send_command("exit")
    device.send_command("end")
    print("✓ VLAN configuration commands sent")

# Main deployment workflow
device = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    password="password"
)

rollback = RollbackManager(device)

validators = [
    ("config_errors", validate_no_config_errors),
    ("interfaces_up", validate_interfaces_up),
    ("vlans_created", lambda d: validate_vlans_created(d, [100, 101])),
]

success = rollback.safe_config_deploy(deploy_vlan_config, validators)

if success:
    print("\n✓ Deployment successful!")
else:
    print("\n✗ Deployment failed and rolled back")

device.disconnect()
```

---

## Pattern 4: Nornir Integration with Rollback

```python
# src/nornir_rollback_task.py
from nornir import InitNornir
from nornir.core.task import Task, Result
from rollback import RollbackManager
from validation import (
    validate_no_config_errors,
    validate_interfaces_up
)

def deploy_with_rollback(task: Task) -> Result:
    """
    Nornir task: Deploy config with automatic rollback.
    """
    try:
        # Get device connection
        device = task.host.get_connection("netmiko", task.nornir.config)
        
        # Initialize rollback manager
        rollback = RollbackManager(device)
        
        # Define change function
        def apply_changes(dev):
            dev.send_command("configure terminal")
            dev.send_command("interface Gi0/0/1")
            dev.send_command("shutdown")
            dev.send_command("exit")
            dev.send_command("end")
        
        # Define validators
        validators = [
            ("config_errors", validate_no_config_errors),
            ("interfaces_up", validate_interfaces_up),
        ]
        
        # Perform safe deployment
        success = rollback.safe_config_deploy(apply_changes, validators)
        
        if success:
            return Result(
                host=task.host,
                result="Deployment successful with all validations passed"
            )
        else:
            return Result(
                host=task.host,
                failed=True,
                result="Deployment failed and was rolled back"
            )
    
    except Exception as e:
        return Result(
            host=task.host,
            failed=True,
            result=f"Deployment error: {str(e)}"
        )

# Usage
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=deploy_with_rollback)

# Print results
for hostname, result in results.items():
    status = "✓" if not result[0].failed else "✗"
    print(f"{status} {hostname}: {result[0].result}")
```

---

## Best Practices

### 1. Always Capture State BEFORE Changes

```python
# ✅ GOOD
state_mgr.capture_state("pre_change")
make_changes()
state_mgr.capture_state("post_change")

# ❌ BAD - No pre-state to rollback to
make_changes()
state_mgr.capture_state("post_change")
```

### 2. Validate Specific, Measurable Conditions

```python
# ✅ GOOD - Specific, testable condition
def validate_vlan_100_exists(device):
    output = device.send_command("show vlan id 100")
    if "VLAN0100" in output:
        return ValidationResult(passed=True, message="VLAN 100 exists")
    return ValidationResult(passed=False, message="VLAN 100 missing")

# ❌ BAD - Vague, unmeasurable
def validate_config_good(device):
    # "Good"? What does that mean?
    return ValidationResult(passed=True, message="Config looks good")
```

### 3. Implement Gradual Rollout

```python
# ✅ GOOD - Deploy to 5% first, then 50%, then 100%
devices = get_all_devices()
deploy_to_devices(devices[0:len(devices)//20])  # 5%
validate_all()
deploy_to_devices(devices[len(devices)//20:len(devices)//2])  # 45%
validate_all()
deploy_to_devices(devices[len(devices)//2:])  # 50%

# ❌ BAD - All-or-nothing deployment
deploy_to_devices(all_devices)
```

### 4. Keep Rollback Simple

```python
# ✅ GOOD - Rollback is straightforward
# Option 1: Reload from NVRAM
device.send_command("reload")

# Option 2: Restore from backup
restore_from_backup(device)

# ❌ BAD - Complex rollback that might fail
try_to_undo_each_command()  # Fragile!
```

### 5. Test Rollback Procedures

```python
# pytest
def test_rollback_works(mock_device):
    """Ensure rollback actually works."""
    rollback = RollbackManager(mock_device)
    
    # Capture state
    rollback.state_manager.capture_state("pre_change")
    
    # Make bad change that fails validation
    def bad_change(dev):
        dev.send_command("shutdown all interfaces")  # BAD!
    
    validators = [
        ("interfaces_up", validate_interfaces_up)
    ]
    
    success = rollback.safe_config_deploy(bad_change, validators)
    
    assert success is False  # Should have rolled back
    assert mock_device.reload.called  # Verify reload was called
```

---

## Summary

| Concept | Purpose |
| :--- | :--- |
| **State Capture** | Snapshot device before and after |
| **Comparison** | Identify exactly what changed |
| **Validation** | Verify changes are correct |
| **Automatic Rollback** | Fix problems without manual intervention |
| **Gradual Rollout** | Detect failures early, limit blast radius |

## **Safe deployment = Capture → Change → Validate → Rollback if needed**

---

## Next Steps

- **[State Management & Idempotency](./state-management-idempotency-network-automation.md)** — Ensure safe repeatable deployments
- **[Health Checks & Pre-Flight Validation](./health-checks-pre-flight-validation.md)** — Validate before changes
