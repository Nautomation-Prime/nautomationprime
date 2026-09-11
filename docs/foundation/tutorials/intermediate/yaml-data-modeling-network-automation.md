---
title: YAML Data Modelling for Network Automation
description: Master YAML for network automation - device inventories, configuration templates, and structured data. Learn syntax, best practices, and real-world patterns.
tags:
  - Intermediate
  - YAML
  - Data Modelling
  - Configuration
  - Best Practices
  - Tutorial
---

## YAML Data Modelling for Network Automation

## "From Hardcoded Values to Structured Data — The Foundation of Scalable Automation"

Every production network automation system relies on **structured data**. Device inventories, configuration templates, credential stores, testbeds—they all use **YAML** (YAML Ain't Markup Language).

**Why YAML dominates network automation:**

- ✅ **Human-readable** — Network engineers can read and edit without programming knowledge
- ✅ **Framework-native** — Nornir inventories, PyATS testbeds, Ansible playbooks all use YAML
- ✅ **Version control friendly** — Plain text format works perfectly with Git
- ✅ **Supports complex structures** — Nested data, lists, dictionaries without JSON's noise
- ✅ **Comments allowed** — Document your data inline (JSON can't do this)

If you're hardcoding IPs, credentials, or configuration values in Python scripts, you're doing it wrong. This tutorial teaches you the right way.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ YAML syntax fundamentals (scalars, lists, dictionaries, nested structures)
- ✅ Reading and writing YAML in Python
- ✅ Nornir inventory structure (hosts, groups, defaults)
- ✅ PyATS testbed structure (devices, connections, credentials)
- ✅ Configuration data modelling best practices
- ✅ Common YAML pitfalls and how to avoid them
- ✅ Real-world patterns used in production automation
- ✅ Validating YAML structure programmatically

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [Beginner Tutorials](../beginner/index.md)** — Familiar with Python dictionaries and lists
- ✅ Understanding of Python data structures (dict, list, str)
- ✅ Basic text editor skills

### Required Software

```bash
# Create a virtual environment
python -m venv yaml_venv
source yaml_venv/bin/activate
# Windows PowerShell: .\yaml_venv\Scripts\Activate.ps1
# Windows CMD: yaml_venv\Scripts\activate.bat

# Install required packages
pip install pyyaml netmiko nornir pyats
```

### Required Access

- No device access required for this tutorial (we'll work with files and Python)

---

## 📖 YAML Fundamentals: Understanding the Syntax

### What is YAML?

YAML is a **data serialization language**—it converts human-readable text into data structures (dictionaries, lists) that programs can use.

**Example:** Instead of this Python code:

```python
devices = {
    'router1': {
        'ip': '10.1.1.1',
        'username': 'admin',
        'device_type': 'cisco_ios'
    },
    'router2': {
        'ip': '10.1.1.2',
        'username': 'admin',
        'device_type': 'cisco_ios'
    }
}
```

Write this YAML file:

```yaml
router1:
  ip: 10.1.1.1
  username: admin
  device_type: cisco_ios
router2:
  ip: 10.1.1.2
  username: admin
  device_type: cisco_ios
```

**Result:** Cleaner, more readable, editable without Python knowledge.

---

## 🔧 YAML Syntax: Core Concepts

### 1. Scalars (Single Values)

Scalars are simple values: strings, numbers, booleans.

```yaml
---
# String (no quotes needed for simple strings)
hostname: router1

# Number (integer)
vlan_id: 100

# Number (float)
timeout: 5.5

# Boolean
enabled: true
admin_mode: false

# String with special characters (quotes required)
password: "P@ssw0rd!"

# String with spaces (quotes required)
description: "Main office router"

# Null value
bgp_asn: null
```

**Key rules:**

- Strings usually don't need quotes (unless they contain special characters)
- Numbers are automatically typed (int vs float)
- Booleans: `true`, `false`, `yes`, `no`, `on`, `off`
- `null` represents no value

---

### 2. Lists (Arrays)

Lists are collections of items, denoted with `-` (dash).

```yaml
---
# List of strings
vlans:
  - 10
  - 20
  - 30
  - 40

# List of dictionaries (more complex)
interfaces:
  - name: GigabitEthernet0/0
    ip: 10.1.1.1
    subnet: 255.255.255.0
  - name: GigabitEthernet0/1
    ip: 10.1.2.1
    subnet: 255.255.255.0

# Inline list syntax (less common)
allowed_vlans: [10, 20, 30, 40]
```

**Python equivalent:**

```python
vlans = [10, 20, 30, 40]

interfaces = [
    {'name': 'GigabitEthernet0/0', 'ip': '10.1.1.1', 'subnet': '255.255.255.0'},
    {'name': 'GigabitEthernet0/1', 'ip': '10.1.2.1', 'subnet': '255.255.255.0'}
]
```

---

### 3. Dictionaries (Mappings)

Dictionaries are key-value pairs, using `key: value` format.

```yaml
---
# Simple dictionary
device:
  hostname: router1
  ip: 10.1.1.1
  os: ios

# Nested dictionary
device_config:
  basic:
    hostname: core-router-01
    domain: example.com
  interfaces:
    management:
      name: GigabitEthernet0/0
      ip: 192.168.1.1
```

**Python equivalent:**

```python
device = {
    'hostname': 'router1',
    'ip': '10.1.1.1',
    'os': 'ios'
}

device_config = {
    'basic': {
        'hostname': 'core-router-01',
        'domain': 'example.com'
    },
    'interfaces': {
        'management': {
            'name': 'GigabitEthernet0/0',
            'ip': '192.168.1.1'
        }
    }
}
```

---

### 4. Nested Structures (Real-World Pattern)

Combine lists and dictionaries to model complex data:

```yaml
---
# Network inventory with nested structure
network:
  datacenters:
    dc1:
      location: "New York"
      devices:
        - hostname: nyc-core-01
          ip: 10.1.1.1
          type: router
          vlans: [10, 20, 30]
        - hostname: nyc-core-02
          ip: 10.1.1.2
          type: router
          vlans: [10, 20, 30]
    dc2:
      location: "Los Angeles"
      devices:
        - hostname: la-core-01
          ip: 10.2.1.1
          type: router
          vlans: [40, 50, 60]
```

**What this represents:**

- Network has multiple datacenters
- Each datacenter has location and devices
- Each device has hostname, IP, type, and VLANs

**Python access:**

```python
data['network']['datacenters']['dc1']['devices'][0]['hostname']
# Returns: 'nyc-core-01'
```

---

## 🐍 Reading YAML in Python

### Basic YAML Loading

```python
#!/usr/bin/env python3
"""
Read YAML file and convert to Python data structures
"""

import yaml

# Read YAML file
with open('devices.yaml', 'r') as file:
    data = yaml.safe_load(file)
    # safe_load() parses YAML and returns Python dict/list
    # Always use safe_load() (not load()) for security

# Access the data
print(f"Router 1 IP: {data['router1']['ip']}")
print(f"Router 2 Username: {data['router2']['username']}")

# Iterate through devices
for device_name, device_info in data.items():
    print(f"Device: {device_name}")
    print(f"  IP: {device_info['ip']}")
    print(f"  Type: {device_info['device_type']}")
```

**Why `safe_load()` not `load()`:**

- `safe_load()` only parses standard YAML (safe)
- `load()` can execute arbitrary Python code (security risk)
- Always use `safe_load()` unless you have a specific reason not to

---

### Handling Complex Structures

```python
#!/usr/bin/env python3
"""
Read nested YAML and extract specific data
"""

import yaml

# Sample YAML file: network_inventory.yaml
yaml_content = """
---
datacenters:
  dc1:
    location: "New York"
    devices:
      - hostname: nyc-core-01
        ip: 10.1.1.1
        vlans: [10, 20, 30]
      - hostname: nyc-core-02
        ip: 10.1.1.2
        vlans: [10, 20, 30]
"""

# Parse YAML
data = yaml.safe_load(yaml_content)

# Navigate nested structure
dc1_location = data['datacenters']['dc1']['location']
print(f"DC1 Location: {dc1_location}")

# Access list items
for device in data['datacenters']['dc1']['devices']:
    print(f"\nDevice: {device['hostname']}")
    print(f"  IP: {device['ip']}")
    print(f"  VLANs: {', '.join(map(str, device['vlans']))}")
```

**Output:**

```
DC1 Location: New York

Device: nyc-core-01
  IP: 10.1.1.1
  VLANs: 10, 20, 30

Device: nyc-core-02
  IP: 10.1.1.2
  VLANs: 10, 20, 30
```

---

## 📄 Writing YAML in Python

### Creating YAML from Python Data

```python
#!/usr/bin/env python3
"""
Convert Python data structures to YAML files
"""

import yaml

# Python data structure
devices = {
    'router1': {
        'ip': '10.1.1.1',
        'username': 'admin',
        'device_type': 'cisco_ios',
        'vlans': [10, 20, 30]
    },
    'router2': {
        'ip': '10.1.1.2',
        'username': 'admin',
        'device_type': 'cisco_ios',
        'vlans': [10, 20, 30]
    }
}

# Write to YAML file
with open('devices_output.yaml', 'w') as file:
    yaml.dump(devices, file, default_flow_style=False, sort_keys=False)
    # default_flow_style=False makes output readable (not inline)
    # sort_keys=False preserves key order

print("✓ YAML file created: devices_output.yaml")
```

**Generated YAML:**

```yaml
router1:
  ip: 10.1.1.1
  username: admin
  device_type: cisco_ios
  vlans:
  - 10
  - 20
  - 30
router2:
  ip: 10.1.1.2
  username: admin
  device_type: cisco_ios
  vlans:
  - 10
  - 20
  - 30
```

---

## 🏗️ Real-World Pattern 1: Nornir Inventory

Nornir uses YAML for device inventory management. Understanding this structure is critical for Nornir automation.

### Nornir Inventory Structure

Nornir uses three YAML files:

1. **hosts.yaml** — Individual device definitions
2. **groups.yaml** — Device groupings with shared settings
3. **defaults.yaml** — Default values applied to all devices

### hosts.yaml

```yaml
---
# Individual device definitions
router1:
  hostname: 10.1.1.1
  # IP address or DNS name for SSH connection

  groups:
    - ios_routers
  # Device belongs to ios_routers group (inherits settings)

  data:
    # Custom data specific to this device
    device_type: cisco_ios
    location: "New York"
    is_production: true

switch1:
  hostname: 10.1.1.10
  groups:
    - ios_switches
  data:
    device_type: cisco_ios
    location: "New York"
    vlan_range: "1-100"

router2:
  hostname: 10.2.1.1
  groups:
    - ios_routers
  data:
    device_type: cisco_ios
    location: "Los Angeles"
    is_production: false
```

**Key concepts:**

- Device name (e.g., `router1`) is the unique identifier
- `hostname` is the actual IP/DNS for connection
- `groups` assigns device to group (inherits credentials, settings)
- `data` stores custom fields (access via `host.data['location']`)

### groups.yaml

```yaml
---
# Group definitions with shared settings
ios_routers:
  username: admin
  password: ""  # Will be set at runtime (security)
  data:
    connection_timeout: 30
    enable_password: ""

ios_switches:
  username: switch_admin
  password: ""
  data:
    connection_timeout: 20
    enable_password: ""

nxos_devices:
  username: nxos_admin
  password: ""
  data:
    device_type: cisco_nxos
    connection_timeout: 30
```

**Key concepts:**

- Groups define shared settings (credentials, timeouts)
- Devices inherit from groups they belong to
- Password left blank (set at runtime for security)

### defaults.yaml

```yaml
---
# Default values applied to ALL devices
data:
  connection_timeout: 15
  # Default SSH timeout if not specified elsewhere

  auth_timeout: 10
  # Default authentication timeout

  read_timeout: 30
  # Default command read timeout

  ssh_config_file: null
  # No custom SSH config by default
```

**Key concepts:**

- Applies to all devices unless overridden
- Useful for organisation-wide standards

### Using Nornir Inventory in Python

```python
#!/usr/bin/env python3
"""
Use Nornir inventory from YAML files
"""

from nornir import InitNornir
from nornir.core.filter import F

# Initialize Nornir with config file
nr = InitNornir(config_file="nornir_config.yaml")

# Access device data
router1 = nr.inventory.hosts['router1']

print(f"Device: {router1.name}")
print(f"Hostname: {router1.hostname}")
print(f"Location: {router1.data['location']}")
print(f"Username: {router1.username}")  # Inherited from group

# Filter devices by group
ios_devices = nr.filter(F(groups__contains="ios_routers"))
print(f"\nFound {len(ios_devices.inventory.hosts)} IOS routers")

# Filter devices by custom data
prod_devices = nr.filter(lambda h: h.data.get('is_production') == True)
print(f"Found {len(prod_devices.inventory.hosts)} production devices")
```

---

## 🔬 Real-World Pattern 2: PyATS Testbed

PyATS uses YAML to define network testbeds (device topology and connectivity).

### PyATS Testbed Structure

```yaml
---
testbed:
  name: "Production Network"
  # Testbed identifier

devices:
  csr1000v:
    # Device name (referenced as testbed.devices['csr1000v'])

    type: router
    # Device type (router, switch, firewall, etc.)

    os: iosxe
    # Operating system (determines parser)

    connections:
      # Multiple connection types supported

      cli:
        # Command-line interface connection
        protocol: ssh
        ip: 192.168.1.10
        port: 22

        credentials:
          default:
            # Primary credential set
            username: admin
            password: !vault |
              # Ansible Vault encrypted password
              $ANSIBLE_VAULT;1.2;AES256;default
              # Encrypted password here

      netconf:
        # NETCONF connection (if supported)
        protocol: netconf
        ip: 192.168.1.10
        port: 830

        credentials:
          default:
            username: admin
            password: !vault |
              # Same password, encrypted

  nexus9k:
    type: switch
    os: nxos

    connections:
      cli:
        protocol: ssh
        ip: 192.168.1.20
        port: 22

        credentials:
          default:
            username: admin
            password: !vault |
              # Encrypted password

          backup:
            # Backup credential set
            username: backup_user
            password: !vault |
              # Different credentials
```

**Key concepts:**

- Each device can have multiple connection types (cli, netconf, restconf)
- Credentials encrypted with Ansible Vault (secure)
- Multiple credential sets supported (primary, backup)

### Using PyATS Testbed in Python

```python
#!/usr/bin/env python3
"""
Load PyATS testbed and connect to devices
"""

from pyats.topology import loader

# Load testbed from YAML
testbed = loader.load('testbed.yaml')

# Access device
device = testbed.devices['csr1000v']

# Connect to device
device.connect()
print(f"✓ Connected to {device.name}")

# Parse device output
output = device.parse('show version')
print(f"Device version: {output['version']['version']}")

# Disconnect
device.disconnect()
```

---

## 🏭 Real-World Pattern 3: Configuration Data Modelling

Model configuration data in YAML for template-driven automation.

### VLAN Configuration Data

```yaml
---
# VLAN definitions for network-wide deployment
vlans:
  - id: 10
    name: DATA
    description: "Corporate data network"
    enabled: true

  - id: 20
    name: VOICE
    description: "VoIP phones"
    enabled: true

  - id: 30
    name: GUEST
    description: "Guest wireless"
    enabled: true

  - id: 99
    name: MGMT
    description: "Management network"
    enabled: true

# Interface assignments
interface_assignments:
  GigabitEthernet0/1:
    mode: access
    vlan: 10
    description: "Data port - Workstation"

  GigabitEthernet0/2:
    mode: access
    vlan: 20
    description: "Voice port - IP Phone"

  GigabitEthernet0/24:
    mode: trunk
    allowed_vlans: [10, 20, 30, 99]
    description: "Trunk to distribution switch"
```

### Using Configuration Data in Python

```python
#!/usr/bin/env python3
"""
Generate Cisco configuration from YAML data
"""

import yaml
from netmiko import ConnectHandler

# Load YAML configuration data
with open('vlan_config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)

# Connect to device
device = ConnectHandler(
    device_type='cisco_ios',
    host='10.1.1.1',
    username='admin',
    password='password'
)

# Generate VLAN configuration commands
vlan_commands = []
for vlan in config_data['vlans']:
    if vlan['enabled']:
        vlan_commands.extend([
            f"vlan {vlan['id']}",
            f"name {vlan['name']}"
        ])

# Generate interface configuration commands
interface_commands = []
for interface, config in config_data['interface_assignments'].items():
    interface_commands.append(f"interface {interface}")
    interface_commands.append(f"description {config['description']}")

    if config['mode'] == 'access':
        interface_commands.extend([
            "switchport mode access",
            f"switchport access vlan {config['vlan']}"
        ])
    elif config['mode'] == 'trunk':
        vlans_str = ','.join(map(str, config['allowed_vlans']))
        interface_commands.extend([
            "switchport mode trunk",
            f"switchport trunk allowed vlan {vlans_str}"
        ])

# Deploy configuration
print("Deploying VLAN configuration...")
output = device.send_config_set(vlan_commands)
print(output)

print("\nDeploying interface configuration...")
output = device.send_config_set(interface_commands)
print(output)

device.disconnect()
print("\n✓ Configuration deployed successfully")
```

**Why this pattern works:**

- Configuration data separated from code
- Easy to modify VLANs without changing Python script
- Version control tracks configuration changes
- Non-programmers can edit YAML

---

## ⚠️ Common YAML Pitfalls & How to Avoid Them

### Pitfall 1: Indentation Errors

**Wrong:**

```yaml
devices:
  router1:
  hostname: 10.1.1.1  # ✗ Wrong indentation
    ip: 10.1.1.1
```

**Right:**

```yaml
devices:
  router1:
    hostname: 10.1.1.1  # ✓ Correct indentation
    ip: 10.1.1.1
```

**Rule:** Always use 2 spaces for indentation (not tabs, not 4 spaces).

---

### Pitfall 2: Unquoted Special Characters

**Wrong:**

```yaml
password: P@ssw0rd!  # ✗ @ and ! are special characters
description: Device: Core Router  # ✗ Colon without quotes
```

**Right:**

```yaml
password: "P@ssw0rd!"  # ✓ Quoted
description: "Device: Core Router"  # ✓ Quoted
```

**Rule:** Use quotes for strings with special characters (`:`, `@`, `!`, `#`, `%`, etc.).

---

### Pitfall 3: Boolean Confusion

**Wrong:**

```yaml
enabled: yes  # Works but inconsistent
admin: on     # Works but inconsistent
debug: true   # Works but different style
```

**Right:**

```yaml
enabled: true   # ✓ Consistent
admin: true     # ✓ Consistent
debug: true     # ✓ Consistent
```

**Rule:** Use `true`/`false` for consistency (avoid `yes`/`no`, `on`/`off`).

---

### Pitfall 4: Missing Document Separator

**Wrong:**

```yaml
device: router1  # No document separator
hostname: 10.1.1.1
```

**Right:**

```yaml
---
device: router1  # ✓ Document separator
hostname: 10.1.1.1
```

**Rule:** Always start YAML files with `---` (document separator).

---

### Pitfall 5: Duplicate Keys

**Wrong:**

```yaml
device:
  hostname: router1
  hostname: router2  # ✗ Duplicate key (only last value used)
```

**Right:**

```yaml
device:
  hostname: router1  # ✓ Unique key
  backup_hostname: router2
```

**Rule:** Each key must be unique within its scope.

---

## 🧪 Validating YAML Structure

### Validation Script

```python
#!/usr/bin/env python3
"""
Validate YAML files before using them in automation
"""

import yaml
import sys

def validate_yaml_file(filepath):
    """
    Validate YAML file syntax and structure
    Returns True if valid, False otherwise
    """
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)

        # Check if data was parsed
        if data is None:
            print(f"✗ {filepath}: File is empty or invalid")
            return False

        # Type check (expecting dict for most network configs)
        if not isinstance(data, dict):
            print(f"⚠ {filepath}: Root element is not a dictionary")

        print(f"✓ {filepath}: Valid YAML")
        return True

    except yaml.YAMLError as e:
        print(f"✗ {filepath}: YAML syntax error")
        print(f"  Error: {e}")
        return False
    except FileNotFoundError:
        print(f"✗ {filepath}: File not found")
        return False
    except Exception as e:
        print(f"✗ {filepath}: Unexpected error")
        print(f"  Error: {e}")
        return False

def validate_nornir_inventory(hosts_file, groups_file, defaults_file):
    """
    Validate Nornir inventory structure
    """
    print("Validating Nornir inventory...")

    # Validate each file
    if not validate_yaml_file(hosts_file):
        return False
    if not validate_yaml_file(groups_file):
        return False
    if not validate_yaml_file(defaults_file):
        return False

    # Load and check structure
    with open(hosts_file) as f:
        hosts = yaml.safe_load(f)

    # Check hosts have required fields
    for host_name, host_data in hosts.items():
        if 'hostname' not in host_data:
            print(f"✗ Host '{host_name}' missing 'hostname' field")
            return False

    print("✓ Nornir inventory structure valid")
    return True

if __name__ == "__main__":
    # Validate single file
    validate_yaml_file('devices.yaml')

    # Validate Nornir inventory
    validate_nornir_inventory(
        'inventory/hosts.yaml',
        'inventory/groups.yaml',
        'inventory/defaults.yaml'
    )
```

**Run validation:**

```bash
python validate_yaml.py
```

---

## 🎓 Best Practices for Network Automation

### 1. Separate Data from Code

**Bad:**

```python
# Hardcoded in Python
devices = {
    'router1': {'ip': '10.1.1.1', 'username': 'admin'},
    'router2': {'ip': '10.1.1.2', 'username': 'admin'}
}
```

**Good:**

```yaml
# devices.yaml
---
router1:
  ip: 10.1.1.1
  username: admin
router2:
  ip: 10.1.1.2
  username: admin
```

```python
# Load from YAML
with open('devices.yaml') as f:
    devices = yaml.safe_load(f)
```

---

### 2. Use Comments Liberally

```yaml
---
# Production datacenter devices
# Last updated: 2026-03-12
# Contact: network-team@example.com

devices:
  router1:
    hostname: 10.1.1.1  # Primary WAN router
    location: "NYC DC1"

  router2:
    hostname: 10.1.1.2  # Backup WAN router
    location: "NYC DC1"
```

---

### 3. Version Control Your YAML

```bash
git add inventory/
git commit -m "Added router3 to NYC datacenter inventory"
git push
```

**Benefits:**

- Track changes over time
- Rollback if needed
- Audit trail for compliance

---

### 4. Validate Before Deployment

```python
# Always validate YAML before using it
try:
    with open('devices.yaml') as f:
        devices = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"✗ YAML error: {e}")
    sys.exit(1)

# Proceed with automation...
```

---

### 5. Never Store Passwords in Plain Text

**Bad:**

```yaml
credentials:
  username: admin
  password: MyPassword123  # ✗ Plain text password
```

**Good:**

```yaml
credentials:
  username: admin
  password: ""  # Set at runtime or use vault
```

```python
import getpass

# Prompt for password at runtime
password = getpass.getpass("Enter device password: ")
```

Or use Ansible Vault:

```yaml
credentials:
  username: admin
  password: !vault |
    $ANSIBLE_VAULT;1.2;AES256
    # Encrypted password
```

---

## 🚀 Complete Working Example: Network Inventory System

### Project Structure

```text
network-inventory/
├── inventory/
│   ├── hosts.yaml
│   ├── groups.yaml
│   └── defaults.yaml
├── config/
│   └── vlan_config.yaml
├── scripts/
│   ├── load_inventory.py
│   └── validate_yaml.py
└── README.md
```

### inventory/hosts.yaml

```yaml
---
# Network device inventory
router1:
  hostname: 10.1.1.1
  groups:
    - ios_routers
    - production
  data:
    location: "NYC-DC1"
    rack: "A-01"

router2:
  hostname: 10.1.1.2
  groups:
    - ios_routers
    - production
  data:
    location: "NYC-DC1"
    rack: "A-02"

switch1:
  hostname: 10.1.1.10
  groups:
    - ios_switches
    - production
  data:
    location: "NYC-DC1"
    rack: "A-03"
```

### inventory/groups.yaml

```yaml
---
# Device groups with shared settings
ios_routers:
  username: router_admin
  data:
    device_type: cisco_ios
    connection_timeout: 30

ios_switches:
  username: switch_admin
  data:
    device_type: cisco_ios
    connection_timeout: 20

production:
  data:
    backup_schedule: "daily"
    monitoring: true
```

### inventory/defaults.yaml

```yaml
---
# Default values applied to all devices
data:
  auth_timeout: 10
  read_timeout: 30
```

### scripts/load_inventory.py

```python
#!/usr/bin/env python3
"""
Load and display network inventory from YAML
"""

import yaml
from pathlib import Path

def load_inventory():
    """Load Nornir-style inventory from YAML files"""

    # Load hosts
    with open('inventory/hosts.yaml') as f:
        hosts = yaml.safe_load(f)

    # Load groups
    with open('inventory/groups.yaml') as f:
        groups = yaml.safe_load(f)

    # Load defaults
    with open('inventory/defaults.yaml') as f:
        defaults = yaml.safe_load(f)

    return hosts, groups, defaults

def display_inventory(hosts, groups):
    """Display inventory in human-readable format"""

    print("=" * 70)
    print("NETWORK INVENTORY")
    print("=" * 70)

    for host_name, host_data in hosts.items():
        print(f"\n{host_name}:")
        print(f"  Hostname: {host_data['hostname']}")
        print(f"  Groups: {', '.join(host_data.get('groups', []))}")

        if 'data' in host_data:
            print("  Data:")
            for key, value in host_data['data'].items():
                print(f"    {key}: {value}")

def main():
    """Main function"""
    try:
        hosts, groups, defaults = load_inventory()
        display_inventory(hosts, groups)

        print(f"\n{'=' * 70}")
        print(f"Total devices: {len(hosts)}")
        print(f"Total groups: {len(groups)}")
        print("=" * 70)

    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("  Make sure inventory files exist")
    except yaml.YAMLError as e:
        print(f"✗ YAML error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

**Run the script:**

```bash
python scripts/load_inventory.py
```

**Output:**

```
======================================================================
NETWORK INVENTORY
======================================================================

router1:
  Hostname: 10.1.1.1
  Groups: ios_routers, production
  Data:
    location: NYC-DC1
    rack: A-01

router2:
  Hostname: 10.1.1.2
  Groups: ios_routers, production
  Data:
    location: NYC-DC1
    rack: A-02

switch1:
  Hostname: 10.1.1.10
  Groups: ios_switches, production
  Data:
    location: NYC-DC1
    rack: A-03

======================================================================
Total devices: 3
Total groups: 2
======================================================================
```

---

## 🐛 Troubleshooting

### "YAMLError: mapping values are not allowed here"

**Cause:** Unquoted string with colon

**Fix:**

```yaml
# Wrong
description: Device: Core Router

# Right
description: "Device: Core Router"
```

---

### "YAMLError: expected <block end>, but found"

**Cause:** Indentation error

**Fix:** Use 2 spaces consistently (not tabs, not 4 spaces)

```yaml
# Wrong
device:
    hostname: router1  # 4 spaces

# Right
device:
  hostname: router1  # 2 spaces
```

---

### "AttributeError: 'NoneType' object has no attribute"

**Cause:** Empty or missing YAML file

**Fix:**

```python
with open('devices.yaml') as f:
    data = yaml.safe_load(f)

    # Check if data was loaded
    if data is None:
        print("Error: YAML file is empty")
        sys.exit(1)
```

---

## 📚 Additional Resources

- **[YAML Official Specification](https://yaml.org/spec/)** — Full YAML specification
- **[PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)** — Python YAML library docs
- **[Nornir Inventory Guide](https://nornir.readthedocs.io/en/latest/tutorial/inventory.html)** — Nornir-specific YAML structure
- **[PyATS Testbed Documentation](https://pubhub.devnetcloud.com/media/pyats/docs/topology/creation.html)** — PyATS testbed YAML structure
- **[YAML Validator Online](https://www.yamllint.com/)** — Validate YAML syntax online

---

## 🎯 Key Takeaways

- ✅ **YAML is the standard** for network automation data modelling
- ✅ **Human-readable** format that network engineers can edit without programming
- ✅ **Separation of concerns** — Keep data (YAML) separate from code (Python)
- ✅ **Version control friendly** — Track changes, rollback if needed
- ✅ **Framework-native** — Nornir, PyATS, Ansible all use YAML
- ✅ **Security-conscious** — Never store plaintext passwords, use vaults
- ✅ **Validate before deployment** — Catch syntax errors early

---

## 🎓 Next Steps

You've mastered YAML! Continue your data modelling journey:

1. **[JSON Data Handling for Network Automation](./json-data-handling-network-automation.md)** (Recommended Next)
   - Learn JSON for API interactions
   - REST API responses and structured logging
   - When to use JSON vs YAML

2. **[Jinja2 Configuration Templates](./jinja2-configuration-templates.md)**
   - Combine YAML data with Jinja2 templates
   - Generate device configurations dynamically
   - Template-driven automation patterns

3. **[Nornir Fundamentals](./nornir-fundamentals.md)**
   - Apply YAML inventory in real Nornir automation
   - Parallel execution at scale

4. **[PyATS Fundamentals](./pyats-fundamentals.md)**
   - Use YAML testbeds for network validation
   - Enterprise testing patterns

---

> **Remember:** YAML is the foundation of structured network automation. Master it now, use it everywhere later.

[← Back to Intermediate Tutorials](./index.md) | [Continue to JSON Tutorial →](./json-data-handling-network-automation.md)
