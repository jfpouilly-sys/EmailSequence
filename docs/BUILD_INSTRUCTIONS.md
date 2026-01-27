# Build Instructions

This document provides step-by-step instructions for building the Lead Generator application.

## Prerequisites

Before building, ensure you have the following installed:

1. **.NET 8 SDK** (https://dotnet.microsoft.com/download/dotnet/8.0)
2. **Visual Studio 2022** (optional, but recommended for Windows development)
3. **PostgreSQL 15+** for database
4. **Git** for version control

## Building from Command Line

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LeadGenerator
```

### 2. Restore NuGet Packages

```bash
dotnet restore LeadGenerator.sln
```

### 3. Build the Solution

```bash
# Debug build
dotnet build LeadGenerator.sln -c Debug

# Release build
dotnet build LeadGenerator.sln -c Release
```

### 4. Run Tests (if available)

```bash
dotnet test LeadGenerator.sln
```

### 5. Publish for Deployment

```bash
# Publish API Server
dotnet publish src/LeadGenerator.Api -c Release -o ./publish/Api --self-contained false

# Publish Desktop Client
dotnet publish src/LeadGenerator.Desktop -c Release -o ./publish/Desktop --self-contained false

# Publish Mail Service
dotnet publish src/LeadGenerator.MailService -c Release -o ./publish/MailService --self-contained false
```

## Building with Visual Studio

1. Open `LeadGenerator.sln` in Visual Studio 2022
2. Select **Build → Build Solution** or press `Ctrl+Shift+B`
3. For publishing:
   - Right-click each project
   - Select **Publish**
   - Choose **Folder** as publish target
   - Configure output path and click **Publish**

## Build Configuration

### Debug Configuration
- Includes debugging symbols
- No optimizations
- Detailed logging enabled

```bash
dotnet build -c Debug
```

### Release Configuration
- Optimized for performance
- No debugging symbols
- Production-ready

```bash
dotnet build -c Release
```

## Platform-Specific Builds

### Windows (Required)
The Desktop Client and Mail Service require Windows due to WPF and Outlook COM Interop:

```bash
dotnet publish -c Release -r win-x64 --self-contained true
```

### Linux/Mac (API Only)
The API server can run on Linux/Mac:

```bash
# Linux
dotnet publish src/LeadGenerator.Api -c Release -r linux-x64

# macOS
dotnet publish src/LeadGenerator.Api -c Release -r osx-x64
```

## Database Setup

After building, set up the database:

```bash
# Navigate to scripts directory
cd scripts/database

# Run SQL scripts in order
psql -U postgres -f 001_create_database.sql
psql -U leadgen_user -d leadgenerator -f 002_create_tables.sql
psql -U leadgen_user -d leadgenerator -f 003_seed_admin_user.sql
psql -U leadgen_user -d leadgenerator -f 004_create_indexes.sql
```

## Troubleshooting Build Issues

### Issue: NuGet Package Restore Fails
**Solution:**
```bash
# Clear NuGet cache
dotnet nuget locals all --clear

# Restore packages
dotnet restore --force
```

### Issue: PostgreSQL Connection Error
**Solution:**
- Verify PostgreSQL is installed and running
- Check connection string in appsettings.json
- Ensure leadgen_user exists with correct permissions

### Issue: Outlook Interop Not Found
**Solution:**
- Install Microsoft Office/Outlook on the build machine
- Or use the NuGet package which is already included

### Issue: WPF Designer Errors
**Solution:**
- This is normal on non-Windows platforms
- Build will still succeed for API server
- Use Windows for full solution build

## Creating a Deployment Package

After successful build:

```bash
# Create deployment folder
mkdir deployment
mkdir deployment/server
mkdir deployment/workstation

# Copy server components
Copy-Item -Path publish/Api -Destination deployment/server/Api -Recurse
Copy-Item -Path scripts/database -Destination deployment/server/database -Recurse
Copy-Item -Path scripts/install/install-all.ps1 -Destination deployment/server/

# Copy workstation components
Copy-Item -Path publish/Desktop -Destination deployment/workstation/Desktop -Recurse
Copy-Item -Path publish/MailService -Destination deployment/workstation/MailService -Recurse
Copy-Item -Path scripts/install/install-desktop.ps1 -Destination deployment/workstation/
Copy-Item -Path scripts/install/install-mailservice.ps1 -Destination deployment/workstation/

# Create archive
Compress-Archive -Path deployment/* -DestinationPath LeadGenerator-v1.0.0.zip
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: '8.0.x'

    - name: Restore dependencies
      run: dotnet restore

    - name: Build
      run: dotnet build --configuration Release --no-restore

    - name: Test
      run: dotnet test --no-build --verbosity normal

    - name: Publish
      run: |
        dotnet publish src/LeadGenerator.Api -c Release -o ./publish/Api
        dotnet publish src/LeadGenerator.Desktop -c Release -o ./publish/Desktop
        dotnet publish src/LeadGenerator.MailService -c Release -o ./publish/MailService
```

## Next Steps

After successful build:

1. Review [Installation Guide](../README.md#installation)
2. Configure [appsettings.json](../README.md#configuration)
3. Run database migration scripts
4. Install and test on target environment

## Version Information

- .NET SDK: 8.0
- Entity Framework Core: 8.0
- PostgreSQL: 15+
- Target Framework: net8.0 / net8.0-windows

## Support

For build issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Review build logs for specific errors
4. Contact the development team

---

Last updated: 2026-01-27
