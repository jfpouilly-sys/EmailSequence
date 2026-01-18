# Email Sequence Manager - Installation Manual

Complete installation guide for the Email Sequence Manager application (CLI and GUI).

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Python Installation](#python-installation)
4. [GUI Installation](#gui-installation)
5. [CLI Installation](#cli-installation)
6. [Outlook Configuration](#outlook-configuration)
7. [First-Time Setup](#first-time-setup)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Operating System:**
  - Windows 10 or later (recommended for Outlook integration)
  - Linux (Ubuntu 20.04+, Debian 11+, or equivalent)
  - macOS 11+ (limited Outlook support)

- **Python:** Version 3.8 or higher

- **RAM:** 2 GB minimum, 4 GB recommended

- **Disk Space:** 500 MB for Python and dependencies

- **Microsoft Outlook:**
  - Outlook 2016 or later (Windows only)
  - Outlook must be installed and configured with an active email account

### Recommended Requirements

- Windows 11
- Python 3.11+
- 8 GB RAM
- 1 GB free disk space
- Microsoft Outlook 365

---

## Installation Methods

Choose one of the following installation methods:

### Method 1: Standalone Executable (Windows Only) - Easiest

**For GUI users who don't want to install Python**

1. Download `EmailSequenceManager.exe` from releases
2. Place it in a folder (e.g., `C:\EmailSequence`)
3. Double-click to run
4. Skip to [First-Time Setup](#first-time-setup)

### Method 2: Python Installation - Recommended

**For both CLI and GUI usage, full control**

Continue reading this manual for complete instructions.

---

## Python Installation

### Windows

1. **Download Python**
   - Visit https://www.python.org/downloads/
   - Download Python 3.11 or later
   - **IMPORTANT:** Check "Add Python to PATH" during installation

2. **Verify Installation**
   ```bash
   python --version
   # Should show: Python 3.11.x or higher
   ```

3. **Install pip (if not included)**
   ```bash
   python -m ensurepip --upgrade
   ```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Verify
python3 --version
```

### macOS

```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org

# Verify
python3 --version
```

---

## GUI Installation

### Step 1: Download/Clone Repository

**Option A: Download ZIP**
1. Download repository as ZIP
2. Extract to a folder (e.g., `C:\EmailSequence` or `~/EmailSequence`)

**Option B: Git Clone**
```bash
git clone https://github.com/yourusername/EmailSequence.git
cd EmailSequence
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
cd C:\EmailSequence
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd ~/EmailSequence
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install GUI requirements
pip install -r requirements-gui.txt

# This installs:
# - customtkinter (GUI framework)
# - Pillow (image handling)
# - tkcalendar (date pickers)
# - pandas, openpyxl (Excel handling)
# - PyYAML (configuration)
```

### Step 4: Verify Installation

```bash
# Test GUI launch
python run_gui.py
```

You should see the Email Sequence Manager window open.

---

## CLI Installation

### Step 1: Install Core Dependencies

```bash
# From repository root
pip install -r requirements.txt

# This installs:
# - pywin32 (Outlook integration on Windows)
# - pandas, openpyxl (data handling)
# - PyYAML (configuration)
# - python-dateutil (date handling)
```

### Step 2: Verify Installation

```bash
# Test CLI
python main.py --help
```

You should see the command-line help output.

---

## Outlook Configuration

### Windows Setup

1. **Verify Outlook Installation**
   - Open Outlook desktop application
   - Ensure it's configured with your email account
   - Send a test email to verify it works

2. **Enable Programmatic Access**
   - Go to File > Options > Trust Center > Trust Center Settings
   - Click "Programmatic Access"
   - Ensure "Never warn me about suspicious activity" is **NOT** checked
   - Allow access when prompted by the application

3. **Default Email Account**
   - The application uses your default Outlook account
   - To change: File > Account Settings > Set as Default

### Permission Prompts

When you first run the application:
- Outlook may show a security prompt
- Select "Allow access for 10 minutes" or "Always allow"
- This is normal and safe for your own scripts

### macOS/Linux Note

- Outlook integration requires Windows
- For macOS/Linux, you'll need to use alternative methods:
  - SMTP/IMAP direct connection (future feature)
  - Run via Windows VM
  - Use Windows machine remotely

---

## First-Time Setup

### 1. Create Project Structure

```bash
# Navigate to installation directory
cd C:\EmailSequence  # Windows
# or
cd ~/EmailSequence   # Linux/macOS

# Create required folders
mkdir -p templates logs data
```

### 2. Create Configuration Files

**Create `config.yaml`:**
```yaml
email:
  sender_name: "Your Name"
  subject_template: "Subject: {topic}"
  delay_between_sends: 5

sequence:
  followup_delays:
    followup_1: 3
    followup_2: 7
    followup_3: 14
  max_followups: 3

outlook:
  inbox_scan_days: 30
  folder_name: "Inbox"

logging:
  level: "INFO"
  file: "logs/sequence.log"
```

**Create `gui_config.yaml`:**
```yaml
paths:
  project_folder: "C:/EmailSequence"  # Or your path
  python_executable: "python"
  config_file: "config.yaml"
  contacts_file: "contacts.xlsx"
  templates_folder: "templates"
  logs_folder: "logs"

appearance:
  theme: "dark"
  color_scheme: "blue"
  window_width: 1200
  window_height: 800

behavior:
  auto_refresh_seconds: 30
  confirm_before_send: true
  show_notifications: true
```

### 3. Create Contacts File

**Create `contacts.xlsx`** with these columns:
- title (Mr, Ms, Dr, etc.)
- first_name
- last_name
- email
- company
- status (initially: "pending")

You can use Excel or the GUI's import feature to add contacts.

### 4. Create Email Templates

Create `templates/initial.html`:
```html
<!-- Subject: Partnership Opportunity - ISIT -->
<p>Dear {title} {last_name},</p>

<p>I hope this message finds you well.</p>

<p>I am reaching out to discuss a potential partnership opportunity between {company} and ISIT.</p>

<p>Best regards,<br>
{sender_name}</p>
```

Create similar files for:
- `templates/followup_1.html`
- `templates/followup_2.html`
- `templates/followup_3.html`

### 5. Test the Installation

**Test GUI:**
```bash
python run_gui.py
```

**Test CLI:**
```bash
python main.py --help
```

---

## Building Standalone Executable (Optional)

To create a standalone `.exe` file:

### Prerequisites

```bash
pip install pyinstaller
```

### Build Process

```bash
# Using the spec file
pyinstaller EmailSequence.spec

# Output will be in dist/EmailSequenceManager.exe
```

### Distribution

The executable can be copied to any Windows machine without Python installed:

1. Copy `dist/EmailSequenceManager.exe` to target machine
2. Create `gui_config.yaml` in same folder
3. Run the executable

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**
- Reinstall Python with "Add to PATH" checked
- Or add Python to PATH manually:
  - Windows: System Properties > Environment Variables > Path
  - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`

### Issue: "No module named 'customtkinter'"

**Solution:**
```bash
pip install --upgrade customtkinter
```

### Issue: "Outlook is not installed"

**Solution:**
- Install Microsoft Outlook desktop application
- GUI features will work without Outlook, but email sending won't

### Issue: "Permission denied" on Outlook

**Solution:**
- Run Outlook as administrator once
- Check Trust Center settings (see Outlook Configuration above)
- Disable antivirus temporarily to test

### Issue: GUI window doesn't open

**Solution:**
```bash
# Check for errors
python run_gui.py

# Try updating tkinter
sudo apt install python3-tk  # Linux
brew install python-tk       # macOS
```

### Issue: "ImportError: DLL load failed"

**Solution (Windows):**
- Install Microsoft Visual C++ Redistributable
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Issue: Excel file won't open

**Solution:**
```bash
# Reinstall openpyxl
pip install --upgrade openpyxl pandas
```

### Getting Help

1. Check logs in `logs/sequence.log`
2. Run with verbose output: `python run_gui.py --debug`
3. Check GitHub issues
4. Contact support with:
   - Python version (`python --version`)
   - Operating system
   - Error message
   - Log file

---

## Next Steps

After installation:

1. Read [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options
2. Read [GUI_MANUAL.md](GUI_MANUAL.md) for GUI usage instructions
3. Import your contacts
4. Customize email templates
5. Run a test sequence with a few contacts

---

## Uninstallation

### Remove Virtual Environment

```bash
# Windows
rmdir /s venv

# Linux/macOS
rm -rf venv
```

### Remove Application

Simply delete the EmailSequence folder.

### Clean Python Packages (Optional)

```bash
pip uninstall customtkinter Pillow pandas openpyxl PyYAML pywin32
```

---

## Version Information

- Application Version: 1.0.0
- Python Minimum: 3.8
- Recommended Python: 3.11+
- Last Updated: 2026-01-17
