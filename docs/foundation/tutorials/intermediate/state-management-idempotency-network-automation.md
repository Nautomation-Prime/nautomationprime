---
title: State Management & Idempotency
description: Build repeatable, safe automations. Run the same script multiple times without breaking things. Idempotent operations and state tracking for reliable automation.
tags:
  - State Management
  - Idempotency
  - Network Automation
  - Intermediate
  - Design Patterns
  - Reliability
---

## Why Idempotency Matters

**Ask yourself:** "What happens if I run this automation script twice?"

**Bad answer:** "It breaks things on the second run"
**Good answer:** "It's safe to run as many times as needed"

Idempotent operations are **repeatable without side effects.**

---

## The Problem: Non-Idempotent Operations

```python
# ❌ NOT IDEMPOTENT
def add_vlan_100(device):
    """Add VLAN 100."""
    device.send_command("configure terminal")
    device.send_command("vlan 100")
    device.send_command("name DATA")
    device.send_command("exit")
    device.send_command("end")

# Run 1: ✓ VLAN 100 created
# Run 2: ✗ ERROR - VLAN 100 already exists!
# Run 3-5: ✗ ERROR - VLAN 100 already exists!
```

**Non-idempotent operations are unreliable:**

- Fail on retry attempts
- Can't be used in scheduled jobs (will fail eventually)
- Cause automation distrust

---

## The Solution: Idempotent Operations

```python
# ✅ IDEMPOTENT
def ensure_vlan_100_exists(device):
    """Ensure VLAN 100 exists (safe to call repeatedly)."""
    # Check if VLAN already exists
    output = device.send_command("show vlan id 100")
    
    if "VLAN0100" in output:
        print("VLAN 100 already exists, skipping creation")
        return True
    
    # Only create if it doesn't exist
    device.send_command("configure terminal")
    device.send_command("vlan 100")
    device.send_command("name DATA")
    device.send_command("exit")
    device.send_command("end")
    
    print("VLAN 100 created")
    return True

# Run 1: ✓ VLAN 100 created
# Run 2: ✓ VLAN 100 already exists (skipped, safe)
# Run 3-5: ✓ VLAN 100 already exists (skipped, safe)
```

---

## Pattern 1: Check-Before-Change

### The Implementation

```python
# src/idempotent_operations.py
from dataclasses import dataclass
from enum import Enum

class OperationStatus(Enum):
    """Status of an idempotent operation."""
    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    FAILED = "failed"

@dataclass
class OperationResult:
    """Result of an idempotent operation."""
    status: OperationStatus
    message: str
    details: dict = None

class IdempotentOperations:
    """Idempotent network operations (safe to repeat)."""
    
    @staticmethod
    def ensure_vlan_exists(device, vlan_id: int, vlan_name: str) -> OperationResult:
        """
        Ensure VLAN exists with given name (idempotent).
        
        Safe to call multiple times—won't duplicate VLAN.
        """
        # Check if VLAN already exists
        output = device.send_command(f"show vlan id {vlan_id}")
        
        vlan_exists = any(
            line.split() and line.split()[0] == str(vlan_id)
            for line in output.splitlines()
        )
        
        if vlan_exists:
            # VLAN exists, verify name matches
            if vlan_name in output:
                return OperationResult(
                    status=OperationStatus.UNCHANGED,
                    message=f"VLAN {vlan_id} exists with correct name",
                    details={"vlan_id": vlan_id, "vlan_name": vlan_name}
                )
            else:
                # VLAN exists but name differs, update it
                device.send_command("configure terminal")
                device.send_command(f"vlan {vlan_id}")
                device.send_command(f"name {vlan_name}")
                device.send_command("exit")
                device.send_command("end")
                
                return OperationResult(
                    status=OperationStatus.UPDATED,
                    message=f"VLAN {vlan_id} name updated to {vlan_name}",
                    details={"vlan_id": vlan_id, "vlan_name": vlan_name}
                )
        
        # VLAN doesn't exist, create it
        device.send_command("configure terminal")
        device.send_command(f"vlan {vlan_id}")
        device.send_command(f"name {vlan_name}")
        device.send_command("exit")
        device.send_command("end")
        
        return OperationResult(
            status=OperationStatus.CREATED,
            message=f"VLAN {vlan_id} created with name {vlan_name}",
            details={"vlan_id": vlan_id, "vlan_name": vlan_name}
        )
    
    @staticmethod
    def ensure_interface_config(device, interface: str, config_lines: list) -> OperationResult:
        """
        Ensure interface has specific configuration (idempotent).
        
        Args:
            device: Netmiko device
            interface: Interface name (e.g., "Gi0/0/1")
            config_lines: List of config commands to apply
        """
        # Get current interface configuration
        current_config = device.send_command(f"show running-config interface {interface}")
        
        # Check if all config lines already exist
        all_exist = all(line in current_config for line in config_lines)
        
        if all_exist:
            return OperationResult(
                status=OperationStatus.UNCHANGED,
                message=f"Interface {interface} already has required configuration",
                details={"interface": interface, "lines": config_lines}
            )
        
        # Apply missing configuration
        device.send_command("configure terminal")
        device.send_command(f"interface {interface}")
        
        for config_line in config_lines:
            device.send_command(config_line)
        
        device.send_command("exit")
        device.send_command("end")
        
        return OperationResult(
            status=OperationStatus.UPDATED,
            message=f"Interface {interface} configuration applied",
            details={"interface": interface, "lines": config_lines}
        )
    
    @staticmethod
    def ensure_bgp_neighbor(device, asn: int, neighbor_ip: str, neighbor_asn: int) -> OperationResult:
        """Ensure BGP neighbor is configured (idempotent)."""
        # Check if neighbor already exists
        output = device.send_command("show ip bgp summary")
        
        if neighbor_ip in output:
            return OperationResult(
                status=OperationStatus.UNCHANGED,
                message=f"BGP neighbor {neighbor_ip} already configured",
                details={"neighbor_ip": neighbor_ip}
            )
        
        # Configure BGP neighbor
        device.send_command("configure terminal")
        device.send_command(f"router bgp {asn}")
        device.send_command(f"neighbor {neighbor_ip} remote-as {neighbor_asn}")
        device.send_command("exit")
        device.send_command("end")
        
        return OperationResult(
            status=OperationStatus.CREATED,
            message=f"BGP neighbor {neighbor_ip} configured",
            details={"neighbor_ip": neighbor_ip, "neighbor_asn": neighbor_asn}
        )
```

### Usage Example

```python
from netmiko import ConnectHandler
from idempotent_operations import IdempotentOperations, OperationStatus

device = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    password="password"
)

ops = IdempotentOperations()

# Run 1: Creates VLAN 100
result = ops.ensure_vlan_exists(device, 100, "DATA")
print(f"{result.status.value}: {result.message}")
# Output: created: VLAN 100 created with name DATA

# Run 2: Detects VLAN 100 already exists
result = ops.ensure_vlan_exists(device, 100, "DATA")
print(f"{result.status.value}: {result.message}")
# Output: unchanged: VLAN 100 exists with correct name

# Run 3: Safe to call again and again
result = ops.ensure_vlan_exists(device, 100, "DATA")
print(f"{result.status.value}: {result.message}")
# Output: unchanged: VLAN 100 exists with correct name

device.disconnect()
```

---

## Pattern 2: State-Driven Configuration

### The Problem

Imperative code (commands in order) doesn't guarantee desired state:

```python
# ❌ IMPERATIVE - Order-dependent
device.send_command("interface Gi0/0/1")
device.send_command("ip address 10.0.0.1 255.255.255.0")
# If someone manually removed the IP later, this script doesn't fix it
```

### The Solution: Declarative State

```python
# ✅ DECLARATIVE - Desired state always applied
desired_state = {
    "interfaces": {
        "Gi0/0/1": {
            "ip": "10.0.0.1",
            "netmask": "255.255.255.0",
            "enabled": True
        }
    }
}

# Ensure device matches desired state (idempotent)
ensure_device_state(device, desired_state)
```

### Implementation

```python
# src/state_driver.py
class StateDrivenConfigurator:
    """Apply desired state to device (idempotent)."""
    
    def __init__(self, device):
        self.device = device
    
    def get_current_state(self) -> dict:
        """Retrieve current device state."""
        return {
            "interfaces": self._get_interfaces(),
            "vlans": self._get_vlans(),
            "bgp": self._get_bgp_state(),
        }
    
    def _get_interfaces(self) -> dict:
        """Get current interface configuration."""
        output = self.device.send_command("show ip interface brief")
        interfaces = {}
        
        for line in output.split('\n'):
            if 'Gi' in line or 'Et' in line:
                parts = line.split()
                interface = parts[0]
                ip = parts[1] if len(parts) > 1 else None
                status = parts[4] if len(parts) > 4 else None
                
                interfaces[interface] = {
                    "ip": ip,
                    "status": status
                }
        
        return interfaces
    
    def _get_vlans(self) -> dict:
        """Get current VLAN configuration."""
        output = self.device.send_command("show vlan brief")
        vlans = {}
        
        for line in output.split('\n'):
            if line.split() and line.split()[0].isdigit():
                parts = line.split()
                vlan_id = parts[0]
                vlan_name = parts[1] if len(parts) > 1 else ""
                
                vlans[vlan_id] = {"name": vlan_name}
        
        return vlans
    
    def _get_bgp_state(self) -> dict:
        """Get current BGP state."""
        output = self.device.send_command("show ip bgp summary")
        
        # Simple parsing for neighbor count
        neighbor_count = output.count("Established")
        
        return {"neighbors_established": neighbor_count}
    
    def ensure_interfaces(self, desired_interfaces: dict):
        """Ensure interface configuration matches desired state."""
        current = self.get_current_state()["interfaces"]
        
        for interface, desired_config in desired_interfaces.items():
            current_config = current.get(interface, {})
            
            # Check if interface configuration matches
            if current_config.get("ip") != desired_config.get("ip"):
                print(f"Updating {interface} IP...")
                self.device.send_command("configure terminal")
                self.device.send_command(f"interface {interface}")
                self.device.send_command(
                    f"ip address {desired_config['ip']} {desired_config['netmask']}"
                )
                self.device.send_command("exit")
                self.device.send_command("end")
    
    def ensure_vlans(self, desired_vlans: dict):
        """Ensure VLAN configuration matches desired state."""
        current = self.get_current_state()["vlans"]
        
        for vlan_id, vlan_config in desired_vlans.items():
            if vlan_id not in current:
                print(f"Creating VLAN {vlan_id}...")
                self.device.send_command("configure terminal")
                self.device.send_command(f"vlan {vlan_id}")
                self.device.send_command(f"name {vlan_config['name']}")
                self.device.send_command("exit")
                self.device.send_command("end")
    
    def apply_desired_state(self, desired_state: dict):
        """Apply all desired state (idempotent)."""
        print("Applying desired state...")
        
        if "interfaces" in desired_state:
            self.ensure_interfaces(desired_state["interfaces"])
        
        if "vlans" in desired_state:
            self.ensure_vlans(desired_state["vlans"])
        
        print("✓ Desired state applied")
```

### Usage

```python
device = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1", 
    username="admin",
    password="password"
)

configurator = StateDrivenConfigurator(device)

desired_state = {
    "interfaces": {
        "Gi0/0/1": {
            "ip": "10.0.0.1",
            "netmask": "255.255.255.0"
        }
    },
    "vlans": {
        "100": {"name": "DATA"},
        "101": {"name": "VOICE"}
    }
}

# Run 1: Applies all configuration
configurator.apply_desired_state(desired_state)

# Run 2: Checks state, skips what's already correct
configurator.apply_desired_state(desired_state)

# Run 3-N: Safe to run anytime
configurator.apply_desired_state(desired_state)
```

---

## Pattern 3: Nornir with Idempotent Tasks

```python
# src/nornir_idempotent_tasks.py
from nornir import InitNornir
from nornir.core.task import Task, Result
from idempotent_operations import IdempotentOperations

def ensure_vlans(task: Task) -> Result:
    """Nornir task: Ensure VLANs exist (idempotent)."""
    device = task.host.get_connection("netmiko", task.nornir.config)
    ops = IdempotentOperations()
    
    # Get VLAN configuration from inventory or task data
    vlans = task.host.get("vlans", {})
    
    results = []
    for vlan_id, vlan_config in vlans.items():
        result = ops.ensure_vlan_exists(
            device,
            vlan_id,
            vlan_config["name"]
        )
        results.append(result)
    
    return Result(
        host=task.host,
        result={
            "vlans": [
                {
                    "vlan_id": r.details["vlan_id"],
                    "status": r.status.value,
                    "message": r.message
                }
                for r in results
            ]
        }
    )

# Usage
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=ensure_vlans)

# Results show what changed
for hostname, result in results.items():
    for vlan in result[0].result["vlans"]:
        print(f"{hostname}: VLAN {vlan['vlan_id']} - {vlan['status']}")
```

---

## Best Practices

### 1. Separate Checking from Doing

```python
# ✅ GOOD
def ensure_vlan_exists(device, vlan_id):
    # 1. Check
    if vlan_exists(device, vlan_id):
        return "already_exists"
    
    # 2. Create only if needed
    create_vlan(device, vlan_id)
    return "created"

# ❌ BAD - Assumes creation is needed
def create_vlan(device, vlan_id):
    device.send_command(f"vlan {vlan_id}")  # Fails if exists!
```

### 2. Return Operation Status

```python
# ✅ GOOD - Caller knows what happened
status = ensure_vlan_exists(device, 100)
if status == "created":
    print("New VLAN created")
elif status == "unchanged":
    print("VLAN already existed")

# ❌ BAD - Caller doesn't know
ensure_vlan_exists(device, 100)  # Did something happen?
```

### 3. Make Operations Small and Focused

```python
# ✅ GOOD - Single responsibility
def ensure_vlan_exists(device, vlan_id, vlan_name):
    # Only concerned with VLAN existence
    pass

# ❌ BAD - Too much responsibility
def configure_vlan_and_interfaces_and_bgp(device, vlan_id):
    # Does too many things, hard to reason about
    pass
```

### 4. Test Idempotency Explicitly

```python
def test_operation_is_idempotent(mock_device):
    """Verify running operation twice is safe."""
    
    # Run 1
    result1 = ensure_vlan_exists(mock_device, 100, "DATA")
    assert result1.status == OperationStatus.CREATED
    
    # Run 2 - should be safe
    result2 = ensure_vlan_exists(mock_device, 100, "DATA")
    assert result2.status == OperationStatus.UNCHANGED
    
    # Run 3 - still safe
    result3 = ensure_vlan_exists(mock_device, 100, "DATA")
    assert result3.status == OperationStatus.UNCHANGED
```

---

## Summary

| Concept | Definition |
| :--- | :--- |
| **Idempotent** | Safe to run multiple times, always produces same result |
| **Check-before-change** | Verify state before making changes |
| **Declarative** | "What state do we want?" not "What commands run?" |
| **Status reporting** | Tell caller what actually happened |

**Idempotent automation is reliable, repeatable, and trustworthy.**

---

## Next Steps

- **[Structured Logging](./structured-logging-network-automation.md)** — Track what idempotent operations did
- **[Health Checks & Pre-Flight](./health-checks-pre-flight-validation.md)** — Validate before idempotent deployment
