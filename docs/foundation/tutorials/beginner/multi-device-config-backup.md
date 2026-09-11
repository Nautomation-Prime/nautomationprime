---
title: Multi-Device Configuration Backup
description: Build on Tutorial #2 to automatically backup running configurations from multiple Cisco devices with timestamped filenames, organised by device type.
tags:
  - Beginner
  - Netmiko
  - Configuration Management
  - Backup
  - Multi-Device
  - Tutorial
---

## Multi-Device Configuration Backup

## "From Read-Only to Read-and-Archive — Capture Your Network's Source of Truth"

In [Tutorial #1](./netmiko-show-command-to-excel.md), you read `show` commands. In [Tutorial #2](./multi-device-show-command.md), you scaled that to multiple devices. But here's the problem: **show command output is temporary**. If your network changes (intentionally or by mistake), that data is lost.

In this tutorial, we'll **build on your multi-device foundation** and create a production-grade backup system:

1. Collect **running configurations** from multiple devices (not just show commands)
2. Save each config to a **timestamped backup file**
3. Organise configs by **device type and hostname**
4. Handle errors gracefully **(one failed backup doesn't stop others)**
5. Provide a **backup inventory** showing what was and wasn't captured

This is how you build **audit trails** and enable quick disaster recovery!

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ How to retrieve full running configurations from network devices
- ✅ Why timestamped backups are critical for change tracking
- ✅ How to organise backups in a logical directory structure
- ✅ The difference between running and startup configurations
- ✅ How to create a backup manifest (what was backed up, when, and from where)
- ✅ Per-device backup validation and error handling
- ✅ File I/O in Python and directory management
- ✅ How to prepare for configuration comparison and drift detection

---

## 📋 Prerequisites

### Required Knowledge

- ✅ **Completed [Tutorial #2](./multi-device-show-command.md)** — This builds directly on that script
- ✅ Basic understanding of network configuration files
- ✅ Comfortable with Python file I/O operations
- ✅ Familiar with directory structures and file naming conventions

### Required Software

```bash
# Same libraries as Tutorial #2
pip install netmiko pandas openpyxl
```

Note: We use `pandas` and `openpyxl` only for the backup manifest. Configuration data is plain text files.

### Required Access

- **Multiple Cisco devices** (2 or more) with:
  - SSH enabled
  - Same credentials (or per-device credentials)
  - Reachable from your workstation
  - Accessible user with privilege level 15 or equivalent (needed to read running config)

---

## 🔄 Evolution from Tutorial #2

Here's what we're changing:

| Tutorial #2 (Show Commands) | Tutorial #3 (Configurations) |
| :--- | :--- |
| Executes show commands | Executes `show run` (running config) |
| Parses output with TextFSM | No parsing—raw config text |
| Exports to Excel sheets | Saves to timestamped `.txt` files |
| One Excel file with data | Organised folder structure with manifest |
| Shows data table | Shows backup file locations and sizes |

Key insight: **Configurations are too large and complex for Excel**. We save them as files and create a manifest for tracking.

---

## 🔧 The Complete Script

Here's the full backup script. We'll break down what changed below.

```python
"""
Multi-Device Configuration Backup Script
Description: Backs up running configs from multiple Cisco devices with timestamps and manifest
Author: Nautomation Prime
"""

# Import required libraries
from netmiko import ConnectHandler
import pandas as pd
import getpass
import csv
import os
from datetime import datetime

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
                    'secret': row.get('secret', ''),
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

def create_backup_directory(base_directory='backups'):
    """
    Create a timestamped backup directory
    
    Args:
        base_directory: Parent directory for backups (default: 'backups')
        
    Returns:
        Path to the created timestamp directory
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(base_directory, timestamp)
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        print(f"✓ Created backup directory: {backup_dir}")
        return backup_dir
    except Exception as e:
        print(f"✗ Error creating backup directory: {e}")
        return None

def backup_device_config(device, backup_dir):
    """
    Connect to a device and backup its running configuration
    
    Args:
        device: Dictionary with connection parameters
        backup_dir: Directory where backups will be stored
        
    Returns:
        Tuple of (hostname, config_filename, file_size, status) or (hostname, None, 0, 'failed')
    """
    hostname = device['host']
    device_type = device['device_type']
    
    try:
        print(f"  Connecting to {hostname} ({device_type})...")
        connection = ConnectHandler(**device)
        if device.get('secret'):
            connection.enable()
        
        # Get running configuration
        print(f"    Retrieving running configuration...")
        config = connection.send_command('show running-config')
        
        # Verify we got data
        if isinstance(config, str) and len(config) > 0:
            # Create safe filename: replace dots with dashes in IP addresses
            safe_hostname = hostname.replace('.', '-')
            config_filename = f"{safe_hostname}_running-config.txt"
            config_filepath = os.path.join(backup_dir, config_filename)
            
            # Write configuration to file
            with open(config_filepath, 'w') as f:
                f.write(config)
            
            # Get file size to confirm write
            file_size = os.path.getsize(config_filepath)
            
            connection.disconnect()
            print(f"  ✓ Success: {hostname} - {file_size} bytes backed up")
            return (hostname, config_filename, file_size, 'success')
        else:
            connection.disconnect()
            print(f"  ⚠ Warning: {hostname} - No configuration data received")
            return (hostname, None, 0, 'no-data')
            
    except Exception as e:
        print(f"  ✗ Failed: {hostname} - {str(e)}")
        return (hostname, None, 0, 'failed')

def create_backup_manifest(backup_dir, results):
    """
    Create an Excel manifest of all backup operations
    
    Args:
        backup_dir: Directory containing backups
        results: List of backup operation results
        
    Returns:
        Path to created manifest file
    """
    # Prepare data for manifest
    manifest_data = []
    
    for hostname, filename, size, status in results:
        manifest_data.append({
            'Device IP': hostname,
            'Backup File': filename if filename else 'N/A',
            'File Size (bytes)': size,
            'Status': status,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Create DataFrame
    df = pd.DataFrame(manifest_data)
    
    # Write to Excel
    manifest_filename = 'backup_manifest.xlsx'
    manifest_filepath = os.path.join(backup_dir, manifest_filename)
    
    try:
        df.to_excel(manifest_filepath, index=False, sheet_name='Backup Manifest')
        print(f"\n✓ Manifest created: {manifest_filename}")
        return manifest_filepath
    except Exception as e:
        print(f"✗ Error creating manifest: {e}")
        return None

def main():
    """Main function to orchestrate multi-device backup"""
    
    # Define settings
    inventory_file = 'devices.csv'
    base_backup_dir = 'backups'
    
    print("=" * 70)
    print("Multi-Device Configuration Backup")
    print("=" * 70)
    
    # Read device inventory
    devices = read_inventory(inventory_file)
    
    if not devices:
        print("No devices to process. Exiting.")
        return
    
    # Create timestamped backup directory
    backup_dir = create_backup_directory(base_backup_dir)
    
    if not backup_dir:
        print("Failed to create backup directory. Exiting.")
        return
    
    # Backup configurations from all devices
    print(f"\nBacking up {len(devices)} device(s)...\n")
    
    results = []
    successful_backups = 0
    failed_backups = 0
    
    for device in devices:
        hostname, filename, size, status = backup_device_config(device, backup_dir)
        results.append((hostname, filename, size, status))
        
        if status == 'success':
            successful_backups += 1
        else:
            failed_backups += 1
    
    # Create backup manifest
    print(f"\n{'=' * 70}")
    create_backup_manifest(backup_dir, results)
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("BACKUP SUMMARY")
    print(f"{'=' * 70}")
    print(f"Backup Location: {backup_dir}")
    print(f"Successful Backups: {successful_backups}/{len(devices)}")
    print(f"Failed Backups: {failed_backups}/{len(devices)}")
    print(f"{'=' * 70}\n")
    
    if successful_backups > 0:
        print("Backed Up Devices:")
        for hostname, filename, size, status in results:
            if status == 'success':
                print(f"  ✓ {hostname}: {filename} ({size:,} bytes)")
    
    if failed_backups > 0:
        print("\nFailed Devices:")
        for hostname, filename, size, status in results:
            if status != 'success':
                print(f"  ✗ {hostname}: {status}")

# Script entry point
if __name__ == "__main__":
    main()
```

---

## 📄 Create Your Inventory File

Use the same CSV format as Tutorial #2. Create `devices.csv`:

```csv
device_type,host,username,secret
cisco_ios,192.168.1.1,admin,
cisco_ios,192.168.1.2,admin,
cisco_nxos,192.168.1.10,admin,
```

---

## 📖 What Changed - Line by Line

Let's focus on what's different from Tutorial #2. We'll skip unchanged sections and highlight new concepts.

### New Imports

```python
import os
from datetime import datetime
```

**What they do**:

- `os`: Provides functions to interact with the operating system (create directories, work with file paths)
- `datetime`: Allows us to generate timestamps for backup directories

**Why**: We need to create timestamped directories and write files to disk.

---

### New Function: `create_backup_directory()`

This function is completely new:

```python
def create_backup_directory(base_directory='backups'):
    """
    Create a timestamped backup directory
    
    Args:
        base_directory: Parent directory for backups (default: 'backups')
        
    Returns:
        Path to the created timestamp directory
    """
```

**What it does**: Creates a directory structure like `backups/20260215_143022/` for each backup run.

**Why**: Timestamped directories allow you to keep historical backups. You can compare configs from different dates and see exactly when changes occurred.

---

```python
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
```

**What it does**: Gets the current date and time in format `YYYYMMDD_HHMMSS` (e.g., `20260215_143022`).

**Why**: This creates unique, sortable directory names. Sorting by name sorts by time!

---

```python
backup_dir = os.path.join(base_directory, timestamp)
```

**What it does**: Joins path components safely.

**Why**: `os.path.join()` handles Windows vs. Unix path separators automatically. It's much better than manually concatenating strings with `/` or `\`.

Example output:

- Linux: `backups/20260215_143022`
- Windows: `backups\20260215_143022`

---

```python
try:
    os.makedirs(backup_dir, exist_ok=True)
    print(f"✓ Created backup directory: {backup_dir}")
    return backup_dir
except Exception as e:
    print(f"✗ Error creating backup directory: {e}")
    return None
```

**What it does**: Creates the directory, handling errors gracefully.

**Why**:

- `os.makedirs()` creates all intermediate directories (like `mkdir -p`)
- `exist_ok=True` means "don't error if the directory already exists"
- The try/except block catches permission errors or other filesystem issues
- If success, we return the path; if failure, we return `None`

---

### New Function: `backup_device_config()`

This is the core backup function:

```python
def backup_device_config(device, backup_dir):
    """
    Connect to a device and backup its running configuration
    
    Args:
        device: Dictionary with connection parameters
        backup_dir: Directory where backups will be stored
        
    Returns:
        Tuple of (hostname, config_filename, file_size, status)
    """
```

**What it does**: Connects to ONE device, retrieves its running configuration, and saves it to a file.

**Why**: Similar to Tutorial #2's `collect_from_device()`, but instead of returning a DataFrame, we return file information. The function is designed to be called in a loop for multiple devices.

---

```python
hostname = device['host']
device_type = device['device_type']

try:
    print(f"  Connecting to {hostname} ({device_type})...")
    connection = ConnectHandler(**device)
    if device.get('secret'):
        connection.enable()
```

**What it does**: Stores device info and connects.

**Why**: Same pattern as Tutorial #2. We display the device_type so users know what they're connecting to. If an enable secret is provided, `connection.enable()` enters privileged EXEC mode before reading the running configuration.

---

```python
config = connection.send_command('show running-config')
```

**What it does**: Sends the `show running-config` command and gets the raw output.

**Why**: Key difference from earlier tutorials:

- **No `use_textfsm=True`**: Running configs are text-based and don't need parsing
- **Raw text output**: We keep it exactly as-is for archiving

---

```python
if isinstance(config, str) and len(config) > 0:
```

**What it does**: Verifies we got configuration data.

**Why**: Unlike TextFSM-parsed data (which is a list), `show running-config` returns a string. We check it's not empty.

---

```python
safe_hostname = hostname.replace('.', '-')
config_filename = f"{safe_hostname}_running-config.txt"
```

**What it does**: Creates a safe filename from the hostname.

**Why**:

- Filenames can't contain certain characters (like dots)
- Replacing `192.168.1.1` with `192-168-1-1` makes the filename valid
- The pattern `hostname_running-config.txt` is clear and self-documenting

---

```python
config_filepath = os.path.join(backup_dir, config_filename)

with open(config_filepath, 'w') as f:
    f.write(config)
```

**What it does**: Creates a file and writes the configuration.

**Why**:

- `os.path.join()` creates the full path (e.g., `backups/20260215_143022/192-168-1-1_running-config.txt`)
- `with open(...) as f:` opens the file in a context manager (auto-closes even if error occurs)
- `f.write(config)` writes the entire configuration to the file

---

```python
file_size = os.path.getsize(config_filepath)
```

**What it does**: Gets the file size in bytes.

**Why**: File size is useful for sanity checks:

- If a large router backed up only 100 bytes, something's wrong
- Users can see at a glance which devices have large configs

---

```python
connection.disconnect()
print(f"  ✓ Success: {hostname} - {file_size} bytes backed up")
return (hostname, config_filename, file_size, 'success')
```

**What it does**: Closes connection and returns success information.

**Why**: Returns a tuple with:

- `hostname`: Which device
- `config_filename`: Filename (for reference)
- `file_size`: How much data
- `status`: 'success' (vs. 'failed' or 'no-data')

---

```python
except Exception as e:
    print(f"  ✗ Failed: {hostname} - {str(e)}")
    return (hostname, None, 0, 'failed')
```

**What it does**: Catches any error and continues gracefully.

**Why**: Continue-on-error pattern from Tutorial #2. One device failure doesn't stop the whole backup.

---

### New Function: `create_backup_manifest()`

This function creates an Excel summary of the backup operation:

```python
def create_backup_manifest(backup_dir, results):
    """
    Create an Excel manifest of all backup operations
    
    Args:
        backup_dir: Directory containing backups
        results: List of backup operation results
        
    Returns:
        Path to created manifest file
    """
    manifest_data = []
    
    for hostname, filename, size, status in results:
        manifest_data.append({
            'Device IP': hostname,
            'Backup File': filename if filename else 'N/A',
            'File Size (bytes)': size,
            'Status': status,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
```

**What it does**: Builds a list of dictionaries, one per device.

**Why**: Each dictionary becomes a row in the Excel manifest. The manifest acts as a **backup inventory**—a record of what was backed up, when, and from where.

---

```python
df = pd.DataFrame(manifest_data)
```

**What it does**: Converts the list of dictionaries to a pandas DataFrame.

**Why**: Makes it easy to export to Excel—same pattern as Tutorial #1.

---

```python
manifest_filename = 'backup_manifest.xlsx'
manifest_filepath = os.path.join(backup_dir, manifest_filename)

df.to_excel(manifest_filepath, index=False, sheet_name='Backup Manifest')
```

**What it does**: Saves the manifest to an Excel file in the backup directory.

**Why**: The manifest lives alongside the backups, providing metadata. Users can open it to see:

- Which devices succeeded/failed
- How large each device's config is
- When the backup ran

---

### Updated `main()` Function

The main function orchestrates the entire backup operation:

```python
results = []
successful_backups = 0
failed_backups = 0

for device in devices:
    hostname, filename, size, status = backup_device_config(device, backup_dir)
    results.append((hostname, filename, size, status))
    
    if status == 'success':
        successful_backups += 1
    else:
        failed_backups += 1
```

**What it does**: Loops through devices and counts successes/failures.

**Why**:

- `results` collects all backup operations (for the manifest)
- Counters track success/failure for the summary report
- Similar pattern to Tutorial #2, but with status tracking

---

```python
if successful_backups > 0:
    print("Backed Up Devices:")
    for hostname, filename, size, status in results:
        if status == 'success':
            print(f"  ✓ {hostname}: {filename} ({size:,} bytes)")
```

**What it does**: Lists all successful backups.

**Why**: User feedback. The `{size:,}` formats numbers with commas (e.g., `15,234` instead of `15234`).

---

## 🚀 How to Run the Script

### Step 1: Create the Inventory CSV

Create `devices.csv`:

```csv
device_type,host,username,secret
cisco_ios,10.1.1.1,admin,
cisco_ios,10.1.1.2,admin,
cisco_nxos,10.1.1.10,admin,
```

---

### Step 2: Save the Script

Save the complete script as `backup_running_configs.py`

---

### Step 3: Run the Script

```bash
python backup_running_configs.py
```

---

### Step 4: Enter Your Password

When prompted:

```text
Enter device password:
```

Type your password (it won't be displayed) and press Enter.

---

### Step 5: Watch the Progress

You'll see output like:

```bash
======================================================================
Multi-Device Configuration Backup
======================================================================
✓ Loaded 3 device(s) from devices.csv
✓ Created backup directory: backups/20260215_143022

Backing up 3 device(s)...

  Connecting to 10.1.1.1 (cisco_ios)...
    Retrieving running configuration...
  ✓ Success: 10.1.1.1 - 45,234 bytes backed up
  Connecting to 10.1.1.2 (cisco_ios)...
    Retrieving running configuration...
  ✓ Success: 10.1.1.2 - 38,912 bytes backed up
  Connecting to 10.1.1.10 (cisco_nxos)...
    Retrieving running configuration...
  ✓ Success: 10.1.1.10 - 62,148 bytes backed up

======================================================================
✓ Manifest created: backup_manifest.xlsx

======================================================================
BACKUP SUMMARY
======================================================================
Backup Location: backups/20260215_143022
Successful Backups: 3/3
Failed Backups: 0/3
======================================================================

Backed Up Devices:
  ✓ 10.1.1.1: 10-1-1-1_running-config.txt (45,234 bytes)
  ✓ 10.1.1.2: 10-1-1-2_running-config.txt (38,912 bytes)
  ✓ 10.1.1.10: 10-1-1-10_running-config.txt (62,148 bytes)
```

---

### Step 6: Verify Your Backups

After running, you'll see this directory structure:

```text
backups/
└── 20260215_143022/
    ├── backup_manifest.xlsx
    ├── 10-1-1-1_running-config.txt
    ├── 10-1-1-2_running-config.txt
    └── 10-1-1-10_running-config.txt
```

Each `.txt` file contains the full running configuration from that device!

---

## 📊 Example Backup Directory Structure

After running backups multiple times, you'll have:

```text
backups/
├── 20260215_120000/
│   ├── backup_manifest.xlsx
│   ├── 192-168-1-1_running-config.txt
│   ├── 192-168-1-2_running-config.txt
│   └── 192-168-1-10_running-config.txt
├── 20260215_143022/
│   ├── backup_manifest.xlsx
│   ├── 192-168-1-1_running-config.txt
│   ├── 192-168-1-2_running-config.txt
│   └── 192-168-1-10_running-config.txt
└── 20260216_090000/
    ├── backup_manifest.xlsx
    ├── 192-168-1-1_running-config.txt
    ├── 192-168-1-2_running-config.txt
    └── 192-168-1-10_running-config.txt
```

This structure makes it trivial to:

- Find the latest backup
- Compare configs across backup runs
- Identify when changes occurred
- Restore configs from any point in time

---

## 🔄 Trying Different Configuration Sources

The script currently backs up `show running-config`. You can capture other config sources:

```python
# Backup startup configuration instead:
config = connection.send_command('show startup-config')

# Backup candidate configuration (some platforms):
config = connection.send_command('show candidate-config')
```

Just update the `send_command()` call and modify the filename accordingly.

---

## 🎓 Key Concepts Learned

Congratulations! You've built a production-grade backup system. You now understand:

### 1. **File I/O Operations**

Reading configurations from devices and reliably writing them to disk with proper error handling.

### 2. **Directory Structure and Organisation**

Using timestamps to organise backups chronologically and creating logical directory hierarchies.

### 3. **Backup Validation**

Confirming that data was successfully written to disk by checking file sizes.

### 4. **Manifest/Inventory Tracking**

Creating audit trails (the Excel manifest) that record what was backed up, when, and the status.

### 5. **Configuration Versioning**

Organizing timestamped backups to enable version tracking and change detection.

### 6. **Safe Filename Handling**

Converting hostnames with special characters into valid filenames.

### 7. **Multi-Step Operations**

Combining several operations (connect, command, file write, validation) into a cohesive workflow.

---

## 🐛 Troubleshooting

### "Permission denied" when creating backup directory

**Cause**: You don't have write permissions in the directory where the script runs.

**Solution**:

- Try running from a different directory
- Use an absolute path: `base_backup_dir = 'C:/Backups'` (Windows) or `/tmp/backups` (Linux)
- Check file permissions on the current directory

---

### Backup files are empty or very small

**Causes**:

- Device user doesn't have privilege level 15 (can't read full config)
- Device running-config is actually small (possible but unlikely)
- Command executed but returned no data

**Solution**:

- Verify your account has `privilege level 15` or equivalent
- Check manually with SSH: `show running-config | wc -l` to see line count
- Verify `show running-config` works manually on the device

---

### "Authentication failed" for some devices

**Cause**: Those devices have different credentials.

**Solution**: See "Advanced Variations" below for per-device passwords.

---

### Running the script multiple times is creating huge backup directories

**Cause**: Each run creates a new timestamped directory.

**Solution**: This is by design! Each run is a separate backup point. If you want to clean old backups:

```bash
# Windows
rmdir /s /q backups\20260101_000000

# Linux
rm -rf backups/20260101_000000
```

Or implement retention policies (see "Advanced Variations").

---

## 🚀 Advanced Variations

### Per-Device Passwords

If devices have different passwords, use per-device credentials in CSV:

**devices.csv with passwords:**

```csv
device_type,host,username,password,secret
cisco_ios,10.1.1.1,admin,password1,
cisco_ios,10.1.1.2,admin,password2,
```

**Modified `read_inventory()` function:**

```python
def read_inventory(csv_file):
    devices = []
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                device = {
                    'device_type': row['device_type'],
                    'host': row['host'],
                    'username': row['username'],
                    'password': row['password'],  # Get from CSV instead
                    'secret': row.get('secret', ''),
                }
                devices.append(device)
        
        print(f"✓ Loaded {len(devices)} device(s) from {csv_file}")
        return devices
    # ... rest of function unchanged
```

**Security Note**: Storing passwords in CSV is NOT recommended for production. Use a vault (HashiCorp Vault, CyberArk, AWS Secrets Manager) instead.

---

### Add Pre- and Post-Backup Hash Checking

Detect if config changed since last backup:

```python
import hashlib

def get_config_hash(config):
    """Calculate SHA256 hash of configuration"""
    return hashlib.sha256(config.encode()).hexdigest()

# In backup_device_config():
config = connection.send_command('show running-config')
config_hash = get_config_hash(config)

# Store hash in manifest for comparison
```

Then compare hashes in your manifest to detect changes!

---

### Organise by Device Type

Save IOS configs separately from NX-OS:

```python
def backup_device_config(device, backup_dir):
    # Create subdirectory by device type
    device_type_dir = os.path.join(backup_dir, device['device_type'])
    os.makedirs(device_type_dir, exist_ok=True)
    
    # ... rest of function, but use device_type_dir instead of backup_dir
```

Result:

```text
backups/20260215_143022/
├── cisco_ios/
│   ├── 192-168-1-1_running-config.txt
│   └── 192-168-1-2_running-config.txt
├── cisco_nxos/
│   └── 192-168-1-10_running-config.txt
└── backup_manifest.xlsx
```

---

### Backup to Remote Server (SFTP)

Store backups on a remote backup server instead of local disk:

```python
from paramiko import SFTPClient, Transport
import socket

def backup_to_sftp(config, hostname, sftp_host, sftp_user, sftp_pass):
    """Backup config to remote SFTP server"""
    try:
        transport = Transport((sftp_host, 22))
        transport.connect(username=sftp_user, password=sftp_pass)
        sftp = SFTPClient.from_transport(transport)
        
        safe_hostname = hostname.replace('.', '-')
        filename = f"{safe_hostname}_running-config.txt"
        
        with sftp.file(filename, 'w') as f:
            f.write(config)
        
        transport.close()
        return True
    except Exception as e:
        print(f"SFTP backup failed: {e}")
        return False
```

---

### Backup Only if Config Changed

Compare current config with previous backup:

```python
import glob
import os

def find_latest_backup(hostname, base_dir='backups'):
    """Find the most recent backup file for a device"""
    safe_hostname = hostname.replace('.', '-')
    pattern = os.path.join(base_dir, '*', f'{safe_hostname}_running-config.txt')
    backups = glob.glob(pattern)
    return max(backups) if backups else None

def config_changed(hostname, current_config):
    """Check if config differs from last backup"""
    latest_backup = find_latest_backup(hostname)
    
    if latest_backup is None:
        return True  # No previous backup, so "changed"
    
    with open(latest_backup, 'r') as f:
        previous_config = f.read()
    
    return current_config != previous_config

# In backup_device_config():
config = connection.send_command('show running-config')

if not config_changed(hostname, config):
    print(f"  ⚠ No changes since last backup. Skipping.")
    return (hostname, None, 0, 'no-change')
```

---

### Email Notification on Backup Completion

Send status report via email:

```python
import smtplib
from email.mime.text import MIMEText

def send_backup_email(backup_dir, results, smtp_host, smtp_user, smtp_pass, recipient):
    """Send backup status via email"""
    successful = sum(1 for _, _, _, status in results if status == 'success')
    failed = sum(1 for _, _, _, status in results if status != 'success')
    
    body = f"""
Backup Summary:
Backup Location: {backup_dir}
Successful: {successful}
Failed: {failed}

Backed Up Devices:
"""
    
    for hostname, filename, size, status in results:
        if status == 'success':
            body += f"✓ {hostname}: {filename} ({size:,} bytes)\n"
    
    if failed > 0:
        body += "\nFailed Devices:\n"
        for hostname, _, _, status in results:
            if status != 'success':
                body += f"✗ {hostname}: {status}\n"
    
    msg = MIMEText(body)
    msg['Subject'] = f"Config Backup Report: {successful} successful, {failed} failed"
    msg['From'] = smtp_user
    msg['To'] = recipient
    
    server = smtplib.SMTP(smtp_host, 587)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    server.quit()

# In main():
send_backup_email(backup_dir, results, 'smtp.gmail.com', 'your_email@gmail.com', 'password', 'admin@company.com')
```

---

### Retention Policy (Auto-Delete Old Backups)

Keep only last 30 days of backups:

```python
from datetime import datetime, timedelta
import glob

def cleanup_old_backups(base_dir, days_to_keep=30):
    """Delete backup directories older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for backup_dir in glob.glob(os.path.join(base_dir, '*')):
        if not os.path.isdir(backup_dir):
            continue
        
        # Extract timestamp from directory name (format: YYYYMMDD_HHMMSS)
        dirname = os.path.basename(backup_dir)
        try:
            backup_date = datetime.strptime(dirname, '%Y%m%d_%H%M%S')
            
            if backup_date < cutoff_date:
                import shutil
                shutil.rmtree(backup_dir)
                print(f"  ✓ Deleted old backup: {dirname}")
        except ValueError:
            pass  # Skip non-timestamped directories

# In main(), after creating manifest:
cleanup_old_backups(base_backup_dir, days_to_keep=30)
```

---

## 🎯 Next Steps

You've now built a complete backup system! Ready for the next challenge?

**Continue Learning with These Tutorials:**

1. **Complete the Learning Path:**
   - You've completed the Beginner tutorials! You now understand Netmiko, multi-device connections, and data management.

2. **[Nornir Fundamentals](../intermediate/nornir-fundamentals.md)** (Intermediate)
   - Learn a powerful framework used in enterprise automation
   - Understand how to scale to thousands of devices
   - Master structured task execution

3. **[Enterprise Config Backup with Nornir](../intermediate/enterprise-config-backup-nornir.md)** (Intermediate)
   - See this same backup pattern scaled to production
   - Backup comparison and diff reporting
   - Configuration drift detection and automated remediation
   - Encrypted backup storage and database-backed versioning

4. **[Advanced Nornir Patterns](../intermediate/advanced-nornir-patterns.md)** (Intermediate)
   - Advanced filtering and task chaining
   - Custom inventory sources
   - Integration with external systems

    **Study Production Code:**

5. **[Deep Dives](../../deep-dives/index.md)** — Review how production tools handle similar challenges
   - [CDP Network Audit](../../deep-dives/cdp-audit.md) — Threading, security, and credential management
   - [Access Switch Audit](../../deep-dives/access-switch-audit.md) — Parallel device collection and intelligent parsing

    **Ready to Deploy?**

6. **[Script Library](../../../scripts/index.md)** — Deploy pre-built tools
   - Access Switch Audit for port configurations

7. **Enhance This Script** — Practice by adding:
   - Configuration comparison between backup runs
   - Backup compression (ZIP files for storage efficiency)
   - Progress bars using `tqdm`
   - Logging to file with the `logging` module
   - Database storage of backup metadata
   - Web interface to browse backups

---

## 💡 Production Readiness Checklist

Want to use this script in production? Consider these enhancements:

### 🟡 Intermediate Level (Coming Soon in Tutorials)

- [ ] **Configuration Comparison**: Show what changed between backups
- [ ] **Drift Detection**: Alert when running config differs from startup
- [ ] **Backup Compression**: ZIP files to reduce storage
- [ ] **Email Notifications**: Status reports sent to admins
- [ ] **Database Backend**: Store config metadata and versions in SQLite/PostgreSQL
- [ ] **Automated Cleanup**: Delete backups older than retention period
- [ ] **Conflict Resolution**: Handle failed backups with retry logic
- [ ] **Backup Verification**: Spot-check that backups are not corrupted
- [ ] **Version Tagging**: Mark backups with change reasons ("Pre-maintenance", "Post-change", etc.)
- [ ] **Selective Backup**: Backup only specific devices or device types
- [ ] **Change Tracking**: Log when and why configs changed based on Git commits
- [ ] **Config Sanitization**: Remove sensitive data (passwords, private keys) before backup

### 🔴 Expert Level (Coming Soon in Tutorials)

- [ ] **GitOps Integration**: Auto-commit backups to Git, enable version control
- [ ] **Configuration Compliance**: Compare configs against standards/templates
- [ ] **Netbox Integration**: Backup device configs as source of truth
- [ ] **Event-Driven Backup**: Trigger immediately after detected changes
- [ ] **Distributed Backup**: Multi-location, replicated backup storage
- [ ] **Automated Remediation**: Detect drift and auto-remediate deviations
- [ ] **Change Request Integration**: ServiceNow tickets trigger backups
- [ ] **Audit Trail**: Full chain-of-custody for who accessed/modified backups
- [ ] **API Exposures**: REST API to query and restore backups
- [ ] **Machine Learning**: Anomaly detection for unexpected config changes
- [ ] **Multi-Vendor Support**: Backup Cisco, Arista, Juniper, Palo Alto configs
- [ ] **Container Deployment**: Docker-based scheduled backup service
- [ ] **Testing & Validation**: Automated tests verify backup integrity
- [ ] **Cost Optimisation**: Deduplication and incremental backups

These topics are covered in our **Intermediate** and **Expert** tutorials!

---

## 💬 What You've Accomplished

**Impressive!** You've evolved from a single-device automation script to a enterprise-grade configuration backup system. You now understand:

✅ File I/O and directory management  
✅ Configuration retrieval and archival  
✅ Timestamped backup organisation  
✅ Backup manifest creation  
✅ Error handling and recovery  
✅ Multi-device orchestration  
✅ Audit trail creation  

This foundation prepares you for configuration management, change detection, and compliance auditing at enterprise scale.

---

[← Back to Beginner Tutorials](./index.md) | [Continue to Intermediate →](../intermediate/index.md)
