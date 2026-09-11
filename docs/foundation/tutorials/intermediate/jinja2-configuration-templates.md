---
title: Jinja2 Configuration Templates for Network Automation
description: Master Jinja2 templating for Cisco network automation - generate configurations dynamically from data. Learn syntax, filters, inheritance, and production patterns.
tags:
  - Intermediate
  - Jinja2
  - Templates
  - Configuration Management
  - Automation
  - Tutorial
---

## Jinja2 Configuration Templates for Network Automation

## "From Copy-Paste Configs to Data-Driven Generation — Template Everything"

You've mastered YAML for data modelling and JSON for API interactions. Now it's time to learn **Jinja2**—the template engine that transforms your structured data into actual device configurations.

**Why Jinja2 is essential for network automation:**

- ✅ **Generate configurations from data** — Write template once, apply to 1000 devices
- ✅ **Eliminate copy-paste errors** — No more manual find-and-replace
- ✅ **Consistent standards** — Every device gets the same template (with device-specific values)
- ✅ **Version controlled templates** — Track configuration standards over time
- ✅ **Conditional logic** — Different config blocks based on device type, role, location
- ✅ **Python-native** — Integrates seamlessly with your automation workflows

**Real-world impact:** A single Jinja2 template can replace hundreds of static configuration files. Change the template once, regenerate configs for your entire network.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ Jinja2 syntax fundamentals (variables, conditionals, loops, filters)
- ✅ Rendering templates with Python
- ✅ Template inheritance and reusability
- ✅ Advanced filters for network automation
- ✅ Whitespace control for clean configurations
- ✅ Error handling and debugging templates
- ✅ Real-world patterns: VLAN configs, interface templates, ACLs
- ✅ Integration with YAML data sources
- ✅ Production deployment workflows

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [YAML Data Modelling Tutorial](./yaml-data-modeling-network-automation.md)** — Understanding structured data
- ✅ **Completed [JSON Data Handling Tutorial](./json-data-handling-network-automation.md)** — Data serialization
- ✅ Familiarity with Cisco IOS configuration syntax

### Required Software

```bash
# Create a virtual environment
python -m venv jinja2_venv
source jinja2_venv/bin/activate
# Windows PowerShell: .\jinja2_venv\Scripts\Activate.ps1
# Windows CMD: jinja2_venv\Scripts\activate.bat

# Install required packages
pip install jinja2 pyyaml netmiko
```

### Required Access

- No device access required for basic concepts
- Optional: SSH access to test device for deployment examples

---

## 📖 Jinja2 Fundamentals: Understanding Templates

### What is Jinja2?

Jinja2 is a **templating engine**—it takes templates (text with placeholders) and renders them with actual data.

**Example:**

**Template (config_template.j2):**

```jinja2
hostname {{ hostname }}
!
interface {{ interface_name }}
 ip address {{ ip_address }} {{ subnet_mask }}
 no shutdown
```

**Data (Python dict):**

```python
data = {
    'hostname': 'router1',
    'interface_name': 'GigabitEthernet0/0',
    'ip_address': '10.1.1.1',
    'subnet_mask': '255.255.255.0'
}
```

**Rendered Output:**

```
hostname router1
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.0
 no shutdown
```

**Key concept:** `{{ variable }}` gets replaced with actual values from your data.

---

## 🔧 Jinja2 Syntax: Core Concepts

### 1. Variables

Variables are enclosed in double curly braces `{{ }}`.

```jinja2
hostname {{ hostname }}
ip domain-name {{ domain_name }}
```

**Data:**

```python
{
    'hostname': 'core-router-01',
    'domain_name': 'example.com'
}
```

**Output:**

```
hostname core-router-01
ip domain-name example.com
```

---

### 2. Accessing Nested Data

Access nested dictionary values with dot notation or brackets.

```jinja2
hostname {{ device.hostname }}
!
interface {{ device.interfaces.management.name }}
 ip address {{ device.interfaces.management.ip }}
```

**Data:**

```python
{
    'device': {
        'hostname': 'router1',
        'interfaces': {
            'management': {
                'name': 'GigabitEthernet0/0',
                'ip': '192.168.1.1'
            }
        }
    }
}
```

---

### 3. Conditionals

Use `{% if %}` for conditional logic.

```jinja2
hostname {{ hostname }}
!
{% if enable_ssh %}
ip ssh version 2
{% endif %}
!
{% if enable_logging %}
logging buffered {{ log_size }}
logging host {{ syslog_server }}
{% endif %}
```

**Data:**

```python
{
    'hostname': 'router1',
    'enable_ssh': True,
    'enable_logging': True,
    'log_size': 32000,
    'syslog_server': '10.10.10.10'
}
```

**Output:**

```
hostname router1
!
ip ssh version 2
!
logging buffered 32000
logging host 10.10.10.10
```

---

### 4. Loops

Use `{% for %}` to iterate over lists.

```jinja2
hostname {{ hostname }}
!
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
```

**Data:**

```python
{
    'hostname': 'switch1',
    'vlans': [
        {'id': 10, 'name': 'DATA'},
        {'id': 20, 'name': 'VOICE'},
        {'id': 30, 'name': 'GUEST'}
    ]
}
```

**Output:**

```
hostname switch1
!
vlan 10
 name DATA
vlan 20
 name VOICE
vlan 30
 name GUEST
```

---

### 5. Filters

Filters modify variables using the pipe `|` operator.

```jinja2
hostname {{ hostname | upper }}
!
interface {{ interface }}
 description {{ description | default('No description') }}
```

**Common filters:**

- `upper` — Convert to uppercase
- `lower` — Convert to lowercase
- `default(value)` — Provide default if variable is undefined
- `length` — Get length of list/string
- `join(separator)` — Join list items

**Example:**

```jinja2
hostname {{ hostname | upper }}
!
{% for vlan in vlans %}
vlan {{ vlan }}
{% endfor %}
!
! Total VLANs: {{ vlans | length }}
! VLAN list: {{ vlans | join(',') }}
```

**Data:**

```python
{
    'hostname': 'router1',
    'vlans': [10, 20, 30, 40]
}
```

**Output:**

```
hostname ROUTER1
!
vlan 10
vlan 20
vlan 30
vlan 40
!
! Total VLANs: 4
! VLAN list: 10,20,30,40
```

---

## 🐍 Rendering Templates in Python

### Basic Template Rendering

```python
#!/usr/bin/env python3
"""
Render Jinja2 template with Python
"""

from jinja2 import Template

# Define template
template_string = """
hostname {{ hostname }}
!
interface {{ interface }}
 ip address {{ ip }} {{ mask }}
 no shutdown
"""

# Create template object
template = Template(template_string)

# Data to render
data = {
    'hostname': 'router1',
    'interface': 'GigabitEthernet0/0',
    'ip': '10.1.1.1',
    'mask': '255.255.255.0'
}

# Render template
config = template.render(data)

print(config)
```

**Output:**

```
hostname router1
!
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.0
 no shutdown
```

---

### Loading Templates from Files

```python
#!/usr/bin/env python3
"""
Load and render Jinja2 templates from files
"""

from jinja2 import Environment, FileSystemLoader
import yaml

# Create Jinja2 environment
env = Environment(
    loader=FileSystemLoader('templates'),  # Template directory
    trim_blocks=True,      # Remove first newline after block
    lstrip_blocks=True     # Strip leading spaces from blocks
)

# Load template from file
template = env.get_template('router_config.j2')

# Load data from YAML
with open('device_data.yaml') as f:
    data = yaml.safe_load(f)

# Render template
config = template.render(data)

# Save to file
with open(f"configs/{data['hostname']}_config.txt", 'w') as f:
    f.write(config)

print(f"✓ Configuration generated for {data['hostname']}")
```

**Project structure:**

```
project/
├── templates/
│   └── router_config.j2
├── device_data.yaml
├── configs/
└── generate_config.py
```

---

## 🏗️ Real-World Pattern 1: VLAN Configuration

### VLAN Template (templates/vlan_config.j2)

```jinja2
!
! VLAN Configuration
! Generated: {{ generation_date }}
! Device: {{ hostname }}
!
hostname {{ hostname }}
!
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% if vlan.description %}
 description {{ vlan.description }}
{% endif %}
{% endfor %}
!
{% for interface, config in interfaces.items() %}
interface {{ interface }}
{% if config.mode == 'access' %}
 switchport mode access
 switchport access vlan {{ config.vlan }}
{% elif config.mode == 'trunk' %}
 switchport mode trunk
 switchport trunk allowed vlan {{ config.allowed_vlans | join(',') }}
{% endif %}
 description {{ config.description }}
 no shutdown
!
{% endfor %}
```

### VLAN Data (vlan_data.yaml)

```yaml
---
hostname: access-switch-01
generation_date: "2026-03-12"

vlans:
  - id: 10
    name: DATA
    description: "Corporate data network"
  - id: 20
    name: VOICE
    description: "VoIP phones"
  - id: 30
    name: GUEST
    description: "Guest wireless"
  - id: 99
    name: MGMT
    description: "Management"

interfaces:
  GigabitEthernet0/1:
    mode: access
    vlan: 10
    description: "Workstation port"

  GigabitEthernet0/2:
    mode: access
    vlan: 20
    description: "IP Phone"

  GigabitEthernet0/24:
    mode: trunk
    allowed_vlans: [10, 20, 30, 99]
    description: "Trunk to distribution"
```

### Generate Script (generate_vlan_config.py)

```python
#!/usr/bin/env python3
"""
Generate VLAN configuration from template and data
"""

from jinja2 import Environment, FileSystemLoader
import yaml
from datetime import datetime

def generate_vlan_config(data_file, template_file, output_file):
    """
    Generate VLAN configuration
    """
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Load data
    with open(data_file) as f:
        data = yaml.safe_load(f)

    # Add generation timestamp
    data['generation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Load and render template
    template = env.get_template(template_file)
    config = template.render(data)

    # Save configuration
    with open(output_file, 'w') as f:
        f.write(config)

    print(f"✓ Configuration generated: {output_file}")
    print(f"  Device: {data['hostname']}")
    print(f"  VLANs: {len(data['vlans'])}")
    print(f"  Interfaces: {len(data['interfaces'])}")

    return config

if __name__ == "__main__":
    config = generate_vlan_config(
        'vlan_data.yaml',
        'vlan_config.j2',
        'configs/access-switch-01_config.txt'
    )

    print("\nGenerated Configuration Preview:")
    print("=" * 70)
    print(config[:500])  # Show first 500 characters
```

**Generated Output:**

```
!
! VLAN Configuration
! Generated: 2026-03-12 11:45:30
! Device: access-switch-01
!
hostname access-switch-01
!
vlan 10
 name DATA
 description Corporate data network
vlan 20
 name VOICE
 description VoIP phones
vlan 30
 name GUEST
 description Guest wireless
vlan 99
 name MGMT
 description Management
!
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 description Workstation port
 no shutdown
!
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 20
 description IP Phone
 no shutdown
!
interface GigabitEthernet0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,99
 description Trunk to distribution
 no shutdown
!
```

---

## 🔒 Real-World Pattern 2: Access Control Lists

### ACL Template (templates/acl_config.j2)

```jinja2
!
! Access Control Lists
! Device: {{ hostname }}
!
{% for acl in acls %}
{% if acl.type == 'standard' %}
ip access-list standard {{ acl.name }}
{% for rule in acl.rules %}
 {{ rule.action }} {{ rule.source }}
{% endfor %}
{% elif acl.type == 'extended' %}
ip access-list extended {{ acl.name }}
{% for rule in acl.rules %}
 {{ rule.action }} {{ rule.protocol }} {{ rule.source }} {{ rule.destination }}{{ ' eq ' ~ rule.port if rule.port is defined else '' }}
{% endfor %}
{% endif %}
!
{% endfor %}
!
! Apply ACLs to interfaces
{% for interface, config in interface_acls.items() %}
interface {{ interface }}
{% if config.inbound is defined %}
 ip access-group {{ config.inbound }} in
{% endif %}
{% if config.outbound is defined %}
 ip access-group {{ config.outbound }} out
{% endif %}
!
{% endfor %}
```

### ACL Data (acl_data.yaml)

```yaml
---
hostname: edge-router-01

acls:
  - name: ALLOW_MANAGEMENT
    type: standard
    rules:
      - action: permit
        source: 10.10.0.0 0.0.255.255
      - action: deny
        source: any

  - name: ALLOW_WEB_TRAFFIC
    type: extended
    rules:
      - action: permit
        protocol: tcp
        source: any
        destination: any
        port: 80
      - action: permit
        protocol: tcp
        source: any
        destination: any
        port: 443
      - action: deny
        protocol: ip
        source: any
        destination: any

interface_acls:
  GigabitEthernet0/0:
    inbound: ALLOW_MANAGEMENT
  GigabitEthernet0/1:
    outbound: ALLOW_WEB_TRAFFIC
```

---

## ⚙️ Advanced Jinja2 Features

### 1. Template Inheritance

**Base template (templates/base_config.j2):**

```jinja2
!
! Base Configuration
! Device: {{ hostname }}
! Template: {{ template_name }}
! Generated: {{ timestamp }}
!
hostname {{ hostname }}
!
{% block common_settings %}
ip domain-name {{ domain_name }}
ip name-server {{ dns_servers | join(' ') }}
{% endblock %}
!
{% block device_specific %}
! Device-specific configuration goes here
{% endblock %}
!
{% block interfaces %}
! Interface configuration
{% endblock %}
!
end
```

**Child template (templates/router_config.j2):**

```jinja2
{% extends "base_config.j2" %}

{% block device_specific %}
! Router-specific settings
ip routing
router ospf {{ ospf_process_id }}
 network {{ ospf_network }} {{ ospf_wildcard }} area {{ ospf_area }}
{% endblock %}

{% block interfaces %}
{% for interface in interfaces %}
interface {{ interface.name }}
 ip address {{ interface.ip }} {{ interface.mask }}
 no shutdown
!
{% endfor %}
{% endblock %}
```

---

### 2. Macros (Reusable Blocks)

```jinja2
{% macro interface_config(name, ip, mask, description='') %}
interface {{ name }}
 ip address {{ ip }} {{ mask }}
{% if description %}
 description {{ description }}
{% endif %}
 no shutdown
!
{% endmacro %}

!
! Using macros
{{ interface_config('GigabitEthernet0/0', '10.1.1.1', '255.255.255.0', 'WAN Link') }}
{{ interface_config('GigabitEthernet0/1', '192.168.1.1', '255.255.255.0') }}
```

---

### 3. Whitespace Control

Control how Jinja2 handles whitespace and newlines.

```jinja2
{# Remove whitespace before/after block #}
{% for vlan in vlans -%}
vlan {{ vlan }}
{% endfor -%}

{# The minus sign (-) removes whitespace #}
{%- for interface in interfaces -%}
interface {{ interface }}
{% endfor -%}
```

**Whitespace modifiers:**

- `{%-` — Strip whitespace before
- `-%}` — Strip whitespace after
- `{#` — Comment (not rendered)

---

### 4. Custom Filters

Create custom filters for network automation.

```python
#!/usr/bin/env python3
"""
Custom Jinja2 filters for network automation
"""

from jinja2 import Environment, FileSystemLoader
import ipaddress

def subnet_mask_to_cidr(mask):
    """
    Convert subnet mask to CIDR notation
    Example: '255.255.255.0' -> '/24'
    """
    return '/' + str(ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen)

def wildcard_mask(subnet_mask):
    """
    Convert subnet mask to wildcard mask
    Example: '255.255.255.0' -> '0.0.0.255'
    """
    mask_int = int(ipaddress.IPv4Address(subnet_mask))
    wildcard_int = 0xFFFFFFFF ^ mask_int
    return str(ipaddress.IPv4Address(wildcard_int))

def interface_short_name(interface):
    """
    Convert interface name to short form
    Example: 'GigabitEthernet0/0' -> 'Gi0/0'
    """
    replacements = {
        'GigabitEthernet': 'Gi',
        'FastEthernet': 'Fa',
        'TenGigabitEthernet': 'Te',
        'Ethernet': 'Et'
    }

    for long, short in replacements.items():
        if interface.startswith(long):
            return interface.replace(long, short)

    return interface

# Setup Jinja2 environment with custom filters
env = Environment(loader=FileSystemLoader('templates'))
env.filters['subnet_to_cidr'] = subnet_mask_to_cidr
env.filters['wildcard'] = wildcard_mask
env.filters['short_name'] = interface_short_name

# Example template using custom filters
template_string = """
interface {{ interface }}
 ip address {{ ip }} {{ mask }} {# {{ mask | subnet_to_cidr }} #}
!
router ospf 1
 network {{ network }} {{ mask | wildcard }} area 0
!
! Short name: {{ interface | short_name }}
"""

template = env.from_string(template_string)

data = {
    'interface': 'GigabitEthernet0/0',
    'ip': '10.1.1.1',
    'mask': '255.255.255.0',
    'network': '10.1.1.0'
}

print(template.render(data))
```

**Output:**

```
interface GigabitEthernet0/0
 ip address 10.1.1.1 255.255.255.0
!
router ospf 1
 network 10.1.1.0 0.0.0.255 area 0
!
! Short name: Gi0/0
```

---

## 🚀 Real-World Pattern 3: Multi-Device Configuration Generation

### Complete Automation Workflow

**Project Structure:**

```
network-config-automation/
├── templates/
│   ├── base_config.j2
│   ├── router_config.j2
│   └── switch_config.j2
├── data/
│   ├── devices.yaml
│   └── global_settings.yaml
├── configs/
│   └── (generated configs)
├── generate_configs.py
└── deploy_configs.py
```

### devices.yaml

```yaml
---
devices:
  - hostname: core-router-01
    device_type: router
    template: router_config.j2
    management_ip: 10.1.1.1
    interfaces:
      - name: GigabitEthernet0/0
        ip: 192.168.1.1
        mask: 255.255.255.0
        description: "WAN Link"
      - name: GigabitEthernet0/1
        ip: 10.10.1.1
        mask: 255.255.255.0
        description: "LAN Link"
    ospf:
      process_id: 1
      networks:
        - network: 192.168.1.0
          wildcard: 0.0.0.255
          area: 0

  - hostname: access-switch-01
    device_type: switch
    template: switch_config.j2
    management_ip: 10.1.1.10
    vlans:
      - id: 10
        name: DATA
      - id: 20
        name: VOICE
    interfaces:
      GigabitEthernet0/1:
        mode: access
        vlan: 10
        description: "User port"
```

### global_settings.yaml

```yaml
---
domain_name: example.com
dns_servers:
  - 8.8.8.8
  - 8.8.4.4
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org
syslog_server: 10.10.10.10
snmp_community: public
timezone: EST -5 0
```

### generate_configs.py

```python
#!/usr/bin/env python3
"""
Generate configurations for all devices from templates and data
"""

from jinja2 import Environment, FileSystemLoader
import yaml
from datetime import datetime
import os

def load_data():
    """Load device and global configuration data"""
    with open('data/devices.yaml') as f:
        devices = yaml.safe_load(f)

    with open('data/global_settings.yaml') as f:
        global_settings = yaml.safe_load(f)

    return devices['devices'], global_settings

def generate_device_config(device, global_settings, env):
    """
    Generate configuration for a single device
    """
    # Combine device-specific and global settings
    data = {**global_settings, **device}
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Load template
    template = env.get_template(device['template'])

    # Render configuration
    config = template.render(data)

    return config

def save_config(hostname, config):
    """Save configuration to file"""
    os.makedirs('configs', exist_ok=True)
    filename = f"configs/{hostname}_config.txt"

    with open(filename, 'w') as f:
        f.write(config)

    return filename

def main():
    """Main function"""
    print("=" * 70)
    print("NETWORK CONFIGURATION GENERATOR")
    print("=" * 70)

    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Load data
    devices, global_settings = load_data()

    print(f"\n✓ Loaded {len(devices)} device(s)")
    print(f"✓ Loaded global settings")

    # Generate configs
    print(f"\n{'=' * 70}")
    print("GENERATING CONFIGURATIONS")
    print("=" * 70)

    generated_configs = []

    for device in devices:
        print(f"\n📝 Generating config for {device['hostname']}...")

        # Generate config
        config = generate_device_config(device, global_settings, env)

        # Save config
        filename = save_config(device['hostname'], config)

        # Track generated files
        generated_configs.append({
            'hostname': device['hostname'],
            'filename': filename,
            'size': len(config)
        })

        print(f"  ✓ Saved to {filename}")
        print(f"  ✓ Size: {len(config):,} bytes")

    # Summary
    print(f"\n{'=' * 70}")
    print("GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total devices: {len(generated_configs)}")
    print(f"Total config size: {sum(c['size'] for c in generated_configs):,} bytes")

    print(f"\n{'=' * 70}")
    print("GENERATED FILES:")
    print("=" * 70)
    for config in generated_configs:
        print(f"  {config['filename']}")

    print()

if __name__ == "__main__":
    main()
```

**Run the generator:**

```bash
python generate_configs.py
```

**Output:**

```
======================================================================
NETWORK CONFIGURATION GENERATOR
======================================================================

✓ Loaded 2 device(s)
✓ Loaded global settings

======================================================================
GENERATING CONFIGURATIONS
======================================================================

📝 Generating config for core-router-01...
  ✓ Saved to configs/core-router-01_config.txt
  ✓ Size: 1,245 bytes

📝 Generating config for access-switch-01...
  ✓ Saved to configs/access-switch-01_config.txt
  ✓ Size: 987 bytes

======================================================================
GENERATION SUMMARY
======================================================================
Total devices: 2
Total config size: 2,232 bytes

======================================================================
GENERATED FILES:
======================================================================
  configs/core-router-01_config.txt
  configs/access-switch-01_config.txt
```

---

## 🧪 Testing and Validating Templates

### Template Testing Script

```python
#!/usr/bin/env python3
"""
Test Jinja2 templates with sample data
Catch errors before deployment
"""

from jinja2 import Environment, FileSystemLoader, TemplateError
import yaml

def test_template(template_name, test_data_file):
    """
    Test template with sample data
    """
    print(f"\nTesting: {template_name}")
    print("-" * 50)

    # Setup environment
    env = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )

    try:
        # Load template
        template = env.get_template(template_name)

        # Load test data
        with open(test_data_file) as f:
            data = yaml.safe_load(f)

        # Render template
        config = template.render(data)

        # Basic validation
        if len(config) == 0:
            print("✗ FAIL: Generated config is empty")
            return False

        # Check for common Cisco config patterns
        if 'hostname' not in config:
            print("⚠ WARNING: Config doesn't contain hostname")

        print(f"✓ PASS: Generated {len(config):,} bytes")
        print("\nPreview (first 300 characters):")
        print(config[:300])

        return True

    except TemplateError as e:
        print(f"✗ FAIL: Template error")
        print(f"  Error: {e}")
        return False

    except Exception as e:
        print(f"✗ FAIL: Unexpected error")
        print(f"  Error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("TEMPLATE TESTING")
    print("=" * 70)

    tests = [
        ('router_config.j2', 'test_data/router_test.yaml'),
        ('switch_config.j2', 'test_data/switch_test.yaml'),
        ('vlan_config.j2', 'test_data/vlan_test.yaml')
    ]

    results = []
    for template, test_data in tests:
        result = test_template(template, test_data)
        results.append((template, result))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for template, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {template}")

    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

if __name__ == "__main__":
    main()
```

---

## 🐛 Common Jinja2 Pitfalls & Solutions

### Pitfall 1: Undefined Variables

**Problem:**

```jinja2
hostname {{ hostname }}
interface {{ undefined_variable }}
```

**Default behaviour:** Jinja2 renders missing variables as empty strings, which can hide mistakes.
If you enable `StrictUndefined` (recommended during testing), this raises
`UndefinedError: 'undefined_variable' is undefined`.

**Solutions:**

```jinja2
{# Option 1: Use default filter #}
interface {{ interface_name | default('GigabitEthernet0/0') }}

{# Option 2: Check if defined #}
{% if interface_name is defined %}
interface {{ interface_name }}
{% endif %}

{# Option 3: Configure Jinja2 to fail fast on undefined variables #}
```

```python
from jinja2 import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
```

---

### Pitfall 2: Whitespace Issues

**Problem:**

```jinja2
{% for vlan in vlans %}
vlan {{ vlan }}
{% endfor %}
```

**Output (extra blank lines):**

```

vlan 10

vlan 20

vlan 30

```

**Solution:**

```jinja2
{% for vlan in vlans -%}
vlan {{ vlan }}
{% endfor -%}
```

**Output (clean):**

```
vlan 10
vlan 20
vlan 30
```

---

### Pitfall 3: Type Errors

**Problem:**

```jinja2
switchport trunk allowed vlan {{ vlans }}
```

**Data:**

```python
{'vlans': [10, 20, 30]}  # List, not string
```

**Output (wrong):**

```
switchport trunk allowed vlan [10, 20, 30]
```

**Solution:**

```jinja2
switchport trunk allowed vlan {{ vlans | join(',') }}
```

**Output (correct):**

```
switchport trunk allowed vlan 10,20,30
```

---

## 🎓 Best Practices for Production

### 1. Separate Data from Templates

**Good structure:**

```
project/
├── templates/        # Templates (version controlled)
├── data/            # Data files (version controlled)
├── configs/         # Generated configs (excluded from git)
└── scripts/         # Generation scripts
```

---

### 2. Version Control Everything

```bash
git add templates/ data/ scripts/
git commit -m "Updated VLAN template for new standard"
git push
```

**Exclude generated configs:**

```gitignore
# .gitignore
configs/
*.pyc
__pycache__/
```

---

### 3. Use Template Inheritance

Don't repeat yourself—use base templates:

```jinja2
{# base_config.j2 #}
{% block header %}
! Base configuration
{% endblock %}

{% block device_config %}
! Override this block
{% endblock %}
```

---

### 4. Document Your Templates

```jinja2
{#
Template: router_config.j2
Purpose: Generate router configurations for WAN edge devices
Required variables:
  - hostname (string)
  - interfaces (list of dicts)
  - ospf (dict with process_id, networks)
Optional variables:
  - enable_ssh (boolean, default: true)
Author: Network Team
Last updated: 2026-03-12
#}

hostname {{ hostname }}
...
```

---

### 5. Test Before Deploy

```python
# Always test templates before deploying
def validate_config(config):
    """Basic config validation"""
    checks = [
        ('hostname' in config, "Missing hostname"),
        ('end' in config, "Missing end statement"),
        (len(config) > 100, "Config too short")
    ]

    for check, error_msg in checks:
        if not check:
            raise ValueError(f"Validation failed: {error_msg}")

    return True
```

---

## 📚 Additional Resources

- **[Jinja2 Official Documentation](https://jinja.palletsprojects.com/)** — Complete Jinja2 reference
- **[Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/stable/templates/)** — Template syntax guide
- **[Network to Code Jinja2 Blog](https://networktocode.com/blog/)** — Real-world Jinja2 examples
- **[PyYAML Documentation](https://pyyaml.org/)** — For loading YAML data

---

## 🎯 Key Takeaways

- ✅ **Jinja2 transforms data into configurations** — Write template once, use everywhere
- ✅ **Separation of concerns** — Data (YAML) + Logic (Python) + Templates (Jinja2)
- ✅ **Version control templates** — Track configuration standards over time
- ✅ **Eliminate manual errors** — No more copy-paste mistakes
- ✅ **Conditional logic** — Generate different configs based on device type, role
- ✅ **Production-ready** — Used by enterprises for large-scale automation

---

## 🎓 Next Steps

You've mastered the data modelling trilogy (YAML + JSON + Jinja2)! Now apply these skills:

1. **[Nornir Fundamentals](./nornir-fundamentals.md)** (Recommended Next)
   - Use YAML inventories and Jinja2 templates
   - Deploy configs at scale with parallel execution

2. **[PyATS Fundamentals](./pyats-fundamentals.md)**
   - Validate generated configs with PyATS
   - Ensure templates produce correct output

3. **[Credential Management](./credential-management-network-automation.md)**
   - Secure your automation workflows
   - Manage credentials for template deployment

4. **[Enterprise Config Backup with Nornir](./enterprise-config-backup-nornir.md)**
   - Compare generated configs vs running configs
   - Detect configuration drift

---

> **Remember:** Templates + Data = Scalable Configuration Management. Master Jinja2, eliminate manual configuration errors forever.

[← Back to JSON Tutorial](./json-data-handling-network-automation.md) | [Continue to Nornir Fundamentals →](./nornir-fundamentals.md)
