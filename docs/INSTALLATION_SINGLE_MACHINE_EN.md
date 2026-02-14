# Lead Generator - Single Machine Installation Guide

**Version**: 260128-2
**Language**: English

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Prerequisites Installation](#prerequisites-installation)
4. [Database Setup](#database-setup)
5. [API Server Installation](#api-server-installation)
6. [Desktop Client Installation](#desktop-client-installation)
7. [Mail Service Installation](#mail-service-installation)
8. [Post-Installation Configuration](#post-installation-configuration)
9. [Verification and Testing](#verification-and-testing)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the installation of all Lead Generator components on a single Windows machine. This configuration is ideal for:

- Small teams (1-5 users)
- Testing and evaluation environments
- Development setups

### Components Installed

| Component | Description | Port |
|-----------|-------------|------|
| PostgreSQL Database | Data storage | 5432 |
| LeadGenerator.Api | REST API Server | 5000 |
| LeadGenerator.Desktop | Windows Desktop Client | - |
| LeadGenerator.MailService | Email Processing Service | - |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SINGLE MACHINE                            │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  Desktop Client │───▶│   API Server    │                 │
│  │     (WPF)       │    │   (Port 5000)   │                 │
│  └─────────────────┘    └────────┬────────┘                 │
│                                  │                           │
│  ┌─────────────────┐             │                          │
│  │  Mail Service   │─────────────┼──────────┐               │
│  │(Windows Service)│             │          │               │
│  └────────┬────────┘             │          │               │
│           │                      ▼          │               │
│           │              ┌───────────────┐  │               │
│           │              │  PostgreSQL   │◀─┘               │
│           │              │  (Port 5432)  │                  │
│           │              └───────────────┘                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Microsoft       │                                        │
│  │ Outlook         │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## System Requirements

### Hardware

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk Space | 50 GB SSD | 100 GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Software

| Software | Version | Required |
|----------|---------|----------|
| Windows | 10/11 Pro or Server 2019+ | Yes |
| .NET Runtime | 8.0 | Yes |
| .NET Desktop Runtime | 8.0 | Yes |
| PostgreSQL | 15+ | Yes |
| Microsoft Outlook | 2016+ | Yes |

---

## Prerequisites Installation

### Step 1: Install .NET 8 Runtime

1. Download .NET 8 from: https://dotnet.microsoft.com/download/dotnet/8.0
2. Download both:
   - **.NET Runtime 8.0** (for API and Mail Service)
   - **.NET Desktop Runtime 8.0** (for Desktop Client)
3. Run both installers with Administrator privileges
4. Verify installation:

```powershell
dotnet --list-runtimes
```

Expected output should include:
```
Microsoft.AspNetCore.App 8.0.x
Microsoft.NETCore.App 8.0.x
Microsoft.WindowsDesktop.App 8.0.x
```

### Step 2: Install PostgreSQL

1. Download PostgreSQL 15+ from: https://www.postgresql.org/download/windows/
2. Run the installer as Administrator
3. During installation:
   - **Installation Directory**: `C:\Program Files\PostgreSQL\15`
   - **Data Directory**: `C:\Program Files\PostgreSQL\15\data`
   - **Password**: Set a strong password for the `postgres` user (remember this!)
   - **Port**: 5432 (default)
   - **Locale**: Default locale
4. Complete the installation
5. Verify PostgreSQL is running:

```powershell
# Open PowerShell as Administrator
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "SELECT version();"
```

### Step 3: Install Microsoft Outlook

1. Install Microsoft Office 2016 or later (Outlook required)
2. Configure at least one email account in Outlook
3. Ensure Outlook starts correctly and can send/receive emails
4. Close Outlook after verification

---

## Database Setup

### Step 1: Create Database and User

Open PowerShell as Administrator and navigate to the project directory:

```powershell
cd C:\LeadGenerator\Source
```

Connect to PostgreSQL and run the setup scripts:

```powershell
# Connect to PostgreSQL
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

Execute the following SQL commands (or run the script files):

```sql
-- Create database
CREATE DATABASE leadgenerator
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create application user
CREATE USER leadgen_user WITH PASSWORD 'ChangeThisPassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE leadgenerator TO leadgen_user;

-- Connect to the new database
\c leadgenerator

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO leadgen_user;
```

### Step 2: Create Tables

Run the table creation script:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\002_create_tables.sql"
```

### Step 3: Seed Initial Data

Run the seed script to create the default admin user:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\003_seed_admin_user.sql"
```

### Step 4: Create Indexes

Run the index creation script:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\004_create_indexes.sql"
```

---

## API Server Installation

### Step 1: Create Directory Structure

```powershell
# Run as Administrator
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Api"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Files"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Logs"
```

### Step 2: Build and Publish the API

Navigate to the source directory and publish:

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.Api -c Release -o C:\LeadGenerator\Api
```

### Step 3: Configure the API

Edit `C:\LeadGenerator\Api\appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=ChangeThisPassword123!"
  },
  "Jwt": {
    "Key": "YourSuperSecretKeyMustBeAtLeast32CharactersLongForSecurity!",
    "Issuer": "LeadGenerator",
    "Audience": "LeadGeneratorClients",
    "ExpirationMinutes": 480
  },
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files",
    "MaxFileSizeMB": 10,
    "AllowedExtensions": [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg"]
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "AllowedHosts": "*",
  "Urls": "http://localhost:5000"
}
```

**Important**: Change the following values:
- `Password` in ConnectionStrings (must match database user password)
- `Key` in Jwt section (use a strong, unique 32+ character key)

### Step 4: Install as Windows Service

```powershell
# Run as Administrator
sc.exe create "LeadGeneratorApi" binPath="C:\LeadGenerator\Api\LeadGenerator.Api.exe" start=auto displayname="Lead Generator API"
sc.exe description "LeadGeneratorApi" "Lead Generator REST API Server"

# Start the service
sc.exe start LeadGeneratorApi
```

### Step 5: Configure Windows Firewall

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Lead Generator API" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow
```

### Step 6: Verify API Installation

Open a browser and navigate to:
- Health check: http://localhost:5000/health
- Swagger UI: http://localhost:5000/swagger

---

## Desktop Client Installation

### Step 1: Create Directory

```powershell
New-Item -ItemType Directory -Force -Path "C:\Program Files\LeadGenerator\Desktop"
```

### Step 2: Build and Publish

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.Desktop -c Release -o "C:\Program Files\LeadGenerator\Desktop"
```

### Step 3: Configure the Client

Edit `C:\Program Files\LeadGenerator\Desktop\appsettings.json`:

```json
{
  "ApiSettings": {
    "BaseUrl": "http://localhost:5000",
    "Timeout": 30
  },
  "AppSettings": {
    "SessionTimeoutMinutes": 480,
    "AutoRefreshIntervalSeconds": 60
  }
}
```

### Step 4: Create Desktop Shortcut

```powershell
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\Lead Generator.lnk")
$Shortcut.TargetPath = "C:\Program Files\LeadGenerator\Desktop\LeadGenerator.Desktop.exe"
$Shortcut.WorkingDirectory = "C:\Program Files\LeadGenerator\Desktop"
$Shortcut.Description = "Lead Generator Desktop Client"
$Shortcut.Save()
```

---

## Mail Service Installation

### Step 1: Create Directory

```powershell
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService\Logs"
```

### Step 2: Build and Publish

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.MailService -c Release -o C:\LeadGenerator\MailService
```

### Step 3: Configure the Mail Service

Edit `C:\LeadGenerator\MailService\appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=ChangeThisPassword123!"
  },
  "ApiSettings": {
    "BaseUrl": "http://localhost:5000",
    "Timeout": 30
  },
  "MailService": {
    "WorkstationId": "WORKSTATION-01",
    "ScanIntervalSeconds": 60,
    "OutlookProfileName": "",
    "EnableReplyDetection": true,
    "EnableUnsubscribeDetection": true,
    "UnsubscribeKeywords": ["unsubscribe", "désabonner", "remove", "stop", "optout", "opt-out"]
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

**Important Configuration**:
- `WorkstationId`: Unique identifier for this machine
- `OutlookProfileName`: Leave empty to use default profile, or specify profile name
- `UnsubscribeKeywords`: Add keywords relevant to your campaigns

### Step 4: Install as Windows Service

The Mail Service requires running under a user account that has Outlook configured:

```powershell
# Run as Administrator

# Create the service
sc.exe create "LeadGeneratorMailService" binPath="C:\LeadGenerator\MailService\LeadGenerator.MailService.exe" start=auto displayname="Lead Generator Mail Service"
sc.exe description "LeadGeneratorMailService" "Lead Generator Email Processing Service"

# Configure to run under a user account (required for Outlook access)
# Replace DOMAIN\Username and password with actual values
sc.exe config "LeadGeneratorMailService" obj=".\YourUsername" password="YourPassword"

# Start the service
sc.exe start LeadGeneratorMailService
```

**Note**: The user account must:
- Have Outlook installed and configured
- Have "Log on as a service" permission
- Be an administrator or have appropriate permissions

### Step 5: Grant "Log on as a service" Permission

1. Press `Win + R`, type `secpol.msc`, press Enter
2. Navigate to: Local Policies > User Rights Assignment
3. Double-click "Log on as a service"
4. Click "Add User or Group"
5. Add the user account that will run the Mail Service
6. Click OK and close

---

## Post-Installation Configuration

### Step 1: Change Default Admin Password

1. Open the Desktop Client
2. Login with default credentials:
   - Username: `admin`
   - Password: `Admin123!`
3. Go to Settings > Change Password
4. Set a strong, unique password

### Step 2: Configure Mail Accounts

1. In the Desktop Client, go to Settings > Mail Accounts
2. Add the Outlook accounts configured on this machine
3. Assign accounts to users as needed

### Step 3: Create Additional Users

1. Go to Settings > Users
2. Create user accounts for your team members
3. Assign appropriate roles:
   - **Admin**: Full system access
   - **Manager**: Campaign management, no system settings
   - **User**: Limited to assigned campaigns

---

## Verification and Testing

### Test Checklist

| Test | Command/Action | Expected Result |
|------|---------------|-----------------|
| Database Connection | `psql -U leadgen_user -d leadgenerator -c "SELECT 1"` | Returns 1 |
| API Health | Browser: `http://localhost:5000/health` | "Healthy" |
| API Swagger | Browser: `http://localhost:5000/swagger` | Swagger UI loads |
| Desktop Login | Open Desktop Client, login | Login successful |
| Mail Service | `sc.exe query LeadGeneratorMailService` | RUNNING |

### Test Email Sending

1. Create a test contact list with your own email
2. Create a simple test campaign
3. Start the campaign
4. Verify email is received

---

## Troubleshooting

### API Won't Start

**Symptoms**: Service fails to start, port 5000 not accessible

**Solutions**:
1. Check logs at `C:\LeadGenerator\Logs`
2. Verify PostgreSQL is running:
   ```powershell
   Get-Service postgresql*
   ```
3. Test database connection:
   ```powershell
   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -c "SELECT 1"
   ```
4. Check if port 5000 is in use:
   ```powershell
   netstat -ano | findstr :5000
   ```

### Mail Service Won't Start

**Symptoms**: Service starts but immediately stops

**Solutions**:
1. Check logs at `C:\LeadGenerator\MailService\Logs`
2. Verify the service account has Outlook configured
3. Test Outlook opens correctly for the service account
4. Ensure "Log on as a service" permission is granted

### Desktop Client Can't Connect

**Symptoms**: "Connection refused" or timeout errors

**Solutions**:
1. Verify API is running: `http://localhost:5000/health`
2. Check `appsettings.json` has correct API URL
3. Verify firewall allows port 5000

### Database Connection Issues

**Symptoms**: "Connection refused" to PostgreSQL

**Solutions**:
1. Verify PostgreSQL service is running:
   ```powershell
   Get-Service postgresql*
   ```
2. Check `pg_hba.conf` allows local connections
3. Verify password in connection string matches database user

---

## Quick Reference

### Service Management Commands

```powershell
# API Service
sc.exe start LeadGeneratorApi
sc.exe stop LeadGeneratorApi
sc.exe query LeadGeneratorApi

# Mail Service
sc.exe start LeadGeneratorMailService
sc.exe stop LeadGeneratorMailService
sc.exe query LeadGeneratorMailService

# PostgreSQL
net start postgresql-x64-15
net stop postgresql-x64-15
```

### Important File Locations

| Item | Location |
|------|----------|
| API Application | `C:\LeadGenerator\Api` |
| API Configuration | `C:\LeadGenerator\Api\appsettings.json` |
| API Logs | `C:\LeadGenerator\Logs` |
| Desktop Client | `C:\Program Files\LeadGenerator\Desktop` |
| Mail Service | `C:\LeadGenerator\MailService` |
| Mail Service Logs | `C:\LeadGenerator\MailService\Logs` |
| File Storage | `C:\LeadGenerator\Files` |
| PostgreSQL Data | `C:\Program Files\PostgreSQL\15\data` |

### Default Credentials

| Account | Username | Password | Notes |
|---------|----------|----------|-------|
| Application Admin | admin | Admin123! | CHANGE IMMEDIATELY |
| Database User | leadgen_user | ChangeThisPassword123! | Update in config files |

---

**Document Version**: 1.0
**Last Updated**: January 2026
**Applies to**: Lead Generator v260128-2
