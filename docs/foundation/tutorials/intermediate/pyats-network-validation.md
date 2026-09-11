---
title: PyATS Network Validation
description: Master PyATS device parsing, testbed configuration, and validation patterns. Learn how to capture network state and validate automation changes in production.
tags:
  - PyATS
  - Network Validation
  - Device Parsing
  - Testing
  - Cisco
---

## From Basics to Production Patterns

In the [PyATS Fundamentals](./pyats-fundamentals.md) guide, you learned the core concepts. Now let's build practical patterns you'll use in production.

This guide focuses on:

- Real device parsing (what does the data actually look like?)
- Designing validation checkpoints (what should you validate?)
- Handling common pitfalls (dealing with failures, timeouts, credential issues)
- Scaling across multiple devices

### Platform Support Note

PyATS/Genie workflows are intended for **Linux and macOS**. If you're working from Windows, use **WSL2** (recommended), a Linux VM, or a Linux container before following the examples.

---

## Deep Dive: Device Parsing

### What PyATS Parsing Actually Returns

When you call `device.parse('show vlan')`, you don't get text. You get structured data:

```python
from pyats.topology import loader

# Load testbed — reads device definitions and credentials
testbed = loader.load('testbed.yaml')

# Get specific device from testbed dictionary
device = testbed.devices['switch-01']

# Connect to device — initiates SSH session using testbed credentials
device.connect()

# Parse VLAN output into structured data
# device.parse() sends 'show vlan' command to device
# Genie parser (specific to device OS) converts text output to dict
vlan_output = device.parse('show vlan')

# Visualize the structure by printing as JSON
import json
print(json.dumps(vlan_output, indent=2))
# This shows exact structure so you know how to access data
```

**Output structure** — Let's break down what you get:

```json
{
  "vlans": {
    "1": {
      "name": "default",
      "state": "active",
      "interfaces": [
        "Ethernet1/1",
        "Ethernet1/2"
      ]
    },
    "10": {
      "name": "DATA",
      "state": "active",
      "interfaces": [
        "Ethernet1/3",
        "Ethernet1/4"
      ]
    }
  }
}
```

**Key Point:** Structured, not text. Easy to validate.

### Common Commands & Their Output Structure

#### Show VLAN

```python
# Parse show vlan command and get dictionary
vlans = device.parse('show vlan')

# Navigate to specific VLAN
# vlans is dict with 'vlans' key
# vlans['vlans'] gives us dict of VLAN IDs
# vlans['vlans']['10'] gives us VLAN 10's data

vlan_10 = vlans['vlans']['10']
# vlan_10 now contains: {'name': 'DATA', 'state': 'active', 'interfaces': [...]}

# Access VLAN 10 properties
print(vlan_10['name'])  
# Returns: "DATA" — the VLAN name

print(vlan_10['state'])
# Returns: "active" — whether VLAN is active or suspended

print(vlan_10['interfaces'])
# Returns: ['Ethernet1/3', 'Ethernet1/4'] — list of interface names in this VLAN
```

**How to use this in validation:**

```python
# Check if VLAN exists
if '20' in vlans['vlans']:
    print("✅ VLAN 20 found")
else:
    print("❌ VLAN 20 NOT found")

# Check VLAN name
assert vlans['vlans']['10']['name'] == 'DATA', "VLAN 10 name is wrong!"

# Check interfaces in VLAN
vlan_10_ports = vlans['vlans']['10']['interfaces']
assert 'Ethernet1/3' in vlan_10_ports, "Ethernet1/3 not in VLAN 10!"
```

---

#### Show IP Route

```python
# Parse show ip route command
routes = device.parse('show ip route')

# IOS/IOS-XE Genie route output is nested by VRF and address family:
# routes['vrf']['default']['address_family']['ipv4']['routes']
# Each prefix maps to route information (next hops, metrics, protocols)

# Navigate routing table
# route_table is dict where keys are IP prefixes (like "10.0.0.0/24")
route_table = routes['vrf']['default']['address_family']['ipv4']['routes']

for prefix, route_data in route_table.items():
    # prefix examples: "10.0.0.0/24", "192.168.1.0/24"
    # route_data is dict with next hop, metric, and protocol info
    
    print(f"{prefix}: {route_data}")
    # Output example:
    # 10.0.0.0/24: {'metric': 0, 'next_hop': {'next_hop_list': {...}}, ...}
```

**How to use in validation:**

```python
# Check if specific route exists
if '10.0.0.0/24' in route_table:
    print("✅ Route to 10.0.0.0/24 exists")
else:
    print("❌ Route to 10.0.0.0/24 missing!")

# Check route metric (hop count)
route_data = route_table['10.0.0.0/24']
metric = route_data['metric']
assert metric == 0, f"Expected metric 0, got {metric}"
```

---

#### Show Interfaces

```python
# Parse show interfaces command
interfaces = device.parse('show interfaces')

# Dictionary where keys are interface names
# interfaces['Ethernet1/1'] has all data for that interface

# Check which interfaces are operationally up
interfaces_up = [
    name for name, data in interfaces.items()
    # Iterate through all interfaces
    if data.get('oper_status') == 'up'
    # Filter only those with oper_status='up'
]

print(f"Interfaces up: {len(interfaces_up)}")
# Output example: Interfaces up: 48

# Detailed interface status
for iface_name, iface_data in interfaces.items():
    status = iface_data.get('oper_status')  # 'up' or 'down'
    mtu = iface_data.get('mtu')  # Interface MTU
    mac = iface_data.get('mac_address')  # MAC address
    errors = iface_data.get('counters', {}).get('in_errors', 0)
    # Safely access nested dict with .get() to avoid KeyError
    
    print(f"{iface_name}: {status} (MTU:{mtu}, MAC:{mac}, Errors:{errors})")
```

**How to use in validation:**

```python
# Check that minimum number of interfaces are up
min_expected_up = 48
assert len(interfaces_up) >= min_expected_up, \
    f"Expected {min_expected_up} up, got {len(interfaces_up)}"

# Check for error counters (indicates hardware problems)
eth1_data = interfaces['Ethernet1/1']
input_errors = eth1_data.get('counters', {}).get('in_errors', 0)
output_errors = eth1_data.get('counters', {}).get('out_errors', 0)

assert input_errors == 0, f"Ethernet1/1 has input errors: {input_errors}"
assert output_errors == 0, f"Ethernet1/1 has output errors: {output_errors}"
```

---

#### Show IP BGP Summary

```python
# Parse show ip bgp summary command
bgp = device.parse('show ip bgp summary')

# Navigate nested structure: device → bgp_id → neighbors
# bgp['vrf']['default']['neighbor'] gives dict of BGP neighbors

neighbors = bgp['vrf']['default']['neighbor']
# Use a different VRF name if you're validating non-default VRFs

# Iterate through BGP neighbors
for neighbor_ip, neighbor_data in neighbors.items():
    # neighbor_ip examples: "10.0.0.1", "192.168.1.1"
    # neighbor_data contains per-address-family data
    af_data = neighbor_data['address_family']['ipv4 unicast']
    
    state_or_prefixes = af_data['state_pfxrcd']
    # Established peers show a prefix count; down peers show states like 'Idle' or 'Active'
    
    print(f"Neighbor {neighbor_ip}: {state_or_prefixes}")
    # Output examples:
    # Neighbor 10.0.0.1: 100
    # Neighbor 10.0.0.2: 42
```

**How to use in validation:**

```python
# Check that all BGP neighbors are established
required_neighbors = ['10.0.0.1', '10.0.0.2']

for neighbor_ip in required_neighbors:
    # Check neighbor exists in BGP summary
    assert neighbor_ip in neighbors, \
        f"BGP neighbor {neighbor_ip} not in summary!"
    
    # Check neighbor is established (state_pfxrcd is a prefix count)
    af_data = neighbors[neighbor_ip]['address_family']['ipv4 unicast']
    state_or_prefixes = af_data['state_pfxrcd']
    assert state_or_prefixes.isdigit(), \
        f"BGP neighbor {neighbor_ip} not established! State: {state_or_prefixes}"
```

### Finding Available Parsers

Not all commands are available. Check which ones Cisco supports:

# Verify that Genie has a parser for a command on your device
pyats parse "show vlan" --testbed-file testbed.yaml --devices switch-01

# Try command variants if needed
pyats parse "show vlan id 10" --testbed-file testbed.yaml --devices switch-01
```

Or visit [Cisco's Parser Index](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers) for the full list.

---

## Real-World Validation Patterns

### Pattern 1: Configuration Compliance Check

**Scenario:** Ensure all access ports are in the correct VLAN

```python
def test_access_port_compliance(device):
    """
    Validate: All access ports must be in VLAN 10 (DATA)
    Except: Port Et1/48 which should be in VLAN 20 (MGMT)
    
    This pattern proves that your VLAN configuration matches requirements
    """
    
    # Parse VLAN data — returns structured dict of all VLANs and their ports
    vlan_data = device.parse('show vlan')
    
    # Define REQUIRED configuration: which ports MUST be in which VLANs
    required_config = {
        '10': ['Ethernet1/1', 'Ethernet1/2', 'Ethernet1/3', 'Ethernet1/4'],
        # VLAN 10 must have these 4 ports (DATA VLAN)
        
        '20': ['Ethernet1/48'],
        # VLAN 20 must have this 1 port (MGMT VLAN)
    }
    
    # For each VLAN in required config, validate all ports are there
    for vlan_id, required_ports in required_config.items():
        # Get actual ports in this VLAN from device parsing
        actual_ports = vlan_data['vlans'][vlan_id]['interfaces']
        # vlan_data['vlans'][vlan_id] gets VLAN's dict
        # ['interfaces'] gets the list of interface names in this VLAN
        
        # Validate: all required ports are actually there
        for port in required_ports:
            # Check each required port
            assert port in actual_ports, \
                f"{port} missing from VLAN {vlan_id}!"
            # If port not found, assertion fails with error message
        
        # Also warn about UNEXPECTED ports (ports that shouldn't be there)
        unexpected = set(actual_ports) - set(required_ports)
        # set() creates set of port names
        # actual_ports - required_ports gives ports in actual but not required
        
        if unexpected:
            # Print warning about extra ports (not required, but not harmful)
            print(f"⚠️  Warning: Unexpected ports in VLAN {vlan_id}: {unexpected}")
            # This warns ops team but doesn't fail test
    
    print("✅ VLAN compliance check passed")
    # All assertions passed = all ports are correctly assigned
```

**How this works step-by-step:**

1. Parse show vlan (get current port-to-VLAN mapping)
2. Define required mapping (what ports SHOULD be in each VLAN)
3. For each VLAN: extract actual ports from parsing
4. Compare: actual ports must include all required ports
5. Warn: if extra ports found that shouldn't be there
6. Result: pass if all requirements met

---

### Pattern 2: Interface Health Check

**Scenario:** After deploying new infrastructure, validate all interfaces are up and operational

```python
def test_interface_health(device, expected_up_count=48):
    """
    Validate: Expected number of interfaces are operational
    Also Check: No disabled ports, no down ports, no errors
    
    This pattern proves infrastructure is healthy after deployment
    """
    
    # Parse show interfaces — get detailed data for every interface
    interfaces = device.parse('show interfaces')
    
    # Initialize counters to track interface status
    interfaces_up = 0
    # Count how many interfaces are operationally up
    
    interfaces_errors = 0
    # Count interfaces with errors (input or output errors)
    
    interfaces_down = []
    # List of interface names that are down
    
    # Iterate through all interfaces on device
    for iface_name, iface_data in interfaces.items():
        # iface_name examples: 'Ethernet1/1', 'Ethernet1/2'
        # iface_data is dict with all interface properties
        
        # Skip loopbacks and management interfaces (not data ports)
        if 'Loopback' in iface_name or 'Management' in iface_name:
            continue
            # Skip these interface types — we're only checking data ports
        
        # Count how many are operationally up
        if iface_data.get('oper_status') == 'up':
            # .get() safely accesses dict key (returns None if missing)
            interfaces_up += 1
            # Increment counter if interface is up
        else:
            # Interface is NOT up (down, testing, etc.)
            interfaces_down.append(iface_name)
            # Add to list of down interfaces for reporting
        
        # Check for error counters (indicates hardware or line problems)
        input_errors = iface_data.get('counters', {}).get('in_errors', 0)
        # Get input error count from counters dict (default 0 if missing)
        
        output_errors = iface_data.get('counters', {}).get('out_errors', 0)
        # Get output error count (default 0 if missing)
        
        # Warn if either error counter is non-zero
        if input_errors > 0 or output_errors > 0:
            interfaces_errors += 1
            # Increment error counter
            
            print(f"⚠️  {iface_name}: errors detected (in:{input_errors}, out:{output_errors})")
            # Print warning with error details
    
    # Run assertions — fail test if any condition not met
    
    # Assertion 1: Minimum number of interfaces must be up
    assert interfaces_up >= expected_up_count, \
        f"Expected {expected_up_count} interfaces up, got {interfaces_up}"
        # Shows expected vs actual in error message
    
    # Assertion 2: No interfaces should have errors
    assert interfaces_errors == 0, \
        f"Found {interfaces_errors} interfaces with errors"
    
    # Assertion 3: All expected interfaces should be up (none down)
    assert len(interfaces_down) == 0, \
        f"Expected all interfaces up, but these are down: {interfaces_down}"
        # List the down interfaces in error message
    
    print(f"✅ Interface health check passed ({interfaces_up} interfaces up)")
    # All assertions passed = infrastructure is healthy
```

**How this works step-by-step:**

1. Parse show interfaces (get status of every interface)
2. Skip management/loopback interfaces (not data ports)
3. Count up interfaces
4. Check for error counters (indicates hardware problems)
5. Assert: minimum number up, no errors, no unexpected downs
6. Result: pass if all conditions met

---

### Pattern 3: Routing Validation

**Scenario:** Ensure critical routes exist after a network change

```python
def test_critical_routes(device):
    """
    Validate: Critical routes exist and are reachable
    
    This pattern proves your network topology changes worked
    """
    
    routes = device.parse('show ip route')
    
    required_routes = [
        '10.0.0.0/8',      # Corporate network
        '192.168.0.0/16',  # Management network
        '172.16.0.0/12',   # WAN network
    ]
    
    route_table = routes['vrf']['default']['address_family']['ipv4']['routes']
    available_routes = list(route_table.keys())
    
    for required in required_routes:
        assert required in available_routes, \
            f"Critical route {required} not found in routing table!"
        
        route_info = route_table[required]
        print(f"✅ Route {required} exists")
    
    print("✅ Routing validation passed")
```

### Pattern 4: BGP Neighbor Validation

**Scenario:** Ensure all expected BGP neighbors are established

```python
def test_bgp_neighbors(device):
    """
    Validate: All BGP neighbors are established
    """
    
    bgp = device.parse('show ip bgp summary')
    
    # Get neighbors
    neighbors = bgp['vrf']['default']['neighbor']
    
    required_neighbors = {
        '10.0.1.1': 'ipv4 unicast',     # Primary ISP peer
        '10.0.2.1': 'ipv4 unicast',     # Secondary ISP peer
        '192.168.1.2': 'ipv4 unicast',  # Internal peer
    }
    
    for neighbor_ip, address_family in required_neighbors.items():
        actual_neighbor = neighbors.get(neighbor_ip, {})
        af_data = actual_neighbor.get('address_family', {}).get(address_family, {})
        state_or_prefixes = af_data.get('state_pfxrcd', 'Down')
        
        assert state_or_prefixes.isdigit(), \
            f"BGP neighbor {neighbor_ip}: not established, got {state_or_prefixes}"
        
        # Check message counts
        messages_received = af_data.get('msg_rcvd', 0)
        assert messages_received > 0, \
            f"BGP neighbor {neighbor_ip}: no messages received!"
        
        print(f"✅ BGP neighbor {neighbor_ip}: {state_or_prefixes} prefixes ({messages_received} messages)")
    
    print("✅ BGP validation passed")
```

---

## Handling Real-World Challenges

### Challenge 1: Device Connection Timeouts

Some devices are slow or unreliable. Handle gracefully:

```python
import pytest
from pyats.topology import loader

@pytest.fixture
def device_with_timeout(testbed):
    """Connect with timeout handling"""
    device = testbed.devices['slow_switch']
    
    try:
        device.connect(timeout=30)  # 30-second timeout
        yield device
    except Exception as e:
        pytest.fail(f"Failed to connect to device: {e}")
    finally:
        try:
            device.disconnect()
        except:
            pass  # Connection already closed or never opened

def test_with_retry(device_with_timeout):
    """Retry parsing if device is slow"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            vlan_data = device_with_timeout.parse('show vlan')
            break  # Success
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                pytest.fail(f"Failed after {max_retries} retries: {e}")
            print(f"⚠️  Retry {retry_count}/{max_retries}")
```

### Challenge 2: Incomplete Device Data

Some commands might fail on some devices:

```python
def test_with_graceful_fallback(device):
    """
    Validate routing even if BGP isn't configured
    """
    
    # Try to get BGP data, but don't fail if not available
    bgp_data = None
    try:
        bgp_data = device.parse('show ip bgp summary')
    except Exception:
        print("⚠️  BGP not configured on this device")
    
    # Validate routing (always available)
    routes = device.parse('show ip route')
    assert routes is not None, "No routing table?"
    
    # Optional: validate BGP only if available
    if bgp_data:
        neighbors = bgp_data['vrf']['default']['neighbor']
        assert len(neighbors) > 0, "BGP neighbors not established"
    
    print("✅ Validation passed")
```

### Challenge 3: Credential Management

Always use vault encryption:

```yaml
# testbed.yaml
testbed:
  name: "Production"

devices:
  switch-01:
    type: switch
    os: ios
    connections:
      cli:
        protocol: ssh
        ip: 10.1.1.1
        port: 22
        credentials:
          default:
            username: admin
            password: !vault |
              $ANSIBLE_VAULT;1.1;AES256;secrets
              # Encrypted password
```

In your test, credentials are automatically decrypted:

```python
def test_with_vault_credentials(device):
    """Credentials are automatically decrypted from vault"""
    # No need to pass password - PyATS handles it
    device.connect()
    # ... run your tests
    device.disconnect()
```

---

## Scaling: Testing Multiple Devices

### Pattern: Multi-Device Validation

```python
import pytest
from pyats.topology import loader

@pytest.fixture(scope='session')
def testbed():
    return loader.load('testbed.yaml')

@pytest.mark.parametrize('device_name', ['switch-01', 'switch-02', 'switch-03'])
def test_vlan_on_all_switches(testbed, device_name):
    """
    Run the same test on all switches
    PyTest will run this 3 times (once per device)
    """
    device = testbed.devices[device_name]
    device.connect()
    
    # Validate VLAN 10 exists
    vlans = device.parse('show vlan')
    assert '10' in vlans['vlans'], f"VLAN 10 missing on {device_name}!"
    
    device.disconnect()
```

Run it:

```bash
pytest test_multi_device.py -v

# Output:
# test_vlan_on_all_switches[switch-01] PASSED
# test_vlan_on_all_switches[switch-02] PASSED
# test_vlan_on_all_switches[switch-03] PASSED
```

### Pattern: Validate Configuration Consistency Across Devices

```python
def test_consistent_vlan_config(testbed):
    """
    Ensure all switches have the same VLAN configuration
    """
    
    all_devices_vlans = {}
    
    # Collect VLAN data from all switches
    for device_name in ['switch-01', 'switch-02', 'switch-03']:
        device = testbed.devices[device_name]
        device.connect()
        
        vlans = device.parse('show vlan')
        all_devices_vlans[device_name] = set(vlans['vlans'].keys())
        
        device.disconnect()
    
    # Compare
    reference_vlans = all_devices_vlans['switch-01']
    
    for device_name, vlans in all_devices_vlans.items():
        assert vlans == reference_vlans, \
            f"{device_name} VLAN config differs from switch-01!"
    
    print("✅ All switches have consistent VLAN configuration")
```

---

## Integration with Automation

### Before/After Pattern (Complete Example)

```python
from pyats.topology import loader
from netmiko import ConnectHandler
import pytest

@pytest.fixture
def testbed():
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    dev = testbed.devices['switch-01']
    dev.connect()
    yield dev
    dev.disconnect()

def capture_baseline(device):
    """Capture state BEFORE automation"""
    return {
        'vlans': set(device.parse('show vlan')['vlans'].keys()),
        'interfaces_up': sum(
            1 for iface_data in device.parse('show interfaces').values()
            if iface_data.get('oper_status') == 'up'
        ),
    }

def run_automation(device):
    """Execute your actual automation"""
    from netmiko import ConnectHandler
    
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device.connections.cli.ip,
        username='admin',
        password='...',
    )
    
    # Configure new VLAN
    net_connect.send_config_set([
        'vlan 100',
        'name AUTOMATION-TEST',
    ])
    net_connect.disconnect()

def validate_automation(device, baseline):
    """Validate state AFTER automation"""
    after = {
        'vlans': set(device.parse('show vlan')['vlans'].keys()),
        'interfaces_up': sum(
            1 for iface_data in device.parse('show interfaces').values()
            if iface_data.get('oper_status') == 'up'
        ),
    }
    
    # Validate changes
    new_vlans = after['vlans'] - baseline['vlans']
    assert '100' in new_vlans, "VLAN 100 not created!"
    assert after['interfaces_up'] == baseline['interfaces_up'], \
        "Interfaces changed state!"
    
    return after

def test_vlan_automation_with_validation(device):
    """Complete automation with before/after validation"""
    
    baseline = capture_baseline(device)
    print(f"Before: {len(baseline['vlans'])} VLANs, {baseline['interfaces_up']} interfaces up")
    
    run_automation(device)
    
    after = validate_automation(device, baseline)
    print(f"After: {len(after['vlans'])} VLANs, {after['interfaces_up']} interfaces up")
    print("✅ Automation validated successfully")
```

---

## Testing Tips & Best Practices

### ✅ Do's

- ✅ **Capture baseline before automation** — You can't validate change without knowing the starting state
- ✅ **Test in non-critical environments first** — Lab or staging before production
- ✅ **Use fixtures for device connections** — PyTest fixtures handle setup/teardown automatically
- ✅ **Parameterise multi-device tests** — Run the same test on different devices
- ✅ **Document what you're validating** — Clear test names explain intent
- ✅ **Log results verbosely** — Future you will appreciate the detail

### ❌ Don'ts

- ❌ **Hardcode IP addresses** — Use testbed files
- ❌ **Store credentials in test files** — Use vault encryption
- ❌ **Assume device behaviour** — Parse and validate actual state
- ❌ **Skip error handling** — Devices fail. Handle it gracefully.
- ❌ **Test only happy paths** — What happens when a device is unreachable?

---

## Next Step

Ready to integrate PyATS into your actual automation workflow?

**[Building Reliable Automation with PyATS](./building-reliable-automation-with-pyats.md)** — Learn how PyATS integrates with Netmiko, Nornir, and your PRIME Framework engagements.

---

> **Structured parsing + validation = confidence.** When you can test network state programmatically, you can automate with certainty, not hope.
