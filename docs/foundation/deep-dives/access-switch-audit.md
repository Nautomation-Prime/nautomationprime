---
title: Access Switch Audit
description: Enterprise port intelligence tool with PoE monitoring, stale port detection, and professional Excel reporting. Modular Python automation for Cisco access switches.
tags:
  - Deep Dive
  - Access Switch
  - Port Audit
  - PoE
  - Excel
  - YAML
---

## Deep Dive: Access Switch Port Audit Tool

### "Enterprise Port Intelligence, Distilled to Pure Python."

!!! info "Version Alignment"
    This deep dive reflects the **current released state (May 2026)** of Access Switch Audit and aligns with the modular package structure, YAML configuration model, threaded collection workflow, bastion-handling path, stale-port logic, and Excel reporting behaviour described in the current tool release.

A modular Python utility that connects to Cisco switches (optionally through an SSH jump host), collects comprehensive interface details, PoE information, and neighbour presence, then exports a professional, filters-only Excel workbook with a SUMMARY sheet and one sheet per device. Built for production reliability with **YAML-based configuration**, **intelligent fallback parsing**, and **customisable credential management**.

!!! abstract "Premium tool — buy ready-to-run or have it customised"
    The **Access Switch Port Audit** tool is a production-grade Nautomation Prime tool. This deep dive shows exactly how it works; the tool itself is a premium product, available on request rather than as a free download.

    - **Buy as-is (unmodified) — £795:** the modular Python package and Excel reporting, delivered with a setup runbook and licensed for use in your environment.
    - **Customised to your estate — £2,000–£5,000:** tailored classification, PoE and stale-port logic, bastion handling, and workbook formatting for your access layer.

[Request this tool](../../contact.md){ .md-button .md-button--primary }
[Explore Services](../../services.md){ .md-button }

---

## 🧭 How to Read This Deep Dive

This guide is intended to show not only what the tool produces, but why the code is shaped the way it is. Read it using four lenses:

- **What happens** during collection, enrichment, and reporting
- **Why each design choice exists** in production terms
- **How to run it safely** using real commands and expected outcomes
- **Where to modify it** without destabilising the broader workflow

---

## 🗺️ Tutorial Roadmap

Read this guide in the following order:

1. Start with tool purpose, architecture, and configuration so the execution model is clear.
2. Review launcher usage, CLI arguments, and technical architecture to understand the operator path.
3. Study parsing, enrichment, stale logic, and Excel output sections to see how raw CLI becomes report data.
4. Finish with logging, extension, examples, FAQs, and learning outcomes to understand operational boundaries.

---

## 🔍 Transparency Contract

This guide is written to make the following explicit:

- What each collection stage gathers and how those data sources are fused
- Why stale-port logic is intentionally conservative
- How launcher, CLI, and report generation behave in real usage
- Where you can customise behaviour without breaking the broader audit flow

---

!!! success "What's New in Version 2.0"
    **The Access Switch Audit tool has been restructured into a professional Python package!**

    ✨ **Key Improvements:**
    
    - **Modular Architecture:** Code separated into focused modules (`cli.py`, `device_auditor.py`, `excel_reporter.py`, etc.)
    - **Professional Package Structure:** Follows enterprise Python best practices with proper package organisation
    - **Better Maintainability:** Each module has a single, well-defined responsibility
    - **Enhanced Extensibility:** Easy to add new features, output formats, or device types
    - **Improved Testing:** Isolated components can be unit tested independently
    - **New Entry Point:** Use `python -m switch_audit` as the standard launch method
    
    **For End Users:** Everything works the same! All CLI arguments, configuration options, and output formats are identical.
    
    **For Developers:** See the [Migration Guide](#migration-guide-v10-v20) for updated import paths and structure details.
    
    📖 Full details are in the `MIGRATION.md` guide included with the licensed package.

---

## ✨ What This Tool Does

- Audits access ports across multiple Cisco switches in parallel
- Normalises interface names (e.g., `GigabitEthernet1/0/1` → `Gi1/0/1`) for cross-command matching
- Enriches interfaces with:
  - PoE draw and state (`show power inline`)
  - LLDP/CDP neighbour presence (`show lldp neighbors detail`, `show cdp neighbors detail`)
- Classifies port mode & VLAN using `show interfaces status` (access / trunk / routed)
- Flags stale access ports using conservative rules
- Exports Excel with an at-a-glance SUMMARY and one sheet per device, with filters, frozen header, column auto-size, and conditional formatting
- Shows a progress bar whilst running concurrent device jobs

> **Design note:** The workbook intentionally uses filters only (no Excel tables), and places SUMMARY first.

---

## 🎯 The PRIME Philosophy in Action

Before diving into the code, understand how every design decision reflects our three core principles:

### **Principle 1: Line-by-Line Transparency**

Every function in this tool includes explicit documentation of *what it does* and *why it's structured this way*. You'll see comments explaining the engineering tradeoffs—why we parse with TextFSM *and* maintain a fallback parser, why we use conservative stale-detection logic, and why conditional formatting in Excel matters for operations teams.

### **Principle 2: Hardened for Production**

Access layer audits run on infrastructure that cannot afford downtime. You'll notice patterns like concurrent connection pooling, per-device failure isolation, graceful fallbacks when commands fail, and secure credential rotation. These aren't "nice to have"—they're mandatory for enterprise reliability.

### **Principle 3: Vendor-Neutral**

This tool is built on industry-standard Python libraries: **Netmiko** (multi-device SSH), **Paramiko** (jump host tunnelling), **Pandas & OpenPyXL** (Excel generation), and **TextFSM** (intelligent parsing). Your skills remain portable across vendors.

---

## 🧱 Project Layout

The tool has been restructured into a **professional modular package** (v2.0), separating concerns and following enterprise Python best practices:

```text
    .
    ├── switch_audit/           # Main package (modular design)
    │   ├── __init__.py
    │   ├── __main__.py        # Entry point for python -m switch_audit
    │   ├── cli.py             # Command-line interface and orchestration
    │   ├── device_auditor.py  # Device connection and data collection
    │   ├── excel_reporter.py  # Excel workbook generation
    │   ├── credentials.py     # Secure credential management
    │   ├── jump_manager.py    # SSH jump host (bastion) support
    │   ├── netmiko_utils.py   # Network device connection utilities
    │   ├── formatters.py      # Excel formatting and interface name normalisation
    │   ├── validators.py      # Input validation functions
    │   └── app_config.py      # Configuration access wrapper
    ├── assets/
    │   └── config_files/
    │       └── config_loader.py  # YAML configuration loader
    ├── config.yaml            # User-editable configuration
    ├── devices.txt            # Device list (one IP/hostname per line)
    ├── main.py                # Legacy entry point (deprecated)
    ├── run.bat                # Windows launcher script
    ├── requirements.txt       # Python dependencies
    ├── MIGRATION.md           # Migration guide for v2.0
    └── README.md
```

> **V2.0 Architecture:** The restructure separates the monolithic `main.py` (1,300+ lines) into focused modules with single responsibilities. This improves maintainability, testability, and extensibility.
>
> **Backward Compatibility:** The old `main.py` remains for reference. New users should use `python -m switch_audit`.

### Module Responsibilities (v2.0)

Each module in the `switch_audit/` package has a specific, well-defined role:

| Module | Purpose | Key Functions |
| :--- | :--- | :--- |
| **`__main__.py`** | Package entry point | Enable `python -m switch_audit` execution |
| **`cli.py`** | Command-line interface | Argument parsing, orchestration, progress tracking |
| **`device_auditor.py`** | Device connection & data collection | SSH connections, command execution, retry logic, data enrichment |
| **`excel_reporter.py`** | Excel report generation | Workbook creation, sheet formatting, conditional formatting |
| **`credentials.py`** | Credential management | Windows Credential Manager integration, interactive prompts |
| **`jump_manager.py`** | SSH bastion support | Persistent jump host connections, channel management |
| **`netmiko_utils.py`** | Network device utilities | Netmiko connection wrappers, timeout handling |
| **`formatters.py`** | Data formatting utilities | Interface name normalisation, CLI parsing, Excel formatting |
| **`validators.py`** | Input validation | File existence checks, argument validation |
| **`app_config.py`** | Configuration singleton | Global config access wrapper |

**Configuration Package:**

| Module | Purpose |
| :--- | :--- |
| **`assets/config_files/config_loader.py`** | YAML configuration loader with type-safe property accessors and validation |

---

## 📦 Requirements

- **Python:** 3.8+
- **Python packages:**
  - `netmiko`
  - `paramiko`
  - `pandas`
  - `openpyxl`
  - `pywin32` (Windows only; used for Windows Credential Manager integration)

Install with pip:
```bash
    pip install netmiko paramiko pandas openpyxl pywin32
```

### Optional but Recommended

- **TextFSM templates** (NTC templates) for robust parsing of `show interfaces` when `use_textfsm=True`.
  - If templates are available and the `NET_TEXTFSM` environment variable points to them, parsing accuracy improves.
  - If not available, the script still works and falls back where needed (e.g., it has its own fixed-width parser for `show interfaces status`).

---

## ⚙️ Configuration System

The tool uses a **modern YAML-based configuration system** with centralised management in v2.0.

### YAML Configuration File (config.yaml)

All configurable settings are centralised in `config.yaml` at the project root. The configuration is loaded via `assets/config_files/config_loader.py` and accessed throughout the application via the `app_config.py` singleton wrapper.

**Key Configuration Categories:**

**1. Network Settings:**
```yaml
    network:
    jump_host: "jump-gateway.example.com"  # Default bastion/jump host
    device_type: "cisco_ios"                # Netmiko device type
    ssh_port: 22                            # SSH port
    read_timeout: 30                        # Command read timeout
```

**2. Credential Settings:**
```yaml
    credentials:
    cred_target: "MyApp/ADM"  # Windows Credential Manager target
    enable_target: ""          # Optional enable secret target
```

**3. Performance & Concurrency:**
```yaml
    concurrency:
    default_workers: 10        # Max concurrent device sessions
    retry_attempts: 3          # Connection retry count
    retry_base_wait: 2         # Base wait time for exponential backoff
```

**4. Excel Output:**
```yaml
    output:
    default_filename: "audit.xlsx"  # Default output filename

    excel_formatting:
    min_column_width: 10
    max_column_width: 50
```

**5. Stale Port Detection:**
```yaml
    stale_detection:
    default_stale_days: 30  # Days threshold for stale ports
```

### Why YAML Configuration?

| Benefit | Explanation |
| :--- | :--- |
| **Human-Readable** | No Python knowledge required to modify settings |
| **Version Control Friendly** | Plain text format works seamlessly with Git |
| **Safer** | No code execution risk (pure data) |
| **Validated** | Config loader validates types and provides defaults |
| **Hierarchical** | Natural grouping of related settings |
| **Documented** | Inline comments explain each setting |

### Environment Variable Overrides

Specific settings can be overridden at runtime via environment variables (primarily for the jump host):

```powershell
    # Override jump host at runtime
    $env:JUMP_HOST = "temp-bastion.example.com"
```

> **Best Practice:** Use `config.yaml` for organisational defaults; use CLI arguments (`--direct`, `--workers`, etc.) for per-run overrides.

---

## 🚀 Quick Start: Using the Launcher (Recommended)

The repository includes a **professional Windows batch launcher** (`run.bat`) that provides the easiest way to run the tool with default settings.

### Why Use the Launcher?

- **Zero configuration required** - Just double-click or run from command line
- **Automatic validation** - Checks for Python environment and required files before execution
- **Helpful diagnostics** - Clear error messages if something is missing
- **Professional interface** - Clean output with status indicators and progress messages
- **Safe execution** - Validates environment before running the script
- **Updated for v2.0** - Uses the new modular package structure automatically

### Using run.bat

### Option 1: Double-click

Simply double-click `run.bat` in Windows Explorer to launch the tool with default behaviour.

### Option 2: Command Line (Default Behaviour)

```cmd
    run.bat
```

This runs the Access Switch Audit using `python -m switch_audit` with all default settings from `config.yaml`.

### What the Launcher Does

1. **Validates the environment:**
   - Checks that the `portable_env` virtual environment exists
   - Verifies Python executable is present
    - Confirms `switch_audit` package files are present
   - Validates `config.yaml` and `devices.txt` are present

2. **Provides clear feedback:**
   - Shows [OK] for successful checks
   - Shows [WARNING] for missing optional files with option to continue
   - Shows [ERROR] for critical missing components
   - Displays helpful troubleshooting tips on failure

3. **Runs the tool:**
   - Activates the virtual environment
   - Executes the main script
   - Captures and displays the exit code
   - Provides common troubleshooting tips if errors occur

### Example Output

```
    ================================================================================
                    ACCESS SWITCH AUDIT TOOL
    ================================================================================

    Starting validation checks...

    [OK] Python Environment: Found at portable_env\Scripts\python.exe
    [OK] Required support files found
    [OK] All validation checks passed

    ================================================================================

    Running Access Switch Audit...

    ================================================================================

    [Script output appears here]

    ================================================================================

    [SUCCESS] Script completed successfully

    ================================================================================
```

---

## 🚀 Advanced: Command Line with Arguments

For advanced users who need to **customise behaviour beyond the defaults**, you can still run the tool directly with Python and command-line arguments.

### When to Use Command Line Arguments

Use `python -m switch_audit` with arguments when you need to:

- Override default settings from `config.yaml`
- Specify a different devices file
- Change output filename
- Adjust worker thread count
- Enable debug mode
- Force direct connections (bypass jump host)

### Method 1: Using the Launcher with Arguments

You can pass arguments to `run.bat` and they will be forwarded to the Python script:

```cmd
    run.bat --devices my-switches.txt --output custom-audit.xlsx --workers 5
```

### Method 2: Direct Python Execution (New in v2.0)

Activate the virtual environment and run the package as a module:

```bash
    # Windows (recommended)
    portable_env\Scripts\activate
    python -m switch_audit --devices my-switches.txt --output audit-report.xlsx

    # Linux/macOS  
    source portable_env/bin/activate
    python -m switch_audit --devices my-switches.txt --output audit-report.xlsx

    # Backward compatibility (legacy mode)
    python main.py --devices my-switches.txt --output audit-report.xlsx
```

### Available Command-Line Arguments

| Argument | Description | Default |
| :--------- | :------------ | :-------- |
| `--devices`, `-d` | Path to devices file | `devices.txt` |
| `--output`, `-o` | Output Excel filename | `audit.xlsx` |
| `--workers`, `-w` | Number of concurrent threads | 10 |
| `--stale-days` | Days threshold for stale ports | 30 |
| `--direct` | Skip jump host, connect directly | False |
| `--debug` | Enable debug-level logging | False |

**Example: Custom audit with direct connections:**

```bash
    python -m switch_audit --devices critical-switches.txt --output critical-audit.xlsx --direct --debug
```

---

## 🏗️ Technical Architecture

The v2.0 restructure transformed the tool from a monolithic script into a **professional Python package** with clear separation of concerns:

| Module | Responsibility | Why It Matters |
| :--- | :--- | :--- |
| **cli.py** | Command-line interface and orchestration | Entry point handling, argument parsing, progress tracking |
| **device_auditor.py** | Device connection and data collection | Parallel SSH connections, command execution, retry logic |
| **excel_reporter.py** | Excel workbook generation and formatting | Professional reports with conditional formatting and filters |
| **credentials.py** | Secure credential retrieval from OS stores | Passwords never touch plaintext or config files |
| **jump_manager.py** | Persistent SSH tunnelling through bastion | Centralises network access control; supports air-gapped environments |
| **netmiko_utils.py** | Network device connection utilities | Connection wrapper with timeout and error handling |
| **formatters.py** | Interface name normalisation and Excel formatting | Cross-command data correlation and professional output |
| **validators.py** | Input validation functions | Pre-flight checks for files and arguments |
| **app_config.py** | Configuration access wrapper | Singleton pattern for config access across modules |
| **config_loader.py** | YAML parsing and validation | Type-safe settings with environment overrides |

### Key Design Patterns (v2.0)

**1. Package-Based Architecture:**

- Each module has single, well-defined responsibility
- Clear dependency hierarchy (cli → device_auditor → excel_reporter)
- Easy to test, extend, and maintain
- Follows Python packaging best practices

**2. Separation of Concerns:**

- **Presentation layer** (cli.py): User interaction and progress display
- **Business logic layer** (device_auditor.py): Data collection and processing
- **Data layer** (excel_reporter.py, formatters.py): Output generation
- **Infrastructure layer** (credentials.py, jump_manager.py, netmiko_utils.py): Supporting services

**3. Configuration Centralisation:**

- All config in `assets/config_files/config_loader.py`
- Accessed via singleton pattern in `app_config.py`
- Environment variables override YAML settings
- Type-safe property accessors

**4. Intelligent Fallback Parsing:**

- Primary: TextFSM templates (when available)
- Fallback: Custom fixed-width parsers in formatters.py
- Ensures reliability even without external dependencies

**5. Multi-Threaded Execution:**

- ThreadPoolExecutor with configurable worker count
- Thread-safe data accumulation with locks
- Per-device failure isolation
- Event-driven progress bar

**6. Graceful Error Handling:**

- Exponential backoff retry logic
- Per-device error capture (doesn't stop entire audit)
- Comprehensive logging for troubleshooting

---

## 🧬 End-to-End Code Path: From CLI Flag to Workbook Row

The architecture table above explains the modules. This section explains the runtime hand-off between them, which is the more useful lesson if you want to build your own production-grade audit tool.

### 1. `cli.py` Owns Orchestration, Not Parsing

The CLI layer handles process-level concerns:

- parse flags such as `--tui`, `--direct`, `--workers`, `--stale-days`, and `--output`
- validate the target workbook filename
- determine whether to use the configured jump host
- acquire credentials and validate the device list
- build an event queue for progress reporting
- submit one `audit_device(...)` job per target via `ThreadPoolExecutor`

The key pattern is the event-driven wrapper around each worker. `_worker_wrapper(...)` emits `start` and `done` events into a queue so progress display is separated from the actual audit logic.

Why this matters:

- progress reporting stays accurate without contaminating collection code
- CLI argument handling does not become the place where parsing decisions live
- concurrency can be tuned without rewriting the device audit engine

### 2. Transport Complexity Is Isolated in the Connection Layer

The audit engine does not talk to Paramiko or Netmiko directly in scattered places. That complexity is pushed into `jump_manager.py` and `netmiko_utils.py`.

`JumpManager` keeps a persistent bastion SSH session and opens `direct-tcpip` channels for each downstream device. `connect_to_device(...)` then hands that channel to Netmiko and strips kwargs that some Netmiko variants do not accept.

Why this matters:

- connection quirks are isolated from business logic
- the device auditor can think in terms of "give me a connection" instead of "how do I tunnel this socket"
- direct and jump-host modes share the same audit path once the connection is established

This is a strong production pattern: transport plumbing should be replaceable without rewriting the logic that interprets device state.

### 3. `audit_device(...)` Is the Real Collection Engine

The core runtime pattern is:

1. attempt connection, with exponential backoff retries
2. enter the jump context when required
3. once connected, hand off to `_audit_connected_device(...)`
4. always disconnect cleanly in `finally`

Inside `_audit_connected_device(...)`, the command order is deliberate:

- discover hostname
- enter enable mode if required
- collect `show version` for IOS and hardware context
- collect `show interfaces` for detailed counters and activity data
- collect `show interfaces status` for mode, VLAN, and status correction
- collect `show power inline` for PoE enrichment
- collect LLDP and CDP neighbour data
- normalise and merge everything into one per-interface record set
- calculate stale flags and summary totals

Why this matters:

- later enrichment depends on earlier normalisation work
- command responsibilities stay distinct instead of being treated as interchangeable text blobs
- every summary row is built from the same deterministic record pipeline

### 4. Parsing Is Layered Because Real CLI Output Is Messy

This tool demonstrates a production reality that many tutorials skip: no single parser strategy is reliable enough on its own.

Examples from the code:

- `_parse_hardware_from_version(...)` tries TextFSM first, then falls back to regex patterns
- `parse_show_interfaces_status(...)` uses a custom fixed-width parser that does not depend on external templates
- `parse_show_power_inline(...)` stores PoE data under short, long, and raw interface aliases to improve match rates
- neighbour collection normalises interface names before attempting correlation

Why this matters:

- the tool degrades gracefully when TextFSM templates are absent or incomplete
- different Cisco output variations do not immediately break the audit
- cross-command joins work because alias handling is treated as a first-class problem

That is one of the strongest learning points in the whole page: resilience often comes from combining multiple parsers, not from betting everything on one perfect parser.

### 5. Reporting Is Deterministic and Failure-Tolerant

`ExcelReporter.save_to_excel(...)` sorts results, writes the `SUMMARY` sheet first, appends a `TOTAL` row, and then creates one worksheet per device.

Crucially, even failed devices are still represented. When there is no detailed dataset, the reporter creates a small placeholder sheet containing the error text rather than silently dropping that device from the workbook.

Formatting is then centralised in `formatters.py`:

- safe sheet naming and uniqueness handling
- filters and frozen headers
- conditional formatting for status, PoE, stale ports, and error counters
- interface alias helpers reused by the audit pipeline

Why this matters:

- every requested device remains visible in the final artefact
- worksheet behaviour stays consistent regardless of data volume
- report logic and data-collection logic remain separate concerns

### 6. Failure Model and Safe Extension Points

The runtime failure model is intentionally conservative:

- connection issues are retried with exponential backoff
- per-device failures do not abort the full run
- exhausted retries return an error summary row instead of an untracked omission
- jump connections and device sessions are always cleaned up

The safe places to extend behaviour are also clear:

- adjust parsing and stale logic in `device_auditor.py`
- adjust transport behaviour in `jump_manager.py` or `netmiko_utils.py`
- adjust workbook structure and formatting in `excel_reporter.py` and `formatters.py`
- adjust operator defaults in configuration loading, not in collection code

What you should avoid is editing `cli.py` when the real change belongs in parsing or reporting. The CLI should stay an orchestration layer, not a dumping ground for business logic.

---

## 🔄 Migration Guide (v1.0 → v2.0)

If you're upgrading from the older monolithic version, see the **MIGRATION.md** file in the repository for detailed migration instructions.

### What Changed in v2.0?

**1. Modular Package Design**
    - Code separated into focused modules (cli.py, device_auditor.py, excel_reporter.py, etc.)
    - Core components moved into the `switch_audit/` package
    - Config loader centralised under `assets/config_files/`

**2. New Entry Point**
    - **Old**: `python main.py --devices devices.txt`
    - **New**: `python -m switch_audit --devices devices.txt` (recommended)
    - **Backward Compatible**: `python main.py --devices devices.txt`

**3. Updated Imports (for developers)**
```python
    # Configuration loader:
    from assets.config_files.config_loader import Config

    # Package imports:
    from switch_audit.credentials import get_secret_with_fallback
    from switch_audit.app_config import config  # Singleton wrapper
```

### Benefits of v2.0 Restructure

| Benefit | Description |
| :--- | :--- |
| **Better Organisation** | Each module has a single, clear responsibility |
| **Easier Testing** | Isolated components can be unit tested |
| **Professional Architecture** | Follows enterprise Python package standards |
| **Improved Maintainability** | Changes to one module don't cascade |
| **Enhanced Extensibility** | Easy to add new features or output formats |
| **Onboarding** | New contributors can understand structure quickly |

### No User Impact

For end users, the tool works identically. All CLI arguments, configuration options, and output formats remain the same. The `run.bat` launcher has been automatically updated to use the new structure.

---

## 📊 Intelligent Parsing: The Heart of the Tool

> **Note:** In v2.0, parsing logic has been modularised into `switch_audit/formatters.py` for better maintainability and reusability.

### Why Intelligent Parsing Matters

**The Problem:** Cisco CLI output varies by device model, IOS version, and platform. `show interfaces status` might be formatted differently on a Catalyst 2960 vs a 9300. TextFSM templates might not exist for your specific platform.

**The Solution:** Multi-tier parsing strategy with intelligent fallbacks.

### Parsing Strategy: TextFSM + Custom Fallback

```python
    def get_interfaces_via_show_interfaces(conn) -> List[Dict[str, Any]]:
        """
        Use TextFSM to parse 'show interfaces' for all ports.
        Falls back gracefully if templates unavailable.
        """
        try:
            output = conn.send_command("show interfaces", use_textfsm=True)
            if isinstance(output, list):
                return output
            return []
        except Exception:
            return []  # Graceful degradation
```

**Why This Approach:**

- TextFSM provides structured parsing when templates exist
- Returns empty list (not exception) if parsing fails
- Main logic continues with custom parsers

### Custom Fixed-Width Parser: `parse_show_interfaces_status()`

This is the **authoritative source** for port mode and VLAN classification.

```python
    def parse_show_interfaces_status(output: str) -> List[Dict[str, str]]:
        """
        Robust fixed-width parser for 'show interfaces status'.
        Handles:
        - Multiple header formats
        - Variable column widths
        - Missing/malformed data
        """
```

**Step 1: Identify Header Row**
```python
    def is_header(ln: str) -> bool:
        return ("Port" in ln and "Status" in ln and "Vlan" in ln and "Speed" in ln)
```

**Why:** Header detection must be flexible. Different IOS versions capitalize differently.

**Step 2: Extract Column Positions**
```python
    def _find_columns(header_line: str) -> Dict[str, slice]:
        """
        Calculate exact character positions for each column.
        Returns slice objects for substring extraction.
        """
        tokens = ["Port", "Name", "Status", "Vlan", "Duplex", "Speed", "Type"]
        positions = {}
        for i, tok in enumerate(tokens):
            start = header_line.find(tok)
            end = header_line.find(tokens[i+1]) if i+1 < len(tokens) else len(header_line)
            positions[tok.lower()] = slice(start, end)
        return positions
```

**Why This Matters:**

- Fixed-width parsing is more reliable than regex for tabular CLI output
- Dynamically calculated positions adapt to slight formatting variations
- Slice objects provide clean substring extraction

**Step 3: Parse Data Rows**
```python
    for line in lines:
        if line.startswith(("--", "Port")) or not line.strip():
            continue  # Skip separators and empty lines

        record = {}
        for key, col_slice in slices.items():
            record[key] = line[col_slice].strip()
        
        # Normalise status values
        status_raw = record.get('status', '').lower()
        if 'connect' in status_raw:
            record['status'] = 'connected'
        elif 'notconnect' in status_raw:
            record['status'] = 'notconnect'
        elif 'disabled' in status_raw:
            record['status'] = 'disabled'
        elif 'err' in status_raw:
            record['status'] = 'err-disabled'
```

**Why Status Normalisation:**

- Different IOS versions use slight variations ("connected" vs "connect")
- Normalised values enable reliable conditional formatting in Excel
- Consistent categorisation across device types

### Port Mode Classification

```python
    # Determine mode from VLAN column
    vlan_value = record.get('vlan', '').lower()

    if vlan_value in ('trunk', 'rspan'):
        mode = 'trunk'
    elif vlan_value == 'routed':
        mode = 'routed'
    else:
        mode = 'access'  # Default assumption
```

**Why This Logic:**

- VLAN column is the most reliable indicator of port mode
- Trunk ports show "trunk" or "rspan" in VLAN field
- Routed ports show "routed"
- Everything else is access (may show VLAN number)

---

## 🔌 PoE Enrichment: Multi-Source Data Fusion

### The PoE Challenge

**Problem:** PoE data (`show power inline`) uses different interface naming than `show interfaces status`. Example:

- Status command: `Gi1/0/1`
- PoE command: `GigabitEthernet1/0/1`

**Solution:** Interface name aliasing and multi-key lookups.

### Interface Name Normalisation

```python
    def normalize_ifname(ifname: str) -> Tuple[str, str]:
        """
        Normalise interface names to canonical short and long forms.
        Returns: (short_form, long_form)
        Example: "Gi1/0/1" → ("Gi1/0/1", "GigabitEthernet1/0/1")
        """
        # Extract prefix and port number
        m = re.match(r"([A-Za-z]+)([0-9/\.]+.*)", ifname)
        if not m:
            return (ifname, ifname)
        
        prefix_raw = m.group(1)
        rest = m.group(2)
        
        # Map to short form
        short_prefix = _IF_MAP.get(prefix_raw.lower(), prefix_raw)
        
        # Generate long form
        long_prefix = {
            "Gi": "GigabitEthernet",
            "Fa": "FastEthernet",
            "Te": "TenGigabitEthernet",
            "Eth": "Ethernet",
        }.get(short_prefix, prefix_raw)
        
        return (f"{short_prefix}{rest}", f"{long_prefix}{rest}")
```

**Why This Matters:**

- Enables reliable cross-command matching
- Handles all common Cisco interface types
- Works across different IOS versions and platforms

### Alias-Based Lookup

```python
    def all_aliases(ifname: str) -> List[str]:
        """
        Return all possible alias strings for an interface.
        Used for PoE data matching.
        """
        short, long = normalize_ifname(ifname)
        return [short, long, ifname]  # Try all variations

    # During PoE enrichment:
    for alias in all_aliases(port_name):
        if alias in poe_map:
            poe_data = poe_map[alias]
            break
```

**Why Multiple Aliases:**

- Different commands use different naming conventions
- Maximizes successful PoE data correlation
- Prevents data loss due to naming mismatches

---

## 🚨 Stale Port Detection: Conservative Risk Assessment

### The Business Problem

**Scenario:** You have 1,000 switch ports. How do you identify which ones are truly unused vs. temporarily disconnected vs. connected to equipment that's powered off?

**False Positives Are Expensive:**

- Marking an active port as "stale" disrupts operations
- Users lose network access
- Help desk tickets spike

**False Negatives Waste Resources:**

- Unused ports consume switch capacity
- Security risk (unauthorized devices can plug in)

### Conservative Detection Strategy

```python
    def _categorize_port(row: Dict[str, Any], stale_days: int) -> str:
        """
        Classify port as: active, stale, or available.
        Uses conservative logic to minimise false positives.
        """
```

**Rule 1: Only Classify Access Ports**
```python
    mode = row.get('Mode', '')
    if mode != 'access':
        return 'active'  # Trunk and routed ports are infrastructure
```

**Why:** Trunk and routed ports connect switches to each other. They should never be flagged as stale.

**Rule 2: Connected Ports — Check Activity**
```python
    status = row.get('Status', '')
    if status == 'connected':
        last_input_secs = row.get('Last Input Seconds')
        if last_input_secs and last_input_secs >= (stale_days * 86400):
            return 'stale'
        return 'active'
```

**Why:**

- Port is physically connected
- But hasn't passed traffic in N days
- Likely a powered-off device or misconfigured endpoint

**Rule 3: Disconnected Ports — Check for Indicators**
```python
    if status in ('notconnect', 'disabled', 'err-disabled'):
        # Conservative: require BOTH conditions to flag as stale
        has_poe = row.get('PoE Power (W)')
        has_neighbor = row.get('LLDP/CDP Neighbor')

        poe_w = None
        if has_poe:
            try:
                poe_w = float(str(has_poe).split()[0])
            except:
                pass
        
        # Stale only if: no PoE draw AND no neighbour
        if (poe_w is None or poe_w == 0.0) and not has_neighbor:
            return 'stale'
        
        return 'available'  # May be in use (PoE or neighbour present)
```

**Why This Conservative Approach:**

| Indicator | Interpretation |
| :--- | :--- |
| **PoE draw > 0** | Device is powered (IP phone, camera, AP) |
| **LLDP/CDP neighbour** | Device is network-aware (switch, phone, AP) |
| **Both absent** | Likely unused cable or dead device |

**Example Scenarios:**

| Status | PoE | Neighbour | Last Input | Classification | Reasoning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| connected | 7.0W | Yes | 10 days | **active** | IP phone actively drawing power |
| connected | 0W | No | 45 days | **stale** | Connected but no traffic for 45+ days |
| notconnect | 0W | No | N/A | **stale** | Disconnected, no indicators of use |
| notconnect | 6.5W | No | N/A | **available** | PoE device present (might be powered off) |
| notconnect | 0W | Yes | N/A | **available** | Neighbour detected (might be rebooting) |

### Time Parsing: Handling Cisco Duration Formats

```python
    def _parse_last_input_seconds(s: str) -> float | None:
        """
        Parse Cisco 'Last input' timer into seconds.
        Handles: "00:01:23", "1d2h30m", "never"
        """
        s = (s or "").strip().lower()
        if not s or s == "never":
            return None
        
        # Format 1: hh:mm:ss
        if re.match(r"^\d{1,2}:\d{2}:\d{2}$", s):
            hh, mm, ss = s.split(":")
            return int(hh) * 3600 + int(mm) * 60 + int(ss)
        
        # Format 2: Compact duration (1y2w3d4h5m6s)
        m = _TIME_RE.fullmatch(s.replace(" ", ""))
        if m:
            y = int(m.group("y") or 0)
            w = int(m.group("w") or 0)
            d = int(m.group("d") or 0)
            h = int(m.group("h").rstrip("h") or 0)
            m_val = int(m.group("m").rstrip("m") or 0)
            s_val = int(m.group("s").rstrip("s") or 0)
            
            days = y * 365 + w * 7 + d
            return days * 86400 + h * 3600 + m_val * 60 + s_val
```

**Why Multiple Format Support:**

- Different IOS versions use different time formats
- Ensures accurate stale detection across all platforms

---

## 🔐 Credentials & Security

The script retrieves device credentials using `switch_audit/credentials.py`:

- **Primary:** Windows Credential Manager (target name from `config.yaml`: default `MyApp/ADM`)
- **Fallback:** Interactive prompt for username and password (secure, not echoed)
- **Enable secret:** Retrieved by `get_enable_secret()` if `USE_ENABLE` environment variable is set, otherwise not required

> **Note:** If you are running on Linux/macOS, ensure `credentials.py` prompts for credentials or implements your preferred secure store. On Windows, `pywin32` enables Credential Manager access.
>
> **Important:** Never hard-code credentials in the repository. Use the secure store or environment prompts.
>
> **Configuration:** Credential Manager targets are set in `config.yaml` under the `credentials` section:
>
```yaml
    credentials:
    cred_target: "MyApp/ADM"  # Primary credential target
    enable_target: ""          # Optional enable secret target
```

---

## 🛰️ Jump Host (Bastion) Behaviour

- `main.py` reads `jump_host` from the `network` section of `config.yaml`
- **Default:** the script uses the jump host if `--direct` is not supplied
- `--direct` will skip the jump host entirely and attempt direct SSH connections

Example configuration in `config.yaml`:
```yaml
    network:
    jump_host: "jump-gateway.example.com"  # or "" to disable by default
```

The `JumpManager` (now in `switch_audit/jump_manager.py`) maintains a persistent SSH session to the bastion and proxies device connections through it.

**How JumpManager Works:**

```python
    class JumpManager:
        def __init__(self, jump_host: str, username: str, password: str):
            self.jump_host = jump_host
            self.username = username
            self.password = password
            self.client = None  # Paramiko SSH client
        
        def connect(self) -> None:
            """Establish persistent SSH connection to bastion."""
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.jump_host,
                username=self.username,
                password=self.password,
                timeout=10
            )
        
        def open_channel(self, target_ip: str, target_port: int):
            """Open direct-tcpip channel through bastion."""
            return self.client.get_transport().open_channel(
                'direct-tcpip',
                (target_ip, target_port),
                ('localhost', 0)
            )
```

**Why direct-tcpip Channel:**

- No port forwarding needed on bastion
- All traffic stays within authenticated SSH session
- Cleaner than local port forwarding
- Works with restrictive bastion configurations

---

## 🧾 Direct Execution Inputs and Examples

The launcher and advanced operator paths above are the best way to start using the tool. This shorter section exists for engineers reading the code walkthroughs who want the minimum artefacts and commands required by the direct module path.

### Device List File

Provide a plain-text file with one device per line. Lines that are blank or start with `#` are ignored.

```text
# devices.txt
192.0.2.11
192.0.2.12  # inline comments are not parsed; this whole token must be a host/IP only
core-switch-01
access-sw-22
```

> **Note:** Hostnames must be resolvable from the machine (or via the jump host, depending on your SSH setup).

---

### Minimal Direct Run

1. Install dependencies (see Requirements).
2. Create `devices.txt` with your targets (see Device list file).
3. (Optional) Configure `config.yaml` with your `jump_host` and other settings.
4. Run the audit:

```bash
# Using jump host from config.yaml
python -m switch_audit --devices devices.txt --output access_port_audit.xlsx

# Direct connections (no bastion), 5 workers, different stale threshold
python -m switch_audit --direct -w 5 --stale-days 60 -d devices.txt -o results.xlsx

# Verbose debugging
python -m switch_audit --debug -d devices.txt
```

---

### Direct CLI Reference

`switch_audit` exposes the following command-line options:

```text
--devices, -d    (required)  Path to the devices file (one IP/hostname per line; '#' comments allowed)
--output,  -o    (optional)  Output Excel file name. Default: audit.xlsx
--workers, -w    (optional)  Max concurrent device sessions (threads). Default: 10
--stale-days     (optional)  Days threshold for stale access ports. 0 disables stale flagging. Default: 30
--direct         (optional)  Connect directly (do not use jump host)
--debug          (optional)  Enable verbose logging/prints
```

### Required vs Optional

- **Required:** `--devices`
- **Optional:** everything else

**Usage Examples:**

```bash
# Standard audit with jump host
python -m switch_audit --devices devices.txt --output report.xlsx

# Direct connections, custom workers
python -m switch_audit --devices devices.txt --direct --workers 20

# Debug mode with custom stale threshold
python -m switch_audit --devices devices.txt --stale-days 60 --debug

# Using the launcher
run.bat --devices devices.txt --output audit.xlsx
```

---

## PortAuditor: The Threaded Collection Engine

### Why Parallel Port Auditing is Essential

**The Problem:** Auditing 50 switches serially with 5 commands per device = 250 SSH round-trips. At 2 seconds per connection, that's 8+ minutes of waiting.

**The Solution:** Thread pool with 10 concurrent workers = 10 simultaneous SSH sessions. Same 50 switches audited in 1-2 minutes.

### Thread-Safe Architecture

```python
    # Thread-safe accumulators (protected by locks)
    self.device_records = []       # Parsed results: one row per device
    self.interface_details = []    # Detailed per-interface data
    self.failed_devices = {}       # {ip: error_message}
    self.progress_lock = threading.Lock()  # Protects shared state
```

**Why Thread Locks Matter:**

- Without locks, multiple threads writing to the same list causes data corruption
- The lock ensures atomic append operations
- Minimal lock contention because we hold locks for microseconds, not seconds

### Command Collection Strategy

For each device, the tool collects five commands in sequence:

| Command | Purpose | Fallback |
| :--- | :--- | :--- |
| `show version` | Extract hostname, OS version, uptime | Use management IP if hostname parse fails |
| `show interfaces` | Parse interface types, error counters, activity | Use TextFSM if available; use internal parser otherwise |
| `show interfaces status` | Extract port mode, VLAN, status using fixed-width parsing | Built-in fallback parser (no external dependency) |
| `show power inline` | Collect PoE admin/oper state and power draw | Empty dict if device is non-PoE or command fails |
| `show cdp/lldp neighbors detail` | Detect peer devices on each port | Boolean flag (true if neighbour present) |

**Why This Command Set?**

- Comprehensive but minimal: each command provides data no other command offers
- Covers the three dimensions of port health: *configuration* (mode/VLAN), *activity* (errors, last input), *attachment* (PoE, neighbours)

### The Intelligence Layer: Port Classification

```python
    def classify_port(interface_record):
        """
        Assign a port to one of three categories:
        - 'access': Single VLAN, typically hosts
        - 'trunk': Multiple VLANs, typically uplinks
        - 'routed': No VLAN (layer 3), typically inter-device links
        """
```

**Classification Logic:**

From `show interfaces status`, inspect the VLAN column:

- If `trunk` or `rspan` → **Trunk**
- If `routed` → **Routed**
- Otherwise → **Access**

**Why This Matters:**

- Different port types require different stale-detection rules
- Access ports should be connected to hosts; trunk ports connect infrastructure
- This classification enables intelligent filtering and reporting

---

## 🛑 Stale Logic — How Ports Are Flagged

A conservative approach is used only for ports in `access` mode and when `--stale-days > 0`:

- **If Status = `connected`** → mark stale = True only if `Last input ≥ <stale-days>`
- **If Status ≠ `connected`** → mark stale = True when both conditions hold:
  1. No PoE draw (PoE power is blank/`-`/0.0), and
  2. No LLDP/CDP neighbour present on the port

This tends to avoid false positives on trunk/routed ports and on access ports actively in use.

> **Note:** You can disable stale flagging entirely by setting `--stale-days 0`.

---

## 🧪 What the Script Collects

For each device the script attempts to gather:

- **Hostname** (from `show running-config | include ^hostname` or CLI prompt fallback)
- **Interfaces** via TextFSM (`show interfaces`) when available
- **Port mode & VLAN** via a robust, fixed-width parser of `show interfaces status`
- **PoE details:** admin/oper state, power draw (W), class, device (`show power inline`)
- **Neighbour presence:** LLDP/CDP seen on the port (boolean)
- **Error counters:** input, output, CRC (from `show interfaces` parsed data)
- **Activity indicator:** "Last input" time (seconds parsed when present)

---

## 📤 Excel Output Structure

The workbook contains:

### 1) `SUMMARY` Sheet (First)

- One row per device, with a final TOTAL row (sums numeric columns)
- Columns include:
  - `Device`, `Mgmt IP`, `Total Ports (phy)`
  - `Access Ports`, `Trunk Ports`, `Routed Ports`
  - `Connected`, `Not Connected`, `Admin Down`, `Err-Disabled`
  - `% Access of Total`, `% Trunk of Total`, `% Routed of Total`, `% Connected of Total`

### 2) One Sheet Per Device

Columns typically include (when available):

- `Device`, `Mgmt IP`, `Interface` (long form), `Description`
- `Status` (normalised: connected / notconnect / administratively down / err-disabled)
- `AdminDown`, `Connected`, `ErrDisabled` (booleans for quick filters)
- `Mode` (access/trunk/routed), `VLAN`
- `Duplex`, `Speed`, `Type`
- `Input Errors`, `Output Errors`, `CRC Errors`
- `Last Input` (raw text)
- `PoE Power (W)`, `PoE Oper`, `PoE Admin`
- `LLDP/CDP Neighbour` (boolean)
- `Stale (≥<N> d)` (boolean)

### Formatting

- **Frozen header** (`A2`) and AutoFilter across all columns
- **Auto-sized columns** with sensible min/max widths
- **Conditional formatting:**
  - `Status = connected` → green
  - `Status = notconnect` / `err-disabled` → red
  - `Status = administratively down` → grey
  - Any `*Errors` > 0 → red
  - `PoE Power (W)` > 0 → green
  - `Stale (≥N d)` = TRUE → red

### Worked Example: From One Device to Report Rows

Use documentation-only addressing here as a validation pattern:

```text
devices.txt
192.0.2.11
```

```bash
python -m switch_audit --devices devices.txt --output access_port_audit.xlsx
```

**Example SUMMARY row:**

| Device | Mgmt IP | Total Ports (phy) | Access Ports | Trunk Ports | Connected | Not Connected | Admin Down |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `BRN1-ACC-01` | `192.0.2.11` | `28` | `24` | `4` | `18` | `6` | `4` |

**Example per-interface row (healthy access port):**

| Interface | Description | Status | Mode | VLAN | PoE Power (W) | LLDP/CDP Neighbour | Stale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GigabitEthernet1/0/10` | `Finance Desk` | `connected` | `access` | `20` | `6.3` | `False` | `False` |

**Example per-interface row (stale candidate):**

| Interface | Description | Status | Mode | VLAN | PoE Power (W) | LLDP/CDP Neighbour | Stale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GigabitEthernet1/0/24` | `` | `notconnect` | `access` | `999` | `` | `False` | `True` |

**Why the second row is flagged stale:**

- The port is an **access** port
- Status is **notconnect**
- There is **no PoE draw**
- There is **no LLDP/CDP neighbour**

That is the exact conservative logic described in the stale-detection section above.

---

## ⚙️ Performance & Concurrency

- Uses a `ThreadPoolExecutor` with `--workers` threads (default 10)
- An event-driven progress bar updates as jobs start/finish
- Each device is independent; a failure on one does not stop others

The script prints an event-driven progress bar like:

```
    Progress: [██████████░░░░░░░░░░░░] 12/30 started: 15/30
```

On completion, the Excel workbook is written to the filename you specify (default `audit.xlsx`).

---

## Logging, Debug, and Errors

- Add `--debug` to surface additional prints (e.g., enable mode attempts, jump host info, file counts)
- Per-device errors are captured into the device's summary row (and a minimal sheet may be created with the error text so the workbook always reflects all devices)

**Common runtime issues & tips:**

- **Authentication failures** → check Credential Manager entry or typed credentials
- **SSH connectivity** → verify reachability from the workstation or via the jump host
- **TextFSM templates missing** → parsing still proceeds, but some fields may be blank
- **Channel/line rate limits on older devices** → consider lowering `--workers`

---

## 🔧 Extending and Customising

- **Credentials:** Adapt `switch_audit/credentials.py` to your environment (Linux keyring, Azure Key Vault, etc.)
- **Jump host:** Tune `switch_audit/jump_manager.py` (keep-alive, ciphers, auth methods) as needed
- **Connection behaviour:** Modify `switch_audit/netmiko_utils.py` for device types, timeouts, or SSH options
- **Configuration:** Edit `config.yaml` to set organisational defaults:
  - `network.jump_host`: Default bastion server
  - `concurrency.default_workers`: Concurrent device sessions
  - `stale_detection.default_stale_days`: Stale port threshold
  - `credentials.cred_target`: Credential Manager target name
  - `output.default_filename`: Default Excel output filename
- **Output columns:** Adjust record construction in `switch_audit/device_auditor.py` (search for data collection logic)
- **Conditional formatting:** Tweak formatting in `switch_audit/excel_reporter.py` or `switch_audit/formatters.py`
- **Parsers:** Modify parsing logic in `switch_audit/formatters.py` for custom CLI output handling

**Example config.yaml for Enterprise:**

```yaml
    network:
    jump_host: "bastion.corp.example.com"
    read_timeout: 45  # Slower WAN links
    
    credentials:
    cred_target: "NetworkAudit/Production"
    
    concurrency:
    default_workers: 20  # Fast discovery
    retry_attempts: 5    # More retries for flaky network
    
    stale_detection:
    default_stale_days: 90  # Longer threshold
    
    output:
    default_filename: "port_audit_report.xlsx"
    
    excel_formatting:
    min_column_width: 12
    max_column_width: 60
```

---

## 🔒 Security Considerations

- Prefer secure stores over plaintext
- Limit who can run the tool and who can read the generated Excel
- When using a jump host, ensure strong authentication and proper network segmentation

---

## 🧩 Compatibility

- **Target devices:** Cisco IOS/IOS-XE access and distribution switches reachable via SSH
- The tool relies on Netmiko; specify the right device type(s) inside `switch_audit/netmiko_utils.py`
- TextFSM/NTC templates significantly improve interface parsing fidelity but are not strictly required

### Tested Devices

This tool has been tested and verified on the following Cisco IOS and IOS-XE platforms:

- **Catalyst 9200 Series**
- **Catalyst 3650 Series**
- **Catalyst 3650C**
- **Catalyst 3650CG**
- **Catalyst 3650CX**
- **Catalyst 2960X Series**
- **Catalyst 2960 Series**

> **Note:** The tool should work with any Cisco IOS/IOS-XE device that supports the required show commands (interfaces, status, power inline, CDP/LLDP). The devices listed above have been explicitly tested and validated.

---

## ✅ Examples

```bash
    # Basic, with jump host (new modular entry point)
    python -m switch_audit -d devices.txt -o audit.xlsx

    # Direct (no bastion), 20 workers, stale disabled
    python -m switch_audit --direct -w 20 --stale-days 0 -d devices.txt -o audit.xlsx

    # Conservative concurrency, higher stale threshold, verbose
    python -m switch_audit -w 4 --stale-days 90 --debug -d devices.txt -o siteA.xlsx

    # Backward compatibility (legacy mode)
    python main.py --devices devices.txt --output audit.xlsx
```

---

## 🧠 FAQs

**Q: Do I need NTC TextFSM templates?**  
A: They are recommended for better `show interfaces` parsing. Without them, the script still works and uses its internal parser for `show interfaces status` and best-effort logic elsewhere.

**Q: Where do credentials come from?**  
A: On Windows, from Credential Manager (default target `MyApp/ADM`). Otherwise, you are prompted interactively or you can adapt `switch_audit/credentials.py` to your secret store.

**Q: How is `Mode` determined?**  
A: From `show interfaces status`: if VLAN column is `trunk`/`rspan` → `trunk`; if `routed` → `routed`; otherwise `access`.

**Q: How is a port considered stale?**  
A: Only for access ports and when `--stale-days > 0`. Connected ports are flagged stale only if `Last input ≥ N days`. Disconnected ports require both no PoE draw and no LLDP/CDP neighbour to be flagged stale.

**Q: What changed in v2.0?**  
A: The monolithic `main.py` was restructured into a professional Python package (`switch_audit/`) with modular components. The functionality is identical, but the code is now organised following enterprise best practices. See MIGRATION.md for details.

---

## 🎓 Learning Outcomes

After studying this code, you should understand:

✅ **YAML Configuration Management** — How to separate configuration from code using YAML with Python  
✅ **Python Package Design** — Structuring modular packages with clear entry points and separation of concerns  
✅ **Singleton Pattern** — Using configuration singletons for application-wide settings access  
✅ **Fixed-Width Parsing** — Reliable CLI output parsing without external dependencies  
✅ **Multi-Source Data Fusion** — Correlating data across different commands using interface name aliasing  
✅ **Conservative Risk Assessment** — Stale port detection logic that minimises false positives  
✅ **Thread-Safe Concurrency** — Parallel device audits with proper lock management  
✅ **Intelligent Fallback Strategy** — TextFSM + custom parsers for maximum compatibility  
✅ **SSH Tunnelling** — Jump host integration with Paramiko direct-tcpip channels  
✅ **Excel Automation** — Professional workbook generation with conditional formatting  
✅ **Exponential Backoff** — Retry logic for transient network failures  
✅ **Credential Management** — Secure OS-level credential storage integration  
✅ **Modular Architecture** — Separating CLI, business logic, and presentation layers  

### Key Code Patterns Demonstrated

### Pattern 1: Modular Package Structure

```python
    # Entry point (__main__.py)
    from .cli import main
    if __name__ == "__main__":
        main()

    # CLI layer delegates to business logic
    from .device_auditor import audit_device
    results = audit_device(ip, username, password, ...)

    # Business logic delegates to reporting
    from .excel_reporter import ExcelReporter
    reporter = ExcelReporter()
    reporter.generate(results)
```

### Pattern 2: Configuration Singleton

```python
    # app_config.py - Single source of truth
    from assets.config_files.config_loader import Config
    config = Config()

    # Used throughout application
    from .app_config import config
    workers = config.default_workers
```

### Pattern 3: Graceful Degradation

```python
    try:
        data = parse_with_textfsm(output)  # Preferred method
    except:
        data = parse_with_custom_logic(output)  # Fallback
```

### Pattern 4: Multi-Key Lookup

```python
    for alias in all_aliases(interface_name):
        if alias in poe_map:
            poe_data = poe_map[alias]
            break
```

### Pattern 5: Thread-Safe Accumulation

```python
    with lock:
        results.append(new_data)  # Atomic operation
```

### Pattern 6: Conservative Classification

```python
    if condition_A and condition_B:  # Both must be true
        mark_as_risky()
    else:
        mark_as_safe()  # Default to safe
```

### Pattern 7: Type-Safe Configuration

```python
    @property
    def default_workers(self) -> int:
        return self._get_nested("concurrency", "default_workers", default=10)
```

---

## 🚀 Distribution & Execution

Consistent with the **Nautomation Prime** delivery model, this tool is available in multiple formats:

- **Zero-Install Portable Bundle:** A self-contained package including the Python interpreter and all libraries (Netmiko, Pandas, OpenPyXL) for use on restricted Windows jump boxes.

- **Scheduled Docker Appliance:** A pre-built container designed for autonomous execution and periodic port auditing.

- **Licensed source:** Customise parsing logic, add vendor-specific commands, or integrate with your CMDB — the full source is included when you purchase the tool.

---

## Related Resources

**Get Started Now:**

- [📖 Script Library](../../scripts/index.md) — Find the Access Switch Audit tool and other automation scripts
- [💬 Request this tool](../../contact.md) — Buy it as-is or discuss customisation for your estate

**Learn More:**

- [🛠️ Nornir Fundamentals](../tutorials/intermediate/nornir-fundamentals.md) — Understanding parallel automation patterns like those in this tool
- [🚀 PRIME Framework](../../prime-framework/index.md) — Understand the methodology behind this tool

**Explore Similar Topics:**

- [CDP Network Audit Deep Dive](./cdp-audit.md) — Another production tool focusing on network topology discovery

---

## Licence

Premium tool — supplied under a commercial licence on purchase (buy as-is or customised to your environment). Not open-source; redistribution is not permitted. See [Licensing](../../legal/licensing.md) for details.

## 👤 Author

Christopher Davies

---

> **Mission:** To empower network engineers through the **[PRIME Framework](../../prime-framework/index.md)**—delivering automation with measurable ROI, production-grade quality, and sustainable team capability built on the **[PRIME Philosophy](../../prime-framework/philosophy.md)** of transparency, measurability, ownership, safety, and empowerment.
