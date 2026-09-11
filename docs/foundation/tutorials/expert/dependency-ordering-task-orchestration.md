---
title: Dependency Management & Task Orchestration
description: Coordinate complex multi-device workflows. Task DAGs, dependency ordering, and safe parallel execution. Orchestrate enterprise automation at scale.
tags:
  - Task Orchestration
  - Dependencies
  - DAG
  - Network Automation
  - Expert
  - Workflows
  - Nornir
---

## Why Task Ordering Matters

**Scenario:** Deploy new WAN architecture across 10 sites.

**Simple approach** (no dependency management):

- Start deploying to all sites in parallel
- Site 5 finishes before Site 1's dependencies are ready
- Everything breaks

**With dependency management:**

- Deploy hub site first
- Wait for hub to be ready
- Then deploy spoke sites to the hub
- Everything works in correct order

**Dependency management ensures safe, predictable execution order.**

---

## Pattern 1: Task DAG (Directed Acyclic Graph)

### The Implementation

```python
# src/task_orchestrator.py
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Callable
from enum import Enum

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    """Represents a single task in the workflow."""
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    dependencies: List[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.dependencies is None:
            self.dependencies = []

class TaskOrchestrator:
    """Execute tasks in dependency order."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.execution_order = []
    
    def add_task(
        self,
        name: str,
        func: Callable,
        dependencies: List[str] = None,
        **kwargs
    ):
        """
        Add task to DAG.
        
        Args:
            name: Task name
            func: Function to execute
            dependencies: List of task names this depends on
            **kwargs: Arguments to pass to function
        """
        task = Task(
            name=name,
            func=func,
            kwargs=kwargs,
            dependencies=dependencies or []
        )
        self.tasks[name] = task
    
    def _validate_dependencies(self) -> None:
        """Ensure all dependencies reference known tasks."""
        missing = {
            dep
            for task in self.tasks.values()
            for dep in task.dependencies
            if dep not in self.tasks
        }
        if missing:
            raise ValueError(f"Unknown task dependencies: {sorted(missing)}")
     
    def validate_dag(self) -> bool:
        """Check for cycles in dependency graph."""
        self._validate_dependencies()
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for dep in self.tasks[node].dependencies:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_name in self.tasks:
            if task_name not in visited:
                if has_cycle(task_name):
                    return False
        
        return True
    
    def topological_sort(self) -> List[str]:
        """
        Calculate execution order using topological sort.
        
        Returns:
            List of task names in execution order
        """
        if not self.validate_dag():
            raise ValueError("DAG contains cycle - impossible to order")
        
        visited = set()
        order = []
        
        def visit(node):
            if node in visited:
                return
            
            visited.add(node)
            
            # Visit dependencies first
            for dep in self.tasks[node].dependencies:
                visit(dep)
            
            order.append(node)
        
        for task_name in self.tasks:
            visit(task_name)
        
        return order
    
    def execute(self) -> Dict[str, any]:
        """
        Execute all tasks in dependency order.
        
        Returns:
            dict: Results for each task
        """
        execution_order = self.topological_sort()
        results = {}
        
        print(f"Execution order: {' → '.join(execution_order)}\n")
        
        for task_name in execution_order:
            task = self.tasks[task_name]
            
            # Check if any dependencies failed
            deps_failed = [
                dep for dep in task.dependencies
                if self.tasks[dep].status == TaskStatus.FAILED
            ]
            
            if deps_failed:
                task.status = TaskStatus.SKIPPED
                print(f"⏭ Skipping '{task_name}' (depends on failed: {deps_failed})")
                results[task_name] = {
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error
                }
                continue
            
            task.status = TaskStatus.RUNNING
            print(f"▶ Running '{task_name}'...")
            
            try:
                task.result = task.func(**task.kwargs)
                task.status = TaskStatus.SUCCESS
                print(f"✓ '{task_name}' completed\n")
            
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                print(f"✗ '{task_name}' failed: {str(e)}\n")
            
            results[task_name] = {
                "status": task.status.value,
                "result": task.result,
                "error": task.error
            }
        
        return results
    
    def get_dependency_graph(self) -> dict:
        """Get human-readable dependency graph."""
        return {
            name: task.dependencies
            for name, task in self.tasks.items()
        }
```

### Usage Example

```python
from task_orchestrator import TaskOrchestrator

def setup_hub():
    print("  Setting up hub router...")
    # hub setup logic
    return {"hub": "ready"}

def setup_spoke(spoke_id):
    print(f"  Setting up spoke {spoke_id}...")
    # spoke setup logic
    return {"spoke": spoke_id}

def verify_hub_connectivity():
    print("  Verifying hub connectivity...")
    return True

# Create orchestrator
orchestrator = TaskOrchestrator()

# Add tasks with dependencies
orchestrator.add_task("setup_hub", setup_hub)
orchestrator.add_task(
    "verify_hub",
    verify_hub_connectivity,
    dependencies=["setup_hub"]
)
orchestrator.add_task(
    "setup_spoke_1",
    setup_spoke,
    spoke_id=1,
    dependencies=["verify_hub"]
)
orchestrator.add_task(
    "setup_spoke_2",
    setup_spoke,
    spoke_id=2,
    dependencies=["verify_hub"]
)

# Visualize
print("Dependency Graph:")
print(orchestrator.get_dependency_graph())

# Execute
results = orchestrator.execute()

print("\nFinal Results:")
for task, result in results.items():
    print(f"  {task}: {result['status']}")
```

---

## Pattern 2: Nornir-Based Orchestration

```python
# src/nornir_orchestration.py
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir.core.filter import F

def orchestrate_multisite_deployment():
    """Orchestrate deployment across multiple sites."""
    
    # Load inventory
    nr = InitNornir(config_file="config.yaml")
    
    # Define sites and dependencies
    sites = {
        "hub1": {
            "devices": ["hub1-router", "hub1-switch"],
            "depends_on": []
        },
        "site1": {
            "devices": ["site1-router"],
            "depends_on": ["hub1"]
        },
        "site2": {
            "devices": ["site2-router"],
            "depends_on": ["hub1"]
        }
    }
    
    deployed_sites = set()
    results = {}
    
    # Deploy sites in dependency order
    for site, config in sites.items():
        # Wait for dependencies
        if not all(dep in deployed_sites for dep in config["depends_on"]):
            print(f"⏳ Waiting for dependencies for {site}...")
            continue
        
        print(f"\nDeploying site: {site}")
        
        # Filter inventory to this site's devices
        site_inventory = nr.filter(F(name__in=config["devices"]))
        
        # Deploy to site
        site_results = site_inventory.run(
            task=deploy_to_device
        )
        
        # Check results
        if all(not r[0].failed for r in site_results.values()):
            deployed_sites.add(site)
            results[site] = "success"
            print(f"✓ {site} deployment successful")
        else:
            results[site] = "failed"
            print(f"✗ {site} deployment failed")
    
    return results
```

---

## Pattern 3: Conditional Task Execution

```python
# src/conditional_execution.py
class ConditionalTask:
    """Execute task only if condition is met."""
    
    def __init__(self, name, func, condition=None, dependencies=None):
        self.name = name
        self.func = func
        self.condition = condition or (lambda: True)
        self.dependencies = dependencies or []
    
    def should_execute(self) -> bool:
        """Determine if this task should run."""
        return self.condition()

# Usage
tasks = [
    ConditionalTask(
        "update_hub",
        update_hub_config,
        condition=lambda: check_if_hub_needs_update()
    ),
    ConditionalTask(
        "rollback_hub",
        rollback_hub_config,
        condition=lambda: hub_deployment_failed(),
        dependencies=["update_hub"]
    )
]

# Only run tasks where condition is True
for task in tasks:
    if task.should_execute():
        task.func()
```

---

## Pattern 4: Parallelizable Subtasks

```python
# src/parallel_subtasks.py
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable

class ParallelTask:
    """Task that can execute sub-tasks in parallel."""
    
    def __init__(self, name: str, items: List, worker_func: Callable):
        self.name = name
        self.items = items
        self.worker_func = worker_func
    
    def execute(self, max_workers: int = 5) -> dict:
        """
        Execute task across items in parallel.
        
        Example:
            # Configure 100 devices in parallel
            task = ParallelTask(
                "configure_all_spokes",
                items=spoke_devices,
                worker_func=configure_device
            )
            results = task.execute(max_workers=10)
        """
        results = {"success": [], "failed": []}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.worker_func, item): item
                for item in self.items
            }
            
            for future in futures:
                item = futures[future]
                try:
                    result = future.result()
                    results["success"].append(item)
                except Exception as e:
                    results["failed"].append((item, str(e)))
        
        return results

# Usage
task = ParallelTask(
    "configure_spokes",
    items=[f"spoke{i}" for i in range(1, 51)],
    worker_func=configure_spoke_device
)

results = task.execute(max_workers=10)
print(f"✓ {len(results['success'])} spokes configured")
print(f"✗ {len(results['failed'])} spokes failed")
```

---

## Best Practices

### 1. Fail Fast, Skip Dependents

```python
# ✅ GOOD - Dependencies skip if upstream fails
if hub_setup.failed:
    skip_all_spoke_deployments()

# ❌ BAD - Attempt spoke setup despite hub failure
deploy_spokes()  # Will fail anyway, wastes time
```

### 2. Detect Dependency Cycles

```python
# ✅ GOOD - Validate before executing
orchestrator = TaskOrchestrator()
if not orchestrator.validate_dag():
    raise ValueError("Circular dependency detected!")

# ❌ BAD - Discover at runtime
orchestrator.execute()  # Hangs waiting for circular dependency
```

### 3. Document Dependencies

```python
# ✅ GOOD - Clear dependency documentation
orchestrator.add_task("configure_hub", configure_hub)
orchestrator.add_task(
    "verify_hub_up",
    verify_hub,
    dependencies=["configure_hub"]
)
orchestrator.add_task(
    "configure_spoke",
    configure_spoke,
    dependencies=["verify_hub_up"]  # Clear!
)

# ❌ BAD - Implicit dependencies
orchestrator.add_task("configure_hub", configure_hub)
orchestrator.add_task("configure_spoke", configure_spoke)
# Dependencies not obvious, might fail
```

---

## Advanced: Visualizing Execution Plans

```python
import json

def visualize_dag(orchestrator):
    """Print DAG visualization."""
    graph = orchestrator.get_dependency_graph()
    
    print("\nTask Dependencies:")
    for task, deps in graph.items():
        if deps:
            print(f"  {task} ← {deps}")
        else:
            print(f"  {task} (no dependencies)")
    
    execution_order = orchestrator.topological_sort()
    print(f"\nExecution Order: {' → '.join(execution_order)}")
```

---

## Summary

Task orchestration enables:

- **Dependency ordering** → Execute in safe order
- **Conditional execution** → Skip unnecessary tasks
- **Parallelism** → Run independent tasks together
- **Failure handling** → Skip dependents on failure
- **Visibility** → Know execution plan before running

---

## Next Steps

- **[Incident Response Automation](./incident-response-automation.md)** — Automated fixes for known issues
