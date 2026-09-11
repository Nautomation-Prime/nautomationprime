---
title: Health Checks & Pre-Flight Validation
description: Validate devices before deployment. Pre-flight checks prevent bad configurations from reaching production. Safe deployment starts with validation.
tags:
  - Health Checks
  - Validation
  - Pre-Flight
  - Network Automation
  - Intermediate
  - Safety
---

## Why Pre-Flight Matters

Pilots check instruments before takeoff. Network operators should validate before deployment.

**Without Pre-Flight Checks:**

- ❌ Deploy to down device (wasted time)
- ❌ Deploy to already-misconfigured device (adds complexity)
- ❌ Deploy when bandwidth is saturated (timeouts)
- ❌ Deploy to device with low disk space (changes fail)
- ❌ Deploy to device with high CPU (risk of crash)

**With Pre-Flight Checks:**

- ✅ Skip down devices, report status
- ✅ Know if device is in clean state
- ✅ Only deploy when safe
- ✅ Predictable success rate

**Pre-flight checks are the first line of defense against failed deployments.**

---

## Pattern 1: Device Health Checks

### The Implementation

```python
# src/health_checks.py
from dataclasses import dataclass
from enum import Enum
import re

class HealthStatus(Enum):
    """Device health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class HealthCheckResult:
    """Result of a health check."""
    check_name: str
    status: HealthStatus
    message: str
    details: dict = None

class DeviceHealthChecker:
    """Validate device health before deployment."""
    
    def __init__(self, device):
        self.device = device
        self.checks = []
    
    def check_device_reachable(self) -> HealthCheckResult:
        """Check if device responds to ping/SSH."""
        try:
            output = self.device.send_command("ping 8.8.8.8 repeat 1")
            if "100 percent" in output or "100%" in output or "0% packet loss" in output:
                return HealthCheckResult(
                    check_name="device_reachable",
                    status=HealthStatus.HEALTHY,
                    message="Device is reachable"
                )
            return HealthCheckResult(
                check_name="device_reachable",
                status=HealthStatus.WARNING,
                message="Device has connectivity issues",
                details={"ping_output": output[:100]}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name="device_reachable",
                status=HealthStatus.CRITICAL,
                message=f"Cannot reach device: {str(e)}"
            )
    
    def check_disk_space(self, min_percent_free=10) -> HealthCheckResult:
        """Check device has sufficient free disk space."""
        try:
            output = self.device.send_command("show disk:")
            
            # Parse disk usage (device-specific)
            lines = output.split('\n')
            for line in lines:
                if 'Kbytes total' in line:
                    # Extract percentages
                    parts = line.split()
                    # (This is simplified; real parsing depends on device OS)
                    
                    # If we get here, device has space
                    return HealthCheckResult(
                        check_name="disk_space",
                        status=HealthStatus.HEALTHY,
                        message=f"Disk space available",
                        details={"output": line}
                    )
            
            return HealthCheckResult(
                check_name="disk_space",
                status=HealthStatus.WARNING,
                message="Could not parse disk usage"
            )
        except Exception as e:
            return HealthCheckResult(
                check_name="disk_space",
                status=HealthStatus.CRITICAL,
                message=f"Cannot check disk space: {str(e)}"
            )
    
    def check_cpu_usage(self, max_percent=80) -> HealthCheckResult:
        """Check device CPU is not overloaded."""
        try:
            output = self.device.send_command("show processes cpu")
            
            # Look for CPU usage line
            for line in output.split('\n'):
                if 'CPU utilization' in line:
                    # Parse first CPU percentage (e.g. "5%/0%" or "7%;")
                    match = re.search(r"(\d+(?:\.\d+)?)%", line)
                    if not match:
                        continue
                    cpu_percent = float(match.group(1))
                    
                    if cpu_percent < max_percent:
                        return HealthCheckResult(
                            check_name="cpu_usage",
                            status=HealthStatus.HEALTHY,
                            message=f"CPU usage OK ({cpu_percent}%)"
                        )
                    else:
                        return HealthCheckResult(
                            check_name="cpu_usage",
                            status=HealthStatus.WARNING,
                            message=f"CPU usage high ({cpu_percent}%)"
                        )
            
            return HealthCheckResult(
                check_name="cpu_usage",
                status=HealthStatus.WARNING,
                message="Could not parse CPU usage"
            )
        except Exception as e:
            return HealthCheckResult(
                check_name="cpu_usage",
                status=HealthStatus.CRITICAL,
                message=f"Cannot check CPU: {str(e)}"
            )
    
    def check_memory_usage(self, max_percent=80) -> HealthCheckResult:
        """Check device memory is not exhausted."""
        try:
            output = self.device.send_command("show memory")
            
            for line in output.split('\n'):
                if 'Processor' in line:
                    # Parse memory (simplified)
                    parts = line.split()
                    # Real implementation depends on device OS
                    
                    return HealthCheckResult(
                        check_name="memory_usage",
                        status=HealthStatus.HEALTHY,
                        message="Memory available"
                    )
            
            return HealthCheckResult(
                check_name="memory_usage",
                status=HealthStatus.WARNING,
                message="Could not parse memory usage"
            )
        except Exception as e:
            return HealthCheckResult(
                check_name="memory_usage",
                status=HealthStatus.CRITICAL,
                message=f"Cannot check memory: {str(e)}"
            )
    
    def check_running_config_valid(self) -> HealthCheckResult:
        """Check running configuration is valid."""
        try:
            output = self.device.send_command("show running-config | include ERROR")
            
            if output.strip() == "":
                return HealthCheckResult(
                    check_name="config_valid",
                    status=HealthStatus.HEALTHY,
                    message="Running configuration is valid"
                )
            else:
                return HealthCheckResult(
                    check_name="config_valid",
                    status=HealthStatus.CRITICAL,
                    message="Running configuration has errors",
                    details={"errors": output}
                )
        except Exception as e:
            return HealthCheckResult(
                check_name="config_valid",
                status=HealthStatus.WARNING,
                message=f"Cannot validate config: {str(e)}"
            )
    
    def run_all_checks(self) -> list:
        """Run all health checks."""
        results = [
            self.check_device_reachable(),
            self.check_disk_space(),
            self.check_cpu_usage(),
            self.check_memory_usage(),
            self.check_running_config_valid(),
        ]
        return results
    
    def is_healthy(self, results: list, allow_warnings=True) -> bool:
        """
        Determine if device is healthy enough for deployment.
        
        Args:
            results: List of HealthCheckResult
            allow_warnings: Allow deployment if only warnings
        
        Returns:
            bool: True if device is healthy
        """
        critical = [r for r in results if r.status == HealthStatus.CRITICAL]
        
        if critical:
            return False
        
        if not allow_warnings:
            warnings = [r for r in results if r.status == HealthStatus.WARNING]
            return len(warnings) == 0
        
        return True
```

### Usage

```python
from netmiko import ConnectHandler
from health_checks import DeviceHealthChecker

device = ConnectHandler(
    device_type="cisco_ios",
    host="10.0.0.1",
    username="admin",
    password="password"
)

checker = DeviceHealthChecker(device)
results = checker.run_all_checks()

# Print results
for result in results:
    status_icon = "✓" if result.status.value == "healthy" else "⚠" if result.status.value == "warning" else "✗"
    print(f"{status_icon} {result.check_name}: {result.message}")

# Decide whether to deploy
if checker.is_healthy(results, allow_warnings=True):
    print("\n✓ Device is healthy, proceeding with deployment")
    # deploy_to_device()
else:
    print("\n✗ Device has critical issues, skipping deployment")
    # Log and skip
```

---

## Pattern 2: Configuration Backup Before Deployment

### The Implementation

```python
# src/config_backup.py
import json
from datetime import datetime, timezone
from pathlib import Path

class ConfigurationBackup:
    """Backup device configuration before changes."""
    
    def __init__(self, device, backup_dir="config_backups"):
        self.device = device
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_file = None
    
    def backup_running_config(self):
        """Backup current running configuration."""
        try:
            config = self.device.send_command("show running-config")
            
            # Create backup file
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = self.backup_dir / f"{self.device.host}_{timestamp}.cfg"
            
            with open(filename, 'w') as f:
                f.write(config)
            
            self.backup_file = filename
            
            return {
                "status": "success",
                "filename": str(filename),
                "lines": len(config.split('\n'))
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def get_config_checksum(self):
        """Get MD5 checksum of running configuration."""
        try:
            import hashlib
            config = self.device.send_command("show running-config")
            checksum = hashlib.md5(config.encode()).hexdigest()
            return checksum
        except Exception as e:
            return None
```

---

## Pattern 3: Nornir Pre-Flight Tasks

```python
# src/nornir_preflight_tasks.py
from nornir import InitNornir
from nornir.core.task import Task, Result
from health_checks import DeviceHealthChecker, HealthStatus
from config_backup import ConfigurationBackup

def preflight_validation(task: Task) -> Result:
    """
    Nornir task: Validate device before deployment.
    """
    try:
        device = task.host.get_connection("netmiko", task.nornir.config)
        checker = DeviceHealthChecker(device)
        backup = ConfigurationBackup(device)
        
        # Run health checks
        health_results = checker.run_all_checks()
        
        # Determine status
        critical_issues = [
            r for r in health_results 
            if r.status == HealthStatus.CRITICAL
        ]
        
        if critical_issues:
            return Result(
                host=task.host,
                failed=True,
                result={
                    "preflight_status": "FAILED",
                    "critical_issues": [
                        {
                            "check": r.check_name,
                            "message": r.message
                        }
                        for r in critical_issues
                    ]
                }
            )
        
        # Backup configuration
        backup_result = backup.backup_running_config()
        
        if backup_result["status"] == "failed":
            return Result(
                host=task.host,
                failed=True,
                result={
                    "preflight_status": "FAILED",
                    "reason": "Could not backup configuration",
                    "error": backup_result.get("error")
                }
            )
        
        return Result(
            host=task.host,
            result={
                "preflight_status": "PASSED",
                "health_checks": [
                    {
                        "check": r.check_name,
                        "status": r.status.value,
                        "message": r.message
                    }
                    for r in health_results
                ],
                "backup": backup_result
            }
        )
    
    except Exception as e:
        return Result(
            host=task.host,
            failed=True,
            result={"error": str(e)}
        )

# Usage
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=preflight_validation)

# Filter: Only deploy to passing devices
passing_devices = [
    hostname for hostname, result in results.items()
    if not result[0].failed and result[0].result["preflight_status"] == "PASSED"
]

print(f"✓ {len(passing_devices)} devices passed pre-flight validation")
print(f"✗ {len(results) - len(passing_devices)} devices failed pre-flight")

# Deploy only to passing devices
# nr = InitNornir(config_file="config.yaml")
# nr.inventory.hosts = {h: nr.inventory.hosts[h] for h in passing_devices}
# nr.run(task=deploy_to_devices)
```

---

## Pattern 4: Sanity Tests After Deployment

### The Implementation

```python
# src/sanity_tests.py
class SanityTestResult:
    def __init__(self, test_name: str, passed: bool, message: str):
        self.test_name = test_name
        self.passed = passed
        self.message = message

class SanityTests:
    """Verify deployment had expected effect."""
    
    def __init__(self, device):
        self.device = device
    
    def test_interfaces_still_up(self, expected_up=2) -> SanityTestResult:
        """Verify interfaces didn't break."""
        output = self.device.send_command("show ip interface brief")
        up_count = output.count(" UP ")
        
        if up_count >= expected_up:
            return SanityTestResult(
                "interfaces_up",
                True,
                f"{up_count} interfaces up (expected {expected_up})"
            )
        else:
            return SanityTestResult(
                "interfaces_up",
                False,
                f"Only {up_count} interfaces up (expected {expected_up})"
            )
    
    def test_config_saved(self) -> SanityTestResult:
        """Verify configuration was saved."""
        try:
            self.device.send_command("write memory")
            return SanityTestResult(
                "config_saved",
                True,
                "Configuration saved successfully"
            )
        except Exception as e:
            return SanityTestResult(
                "config_saved",
                False,
                f"Failed to save configuration: {str(e)}"
            )
    
    def test_device_responsive(self) -> SanityTestResult:
        """Verify device still responds to commands."""
        try:
            self.device.send_command("show version")
            return SanityTestResult(
                "device_responsive",
                True,
                "Device is responsive"
            )
        except Exception as e:
            return SanityTestResult(
                "device_responsive",
                False,
                f"Device not responsive: {str(e)}"
            )
```

---

## Best Practices

### 1. Fail Fast on Critical Issues

```python
# ✅ GOOD
def deploy_if_healthy(checker, results):
    if checker.is_healthy(results):
        deploy()
    else:
        return False  # Stop immediately

# ❌ BAD - Deploying despite critical issues
if has_critical_issues(results):
    log_warning("Issues detected but deploying anyway")
    deploy()  # 💥 Will fail
```

### 2. Backup Before Every Change

```python
# ✅ GOOD
backup.backup_running_config()
deploy_changes()

# ❌ BAD - No backup
deploy_changes()
# Now if something breaks, no recovery point
```

### 3. Test Your Health Checks

```python
def test_health_checker_detects_critical(mock_device):
    """Verify health checker catches real problems."""
    mock_device.send_command.side_effect = Exception("SSH timeout")
    
    checker = DeviceHealthChecker(mock_device)
    results = checker.run_all_checks()
    
    assert not checker.is_healthy(results)
```

---

## Summary

Pre-flight validation is critical:

- ✅ Check device health
- ✅ Backup configuration
- ✅ Run sanity tests
- ✅ Only deploy if safe
- ✅ Verify after deployment

## **Safe deployment = Validate before + Backup before + Verify after**

---

## Next Steps

- **[Circuit Breakers & Backpressure](../expert/circuit-breakers-backpressure-network-automation.md)** — Safety at scale
