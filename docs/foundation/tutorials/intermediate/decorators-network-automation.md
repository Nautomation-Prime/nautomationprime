---
title: Decorators in Network Automation
description: Master Python decorators for production network automation. Build retry logic, logging, error handling, rate limiting, and monitoring—all patterns proven in enterprise environments.
tags:
  - Decorators
  - Python
  - Network Automation
  - Production Patterns
  - Error Handling
  - Intermediate
  - Design Patterns
---

## Why Decorators Matter in Network Automation

You've written automation that connects to devices, extracts data, and makes changes.

Now consider these real-world scenarios:

- A network device times out mid-operation—should you retry automatically?
- A configuration change fails on one of 50 devices—how do you audit what happened?
- Your API is rate-limited—how do you throttle requests without rewriting logic?
- You need to measure how long each network operation takes—how do you do that without cluttering your code?

**Decorators are Python's answer to these problems.**

Decorators let you wrap functions with cross-cutting behaviour—retry logic, logging, error handling, rate limiting—without modifying the original function. In network automation, this pattern separates your **core device logic** from your **operational concerns**.

---

## The Business Case: Enterprise Network Operations

### The Problem

Your network automation works on your test network. But production has:

- **Intermittent failures** — device timeouts, SSH connection resets
- **Compliance audits** — "Who changed what on which device at what time?"
- **Rate limiting** — External APIs only allow 100 requests/minute
- **Performance bottlenecks** — No visibility into which operations are slow
- **Error cascades** — One device fails, causing 50 others to fail

**Without decorators, you add if/try/except logic to every function, creating unmaintainable code.**

### The Solution: Decorator-Driven Architecture

```python
@retry(max_attempts=3, delay=2)
@log_audit(action="config_change")
@measure_performance()
def configure_interface(device, interface, config):
    """Pure business logic—no infrastructure concerns."""
    device.send_command(f"interface {interface}")
    device.send_command(config)
```

**Result:**

- Retries automatically on failure
- Logs every attempt for compliance
- Measures execution time
- Test code stays focused and readable
- Infrastructure concerns are declarative and composable

---

## Decorator Fundamentals (Quick Review)

If you're familiar with decorators, skip to [Patterns in Network Automation](#patterns-in-network-automation).

### What is a Decorator?

A decorator is a function that takes a function as input and returns a modified function.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Before calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"After calling {func.__name__}")
        return result
    return wrapper

@my_decorator
def greet(name):
    return f"Hello, {name}"

greet("Alice")
# Output:
# Before calling greet
# Hello, Alice
# After calling greet
```

### Why Decorators Work

When you write:

```python
@my_decorator
def my_function():
    pass
```

Python executes:

```python
my_function = my_decorator(my_function)
```

The decorator function **replaces** the original function with the wrapper.

### The `functools.wraps` Pattern

Always use `functools.wraps` when writing decorators. It preserves the original function's metadata:

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

Without `functools.wraps`, debugging is a nightmare—the wrapper function's name is "wrapper," not your actual function.

---

## Patterns in Network Automation

---

## Pattern 1: Automatic Retry with Exponential Backoff

### The Problem

Network operations fail intermittently:

- SSH timeouts
- Device CPU spikes
- Temporary connectivity issues

Manual retry logic clutters code. Decorators solve this elegantly.

### The Implementation

```python
import functools
import time
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException

def retry(max_attempts=3, delay=1, backoff=2, 
          exceptions=(Exception,)):
    """
    Retry a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch
    
    Example:
        @retry(max_attempts=3, delay=2, backoff=2)
        def connect_to_device(host):
            return connect(host)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"[{func.__name__}] Attempt {attempt}/{max_attempts}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        print(f"[{func.__name__}] All {max_attempts} attempts failed")
                        raise
                    print(f"[{func.__name__}] Failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator
```

### Real-World Usage

```python
from netmiko import ConnectHandler
from netmiko import NetmikoTimeoutException

@retry(
    max_attempts=3, 
    delay=2, 
    backoff=2,
    exceptions=(NetmikoTimeoutException, OSError)
)
def connect_to_device(host, username, password):
    """Connect to network device with automatic retry."""
    device = ConnectHandler(
        device_type="cisco_ios",
        host=host,
        username=username,
        password=password,
        timeout=10
    )
    return device

# Usage
try:
    device = connect_to_device("10.0.0.1", "admin", "password")
    output = device.send_command("show version")
    device.disconnect()
except Exception as e:
    print(f"Connection failed after retries: {e}")
```

### Why This Matters

- **Resilience** — Transient failures don't crash your automation
- **No code duplication** — Every function you decorate gets retry behaviour
- **Configurable** — Adjust retry behaviour per function, not at application level
- **Observable** — Print statements show retry attempts (integrate with logging in production)

---

## Pattern 2: Audit Logging for Compliance

### The Problem

In enterprise environments, you need concrete audit trails:

- Who made what change?
- When did it happen?
- What device was affected?
- Did it succeed or fail?

Without structured logging, compliance audits are nightmares.

### The Implementation

```python
import functools
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
audit_logger = logging.getLogger("network_audit")

def log_audit(action, include_args=True):
    """
    Log audit events for compliance and troubleshooting.
    
    Args:
        action: Description of the action (e.g., "config_deploy", "interface_enable")
        include_args: Whether to log function arguments
    
    Example:
        @log_audit(action="vlan_provision")
        def create_vlan(device, vlan_id, vlan_name):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.utcnow().isoformat()
            
            # Extract meaningful context
            context = {
                "timestamp": timestamp,
                "action": action,
                "function": func.__name__,
            }
            
            if include_args:
                context["args"] = str(args)
                context["kwargs"] = str(kwargs)
            
            audit_logger.info(f"[AUDIT START] {context}")
            
            try:
                result = func(*args, **kwargs)
                audit_logger.info(
                    f"[AUDIT SUCCESS] action={action}, function={func.__name__}, "
                    f"result_type={type(result).__name__}"
                )
                return result
            except Exception as e:
                audit_logger.error(
                    f"[AUDIT FAILURE] action={action}, function={func.__name__}, "
                    f"error={str(e)}"
                )
                raise
        
        return wrapper
    return decorator
```

### Real-World Usage

```python
@log_audit(action="enable_interface")
def enable_interface(device, interface):
    """Enable a network interface."""
    device.send_command(f"interface {interface}")
    device.send_command("no shutdown")
    return True

@log_audit(action="provision_vlan")
def provision_vlan(device, vlan_id, vlan_name):
    """Create and configure a VLAN."""
    device.send_command(f"vlan {vlan_id}")
    device.send_command(f"name {vlan_name}")
    device.send_command("exit")
    return vlan_id

# Usage
device = connect_to_device("10.0.0.1", "admin", "password")
enable_interface(device, "Gi0/0/1")
provision_vlan(device, 100, "Management")
```

### Audit Log Output

```text
2026-03-04 14:23:45,123 - network_audit - INFO - [AUDIT START] {
  'timestamp': '2026-03-04T14:23:45.123456', 
  'action': 'enable_interface', 
  'function': 'enable_interface'
}
2026-03-04 14:23:47,456 - network_audit - INFO - [AUDIT SUCCESS] action=enable_interface, 
  function=enable_interface, result_type=bool
2026-03-04 14:23:47,789 - network_audit - INFO - [AUDIT START] {
  'timestamp': '2026-03-04T14:23:47.789012', 
  'action': 'provision_vlan', 
  'function': 'provision_vlan'
}
2026-03-04 14:23:50,012 - network_audit - INFO - [AUDIT SUCCESS] action=provision_vlan, 
  function=provision_vlan, result_type=int
```

### Why This Matters

- **Compliance** — Every change is tracked with timestamp and outcome
- **Troubleshooting** — When something goes wrong, you have a complete audit trail
- **Accountability** — Clear record of what automation did
- **Forensics** — Analyse what happened during a failure

---

## Pattern 3: Error Handling and Recovery

### The Problem

Network operations can fail in many ways. Generic try/except blocks get repetitive and inconsistent.

```python
# Without decorators—lots of repetition
try:
    result1 = operation_1()
except SomeError as e:
    log_error(e)
    notify_team(e)
    raise

try:
    result2 = operation_2()
except SomeError as e:
    log_error(e)
    notify_team(e)
    raise
```

### The Implementation

```python
import functools
import logging

def handle_errors(default_return=None, notify=True, reraise=True):
    """
    Unified error handling for network operations.
    
    Args:
        default_return: What to return if error occurs (if reraise=False)
        notify: Whether to notify critical errors
        reraise: Whether to re-raise the exception after handling
    
    Example:
        @handle_errors(notify=True, reraise=True)
        def deploy_config(device, config):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error in {func.__name__}: {str(e)}"
                logging.error(error_msg)
                
                if notify:
                    # Send critical alert to operations team
                    send_alert(f"AUTOMATION FAILURE: {error_msg}")
                
                if not reraise:
                    return default_return
                
                raise
        
        return wrapper
    return decorator

def send_alert(message):
    """Placeholder for actual alerting (email, Slack, PagerDuty, etc.)"""
    print(f"[ALERT] {message}")
```

### Real-World Usage

```python
@handle_errors(notify=True, reraise=True)
def deploy_bgp_config(device, bgp_config):
    """Deploy BGP configuration to device."""
    device.send_command("configure terminal")
    device.send_command(f"router bgp {bgp_config['asn']}")
    for neighbor in bgp_config['neighbors']:
        device.send_command(f"neighbor {neighbor['ip']} remote-as {neighbor['asn']}")
    device.send_command("end")
    return True

@handle_errors(default_return=False, notify=False, reraise=False)
def check_device_health(device):
    """Check device health (non-critical operation)."""
    output = device.send_command("show system")
    return "OK" in output
```

### Why This Matters

- **Consistency** — Same error handling across all operations
- **Observability** — Errors are logged centrally
- **Alert integration** — Critical failures trigger notifications immediately
- **Graceful degradation** — Non-critical operations can fail safely

---

## Pattern 4: Rate Limiting

### The Problem

External APIs and some devices have rate limits:

- 100 requests per minute
- 10 concurrent connections per IP
- Thresholds that trigger device CPU throttling

Without coordination, your automation triggers rate limits, causing cascading failures.

### The Implementation

```python
import functools
import time
from collections import deque
from threading import Lock

class RateLimiter:
    """Thread-safe rate limiter using sliding window."""
    
    def __init__(self, max_calls, time_window):
        """
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self.lock = Lock()
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                
                # Remove calls outside the time window
                while self.calls and self.calls[0] <= now - self.time_window:
                    self.calls.popleft()
                
                # If we've hit the limit, wait
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.time_window - (now - self.calls[0])
                    print(f"Rate limit reached. Waiting {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                
                self.calls.append(time.time())
            
            return func(*args, **kwargs)
        
        return wrapper

# Create rate limiters for different APIs
dns_limiter = RateLimiter(max_calls=100, time_window=60)
api_limiter = RateLimiter(max_calls=50, time_window=10)
```

### Real-World Usage

```python
# 100 requests per minute to DNS API
@dns_limiter
def query_dns_api(hostname):
    """Query external DNS API."""
    # API call here
    return resolve_hostname(hostname)

# 50 requests per 10 seconds to device API
@api_limiter
def fetch_device_data(device_id):
    """Fetch data from rate-limited device API."""
    # API call here
    return get_device_stats(device_id)

# Usage
devices = ["device1", "device2", ..., "device200"]  # 200 devices
for device_id in devices:
    stats = fetch_device_data(device_id)  # Automatically rate-limited
    print(stats)
# Completes in 40+ seconds (respecting 50 req/10sec limit), 
# not crashing with rate limit errors
```

### Why This Matters

- **Prevents triggering rate limits** — Operations complete reliably
- **No manual throttling** — Rate limiting is transparent
- **Scales safely** — Add 1000 devices without changing code
- **Automatic backoff** — No cascading failures

---

## Pattern 5: Performance Monitoring

### The Problem

Automation takes too long and you don't know why:

- Which device takes 30 seconds to respond?
- Which operation is the bottleneck?
- Are SSH connections the problem or the logic?

Without metrics, you're flying blind.

### The Implementation

```python
import functools
import time
import statistics
from collections import defaultdict
from threading import Lock

class PerformanceMonitor:
    """Thread-safe performance monitor for tracking execution time."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = Lock()
    
    def monitor(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                with self.lock:
                    self.metrics[func.__name__].append(elapsed)
                print(f"[{func.__name__}] took {elapsed:.2f}s")
        
        return wrapper
    
    def report(self):
        """Print performance statistics."""
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        
        with self.lock:
            metrics_snapshot = dict(self.metrics)
        
        for func_name, times in metrics_snapshot.items():
            print(f"\n{func_name}:")
            print(f"  Calls:     {len(times)}")
            print(f"  Min:       {min(times):.3f}s")
            print(f"  Max:       {max(times):.3f}s")
            print(f"  Mean:      {statistics.mean(times):.3f}s")
            if len(times) > 1:
                print(f"  Median:    {statistics.median(times):.3f}s")
                print(f"  StdDev:    {statistics.stdev(times):.3f}s")
            print(f"  Total:     {sum(times):.3f}s")

# Global performance monitor
perf = PerformanceMonitor()
```

### Real-World Usage

```python
@perf.monitor
def collect_show_version(device):
    """Collect show version from device."""
    return device.send_command("show version")

@perf.monitor
def collect_show_interfaces(device):
    """Collect interface status from device."""
    return device.send_command("show interfaces brief")

@perf.monitor
def parse_and_store(data):
    """Parse device data and store in database."""
    parsed = parse_device_output(data)
    store_in_db(parsed)
    return parsed

# Usage
devices = [connect_to_device(ip) for ip in device_ips]

for device in devices:
    version = collect_show_version(device)
    interfaces = collect_show_interfaces(device)
    parse_and_store(interfaces)

# Print performance report
perf.report()
```

### Example Output

```text
============================================================
PERFORMANCE REPORT
============================================================

collect_show_version:
  Calls:     50
  Min:       0.234s
  Max:       2.156s
  Mean:      0.512s
  Median:    0.445s
  StdDev:    0.341s
  Total:     25.600s

collect_show_interfaces:
  Calls:     50
  Min:       0.198s
  Max:       1.843s
  Mean:      0.478s
  Median:    0.412s
  StdDev:    0.289s
  Total:     23.900s

parse_and_store:
  Calls:     50
  Min:       0.012s
  Max:       0.094s
  Mean:      0.031s
  Median:    0.028s
  StdDev:    0.018s
  Total:     1.550s
```

### Why This Matters

- **Identify bottlenecks** — See which operations are slow
- **Data-driven optimisation** — Fix what actually matters
- **Track improvements** — Measure impact of optimisations
- **Capacity planning** — Understand performance at scale

---

## Pattern 6: Composable Decorators

### The Power of Combining Decorators

The real power of decorators is composing them together. A single function can have multiple decorators, each adding a layer of functionality.

### Implementation

```python
# All the previous decorators: @retry, @log_audit, @handle_errors, @measure_performance

@retry(max_attempts=3, delay=2)
@log_audit(action="configure_device")
@handle_errors(notify=True, reraise=True)
@perf.monitor
def configure_device(device, config):
    """
    Pure business logic focused on the network operation.
    
    All infrastructure concerns are handled by decorators:
    - Retry: Automatic retry on failure
    - Log audit: Compliance logging
    - Handle errors: Unified error handling and alerting
    - Performance: Execution time tracking
    """
    device.send_command("configure terminal")
    for command in config:
        device.send_command(command)
    device.send_command("end")
    return True
```

### Decorator Execution Order

**Important:** Decorators execute from the bottom up (closest to the function first), but the wrapper layers stack.

```python
@decorator_A  # Executes last (outermost layer)
@decorator_B  # Executes second
@decorator_C  # Executes first (closest to function)
def my_function():
    pass
```

This is equivalent to:

```python
my_function = decorator_A(decorator_B(decorator_C(my_function)))
```

### When Composing, Order Matters

```python
# GOOD: Retry is the outermost (catches all failures)
@retry(max_attempts=3)
@log_audit(action="deploy")
def deploy_config(device, config):
    pass

# LESS IDEAL: Audit logging wraps retry
@log_audit(action="deploy")
@retry(max_attempts=3)
def deploy_config(device, config):
    pass
# This still works, but retry failures aren't logged as "final" failures
```

**General principle:** Put decorators that handle exceptional cases (retry, error handling) on the outside, and decorators that monitor normal execution (logging, performance) on the inside.

---

## Integration with Nornir

### Using Decorators with Nornir Tasks

[Nornir](./nornir-fundamentals.md) is a Python framework for automating network operations across multiple devices. Decorators integrate seamlessly with Nornir tasks.

### Example: Nornir Task with Decorators

```python
from nornir import InitNornir
from nornir.core.task import Task, Result

perf = PerformanceMonitor()

@retry(max_attempts=2, delay=1)
@log_audit(action="nornir_device_config")
@perf.monitor
def apply_config_task(task: Task) -> Result:
    """Nornir task with automatic retry, audit logging, and performance tracking."""
    device = task.host.get_connection("netmiko", task.nornir.config)
    
    config_commands = [
        "interface Gi0/0/1",
        "ip address 10.0.0.1 255.255.255.0",
        "no shutdown",
        "exit"
    ]
    
    device.send_command("configure terminal")
    for command in config_commands:
        device.send_command(command)
    device.send_command("end")
    
    return Result(
        host=task.host,
        result="Configuration applied successfully"
    )

# Usage with Nornir
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=apply_config_task)

perf.report()
```

### Nornir + Rate Limiting = Scale Safe

```python
# Rate limit API calls per device (10 sec between each device)
device_api_limiter = RateLimiter(max_calls=1, time_window=10)

@device_api_limiter
@retry(max_attempts=2)
def query_device_api(task: Task) -> Result:
    """Query device API with rate limiting (one per 10 seconds)."""
    # This automatically throttles: process 100 devices in 1000 seconds
    api_response = task.host["api_endpoint"].query_status()
    return Result(host=task.host, result=api_response)

# This scales safely—no rate limit errors
nr.run(task=query_device_api)
```

---

## Advanced Pattern: Conditional Decorators

### The Problem

Sometimes you want a decorator to apply only under certain conditions:

- Enable retry only in production
- Log audit events only for production changes
- Rate limit only when hitting an external API

### The Implementation

```python
import functools
import os

def conditional_retry(condition, **retry_kwargs):
    """Apply retry only if condition is True."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if condition:
                # Apply retry decorator
                return retry(**retry_kwargs)(func)(*args, **kwargs)
            else:
                # Skip decorator
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Use environment variable to control behaviour
PRODUCTION = os.getenv("ENV") == "production"

@conditional_retry(
    condition=PRODUCTION,
    max_attempts=3,
    delay=2
)
def configure_device(device, config):
    """In production: retry 3 times. Otherwise: fail fast."""
    pass
```

### Real-World Example

```python
import os

PRODUCTION = os.getenv("ENV") == "production"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

def conditional_decorator(condition=True, decorator_func=None):
    """Conditionally apply a decorator."""
    def wrapper(func):
        if condition:
            return decorator_func(func)
        return func
    return wrapper

@conditional_decorator(
    condition=PRODUCTION,
    decorator_func=lambda f: retry(max_attempts=3)(f)
)
@conditional_decorator(
    condition=PRODUCTION,
    decorator_func=lambda f: log_audit(action="deploy")(f)
)
def deploy_config(device, config):
    """
    - In production: auto-retry, audit log, and execute
    - In testing: fail fast, no logging, execute
    """
    if DRY_RUN:
        print(f"[DRY RUN] Would execute: {config}")
        return True
    
    # Actual deployment
    device.apply_config(config)
    return True
```

---

## Best Practices

### 1. Always Use `functools.wraps`

```python
import functools

# ❌ WRONG - loses metadata
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# ✅ CORRECT - preserves metadata
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### 2. Keep Decorators Single-Responsibility

Each decorator should do one thing:

```python
# ❌ WRONG - decorator does too much
def do_everything(func):
    """Retry, log, monitor, rate limit - all in one."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 100 lines of mixed logic
        pass
    return wrapper

# ✅ CORRECT - focused decorators compose well
@retry(max_attempts=3)
@log_audit(action="deploy")
@perf.monitor
@rate_limiter
def deploy_config(device, config):
    pass
```

### 3. Document Decorator Parameters

```python
def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Retry a function with exponential backoff.
    
    Args:
        max_attempts (int): Maximum number of attempts. Default: 3
        delay (float): Initial delay between retries in seconds. Default: 1
        backoff (float): Multiplier for exponential backoff. Default: 2
        exceptions (tuple): Exception types to catch and retry on. Default: (Exception,)
    
    Raises:
        The last caught exception if all retries fail.
    
    Example:
        @retry(max_attempts=3, delay=2, backoff=1.5)
        def connect_to_device(host):
            return device_connection(host)
    """
```

### 4. Order Matters When Composing

```python
# General rule: exceptional cases on the outside, observability on the inside

# ✅ GOOD
@retry(max_attempts=3)  # Exception handler (outermost)
@log_audit(action="deploy")  # Logging (middle)
@perf.monitor  # Observability (innermost)
def deploy():
    pass

# This order makes sense:
# 1. Try the operation (retry wrapper is outermost)
# 2. Log what happened
# 3. Measure how long it took
```

### 5. Test Decorators Independently

```python
import unittest
from unittest.mock import patch, MagicMock

class TestRetryDecorator(unittest.TestCase):
    def test_succeeds_on_first_attempt(self):
        @retry(max_attempts=3)
        def succeeds():
            return "success"
        
        result = succeeds()
        self.assertEqual(result, "success")
    
    def test_retries_on_failure(self):
        attempts = []
        
        @retry(max_attempts=3, delay=0)
        def fails_twice():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Failed")
            return "success"
        
        result = fails_twice()
        self.assertEqual(result, "success")
        self.assertEqual(len(attempts), 3)
    
    def test_raises_after_max_attempts(self):
        @retry(max_attempts=2, delay=0)
        def always_fails():
            raise ValueError("Always fails")
        
        with self.assertRaises(ValueError):
            always_fails()
```

### 6. Make Decorators Production-Grade

```python
import functools
import logging
import time
from typing import Callable, Tuple, Type, Any

def production_retry(
    max_attempts: int = 3,
    delay: float = 1,
    backoff: float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: logging.Logger = None
):
    """
    Production-grade retry decorator with logging and metrics.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries
        backoff: Exponential backoff multiplier
        exceptions: Tuple of exceptions to retry on
        logger: Logger instance for recording retries (uses module logger if None)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__}"
                    )
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {func.__name__}",
                            exc_info=True
                        )
                        raise
                    logger.warning(
                        f"Attempt {attempt} failed: {str(e)}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    return decorator
```

---

## Enterprise Example: Complete Workflow

### Scenario

You're deploying configuration to 100 network devices. You need:

- Automatic retry for transient failures
- Audit logging for compliance
- Rate limiting to avoid device overload
- Performance metrics
- Error notifications
- Graceful handling of partial failures

### Implementation

```python
import functools
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")

# Performance monitor
perf = PerformanceMonitor()

# Rate limiter: 10 devices per minute
device_limiter = RateLimiter(max_calls=10, time_window=60)

# Core decorators (as defined above)
# @retry, @log_audit, @handle_errors, @perf.monitor, etc.

class ConfigDeployment:
    """Enterprise configuration deployment with full decorator integration."""
    
    @device_limiter
    @retry(max_attempts=2, delay=2)
    @log_audit(action="deploy_config")
    @handle_errors(notify=True, reraise=False)
    @perf.monitor
    def deploy_to_single_device(
        self,
        device_ip: str,
        device_username: str,
        device_password: str,
        config: List[str],
        pre_check: bool = True,
        post_check: bool = True
    ) -> Dict[str, Any]:
        """
        Deploy configuration to a single device with full observability.
        
        Decorators provide:
        - device_limiter: Rate limitation (10 devices/min)
        - retry: Automatic retry (2 attempts, 2s delay)
        - log_audit: Compliance logging
        - handle_errors: Unified error handling
        - perf.monitor: Performance metrics
        """
        
        # Connect
        device = connect_to_device(device_ip, device_username, device_password)
        
        try:
            # Pre-deployment check
            if pre_check:
                pre_state = device.send_command("show running-config | include hostname")
                logger.info(f"Pre-check state: {pre_state}")
            
            # Deploy configuration
            device.send_command("configure terminal")
            for command in config:
                logger.debug(f"Sending command: {command}")
                device.send_command(command)
            device.send_command("end")
            
            # Post-deployment verification
            if post_check:
                post_state = device.send_command("show running-config | include hostname")
                logger.info(f"Post-check state: {post_state}")
            
            return {
                "device": device_ip,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        finally:
            device.disconnect()
    
    def deploy_to_fleet(
        self,
        devices: List[Dict[str, str]],
        config: List[str]
    ) -> Dict[str, Any]:
        """
        Deploy configuration to a fleet of devices with aggregated reporting.
        
        Args:
            devices: List of dicts with 'ip', 'username', 'password'
            config: List of CLI commands to deploy
        
        Returns:
            Aggregated results with success/failure counts
        """
        results = {
            "successful": [],
            "failed": [],
            "total_devices": len(devices)
        }
        
        for device in devices:
            try:
                result = self.deploy_to_single_device(
                    device_ip=device["ip"],
                    device_username=device["username"],
                    device_password=device["password"],
                    config=config
                )
                results["successful"].append(result)
                logger.info(f"✅ {device['ip']}: deployment successful")
            
            except Exception as e:
                failure = {
                    "device": device["ip"],
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                results["failed"].append(failure)
                logger.error(
                    f"❌ {device['ip']}: deployment failed - {str(e)}"
                )
        
        # Print performance report
        logger.info("\n" + "="*60)
        logger.info(f"DEPLOYMENT SUMMARY")
        logger.info("="*60)
        logger.info(
            f"Total: {results['total_devices']}, "
            f"Success: {len(results['successful'])}, "
            f"Failed: {len(results['failed'])}"
        )
        
        perf.report()
        
        return results

# Usage
devices = [
    {"ip": "10.0.0.1", "username": "admin", "password": "password"},
    {"ip": "10.0.0.2", "username": "admin", "password": "password"},
    # ... 98 more devices
]

config = [
    "interface Gi0/0/1",
    "ip address 10.1.1.1 255.255.255.0",
    "no shutdown",
    "exit"
]

deployer = ConfigDeployment()
results = deployer.deploy_to_fleet(devices, config)
```

### Output

```text
INFO:__main__:AUDIT START - action=deploy_config, device=10.0.0.1
INFO:__main__:[deploy_to_single_device] took 2.34s
INFO:__main__:✅ 10.0.0.1: deployment successful
INFO:__main__:Rate limit reached. Waiting 5.23s...
INFO:__main__:AUDIT START - action=deploy_config, device=10.0.0.2
INFO:__main__:[deploy_to_single_device] took 1.98s
INFO:__main__:✅ 10.0.0.2: deployment successful
...

INFO:__main__:============================================================
INFO:__main__:DEPLOYMENT SUMMARY
INFO:__main__:============================================================
INFO:__main__:Total: 100, Success: 98, Failed: 2

INFO:__main__:PERFORMANCE REPORT
INFO:__main__:deploy_to_single_device:
INFO:__main__:  Calls:     100
INFO:__main__:  Min:       1.234s
INFO:__main__:  Max:       4.567s
INFO:__main__:  Mean:      2.345s
INFO:__main__:  Median:    2.234s
INFO:__main__:  StdDev:    0.678s
INFO:__main__:  Total:     234.500s
```

---

## Troubleshooting

### Problem: Decorator Doesn't Seem to Work

**Cause:** Missing `functools.wraps`

```python
# ❌ Wrong - decorator doesn't preserve function name
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# ✅ Correct
def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### Problem: Decorator Not Catching Exceptions

**Cause:** Incorrect exception type

```python
# ❌ Catches Exception but device raises Timeout (subclass)
@retry(exceptions=(Exception,))
def connect():
    pass

# ✅ Catch the specific exception
from netmiko import NetmikoTimeoutException
@retry(exceptions=(NetmikoTimeoutException,))
def connect():
    pass
```

### Problem: Decorators Executing in Wrong Order

**Cause:** Misunderstanding decorator stacking

```python
# This:
@decorator_a
@decorator_b
@decorator_c
def func():
    pass

# Is equivalent to:
func = decorator_a(decorator_b(decorator_c(func)))

# So decorator_c runs first (closest to func), then decorator_b, then decorator_a
# If you want decorator_a to run first, put it closest to the function
```

### Problem: Performance Issues with Decorators

**Cause:** Decorator overhead with high-frequency calls

```python
# ❌ Overhead for simple, fast operations
@log_audit(action="send_data")
@perf.monitor
@retry(max_attempts=3)
def send_packet(data):
    return socket.send(data)  # Takes 1ms

# For 100,000 calls, decorator overhead becomes significant

# ✅ Use conditional decorators for high-frequency operations
@conditional_retry(condition=not high_frequency_mode, max_attempts=3)
@conditional_decorator(condition=not high_frequency_mode, decorator_func=perf.monitor)
def send_packet(data):
    return socket.send(data)
```

---

## Next Steps

Decorators are powerful tools, but they're part of a larger ecosystem:

- **[Nornir Fundamentals](./nornir-fundamentals.md)** — Apply decorators to multi-device operations at scale
- **[PyATS Fundamentals](./pyats-fundamentals.md)** — Combine decorators with structured validation
- **[Advanced Nornir Patterns](./advanced-nornir-patterns.md)** — Use decorators in enterprise architectures

---

## Summary

Decorators solve real problems in network automation:

| Problem | Decorator Pattern | Benefit |
| :--- | :--- | :--- |
| Transient failures | Retry | Resilience without code duplication |
| Compliance audits | Audit logging | Complete audit trail for every operation |
| Rate limits | Rate limiter | Scale safely without triggering limits |
| Performance bottlenecks | Performance monitor | Identify and fix slow operations |
| Error handling | Unified error handling | Consistent error behaviour and alerting |
| Cross-cutting concerns | Composable decorators | Separation of business logic and infrastructure |

**Master these patterns and your network automation will be more resilient, observable, and maintainable.**
