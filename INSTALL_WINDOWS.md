# Email Sequence Automation System - Windows 11 Installation Guide

Complete installation guide for setting up the Email Sequence Automation System on Windows 11.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Python Installation](#python-installation)
4. [Microsoft Outlook Setup](#microsoft-outlook-setup)
5. [Application Installation](#application-installation)
6. [Configuration](#configuration)
7. [First Run](#first-run)
8. [Automated Scheduling](#automated-scheduling)
9. [Troubleshooting](#troubleshooting)
10. [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 11 (22H2 or later) or Windows 10 (21H2 or later)
- **Processor**: Intel Core i3 or equivalent
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 500 MB for application and dependencies
- **Display**: 1920x1080 minimum resolution

### Software Requirements
- Microsoft Outlook (Desktop version - part of Microsoft 365 or standalone)
- Python 3.8 or higher (3.11 or 3.12 recommended)
- Microsoft Excel (for viewing/editing contacts.xlsx)
- Internet connection (for initial setup and sending emails)

---

## Prerequisites Installation

### 1. Microsoft Office / Outlook

**Option A: Microsoft 365 Subscription** (Recommended)
1. Visit https://www.microsoft.com/microsoft-365
2. Subscribe to Microsoft 365 Personal or Business
3. Download and install Microsoft 365
4. Sign in with your Microsoft account
5. Ensure Outlook is configured with your email account

**Option B: Standalone Outlook**
1. Purchase Outlook 2021 or later from Microsoft Store
2. Install and activate
3. Configure with your email account

**Verify Outlook Installation:**
```powershell
# Run in PowerShell
Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*Outlook*" }
```

### 2. Check Windows Version

```powershell
# Run in PowerShell
winver
```

Ensure you're running Windows 11 build 22000 or later, or Windows 10 build 19041 or later.

---

## Python Installation

### Step 1: Download Python

1. Visit https://www.python.org/downloads/
2. Download **Python 3.12.x** (latest stable version)
3. **IMPORTANT**: Choose "Windows installer (64-bit)"

### Step 2: Install Python

1. Run the downloaded installer
2. **☑️ CRITICAL**: Check "Add python.exe to PATH"
3. Click "Install Now"
4. Wait for installation to complete
5. Click "Disable path length limit" if prompted (requires admin)
6. Click "Close"

### Step 3: Verify Python Installation

Open **Command Prompt** (Win+R → type `cmd` → Enter) and run:

```cmd
python --version
```

Should output: `Python 3.12.x` or similar

```cmd
pip --version
```

Should output: `pip 24.x.x from ...`

If these commands don't work, restart your computer and try again.

---

## Microsoft Outlook Setup

### 1. Configure Outlook Email Account

1. Open Microsoft Outlook
2. Go to **File → Add Account**
3. Enter your email address
4. Follow prompts to complete setup
5. Ensure emails can be sent and received

### 2. Configure Outlook for Automation

**Disable Security Prompts** (Optional, for easier automation):

⚠️ **Security Warning**: Only do this on your personal computer. This reduces security by allowing programs to send emails without prompting.

**Method 1: Via Registry** (Requires Administrator)

1. Press `Win+R`
2. Type `regedit` and press Enter
3. Navigate to:
   ```
   HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Security
   ```
   (If using Outlook 2019/2021, use `16.0`; for Outlook 2016, use `16.0`)

4. Right-click on **Security** → **New → DWORD (32-bit) Value**
5. Name it `PromptOOMSend`
6. Double-click and set value to `0`
7. Click OK
8. Restart Outlook

**Method 2: Via Trusted Add-ins** (Safer)

1. In Outlook, go to **File → Options → Trust Center → Trust Center Settings**
2. Click **Programmatic Access**
3. Select **Never warn me about suspicious activity**
4. Click OK

**Method 3: Click "Allow" When Prompted** (Most Secure)

- Simply click "Allow" and "Allow access for 10 minutes" each time the system sends emails
- This is the most secure option

### 3. Test Outlook COM Access

Open **PowerShell** and run:

```powershell
# Test Outlook automation
$outlook = New-Object -ComObject Outlook.Application
if ($outlook) {
    Write-Host "Outlook COM accessible - GOOD!" -ForegroundColor Green
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
} else {
    Write-Host "Outlook COM NOT accessible - Check installation" -ForegroundColor Red
}
```

---

## Application Installation

### Method 1: Automated Installation (Recommended)

1. **Download the Application**
   - Download the ZIP file from GitHub
   - Extract to `C:\EmailSequence`

2. **Run the Installer**

   Right-click **install_windows.bat** → **Run as Administrator**

   This will automatically:
   - Install Python dependencies
   - Initialize the system
   - Create necessary folders
   - Create desktop shortcuts

3. **Verify Installation**

   You should see:
   - ✓ Dependencies installed
   - ✓ System initialized
   - ✓ Desktop shortcuts created

### Method 2: Manual Installation

1. **Download and Extract**

   ```powershell
   # Create installation directory
   New-Item -Path "C:\EmailSequence" -ItemType Directory -Force
   cd C:\EmailSequence

   # Extract downloaded files here
   ```

2. **Install Python Dependencies**

   Open **Command Prompt** in the `C:\EmailSequence` folder:

   ```cmd
   cd C:\EmailSequence
   pip install -r requirements.txt
   ```

   This installs:
   - `pywin32>=306` - Windows COM automation for Outlook
   - `pandas>=2.0.0` - Excel file operations
   - `openpyxl>=3.1.0` - Excel file format support
   - `pyyaml>=6.0` - YAML configuration files
   - `click>=8.0.0` - Command-line interface

   **Expected output:**
   ```
   Successfully installed pywin32-306 pandas-2.1.4 openpyxl-3.1.2 pyyaml-6.0.1 click-8.1.7 ...
   ```

3. **Post-Install Configuration for pywin32**

   ```cmd
   python -m pywin32_postinstall -install
   ```

4. **Initialize the System**

   ```cmd
   python main.py init
   ```

   This creates:
   - `contacts.xlsx` - Contact database
   - `templates/` - Email template folder
   - `logs/` - Log file folder

---

## Configuration

### 1. Edit Configuration File

Open `config.yaml` in Notepad or your preferred text editor:

```yaml
# Email settings
sender_name: "Jean-François"           # ← Change to your name
default_subject: "Partnership Opportunity - ISIT"  # ← Change to your subject

# Sequence timing (in days)
followup_delays:
  - 3    # Days after initial send for followup_1
  - 7    # Days after initial send for followup_2
  - 14   # Days after initial send for followup_3

max_followups: 3

# Reply detection
inbox_scan_days: 30          # How far back to scan inbox
match_by: "conversation"     # "conversation" or "subject"

# Safety settings
send_delay_seconds: 5        # Pause between emails
dry_run: false               # Set to true for testing
```

**OR use the GUI Configuration Editor:**

```cmd
python gui_config.py
```

### 2. Customize Email Templates

Navigate to `templates/` folder and edit the HTML files:

- **initial.html** - First email template
- **followup_1.html** - First follow-up (sent after 3 days)
- **followup_2.html** - Second follow-up (sent after 7 days)
- **followup_3.html** - Third follow-up (sent after 14 days)

**Available placeholders:**
- `{title}` - Mr, Ms, Dr, etc.
- `{first_name}` - Contact's first name
- `{last_name}` - Contact's last name
- `{full_name}` - Full name (first + last)
- `{email}` - Contact's email
- `{company}` - Company name
- `{sender_name}` - Your name from config.yaml

**Example:**
```html
<p>Dear {title} {last_name},</p>
<p>I hope this email finds you well at {company}...</p>
<p>Best regards,<br>{sender_name}</p>
```

### 3. Add Contacts

**Option A: Edit Excel File**

1. Open `contacts.xlsx` in Microsoft Excel
2. Add rows with the following columns:
   - `title` - Mr, Ms, Dr, etc.
   - `first_name` - Contact's first name
   - `last_name` - Contact's last name
   - `email` - Email address
   - `company` - Company name
   - `status` - Set to `pending` for new contacts
3. Save and close Excel

**Option B: Use GUI**

```cmd
python gui_main.py
```

Click **Add Contact** button and fill in the form.

**Option C: Use CLI**

```cmd
python main.py add --email "john@company.com" --first-name "John" --last-name "Doe" --company "Acme Corp" --title "Mr"
```

---

## First Run

### 1. Test with Dry Run

**CLI Method:**
```cmd
python main.py send --dry-run
```

**GUI Method:**
1. Run `python gui_main.py`
2. Ensure "Dry Run" is enabled in config
3. Click "Send Initial"

**What happens in dry run:**
- Emails open in Outlook windows (not sent)
- You can review each email
- Close the windows when done
- No changes to contact status

### 2. Send First Real Email

**⚠️ Important: Disable dry run first**

Edit `config.yaml`:
```yaml
dry_run: false
```

**CLI Method:**
```cmd
python main.py send
```

**GUI Method:**
1. Run `python gui_main.py`
2. Ensure "Dry Run" is disabled
3. Click "Send Initial"
4. Confirm the action

**What happens:**
- Emails are sent via Outlook
- Each contact's status changes to `sent`
- 5-second delay between emails
- Results shown in log

### 3. Check for Replies

```cmd
python main.py check
```

Or use GUI: Click **Check Replies**

### 4. Send Follow-ups

```cmd
python main.py followup
```

Or use GUI: Click **Send Follow-ups**

### 5. View Status

```cmd
python main.py status
```

Or use GUI: Click **Refresh Status**

---

## Automated Scheduling

### Setup Windows Task Scheduler

**Option 1: PowerShell Script** (Recommended)

1. **Create PowerShell Script**

   Create `C:\EmailSequence\run_cycle.ps1`:

   ```powershell
   # Email Sequence Automation - Cycle Runner
   Set-Location "C:\EmailSequence"
   python main.py cycle
   ```

2. **Create Scheduled Task**

   Run **PowerShell as Administrator** and execute:

   ```powershell
   # Create the scheduled task action
   $Action = New-ScheduledTaskAction `
       -Execute "powershell.exe" `
       -Argument "-ExecutionPolicy Bypass -File C:\EmailSequence\run_cycle.ps1" `
       -WorkingDirectory "C:\EmailSequence"

   # Create trigger - runs every 30 minutes
   $Trigger = New-ScheduledTaskTrigger `
       -Once `
       -At (Get-Date).Date `
       -RepetitionInterval (New-TimeSpan -Minutes 30) `
       -RepetitionDuration ([TimeSpan]::MaxValue)

   # Create settings
   $Settings = New-ScheduledTaskSettingsSet `
       -StartWhenAvailable `
       -DontStopOnIdleEnd `
       -AllowStartIfOnBatteries `
       -DontStopIfGoingOnBatteries

   # Register the task
   Register-ScheduledTask `
       -TaskName "EmailSequenceCycle" `
       -Action $Action `
       -Trigger $Trigger `
       -Settings $Settings `
       -Description "Automatically check replies and send follow-ups every 30 minutes" `
       -User $env:USERNAME

   Write-Host "Task created successfully!" -ForegroundColor Green
   Write-Host "The email sequence will run every 30 minutes automatically." -ForegroundColor Green
   ```

3. **Verify Task Creation**

   ```powershell
   Get-ScheduledTask -TaskName "EmailSequenceCycle"
   ```

**Option 2: Task Scheduler GUI**

1. Press `Win+R` → type `taskschd.msc` → Enter
2. Click **Create Task** (not Basic Task)
3. **General tab:**
   - Name: `EmailSequenceCycle`
   - Description: `Check replies and send follow-ups`
   - Select: **Run whether user is logged on or not**
   - Check: **Do not store password**

4. **Triggers tab:**
   - Click **New**
   - Begin the task: **On a schedule**
   - Settings: **Daily**
   - Start: Today's date, 9:00 AM
   - **Advanced settings:**
     - ☑️ Repeat task every: **30 minutes**
     - For a duration of: **Indefinitely**
   - Click OK

5. **Actions tab:**
   - Click **New**
   - Action: **Start a program**
   - Program/script: `python`
   - Add arguments: `main.py cycle`
   - Start in: `C:\EmailSequence`
   - Click OK

6. **Conditions tab:**
   - **Uncheck** "Start the task only if the computer is on AC power"

7. **Settings tab:**
   - ☑️ Allow task to be run on demand
   - ☑️ Run task as soon as possible after a scheduled start is missed
   - If the task fails, restart every: **10 minutes**

8. Click **OK** to save

### Test Scheduled Task

```powershell
# Run the task manually to test
Start-ScheduledTask -TaskName "EmailSequenceCycle"

# Check if it ran successfully
Get-ScheduledTaskInfo -TaskName "EmailSequenceCycle"
```

### Monitor Scheduled Task

Check logs at `C:\EmailSequence\logs\sequence.log`

```cmd
# View last 20 lines of log
powershell Get-Content C:\EmailSequence\logs\sequence.log -Tail 20
```

---

## Troubleshooting

### Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Reinstall Python
2. **☑️ Check "Add Python to PATH"**
3. Restart computer
4. Or use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe`

### Outlook Not Accessible

**Error:** `Could not connect to Microsoft Outlook`

**Solutions:**
1. Ensure Outlook is **running** (open the application)
2. Verify Outlook is configured with an email account
3. Try restarting Outlook
4. Run command prompt as **Administrator**
5. Reinstall pywin32:
   ```cmd
   pip uninstall pywin32
   pip install pywin32
   python -m pywin32_postinstall -install
   ```

### Excel File Locked

**Error:** `Cannot save to contacts.xlsx - file is locked`

**Solution:**
- Close `contacts.xlsx` in Excel
- The system will auto-retry after 5 seconds
- If problem persists, restart computer

### Security Prompts

**Issue:** Outlook asks for permission every time

**Solutions:**
1. Click "Allow" and select "Allow access for 10 minutes"
2. Use registry method (see [Outlook Setup](#microsoft-outlook-setup))
3. Add application to antivirus whitelist

### ImportError for win32com

**Error:** `ImportError: No module named 'win32com'`

**Solution:**
```cmd
pip install pywin32
python -m pywin32_postinstall -install
```

### Template Not Found

**Error:** `Template not found: initial.html`

**Solution:**
1. Verify `templates/` folder exists
2. Check that template files exist:
   - `templates/initial.html`
   - `templates/followup_1.html`
   - `templates/followup_2.html`
   - `templates/followup_3.html`
3. Check file extensions are `.html` (not `.txt`)

### Emails Not Sending

**Possible causes:**
1. **Dry run mode enabled** - Check `config.yaml`, set `dry_run: false`
2. **Outlook offline** - Click Send/Receive in Outlook
3. **No internet** - Check network connection
4. **Email server issues** - Check Outlook manually
5. **No pending contacts** - Verify contacts have `status='pending'`

### No Replies Detected

**Solutions:**
1. Increase `inbox_scan_days` in `config.yaml`
2. Verify contact replied to the same email thread
3. Check Outlook inbox manually
4. Try `match_by: "subject"` instead of `"conversation"`

### Scheduled Task Not Running

**Check:**
1. Task Scheduler → Find "EmailSequenceCycle"
2. Right-click → **Run** (test manually)
3. Check **Last Run Result** column
4. Review **History** tab
5. Ensure Outlook is configured to start with Windows:
   - Outlook → File → Options → Advanced → Start Outlook automatically

**Common issues:**
- Computer in sleep mode (disable sleep during work hours)
- User not logged in (use "Run whether user is logged on or not")
- Python not in PATH for system account (use full path to python.exe)

---

## Package List Reference

### Required Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| pywin32 | ≥306 | Windows COM automation (Outlook integration) |
| pandas | ≥2.0.0 | Excel file operations and data manipulation |
| openpyxl | ≥3.1.0 | Read/write Excel .xlsx files |
| pyyaml | ≥6.0 | Parse YAML configuration files |
| click | ≥8.0.0 | Command-line interface framework |

### Built-in Python Packages (No Installation Needed)

- `tkinter` - GUI framework (included with Python on Windows)
- `threading` - Multi-threading support
- `datetime` - Date and time operations
- `logging` - Activity logging
- `os` - File system operations
- `sys` - System operations
- `time` - Time delays

### Windows Components

- **Microsoft Outlook** (Desktop version)
  - Part of Microsoft 365 or standalone
  - Versions supported: Outlook 2016, 2019, 2021, Microsoft 365

- **Microsoft Excel** (Desktop version)
  - For viewing/editing contacts.xlsx
  - Part of Microsoft 365 or standalone
  - Versions supported: Excel 2016 or later

### Optional Components

- **Git for Windows** (if cloning from repository)
  - Download: https://git-scm.com/download/win

- **Visual Studio Code** (for editing code)
  - Download: https://code.visualstudio.com/

---

## Uninstallation

### Remove Application

```powershell
# Remove application folder
Remove-Item -Path "C:\EmailSequence" -Recurse -Force

# Remove scheduled task
Unregister-ScheduledTask -TaskName "EmailSequenceCycle" -Confirm:$false
```

### Uninstall Python Packages

```cmd
pip uninstall pywin32 pandas openpyxl pyyaml click -y
```

### Remove Python (Optional)

1. Settings → Apps → Installed apps
2. Find "Python 3.12.x"
3. Click **...** → **Uninstall**

---

## Advanced Configuration

### Custom Installation Path

If installing to a different location:

1. Change all paths in `config.yaml`
2. Update scheduled task paths
3. Update desktop shortcuts

### Multiple Email Accounts

To use different Outlook accounts:

1. Configure the desired account as **default** in Outlook
2. File → Account Settings → Set as Default
3. Restart Outlook

### Network Drive Storage

To store contacts.xlsx on a network drive:

```yaml
contacts_file: "Z:\\Shared\\EmailSequence\\contacts.xlsx"
```

Ensure network drive is always connected.

### Proxy Settings

If behind a corporate proxy, configure Python:

```cmd
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
```

Add to `run_cycle.ps1` for scheduled tasks.

---

## Security Best Practices

1. **Backup contacts.xlsx regularly** - Contains personal data
2. **Encrypt sensitive data** - Use Windows EFS or BitLocker
3. **Rotate logs** - Delete old logs to prevent data accumulation
4. **Use strong passwords** - For Outlook and Windows accounts
5. **Keep software updated** - Regularly update Python and dependencies
6. **Limit access** - Only authorized users should access the system
7. **Review emails** - Use dry run before going live
8. **Monitor logs** - Check for suspicious activity

---

## Support and Resources

### Documentation Files

- `README.md` - User guide and usage examples
- `INSTALL_WINDOWS.md` - This installation guide (you are here)
- `emailSequenceClaudeCode.md` - Technical specification

### Command Reference

```cmd
# Initialize system
python main.py init

# Configuration editor GUI
python gui_config.py

# Main application GUI
python gui_main.py

# CLI Commands
python main.py send [--dry-run]
python main.py check
python main.py followup [--dry-run]
python main.py cycle
python main.py status
python main.py add --email EMAIL --first-name NAME --last-name NAME
python main.py optout --email EMAIL
python main.py reset --email EMAIL
python main.py templates
```

### Log Files

- **Application logs**: `logs/sequence.log`
- **Scheduled task logs**: Task Scheduler → EmailSequenceCycle → History

### Getting Help

1. Check logs: `logs/sequence.log`
2. Review README.md
3. Search error messages online
4. Check Python/Outlook documentation

---

## Appendix: Installation Checklist

Print this checklist and check off each item:

- [ ] Windows 11 (or Windows 10) verified
- [ ] Microsoft Outlook installed and configured
- [ ] Email account set up in Outlook
- [ ] Python 3.8+ installed
- [ ] Python added to PATH
- [ ] pip working correctly
- [ ] Application downloaded to `C:\EmailSequence`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] pywin32 post-install completed
- [ ] System initialized (`python main.py init`)
- [ ] `config.yaml` customized
- [ ] Email templates customized
- [ ] Test contacts added to `contacts.xlsx`
- [ ] Dry run test successful
- [ ] First real email sent successfully
- [ ] Reply detection tested
- [ ] Windows Task Scheduler configured (optional)
- [ ] Desktop shortcuts created (optional)

**Installation Date:** _______________

**Installed By:** _______________

**Notes:** _______________________________________________

---

**Version:** 1.0.0
**Last Updated:** 2026-01-17
**Compatible with:** Windows 11, Windows 10 (21H2+)
