---
title: Testing Network Automation Scripts
description: Master pytest, mocking, and test patterns for reliable network automation. Test decorators, business logic, and device interactions safely without hardware.
tags:
  - Testing
  - Python
  - pytest
  - Network Automation
  - Intermediate
  - Quality Assurance
  - Mocking
---

## Why Testing Network Automation Matters

You've built automation that configures devices, validates states, and makes changes at scale.

But here's the problem: **You can't test in production.**

Running your automation `configure_vlan()` function without tests means:

- Bugs discovered after devices are already changed
- Configuration rolled back manually
- Customer impact, firefighting, blame
- Lost trust in automation

**Testing catches mistakes before they reach production.**

---

## The Business Case: Why Test Automation Code?

### The Reality

Your automation code is **critical infrastructure code**. It:

- Makes changes to live production networks
- Affects hundreds of devices simultaneously
- Has compliance and audit implications
- Is expensive to fix when it fails

Yet many teams test automation by:

- ❌ Running it on test devices once
- ❌ Hoping it works when run on production
- ❌ Discovering bugs in production via customer complaints

### The Cost of Not Testing

| Scenario | Cost |
| :--- | :--- |
| Bug caught in unit test | 5 minutes to fix |
| Bug caught before deployment | 15 minutes to diagnose |
| Bug caught in production | Hours of downtime + customer impact + reputation damage |

### The Solution: Comprehensive Testing

```python
# Testing lets you verify:
# ✅ Decorator logic (retry, rate limiting, audit logging)
# ✅ Business logic (config generation, validation)
# ✅ Error handling (what happens when device fails?)
# ✅ Edge cases (empty config list, timeouts)
# ✅ Integration (decorators + business logic together)
# ✅ All of this WITHOUT touching real devices
```

---

## Testing Fundamentals

### Test Types & Their Purpose

| Type | Purpose | Speed | Real Devices? |
| :--- | :--- | :--- | :--- |
| **Unit Tests** | Individual functions in isolation | ~0.1s | No (mocked) |
| **Integration Tests** | Multiple components together | ~1s | Mocked devices |
| **End-to-End Tests** | Full workflow (optional) | ~30s+ | Real lab devices |
| **Property Tests** | Functions work for ANY valid input | ~1s | No (generated inputs) |

**For production automation: Focus on unit + integration tests.** E2E tests require lab setup and aren't necessary for most cases.

### Pytest Setup

Install pytest:

```bash
pip install pytest pytest-mock pytest-cov
```

Project structure:

```text
my_network_automation/
├── src/
│   ├── __init__.py
│   ├── decorators.py      # Retry, logging, monitoring decorators
│   ├── device_ops.py      # Device operations (configure, verify)
│   └── utils.py           # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_decorators.py
│   ├── test_device_ops.py
│   ├── test_utils.py
│   └── conftest.py        # Shared fixtures
└── pytest.ini
```

---

## Pattern 1: Testing Decorators

### The Problem

Your decorators handle critical concerns (retry, logging, rate limiting). If a decorator breaks, **everything breaks**.

### Testing @retry Decorator

```python
# src/decorators.py
import functools
import logging
import time

logger = logging.getLogger(__name__)

def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

def log_audit(action):
    """Log before and after an audited operation."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info("Starting action", extra={"action": action})
            result = func(*args, **kwargs)
            logger.info("Completed action", extra={"action": action})
            return result
        return wrapper
    return decorator
```

```python
# tests/test_decorators.py
import pytest
import time
from unittest.mock import MagicMock, patch
from src.decorators import retry

class TestRetryDecorator:
    """Test retry decorator behaviour."""
    
    def test_succeeds_on_first_attempt(self):
        """Function succeeds immediately—no retries needed."""
        @retry(max_attempts=3)
        def succeeds():
            return "success"
        
        result = succeeds()
        assert result == "success"
    
    def test_retries_on_transient_failure(self):
        """Function fails twice, succeeds on third—should return success."""
        attempts = []
        
        @retry(max_attempts=3, delay=0)  # delay=0 speeds up test
        def fails_twice():
            attempts.append(1)
            if len(attempts) < 3:
                raise ConnectionError("Transient failure")
            return "success"
        
        result = fails_twice()
        
        assert result == "success"
        assert len(attempts) == 3  # Verify it actually retried
    
    def test_raises_after_max_attempts(self):
        """After max attempts, exception should be raised."""
        @retry(max_attempts=2, delay=0)
        def always_fails():
            raise ConnectionError("Persistent failure")
        
        with pytest.raises(ConnectionError, match="Persistent failure"):
            always_fails()
    
    def test_exponential_backoff(self):
        """Verify backoff multiplier is applied correctly."""
        attempts = []
        
        @retry(max_attempts=3, delay=0, backoff=2)
        def fails_twice():
            attempts.append(time.time() if attempts else 0)
            if len(attempts) < 3:
                raise ConnectionError()
            return "success"
        
        # For precise timing tests, use @patch to mock time.sleep
        with patch('time.sleep') as mock_sleep:
            @retry(max_attempts=3, delay=1, backoff=2)
            def fails_twice_with_sleep():
                if mock_sleep.call_count < 2:
                    raise ConnectionError()
                return "success"
            
            fails_twice_with_sleep()
            
            # Verify sleep called with correct delays: 1s, then 2s
            assert mock_sleep.call_count == 2
            assert mock_sleep.call_args_list[0][0][0] == 1  # First delay
            assert mock_sleep.call_args_list[1][0][0] == 2  # Second delay
    
    def test_catches_only_specified_exceptions(self):
        """Retry only catches specified exceptions, not others."""
        @retry(max_attempts=3, exceptions=(ConnectionError,))
        def raises_value_error():
            raise ValueError("Not caught by retry")
        
        with pytest.raises(ValueError):
            raises_value_error()
    
    def test_preserves_function_metadata(self):
        """@retry should preserve original function name and docstring."""
        @retry()
        def my_function():
            """My docstring."""
            pass
        
        assert my_function.__name__ == "my_function"
        assert "docstring" in my_function.__doc__
```

### Why Each Test Matters

| Test | Why Important |
| :--- | :--- |
| First attempt success | Verify decorator doesn't break successful operations |
| Retry on failure | Verify retry logic actually works |
| Max attempts exhaustion | Verify you eventually give up and raise |
| Exponential backoff | Prevent thundering herd (too-fast retries) |
| Exception filtering | Retry only transient errors, not logic bugs |
| Metadata preservation | Debugging and tooling must work correctly |

---

## Pattern 2: Testing Business Logic with Mocks

### The Problem

Your device operations use Netmiko to send commands. You can't run actual SSH in tests.

Solution: **Mock the device connection.**

### Testing Device Operations

```python
# src/device_ops.py
from netmiko import ConnectHandler

def configure_interface(device, interface, ip_address, netmask):
    """Configure interface with IP address."""
    commands = [
        f"interface {interface}",
        f"ip address {ip_address} {netmask}",
        "no shutdown",
        "exit"
    ]
    device.send_command("configure terminal")
    for cmd in commands:
        device.send_command(cmd)
    device.send_command("end")
    return True

def verify_interface_config(device, interface, expected_ip):
    """Verify interface has expected IP."""
    output = device.send_command(f"show ip interface brief | include {interface}")
    return expected_ip in output
```

```python
# tests/test_device_ops.py
import pytest
from unittest.mock import MagicMock, call
from src.device_ops import configure_interface, verify_interface_config

class TestDeviceOperations:
    """Test device configuration without real devices."""
    
    @pytest.fixture
    def mock_device(self):
        """Create a mock Netmiko device."""
        device = MagicMock()
        device.send_command = MagicMock(return_value="OK")
        return device
    
    def test_configure_interface_sends_correct_commands(self, mock_device):
        """Verify correct CLI commands are sent in correct order."""
        configure_interface(
            mock_device,
            interface="Gi0/0/1",
            ip_address="10.0.0.1",
            netmask="255.255.255.0"
        )
        
        # Verify commands sent in correct order
        expected_calls = [
            call("configure terminal"),
            call("interface Gi0/0/1"),
            call("ip address 10.0.0.1 255.255.255.0"),
            call("no shutdown"),
            call("exit"),
            call("end"),
        ]
        
        assert mock_device.send_command.call_args_list == expected_calls
    
    def test_configure_interface_returns_true_on_success(self, mock_device):
        """Function should return True indicating success."""
        result = configure_interface(
            mock_device,
            interface="Gi0/0/1",
            ip_address="10.0.0.1",
            netmask="255.255.255.0"
        )
        
        assert result is True
    
    def test_configure_interface_handles_device_error(self, mock_device):
        """If device fails, exception should propagate."""
        mock_device.send_command.side_effect = Exception("Device unreachable")
        
        with pytest.raises(Exception, match="Device unreachable"):
            configure_interface(
                mock_device,
                interface="Gi0/0/1",
                ip_address="10.0.0.1",
                netmask="255.255.255.0"
            )
    
    def test_verify_interface_config_detects_correct_ip(self, mock_device):
        """When interface has correct IP, should return True."""
        mock_device.send_command.return_value = "Gi0/0/1 YES manual up 10.0.0.1"
        
        result = verify_interface_config(
            mock_device,
            interface="Gi0/0/1",
            expected_ip="10.0.0.1"
        )
        
        assert result is True
    
    def test_verify_interface_config_detects_wrong_ip(self, mock_device):
        """When interface has different IP, should return False."""
        mock_device.send_command.return_value = "Gi0/0/1 YES manual up 192.168.1.1"
        
        result = verify_interface_config(
            mock_device,
            interface="Gi0/0/1",
            expected_ip="10.0.0.1"
        )
        
        assert result is False
```

### Key Mocking Patterns

| Pattern | Use Case | Example |
| :--- | :--- | :--- |
| `MagicMock()` | Mock any object | `device = MagicMock()` |
| `.return_value` | Set what mock returns | `device.send_command.return_value = "output"` |
| `.side_effect` | Raise exception or return values sequentially | `device.side_effect = Exception()` |
| `.call_args_list` | Assert what arguments were passed | `assert device.call_args_list[0] == call(...)` |
| `.call_count` | Assert how many times called | `assert device.call_count == 5` |

---

## Pattern 3: Testing Decorated Functions

### The Problem

Your production code stacks decorators:

```python
@retry(max_attempts=3)
@log_audit(action="configure_interface")
@perf.monitor
def configure_interface(device, interface, config):
    pass
```

You need to test the **entire stack**, not just individual decorators.

### Testing Decorator Composition

```python
# tests/test_integration.py
import pytest
from unittest.mock import MagicMock, patch
from src.decorators import retry
from src.device_ops import configure_interface

class TestDecoratorIntegration:
    """Test decorators + business logic together."""
    
    def test_retry_recovers_from_transient_failure(self):
        """Verify retry decorator works with real business logic."""
        mock_device = MagicMock()
        
        # Device fails first time, succeeds second time
        mock_device.send_command.side_effect = [
            Exception("Device timeout"),  # First call fails
            "OK",  # configure terminal
            "OK",  # interface command
            "OK",  # ip address command
            "OK",  # no shutdown
            "OK",  # exit
            "OK",  # end
        ]
        
        @retry(max_attempts=3, delay=0)
        def configure_with_retry(device, interface, ip):
            return configure_interface(device, interface, ip, "255.255.255.0")
        
        # Should succeed on second retry
        result = configure_with_retry(
            mock_device,
            interface="Gi0/0/1",
            ip="10.0.0.1"
        )
        
        assert result is True
    
    def test_retry_gives_up_after_max_attempts(self):
        """If all retries fail, exception should propagate."""
        mock_device = MagicMock()
        mock_device.send_command.side_effect = Exception("Device down")
        
        @retry(max_attempts=2, delay=0)
        def configure_with_retry(device, interface, ip):
            return configure_interface(device, interface, ip, "255.255.255.0")
        
        with pytest.raises(Exception, match="Device down"):
            configure_with_retry(
                mock_device,
                interface="Gi0/0/1",
                ip="10.0.0.1"
            )
    
    @patch('src.decorators.logger')
    def test_audit_logging_decorator_logs_attempts(self, mock_logger):
        """Verify audit logging captures operations."""
        from src.decorators import log_audit
        
        mock_device = MagicMock()
        mock_device.send_command.return_value = "OK"
        
        @log_audit(action="configure")
        def configure_with_logging(device, interface):
            device.send_command(f"interface {interface}")
            return True
        
        configure_with_logging(mock_device, "Gi0/0/1")
        
        # Verify something was logged (implementation details depend on your logging)
        assert mock_logger.info.called or mock_logger.debug.called
```

---

## Pattern 4: Fixtures for Reusable Test Setups

### The Problem

Writing `mock_device = MagicMock()` in every test is repetitive.

Solution: **Pytest fixtures**

```python
# tests/conftest.py (shared across all tests)
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_device():
    """Reusable mock Netmiko device."""
    device = MagicMock()
    device.send_command = MagicMock(return_value="OK")
    return device

@pytest.fixture
def mock_device_with_output():
    """Mock device that returns realistic output."""
    device = MagicMock()
    responses = {
        "show ip route": "10.0.0.0/8 via 192.168.1.1",
        "show running-config": "hostname R1\nip domain-name example.com",
        "show interfaces brief": "Gi0/0/1 YES manual up 10.0.0.1",
    }
    device.send_command = MagicMock(side_effect=lambda command, **kwargs: responses.get(command))
    return device

@pytest.fixture
def mock_device_fails():
    """Mock device that fails to connect."""
    device = MagicMock()
    device.send_command.side_effect = Exception("Connection timeout")
    return device
```

Now use in tests:

```python
def test_configure_interface(mock_device):
    """Uses fixture automatically."""
    configure_interface(mock_device, "Gi0/0/1", "10.0.0.1", "255.255.255.0")
    assert mock_device.send_command.called

def test_fails_gracefully(mock_device_fails):
    """Uses failure fixture."""
    with pytest.raises(Exception):
        configure_interface(mock_device_fails, "Gi0/0/1", "10.0.0.1", "255.255.255.0")
```

---

## Running Tests & Coverage

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test

```bash
pytest tests/test_decorators.py::TestRetryDecorator::test_succeeds_on_first_attempt
```

### Run with Coverage Report

```bash
pytest --cov=src tests/
```

Output:

```text
Name                Stmts   Miss  Cover
----------------------------------------
src/decorators.py      45      2    95%
src/device_ops.py      28      1    96%
src/utils.py           15      0   100%
----------------------------------------
TOTAL                 88      3    97%
```

## **Good coverage targets: 80-90% for business logic, 95%+ for critical decorators**

### Fail Fast While Developing

```bash
pytest -x tests/  # Stop on first failure
pytest -v tests/  # Verbose output
pytest -s tests/  # Show print statements
```

---

## CI/CD Integration: GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test Automation Code

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov pytest-mock
    
    - name: Run tests
      run: pytest tests/ --cov=src
    
    - name: Check coverage threshold
      run: pytest tests/ --cov=src --cov-fail-under=80
```

Now **every commit is automatically tested** before merging.

---

## Best Practices

### 1. Test Behaviour, Not Implementation

```python
# ❌ BAD - Tests implementation details
def test_retry():
    @retry()
    def func():
        return "success"
    
    assert func.__name__ == "wrapper"  # Tests internal name

# ✅ GOOD - Tests behaviour
def test_retry():
    @retry()
    def func():
        return "success"
    
    assert func() == "success"  # Tests what user cares about
```

### 2. One Assertion Per Test (Usually)

```python
# ❌ BAD - Multiple assertions make it hard to know what failed
def test_configure():
    result = configure_interface(...)
    assert result is True
    assert mock_device.send_command.called
    assert mock_device.send_command.call_count == 6

# ✅ GOOD - Separate tests for separate concerns
def test_configure_returns_true():
    result = configure_interface(...)
    assert result is True

def test_configure_sends_commands():
    configure_interface(...)
    assert mock_device.send_command.called
```

### 3. Use Meaningful Test Names

```python
# ❌ BAD - Vague
def test_retry():
    pass

# ✅ GOOD - Describes scenario and expected outcome
def test_retry_recovers_from_transient_failure():
    pass

def test_retry_raises_after_max_attempts_exhausted():
    pass
```

### 4. Mock External Dependencies, Not Your Code

```python
# ❌ BAD - Mocking your own code
@patch('src.device_ops.configure_interface')
def test_something(mock_configure):
    # This defeats the purpose of testing
    pass

# ✅ GOOD - Mock Netmiko (external), test your code
@patch('netmiko.ConnectHandler')
def test_configure():
    # Test your logic with real mocking
    pass
```

### 5. Parametrize Tests to Reduce Duplication

```python
@pytest.mark.parametrize("ip,netmask,expected", [
    ("10.0.0.1", "255.255.255.0", True),
    ("192.168.1.1", "255.255.255.0", True),
    ("invalid.ip", "255.255.255.0", False),
])
def test_validate_ip_address(ip, netmask, expected):
    result = validate_ip_address(ip, netmask)
    assert result == expected
```

---

## Enterprise Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E Tests (5%)—real devices in lab
      /    \
     /      \
    /________\
   /          \
  /            \ Integration Tests (15%)—mocked device
 /              \ interactions
/________________\
/                  \
/                    \ Unit Tests (80%)—individual
/____________________\ functions in isolation
```

**Do this:**

- **80% unit tests** — Fast, cheap, comprehensive
- **15% integration tests** — Verify decorator stacks, device flows
- **5% E2E tests** (optional) — Only for critical workflows

### Continuous Testing Workflow

1. **Write test before code** (TDD optional but helpful)
2. **Run locally**: `pytest tests/ -v`
3. **Push to GitHub**
4. **CI/CD runs automatically**
5. **Merge only if tests pass**

---

## Next Steps

**Your testing foundation is now solid.** Next patterns that depend on this:

- **[Credential Management](./credential-management-network-automation.md)** — Test secret handling safely
- **[Error Recovery & Rollback](./error-recovery-rollback-network-automation.md)** — Test rollback logic without breaking devices

---

## Summary

| Concept | Why It Matters |
| :--- | :--- |
| Unit tests | Catch bugs in decorators and business logic |
| Mocking | Test without real devices or credentials |
| Integration tests | Verify decorated functions work together |
| Fixtures | DRY up test setup code |
| Parametrization | Test multiple scenarios efficiently |
| CI/CD | Catch bugs before production |

**Test your automation. Sleep better at night.**
