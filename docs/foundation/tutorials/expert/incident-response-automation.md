---
title: Incident Response Automation
description: Detect, remediate, and recover from network incidents automatically. Pattern matching, self-healing networks, and incident tracking. Enterprise-grade automation.
tags:
  - Incident Response
  - Automation
  - Self-Healing Networks
  - Remediation
  - Expert
  - Resilience
---

## Why Automated Response Matters

**Scenario:** BGP session flaps at 2 AM.

**Manual response:**

- Alert fires at 2 AM
- Engineer gets paged
- Waits 15-30 minutes for engineer to respond
- Engineer investigates (15 minutes)
- Engineer identifies cause (10 minutes)
- Engineer applies fix (10 minutes)
- **Total: 60-90 minutes of outage**

**With automated response:**

- Alert fires at 2 AM
- Automated system identifies flapping pattern
- Runs diagnostics in parallel
- Identifies isolated peer with bad BGP config
- Withdraws peer routes, updates peer config, re-enables
- **Total: 90 seconds of outage**
- Engineer reviews incident history next morning

**Automated response reduces MTTR (Mean Time To Repair) by 98%.**

---

## Pattern 1: Event Detection Engine

### The Implementation

```python
# src/incident_detector.py
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Callable
from datetime import datetime
from enum import Enum
import json

class SeverityLevel(Enum):
    """Incident severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "info"

class RemediationType(Enum):
    """Type of remediation available."""
    AUTOMATIC = "automatic"  # Can be fixed without approval
    MANUAL = "manual"        # Requires engineer approval
    ESCALATE = "escalate"    # Escalate to NOC

@dataclass
class Incident:
    """Detected incident."""
    id: str
    name: str
    severity: SeverityLevel
    device: str
    symptoms: Dict[str, Any]
    detected_at: datetime
    remediation_type: RemediationType
    likely_causes: List[str]
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity.value,
            "device": self.device,
            "symptoms": self.symptoms,
            "detected_at": self.detected_at.isoformat(),
            "remediation_type": self.remediation_type.value,
            "likely_causes": self.likely_causes
        }

class PatternMatcher:
    """Detect incidents from device metrics and events."""
    
    def __init__(self):
        self.patterns = {}
        self.incident_counter = 0
    
    def register_pattern(
        self,
        name: str,
        check_func: Callable,
        severity: SeverityLevel,
        remediation_type: RemediationType,
        likely_causes: List[str] = None
    ):
        """
        Register pattern to detect.
        
        Args:
            name: Pattern name
            check_func: Function to detect pattern (returns True if found)
            severity: Incident severity
            remediation_type: Type of remediation available
            likely_causes: List of possible root causes
        """
        self.patterns[name] = {
            "check_func": check_func,
            "severity": severity,
            "remediation_type": remediation_type,
            "likely_causes": likely_causes or []
        }
    
    def detect(self, device: str, metrics: Dict) -> List[Incident]:
        """
        Check all patterns against device metrics.
        
        Args:
            device: Device name
            metrics: Device metrics/state
        
        Returns:
            List of detected incidents
        """
        incidents = []
        
        for pattern_name, pattern in self.patterns.items():
            try:
                if pattern["check_func"](metrics):
                    incident = Incident(
                        id=f"INC-{self.incident_counter:05d}",
                        name=pattern_name,
                        severity=pattern["severity"],
                        device=device,
                        symptoms=metrics,
                        detected_at=datetime.now(),
                        remediation_type=pattern["remediation_type"],
                        likely_causes=pattern["likely_causes"]
                    )
                    incidents.append(incident)
                    self.incident_counter += 1
            
            except Exception as e:
                # Log pattern check failure, continue
                print(f"⚠ Pattern '{pattern_name}' check failed: {e}")
        
        return incidents
```

### Pattern Registration Examples

```python
# src/patterns.py
from incident_detector import PatternMatcher, SeverityLevel, RemediationType

detector = PatternMatcher()

# Pattern: BGP session flapping
detector.register_pattern(
    name="BGP Session Flapping",
    check_func=lambda m: (
        m.get("bgp_session_changes_last_hour", 0) > 10 and
        m.get("bgp_session_state") != "Established"
    ),
    severity=SeverityLevel.HIGH,
    remediation_type=RemediationType.AUTOMATIC,
    likely_causes=[
        "BGP configuration mismatch",
        "Network connectivity issue",
        "Peer interface bouncing",
        "CPU overload"
    ]
)

# Pattern: High interface error rate
detector.register_pattern(
    name="High Interface Error Rate",
    check_func=lambda m: (
        m.get("interface_crc_errors", 0) > 100 or
        m.get("interface_errors_percent", 0) > 5
    ),
    severity=SeverityLevel.CRITICAL,
    remediation_type=RemediationType.MANUAL,
    likely_causes=[
        "Duplex mismatch",
        "Defective cable",
        "Port flapping",
        "Controller issue"
    ]
)

# Pattern: Low memory
detector.register_pattern(
    name="Low Available Memory",
    check_func=lambda m: m.get("available_memory_percent", 100) < 10,
    severity=SeverityLevel.HIGH,
    remediation_type=RemediationType.MANUAL,
    likely_causes=[
        "Memory leak in process",
        "Process consuming too much memory",
        "Device needs restart"
    ]
)

# Pattern: Reachability loss
detector.register_pattern(
    name="Device Unreachable",
    check_func=lambda m: not m.get("reachable", True),
    severity=SeverityLevel.CRITICAL,
    remediation_type=RemediationType.ESCALATE,
    likely_causes=[
        "Network connectivity issue",
        "Device down",
        "Routing issues",
        "Management interface failure"
    ]
)
```

---

## Pattern 2: Automatic Remediation Engine

```python
# src/remediation.py
from dataclasses import dataclass
from typing import Any, Callable, Dict
from datetime import datetime
from incident_detector import Incident, RemediationType

@dataclass
class RemediationAction:
    """Single remediation step."""
    name: str
    func: Callable
    validate_func: Callable = None  # Verify remediation worked
    
    async def execute(self) -> bool:
        """Execute remediation and validate."""
        try:
            print(f"  Executing: {self.name}")
            await self.func()
            
            if self.validate_func:
                if await self.validate_func():
                    print(f"  ✓ {self.name} successful")
                    return True
                else:
                    print(f"  ✗ {self.name} validation failed")
                    return False
            
            return True
        
        except Exception as e:
            print(f"  ✗ {self.name} failed: {e}")
            return False

class RemediationRunbook:
    """Define remediation steps for an incident type."""
    
    def __init__(self, incident_name: str):
        self.incident_name = incident_name
        self.actions = []
        self.rollback_actions = []
    
    def add_action(
        self,
        name: str,
        func: Callable,
        validate_func: Callable = None,
        reversible: bool = True
    ):
        """Add remediation action."""
        action = RemediationAction(name, func, validate_func)
        self.actions.append(action)
        
        if reversible:
            self.rollback_actions.insert(0, action)
    
    async def execute(self, incident: Incident) -> Dict[str, Any]:
        """
        Execute all remediation actions.
        
        Args:
            incident: Incident to remediate
        
        Returns:
            dict with execution results and success status
        """
        print(f"\n🔧 Remediating: {self.incident_name}")
        print(f"   Device: {incident.device}")
        print(f"   Likely causes: {', '.join(incident.likely_causes)}\n")
        
        results = {
            "incident_id": incident.id,
            "actions_taken": [],
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        for action in self.actions:
            success = await action.execute()
            results["actions_taken"].append({
                "name": action.name,
                "success": success
            })
            
            if not success:
                results["success"] = False
                print(f"\n⚠ Remediation failed at: {action.name}")
                print(f"  Rolling back to previous state...")
                
                # Execute rollback
                for rollback_action in self.rollback_actions:
                    print(f"  Undoing: {rollback_action.name}")
                    try:
                        await rollback_action.func()
                    except:
                        pass
                
                break
        
        return results
```

### Remediation Runbook Examples

```python
# src/remediation_runbooks.py
from remediation import RemediationRunbook
from netmiko import ConnectHandler

# BGP Flapping Remediation
bgp_flapping_runbook = RemediationRunbook("BGP Session Flapping")

async def clear_bgp_session(device):
    """Clear and re-establish BGP session."""
    conn = ConnectHandler(**device)
    conn.send_command("clear ip bgp * soft")
    conn.disconnect()

async def verify_bgp_stable(device):
    """Verify BGP session is stable."""
    conn = ConnectHandler(**device)
    output = conn.send_command("show ip bgp summary")
    # Check for stable state
    conn.disconnect()
    return "Established" in output

bgp_flapping_runbook.add_action(
    name="Clear BGP session",
    func=lambda: clear_bgp_session(device_dict),
    validate_func=lambda: verify_bgp_stable(device_dict),
    reversible=True
)

# Interface Error Remediation
interface_error_runbook = RemediationRunbook("High Interface Error Rate")

async def restart_interface(device, interface):
    """Cycle interface power."""
    conn = ConnectHandler(**device)
    conn.send_config_set([
        f"interface {interface}",
        "shutdown",
        "no shutdown"
    ])
    conn.disconnect()

async def verify_interface_healthy(device, interface):
    """Verify interface is up and healthy."""
    conn = ConnectHandler(**device)
    output = conn.send_command(f"show interface {interface}")
    conn.disconnect()
    return "up" in output.lower() and "crc" not in output.lower()

interface_error_runbook.add_action(
    name="Restart interface",
    func=lambda: restart_interface(device, interface),
    validate_func=lambda: verify_interface_healthy(device, interface),
    reversible=True
)
```

---

## Pattern 3: Incident Tracking & History

```python
# src/incident_tracker.py
import json
from datetime import datetime
from pathlib import Path
from incident_detector import Incident

class IncidentTracker:
    """Track incidents and remediation history."""
    
    def __init__(self, history_file: str = "incidents.jsonl"):
        self.history_file = Path(history_file)
    
    def record_incident(self, incident: Incident):
        """Log detected incident."""
        with open(self.history_file, "a") as f:
            record = {
                "type": "incident_detected",
                "timestamp": datetime.now().isoformat(),
                "incident": incident.to_dict()
            }
            f.write(json.dumps(record) + "\n")
    
    def record_remediation(self, incident_id: str, result: dict):
        """Log remediation attempt."""
        with open(self.history_file, "a") as f:
            record = {
                "type": "remediation_executed",
                "timestamp": datetime.now().isoformat(),
                "incident_id": incident_id,
                "result": result
            }
            f.write(json.dumps(record) + "\n")
    
    def get_incident_history(self, device: str = None) -> List[dict]:
        """Get incident history for device."""
        if not self.history_file.exists():
            return []
        
        incidents = []
        with open(self.history_file, "r") as f:
            for line in f:
                record = json.loads(line)
                
                # Filter by device if specified
                if device and record["type"] == "incident_detected":
                    if record["incident"]["device"] != device:
                        continue
                
                incidents.append(record)
        
        return incidents
    
    def get_mttr(self, days: int = 7) -> float:
        """
        Calculate Mean Time To Repair.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Average repair time in minutes
        """
        incidents = self.get_incident_history()
        
        incident_times = {}
        for record in incidents:
            if record["type"] == "incident_detected":
                incident_id = record["incident"]["id"]
                incident_times[incident_id] = {
                    "detected": record["timestamp"]
                }
            
            elif record["type"] == "remediation_executed":
                incident_id = record["incident_id"]
                if incident_id in incident_times:
                    incident_times[incident_id]["remediated"] = record["timestamp"]
        
        # Calculate repair time for incidents with remediation
        repair_times = []
        for inc_id, times in incident_times.items():
            if "remediated" in times:
                detected = datetime.fromisoformat(times["detected"])
                remediated = datetime.fromisoformat(times["remediated"])
                repair_time = (remediated - detected).total_seconds() / 60
                repair_times.append(repair_time)
        
        if repair_times:
            return sum(repair_times) / len(repair_times)
        return 0
```

---

## Pattern 4: Adaptive Response Based on History

```python
# src/adaptive_remediation.py
from incident_tracker import IncidentTracker

class AdaptiveRemediationEngine:
    """Learn from incident history and adjust remediation."""
    
    def __init__(self, tracker: IncidentTracker):
        self.tracker = tracker
        self.success_rates = {}
    
    def calculate_success_rate(self, remediation_name: str) -> float:
        """Calculate success rate of remediation type."""
        incidents = self.tracker.get_incident_history()
        
        total = 0
        successful = 0
        
        for record in incidents:
            if record["type"] == "remediation_executed":
                for action in record["result"].get("actions_taken", []):
                    if action["name"] == remediation_name:
                        total += 1
                        if action["success"]:
                            successful += 1
        
        if total == 0:
            return 0.0
        
        return (successful / total) * 100
    
    def select_remediation_strategy(
        self,
        incident_name: str,
        available_strategies: List[RemediationRunbook]
    ) -> RemediationRunbook:
        """
        Select best remediation based on historical success.
        
        Args:
            incident_name: Type of incident
            available_strategies: Possible remediation approaches
        
        Returns:
            Best remediation strategy based on history
        """
        strategy_scores = {}
        
        for strategy in available_strategies:
            success_rate = self.calculate_success_rate(strategy.incident_name)
            strategy_scores[strategy.incident_name] = success_rate
        
        # Return strategy with highest success rate
        best_strategy = max(
            available_strategies,
            key=lambda s: strategy_scores.get(s.incident_name, 0)
        )
        
        print(f"Selected strategy: {best_strategy.incident_name} "
              f"(success rate: {strategy_scores[best_strategy.incident_name]:.1f}%)")
        
        return best_strategy
```

---

## Best Practices

### 1. Separate Automatic vs Manual Remediation

```python
# ✅ GOOD - Clear separation
async def handle_incident(incident):
    match incident.severity:
        case SeverityLevel.LOW:
            await automatic_remediation.execute(incident)

        case SeverityLevel.CRITICAL:
            await escalate_to_noc(incident)

# ❌ BAD - Auto-fix critical issues
async def auto_fix_critical(incident):
    if incident.severity == SeverityLevel.CRITICAL:
        await automatic_fix(incident)  # Too risky!
```

### 2. Always Validate Before and After

```python
# ✅ GOOD - Comprehensive validation
async def remediate():
    # Validate current state
    if not await validate_incident():
        return False
    
    # Apply fix
    await fix_issue()
    
    # Validate fix worked
    if not await validate_fix():
        await rollback()
        return False
    
    return True

# ❌ BAD - No validation
async def remediate():
    await fix_issue()  # Hope it works
```

### 3. Design for Rollback

```python
# ✅ GOOD - Keep rollback capability
actions = [
    RemediationAction(
        "update_config",
        func=update_config,
        reversible=True  # Can rollback
    )
]

# ❌ BAD - No way to undo
async def fix_issue():
    delete_old_config()  # Can't rollback
    apply_new_config()
    restart_service()
```

### 4. Track and Learn

```python
# ✅ GOOD - Record all activity
async def track_and_learn(incident):
    tracker.record_incident(incident)
    result = await remediation.execute(incident)
    tracker.record_remediation(incident.id, result)

    # Analyze and improve
    mttr = tracker.get_mttr()
    print(f"MTTR: {mttr:.1f} minutes")

# ❌ BAD - Silent failures
async def silent_remediation(incident):
    await remediation.execute(incident)  # No record of what happened
```

---

## Production Deployment Example

```python
# src/automation_engine.py
import asyncio
from datetime import datetime
from typing import List
from netmiko import ConnectHandler
from incident_detector import Incident, PatternMatcher, RemediationType, SeverityLevel
from remediation import RemediationRunbook
from incident_tracker import IncidentTracker

class AutomationEngine:
    """Main orchestration for incident detection and response."""
    
    def __init__(self, devices: List[dict]):
        self.devices = devices
        self.detector = PatternMatcher()
        self.tracker = IncidentTracker()
        self.runbooks = {}
        
        # Register patterns
        self._register_patterns()
        
        # Register runbooks
        self._register_runbooks()
    
    def _register_patterns(self):
        """Register all incident detection patterns."""
        # BGP flapping
        self.detector.register_pattern(
            name="BGP Session Flapping",
            check_func=lambda m: (
                m.get("bgp_changes_hour", 0) > 10 and
                not m.get("bgp_established", True)
            ),
            severity=SeverityLevel.HIGH,
            remediation_type=RemediationType.AUTOMATIC
        )
        # ... more patterns
    
    def _register_runbooks(self):
        """Register remediation runbooks."""
        bgp_runbook = RemediationRunbook("BGP Session Flapping")
        # ... configure runbook
        self.runbooks["BGP Session Flapping"] = bgp_runbook
    
    async def check_device(self, device: dict) -> List[Incident]:
        """Collect metrics and detect incidents."""
        try:
            conn = ConnectHandler(**device)
            
            metrics = {
                "reachable": True,
                "bgp_changes_hour": self._count_bgp_changes(conn),
                "bgp_established": self._check_bgp_established(conn),
                "interface_errors": self._get_interface_errors(conn)
            }
            
            conn.disconnect()
            
            incidents = self.detector.detect(device["host"], metrics)
            return incidents
        
        except Exception as e:
            return [Incident(
                id="INC-UNREACHABLE",
                name="Device Unreachable",
                severity=SeverityLevel.CRITICAL,
                device=device["host"],
                symptoms={"error": str(e)},
                detected_at=datetime.now(),
                remediation_type=RemediationType.ESCALATE,
                likely_causes=["Network down", "Device down"]
            )]
    
    async def run(self, check_interval: int = 60):
        """Main event loop."""
        print("Starting incident response engine...")
        
        while True:
            print(f"\n[{datetime.now()}] Checking devices...")
            
            # Check all devices
            all_incidents = []
            for device in self.devices:
                incidents = await self.check_device(device)
                all_incidents.extend(incidents)
            
            # Process incidents
            for incident in all_incidents:
                print(f"\n{incident.severity.value.upper()}: {incident.name} on {incident.device}")
                
                self.tracker.record_incident(incident)
                
                # Only auto-remediate lower severity
                if incident.remediation_type == RemediationType.AUTOMATIC:
                    if incident.name in self.runbooks:
                        runbook = self.runbooks[incident.name]
                        result = await runbook.execute(incident)
                        self.tracker.record_remediation(incident.id, result)
                
                else:
                    print(f"  ⚠ Escalating to NOC: {incident.likely_causes}")
            
            # Wait for next check
            await asyncio.sleep(check_interval)
```

---

## Summary

Incident automation provides:

- **Detection** → Pattern matching identifies problems
- **Response** → Automatic remediation for known issues
- **History** → Track what happened and why
- **Learning** → Improve over time based on results
- **Visibility** → Know MTTR and system health

---

## Related Patterns

- **[Testing Patterns](../intermediate/testing-network-automation.md)** — Test remediation behaviours
- **[Health Checks](../intermediate/health-checks-pre-flight-validation.md)** — Detect issues early
- **[Circuit Breakers](./circuit-breakers-backpressure-network-automation.md)** — Prevent cascade failures
