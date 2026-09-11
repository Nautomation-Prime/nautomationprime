---
title: Advanced Nornir Patterns
description: Master advanced Nornir patterns for enterprise deployment - custom plugins, middleware, multi-vendor support, memory optimisation, and testing.
tags:
  - Intermediate
  - Nornir
  - Advanced
  - Patterns
  - Production
  - Tutorial
---

## Advanced Nornir Patterns: Production-Grade Architecture

## "From Working Scripts to Enterprise Systems — Advanced Patterns for Real Deployments"

You've now built functional Nornir automation ([Tutorial #2](./nornir-fundamentals.md)) and enterprise-grade systems ([Tutorial #3](./enterprise-config-backup-nornir.md)). But there's still a gap between "working for your test network" and "reliable across thousands of devices managed by multiple teams."

This tutorial covers the **advanced patterns** used in production Nornir deployments at scale.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ Custom inventory plugins (Netbox integration)
- ✅ Middleware and execution pipelines
- ✅ Advanced error handling, retry logic, and circuit breakers
- ✅ State management across tasks
- ✅ Memory optimisation for 10,000+ devices
- ✅ Multi-vendor device support
- ✅ Testing and mocking Nornir tasks
- ✅ Debugging complex workflows
- ✅ Performance profiling and bottleneck identification
- ✅ Integration with external systems (APIs, databases, message queues)

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [Tutorial #3: Enterprise Config Backup](./enterprise-config-backup-nornir.md)** — Understand complex task composition
- ✅ Comfortable with Python classes and inheritance
- ✅ Understanding of HTTP requests and APIs
- ✅ Familiar with logging and error handling patterns
- ✅ Optional: Understanding of decorators and metaclasses

### Required Software

```bash
# Add to your existing Nornir environment
pip install requests pytest pytest-mock netbox-api
```

---

## 📚 Quick Reference: Which Pattern Do I Need?

| Challenge | Pattern | Benefit |
| :--- | :--- | :--- |
| Inventory always out-of-sync | Pattern 1 | Single source of truth |
| Repetitive logging/validation | Pattern 2 | DRY, automatic preprocessing |
| Devices timeout or fail | Pattern 3 | Automatic recovery |
| Supporting multiple vendors | Pattern 5 | One system for all devices |
| Managing 10,000+ devices | Pattern 6 | Unlimited scale |
| Quality assurance | Pattern 7 | Prevent regressions |
| Identifying bottlenecks | Pattern 10 | Know what to optimise |

---

## 🏗️ Pattern 1: Custom Inventory Plugin

Instead of YAML files, source inventory from **Netbox** (your network CMDB):

### Problem Being Solved

Hardcoded inventory doesn't scale:

- Manual updates
- Inconsistent with source of truth
- No integration with change management

### Solution: Netbox Plugin

Create `plugins/netbox_inventory.py`:

```python
"""
Custom Nornir inventory plugin for Netbox
Fetches devices from Netbox API instead of YAML files
"""

from nornir.core.inventory import (
    Inventory,
    Group,
    Host,
    Groups,
    Hosts,
    Defaults,
    ParentGroups,
)
from nornir.core.plugins.inventory import InventoryPluginRegister
import requests
from typing import Any, Dict, Optional

class NetboxInventory:
    """
    Fetch inventory from Netbox
    Credentials from environment variables
    """
    
    def __init__(
        self,
        nb_url: str,
        nb_token: str,
        filters: Optional[Dict[str, str]] = None,
    ):
        """
        Args:
            nb_url: Netbox API URL (e.g., https://netbox.yourcompany.com/api/)
            nb_token: Netbox API token
            filters: Query filters (e.g., {"site": "New York"})
        """
        self.nb_url = nb_url
        self.nb_token = nb_token
        self.filters = filters or {}
    
    def load(self) -> Inventory:
        """Fetch devices from Netbox and return Nornir Inventory"""
        
        # Fetch devices from Netbox API
        headers = {"Authorization": f"Token {self.nb_token}"}
        params = self.filters
        
        response = requests.get(
            f"{self.nb_url}dcim/devices/",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        devices = response.json()['results']
        
        # Build Nornir inventory
        hosts = {}
        groups = {}
        defaults = Defaults()
        
        for device in devices:
            name = device['name']
            primary_ip = device.get('primary_ip') or {}
            ip = primary_ip.get('address', name).split('/')[0]
            device_type = device.get('device_type', {}).get('model', '').lower()
            site = device.get('site', {}).get('name', 'unknown')
            
            # Determine Netmiko device type from Netbox device type
            if 'cat' in device_type or 'switch' in device_type:
                nornir_device_type = 'cisco_ios'
            elif 'router' in device_type:
                nornir_device_type = 'cisco_ios'
            elif '3850' in device_type:
                nornir_device_type = 'cisco_ios'
            else:
                nornir_device_type = 'cisco_ios'  # Default
            
            # Create groups if needed
            if site not in groups:
                groups[site] = Group(name=site)
            
            # Create host
            hosts[name] = Host(
                name=name,
                hostname=ip,
                platform=nornir_device_type,
                groups=ParentGroups([groups[site]]),
                data={
                    'netbox_id': device['id'],
                    'device_type_model': device_type,
                    'serial': device.get('serial_number', ''),
                }
            )
        
        return Inventory(
            hosts=Hosts(hosts),
            groups=Groups(groups),
            defaults=defaults
        )

# Register the plugin so Nornir can resolve it by name from the config file.
# This runs on import, so import this module before calling InitNornir().
InventoryPluginRegister.register("NetboxInventory", NetboxInventory)

# Usage in nornir_config.yaml:
# inventory:
#   plugin: NetboxInventory
#   options:
#     nb_url: ${NETBOX_URL}
#     nb_token: ${NETBOX_TOKEN}
#     filters:
#       site: "New York"
```

### Using the Plugin

Update your `nornir_config.yaml` (reference the plugin by its **registered name**, not a dotted path):

```yaml
---
runner:
  plugin: threaded
  options:
    num_workers: 10
inventory:
  plugin: NetboxInventory
  options:
    nb_url: "https://netbox.yourcompany.com/api/"
    nb_token: "${NETBOX_API_TOKEN}"
    filters:
      site: "New York"  # Optional filter
```

Then import the plugin module before initialising Nornir so its
`InventoryPluginRegister.register(...)` call runs:

```python
import plugins.netbox_inventory  # noqa: F401  (registers "NetboxInventory")
from nornir import InitNornir

nr = InitNornir(config_file="nornir_config.yaml")
```

**Benefits:**

- Inventory always matches Netbox (single source of truth)
- Automatic device discovery
- No manual YAML maintenance
- Filter options (by site, role, status, etc.)

### Gotchas & Solutions for Pattern 1

**Gotcha 1A: "Token Expired" error during backup**
    - **Root cause:** Netbox token rotated while Nornir was running
    - **Solution:** Reload inventory on each run instead of caching

**Gotcha 1B: Missing "primary_ip" in Netbox**
    - **Root cause:** Device added to Netbox but IP not assigned
    - **Solution:** Add fallback: `ip = (device.get('primary_ip') or {}).get('address', device['name'])`

**Gotcha 1C: Device types don't map correctly**
    - **Root cause:** Netbox device type names don't match vendor expectations
    - **Solution:** Build mapping table or use device role instead of type

---

## 🔄 Pattern 2: Middleware for Cross-Cutting Concerns

Middleware runs before and after each task. Perfect for:

- Logging
- Metrics collection
- Pre-flight validation
- Post-flight notifications

Create `middleware/example_middleware.py`:

```python
"""
Nornir middleware for logging, metrics, and validation
"""

from nornir import InitNornir
from nornir.core.inventory import Host
from nornir.core.task import Task, AggregatedResult, MultiResult
import logging
import time

logger = logging.getLogger(__name__)

# =====================================================================
# PRE-TASK MIDDLEWARE: Validation and setup
# =====================================================================

def validate_device(host: Host) -> None:
    """
    Pre-flight check before each host runs the task
    Validate device is reachable
    """
    logger.debug(f"[Pre-task] Validating {host.name}")
    
    # Example: Check if device credentials are set
    if not host.password:
        raise ValueError(f"No password configured for {host.name}")
    
    # Could also do ping check, device type validation, etc.

# =====================================================================
# POST-TASK MIDDLEWARE: Logging and metrics
# =====================================================================

def log_results(host: Host, result: MultiResult) -> None:
    """
    Post-task logging and metrics
    """
    status = "✓ Success" if not result.failed else "✗ Failed"
    
    logger.info(f"[Post-task] {host.name}: {status}")
    
    if result.failed:
        logger.error(f"[Error] {host.name}: {result[0].exception}")

def alert_on_failure(host: Host, result: MultiResult) -> None:
    """
    Alert (send Slack/email) if task fails
    """
    if result.failed:
        # Example: Send Slack notification
        # send_slack_alert(f"Task failed on {host.name}")
        logger.warning(f"Alert: Task failed on {host.name}")

class LoggingProcessor:
    """Nornir 3 processor for validation, logging, and alerts."""

    def task_started(self, task: Task) -> None:
        pass

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        pass

    def task_instance_started(self, task: Task, host: Host) -> None:
        validate_device(host)

    def task_instance_completed(self, task: Task, host: Host, result: MultiResult) -> None:
        log_results(host, result)
        alert_on_failure(host, result)

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        pass

    def subtask_instance_completed(self, task: Task, host: Host, result: MultiResult) -> None:
        pass

# =====================================================================
# Using Middleware in Nornir
# =====================================================================

def main():
    nornir = InitNornir(config_file="nornir_config.yaml")
    
    # Register middleware (runs on ALL tasks)
    nornir = nornir.with_processors([LoggingProcessor()])
    
    # Now all tasks get pre/post processing automatically
    results = nornir.run(task=my_task)
```

---

## ⚡ Pattern 3: Error Handling with Exponential Backoff

For unreliable networks, retry failed operations:

Create `tasks/resilient_tasks.py`:

```python
"""
Resilient tasks with automatic retry logic
"""

import time
import logging
from functools import wraps
from nornir.core.task import Task, Result

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Decorator for automatic retry with exponential backoff
    
    Usage:
        @retry_on_failure(max_retries=3, backoff_factor=2.0)
        def my_task(task):
            # This will retry 3 times if it fails
    """
    def decorator(func):
        @wraps(func)
        def wrapper(task: Task, *args, **kwargs) -> Result:
            host = task.host
            attempt = 0
            last_exception = None
            
            while attempt < max_retries:
                try:
                    attempt += 1
                    logger.info(f"[{host.name}] Attempt {attempt}/{max_retries}")
                    
                    # Execute task
                    result = func(task, *args, **kwargs)
                    
                    if not result.failed:
                        if attempt > 1:
                            logger.info(f"[{host.name}] Succeeded on attempt {attempt}")
                        return result
                    else:
                        last_exception = result.exception
                        
                except Exception as e:
                    last_exception = e
                
                # Wait before retry (exponential backoff)
                if attempt < max_retries:
                    wait_time = backoff_factor ** (attempt - 1)
                    logger.warning(f"[{host.name}] Retry in {wait_time}s...")
                    time.sleep(wait_time)
            
            # All retries failed
            logger.error(f"[{host.name}] Failed after {max_retries} attempts")
            return Result(
                host=task.host,
                result={'success': False, 'error': str(last_exception)},
                failed=True
            )
        
        return wrapper
    return decorator

# Usage:
@retry_on_failure(max_retries=3, backoff_factor=1.5)
def resilient_backup(task: Task) -> Result:
    # This automatically retries on failure
    # Waits: 1.5^0=1s, then 1.5^1=1.5s, then 1.5^2=2.25s between retries
    pass
```

### Gotchas & Solutions for Pattern 3

**Gotcha 3A: Retrying idempotent tasks**
    - **Problem:** If a task partially succeeds (config saved but validation failed), retry saves duplicate
    - **Solution:** Make tasks idempotent (safe to run twice) OR track state (is this already done?)

**Gotcha 3B: Exponential backoff is too aggressive**
    - **Problem:** Waiting 2^5=32 seconds between retries = slow job
    - **Solution:** Use `backoff_factor=1.2` (12% increase) instead of 2.0 (100% increase)

**Gotcha 3C: Retrying won't help if issue is permanent**
    - **Problem:** Device password expired = will never work, just wastes time
    - **Solution:** Add circuit breaker pattern (stop retrying if error is permanent)

---

## 💾 Pattern 4: Managing State Across Tasks

Tasks need to share data. Use task results effectively:

```python
"""
State management across multi-step workflows
"""

from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command

def step1_backup(task: Task) -> Result:
    """First step: backup config"""
    result = task.run(netmiko_send_command, command_string="show running-config")
    config = result[0].result
    
    return Result(
        host=task.host,
        result={
            'config': config,
            'timestamp': datetime.now()
        }
    )

def step2_validate(task: Task, config_dict: dict) -> Result:
    """Second step: validate config"""
    # Nornir passes the same dict to every host, so extract this host's config
    config = config_dict[task.host.name]
    is_valid = len(config) > 100
    
    return Result(
        host=task.host,
        result={'valid': is_valid}
    )

# Orchestration:
def main():
    nornir = InitNornir(config_file="nornir_config.yaml")
    
    # Step 1: Backup
    backup_results = nornir.run(task=step1_backup)
    
    # Step 2: Validate (pass data from step 1)
    config_data = {
        host_name: backup_results[host_name][0].result['config']
        for host_name in backup_results.keys()
    }
    
    validate_results = nornir.run(
        task=step2_validate,
        config_dict=config_data
    )
```

---

## 🚀 Pattern 5: Multi-Vendor Support

Support Cisco, Arista, Juniper, Palo Alto in one system:

```python
"""
Multi-vendor task with platform abstraction
"""

from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command

VENDOR_CONFIGS = {
    'cisco_ios': 'show running-config',
    'cisco_nxos': 'show running-config',
    'arista_eos': 'show running-config',
    'juniper_junos': 'show configuration',
    'paloalto_panos': 'show config running',
}

def backup_multivendor(task: Task) -> Result:
    """Backup any vendor device"""
    
    device_type = task.host.data.get('device_type', 'cisco_ios')
    
    # Get vendor-specific command
    command = VENDOR_CONFIGS.get(device_type)
    
    if not command:
        return Result(
            host=task.host,
            result={'error': f'Unknown device type: {device_type}'},
            failed=True
        )
    
    try:
        result = task.run(netmiko_send_command, command_string=command)
        config = result[0].result
        
        return Result(
            host=task.host,
            result={'config': config, 'vendor': device_type}
        )
    except Exception as e:
        return Result(
            host=task.host,
            result={'error': str(e)},
            failed=True
        )
```

### Gotchas & Solutions for Pattern 5

**Gotcha 5A: Device type string doesn't match**
    - **Problem:** Netbox says "catalyst", Netmiko expects "cisco_ios"
    - **Solution:** Build normalization map: `DeviceTypeMap = {'catalyst': 'cisco_ios', ...}`

**Gotcha 5B: Command outputs differently between vendors**
    - **Problem:** `show running-config` vs `show configuration` = different format
    - **Solution:** Normalize output parser (strip vendor-specific headers)

**Gotcha 5C: Not all vendors support all features**
    - **Problem:** You check for `spanning-tree` on a Junos router (doesn't use STP)
    - **Solution:** Make compliance checks vendor-aware

---

## 📈 Pattern 6: Memory Optimisation for 10k+ Devices

When managing thousands of devices, memory becomes critical:

```python
"""
Memory-efficient processing for large-scale operations
"""

from nornir import InitNornir
import gc

def backup_large_network():
    """Process 10,000+ devices without memory issues"""
    
    nornir = InitNornir(config_file="nornir_config.yaml")
    
    # Batch processing instead of loading all at once
    batch_size = 100
    total_devices = len(nornir.inventory.hosts)
    
    for i in range(0, total_devices, batch_size):
        # Process one batch
        device_names = list(nornir.inventory.hosts.keys())[i:i+batch_size]
        batch = nornir.filter(filter_func=lambda h: h.name in device_names)
        
        results = batch.run(task=backup_config)
        
        # Process results immediately (don't accumulate)
        for device_name, result in results.items():
            save_to_database(device_name, result)
        
        # Clear memory
        del results
        gc.collect()
    
    logger.info(f"Completed backup of {total_devices} devices")

def save_to_database(device_name, result):
    """Stream results to database instead of holding in memory"""
    # Write to database immediately
    conn = sqlite3.connect("backup.db")
    cursor = conn.cursor()
    # ... save logic ...
    conn.close()
```

**Benefits:**

- Process unlimited devices
- Memory usage stays constant
- Results streamed to storage
- Progress saved in real-time

### Gotchas & Solutions for Pattern 6

**Gotcha 6A: Batch size is wrong**
    - **Problem:** Batch size of 1000 = memory spike again
    - **Solution:** Start with 100, monitor memory. Formula: `batch_size = available_ram_mb / (config_size_mb * 2)`

**Gotcha 6B: Losing progress on failure**
    - **Problem:** Batch 50 of 100 fails, entire batch lost
    - **Solution:** Save `backup_id` to database immediately, mark status as "saved" even if later steps fail

**Gotcha 6C: Database writes become the bottleneck**
    - **Problem:** Fast backups, slow database writes = queue backs up
    - **Solution:** Use connection pooling, batch database inserts (50 at a time), or use async DB driver

---

## 🧪 Pattern 7: Testing Nornir Tasks

Create `tests/test_tasks.py`:

```python
"""
Unit tests for Nornir tasks
Using pytest and mocking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from nornir.core.task import Result
from nornir.core.inventory import Host, Group
from tasks.enterprise_backup import backup_config, compliance_check

@pytest.fixture
def mock_host():
    """Create a mock host for testing"""
    host = Mock(spec=Host)
    host.name = "test-router"
    host.hostname = "192.168.1.1"
    host.password = "testpass"
    host.data = {'device_type': 'cisco_ios'}
    host.groups = []
    return host

@pytest.fixture
def mock_task(mock_host):
    """Create a mock Nornir task"""
    from nornir.core.task import Task
    task = Mock(spec=Task)
    task.host = mock_host
    task.run = Mock()
    return task

def test_backup_config_success(mock_task):
    """Test successful config backup"""
    
    # Mock the netmiko response
    test_config = "hostname test-router\n" * 100  # Simulated config
    mock_result = Mock()
    mock_result.result = test_config
    
    mock_task.run.return_value = [mock_result]
    
    # Call the task
    result = backup_config(mock_task)
    
    # Assertions
    assert result.result['success'] == True
    assert result.result['config'] == test_config
    assert len(result.result['hash']) == 64  # SHA256 hash length

def test_backup_config_failure(mock_task):
    """Test backup failure handling"""
    
    # Mock a failed connection
    mock_task.run.side_effect = Exception("Connection timeout")
    
    # Call the task
    result = backup_config(mock_task)
    
    # Assertions
    assert result.failed == True
    assert result.result['success'] == False

def test_compliance_check():
    """Test compliance scoring"""
    
    # Create a compliant config
    compliant_config = """
    banner motd # Authorized Access Only #
    logging 10.1.1.1
    enable secret 5 $1$12345...
    access-list 1 permit any
    ntp server 8.8.8.8
    snmp-server host 10.1.1.2
    """
    
    # Create a non-compliant config
    non_compliant_config = "hostname test-device\n"
    
    # Test with mock task
    from unittest.mock import patch
    
    with patch('sqlite3.connect'):
        mock_task = Mock()
        mock_task.host.name = "test"
        
        # Example assertions (call the real function in your test suite)
        result_good = compliance_check(mock_task, {"test": compliant_config})
        result_bad = compliance_check(mock_task, {"test": non_compliant_config})
        
        assert result_good.result['score'] > result_bad.result['score']
        assert result_bad.result['score'] < 70

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run tests:**

```bash
pytest tests/test_tasks.py -v
```

---

## 🔍 Pattern 8: Debugging Complex Workflows

Enable detailed logging for troubleshooting:

```python
"""
Debug mode for complex Nornir workflows
"""

import logging
import sys

def setup_debug_logging():
    """Configure verbose logging for debugging"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console.setFormatter(formatter)
    root_logger.addHandler(console)
    
    # File handler
    file_handler = logging.FileHandler('nornir_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.debug("Debug logging enabled")

# In main.py:
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    if args.debug:
        setup_debug_logging()
    
    # ... rest of code ...
```

---

## 🎯 Pattern 9: Integration with External Systems

Trigger external systems based on Nornir results:

```python
"""
Integrations: Netbox, ServiceNow, Slack, etc.
"""

import requests
import json

class ExternalIntegrations:
    """Handle integrations with external systems"""
    
    @staticmethod
    def update_netbox_device_status(device_id: int, status: str):
        """Update device status in Netbox"""
        headers = {"Authorization": f"Token {NETBOX_TOKEN}"}
        url = f"{NETBOX_URL}dcim/devices/{device_id}/"
        
        data = {'status': status}
        response = requests.patch(url, json=data, headers=headers)
        return response.status_code == 200
    
    @staticmethod
    def create_servicenow_incident(device_name: str, issue: str):
        """Create incident in ServiceNow"""
        # Implementation here
        pass
    
    @staticmethod
    def send_slack_notification(message: str, webhook_url: str):
        """Send notification to Slack"""
        payload = {'text': message}
        requests.post(webhook_url, json=payload)

# Usage in tasks:
def task_with_integration(task: Task) -> Result:
    try:
        # ... task logic ...
        result_data = {'success': True}
    except Exception as e:
        # Alert external systems
        ExternalIntegrations.send_slack_notification(
            f"Task failed on {task.host.name}: {str(e)}",
            SLACK_WEBHOOK_URL
        )
        result_data = {'success': False, 'error': str(e)}
    
    return Result(host=task.host, result=result_data)
```

---

## 📊 Pattern 10: Performance Profiling

Identify bottlenecks in your automation:

```python
"""
Profile Nornir task performance
"""

import cProfile
import pstats
import io
from contextlib import contextmanager

@contextmanager
def profile_task(task_name: str):
    """Context manager for profiling tasks"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        yield profiler
    finally:
        profiler.disable()
        
        # Print stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        print(f"\nProfile Results for {task_name}:")
        print(s.getvalue())

# Usage:
def main():
    with profile_task("backup_operation") as profiler:
        nornir = InitNornir(config_file="nornir_config.yaml")
        results = nornir.run(task=backup_config)
    
    # Output shows slowest operations -> optimise those first
```

---

## 📈 Performance Benchmarking for Your Network

Pattern 10 shows you how to profile code. But you also need to measure **actual performance** against your real devices:

### Benchmark Your Current System

Create `benchmark.py`:

```python
#!/usr/bin/env python3
"""
Benchmark your Nornir automation
Measure speed, resource usage, and identify bottlenecks
"""

import time
import psutil
import os
from nornir import InitNornir
from tasks.enterprise_backup import backup_config

class BenchmarkRunner:
    """Run and measure Nornir performance"""
    
    def __init__(self):
        self.metrics = {}
    
    def memory_usage(self):
        """Get current process memory in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def run_benchmark(self, task_name, task, workers=None):
        """Run task and measure performance"""
        
        # Initialize Nornir
        nr = InitNornir(config_file="nornir_config.yaml")
        
        if workers:
            nr.runner.num_workers = workers
        
        # Baseline memory
        mem_start = self.memory_usage()
        time_start = time.time()
        
        # Run task
        results = nr.run(task=task)
        
        # Measurements
        time_end = time.time()
        mem_end = self.memory_usage()
        
        failed = sum(1 for r in results.values() if r.failed)
        succeeded = len(results) - failed
        
        # Record metrics
        self.metrics[task_name] = {
            'total_devices': len(results),
            'succeeded': succeeded,
            'failed': failed,
            'duration_seconds': time_end - time_start,
            'memory_used_mb': mem_end - mem_start,
            'memory_peak_mb': mem_end,
            'devices_per_second': len(results) / (time_end - time_start),
            'workers': nr.runner.num_workers,
        }
        
        return self.metrics[task_name]
    
    def print_report(self):
        """Print benchmark results"""
        
        print("\n" + "="*70)
        print("BENCHMARK REPORT")
        print("="*70)
        
        for test_name, metrics in self.metrics.items():
            print(f"\n{test_name}:")
            print(f"  Devices: {metrics['total_devices']} ({metrics['succeeded']} succeeded, {metrics['failed']} failed)")
            print(f"  Duration: {metrics['duration_seconds']:.2f} seconds")
            print(f"  Throughput: {metrics['devices_per_second']:.1f} devices/second")
            print(f"  Memory used: {metrics['memory_used_mb']:.1f} MB")
            print(f"  Peak memory: {metrics['memory_peak_mb']:.1f} MB")
            print(f"  Workers: {metrics['workers']}")

# Usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Nornir configuration")
    parser.add_argument('--workers', type=int, nargs='+', default=[5, 10, 20],
                        help='Worker counts to test (default: 5 10 20)')
    parser.add_argument('--task', default='backup_config',
                        help='Task to benchmark (default: backup_config)')
    args = parser.parse_args()
    
    runner = BenchmarkRunner()
    
    # Test with different worker counts
    for worker_count in args.workers:
        print(f"Testing with {worker_count} workers...")
        runner.run_benchmark(
            f"backup_config ({worker_count} workers)",
            task=backup_config,
            workers=worker_count
        )
    
    runner.print_report()
```

**Run it:**

```bash
python benchmark.py --workers 5 10 20 50
```

**Expected output:**

```bash
======================================================================
BENCHMARK REPORT
======================================================================

backup_config (5 workers):
  Devices: 100 (100 succeeded, 0 failed)
  Duration: 24.35 seconds
  Throughput: 4.1 devices/second
  Memory used: 145.2 MB
  Peak memory: 287.3 MB
  Workers: 5

backup_config (10 workers):
  Devices: 100 (100 succeeded, 0 failed)
  Duration: 12.18 seconds
  Throughput: 8.2 devices/second
  Memory used: 148.1 MB
  Peak memory: 295.4 MB
  Workers: 10

backup_config (20 workers):
  Devices: 100 (100 succeeded, 0 failed)
  Duration: 6.45 seconds
  Throughput: 15.5 devices/second
  Memory used: 151.3 MB
  Peak memory: 312.1 MB
  Workers: 20

backup_config (50 workers):
  Devices: 100 (100 succeeded, 0 failed)
  Duration: 5.82 seconds
  Throughput: 17.2 devices/second
  Memory used: 148.9 MB
  Peak memory: 398.2 MB
  Workers: 50
```

### Analyzing Results

**What this tells you:**

1. **Throughput plateau** — In example above, 20→50 workers only 1.7x faster (diminishing returns)

   - Optimal: 20 workers
   - More workers = more overhead, less benefit

2. **Memory scaling** — Memory increases with worker count

   - 5 workers = 287 MB peak
   - 50 workers = 398 MB peak
   - Formula: `peak_memory = baseline + (workers × per_worker_overhead)`

3. **Device latency** — Devices/second tells you network latency

   - 4.1 dev/sec with 5 workers = ~244ms per device
   - Suggests 244ms SSH+command time (normal for Cisco devices)

### Finding Your Sweet Spot

```python
# Optimal calculation
optimal_workers = device_count / devices_per_second_single_threaded
max_memory_available_mb = 2048

if peak_memory > max_memory_available_mb:
    optimal_workers = max_memory_available_mb // (peak_memory // workers)

print(f"Recommended workers: {optimal_workers}")
```

### Continuous Benchmarking

Track performance over time:

```python
import json
from datetime import datetime

def save_benchmark_history(metrics, filename='benchmark_history.json'):
    """Save benchmark results for historical comparison"""
    
    try:
        with open(filename, 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    
    metrics['timestamp'] = datetime.now().isoformat()
    history.append(metrics)
    
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)

# In main:
benchmark_results = runner.metrics['backup_config (10 workers)']
save_benchmark_history(benchmark_results)

# Later, compare:
# Was performance 2 weeks ago 5 devices/sec? Is it now 4 devices/sec?
# Something changed - investigate!
```

### Real-World Benchmarking Scenarios

## **Scenario 1: Adding 100 new devices**

```python
# Before addition
before = {"devices": 500, "duration": "50s", "throughput": "10 dev/sec"}

# After addition
after = {"devices": 600, "duration": "55s", "throughput": "10.9 dev/sec"}

# Analysis: Throughput stayed same → network is bottleneck, not code
```

## **Scenario 2: Database writes getting slower**

```python
# Week 1: save_config task = 2s
# Week 4: save_config task = 8s

# Database has 30,000 backups → query scan is slower
# Solution: Add database index on device_name, backup_timestamp
```

## **Scenario 3: Memory leak detection**

```python
# First run: peak memory = 300 MB
# Second run: peak memory = 400 MB
# Third run: peak memory = 520 MB

# Memory not being freed between tasks
# Solution: Explicit garbage collection, check for circular references
```

---

## 🎓 Key Patterns Summary

| Pattern | Use Case | Benefit |
| :--- | :--- | :--- |
| Custom Inventory | Netbox integration | Single source of truth |
| Middleware | Cross-cutting concerns | DRY principle, reusability |
| Retry Logic | Unreliable networks | Automatic recovery |
| State Management | Multi-step workflows | Data coordination |
| Multi-vendor | Heterogeneous networks | One system for all vendors |
| Memory Optimisation | 10k+ devices | Unlimited scale |
| Testing | Quality assurance | Prevent regressions |
| Debugging | Troubleshooting | Fast issue resolution |
| Integrations | External systems | Workflow automation |
| Profiling | Performance tuning | Identify bottlenecks |

---

## 🎯 Connection to PRIME Framework & Consulting Services

These advanced patterns are what enable the **Implement** stage of the PRIME Framework to scale:

- **Pragmatic:** Use proven patterns, not experimental approaches
- **Transparent:** Logging, profiling, and metrics built-in
- **Reliable:** Error handling, retry logic, and testing ensure production readiness

**This is where consulting engagements live** — organisations pay for someone who knows these patterns and can architect systems correctly from the start.

---

## 🚀 Production Deployment Checklist

Before deploying to production:

### Infrastructure

- [ ] Credential vaulting (HashiCorp Vault, AWS Secrets Manager)
- [ ] Job scheduling (Cron, Kubernetes CronJob, Temporal)
- [ ] Message queue for distributed tasks (RabbitMQ, Redis)
- [ ] Monitoring (Prometheus metrics, Grafana dashboards)
- [ ] Logging aggregation (ELK stack, Splunk)

### Code Quality

- [ ] Unit tests with >80% coverage
- [ ] Integration tests on staged network
- [ ] Code review process
- [ ] CI/CD pipeline (GitHub Actions, GitLab CI)

### Operations

- [ ] Runbooks for common failures
- [ ] Alerting on task failures
- [ ] Audit logging for compliance
- [ ] Change management integration
- [ ] Rollback procedures

### Observability

- [ ] Structured logging
- [ ] Performance metrics
- [ ] Error tracking (Sentry, Rollbar)
- [ ] Health checks

---

## 🎓 You've Mastered

After completing all 4 intermediate tutorials:

✅ **Architecture Decisions** — When and why to use Nornir  
✅ **Core Concepts** — Tasks, inventory, parallel execution  
✅ **Production Systems** — Database integration, compliance, change detection  
✅ **Advanced Patterns** — Plugins, middleware, multi-vendor, testing  
✅ **Enterprise Scale** — Memory optimisation, integrations, profiling  

You're now equipped to:

- Build systems from scratch
- Debug complex automation
- Optimise for performance
- Scale to enterprise size
- Lead automation initiatives

---

## 📚 Next Steps: From Learning to Building

You've mastered advanced Nornir patterns used in enterprise deployments worldwide. Here's your path forward:

**Study Real Production Tools:**

1. **[Deep Dives](../../deep-dives/index.md)** — Review production automation built with these patterns
   - [CDP Network Audit](../../deep-dives/cdp-audit.md) — Threading, configuration, and scalable discovery
   - [Access Switch Audit](../../deep-dives/access-switch-audit.md) — Parallel device collection and intelligent parsing
   - See how experts implement the patterns you've just learned

2. **[Script Library](../../../scripts/index.md)** — Deploy production-ready tools using these patterns

    **Build and Scale:**

3. **[PRIME Framework](../../../prime-framework/index.md)** — Structure your automation projects for sustainable ROI
   - Pinpoint opportunities with measurable impact
   - Re-engineer workflows for maximum value
   - Implement with confidence using proven patterns
   - Measure results and empower your team

4. **[Services](../../../services.md)** — Consulting for enterprise automation at scale
   - Custom implementations
   - Team training and mentoring
   - Architecture reviews
   - Contact: [email](../../../about.md#contact)

---

## 💡 Final Thoughts

Nornir is a tool. **You're the craftsman.**

The patterns in this tutorial are battle-tested in real enterprises managing thousands of devices. They exist because they solve real problems. But the best pattern is the one that fits YOUR network, YOUR team, and YOUR constraints.

Use what works. Ignore what doesn't. Build systematically.

---

## 🤝 Got Questions or Insights?

Found a better pattern? Have a real-world use case?

We'd love to hear about it: [Contact Information](../../../about.md#contact)

---

[← Back to Intermediate Tutorials](./index.md) | [Ready for Expert Level?](../expert/index.md)
