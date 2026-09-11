---
title: Multi-Device Show Commands
description: Build on Tutorial #1 to collect show commands from multiple Cisco devices using CSV inventory and export to Excel with per-device error handling.
tags:
  - Beginner
  - Netmiko
  - TextFSM
  - Excel
  - Multi-Device
  - Tutorial
---

## Multi-Device Show Command Collection

## "From One to Many — Evolve Your Script for Production Scale"

In [Tutorial #1](./netmiko-show-command-to-excel.md), you built a script that connects to a single device and exports data to Excel. That's a great start, but real network automation needs to handle **multiple devices**.

In this tutorial, we'll **build on your existing script** and evolve it to:

1. Read device inventory from a **CSV file**
2. Loop through **multiple devices**
3. Handle errors gracefully (one device failing doesn't stop the others)
4. Export results to Excel with **one sheet per device**

This is how you transition from a proof-of-concept to a production-ready tool!

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ How to manage device inventory using CSV files
- ✅ How to loop through multiple devices efficiently
- ✅ Why per-device error handling is critical
- ✅ How to combine multi-device data into a single Excel file
- ✅ How to provide user feedback during long operations
- ✅ The difference between "fail-fast" and "continue-on-error" patterns

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [Tutorial #1](./netmiko-show-command-to-excel.md)** — This builds directly on that script
- ✅ Basic understanding of CSV files
- ✅ Comfortable with Python loops and error handling

### Required Software

```bash
# Same libraries as Tutorial #1
pip install netmiko pandas openpyxl
```

### Required Access

- **Multiple Cisco devices** (2 or more) with:
  - SSH enabled
  - Same credentials (or we'll show you how to handle different credentials)
  - Reachable from your workstation

---

## 🔄 Evolution from Tutorial #1

Here's what we're changing:

| Tutorial #1 (Single Device) | Tutorial #2 (Multi-Device) |
| :--- | :--- |
| Device details hardcoded in script | Device list in external CSV file |
| Connects to one device | Loops through multiple devices |
| Script stops if connection fails | Continues to next device on error |
| One Excel file, one device | One Excel file, multiple sheets (one per device) |
| Password entered once | Password entered once, used for all devices |

---

## 🔧 The Complete Script

Here's the full multi-device script. We'll break down what changed below.

```python
"""
Multi-Device Netmiko Script: Show Version to Excel
Description: Connects to multiple Cisco devices from CSV inventory and exports to Excel
Author: Nautomation Prime
"""

# Import required libraries
from netmiko import ConnectHandler
import pandas as pd
import getpass
import csv

# Get password once (used for all devices)
device_password = getpass.getpass('Enter device password: ')

def read_inventory(csv_file):
    """
    Read device inventory from CSV file
    
    Args:
        csv_file: Path to CSV file containing device information
        
    Returns:
        List of device dictionaries ready for Netmiko
    """
    devices = []
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                device = {
                    'device_type': row['device_type'],
                    'host': row['host'],
                    'username': row['username'],
                    'password': device_password,
                    'secret': row.get('secret', ''),  # Optional enable password
                }
                devices.append(device)
        
        print(f"✓ Loaded {len(devices)} device(s) from {csv_file}")
        return devices
        
    except FileNotFoundError:
        print(f"✗ Error: Could not find file '{csv_file}'")
        return []
    except KeyError as e:
        print(f"✗ Error: Missing required column in CSV: {e}")
        return []

def collect_from_device(device):
    """
    Connect to a single device and collect show version data
    
    Args:
        device: Dictionary with connection parameters
        
    Returns:
        Tuple of (hostname, dataframe) or (hostname, None) on error
    """
    hostname = device['host']
    
    try:
        print(f"  Connecting to {hostname}...")
        connection = ConnectHandler(**device)
        
        # Send show command with TextFSM parsing
        output = connection.send_command('show version', use_textfsm=True)
        
        # Check if parsing was successful
        if isinstance(output, list) and len(output) > 0:
            df = pd.DataFrame(output)
            connection.disconnect()
            print(f"  ✓ Success: {hostname} - {len(output)} row(s) collected")
            return (hostname, df)
        else:
            connection.disconnect()
            print(f"  ⚠ Warning: {hostname} - TextFSM parsing returned no data")
            return (hostname, None)
            
    except Exception as e:
        print(f"  ✗ Failed: {hostname} - {str(e)}")
        return (hostname, None)

def main():
    """Main function to orchestrate multi-device collection"""
    
    # Define inventory file
    inventory_file = 'devices.csv'
    
    print("=" * 60)
    print("Multi-Device Show Version Collection")
    print("=" * 60)
    
    # Read device inventory
    devices = read_inventory(inventory_file)
    
    if not devices:
        print("No devices to process. Exiting.")
        return
    
    # Collect data from all devices
    print(f"\nCollecting data from {len(devices)} device(s)...\n")
    
    results = {}
    for device in devices:
        hostname, df = collect_from_device(device)
        if df is not None:
            results[hostname] = df
    
    # Export results to Excel
    if results:
        excel_file = 'multi_device_show_version.xlsx'
        
        print(f"\n{'=' * 60}")
        print(f"Exporting to Excel: {excel_file}")
        
        # Create Excel writer object
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            for hostname, df in results.items():
                # Excel sheet names have a 31-character limit
                sheet_name = hostname[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"  ✓ Sheet created: {sheet_name}")
        
        print(f"\n✓ Successfully exported {len(results)} device(s) to {excel_file}")
        print(f"{'=' * 60}")
    else:
        print("\n✗ No data collected. No Excel file created.")

# Script entry point
if __name__ == "__main__":
    main()
```

---

## 📄 Create Your Inventory File

Before running the script, create a CSV file named `devices.csv` in the same directory:

## **devices.csv**

```csv
device_type,host,username,secret
cisco_ios,192.168.1.1,admin,
cisco_ios,192.168.1.2,admin,
cisco_ios,192.168.1.3,admin,
cisco_nxos,192.168.1.10,admin,
```

**Column Explanations:**

- **device_type**: The Netmiko device type (`cisco_ios`, `cisco_nxos`, `cisco_xr`, etc.)
- **host**: IP address or hostname of the device
- **username**: SSH username
- **secret**: Enable password (leave blank if not needed)

**Important Notes:**

- The CSV must have a header row with these exact column names
- All devices should use the same password (you'll enter it once when the script runs)
- If devices have different passwords, see the "Advanced Variations" section below

---

## 📖 What Changed - Line by Line

Let's focus ONLY on what's different from Tutorial #1. I won't re-explain concepts you already learned.

### New Import

```python
import csv
```

**What it does**: Imports Python's built-in CSV library.

**Why**: We need to read device information from the CSV file. Python's `csv` module makes this easy and handles edge cases like quoted values and different delimiters.

---

### Password Handling Change

**Tutorial #1:**

```python
'password': getpass.getpass('Enter password: '),
```

**Tutorial #2:**

```python
device_password = getpass.getpass('Enter device password: ')
```

**What changed**: We now capture the password in a variable BEFORE defining devices.

**Why**: We only want to prompt for the password once, then reuse it for all devices. In Tutorial #1, the password was part of the device dictionary. Now we store it separately and assign it to each device as we process the CSV.

---

### New Function: `read_inventory()`

This function is completely new. Let's break it down:

```python
def read_inventory(csv_file):
    """
    Read device inventory from CSV file
    
    Args:
        csv_file: Path to CSV file containing device information
        
    Returns:
        List of device dictionaries ready for Netmiko
    """
```

**What it does**: Defines a function that reads our CSV file and returns a list of device dictionaries.

**Why**: Functions make code reusable and testable. By separating the "read CSV" logic from the "connect to devices" logic, we can easily swap to a different inventory source later (like a database or API).

The triple-quoted docstring documents what the function does, what parameters it expects, and what it returns. This is a Python best practice.

---

```python
devices = []
```

**What it does**: Creates an empty list to store device dictionaries.

**Why**: We'll loop through the CSV rows and append each device to this list.

---

```python
try:
    with open(csv_file, 'r') as file:
```

**What it does**: Opens the CSV file for reading using a context manager (`with`).

**Why**:

- The `try` block catches errors if the file doesn't exist
- The `with` statement automatically closes the file when done, even if an error occurs
- `'r'` means "read mode"

---

```python
reader = csv.DictReader(file)
```

**What it does**: Creates a CSV reader that converts each row into a dictionary.

**Why**: `DictReader` automatically uses the first row as column headers. Each subsequent row becomes a dictionary where keys are column names. This is much easier to work with than positional indexes.

For example, if a CSV row is:

```csv
cisco_ios,192.168.1.1,admin,
```

`DictReader` converts it to:

```python
{
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'secret': ''
}
```

---

```python
for row in reader:
```

**What it does**: Loops through each row in the CSV (after the header).

**Why**: We need to process each device one at a time.

---

```python
device = {
    'device_type': row['device_type'],
    'host': row['host'],
    'username': row['username'],
    'password': device_password,
    'secret': row.get('secret', ''),
}
```

**What it does**: Creates a device dictionary in the format Netmiko expects.

**Why**: This dictionary structure is identical to Tutorial #1, but now we're building it from CSV data instead of hardcoding it.

**Important detail:**

- `row['device_type']` gets the value from the CSV
- `device_password` uses the password we captured at the start
- `row.get('secret', '')` safely gets the secret, defaulting to empty string if the column is missing

---

```python
devices.append(device)
```

**What it does**: Adds this device dictionary to our list.

**Why**: We're building a list of all devices to process.

---

```python
print(f"✓ Loaded {len(devices)} device(s) from {csv_file}")
return devices
```

**What it does**: Prints a success message and returns the list of devices.

**Why**: User feedback! It's important to confirm how many devices were loaded before starting connections.

---

```python
except FileNotFoundError:
    print(f"✗ Error: Could not find file '{csv_file}'")
    return []
```

**What it does**: Catches the error if the CSV file doesn't exist.

**Why**: If the file is missing, we want a friendly error message, not a Python traceback. Returning an empty list allows the script to exit gracefully.

---

```python
except KeyError as e:
    print(f"✗ Error: Missing required column in CSV: {e}")
    return []
```

**What it does**: Catches errors if required CSV columns are missing.

**Why**: If someone forgets the `device_type` column, this provides a clear error message instead of a confusing crash.

---

### New Function: `collect_from_device()`

This function wraps the connection logic from Tutorial #1 but adds error handling.

```python
def collect_from_device(device):
    """
    Connect to a single device and collect show version data
    
    Args:
        device: Dictionary with connection parameters
        
    Returns:
        Tuple of (hostname, dataframe) or (hostname, None) on error
    """
```

**What it does**: Defines a function that handles ONE device.

**Why**: By putting the connection logic in a function, we can easily call it in a loop for multiple devices. The function returns either `(hostname, DataFrame)` on success or `(hostname, None)` on failure.

---

```python
hostname = device['host']
```

**What it does**: Stores the device IP/hostname for easier reference.

**Why**: We use `hostname` multiple times in print statements, so storing it in a variable makes code cleaner.

---

```python
try:
    print(f"  Connecting to {hostname}...")
    connection = ConnectHandler(**device)
```

**What it does**: Attempts to connect to the device, wrapped in error handling.

**Why**: The `try` block is CRITICAL for multi-device operations. If this device fails, we want to:

1. Log the error
2. Continue to the next device

Without `try/except`, one failed device would crash the entire script!

**Note the indentation in the print statement**: The leading spaces make output more readable when processing multiple devices.

---

```python
output = connection.send_command('show version', use_textfsm=True)

if isinstance(output, list) and len(output) > 0:
    df = pd.DataFrame(output)
    connection.disconnect()
    print(f"  ✓ Success: {hostname} - {len(output)} row(s) collected")
    return (hostname, df)
```

**What it does**: Same logic as Tutorial #1, but now returns a tuple.

**Why**: We return `(hostname, df)` so the main script knows which device this data came from. This is essential for creating separate Excel sheets later.

---

```python
else:
    connection.disconnect()
    print(f"  ⚠ Warning: {hostname} - TextFSM parsing returned no data")
    return (hostname, None)
```

**What it does**: Handles the case where TextFSM parsing fails.

**Why**: Unlike Tutorial #1 where we printed raw output, here we just log a warning and return `None`. This keeps the script moving through other devices.

---

```python
except Exception as e:
    print(f"  ✗ Failed: {hostname} - {str(e)}")
    return (hostname, None)
```

**What it does**: Catches ANY error during connection or command execution.

**Why**: This is the "continue-on-error" pattern. Instead of crashing, we:

1. Log which device failed and why
2. Return `None` to indicate failure
3. Let the script continue to the next device

Common errors this catches:

- Authentication failures
- Timeouts
- Device unreachable
- SSH not enabled

---

### Updated `main()` Function

The main function now orchestrates the entire multi-device operation.

```python
inventory_file = 'devices.csv'
```

**What it does**: Defines the CSV filename.

**Why**: Having this at the top of `main()` makes it easy to change if you want to use a different filename.

---

```python
print("=" * 60)
print("Multi-Device Show Version Collection")
print("=" * 60)
```

**What it does**: Prints a header banner.

**Why**: Visual feedback. The `"=" * 60` creates a 60-character line of equals signs for a nice separator.

---

```python
devices = read_inventory(inventory_file)

if not devices:
    print("No devices to process. Exiting.")
    return
```

**What it does**: Reads the CSV and exits if no devices were loaded.

**Why**: If the CSV is missing or empty, there's no point continuing. This is defensive programming—check preconditions before doing work.

---

```python
results = {}
for device in devices:
    hostname, df = collect_from_device(device)
    if df is not None:
        results[hostname] = df
```

**What it does**: Loops through all devices and stores successful results in a dictionary.

**Why**:

- `results = {}` creates an empty dictionary
- For each device, we call `collect_from_device()` which returns `(hostname, dataframe)`
- We use Python's tuple unpacking: `hostname, df = collect_from_device(device)`
- `if df is not None` checks if collection succeeded
- `results[hostname] = df` stores the DataFrame with the hostname as the key

This builds a dictionary like:

```python
{
    '192.168.1.1': DataFrame(...),
    '192.168.1.2': DataFrame(...),
    '192.168.1.3': DataFrame(...)
}
```

---

### Excel Export with Multiple Sheets

This is the biggest change from Tutorial #1!

```python
if results:
```

**What it does**: Only exports if we have at least one successful result.

**Why**: If all devices failed, don't create an empty Excel file.

---

```python
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
```

**What it does**: Creates an Excel writer object using a context manager.

**Why**:

- `ExcelWriter` allows us to write multiple sheets to one Excel file
- `engine='openpyxl'` specifies which library to use (same one Tutorial #1 uses)
- The `with` statement ensures the file is properly saved when done

---

```python
for hostname, df in results.items():
```

**What it does**: Loops through our results dictionary.

**Why**: `results.items()` gives us both the key (hostname) and value (DataFrame) for each successful device.

---

```python
sheet_name = hostname[:31]
```

**What it does**: Truncates the hostname to 31 characters.

**Why**: Excel has a limitation—sheet names cannot exceed 31 characters. If your hostname is longer, this prevents an error by only taking the first 31 characters.

---

```python
df.to_excel(writer, sheet_name=sheet_name, index=False)
```

**What it does**: Writes this device's DataFrame to its own sheet.

**Why**:

- `writer` is the Excel file we opened above
- `sheet_name=sheet_name` names the sheet after the device
- `index=False` prevents pandas from adding row numbers

**Key difference from Tutorial #1**: We're calling `to_excel()` multiple times (once per device), all writing to the same `writer` object. This creates multiple sheets in one file!

---

```python
print(f"  ✓ Sheet created: {sheet_name}")
```

**What it does**: Confirms each sheet was created.

**Why**: Real-time feedback during export. For 50 devices, this shows progress.

---

```python
print(f"\n✓ Successfully exported {len(results)} device(s) to {excel_file}")
```

**What it does**: Prints final success summary.

**Why**: Confirms how many devices were exported and where to find the file.

---

## 🚀 How to Run the Script

### Step 1: Create the Inventory CSV

Create `devices.csv` with your device information:

```csv
device_type,host,username,secret
cisco_ios,10.1.1.1,admin,
cisco_ios,10.1.1.2,admin,
cisco_ios,10.1.1.3,admin,
```

**Important**: Save this file in the **same directory** as your Python script.

---

### Step 2: Save the Script

Save the complete script as `multi_device_show_version.py`

---

### Step 3: Run the Script

```bash
python multi_device_show_version.py
```

---

### Step 4: Enter Your Password

When prompted:

```bash
Enter device password:
```

Type your password (it won't be displayed) and press Enter.

---

### Step 5: Watch the Progress

You'll see output like:

```bash
============================================================
Multi-Device Show Version Collection
============================================================
✓ Loaded 3 device(s) from devices.csv

Collecting data from 3 device(s)...

  Connecting to 10.1.1.1...
  ✓ Success: 10.1.1.1 - 1 row(s) collected
  Connecting to 10.1.1.2...
  ✓ Success: 10.1.1.2 - 1 row(s) collected
  Connecting to 10.1.1.3...
  ✗ Failed: 10.1.1.3 - Authentication failed

============================================================
Exporting to Excel: multi_device_show_version.xlsx
  ✓ Sheet created: 10.1.1.1
  ✓ Sheet created: 10.1.1.2

✓ Successfully exported 2 device(s) to multi_device_show_version.xlsx
============================================================
```

Notice that even though device `10.1.1.3` failed, the script continued and exported the two successful devices!

---

## 📊 Example Excel Output

Open `multi_device_show_version.xlsx` and you'll see:

- **Multiple sheet tabs** at the bottom (one per device)
- **Each sheet** contains that device's show version data
- **Sheet names** match the device IPs/hostnames

---

## 🔄 Trying Different Commands

Just like Tutorial #1, you can change the command:

```python
# Change this line:
output = connection.send_command('show version', use_textfsm=True)

# To this:
output = connection.send_command('show ip interface brief', use_textfsm=True)
```

**And update the filename:**

```python
excel_file = 'multi_device_interfaces.xlsx'
```

---

## 🎓 Key Concepts Learned

Congratulations! You've learned critical production automation patterns:

### 1. **External Inventory Management**

Instead of hardcoding devices, you now use CSV files. This means:

- Non-programmers can update the device list
- Easy to maintain as your network grows
- Can generate the CSV from other systems (CMDB, monitoring tools, etc.)

### 2. **Continue-on-Error Pattern**

One device failing doesn't stop the entire job. This is essential for production automation where you might have:

- Devices undergoing maintenance
- Occasional network blips
- Devices with different credential requirements

### 3. **Per-Device Error Handling**

Each device operation is isolated in a try/except block, providing:

- Clear logging of which device failed and why
- Ability to collect partial results
- Easier troubleshooting

### 4. **Data Aggregation**

Multiple device results combined into one Excel file with multiple sheets. This is much better than:

- Dozens of separate files
- Having to manually combine data
- Losing track of which device is which

### 5. **User Feedback**

Progress indicators during long operations keep users informed:

- CSV load confirmation
- Per-device connection status
- Export progress
- Final summary

---

## 🐛 Troubleshooting

### "Could not find file 'devices.csv'"

**Cause**: The CSV file isn't in the same directory as the script.

**Solution**:

- Check the CSV file exists
- Make sure it's in the same folder as your Python script
- Or use an absolute path: `inventory_file = 'C:/path/to/devices.csv'`

---

### Some Devices Fail with "Authentication failed"

**Cause**: Those devices have different credentials.

**Solution**: See "Advanced Variations" below for per-device passwords.

---

### Excel Sheet Name is Cut Off

**Cause**: Hostname longer than 31 characters (Excel limit).

**Solution**: This is expected behaviour. The script automatically truncates to 31 characters. If you need full hostnames, you could:

- Add a column in the sheet with the full hostname
- Create a mapping file
- Use shorter hostnames in your CSV

---

### No Data Collected (All Devices Failed)

**Troubleshooting steps**:

1. Verify you can manually SSH to at least one device
2. Check the error messages—common issues:
   - Wrong password
   - Wrong device_type in CSV
   - Devices unreachable
3. Test with just one device in the CSV first

---

## 🚀 Advanced Variations

### Different Passwords Per Device

If devices have different passwords, modify the CSV and script:

**devices.csv with passwords:**

```csv
device_type,host,username,password,secret
cisco_ios,10.1.1.1,admin,password1,
cisco_ios,10.1.1.2,admin,password2,
```

**Modified script (don't prompt for password):**

```python
# Remove this line:
# device_password = getpass.getpass('Enter device password: ')

# In read_inventory(), change this:
'password': row['password'],  # Get from CSV instead
```

**Security Warning**: Storing passwords in CSV is NOT recommended for production. Consider using a vault like HashiCorp Vault, CyberArk, or encrypted files.

---

### Separate Excel Files Per Device

If you prefer individual files instead of multiple sheets:

```python
# Replace the Excel export section with:
for hostname, df in results.items():
    excel_file = f"{hostname}_show_version.xlsx"
    df.to_excel(excel_file, index=False, sheet_name='Show Version')
    print(f"  ✓ Created: {excel_file}")
```

---

### Add Timestamp to Filename

To avoid overwriting previous runs:

```python
from datetime import datetime

# Add at the top of main():
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
excel_file = f'multi_device_show_version_{timestamp}.xlsx'
```

This creates files like: `multi_device_show_version_20260215_143022.xlsx`

---

### Filter Devices from CSV

Only process specific devices:

```python
# After loading devices:
devices = [d for d in devices if d['device_type'] == 'cisco_ios']
print(f"Filtered to {len(devices)} IOS device(s)")
```

---

## 🎯 Next Steps

You've now mastered multi-device automation! Ready for the next challenge?

**Continue Learning with These Tutorials:**

1. **[Configuration Backup](./multi-device-config-backup.md)** (Complete the Beginner Path)
   - Save device configurations to disk
   - Build timestamped archives for version control
   - Understand data persistence patterns

2. **[Nornir Fundamentals](../intermediate/nornir-fundamentals.md)** (Intermediate)
   - Learn a powerful framework for scaling automation
   - Understand how industries run automation at scale
   - Multi-threaded device operations (10x speed improvement)

3. **[Enterprise Config Backup with Nornir](../intermediate/enterprise-config-backup-nornir.md)** (Intermediate)
   - See the backup pattern scaled to production
   - Integration with structured logging and error handling
   - Real-world patterns used in enterprise deployments

    **Study Production Code:**

4. **[Deep Dives](../../deep-dives/index.md)** — Review complete production tools
   - [Access Switch Audit](../../deep-dives/access-switch-audit.md) — Learn parallel device collection and PoE intelligence
   - [CDP Network Audit](../../deep-dives/cdp-audit.md) — Study threading, configuration, and jump host support

    **Ready to Deploy?**

5. **[Script Library](../../../scripts/index.md)** — Deploy pre-built tools based on these patterns
   - Credential vaulting with HashiCorp Vault
   - Event-driven automation and webhooks
   - GitOps workflows and CI/CD integration
   - Container deployment and orchestration

6. **[Deep Dives](../../deep-dives/index.md)** — Study production-grade tools:
   - [CDP Network Audit](../../deep-dives/cdp-audit.md) — Multi-threaded topology discovery
   - [Access Switch Audit](../../deep-dives/access-switch-audit.md) — Parallel port health collection

7. **Enhance This Script** — Practice by adding:
   - Progress bars (using the `tqdm` library)
   - Logging to file with the `logging` module
   - Retry logic for failed devices
   - Different commands for different device types
   - Export to CSV in addition to Excel

---

## 💡 Production Readiness Checklist

Want to use this script in production? Consider these enhancements:

### 🟡 Intermediate Level (Coming Soon in Tutorials)

- [ ] **Threading & Concurrency**: Use threading for parallel device connections (10x faster!)
- [ ] **Advanced TextFSM**: Create custom parsing templates for unsupported commands
- [ ] **Configuration Templating**: Use Jinja2 for dynamic configuration generation
- [ ] **Structured Logging**: Implement Python's `logging` module with rotating file handlers
- [ ] **Progress Indicators**: Add `tqdm` progress bars for long-running operations
- [ ] **Command-Line Arguments**: Use `argparse` to specify CSV file, commands, output format
- [ ] **Configuration Files**: Store settings in YAML/JSON instead of hardcoding
- [ ] **Input Validation**: Verify CSV format, IP addresses, and device types before processing
- [ ] **Retry Logic**: Implement exponential backoff for transient failures
- [ ] **Data Validation**: Sanitize and validate collected data before export
- [ ] **Exception Handling**: Granular error handling for different failure types
- [ ] **Dry-Run Mode**: Preview operations without executing changes

### 🔴 Expert Level (Coming Soon in Tutorials)

- [ ] **Nornir Framework**: Scale to hundreds of devices with Nornir's task-based architecture
- [ ] **Async Operations**: Use `asyncio` for true concurrent I/O operations
- [ ] **Database Integration**: Store results in PostgreSQL/SQLite for historical trending
- [ ] **Credential Vaulting**: Integrate HashiCorp Vault or AWS Secrets Manager
- [ ] **API Integration**: Trigger automation via REST API endpoints or webhooks
- [ ] **Message Queuing**: Use RabbitMQ or Kafka for distributed task processing
- [ ] **Observability**: Structured logging to ELK stack, metrics to Prometheus/Grafana
- [ ] **CI/CD Integration**: GitHub Actions, GitLab CI for automated testing and deployment
- [ ] **GitOps Workflows**: Store device configs in Git with version control and rollback
- [ ] **Event-Driven Automation**: React to network events (syslog, SNMP traps, streaming telemetry)
- [ ] **Ansible Integration**: Combine Python scripts with Ansible playbooks
- [ ] **Tool Integration**: Netbox for inventory, ServiceNow for CMDB, DNA Center APIs
- [ ] **Container Deployment**: Package as Docker containers with scheduled execution
- [ ] **Testing & Validation**: Unit tests, integration tests, mock device testing
- [ ] **Multi-Vendor Support**: Extend to Arista, Juniper, Palo Alto with NAPALM

These topics are covered in our **Intermediate** and **Expert** tutorials!

---

## 💬 What You've Accomplished

**Impressive!** You've evolved from a single-device script to a multi-device automation tool. You now understand:

✅ CSV inventory management  
✅ Looping through devices  
✅ Continue-on-error patterns  
✅ Multi-sheet Excel export  
✅ User feedback during operations  
✅ Defensive programming techniques  

This foundation prepares you for enterprise automation scenarios where resilience and scale matter.

---

[← Back to Beginner Tutorials](./index.md) | [Continue to Tutorial #3 →](./multi-device-config-backup.md)
