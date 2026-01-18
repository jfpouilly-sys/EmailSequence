# Outlook Configuration & Setup Guide

This document explains how to configure and verify your Outlook connection for the Email Sequence Manager.

## Overview

The Email Sequence Manager uses **Windows COM Automation** to interact with Microsoft Outlook. This means:
- Outlook **must be installed** on your Windows machine
- Outlook **must be running** while the application executes
- The application runs **on your local machine**, not on a server
- Emails are sent **through your Outlook account** (the one configured in Outlook)

## Prerequisites

### Required Software
1. **Microsoft Outlook** (part of Microsoft Office)
   - Supported versions: Outlook 2016, 2019, 2021, Microsoft 365
   - Outlook must be installed and configured with at least one email account

2. **Python 3.8+** with `win32com` package
   ```bash
   pip install pywin32
   ```

3. **Windows Operating System**
   - Windows 10 or Windows 11 (64-bit recommended)

---

## Outlook Configuration

### 1. Verify Outlook Installation

#### Method A: Using the GUI
1. Run the GUI application
2. Go to the **Settings** tab
3. Click "Test Outlook Connection"
4. You should see: ✓ Connected to Microsoft Outlook

#### Method B: Using Python
```python
from src.outlook_manager import OutlookManager

try:
    outlook = OutlookManager()
    print("✓ Outlook connection successful!")
except Exception as e:
    print(f"✗ Outlook connection failed: {e}")
```

#### Method C: Using Command Line
```bash
python -c "from src.outlook_manager import OutlookManager; OutlookManager(); print('Success!')"
```

### 2. Where Outlook is Configured

The application **does NOT require any Outlook configuration in config files**. It automatically connects to:
- The currently running Outlook application
- The default email account configured in Outlook
- The default "Sent Items" and "Inbox" folders

**Location of Outlook Connection:**
- **File:** `src/outlook_manager.py`
- **Class:** `OutlookManager`
- **Method:** `__init__()` (lines 12-29)

```python
def __init__(self):
    """Initialize Outlook COM connection."""
    try:
        self.outlook = win32com.client.Dispatch('Outlook.Application')
        self.namespace = self.outlook.GetNamespace('MAPI')
    except Exception as e:
        raise ConnectionError("Could not connect to Microsoft Outlook...")
```

### 3. Which Email Account Is Used?

The application uses the **default email account** configured in Outlook:
1. Open Outlook
2. Go to File > Account Settings > Account Settings
3. The account marked with a checkmark is the default account
4. This is the account that will send all emails

**To change which account is used:**
1. In Outlook, go to File > Account Settings > Account Settings
2. Select the account you want to use
3. Click "Set as Default"
4. Restart Outlook

---

## API Calls and Logging

### Outlook COM API Calls

The application makes the following Outlook API calls:

| API Call | Purpose | File | Method |
|----------|---------|------|--------|
| `Dispatch('Outlook.Application')` | Connect to Outlook | outlook_manager.py | `__init__()` |
| `GetNamespace('MAPI')` | Get MAPI namespace | outlook_manager.py | `__init__()` |
| `CreateItem(0)` | Create new email (MailItem) | outlook_manager.py | `send_email()` |
| `mail.Send()` | Send email immediately | outlook_manager.py | `send_email()` |
| `mail.Display()` | Display email (dry run) | outlook_manager.py | `send_email()` |
| `mail.SaveAs(path, 3)` | Save as .msg file | outlook_manager.py | `send_email()` |
| `mail.DeferredDeliveryTime = time` | Schedule deferred send | outlook_manager.py | `send_email()` |
| `GetDefaultFolder(6)` | Get Inbox folder | outlook_manager.py | `get_recent_replies()` |
| `inbox.Items` | Get inbox messages | outlook_manager.py | `get_recent_replies()` |

### Detailed Logging

The application now provides **comprehensive logging** of all operations:

#### Log Prefixes
- `[OUTLOOK API]` - Outlook COM API calls
- `[FILE READ]` - File read operations
- `[FILE WRITE]` - File write operations
- `[FILE CREATE]` - File creation operations
- `[QUERY]` - Database queries
- `[UPDATE]` - Database updates
- `[ADD]` - Adding new records
- `[RENDER]` - Template rendering
- `[TEMPLATES]` - Template engine operations

#### Example Log Output
```
2026-01-18 10:30:15 - INFO - [OUTLOOK API] Initializing Outlook COM connection...
2026-01-18 10:30:15 - INFO - [OUTLOOK API] Calling win32com.client.Dispatch('Outlook.Application')
2026-01-18 10:30:16 - INFO - [OUTLOOK API] Calling GetNamespace('MAPI')
2026-01-18 10:30:16 - INFO - [OUTLOOK API] Successfully connected to Outlook version 16.0.5197.1000
2026-01-18 10:30:20 - INFO - [FILE READ] Loading contacts from: C:\email-sequence\contacts.xlsx
2026-01-18 10:30:20 - INFO - [FILE READ] Loaded 25 contacts from C:\email-sequence\contacts.xlsx
2026-01-18 10:30:25 - INFO - [TEMPLATES] Initializing template engine with folder: C:\email-sequence\templates
2026-01-18 10:30:25 - INFO - [TEMPLATES] Found 4 templates: followup_1, followup_2, followup_3, initial
2026-01-18 10:30:30 - INFO - [FILE READ] Loading template: C:\email-sequence\templates\initial.html
2026-01-18 10:30:30 - INFO - [FILE READ] Loaded template initial.html (2453 bytes, 2453 characters)
2026-01-18 10:30:35 - INFO - [RENDER] Rendering template 'initial' for john@company.com
2026-01-18 10:30:40 - INFO - [OUTLOOK API] Creating email: To=john@company.com, Subject='Partnership Opportunity', Mode=send
2026-01-18 10:30:40 - DEBUG - [OUTLOOK API] Calling outlook.CreateItem(0) to create MailItem
2026-01-18 10:30:41 - DEBUG - [OUTLOOK API] Email properties set (body length: 2453 chars)
2026-01-18 10:30:41 - INFO - [OUTLOOK API] Calling mail.Send() to send email immediately
2026-01-18 10:30:42 - INFO - [OUTLOOK API] Email sent successfully to john@company.com
2026-01-18 10:30:42 - INFO - [UPDATE] Updating contact john@company.com: status=sent, sequence_id=seq_20260118_103040
2026-01-18 10:30:45 - INFO - [FILE WRITE] Saving 25 contacts to: C:\email-sequence\contacts.xlsx
2026-01-18 10:30:45 - INFO - [FILE WRITE] Successfully saved to C:\email-sequence\contacts.xlsx (12345 bytes)
```

### Log File Location

Logs are written to:
- **Default location:** `logs/sequence.log`
- **Configurable in:** `config.yaml` → `log_file` setting

#### Viewing Logs

**Real-time monitoring (Windows PowerShell):**
```powershell
Get-Content -Path "logs\sequence.log" -Wait -Tail 50
```

**View last 100 lines:**
```bash
tail -n 100 logs/sequence.log
```

**Search logs for errors:**
```bash
grep "ERROR" logs/sequence.log
```

**Filter by operation type:**
```bash
# Show only Outlook API calls
grep "\[OUTLOOK API\]" logs/sequence.log

# Show only file operations
grep "\[FILE" logs/sequence.log
```

---

## File Operations Logging

### Files Read by the Application

| File Type | Path | Purpose | Logged As |
|-----------|------|---------|-----------|
| Contacts Database | `contacts.xlsx` | Contact information | `[FILE READ]` |
| Email Templates | `templates/*.html` | Email content | `[FILE READ]` |
| Configuration | `config.yaml` | System settings | (Standard Python loading) |
| Configuration | `gui_config.yaml` | GUI settings | (Standard Python loading) |

### Files Written by the Application

| File Type | Path | Purpose | Logged As |
|-----------|------|---------|-----------|
| Contacts Database | `contacts.xlsx` | Updated contact status | `[FILE WRITE]` |
| Log File | `logs/sequence.log` | Application logs | (Internal logging) |
| .msg Files | `msg_files/*.msg` | Draft emails | `[FILE WRITE]` |

### Example File Operation Logs

```
[FILE CREATE] Creating new contacts file: C:\email-sequence\contacts.xlsx
[FILE READ] Loading contacts from: C:\email-sequence\contacts.xlsx
[FILE READ] Loaded 25 contacts from C:\email-sequence\contacts.xlsx
[FILE WRITE] Saving 25 contacts to: C:\email-sequence\contacts.xlsx
[FILE WRITE] Successfully saved to C:\email-sequence\contacts.xlsx (12345 bytes)
[FILE WRITE] .msg output folder: C:\email-sequence\msg_files
[FILE WRITE] Saved .msg file: C:\email-sequence\msg_files\20260118_103045_john_at_company_com.msg (45678 bytes)
```

---

## Troubleshooting

### "Could not connect to Microsoft Outlook"

**Possible causes:**
1. Outlook is not installed
2. Outlook is not running
3. Outlook profile is not configured
4. Permissions issue

**Solutions:**
1. Ensure Outlook is installed and running
2. Configure at least one email account in Outlook
3. Try running as Administrator
4. Check antivirus/security software settings
5. Check logs for detailed error:
   ```bash
   grep "OUTLOOK API.*Failed" logs/sequence.log
   ```

### "Permission denied" errors

**Cause:** Outlook security settings or antivirus blocking COM automation

**Solutions:**
1. Add the application folder to antivirus exclusions
2. In Outlook: File > Options > Trust Center > Trust Center Settings > Programmatic Access
3. Check Windows Defender Application Control settings

### Emails not sending

**Check the logs:**
```bash
# Look for send operations
grep "\[OUTLOOK API\].*mail.Send()" logs/sequence.log

# Check for errors
grep "ERROR.*send" logs/sequence.log
```

**Verify:**
1. Outlook is online (not in offline mode)
2. Default account is properly configured
3. Email account has send permissions
4. Check Outlook's Outbox for stuck messages

### Cannot find .msg files

**Check the logs:**
```bash
grep "\[FILE WRITE\].*\.msg" logs/sequence.log
```

This will show you the exact path where .msg files were saved.

---

## Security Considerations

### Email Account Access
- The application has **full access** to the Outlook account that is logged in
- It can **read, send, and access** all emails in that account
- Use a **dedicated email account** for automation if possible

### Credentials Storage
- The application **does NOT store** email credentials
- Authentication is handled by Outlook itself
- The application only connects to the already-authenticated Outlook session

### COM Automation Security
- Windows may show security prompts for COM automation
- You may need to approve programmatic access in Outlook settings
- Antivirus software may flag COM automation as suspicious

---

## Advanced Configuration

### Change Outlook Profile

If you have multiple Outlook profiles:
1. Close Outlook completely
2. Open Control Panel > Mail > Show Profiles
3. Set the desired profile as default
4. Restart Outlook with the new profile
5. Run the application

### Use Different Send Account (Multiple Accounts)

If you have multiple accounts in one Outlook profile:
1. Open Outlook
2. File > Account Settings > Account Settings
3. Select the account you want to use as default
4. Click "Set as Default"
5. Restart Outlook

**Note:** The application always uses the default account.

---

## Summary

### Quick Checklist
- ✓ Outlook is installed and running
- ✓ At least one email account is configured in Outlook
- ✓ Default email account is set correctly
- ✓ `pywin32` package is installed (`pip install pywin32`)
- ✓ Application has permissions to access Outlook

### Where Things Are Configured
- **Outlook Connection:** `src/outlook_manager.py` - `OutlookManager.__init__()`
- **Email Sending:** `src/outlook_manager.py` - `OutlookManager.send_email()`
- **Log File Path:** `config.yaml` - `log_file` setting
- **Which Email Account:** Outlook > File > Account Settings (Default Account)

### Getting Help
If you encounter issues:
1. Check the logs: `logs/sequence.log`
2. Look for `[OUTLOOK API]` entries to see API calls
3. Look for `ERROR` entries for failures
4. Test Outlook connection: Run "Test Outlook Connection" in GUI Settings tab
