# Quick Start Guide - Lead Generator

**Version: 260128-2**

This guide will help you build and install Lead Generator for the first time.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **.NET 8 SDK**
   - Download: https://dotnet.microsoft.com/download/dotnet/8.0
   - Verify: `dotnet --version` (should show 8.x.x)

2. **PostgreSQL 15+**
   - Download: https://www.postgresql.org/download/windows/
   - During installation, remember the postgres user password
   - Default port: 5432

3. **Git** (to clone the repository)
   - Download: https://git-scm.com/download/win

### Optional (for development)

- **Visual Studio 2022** or **Visual Studio Code**
- **Microsoft Outlook** (required on workstations running Mail Service)

---

## ⚠️ FIRST TIME SETUP - Fix PowerShell Execution Policy

**If this is your first time**, Windows will block PowerShell scripts by default. You'll see an error like:

```
File cannot be loaded. The file is not digitally signed.
```

### Quick Fix (Choose One):

**Option A: Run Setup Script (Easiest)**

Simply double-click `setup.bat` or run:

```cmd
setup.bat
```

This will unblock all PowerShell scripts automatically.

**Option B: Manual Unblock (PowerShell)**

```powershell
# Open PowerShell as Administrator
cd path\to\EmailSequence

# Unblock all scripts
Get-ChildItem -Recurse -Filter "*.ps1" | Unblock-File
```

**Option C: Bypass for Current Session**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

📖 **For detailed instructions and troubleshooting, see:** `EXECUTION_POLICY.md`

---

## 🚀 Quick Installation (Automated)

The easiest way to build and install everything:

### Option 1: Using PowerShell (Recommended)

```powershell
# Open PowerShell as Administrator
cd path\to\EmailSequence

# Run complete installation
.\build.ps1 -Target install-all
```

Follow the prompts to:
- Build all projects
- Publish applications
- Setup database
- Install services

### Option 2: Using Batch File

```cmd
# Open Command Prompt as Administrator
cd path\to\EmailSequence

# Show available commands
make help

# Run complete installation
make install-all
```

---

## 📝 Step-by-Step Manual Installation

If you prefer to run each step individually:

### Step 1: Clean Previous Builds (Optional)

```powershell
.\build.ps1 -Target clean
```

Or:

```cmd
make clean
```

### Step 2: Restore Dependencies

```powershell
.\build.ps1 -Target restore
```

This downloads all NuGet packages needed for the solution.

### Step 3: Build the Solution

```powershell
.\build.ps1 -Target build
```

This compiles all 5 projects:
- ✅ LeadGenerator.Core
- ✅ LeadGenerator.Data
- ✅ LeadGenerator.Api
- ✅ LeadGenerator.Desktop
- ✅ LeadGenerator.MailService

### Step 4: Publish Applications

```powershell
.\build.ps1 -Target publish
```

This creates deployment-ready binaries in `.\publish\`:
- `publish\Api\` - API Server
- `publish\Desktop\` - WPF Desktop Client
- `publish\MailService\` - Windows Service

### Step 5: Setup Database

```powershell
.\build.ps1 -Target database-setup -DatabasePassword "YourPostgresPassword"
```

This will:
- Create `leadgenerator` database
- Create `leadgen_user` database user
- Create all tables with proper schema
- Seed default admin user (admin/Admin123!)
- Create indexes for performance

---

## 🎯 Build Targets Reference

The build system supports the following targets (like Makefile):

| Target | Description | Command |
|--------|-------------|---------|
| `help` | Show help and check prerequisites | `.\build.ps1 -Target help` |
| `clean` | Remove all build artifacts | `.\build.ps1 -Target clean` |
| `restore` | Restore NuGet packages | `.\build.ps1 -Target restore` |
| `build` | Build the solution | `.\build.ps1 -Target build` |
| `publish` | Publish all projects | `.\build.ps1 -Target publish` |
| `database-setup` | Initialize database | `.\build.ps1 -Target database-setup` |
| `install-all` | Complete installation | `.\build.ps1 -Target install-all` |
| `test` | Run tests | `.\build.ps1 -Target test` |

---

## 🔧 Build Options

### Configuration

Build in Debug or Release mode (default: Release):

```powershell
# Debug mode
.\build.ps1 -Target build -Configuration Debug

# Release mode (default)
.\build.ps1 -Target build -Configuration Release
```

### Custom Output Directory

Specify where to publish applications:

```powershell
.\build.ps1 -Target publish -OutputDir "C:\LeadGenerator\Deploy"
```

### Database Server

Specify PostgreSQL server (default: localhost):

```powershell
.\build.ps1 -Target database-setup -DatabaseServer "192.168.1.100" -DatabasePassword "password"
```

### API URL

Specify API server URL for installation:

```powershell
.\build.ps1 -Target install-all -ApiUrl "http://myserver:5000"
```

---

## 📦 After Installation

### 1. Start API Server

#### As Windows Service (Production)

```powershell
# Start the service
net start LeadGeneratorApi

# Check status
sc query LeadGeneratorApi

# View logs
Get-Content C:\LeadGenerator\Logs\api-*.log -Tail 50
```

#### As Console Application (Development)

```powershell
cd .\publish\Api
.\LeadGenerator.Api.exe
```

Access Swagger UI: http://localhost:5000/swagger

### 2. Launch Desktop Client

```powershell
cd .\publish\Desktop
.\LeadGenerator.Desktop.exe
```

**Default Login:**
- Username: `admin`
- Password: `Admin123!`

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

### 3. Install Mail Service (on workstations)

On each workstation that will send emails:

```powershell
cd scripts\install
.\install-mailservice.ps1 -ApiServerUrl "http://your-server:5000" -WorkstationId "WORKSTATION-01"
```

Requirements:
- Microsoft Outlook installed and configured
- Network access to API server

---

## 🐛 Troubleshooting

### Build Errors

**Issue:** "dotnet: command not found"
- **Solution:** Install .NET 8 SDK and restart terminal

**Issue:** Package restore fails
- **Solution:** Check internet connection, try: `dotnet nuget locals all --clear`

**Issue:** Build fails with errors
- **Solution:** Run `.\build.ps1 -Target clean` then rebuild

### Database Errors

**Issue:** "Connection refused" to PostgreSQL
- **Solution:** Ensure PostgreSQL service is running: `sc query postgresql-x64-15`

**Issue:** "password authentication failed"
- **Solution:** Verify PostgreSQL password, check connection string in `appsettings.json`

**Issue:** Database already exists
- **Solution:** Drop existing database: `psql -U postgres -c "DROP DATABASE leadgenerator;"`

### Service Installation Errors

**Issue:** "Access denied" when installing service
- **Solution:** Run PowerShell as Administrator

**Issue:** Service won't start
- **Solution:**
  - Check event viewer: `eventvwr`
  - Check service logs
  - Verify connection strings in config files

---

## 📁 Project Structure

```
LeadGenerator/
├── build.ps1              # PowerShell build script (Makefile-style)
├── make.bat               # Batch launcher for build.ps1
├── QUICKSTART.md          # This file
├── README.md              # Full documentation
├── CHANGELOG.md           # Version history
├── LeadGenerator.sln      # Visual Studio solution
├── src/                   # Source code
│   ├── LeadGenerator.Core/
│   ├── LeadGenerator.Data/
│   ├── LeadGenerator.Api/
│   ├── LeadGenerator.Desktop/
│   └── LeadGenerator.MailService/
├── scripts/               # Installation scripts
│   ├── database/          # SQL setup scripts
│   └── install/           # PowerShell install scripts
├── docs/                  # Documentation
└── publish/               # Published binaries (created after build)
    ├── Api/
    ├── Desktop/
    └── MailService/
```

---

## 🔐 Security Notes

1. **Change Default Password:** The default admin password (`Admin123!`) must be changed after first login
2. **Database Password:** Use a strong password for PostgreSQL
3. **JWT Secret:** Update the JWT key in `appsettings.json` before production
4. **Internal Network:** The application is designed for internal network use only
5. **Connection Strings:** Never commit passwords to source control

---

## 📚 Next Steps

After successful installation:

1. **Configure Mail Accounts**
   - Login to Desktop app
   - Go to Settings → Mail Accounts
   - Add Outlook accounts for each workstation

2. **Import Contacts**
   - Create contact list
   - Import from CSV file
   - 10 custom fields available per contact

3. **Create First Campaign**
   - Define email sequence steps
   - Use merge tags for personalization
   - Set sending schedule

4. **Monitor Results**
   - View Reports section
   - Track opens, replies, unsubscribes
   - Campaign statistics

---

## 📖 Additional Resources

- **Full Documentation:** `README.md`
- **Version History:** `CHANGELOG.md`
- **Build Instructions:** `docs/BUILD_INSTRUCTIONS.md`
- **API Documentation:** http://localhost:5000/swagger (after API starts)

---

## 🆘 Getting Help

If you encounter issues:

1. Check this QUICKSTART guide
2. Review README.md for detailed documentation
3. Check CHANGELOG.md for known issues
4. Review logs in `C:\LeadGenerator\Logs\`
5. Contact your system administrator

---

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] .NET 8 SDK installed (`dotnet --version`)
- [ ] PostgreSQL running (`sc query postgresql-x64-15`)
- [ ] Solution builds without errors (`.\build.ps1 -Target build`)
- [ ] Database created and seeded
- [ ] API Server starts successfully
- [ ] Can access Swagger UI (http://localhost:5000/swagger)
- [ ] Desktop client launches
- [ ] Can login with admin credentials
- [ ] Mail service installed on workstations (if applicable)

**Congratulations! Lead Generator is now installed and ready to use! 🎉**

---

*Lead Generator v260128-2 | Built with .NET 8 and PostgreSQL*
