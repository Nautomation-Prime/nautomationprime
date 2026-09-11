---
title: Structured Logging for Network Automation
description: Production-grade logging with JSON, log levels, and log aggregation integration. Track what happened, when, and why. Centralized observability for automation.
tags:
  - Logging
  - Observability
  - Network Automation
  - Intermediate
  - Production
  - Structured Data
---

## Why Structured Logging Matters

**Scenario:** Your automation failed 3 hours ago. Now your boss asks: "What happened?"

**Without Structured Logging:**

- ❌ Logs are scattered across different files
- ❌ Each script logs differently
- ❌ Simple grep searches are ineffective
- ❌ Can't correlate events across devices
- ❌ Timestamps don't line up
- ❌ No emergency response capability

**With Structured Logging:**

- ✅ Every log is JSON (machine-readable)
- ✅ Centralized aggregation (ELK, Splunk, CloudWatch)
- ✅ Powerful queries ("Show me all failures for device X")
- ✅ Correlation IDs track operations across devices
- ✅ Automatic alerting on errors
- ✅ Compliance audit trails

**Print statements and unstructured logs don't scale. Structured logging enables production automation.**

---

## Architecture: Log Flow

```text
┌─────────────────────┐
│  Your Script        │
│  (Structured logs)  │
└────────┬────────────┘
         │
         ↓ JSON format
┌─────────────────────┐
│  Log Shipper        │
│  (Filebeat/Logstash)│
└────────┬────────────┘
         │
         ↓ HTTP/socket
┌─────────────────────────────┐
│  Log Aggregation            │
│  (Elasticsearch/Splunk/     │
│   CloudWatch)               │
└────────┬────────────────────┘
         │
         ↓ Querying
┌─────────────────────┐
│  Analytics/         │
│  Dashboards         │
│  Alerts             │
└─────────────────────┘
```

---

## Pattern 1: Structured Logging Basics

### The Implementation

```python
# src/structured_logger.py
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict
import uuid

class StructuredLogger:
    """Structured JSON logging for network automation."""
    
    def __init__(self, name: str, level=logging.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually __name__)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove default handlers
        self.logger.handlers = []
        
        # Create JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        
        # Unique ID for this execution
        self.correlation_id = str(uuid.uuid4())
    
    def _add_context(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Add standard context to log entry."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": self.correlation_id,
            **extra
        }
    
    def info(self, message: str, **context):
        """Log info level with context."""
        self.logger.info(
            message,
            extra=self._add_context(context)
        )
    
    def warning(self, message: str, **context):
        """Log warning level with context."""
        self.logger.warning(
            message,
            extra=self._add_context(context)
        )
    
    def error(self, message: str, exception=None, **context):
        """Log error level with context and optional exception."""
        if exception:
            context["exception"] = str(exception)
            context["exception_type"] = type(exception).__name__
        
        self.logger.error(
            message,
            extra=self._add_context(context),
            exc_info=exception
        )
    
    def debug(self, message: str, **context):
        """Log debug level with context."""
        self.logger.debug(
            message,
            extra=self._add_context(context)
        )


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for machine parsing."""
    
    def format(self, record):
        """Convert log record to JSON."""
        log_data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, "timestamp"):
            log_data["timestamp"] = record.timestamp
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        
        # Add any custom fields from extra={}
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName", 
                          "levelname", "levelno", "lineno", "module", "msecs", 
                          "message", "pathname", "process", "processName", "relativeCreated",
                          "thread", "threadName", "exc_info", "exc_text", "stack_info"]:
                log_data[key] = value
        
        return json.dumps(log_data)
```

### Usage Example

```python
from structured_logger import StructuredLogger

logger = StructuredLogger(__name__)

# Simple log
logger.info("Deployment started", phase="validation")

# Log with context
logger.info(
    "Device configuration retrieved",
    device="router1",
    lines=245,
    duration_ms=1234
)

# Error logging
try:
    connect_to_device("10.0.0.1")
except Exception as e:
    logger.error(
        "Failed to connect to device",
        device="router1",
        exception=e
    )

# Output (pretty-printed):
# {
#   "level": "INFO",
#   "logger": "__main__",
#   "message": "Device configuration retrieved",
#   "timestamp": "2026-03-04T14:23:45.123456",
#   "correlation_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
#   "device": "router1",
#   "lines": 245,
#   "duration_ms": 1234
# }
```

---

## Pattern 2: Contextual Logging Across Operations

### The Problem

When deploying to 50 devices, how do you track which device failed?

```python
# ❌ BAD - No context
for device in devices:
    configure_device(device)

# Logs show errors but not WHICH device
# Result: "ERROR: Configuration failed"
```

### The Solution: Operation Context

```python
# ✅ GOOD - Rich context
logger = StructuredLogger(__name__)

for device in devices:
    logger.info(
        "Starting device configuration",
        device=device.host,
        sequence=devices.index(device) + 1,
        total_devices=len(devices)
    )
    
    try:
        configure_device(device)
        logger.info(
            "Device configuration completed",
            device=device.host,
            status="success"
        )
    except Exception as e:
        logger.error(
            "Device configuration failed",
            device=device.host,
            status="failed",
            exception=e
        )
        # Later, can query: "Show all failures for router1"
```

### Implementation

```python
# src/contextual_logging.py
from contextlib import contextmanager
from structured_logger import StructuredLogger

class OperationLogger:
    """Logger with automatic operation context."""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.operation_stack = []
    
    @contextmanager
    def operation(self, operation_name: str, **context):
        """
        Context manager for logging operations.
        
        Example:
            with op_logger.operation("deploy_to_device", device="router1"):
                configure_device()
                # All logs within this block include device context
        """
        # Add operation to stack
        self.operation_stack.append({
            "operation": operation_name,
            **context
        })
        
        try:
            self.logger.info(
                f"{operation_name} started",
                **context
            )
            yield
            
            self.logger.info(
                f"{operation_name} completed",
                status="success",
                **context
            )
        
        except Exception as e:
            self.logger.error(
                f"{operation_name} failed",
                status="failed",
                exception=e,
                **context
            )
            raise
        
        finally:
            self.operation_stack.pop()
```

### Usage with Nornir

```python
# src/nornir_logging_task.py
from nornir import InitNornir
from nornir.core.task import Task, Result
from contextual_logging import OperationLogger
from structured_logger import StructuredLogger

logger = StructuredLogger(__name__)
op_logger = OperationLogger(logger)

def deploy_with_logging(task: Task) -> Result:
    """Nornir task with structured logging."""
    with op_logger.operation("device_deployment", device=task.host.name):
        device = task.host.get_connection("netmiko", task.nornir.config)
        
        with op_logger.operation("get_current_state", device=task.host.name):
            current_config = device.send_command("show running-config")
            logger.debug(
                "Current configuration retrieved",
                device=task.host.name,
                config_lines=len(current_config.split('\n'))
            )
        
        with op_logger.operation("apply_changes", device=task.host.name):
            device.send_command("configure terminal")
            device.send_command("hostname " + task.host.name)
            device.send_command("end")
            logger.info(
                "Configuration changes applied",
                device=task.host.name
            )
        
        return Result(
            host=task.host,
            result="Deployment successful"
        )

# Usage
nr = InitNornir(config_file="config.yaml")
results = nr.run(task=deploy_with_logging)
```

---

## Pattern 3: Performance Metrics Logging

### The Implementation

```python
# src/metrics_logger.py
import time
from structured_logger import StructuredLogger

class MetricsLogger:
    """Log operation metrics (duration, throughput, etc.)."""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def log_duration(self, operation: str, duration_ms: float, **context):
        """Log operation duration."""
        self.logger.info(
            f"{operation} duration",
            operation=operation,
            duration_ms=f"{duration_ms:.2f}",
            **context
        )
    
    def log_throughput(self, operation: str, items: int, duration_ms: float, **context):
        """Log throughput (items per second)."""
        throughput = (items / duration_ms) * 1000 if duration_ms > 0 else 0
        
        self.logger.info(
            f"{operation} throughput",
            operation=operation,
            items=items,
            duration_ms=f"{duration_ms:.2f}",
            throughput_per_sec=f"{throughput:.2f}",
            **context
        )
    
    def time_operation(self, operation: str, **context):
        """Context manager to automatically time operations."""
        class Timer:
            def __enter__(timer_self):
                timer_self.start = time.time()
                return timer_self
            
            def __exit__(timer_self, *args):
                duration = (time.time() - timer_self.start) * 1000  # ms
                self.log_duration(operation, duration, **context)
        
        return Timer()
```

### Usage

```python
logger = StructuredLogger(__name__)
metrics = MetricsLogger(logger)

# Automatic timing
with metrics.time_operation("device_configuration", device="router1"):
    configure_device(device)

# Manual metrics  
start = time.time()
devices_processed = 0
for device in devices:
    deploy_to_device(device)
    devices_processed += 1
duration = (time.time() - start) * 1000

metrics.log_throughput(
    "fleet_deployment",
    items=devices_processed,
    duration_ms=duration,
    total_devices=len(devices)
)
```

---

## Pattern 4: Log Aggregation Integration

### Sending Logs to Elasticsearch

```python
# src/elasticsearch_logger.py
import json
import logging
from datetime import datetime, timezone
from elasticsearch import Elasticsearch
from structured_logger import StructuredLogger

class ElasticsearchHandler(logging.Handler):
    """Send logs to Elasticsearch."""
    
    def __init__(self, hosts: list, index_name: str = "network-automation"):
        """
        Initialize Elasticsearch handler.
        
        Args:
            hosts: Elasticsearch hosts (e.g., ["localhost:9200"])
            index_name: Index name for logs
        """
        super().__init__()
        self.es = Elasticsearch(hosts=hosts)
        self.index_name = index_name
    
    def emit(self, record):
        """Send log record to Elasticsearch."""
        try:
            log_data = json.loads(self.format(record))
            
            # Add timestamp for Elasticsearch
            log_data["@timestamp"] = log_data.get("timestamp", datetime.now(timezone.utc).isoformat())
            
            # Send to Elasticsearch
            self.es.index(
                index=f"{self.index_name}-{datetime.now(timezone.utc):%Y.%m.%d}",
                document=log_data
            )
        except Exception as e:
            self.handleError(record)
```

### Setup

```python
# In your application startup
logger = StructuredLogger(__name__)

# Add Elasticsearch handler
es_handler = ElasticsearchHandler(hosts=["localhost:9200"])
es_handler.setFormatter(JSONFormatter())
logger.logger.addHandler(es_handler)

# Now all logs are sent to Elasticsearch
logger.info("Application started")
```

### Elasticsearch Queries

```bash
# Find all failures for device router1
GET network-automation-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"device": "router1"}},
        {"term": {"level": "ERROR"}}
      ]
    }
  }
}

# Find slow operations
GET network-automation-*/_search
{
  "query": {
    "range": {
      "duration_ms": {"gte": 5000}
    }
  }
}

# Group errors by device
GET network-automation-*/_search
{
  "aggs": {
    "errors_by_device": {
      "terms": {"field": "device"}
    }
  }
}
```

---

## Pattern 5: Audit Logging for Compliance

```python
# src/audit_logger.py
import json
import logging
from structured_logger import StructuredLogger

class AuditLogger:
    """Compliance-grade audit logging."""
    
    def __init__(self):
        self.logger = StructuredLogger("audit", level=logging.INFO)
    
    def log_action(self, action: str, actor: str, resource: str, result: str, **context):
        """
        Log an action for compliance.
        
        Args:
            action: What was done (e.g., "configure_vlan")
            actor: Who did it (user, service account)
            resource: What was affected (device, interface)
            result: success or failure
        """
        self.logger.info(
            f"Action: {action}",
            action=action,
            actor=actor,
            resource=resource,
            result=result,
            **context
        )
    
    def log_configuration_change(self, device: str, change_type: str, change_details: dict):
        """Log configuration change."""
        self.logger.info(
            "Configuration change",
            device=device,
            change_type=change_type,
            change_details=json.dumps(change_details),
            audit_required=True
        )
    
    def log_authentication(self, user: str, resource: str, success: bool):
        """Log authentication attempt."""
        self.logger.info(
            "Authentication attempt",
            user=user,
            resource=resource,
            success=success,
            audit_required=True
        )
```

### Usage

```python
audit = AuditLogger()

# Log before making changes
audit.log_action(
    action="deploy_vlan_config",
    actor="automation_service",
    resource="router1",
    result="pending",
    vlan_ids=[100, 101, 102]
)

# Deploy configuration...

# Log after completion
audit.log_action(
    action="deploy_vlan_config",
    actor="automation_service",
    resource="router1",
    result="success",
    vlan_ids=[100, 101, 102],
    duration_ms=1234
)
```

---

## Best Practices

### 1. Log at the Right Level

```python
# ✅ GOOD
logger.debug("Verbose details for developers")
logger.info("Normal operations")
logger.warning("Something might be wrong")
logger.error("Something is definitely wrong")

# ❌ BAD - Everything at INFO
logger.info("Detailed debug info")
logger.info("Normal operation")
logger.info("ERROR happening here")
```

### 2. Include Actionable Context

```python
# ✅ GOOD - Easy to find and fix
logger.error(
    "Device configuration failed",
    device="router1",
    module="bgp",
    expected_neighbors=3,
    actual_neighbors=1
)

# ❌ BAD - Vague
logger.error("Configuration failed")
```

### 3. Never Log Sensitive Data

```python
# ❌ ABSOLUTELY NOT
logger.info(f"Connecting with username={username} password={password}")

# ✅ GOOD
logger.info("Authenticating to device", device=host)
```

### 4. Use Correlation IDs

```python
# All logs from one operation get same correlation_id
logger = StructuredLogger(__name__)

# Correlation ID automatically injected
logger.info("Starting deployment")
logger.info("Device 1 configured")
logger.info("Device 2 configured")

# Later: Query all logs for one deployment
# GET logs where correlation_id = "..."
```

---

## Summary

| Concept | Why It Matters |
| :--- | :--- |
| **Structured JSON** | Machines can parse, aggregate, and analyze |
| **Correlation IDs** | Track operations across multiple devices |
| **Log Levels** | Find important information quickly |
| **Context** | Know which device, what operation, when |
| **Aggregation** | Centralized visibility across all automation |
| **Audit Trail** | Compliance and forensics |

**Structured logging transforms logs from debugging tools into operational intelligence.**

---

## Next Steps

- **[Health Checks & Pre-Flight](./health-checks-pre-flight-validation.md)** — Log pre-deployment validation
- **[Circuit Breakers](../expert/circuit-breakers-backpressure-network-automation.md)** — Log safe failure patterns
