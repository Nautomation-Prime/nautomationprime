---
title: Show Command to Excel
description: Learn to connect to Cisco devices with Netmiko, execute show commands with TextFSM parsing, and export structured data to Excel using pandas.
tags:
  - Beginner
  - Netmiko
  - TextFSM
  - Excel
  - pandas
  - Tutorial
---

## Send a Show Command and Export to Excel

## "Your First Python Network Automation Script — Explained Line-by-Line"

This tutorial teaches you how to build a simple but powerful automation script that:

1. Connects to a Cisco device using **Netmiko**
2. Executes a `show version` command
3. Automatically parses the output into structured data using **TextFSM**
4. Exports the data to an Excel file using **pandas**

**Best of all**: We'll explain *every single line* so you know exactly what's happening and why.

---

## 🎯 What You'll Learn

By the end of this tutorial, you'll understand:

- ✅ How to connect to network devices with Netmiko
- ✅ What TextFSM is and why it's essential for automation
- ✅ How to convert show command output to structured data
- ✅ How to export data to Excel using pandas
- ✅ Basic error handling for network connections
- ✅ How to avoid hardcoding passwords in scripts

---

## 📋 Prerequisites

### Required Knowledge

- Basic Python syntax (variables, dictionaries, functions)
- How to run Python scripts from the command line
- Basic understanding of Cisco show commands

### Required Software

```bash
# Install required Python libraries
pip install netmiko pandas openpyxl
```

### Required Access

- One Cisco device (IOS, IOS-XE, or NX-OS) with:
  - SSH enabled
  - Reachable IP address
  - Valid username and password

---

## 🔧 The Complete Script

Here's the full working code. We'll break down every line below.

```python
"""
Simple Netmiko Script: Show Version to Excel
Description: Connects to a Cisco device, runs 'show version', and exports to Excel
Author: Nautomation Prime
"""

# Import required libraries
from netmiko import ConnectHandler
import pandas as pd
import getpass

# Define device connection parameters
device = {
    'device_type': 'cisco_ios',           # Device platform
    'host': '192.168.1.1',                 # Device IP address
    'username': 'admin',                   # SSH username
    'password': getpass.getpass('Enter password: '),  # Prompt for password
    'secret': '',                          # Enable password (if needed)
}

# Main script execution
def main():
    """Main function to connect, collect data, and export to Excel"""
    
    print(f"Connecting to {device['host']}...")
    
    try:
        # Establish SSH connection to the device
        connection = ConnectHandler(**device)
        print(f"✓ Connected to {device['host']}")
        
        # Send show command with automatic TextFSM parsing
        print("Executing 'show version'...")
        output = connection.send_command('show version', use_textfsm=True)
        
        # Check if TextFSM parsing was successful
        if isinstance(output, list) and len(output) > 0:
            print(f"✓ Received structured data with {len(output)} row(s)")
            
            # Convert parsed data to pandas DataFrame
            df = pd.DataFrame(output)
            
            # Define output Excel filename
            excel_file = f"{device['host']}_show_version.xlsx"
            
            # Export DataFrame to Excel
            df.to_excel(excel_file, index=False, sheet_name='Show Version')
            print(f"✓ Data exported to: {excel_file}")
            
        else:
            print("⚠ TextFSM parsing failed or returned no data")
            print("Raw output:")
            print(output)
        
        # Close the SSH connection
        connection.disconnect()
        print("✓ Connection closed")
        
    except Exception as e:
        print(f"✗ Error occurred: {str(e)}")

# Script entry point
if __name__ == "__main__":
    main()
```

---

## 📖 Line-by-Line Explanation

Let's break down exactly what each line does:

### Import Statements

```python
from netmiko import ConnectHandler
```

**What it does**: Imports the `ConnectHandler` class from the Netmiko library.

**Why**: `ConnectHandler` is the main class that handles SSH connections to network devices. It knows how to communicate with dozens of different device types (Cisco, Arista, Juniper, etc.).

---

```python
import pandas as pd
```

**What it does**: Imports the pandas library and gives it the alias `pd`.

**Why**: Pandas is a data manipulation library. We use it to convert our parsed data (which will be a list of dictionaries) into a DataFrame, which can easily be exported to Excel. The `pd` alias is a universal convention that makes code easier to read.

---

```python
import getpass
```

**What it does**: Imports Python's built-in `getpass` module.

**Why**: This module provides a secure way to prompt users for passwords without displaying them on screen. This is much better than hardcoding passwords in your script!

---

### Device Configuration Dictionary

```python
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': getpass.getpass('Enter password: '),
    'secret': '',
}
```

**What it does**: Creates a dictionary containing all the information needed to connect to the device.

**Why**: Netmiko's `ConnectHandler` expects connection parameters in this dictionary format. Let's look at each key:

- **`device_type`**: Tells Netmiko what type of device it's connecting to. This determines which commands and prompts to expect.
  - Use `'cisco_ios'` for IOS and IOS-XE devices
  - Use `'cisco_nxos'` for Nexus switches
  - Use `'cisco_xr'` for IOS-XR routers
  
- **`host`**: The IP address or hostname of the device. Replace `'192.168.1.1'` with your device's IP.

- **`username`**: SSH username for authentication. Replace `'admin'` with your username.

- **`password`**: User password. The `getpass.getpass()` function prompts for a password securely without echoing it to the screen.

- **`secret`**: Enable password (used for `enable` mode). Leave as empty string (`''`) if your user is already in privileged mode or no enable password is required.

---

### Main Function Definition

```python
def main():
    """Main function to connect, collect data, and export to Excel"""
```

**What it does**: Defines a function called `main()` that contains all our automation logic.

**Why**: Wrapping code in a function is a best practice. It makes the code reusable, easier to test, and allows us to use the `if __name__ == "__main__"` pattern at the bottom.

The triple-quoted string is a **docstring** — it documents what the function does.

---

### User Feedback

```python
print(f"Connecting to {device['host']}...")
```

**What it does**: Prints a message to the console showing which device we're connecting to.

**Why**: User feedback is important! This lets you know the script is running and what it's doing. The `f` before the string makes it an **f-string**, which allows us to embed the device IP using `{device['host']}`.

---

### Error Handling Block

```python
try:
```

**What it does**: Starts a `try` block for error handling.

**Why**: Network operations can fail for many reasons (wrong password, device unreachable, timeout, etc.). The `try/except` block catches these errors so your script doesn't crash with a ugly error message. Instead, it will print a friendly error message.

---

### Establish SSH Connection

```python
connection = ConnectHandler(**device)
```

**What it does**: Creates an SSH connection to the device and stores it in the variable `connection`.

**Why**: This is where the magic happens! `ConnectHandler` receives our device dictionary and:

1. Establishes an SSH connection to the device
2. Logs in with the provided credentials
3. Detects the device prompt
4. Returns a connection object we can use to send commands

The `**device` syntax "unpacks" the dictionary, passing each key-value pair as a named parameter to `ConnectHandler`.

---

```python
print(f"✓ Connected to {device['host']}")
```

**What it does**: Prints a success message with a checkmark.

**Why**: Confirms the connection succeeded. If you see this message, authentication and connection were successful!

---

### Execute Show Command with TextFSM

```python
output = connection.send_command('show version', use_textfsm=True)
```

**What it does**: Sends the `show version` command to the device and stores the result in `output`.

**Why**: This is the core of the script! Here's what happens:

1. **`send_command('show version')`**: Sends the show command to the device
2. **`use_textfsm=True`**: Tells Netmiko to automatically parse the output using TextFSM

**What is TextFSM?**

TextFSM is a parsing engine that converts unstructured text output (like show commands) into structured data (lists and dictionaries).

For example, `show version` normally returns text like:

```cisco
Cisco IOS Software, Version 15.2(4)M3
...
uptime is 2 weeks, 3 days, 4 hours, 22 minutes
```

With TextFSM enabled, it becomes a Python list of dictionaries:

```python
[
    {
        'version': '15.2(4)M3',
        'hostname': 'Router1',
        'uptime': '2 weeks, 3 days, 4 hours, 22 minutes',
        'serial': ['FCZ1234A5BC']
        # ... more fields
    }
]
```

This structured data is much easier to work with in Python!

---

### Verify Parsing Success

```python
if isinstance(output, list) and len(output) > 0:
```

**What it does**: Checks if TextFSM parsing was successful.

**Why**: When `use_textfsm=True` works, it returns a **list of dictionaries**. If TextFSM fails (template doesn't exist for your device, or parsing failed), it returns the raw string output instead.

- **`isinstance(output, list)`**: Checks if `output` is a list (meaning TextFSM worked)
- **`len(output) > 0`**: Checks that the list isn't empty

If both conditions are true, we know we have structured data to work with.

---

```python
print(f"✓ Received structured data with {len(output)} row(s)")
```

**What it does**: Prints how many rows of data were received.

**Why**: For `show version`, you'll typically get 1 row (one dictionary). For commands like `show ip interface brief`, you'd get multiple rows (one per interface).

---

### Convert to pandas DataFrame

```python
df = pd.DataFrame(output)
```

**What it does**: Converts the list of dictionaries into a pandas DataFrame.

**Why**: A DataFrame is like a spreadsheet in Python. Pandas makes it incredibly easy to:

- Export to Excel, CSV, JSON, etc.
- Filter and manipulate data
- Combine data from multiple devices

When you pass a list of dictionaries to `pd.DataFrame()`, pandas automatically:

- Uses dictionary keys as column headers
- Creates rows from each dictionary's values

---

### Define Output Filename

```python
excel_file = f"{device['host']}_show_version.xlsx"
```

**What it does**: Creates a filename based on the device IP address.

**Why**: This makes it easy to identify which device the data came from. For example, if the device IP is `192.168.1.1`, the filename will be `192.168.1.1_show_version.xlsx`.

---

### Export to Excel

```python
df.to_excel(excel_file, index=False, sheet_name='Show Version')
```

**What it does**: Exports the DataFrame to an Excel file.

**Why**: This is the final step! Let's break down the parameters:

- **`excel_file`**: The filename we specified above
- **`index=False`**: Don't include the DataFrame index (row numbers) in the Excel file. We don't need them.
- **`sheet_name='Show Version'`**: Names the Excel worksheet "Show Version" instead of the default "Sheet1"

The file is saved in the same directory where you run the script.

---

```python
print(f"✓ Data exported to: {excel_file}")
```

**What it does**: Confirms the Excel file was created successfully.

**Why**: Lets you know where to find your output file!

---

### Handle Parsing Failure

```python
else:
    print("⚠ TextFSM parsing failed or returned no data")
    print("Raw output:")
    print(output)
```

**What it does**: If TextFSM parsing didn't work, print a warning and show the raw text output.

**Why**: This helps with troubleshooting. If TextFSM doesn't have a template for your specific command or device, you'll see the raw output here and can work with it as plain text.

---

### Close Connection

```python
connection.disconnect()
print("✓ Connection closed")
```

**What it does**: Closes the SSH connection to the device.

**Why**: Always clean up your connections! This frees up resources on both your computer and the network device. It's especially important in production where devices have connection limits.

---

### Exception Handling

```python
except Exception as e:
    print(f"✗ Error occurred: {str(e)}")
```

**What it does**: If any error occurs in the `try` block, this catches it and prints a friendly error message.

**Why**: Instead of seeing a confusing Python traceback, you'll see a clear error message. Common errors:

- `Authentication failed` — Wrong username or password
- `TCP connection to device failed` — Device unreachable or SSH not enabled
- `Connection timeout` — Network connectivity issue

---

### Script Entry Point

```python
if __name__ == "__main__":
    main()
```

**What it does**: Runs the `main()` function when the script is executed directly.

**Why**: This is a Python best practice. The condition `if __name__ == "__main__"` is only true when you run the script directly (not when importing it as a module). This pattern allows your code to be:

- Run as a script: `python script.py`
- Imported by other scripts without automatically executing

---

## 🚀 How to Run the Script

### Step 1: Save the Script

Save the complete script to a file, e.g., `show_version_to_excel.py`

### Step 2: Edit Device Parameters

Update the `device` dictionary with your device information:

```python
device = {
    'device_type': 'cisco_ios',  # Change if needed (cisco_nxos, etc.)
    'host': '10.1.1.1',          # Your device IP
    'username': 'your_username', # Your username
    'password': getpass.getpass('Enter password: '),
    'secret': '',
}
```

### Step 3: Run the Script

```bash
python show_version_to_excel.py
```

### Step 4: Enter Your Password

When prompted:

```bash
Enter password:
```

Type your password (it won't be displayed) and press Enter.

### Step 5: Check the Output

You should see:

```bash
Connecting to 10.1.1.1...
✓ Connected to 10.1.1.1
Executing 'show version'...
✓ Received structured data with 1 row(s)
✓ Data exported to: 10.1.1.1_show_version.xlsx
✓ Connection closed
```

The Excel file will be created in the same directory!

---

## 📊 Example Excel Output

After running the script, open the Excel file. You'll see columns like:

| hostname | version   | uptime             | serial      | model       | ... |
|----------|-----------|--------------------|-------------|-------------|-----|
| ROUTER1  | 15.2(4)M3 | 2 weeks, 3 days... | FCZ1234A5BC | CISCO2901   | ... |

The exact columns depend on the TextFSM template for your device type.

---

## 🔄 Trying Different Commands

Once you understand this script, try different show commands:

```python
# Instead of 'show version', try:
output = connection.send_command('show ip interface brief', use_textfsm=True)
excel_file = f"{device['host']}_interfaces.xlsx"
```

Popular commands that work well with TextFSM:

- `show ip interface brief`
- `show interfaces status`
- `show ip route`
- `show cdp neighbors detail`
- `show mac address-table`
- `show inventory`

**Tip**: Not all commands have TextFSM templates. Check available templates at: [https://github.com/networktocode/ntc-templates](https://github.com/networktocode/ntc-templates)

---

## 🐛 Troubleshooting

### "Module 'netmiko' not found"

**Solution**: Install the required libraries:

```bash
pip install netmiko pandas openpyxl
```

---

### "Authentication failed"

**Causes**:

- Wrong username or password
- Account locked
- SSH authentication method not supported

**Solution**:

- Verify credentials by manually SSH'ing to the device
- Check if the device requires key-based authentication
- Ensure your account has appropriate privileges

---

### "Connection timeout" or "TCP connection failed"

**Causes**:

- Device is unreachable
- SSH is not enabled on the device
- Firewall blocking connection
- Wrong IP address

**Solution**:

- Ping the device to verify reachability
- Verify SSH is enabled: `show ip ssh` on the device
- Check firewall rules
- Verify the IP address

---

### "TextFSM parsing failed"

**Causes**:

- No TextFSM template exists for your command + device type combination
- Device output format is non-standard

**Solution**:

- Use `use_textfsm=False` to get raw text output
- Check if your command is supported at [ntc-templates](https://github.com/networktocode/ntc-templates)
- Manually parse the raw text using string methods or regular expressions

Example without TextFSM:

```python
output = connection.send_command('show version')  # Raw string
# Then manually parse the string
```

---

### "Permission denied" or "Excel file is locked"

**Cause**: The Excel file is open in Excel.

**Solution**: Close the Excel file before running the script again.

---

## 🎓 Key Takeaways

Congratulations! You've built your first network automation script. You now understand:

✅ How Netmiko simplifies SSH connections to network devices  
✅ Why TextFSM is essential for converting text to structured data  
✅ How pandas makes data export effortless  
✅ The importance of error handling in network automation  
✅ Why you should never hardcode passwords  

---

## 🚀 Next Steps

Ready to build on this foundation? Here's your learning path:

**Continue with Beginner Concepts:**

1. [**Multi-Device Collection**](./multi-device-show-command.md) — Extend this script to work with multiple devices at once
2. [**Configuration Backup**](./multi-device-config-backup.md) — Learn to save and manage device configurations

    **Move to Intermediate Skills:**

3. [**Nornir Fundamentals**](../intermediate/nornir-fundamentals.md) — Understand frameworks that scale automation to thousands of devices
4. [**Enterprise Config Backup with Nornir**](../intermediate/enterprise-config-backup-nornir.md) — See how patterns scale to production

    **Study Production Code:**

5. [**Deep Dives Section**](../../deep-dives/index.md) — Review complete production scripts with line-by-line explanations
   - Start with [CDP Network Audit](../../deep-dives/cdp-audit.md) to see threading, error handling, and enterprise patterns
   - Then explore [Access Switch Audit](../../deep-dives/access-switch-audit.md) for parallel device collection

    **Ready to Deploy?**

6. [**Script Library**](../../../scripts/index.md) — Use production-ready tools built on these same concepts

---

## 💬 Questions or Feedback?

Found this tutorial helpful? Have questions or suggestions for improvement?

[Contact us](../../../about.md#contact) or check out our other resources!

---
