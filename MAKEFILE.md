# Makefile Reference - Lead Generator

Quick reference for the build system (Makefile-style for Windows)

## 🚀 Quick Commands

```powershell
# Show help
.\build.ps1 -Target help
make help

# Clean build artifacts
.\build.ps1 -Target clean
make clean

# Restore packages
.\build.ps1 -Target restore
make restore

# Build solution
.\build.ps1 -Target build
make build

# Publish applications
.\build.ps1 -Target publish
make publish

# Setup database
.\build.ps1 -Target database-setup
make database-setup

# Complete installation
.\build.ps1 -Target install-all
make install-all

# Run tests
.\build.ps1 -Target test
make test
```

## 📝 Target Description

| Target | Description | Dependencies |
|--------|-------------|--------------|
| `clean` | Remove bin, obj, and publish folders | None |
| `restore` | Download NuGet packages | None |
| `build` | Compile all projects | restore |
| `publish` | Create deployment binaries | restore, build |
| `database-setup` | Initialize PostgreSQL database | None |
| `install-all` | Full build and installation | all |
| `test` | Run unit tests | restore, build |
| `help` | Display help and check prerequisites | None |

## 🔧 Options

### Build Configuration

```powershell
# Debug build
.\build.ps1 -Target build -Configuration Debug

# Release build (default)
.\build.ps1 -Target build -Configuration Release
```

### Custom Output Directory

```powershell
.\build.ps1 -Target publish -OutputDir "C:\MyOutput"
```

### Database Configuration

```powershell
.\build.ps1 -Target database-setup `
    -DatabaseServer "localhost" `
    -DatabasePassword "YourPassword123"
```

### API Server URL

```powershell
.\build.ps1 -Target install-all `
    -ApiUrl "http://myserver:5000"
```

## 📦 Build Workflow

### Development Build

```powershell
# 1. Clean previous build
.\build.ps1 -Target clean

# 2. Build in Debug mode
.\build.ps1 -Target build -Configuration Debug

# 3. Run tests
.\build.ps1 -Target test
```

### Production Build

```powershell
# 1. Clean
.\build.ps1 -Target clean

# 2. Build and publish in Release mode
.\build.ps1 -Target publish -Configuration Release

# 3. Binaries will be in .\publish\
```

### First-Time Installation

```powershell
# Run complete installation (interactive)
.\build.ps1 -Target install-all
```

This will:
1. Clean old builds
2. Restore packages
3. Build solution
4. Publish applications
5. Setup database (if confirmed)
6. Install services (if confirmed)

## 🎯 Common Workflows

### "Just Build"

```powershell
.\build.ps1 -Target build
```

### "Build and Publish"

```powershell
.\build.ps1 -Target publish
```

### "Fresh Build"

```powershell
.\build.ps1 -Target clean
.\build.ps1 -Target build
```

### "Deploy to Server"

```powershell
# 1. Publish
.\build.ps1 -Target publish -Configuration Release

# 2. Copy to server
Copy-Item -Path .\publish\* -Destination \\server\LeadGenerator\ -Recurse -Force

# 3. Install on server
.\scripts\install\install-all.ps1 -ApiServerUrl "http://server:5000"
```

## 🐛 Troubleshooting

### Build Fails

```powershell
# Clean and retry
.\build.ps1 -Target clean
.\build.ps1 -Target build
```

### Package Restore Issues

```powershell
# Clear NuGet cache
dotnet nuget locals all --clear

# Restore again
.\build.ps1 -Target restore
```

### Database Connection Issues

```powershell
# Test PostgreSQL connection
psql -U postgres -h localhost -c "SELECT version();"

# Check service status
sc query postgresql-x64-15
```

## 📊 Output Structure

After running `publish`, you'll get:

```
publish/
├── Api/                      # API Server
│   ├── LeadGenerator.Api.exe
│   ├── appsettings.json
│   └── ...
├── Desktop/                  # Desktop Client
│   ├── LeadGenerator.Desktop.exe
│   ├── appsettings.json
│   └── ...
└── MailService/              # Mail Service
    ├── LeadGenerator.MailService.exe
    ├── appsettings.json
    └── ...
```

## 🔑 Environment Variables

You can set these environment variables to customize builds:

```powershell
# Set default configuration
$env:BUILD_CONFIGURATION = "Release"

# Set default output directory
$env:PUBLISH_DIR = "C:\Deploy\LeadGenerator"

# Use in build
.\build.ps1 -Target publish -Configuration $env:BUILD_CONFIGURATION
```

## 💡 Tips

1. **Run as Administrator** when installing services
2. **Use Release builds** for production
3. **Clean before important builds** to avoid stale artifacts
4. **Check prerequisites** with `.\build.ps1 -Target help`
5. **Review logs** in `C:\LeadGenerator\Logs\` after installation

## 📚 See Also

- `QUICKSTART.md` - First-time installation guide
- `README.md` - Full documentation
- `CHANGELOG.md` - Version history
- `docs/BUILD_INSTRUCTIONS.md` - Detailed build instructions

---

*For help: `.\build.ps1 -Target help`*
