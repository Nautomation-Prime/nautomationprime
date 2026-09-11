---
title: JSON Data Handling for Network Automation
description: Master JSON for network automation - REST API interactions, structured logging, data serialization. Learn parsing, generation, and production patterns.
tags:
  - Intermediate
  - JSON
  - Data Modelling
  - APIs
  - REST
  - Structured Logging
  - Tutorial
---

## JSON Data Handling for Network Automation

## "From CLI Scraping to Structured APIs — The Language of Modern Networks"

While YAML is perfect for **human-editable configuration**, JSON (JavaScript Object Notation) is the lingua franca of **machine-to-machine communication**.

**Every modern network API speaks JSON:**

- ✅ **REST APIs** — Cisco DNA Center, Meraki, ACI, NSO all use JSON
- ✅ **NETCONF/RESTCONF** — Structured device management uses JSON encoding
- ✅ **Webhooks** — Network events delivered as JSON payloads
- ✅ **Structured logging** — Modern logging systems use JSON for queryability
- ✅ **Message queues** — RabbitMQ, Kafka deliver JSON messages
- ✅ **Databases** — NoSQL databases (MongoDB, Elasticsearch) store JSON natively

If YAML is your **configuration language**, JSON is your **data exchange format**. This tutorial teaches you to master both.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ JSON syntax fundamentals and differences from YAML
- ✅ Reading and writing JSON in Python
- ✅ Consuming REST APIs with JSON responses
- ✅ Generating JSON for API requests
- ✅ Structured logging with JSON output
- ✅ JSON Schema validation for data integrity
- ✅ Performance optimisation for large JSON datasets
- ✅ Real-world patterns: API clients, logging, data pipelines

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [YAML Data Modelling Tutorial](./yaml-data-modeling-network-automation.md)** — Understanding structured data
- ✅ Understanding of Python data structures (dict, list, str)
- ✅ Understanding of HTTP basics (GET, POST, PUT, DELETE)

### Required Software

```bash
# Create a virtual environment
python -m venv json_venv
source json_venv/bin/activate
# Windows PowerShell: .\json_venv\Scripts\Activate.ps1
# Windows CMD: json_venv\Scripts\activate.bat

# Install required packages
pip install requests netmiko jsonschema
```

### Required Access

- No device access required for core concepts
- Optional: Access to Cisco DNA Center or Meraki Dashboard for API examples

---

## 📖 JSON Fundamentals: Understanding the Syntax

### What is JSON?

JSON is a **lightweight data-interchange format** that's easy for humans to read and write, and easy for machines to parse and generate.

**Example:** Device data in JSON:

```json
{
  "hostname": "router1",
  "ip_address": "10.1.1.1",
  "device_type": "cisco_ios",
  "vlans": [10, 20, 30],
  "interfaces": {
    "GigabitEthernet0/0": {
      "ip": "10.1.1.1",
      "status": "up"
    }
  },
  "enabled": true,
  "uptime_seconds": 86400
}
```

**Key characteristics:**

- Uses curly braces `{}` for objects (dictionaries)
- Uses square brackets `[]` for arrays (lists)
- Uses double quotes `""` for strings (single quotes not allowed)
- Commas separate elements (no trailing comma allowed)
- No comments allowed (unlike YAML)

---

## 🔧 JSON vs YAML: Key Differences

| Feature | JSON | YAML |
|:--------|:-----|:-----|
| **Syntax** | `{"key": "value"}` | `key: value` |
| **Quotes** | Required for strings | Optional |
| **Comments** | Not allowed | Allowed (`#`) |
| **Readability** | More verbose | More readable |
| **Use Case** | APIs, data exchange | Configuration files |
| **Trailing Commas** | Not allowed | N/A (no commas) |
| **Data Types** | Explicit | Inferred |
| **File Extension** | `.json` | `.yaml` or `.yml` |

**Same data in both formats:**

```json
{
  "device": {
    "hostname": "router1",
    "interfaces": [
      {"name": "Gi0/0", "ip": "10.1.1.1"},
      {"name": "Gi0/1", "ip": "10.1.2.1"}
    ]
  }
}
```

```yaml
# YAML
device:
  hostname: router1
  interfaces:
    - name: Gi0/0
      ip: 10.1.1.1
    - name: Gi0/1
      ip: 10.1.2.1
```

---

## 🐍 Reading JSON in Python

### Basic JSON Loading

```python
#!/usr/bin/env python3
"""
Read JSON from file and string
"""

import json

# Method 1: Load from file
with open('devices.json', 'r') as file:
    data = json.load(file)
    # json.load() parses JSON file and returns Python dict/list

print(f"Device hostname: {data['hostname']}")
print(f"Device IP: {data['ip_address']}")

# Method 2: Parse JSON string
json_string = '{"hostname": "router1", "ip": "10.1.1.1"}'
data = json.loads(json_string)
# json.loads() parses JSON string (note the 's' in loads)

print(f"Parsed hostname: {data['hostname']}")
```

**Key functions:**

- `json.load(file)` — Read from file object
- `json.loads(string)` — Parse JSON string
- Both return Python dict or list

---

### Handling Nested JSON

```python
#!/usr/bin/env python3
"""
Navigate nested JSON structures
"""

import json

# Complex nested JSON
json_data = """
{
  "device": {
    "hostname": "core-router-01",
    "management_ip": "10.1.1.1",
    "interfaces": [
      {
        "name": "GigabitEthernet0/0",
        "ip_address": "192.168.1.1",
        "subnet_mask": "255.255.255.0",
        "status": "up",
        "speed": "1000"
      },
      {
        "name": "GigabitEthernet0/1",
        "ip_address": "192.168.2.1",
        "subnet_mask": "255.255.255.0",
        "status": "up",
        "speed": "1000"
      }
    ],
    "bgp": {
      "asn": 65001,
      "neighbors": [
        {"ip": "10.2.2.2", "remote_asn": 65002, "state": "established"},
        {"ip": "10.3.3.3", "remote_asn": 65003, "state": "established"}
      ]
    }
  }
}
"""

# Parse JSON
data = json.loads(json_data)

# Navigate nested structure
device = data['device']
print(f"Device: {device['hostname']}")
print(f"Management IP: {device['management_ip']}")

# Access list items
print("\nInterfaces:")
for interface in device['interfaces']:
    print(f"  {interface['name']}: {interface['ip_address']} ({interface['status']})")

# Access nested dictionary
print(f"\nBGP ASN: {device['bgp']['asn']}")
print("BGP Neighbors:")
for neighbor in device['bgp']['neighbors']:
    print(f"  {neighbor['ip']} (AS{neighbor['remote_asn']}) - {neighbor['state']}")
```

**Output:**

```
Device: core-router-01
Management IP: 10.1.1.1

Interfaces:
  GigabitEthernet0/0: 192.168.1.1 (up)
  GigabitEthernet0/1: 192.168.2.1 (up)

BGP ASN: 65001
BGP Neighbors:
  10.2.2.2 (AS65002) - established
  10.3.3.3 (AS65003) - established
```

---

### Safe JSON Access with Error Handling

```python
#!/usr/bin/env python3
"""
Safely access JSON with error handling
"""

import json

def safe_get(data, *keys, default=None):
    """
    Safely navigate nested dictionary structure
    Returns default if any key doesn't exist
    """
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data

# Sample JSON (some fields may be missing)
json_data = '{"device": {"hostname": "router1", "interfaces": [{"name": "Gi0/0"}]}}'
data = json.loads(json_data)

# Safe access (won't crash if keys missing)
hostname = safe_get(data, 'device', 'hostname', default='unknown')
print(f"Hostname: {hostname}")

# This would crash without safe_get
bgp_asn = safe_get(data, 'device', 'bgp', 'asn', default='not configured')
print(f"BGP ASN: {bgp_asn}")

# Access first interface name
first_interface = safe_get(data, 'device', 'interfaces', 0, 'name', default='no interfaces')
print(f"First Interface: {first_interface}")
```

**Output:**

```
Hostname: router1
BGP ASN: not configured
First Interface: Gi0/0
```

---

## 📄 Writing JSON in Python

### Creating JSON from Python Data

```python
#!/usr/bin/env python3
"""
Convert Python data to JSON
"""

import json
from datetime import datetime

# Python dictionary
device_data = {
    'hostname': 'router1',
    'ip_address': '10.1.1.1',
    'device_type': 'cisco_ios',
    'vlans': [10, 20, 30, 40],
    'interfaces': {
        'GigabitEthernet0/0': {
            'ip': '192.168.1.1',
            'mask': '255.255.255.0',
            'status': 'up'
        },
        'GigabitEthernet0/1': {
            'ip': '192.168.2.1',
            'mask': '255.255.255.0',
            'status': 'up'
        }
    },
    'enabled': True,
    'last_backup': datetime.now().isoformat()
}

# Method 1: Write to file
with open('device_output.json', 'w') as file:
    json.dump(device_data, file, indent=2)
    # indent=2 makes output readable (pretty-printed)

print("✓ JSON file created: device_output.json")

# Method 2: Convert to JSON string
json_string = json.dumps(device_data, indent=2)
# json.dumps() returns JSON string (note the 's')

print("\nJSON output:")
print(json_string)
```

**Generated JSON (device_output.json):**

```json
{
  "hostname": "router1",
  "ip_address": "10.1.1.1",
  "device_type": "cisco_ios",
  "vlans": [
    10,
    20,
    30,
    40
  ],
  "interfaces": {
    "GigabitEthernet0/0": {
      "ip": "192.168.1.1",
      "mask": "255.255.255.0",
      "status": "up"
    },
    "GigabitEthernet0/1": {
      "ip": "192.168.2.1",
      "mask": "255.255.255.0",
      "status": "up"
    }
  },
  "enabled": true,
  "last_backup": "2026-03-12T11:30:45.123456"
}
```

**Key functions:**

- `json.dump(data, file)` — Write to file object
- `json.dumps(data)` — Convert to JSON string
- `indent=2` — Pretty-print with 2-space indentation

---

### Compact vs Pretty JSON

```python
#!/usr/bin/env python3
"""
Compare compact and pretty-printed JSON
"""

import json

data = {'hostname': 'router1', 'ip': '10.1.1.1', 'vlans': [10, 20, 30]}

# Compact (for APIs and storage efficiency)
compact = json.dumps(data, separators=(',', ':'))
print(f"Compact ({len(compact)} bytes):")
print(compact)

# Pretty (for humans)
pretty = json.dumps(data, indent=2)
print(f"\nPretty ({len(pretty)} bytes):")
print(pretty)
```

**Output:**

```
Compact (57 bytes):
{"hostname":"router1","ip":"10.1.1.1","vlans":[10,20,30]}

Pretty (88 bytes):
{
  "hostname": "router1",
  "ip": "10.1.1.1",
  "vlans": [
    10,
    20,
    30
  ]
}
```

**When to use each:**

- **Compact:** API requests, log files, network transmission (smaller size)
- **Pretty:** Configuration files, debugging, human review (readable)

---

## 🌐 Real-World Pattern 1: REST API Interactions

### Consuming REST APIs (GET Request)

```python
#!/usr/bin/env python3
"""
Get data from REST API and process JSON response
Example: Cisco Meraki Dashboard API
"""

import requests
import json

# API configuration
API_KEY = "your_meraki_api_key_here"
ORG_ID = "your_org_id_here"
BASE_URL = "https://api.meraki.com/api/v1"

headers = {
    'X-Cisco-Meraki-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def get_networks(org_id):
    """
    Get all networks in an organisation
    Returns list of network dictionaries
    """
    url = f"{BASE_URL}/organizations/{org_id}/networks"

    try:
        response = requests.get(url, headers=headers)

        # Check if request was successful
        response.raise_for_status()
        # Raises HTTPError for bad responses (4xx, 5xx)

        # Parse JSON response
        networks = response.json()
        # .json() method automatically parses JSON response

        return networks

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        print(f"  Response: {e.response.text}")
        return None
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Could not reach API")
        return None
    except json.JSONDecodeError:
        print("✗ Invalid JSON response")
        return None

def main():
    """Main function"""
    print("Fetching networks from Meraki API...")

    networks = get_networks(ORG_ID)

    if networks:
        print(f"\n✓ Found {len(networks)} networks:")

        for network in networks:
            # Access JSON fields
            print(f"\n  Network: {network['name']}")
            print(f"    ID: {network['id']}")
            print(f"    Type: {', '.join(network['productTypes'])}")
            print(f"    Time Zone: {network.get('timeZone', 'Not set')}")

        # Save to file for later analysis
        with open('meraki_networks.json', 'w') as f:
            json.dump(networks, f, indent=2)

        print(f"\n✓ Data saved to meraki_networks.json")
    else:
        print("✗ Failed to retrieve networks")

if __name__ == "__main__":
    main()
```

**Key concepts:**

- `requests.get()` — Send HTTP GET request
- `response.json()` — Parse JSON response automatically
- `response.raise_for_status()` — Check for HTTP errors
- Error handling for network and JSON parsing errors

---

### Sending Data to REST APIs (POST Request)

```python
#!/usr/bin/env python3
"""
Send JSON data to REST API
Example: Create VLAN via API
"""

import requests
import json

def create_vlan(device_ip, vlan_id, vlan_name, username, password):
    """
    Create VLAN via REST API
    Sends JSON payload with VLAN configuration
    """
    url = f"https://{device_ip}/restconf/data/Cisco-IOS-XE-native:native/vlan"

    # JSON payload
    payload = {
        "Cisco-IOS-XE-vlan:vlan-list": {
            "id": vlan_id,
            "name": vlan_name
        }
    }

    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json'
    }

    try:
        response = requests.post(
            url,
            auth=(username, password),  # Basic authentication
            headers=headers,
            data=json.dumps(payload),  # Convert dict to JSON string
            verify=False  # Disable SSL verification (lab only!)
        )

        response.raise_for_status()

        print(f"✓ VLAN {vlan_id} ({vlan_name}) created successfully")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")

        # Try to parse error response
        try:
            error_data = e.response.json()
            print(f"  Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"  Response: {e.response.text}")

        return False

def main():
    """Main function"""
    # Device credentials
    device_ip = "10.1.1.1"
    username = "admin"
    password = "password"

    # Create multiple VLANs
    vlans = [
        {'id': 100, 'name': 'DATA'},
        {'id': 200, 'name': 'VOICE'},
        {'id': 300, 'name': 'GUEST'}
    ]

    print("Creating VLANs via REST API...")

    for vlan in vlans:
        create_vlan(device_ip, vlan['id'], vlan['name'], username, password)

if __name__ == "__main__":
    main()
```

**Key concepts:**

- `requests.post()` — Send HTTP POST request
- `json.dumps(payload)` — Convert Python dict to JSON string
- `headers` — Specify content type for API
- Error response parsing — Extract error details from JSON

---

## 📊 Real-World Pattern 2: Structured Logging

### JSON Structured Logging

```python
#!/usr/bin/env python3
"""
Structured logging with JSON output
Makes logs machine-parsable for analysis
"""

import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs JSON
    Makes logs queryable by log aggregation systems
    """

    def format(self, record):
        """
        Format log record as JSON
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add custom fields if present
        if hasattr(record, 'device'):
            log_data['device'] = record.device
        if hasattr(record, 'ip'):
            log_data['ip'] = record.ip
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        if hasattr(record, 'device_count'):
            log_data['device_count'] = record.device_count

        return json.dumps(log_data)

# Configure logger with JSON formatter
logger = logging.getLogger('network_automation')
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def backup_device_config(device_name, device_ip):
    """
    Backup device configuration with structured logging
    """
    import time
    start_time = time.time()

    # Log start
    logger.info(
        f"Starting backup for {device_name}",
        extra={'device': device_name, 'ip': device_ip}
    )

    try:
        # Simulate backup operation
        time.sleep(2)  # Simulate work

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log success
        logger.info(
            f"Backup completed for {device_name}",
            extra={'device': device_name, 'duration': duration_ms}
        )

        return True

    except Exception as e:
        # Log error with exception info
        logger.error(
            f"Backup failed for {device_name}: {str(e)}",
            extra={'device': device_name},
            exc_info=True
        )
        return False

def main():
    """Main function"""
    devices = [
        {'name': 'router1', 'ip': '10.1.1.1'},
        {'name': 'router2', 'ip': '10.1.1.2'},
        {'name': 'switch1', 'ip': '10.1.1.10'}
    ]

    logger.info("Starting network backup job", extra={'device_count': len(devices)})

    for device in devices:
        backup_device_config(device['name'], device['ip'])

    logger.info("Backup job completed")

if __name__ == "__main__":
    main()
```

**Output (each line is a JSON object):**

```json
{"timestamp": "2026-03-12T11:45:23.456789Z", "level": "INFO", "logger": "network_automation", "message": "Starting network backup job", "function": "main", "line": 78, "device_count": 3}
{"timestamp": "2026-03-12T11:45:23.457123Z", "level": "INFO", "logger": "network_automation", "message": "Starting backup for router1", "function": "backup_device_config", "line": 44, "device": "router1", "ip": "10.1.1.1"}
{"timestamp": "2026-03-12T11:45:25.458456Z", "level": "INFO", "logger": "network_automation", "message": "Backup completed for router1", "function": "backup_device_config", "line": 55, "device": "router1", "duration_ms": 2001.5}
```

**Why structured JSON logging:**

- ✅ **Queryable** — Search by device, duration, error type
- ✅ **Machine-parsable** — Feed into Elasticsearch, Splunk, Datadog
- ✅ **Standardised** — Same format across all automation scripts
- ✅ **Aggregatable** — Combine logs from multiple sources easily

---

## 🔒 Real-World Pattern 3: Configuration Management

### Storing Device State in JSON

```python
#!/usr/bin/env python3
"""
Store and compare device state in JSON
Track configuration drift over time
"""

import json
from datetime import datetime
from netmiko import ConnectHandler

def capture_device_state(device_params):
    """
    Capture device state and return as structured data
    """
    # Connect to device
    connection = ConnectHandler(**device_params)

    # Gather device information
    state = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'hostname': device_params['host'],
        'device_type': device_params['device_type'],
        'running_config': connection.send_command('show running-config'),
        'version': connection.send_command('show version'),
        'interfaces': connection.send_command('show ip interface brief'),
        'vlan_database': connection.send_command('show vlan brief'),
        'cdp_neighbors': connection.send_command('show cdp neighbors')
    }

    connection.disconnect()
    return state

def save_device_state(device_name, state):
    """
    Save device state to JSON file with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"state_{device_name}_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✓ State saved to {filename}")
    return filename

def compare_states(state1_file, state2_file):
    """
    Compare two device states
    Returns differences
    """
    # Load states
    with open(state1_file) as f:
        state1 = json.load(f)
    with open(state2_file) as f:
        state2 = json.load(f)

    differences = {}

    # Compare running configs
    if state1['running_config'] != state2['running_config']:
        differences['running_config'] = 'CHANGED'

    # Compare VLAN databases
    if state1['vlan_database'] != state2['vlan_database']:
        differences['vlan_database'] = 'CHANGED'

    # Compare CDP neighbors
    if state1['cdp_neighbors'] != state2['cdp_neighbors']:
        differences['cdp_neighbors'] = 'CHANGED'

    return differences

def main():
    """Main function"""
    device_params = {
        'device_type': 'cisco_ios',
        'host': '10.1.1.1',
        'username': 'admin',
        'password': 'password'
    }

    # Capture current state
    print("Capturing device state...")
    state = capture_device_state(device_params)

    # Save to JSON
    filename = save_device_state('router1', state)

    print(f"\n✓ Device state captured and saved")
    print(f"  Timestamp: {state['timestamp']}")
    print(f"  Hostname: {state['hostname']}")

if __name__ == "__main__":
    main()
```

**Generated JSON (state_router1_20260312_114530.json):**

```json
{
  "timestamp": "2026-03-12T11:45:30.123456Z",
  "hostname": "10.1.1.1",
  "device_type": "cisco_ios",
  "running_config": "!\nversion 15.6\n...",
  "version": "Cisco IOS Software, C2960 Software...",
  "interfaces": "Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/1     192.168.1.1     YES NVRAM  up                    up",
  "vlan_database": "VLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Gi0/2, Gi0/3",
  "cdp_neighbors": "Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID\nRouter2          Gig 0/1           150        R           ISR4331   Gig 0/0"
}
```

---

## 🧪 JSON Schema Validation

### Validating JSON Structure

```python
#!/usr/bin/env python3
"""
Validate JSON data against a schema
Ensures API responses and config files match expected structure
"""

import json
import jsonschema
from jsonschema import validate

# Define JSON schema (what structure we expect)
device_schema = {
    "type": "object",
    "properties": {
        "hostname": {"type": "string"},
        "ip_address": {
            "type": "string",
            "pattern": "^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$"  # IP regex
        },
        "device_type": {
            "type": "string",
            "enum": ["cisco_ios", "cisco_nxos", "cisco_iosxr"]
        },
        "vlans": {
            "type": "array",
            "items": {"type": "integer", "minimum": 1, "maximum": 4094}
        },
        "enabled": {"type": "boolean"}
    },
    "required": ["hostname", "ip_address", "device_type"]
}

def validate_device_data(data):
    """
    Validate device data against schema
    Returns True if valid, raises exception if invalid
    """
    try:
        validate(instance=data, schema=device_schema)
        print("✓ Data is valid")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"✗ Validation error: {e.message}")
        print(f"  Failed at: {' -> '.join(str(x) for x in e.path)}")
        return False

def main():
    """Main function"""

    # Valid data
    valid_device = {
        "hostname": "router1",
        "ip_address": "10.1.1.1",
        "device_type": "cisco_ios",
        "vlans": [10, 20, 30],
        "enabled": True
    }

    print("Testing valid data:")
    validate_device_data(valid_device)

    # Invalid data (wrong IP format)
    invalid_device1 = {
        "hostname": "router2",
        "ip_address": "invalid_ip",  # ✗ Wrong format
        "device_type": "cisco_ios"
    }

    print("\nTesting invalid IP:")
    validate_device_data(invalid_device1)

    # Invalid data (missing required field)
    invalid_device2 = {
        "hostname": "router3",
        # Missing ip_address (required field)
        "device_type": "cisco_ios"
    }

    print("\nTesting missing required field:")
    validate_device_data(invalid_device2)

    # Invalid data (wrong VLAN range)
    invalid_device3 = {
        "hostname": "router4",
        "ip_address": "10.1.1.4",
        "device_type": "cisco_ios",
        "vlans": [10, 5000]  # ✗ VLAN 5000 exceeds maximum
    }

    print("\nTesting invalid VLAN range:")
    validate_device_data(invalid_device3)

if __name__ == "__main__":
    main()
```

**Output:**

```
Testing valid data:
✓ Data is valid

Testing invalid IP:
✗ Validation error: 'invalid_ip' does not match '^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$'
  Failed at: ip_address

Testing missing required field:
✗ Validation error: 'ip_address' is a required property
  Failed at:

Testing invalid VLAN range:
✗ Validation error: 5000 is greater than the maximum of 4094
  Failed at: vlans -> 1
```

**Why schema validation matters:**

- ✅ **API contract enforcement** — Ensure APIs return expected structure
- ✅ **Configuration validation** — Catch errors before deployment
- ✅ **Documentation** — Schema describes expected data structure
- ✅ **Testing** — Automated validation in CI/CD pipelines

---

## ⚡ Performance Optimisation for Large JSON

### Streaming Large JSON Files

```python
#!/usr/bin/env python3
"""
Process large JSON files efficiently
Use streaming for memory-efficient parsing
"""

import json
import ijson  # pip install ijson

def process_large_json_standard(filename):
    """
    Standard approach: Load entire file into memory
    Works for small files, fails for large files (>1GB)
    """
    with open(filename) as f:
        data = json.load(f)  # Loads entire file into memory

    # Process data
    for item in data:
        process_item(item)

def process_large_json_streaming(filename):
    """
    Streaming approach: Process items one at a time
    Memory-efficient for large files
    """
    with open(filename, 'rb') as f:
        # Parse items incrementally
        items = ijson.items(f, 'item')  # Assumes JSON array

        for item in items:
            # Process one item at a time
            process_item(item)
            # Previous items are garbage collected

def process_item(item):
    """Process a single JSON item"""
    # Your processing logic here
    pass

# Example: Process 10GB JSON file with streaming
# process_large_json_streaming('huge_inventory.json')
```

---

### JSON Performance Tips

```python
#!/usr/bin/env python3
"""
JSON performance optimisation tips
"""

import json
import ujson  # pip install ujson (faster JSON library)

# Tip 1: Use ujson for faster parsing
data = ujson.loads(json_string)  # ~2-4x faster than json.loads()

# Tip 2: Minimise serialization round trips
# Bad (serializes twice)
json_str = json.dumps(data)
data_again = json.loads(json_str)

# Good (keep as dict until needed)
data_copy = data.copy()

# Tip 3: Use compact format for storage
compact = json.dumps(data, separators=(',', ':'))  # Smaller file size

# Tip 4: Cache parsed results
# Bad (parses every time)
for i in range(1000):
    data = json.loads(json_string)

# Good (parse once, reuse)
data = json.loads(json_string)
for i in range(1000):
    use_data(data)
```

---

## 🐛 Common JSON Pitfalls & Solutions

### Pitfall 1: Trailing Commas

**Wrong:**

```json
{
  "hostname": "router1",
  "ip": "10.1.1.1",
}
```

**Error:** `json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes`

**Right:**

```json
{
  "hostname": "router1",
  "ip": "10.1.1.1"
}
```

---

### Pitfall 2: Single Quotes

**Wrong:**

```json
{'hostname': 'router1'}
```

**Right:**

```json
{"hostname": "router1"}
```

**Note:** JSON requires double quotes, not single quotes.

---

### Pitfall 3: Comments

**Wrong:**

```json
{
  // This is a comment
  "hostname": "router1"
}
```

**Right:** JSON doesn't support comments. Use YAML if you need comments, or add a `"_comment"` field:

```json
{
  "_comment": "This device is in NYC datacenter",
  "hostname": "router1"
}
```

---

### Pitfall 4: NaN and Infinity

```python
import json
import math

data = {'value': math.nan}

# This will fail in strict JSON mode
try:
    json.dumps(data, allow_nan=False)
except ValueError as e:
    print(f"Error: {e}")

# Solution: Convert NaN to None or string
data = {'value': None if math.isnan(data['value']) else data['value']}
json.dumps(data)  # Works
```

---

## 🎓 Best Practices for Network Automation

### 1. Use JSON for APIs, YAML for Configuration

**JSON:**

- API requests/responses
- Structured logging
- Message queues
- Database storage

**YAML:**

- Device inventories
- Configuration templates
- Testbed definitions
- Human-editable configs

---

### 2. Always Validate API Responses

```python
import requests
import json

response = requests.get(api_url)

# Check HTTP status
if response.status_code != 200:
    print(f"Error: HTTP {response.status_code}")
    sys.exit(1)

# Check content type
if 'application/json' not in response.headers.get('Content-Type', ''):
    print("Error: Response is not JSON")
    sys.exit(1)

# Parse JSON
try:
    data = response.json()
except json.JSONDecodeError:
    print("Error: Invalid JSON response")
    sys.exit(1)

# Validate structure
if 'expected_field' not in data:
    print("Error: Missing expected field in response")
    sys.exit(1)
```

---

### 3. Log JSON for Observability

```python
import logging
import json

# Log as JSON for machine parsing
logger.info(json.dumps({
    'event': 'device_backup',
    'device': 'router1',
    'status': 'success',
    'duration_ms': 2345,
    'config_size_bytes': 45678
}))
```

---

### 4. Version Your JSON Schemas

```json
{
  "schema_version": "1.0",
  "device": {
    "hostname": "router1",
    "ip": "10.1.1.1"
  }
}
```

**Why:** If schema changes (new fields, different structure), you can handle different versions.

---

## 🚀 Complete Working Example: REST API Client

### Project Structure

```text
api-client/
├── api_client.py
├── config.json
└── README.md
```

### config.json

```json
{
  "api": {
    "base_url": "https://api.example.com/v1",
    "timeout": 30,
    "retry_attempts": 3
  },
  "credentials": {
    "api_key": "your_api_key_here"
  },
  "devices": [
    {
      "name": "router1",
      "ip": "10.1.1.1",
      "type": "cisco_ios"
    },
    {
      "name": "router2",
      "ip": "10.1.1.2",
      "type": "cisco_ios"
    }
  ]
}
```

### api_client.py

```python
#!/usr/bin/env python3
"""
Complete REST API client with JSON handling
Demonstrates best practices for network automation
"""

import json
import requests
import logging
from datetime import datetime
import time

# Configure logging with JSON formatter
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class NetworkAPIClient:
    """
    REST API client for network device management
    """

    def __init__(self, config_file='config.json'):
        """Initialize client with configuration from JSON file"""
        # Load configuration
        with open(config_file) as f:
            self.config = json.load(f)

        self.base_url = self.config['api']['base_url']
        self.timeout = self.config['api']['timeout']
        self.retry_attempts = self.config['api']['retry_attempts']
        self.api_key = self.config['credentials']['api_key']

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        })

    def _make_request(self, method, endpoint, **kwargs):
        """
        Make HTTP request with retry logic
        """
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(self.retry_attempts):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs
                )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                logger.error(json.dumps({
                    'event': 'http_error',
                    'status_code': e.response.status_code,
                    'url': url,
                    'attempt': attempt + 1
                }))

                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(json.dumps({
                    'event': 'request_error',
                    'error': str(e),
                    'url': url,
                    'attempt': attempt + 1
                }))

                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def get_device_info(self, device_name):
        """Get device information from API"""
        logger.info(json.dumps({
            'event': 'get_device_info',
            'device': device_name,
            'timestamp': datetime.utcnow().isoformat()
        }))

        data = self._make_request('GET', f'devices/{device_name}')
        return data

    def update_device_config(self, device_name, config):
        """Update device configuration via API"""
        logger.info(json.dumps({
            'event': 'update_device_config',
            'device': device_name,
            'timestamp': datetime.utcnow().isoformat()
        }))

        # Prepare JSON payload
        payload = {
            'device': device_name,
            'config': config,
            'timestamp': datetime.utcnow().isoformat()
        }

        data = self._make_request(
            'PUT',
            f'devices/{device_name}/config',
            json=payload
        )

        return data

def main():
    """Main function"""
    # Initialize API client
    client = NetworkAPIClient('config.json')

    # Process devices from config
    for device in client.config['devices']:
        try:
            # Get device info
            info = client.get_device_info(device['name'])

            logger.info(json.dumps({
                'event': 'device_info_retrieved',
                'device': device['name'],
                'status': 'success'
            }))

        except Exception as e:
            logger.error(json.dumps({
                'event': 'device_info_failed',
                'device': device['name'],
                'error': str(e)
            }))

if __name__ == "__main__":
    main()
```

---

## 📚 Additional Resources

- **[JSON Official Specification](https://www.json.org/)** — Full JSON specification
- **[Python json Module Documentation](https://docs.python.org/3/library/json.html)** — Official Python JSON docs
- **[JSON Schema](https://json-schema.org/)** — Schema validation specification
- **[Requests Library](https://requests.readthedocs.io/)** — HTTP requests with JSON
- **[ijson Documentation](https://pypi.org/project/ijson/)** — Streaming JSON parser

---

## 🎯 Key Takeaways

- ✅ **JSON is the API language** — Every modern network API uses JSON
- ✅ **Compact and efficient** — Ideal for network transmission and storage
- ✅ **Machine-first format** — Designed for programmatic access
- ✅ **Structured logging** — Makes logs queryable and analyzable
- ✅ **Schema validation** — Ensure data integrity with JSON Schema
- ✅ **Performance matters** — Use streaming for large files, ujson for speed

---

## 🎓 Next Steps

You've mastered JSON! Continue your data modelling journey:

1. **[Jinja2 Configuration Templates](./jinja2-configuration-templates.md)** (Recommended Next)
   - Combine YAML/JSON data with Jinja2 templates
   - Generate device configurations dynamically
   - Template-driven automation

2. **[Nornir Fundamentals](./nornir-fundamentals.md)**
   - Use JSON for result aggregation
   - Parallel execution at scale

3. **[PyATS Network Validation](./pyats-network-validation.md)**
   - Parse device output to JSON-like structures
   - Automated validation patterns

4. **[Structured Logging for Network Automation](./structured-logging-network-automation.md)**
   - Production logging patterns with JSON
   - Observability and monitoring

---

> **Remember:** JSON is the data exchange format for modern networks. Master it for API integrations, structured logging, and data-driven automation.

[← Back to YAML Tutorial](./yaml-data-modeling-network-automation.md) | [Continue to Jinja2 Tutorial →](./jinja2-configuration-templates.md)
