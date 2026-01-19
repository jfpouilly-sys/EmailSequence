# Email Sequence Automation - Package Dependencies

Complete list of all software packages and components required for the Email Sequence Automation System on Windows 11.

---

## System Software

### 1. Operating System

**Windows 11** (Recommended) or **Windows 10 21H2+**
- Editions supported: Home, Pro, Enterprise, Education
- Build: 22000 or later (Windows 11) or 19041+ (Windows 10)
- Architecture: x64 (64-bit)

**Verification:**
```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
```

---

### 2. Python

**Python 3.8.0 or higher** (Python 3.11 or 3.12 recommended)

- **Download:** https://www.python.org/downloads/
- **Installer:** Windows installer (64-bit)
- **Size:** ~30 MB download, ~100 MB installed
- **Installation Options:**
  - ☑️ **CRITICAL:** Add Python to PATH
  - ☑️ Install pip
  - ☑️ Install tcl/tk and IDLE (for tkinter GUI support)
  - ☑️ Python test suite
  - ☑️ py launcher

**Included with Python:**
- `pip` - Package installer
- `tkinter` - GUI framework (built-in on Windows)
- Standard library modules

**Verification:**
```cmd
python --version
pip --version
python -m tkinter
```

---

### 3. Microsoft Office Components

#### Microsoft Outlook (Desktop Version)

**Required for:** Email sending and inbox monitoring

**Supported versions:**
- Outlook 2016 (Build 16.0.x)
- Outlook 2019 (Build 16.0.x)
- Outlook 2021 (Build 16.0.x)
- Outlook for Microsoft 365 (Latest)

**Licensing options:**
- Microsoft 365 Personal/Family/Business (subscription)
- Office Home & Student 2021 (one-time purchase)
- Office Professional 2021 (one-time purchase)
- Standalone Outlook 2021

**Download:**
- Microsoft 365: https://www.microsoft.com/microsoft-365
- Standalone: https://www.microsoft.com/microsoft-365/outlook

**Size:** ~3-4 GB (full Microsoft 365 suite)

**Configuration required:**
- Email account must be set up
- Must be desktop version (not Outlook Web App)
- Must run on same machine as Python script

**Verification:**
```powershell
Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*Outlook*" }
```

#### Microsoft Excel (Desktop Version)

**Required for:** Viewing and editing contacts.xlsx

**Supported versions:**
- Excel 2016 or later
- Excel for Microsoft 365

**Note:** Same licensing as Outlook (part of Microsoft Office suite)

**Alternative:** Can use LibreOffice Calc or online Excel editors, but desktop Excel recommended

---

## Python Packages

### Core Dependencies (Required)

All packages listed in `requirements.txt`:

#### 1. pywin32

**Version:** ≥306 (Latest: 306)
**Purpose:** Windows COM automation - enables Python to control Outlook via COM interface
**License:** PSF (Python Software Foundation License)
**Size:** ~10 MB

**Installation:**
```cmd
pip install pywin32>=306
python -m pywin32_postinstall -install
```

**Provides:**
- `win32com.client` - COM object creation and automation
- `pythoncom` - COM threading support
- Windows API access

**Required for:**
- Sending emails via Outlook
- Scanning Outlook inbox
- Creating/reading email items

---

#### 2. pandas

**Version:** ≥2.0.0 (Latest: 2.1.4)
**Purpose:** Data manipulation and Excel file operations
**License:** BSD 3-Clause
**Size:** ~40 MB

**Installation:**
```cmd
pip install pandas>=2.0.0
```

**Provides:**
- DataFrame operations for contact management
- Excel file reading/writing
- Data filtering and selection
- CSV operations (backup/export)

**Dependencies (auto-installed):**
- `numpy` - Numerical computing
- `python-dateutil` - Date/time utilities
- `pytz` - Timezone support

**Required for:**
- Reading contacts.xlsx
- Writing updates to contacts.xlsx
- Filtering pending/active contacts
- Status reporting

---

#### 3. openpyxl

**Version:** ≥3.1.0 (Latest: 3.1.2)
**Purpose:** Read/write Excel 2010+ (.xlsx) files
**License:** MIT
**Size:** ~2 MB

**Installation:**
```cmd
pip install openpyxl>=3.1.0
```

**Provides:**
- Excel .xlsx format support for pandas
- Cell formatting preservation
- Workbook/worksheet operations

**Required for:**
- pandas Excel engine (read_excel/to_excel)
- Preserving Excel formatting in contacts.xlsx

---

#### 4. pyyaml

**Version:** ≥6.0 (Latest: 6.0.1)
**Purpose:** YAML configuration file parsing
**License:** MIT
**Size:** ~1 MB

**Installation:**
```cmd
pip install pyyaml>=6.0
```

**Provides:**
- YAML file parsing (yaml.safe_load)
- YAML file writing (yaml.dump)
- Configuration validation

**Required for:**
- Reading config.yaml
- Saving configuration from GUI editor

---

#### 5. click

**Version:** ≥8.0.0 (Latest: 8.1.7)
**Purpose:** Command-line interface framework
**License:** BSD 3-Clause
**Size:** ~1 MB

**Installation:**
```cmd
pip install click>=8.0.0
```

**Provides:**
- CLI command decoration (@click.command)
- Argument/option parsing
- Colored terminal output
- User input prompts

**Required for:**
- main.py CLI commands
- Interactive command-line interface
- Help documentation generation

---

### Built-in Python Modules (No Installation Required)

These are included with Python standard library:

#### GUI and Interface
- **tkinter** - GUI framework (Tk/Tcl bindings)
- **tkinter.ttk** - Themed widgets
- **tkinter.scrolledtext** - Scrolled text widget
- **tkinter.messagebox** - Dialog boxes
- **tkinter.filedialog** - File/folder dialogs

#### System and File Operations
- **os** - Operating system interface
- **sys** - System-specific parameters
- **pathlib** - Object-oriented filesystem paths
- **shutil** - High-level file operations

#### Data Handling
- **datetime** - Date and time operations
- **time** - Time access and conversions
- **typing** - Type hints (Optional, dict, list)

#### Logging and Threading
- **logging** - Flexible event logging
- **threading** - Thread-based parallelism

#### Other
- **yaml** - Provided by pyyaml package
- **json** - JSON encoder/decoder (if needed)

---

## Complete Installation Commands

### Quick Install (All at Once)

```cmd
# Install all dependencies
pip install -r requirements.txt

# Post-install configuration for pywin32
python -m pywin32_postinstall -install
```

### Individual Package Installation

```cmd
# Install packages one by one
pip install pywin32>=306
pip install pandas>=2.0.0
pip install openpyxl>=3.1.0
pip install pyyaml>=6.0
pip install click>=8.0.0

# Post-install for pywin32
python -m pywin32_postinstall -install
```

### Upgrade Existing Packages

```cmd
# Upgrade all packages to latest versions
pip install --upgrade -r requirements.txt
```

### Verify Installation

```cmd
# List all installed packages
pip list

# Check specific package
pip show pywin32
pip show pandas
```

---

## Dependency Tree

```
Email Sequence Application
│
├── Python 3.8+ (Required)
│   ├── tkinter (built-in) → GUI
│   ├── datetime (built-in) → Date/time operations
│   ├── logging (built-in) → Activity logging
│   ├── threading (built-in) → Background tasks
│   └── os/sys (built-in) → File operations
│
├── pywin32 ≥306 (Required)
│   └── Outlook COM automation
│
├── pandas ≥2.0.0 (Required)
│   ├── numpy (auto-installed)
│   ├── python-dateutil (auto-installed)
│   └── pytz (auto-installed)
│   └── Contact database operations
│
├── openpyxl ≥3.1.0 (Required)
│   └── Excel .xlsx format support
│
├── pyyaml ≥6.0 (Required)
│   └── Configuration file parsing
│
└── click ≥8.0.0 (Required)
    └── CLI interface

External Requirements:
├── Microsoft Outlook (Desktop) - Email operations
└── Microsoft Excel (Desktop) - Contact editing
```

---

## Disk Space Requirements

### Application Files
- Python source code: ~50 KB
- Templates: ~20 KB
- Configuration: ~5 KB
- Documentation: ~200 KB
- **Total:** ~300 KB

### Python and Packages
- Python 3.12 installation: ~100 MB
- pywin32: ~10 MB
- pandas + dependencies: ~50 MB
- openpyxl: ~2 MB
- pyyaml: ~1 MB
- click: ~1 MB
- **Total:** ~165 MB

### Data and Logs
- contacts.xlsx: ~100 KB (50 contacts)
- Logs: ~10 MB (estimated for 1 year)
- **Total:** ~10 MB

### Microsoft Office
- Microsoft 365 (full suite): ~3-4 GB
- Standalone Outlook: ~2-3 GB

### **Grand Total:** ~4.5 GB (including Microsoft Office)

---

## Network Requirements

### Initial Installation
- Python download: ~30 MB
- pip packages: ~60 MB
- **Total download:** ~90 MB

### Runtime
- Minimal bandwidth for email sending
- Internet connection required for:
  - Sending emails via Outlook
  - Receiving emails
  - Syncing with email server

### Offline Operation
- Can run offline if Outlook is in cached mode
- Contacts database is local
- No cloud dependencies

---

## Optional Components

### Development Tools

#### Git for Windows
- **Purpose:** Version control, clone repository
- **Download:** https://git-scm.com/download/win
- **Size:** ~50 MB
- **License:** GPL v2

```cmd
# Clone repository
git clone https://github.com/yourusername/EmailSequence.git
```

#### Visual Studio Code
- **Purpose:** Code editing, development
- **Download:** https://code.visualstudio.com/
- **Size:** ~100 MB
- **License:** MIT

**Recommended Extensions:**
- Python (Microsoft)
- YAML (Red Hat)
- Excel Viewer

#### Windows Terminal
- **Purpose:** Modern terminal with tabs
- **Download:** Microsoft Store
- **Size:** ~30 MB
- **License:** MIT

---

## Package Alternatives

### For Non-Windows Systems

If adapting for Linux/macOS, replace:

| Windows Package | Alternative | Purpose |
|----------------|-------------|---------|
| pywin32 | python-email + smtplib | Email sending (no COM) |
| Microsoft Outlook | Thunderbird + IMAP | Email client |
| openpyxl | Same | Cross-platform Excel support |
| tkinter | Same | Cross-platform GUI (requires tk) |

### Lightweight Alternatives

For minimal installations:

- **Instead of pandas:** Use `csv` module (Python built-in)
- **Instead of openpyxl:** Use CSV format for contacts
- **Instead of tkinter:** CLI-only mode (already supported)

---

## Version Compatibility Matrix

| Component | Minimum Version | Recommended | Maximum Tested |
|-----------|----------------|-------------|----------------|
| Windows | 10 (21H2) | 11 (22H2+) | 11 (23H2) |
| Python | 3.8.0 | 3.12.x | 3.12.x |
| pywin32 | 306 | 306 | 306 |
| pandas | 2.0.0 | 2.1.4 | 2.2.x |
| openpyxl | 3.1.0 | 3.1.2 | 3.1.x |
| pyyaml | 6.0 | 6.0.1 | 6.0.x |
| click | 8.0.0 | 8.1.7 | 8.1.x |
| Outlook | 2016 | 365 (latest) | 365 (latest) |

---

## Update and Maintenance

### Update Python Packages

```cmd
# Update all packages
pip install --upgrade pywin32 pandas openpyxl pyyaml click

# Update specific package
pip install --upgrade pandas
```

### Check for Outdated Packages

```cmd
# List outdated packages
pip list --outdated

# Show package information
pip show pandas
```

### Uninstall Packages

```cmd
# Uninstall specific package
pip uninstall pandas

# Uninstall all project packages
pip uninstall -r requirements.txt -y
```

---

## Security Considerations

### Package Security

All packages are from PyPI (Python Package Index):
- pywin32: Maintained by Microsoft contributors
- pandas: NumFOCUS sponsored project
- openpyxl: Active open-source project
- pyyaml: Established YAML parser
- click: Pallets Projects (same team as Flask)

### Verify Package Integrity

```cmd
# Check package hashes
pip hash pywin32
pip hash pandas

# Install with hash verification
pip install --require-hashes -r requirements.txt
```

### Keep Packages Updated

- Monitor security advisories
- Update packages regularly
- Subscribe to package update notifications

---

## License Summary

| Package | License | Commercial Use |
|---------|---------|----------------|
| Python | PSF License | ✓ Yes |
| pywin32 | PSF License | ✓ Yes |
| pandas | BSD 3-Clause | ✓ Yes |
| openpyxl | MIT | ✓ Yes |
| pyyaml | MIT | ✓ Yes |
| click | BSD 3-Clause | ✓ Yes |
| Microsoft Outlook | Proprietary | ✓ Yes (with license) |

**All open-source packages permit commercial use without restrictions.**

---

## Support and Resources

### Official Documentation

- **Python:** https://docs.python.org/3/
- **pywin32:** https://github.com/mhammond/pywin32
- **pandas:** https://pandas.pydata.org/docs/
- **openpyxl:** https://openpyxl.readthedocs.io/
- **pyyaml:** https://pyyaml.org/wiki/PyYAMLDocumentation
- **click:** https://click.palletsprojects.com/

### Package Repositories

- **PyPI (Python Package Index):** https://pypi.org/
- **Anaconda (alternative):** https://anaconda.org/

### Community Support

- **Stack Overflow:** Tag questions with `python`, `pywin32`, `pandas`
- **GitHub Issues:** Report bugs on respective package repositories
- **Python Discord:** https://discord.gg/python

---

**Version:** 1.0.0
**Last Updated:** 2026-01-17
**Maintained By:** Email Sequence Development Team
