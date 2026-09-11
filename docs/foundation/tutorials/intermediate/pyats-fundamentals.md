---
title: PyATS Fundamentals
description: Learn PyATS (Python API for Test Automation System), Cisco's enterprise-grade framework used for millions of automated tests monthly. Build reliable network validation.
tags:
  - PyATS
  - Testing
  - Network Automation
  - Cisco
  - Validation
---

## Why PyATS Matters

Cisco uses **PyATS to execute millions of automated tests every month** across their infrastructure and products.

That's not millions per year. **Millions per month.**

If you're building production network automation—whether deploying configurations, upgrading devices, or making bulk changes—you need **validation**. PyATS is how enterprise teams prove their automation actually worked.

### Platform Support Note

PyATS/Genie is built for **Linux and macOS environments**. Native Windows installation is typically not supported for full workflows.

If you're on Windows, run these tutorials using **WSL2**, a Linux VM, or a containerized Linux environment.

---

## What is PyATS?

**PyATS** (Python API for Test Automation System) is Cisco's open-source, enterprise-grade test automation framework.

Built by Cisco engineers to test Cisco equipment at massive scale, it's now available for anyone to use.

### Key Capabilities

- **Device State Validation** — "Does the device have this configuration? Are these routes in the routing table?"
- **Before/After Testing** — Capture network state before automation runs, validate state after, prove the change worked
- **Multi-Vendor Support** — Works with Cisco, Juniper, Arista, F5, and others
- **Testbed-Driven** — Define your network topology once, write tests that apply across all devices
- **Production-Grade** — Robust error handling, detailed reporting, designed for enterprise operations

### Why It's Different from Other Testing Frameworks

| Aspect | PyATS | Generic Unit Testing |
| :--- | :--- | :--- |
| **Focus** | Network devices & infrastructure | Code logic |
| **Connection Model** | SSH/NETCONF to actual devices | Mocks and stubs |
| **Real Device State** | Validates actual network state | Validates code behaviour |
| **Enterprise Scale** | Built for millions of tests/month | Built for thousands/day |
| **Network-Specific** | Parsers for Cisco output, device APIs | Generic assertions |

**Example:** PyATS doesn't test "is my VLAN provisioning code correct?" It tests "did the VLAN actually get created on the device?"

---

## The Business Case: Why Your Team Needs This

### The Problem

You've written automation to:

- Provision 50 VLANs across 10 switches
- Upgrade IOS on 200 devices
- Configure new BGP peers on your WAN edge

The automation runs. No errors. You assume it worked.

**But did it actually?**

- Did all 50 VLANs actually get created on all 10 switches?
- Did any devices fail mid-upgrade?
- Did the BGP peering actually establish?

Without validation, you're guessing. And "guesswork" doesn't scale in production environments.

### The Solution: PyATS Validation

```python
# BEFORE automation: Capture current state
before_state = get_vlan_count(switch_ip)
print(f"Before: {before_state} VLANs exist")

# RUN YOUR AUTOMATION (provision 50 new VLANs)
provision_vlans(switch_ip, vlan_list)

# AFTER automation: Validate state changed
after_state = get_vlan_count(switch_ip)
assert after_state == before_state + 50, "VLAN provisioning failed!"
print(f"✅ Validation passed: {after_state} VLANs now exist")
```

**Result:** You have proof. Not "we think it worked." Actual proof.

---

## How PyATS Fits Into the PRIME Framework

| PRIME Stage | PyATS Role |
| :--- | :--- |
| **Pinpoint** | Establish baselines (pre-automation device state) |
| **Re-engineer** | Design validation checkpoints (what to verify) |
| **Implement** | Write PyATS tests alongside automation code |
| **Measure** | Compare before/after states—prove ROI |
| **Empower** | Automated tests become operational runbooks |

---

## PyATS Fundamentals: Key Concepts

### 1. Testbed File

A YAML file defining your network topology:

```yaml
testbed:
  name: "Production Network"
  # The testbed name identifies this set of devices
  # You can have multiple testbeds (prod, staging, lab)

devices:
  switch-01:
    # Device name — referenced in Python as testbed.devices['switch-01']
    # This is just a label you choose (can be hostname, IP, or any identifier)
    
    type: switch
    # Device type (switch, router, etc.) — helps PyATS optimise communications
    
    os: ios
    # Operating system — determines which parser to use
    # Options: ios, iosxe, nxos, junos, etc.
    
    connections:
      # Connection profiles — can have multiple (cli, netconf, etc.)
      cli:
        # 'cli' means SSH connection for CLI commands
        protocol: ssh
        # Protocol to use (ssh, telnet, etc.)
        
        ip: "10.1.1.1"
        # Device IP address or hostname
        
        port: 22
        # SSH port (default 22)
        
        credentials:
          # Define credentials for this connection
          default:
            # 'default' is the credential set name (can have multiple)
            username: admin
            # Username for device login
            
            password: !vault |
              # Encrypted password stored securely in vault format
              # This is Ansible Vault encryption (secure)
              # Never store plaintext passwords
    
  switch-02:
    # Second device with same structure
    type: switch
    os: ios
    connections:
      cli:
        protocol: ssh
        ip: "10.1.1.2"
        port: 22
        credentials:
          default:
            username: admin
            password: !vault |
              # Another encrypted password
```

**How PyATS Uses This:**

When you call `loader.load('testbed.yaml')`, PyATS:

1. Reads the YAML file and parses the structure
2. Creates a Testbed object containing all devices
3. Each device becomes a Device object with connection settings
4. When you call `device.connect()`, PyATS uses settings from this file to establish SSH session
5. Credentials are automatically decrypted (if using Ansible Vault)

**Key Concept — Why Define Once, Use Everywhere:**

- Define connectivity once in testbed.yaml (IPs, credentials, protocols)
- Reference in multiple test files: `testbed.devices['switch-01']`
- If device IP changes, update testbed.yaml once—all tests automatically use new IP
- Credentials encrypted at rest, decrypted on-demand by PyATS

**Credential Security:**

- ❌ **Bad:** `password: admin123` in plaintext (visible to anyone with file access)
- ✅ **Good:** `password: !vault |...` (encrypted, can only decrypt with vault password)

Use: `ansible-vault encrypt_string 'your_password' --name 'password'` to encrypt passwords securely.

### 2. Device Parsing

PyATS parses device CLI output into structured data:

```python
from pyats.topology import loader

# Load testbed — This reads testbed.yaml and creates device objects
# The testbed contains all device definitions, credentials, and connectivity details
testbed = loader.load('testbed.yaml')

# Get a specific device from the testbed
# testbed.devices is a dictionary of all devices defined in testbed.yaml
# 'switch-01' must match a device name in testbed.yaml
device = testbed.devices['switch-01']

# Connect to the device
# This initiates SSH connection using credentials from testbed.yaml
# PyATS handles connection pooling and session management automatically
device.connect()

# Parse CLI output automatically
# device.parse() sends 'show vlan' to the device and processes the output
# Instead of getting raw text, PyATS uses Genie parsers to convert output to structured data
# This parser is specific to the device OS (defined in testbed.yaml)
output = device.parse('show vlan')

# The output is a structured dictionary, not raw text:
# {
#   'vlans': {
#     '1': {
#       'name': 'default',
#       'status': 'active',
#       'interfaces': {'Ethernet0/1': {...}, ...}
#     },
#     '10': {
#       'name': 'DATA',
#       'status': 'active',
#       'interfaces': {'Ethernet0/2': {...}, ...}
#     }
#   }
# }

# Easy to validate using dictionary access (no regex, no parsing strings)
assert '10' in output['vlans'], "VLAN 10 missing!"
# This checks if key '10' exists in vlans dictionary
# Much more reliable than searching for "VLAN 10" in text output
```

**Breaking Down Each Line:**

- `loader.load('testbed.yaml')` — Reads your testbed file and creates device objects. No need to manually create connections.
- `testbed.devices['switch-01']` — Access a specific device by name. Must match device definition in testbed.yaml.
- `device.connect()` — Establishes SSH session. Credentials come from testbed.yaml (encrypted).
- `device.parse('show vlan')` — Sends command to device, receives output, runs Cisco's Genie parser on it.
- `output['vlans']` — Dictionary key access. Parsed data is always in the same structure regardless of device output formatting.
- `'10' in output['vlans']` — Check if VLAN ID exists. Uses dictionary keys, not string searching.

**Why This Matters:**

- ❌ **Without parsing:** Regex patterns that break when output format changes, fragile text processing
- ✅ **With PyATS:** Structured data, consistent dictionary access, parser handles all OS variations

**Key Insight:** Genie parsers are Python modules that understand Cisco CLI output format. When you call `device.parse('show vlan')`, PyATS:

1. Sends `show vlan` to device
2. Gets raw text output
3. Runs the Genie parser for "show vlan" (specific to device OS)
4. Returns structured dictionary

Different OSes (IOS, IOS-XE, NX-OS) return slightly different structures, but the parser handles all that complexity.

### 3. Test Structure

PyATS tests follow a simple pattern:

```python
import pytest
from pyats.topology import loader

@pytest.fixture(scope='session')
def testbed():
    """
    Fixture: Load testbed once per test session
    scope='session' means this runs once for the entire test suite
    Subsequent test functions reuse the same testbed object
    This is efficient—no need to reload testbed.yaml for each test
    """
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    """
    Fixture: Connect to a device and yield it to tests
    The fixture:
    1. Gets the device from testbed
    2. Connects via SSH (using credentials from testbed.yaml)
    3. 'yield' passes device to the test function
    4. After test completes, cleanup code runs (disconnect)
    
    Each test function that needs a device parameter receives this
    """
    dev = testbed.devices['switch-01']
    # Connect to device using settings from testbed.yaml
    dev.connect()
    
    # 'yield' pauses fixture and passes device to test
    # Test function runs here
    yield dev
    
    # This code runs AFTER test completes (cleanup)
    dev.disconnect()

def test_vlan_exists(device):
    """
    Test function: Check that VLAN exists
    
    Receives 'device' from the fixture above
    This is the PyATS Device object, already connected
    
    pytest runs this function and:
    1. Calls the device fixture (which connects)
    2. Passes device to this function
    3. Runs the assertions
    4. Fixture cleanup runs (disconnect)
    """
    # Parse show vlan output into structured data
    output = device.parse('show vlan')
    
    # Check: Is VLAN 10 in the vlans dictionary?
    assert '10' in output['vlans'], "VLAN 10 not found!"
    # If assertion passes, test passes
    # If fails, test fails and shows error message

def test_vlan_has_name(device):
    """
    Test function: Check VLAN has correct name
    """
    # Parse show vlan again (same pattern as above)
    output = device.parse('show vlan')
    
    # Access nested dictionary: output['vlans']['10'] gives us VLAN 10 data
    # VLAN 10 data is a dict with keys: 'name', 'status', 'interfaces', etc.
    vlan_10_data = output['vlans']['10']
    
    # Check: Does VLAN 10 have the expected name?
    assert vlan_10_data['name'] == 'DATA', "VLAN 10 name mismatch!"
    # This accesses the 'name' key from the VLAN data dictionary

def test_vlan_has_interfaces(device):
    """
    Test function: Check VLAN has expected interfaces
    """
    output = device.parse('show vlan')
    
    # Navigate nested structure: vlans → 10 → interfaces
    # VLAN 10 interfaces is a dictionary of interface names
    vlan_10_interfaces = output['vlans']['10']['interfaces']
    
    # vlan_10_interfaces looks like:
    # {'Ethernet0/1': {...}, 'Ethernet0/2': {...}, ...}
    
    # Check: Is Ethernet0/1 in the interfaces?
    assert 'Ethernet0/1' in vlan_10_interfaces, "Ethernet0/1 missing from VLAN 10!"
    # '.keys()' gives us interface names, we check if one exists
```

**Run all tests with:**

```bash
pytest test_vlan_validation.py -v
# Output:
# test_vlan_exists PASSED
# test_vlan_has_name PASSED  
# test_vlan_has_interfaces PASSED
# ============ 3 passed in 0.23s ============
```

**Understanding the Test Flow:**

1. **pytest discovers** `test_*.py` files
2. **Fixtures run first** — `testbed` fixture loads testbed.yaml once
3. **For each test:**
    - `device` fixture connects to switch-01
    - Test function runs with device parameter
    - Assertions check conditions
    - Fixture cleanup disconnects
4. **Results reported** — PASSED, FAILED, or ERROR

**Key Concept — Fixtures:**

- Fixtures are setup functions (database, connections, test data)
- Mark with `@pytest.fixture` decorator
- Referenced by test function parameter names
- PyATS uses fixtures to manage device connections efficiently

---

## Before/After Pattern: The Game Changer

This is the pattern that makes PyATS powerful for automation validation:

### Step 1: Baseline (Before Automation)

```python
def capture_baseline(device):
    """
    Capture network state BEFORE automation runs
    This becomes our "truth" for comparison later
    """
    routes = device.parse('show ip route')
    bgp = device.parse('show ip bgp summary')
    
    # Create dictionary to store baseline measurements
    baseline = {
        # Count how many VLANs exist right now
        'vlan_count': len(device.parse('show vlan')['vlans']),
        # Explanation: device.parse() returns dict, ['vlans'] is the vlans section
        # len() counts how many VLAN IDs (keys in the vlans dictionary)
        
        # Store the IPv4 routing table before changes
        'routes': routes['vrf']['default']['address_family']['ipv4']['routes'],
        # Navigate Genie route structure: vrf → address_family → routes
        
        # Count how many interfaces are operationally up
        'interfaces_up': count_up_interfaces(device),
        # Helper function to count up interfaces (defined below)
        
        # Store BGP neighbor information
        'bgp_neighbors': bgp['vrf']['default']['neighbor'],
        # Navigating Genie BGP structure: vrf → neighbor
    }
    return baseline
    # Return dict for comparison after automation runs

def count_up_interfaces(device):
    """Helper function: Count interfaces that are operationally up"""
    # Parse show interfaces output
    interfaces = device.parse('show interfaces')
    
    # Count how many have oper_status == 'up'
    # Using list comprehension: [name for name, data in interfaces.items() if condition]
    up_count = len([
        name for name, data in interfaces.items()
        if data.get('oper_status') == 'up'
    ])
    # .items() gives us (interface_name, interface_data) tuples
    # .get('oper_status') safely accesses key (returns None if missing)
    # if condition filters only those that are 'up'
    # len() counts how many match
    
    return up_count
```

**What capture_baseline() does:**

- Takes snapshot of network state before automation
- Stores measurements: VLAN count, routes, interface states, BGP neighbors
- Returns dict that we'll compare against after automation

**Why each measurement matters:**

- `vlan_count` — Proves we created the right number of VLANs
- `routes` — Proves routing table wasn't accidentally modified
- `interfaces_up` — Proves no interfaces went down unexpectedly
- `bgp_neighbors` — Proves BGP sessions are still established

### Step 2: Run Automation

```python
def run_automation(device):
    """
    Your actual automation code
    This runs AFTER baseline capture, BEFORE validation
    """
    from netmiko import ConnectHandler
    
    # Connect via Netmiko for configuration capability
    # We use Netmiko here because it's optimized for config commands
    # We use PyATS for parsing (read-only), Netmiko for configs (write)
    conn = ConnectHandler(
        device_type='cisco_ios',
        # Device type tells Netmiko how to communicate with this device
        
        host=device.connections.cli.ip,
        # Get device IP from PyATS device object
        # device.connections.cli is the connection object, .ip is the IP address
        
        username='admin',
        password='...',
        # Credentials (in production, get from testbed or vault)
    )
    
    # Your automation commands
    conn.send_config_set([
        # List of configuration commands to send
        'vlan 100',
        'name PROD-VLAN',
        'vlan 101',
        'name PROD-VLAN-2',
        # Each string is a command. Netmiko sends them sequentially
        # Netmiko waits for device prompts so next command doesn't send too early
    ])
    
    # Always disconnect Netmiko connection when done
    conn.disconnect()
    # Important: Don't reuse Netmiko connections, create fresh ones per automation
```

**Why separate Netmiko from PyATS:**

- **Netmiko:** Best for pushing configs (send_command, send_config_set)
- **PyATS:** Best for parsing device state (parse, structured data)
- Use each for what it's designed for

### Step 3: Validate (After Automation)

```python
def validate_automation(device, baseline):
    """
    Capture network state AFTER automation and compare to baseline
    Returns validation results showing what passed/failed
    """
    routes = device.parse('show ip route')
    
    # Capture state after automation
    after = {
        # Same measurements as baseline
        'vlan_count': len(device.parse('show vlan')['vlans']),
        'routes': routes['vrf']['default']['address_family']['ipv4']['routes'], 
        'interfaces_up': count_up_interfaces(device),
        # Now we can compare these to baseline values
    }
    
    # Assert expectations — if these fail, automation failed
    
    # Check 1: Did we create 2 new VLANs?
    # Expected 2 more VLANs than baseline
    assert after['vlan_count'] == baseline['vlan_count'] + 2, \
        f"VLAN count mismatch! " \
        f"Expected {baseline['vlan_count'] + 2}, " \
        f"got {after['vlan_count']}"
        # Error message shows actual vs expected
    
    # Check 2: Are the new VLANs actually there?
    vlan_data = device.parse('show vlan')['vlans']
    # Get VLAN data after automation
    
    assert '100' in vlan_data, "VLAN 100 not found!"
    # Check VLAN 100 exists
    
    assert '101' in vlan_data, "VLAN 101 not found!"
    # Check VLAN 101 exists
    
    # Check 3: Did any interfaces go down unexpectedly?
    # Should have same number of up interfaces
    assert after['interfaces_up'] == baseline['interfaces_up'], \
        f"Interfaces went down! " \
        f"Before: {baseline['interfaces_up']}, " \
        f"After: {after['interfaces_up']}"
    
    return after
    # Return after-state for reporting or further analysis
```

**Why each assertion matters:**

1. **vlan_count mismatch** — Catches if fewer VLANs created than expected
2. **VLAN doesn't exist** — Catches if VLAN created but already deleted
3. **Interfaces down** — Catches unexpected side effects from configuration

### Step 4: Complete Test

```python
def test_vlan_provisioning_with_validation(testbed):
    """
    Complete before/after validation test
    Shows the full workflow: baseline → automation → validation
    """
    
    device = testbed.devices['switch-01']
    device.connect()
    # Connect to device using PyATS
    
    # BEFORE: Capture baseline
    baseline = capture_baseline(device)
    # Capture current network state
    
    print(f"Baseline: {baseline['vlan_count']} VLANs exist")
    # Show baseline for debugging
    
    # DURING: Run automation
    run_automation(device)
    # Configure new VLANs via Netmiko
    
    # AFTER: Validate results
    after = validate_automation(device, baseline)
    # Compare states, run assertions
    
    # Report results
    print(f"✅ Validation passed!")
    print(f"   VLANs: {baseline['vlan_count']} → {after['vlan_count']}")
    print(f"   Interfaces up: {baseline['interfaces_up']} (no change)")
    
    device.disconnect()
    # Clean up connection
```

**What happens here:**

1. Connect to device
2. Capture baseline (VLAN count, interfaces up, routes, etc.)
3. Run automation (create VLANs)
4. Capture after-state
5. Compare: after-state should equal baseline + expected changes
6. If any assertion fails, test fails (automation failed)
7. If all pass, automation succeeded (with proof)

**Result:** Proof that your automation worked. Not assumption. Proof.

---

## Installation & Setup

### Step 1: Install PyATS

```bash
pip install pyats
# This installs PyATS and dependencies (genie, netmiko, etc.)
# Genie is the parser library that converts output to structured data
```

### Step 2: Create Testbed File

Create `testbed.yaml`:

```yaml
testbed:
  name: "Lab Network"
  # Testbed name — identifies this set of devices

devices:
  csr1000v:
    # Device name — referenced in code as testbed.devices['csr1000v']
    
    type: router
    # Device type (router, switch, firewall, etc.)
    
    os: iosxe
    # OS determines parser used
    # Genie has separate parsers for: ios, iosxe, nxos, ios-xr, junos, etc.
    
    connections:
      cli:
        protocol: ssh
        # Protocol to use for connection (ssh recommended, telnet legacy)
        
        ip: 192.168.1.10
        # Device IP or hostname
        
        port: 22
        # SSH port (default 22)
        
        credentials:
          default:
            # Credential set name — can have multiple (primary, secondary, etc.)
            
            username: admin
            # Username for device login
            
            password: !vault |
              # Ansible Vault encrypted password (secure, not plaintext)
              # See Step 3 below for how to create this
              $ANSIBLE_VAULT;1.2;AES256;default
              # Your encrypted password here
```

### Step 3: Store Credentials Securely

PyATS integrates with Ansible Vault for credential encryption:

```bash
# Encrypt a password interactively
ansible-vault encrypt_string
# Enter password when prompted: (type your device password and hit Enter twice)
# Output:
# !vault |
#   $ANSIBLE_VAULT;1.2;AES256;default
#   ...long encrypted string...
# Vault password: (enter vault password)

# Copy entire "!vault |" block into testbed.yaml
```

**Why encrypt credentials?**

- ❌ **Bad:** `password: admin123` visible to anyone with file access
- ✅ **Good:** `password: !vault |...` encrypted, only decryptable with vault password
- PyATS automatically handles decryption at runtime

**At runtime, PyATS asks for vault password:**

```bash
pytest test_vlan_validation.py -v
# Vault password: (type vault password when prompted)
# PyATS decrypts testbed credentials and connects to devices
```

### Step 4: Test Connection

```python
from pyats.topology import loader

# Load testbed — parses YAML and creates device objects
testbed = loader.load('testbed.yaml')

# Get device by name (must match testbed.yaml)
device = testbed.devices['csr1000v']

# Connect to device
# PyATS uses credentials from testbed.yaml
# Decrypts vault-encrypted password automatically
device.connect()

# Verify connection successful
print(f"✅ Connected to {device.name}")
# device.name is hostname or device name from testbed

# Always disconnect when done
device.disconnect()
```

**What happens during device.connect():**

1. PyATS reads connection settings from testbed.yaml
2. Gets device IP, username, password
3. Automatically decrypts vault password
4. Initiates SSH session
5. Logs in to device
6. Ready for parsing and commands

---

## Real-World Example: Validate a Configuration Change

### Scenario

You've written Netmiko automation to configure a new interface. You want proof it worked.

### The Test

```python
import pytest
from pyats.topology import loader
from netmiko import ConnectHandler

@pytest.fixture
def testbed():
    return loader.load('testbed.yaml')

@pytest.fixture
def device(testbed):
    dev = testbed.devices['csr1000v']
    dev.connect()
    yield dev
    dev.disconnect()

def test_interface_configuration(device):
    """
    Scenario: Configure Ethernet0/1 with IP 10.0.1.1/24
    Validate: Interface exists, has correct IP, is up
    """
    
    # Connect via Netmiko to configure
    from netmiko import ConnectHandler
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        host=device.connections.cli.ip,
        username='admin',
        password=device.credentials['default'].password,
    )
    
    # Run configuration commands
    commands = [
        'interface Ethernet0/1',
        'ip address 10.0.1.1 255.255.255.0',
        'no shutdown',
    ]
    net_connect.send_config_set(commands)
    net_connect.disconnect()
    
    # NOW VALIDATE WITH PYATS
    # Parse interface configuration
    interfaces = device.parse('show interfaces')
    eth01 = interfaces.get('Ethernet0/1', {})
    
    # Validate interface exists
    assert eth01, "Ethernet0/1 not found!"
    
    # Validate interface is up
    assert eth01.get('enabled') == True, "Interface not enabled!"
    assert eth01.get('oper_status') == 'up', "Interface not up!"
    
    # Parse IP address
    ip_config = device.parse('show ip interface Ethernet0/1')
    ip_addr = ip_config['Ethernet0/1']['ipv4']['10.0.1.1']['ip']
    
    # Validate IP address
    assert ip_addr == '10.0.1.1', f"IP mismatch! Got {ip_addr}"
    
    print("✅ Validation passed: Interface configured correctly")
```

Run this test:

```bash
pytest test_interface_config.py -v

# Output:
# test_interface_configuration PASSED
# ✅ Validation passed: Interface configured correctly
```

---

## Key Takeaways

- ✅ **PyATS is Cisco-native** — Built by engineers who understand network devices
- ✅ **Millions of tests/month** — If Cisco trusts it at that scale, so should you
- ✅ **Before/After validation** — Prove your automation actually worked
- ✅ **No more guessing** — Replace "I think it worked" with "The automation passed 47 validation tests"
- ✅ **Integrates with PRIME Framework** — Perfect fit for Implement and Measure stages
- ✅ **Teams understand it** — Your operations team can write tests too (with knowledge transfer)

---

## Next Steps

1. **[PyATS for Network Validation](./pyats-network-validation.md)** — Deep dive into device parsing and validation patterns
2. **[Building Reliable Automation with PyATS](./building-reliable-automation-with-pyats.md)** — Integration into your automation workflow
3. **[PyATS Documentation](https://pubhub.devnetcloud.com/media/pyats/docs/)** — Official Cisco docs

Or jump straight to:

- **[Nornir Fundamentals](./nornir-fundamentals.md)** — Framework for parallel automation execution
- **[Health Checks and Pre-Flight Validation](./health-checks-pre-flight-validation.md)** — Understand how structured validation prevents failures

---

> **Production automation without validation is guesswork.** PyATS transforms validation from manual checklist to automated proof. Enterprise teams use it millions of times per month for good reason.
