# Lead Generator - Client-Server Installation Guide

**Version**: 260128-2
**Language**: English

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [System Requirements](#system-requirements)
4. [Part 1: Server Installation](#part-1-server-installation)
5. [Part 2: Workstation Installation](#part-2-workstation-installation)
6. [Network Configuration](#network-configuration)
7. [Security Considerations](#security-considerations)
8. [Post-Installation Configuration](#post-installation-configuration)
9. [Verification and Testing](#verification-and-testing)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the distributed installation of Lead Generator in a client-server architecture. This configuration is recommended for:

- Medium to large teams (5+ users)
- Production environments
- Multi-office deployments
- High availability requirements

### Deployment Scenarios

| Scenario | Server | Workstations | Best For |
|----------|--------|--------------|----------|
| Small Office | 1 server | 2-5 workstations | Small teams |
| Medium Office | 1 server | 5-20 workstations | Growing teams |
| Enterprise | 1+ servers (with failover) | 20+ workstations | Large organizations |

---

## Architecture

### Network Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           NETWORK                                         │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         SERVER                                       │ │
│  │                   (e.g., 192.168.1.10)                               │ │
│  │                                                                      │ │
│  │    ┌─────────────────┐         ┌─────────────────┐                  │ │
│  │    │ LeadGenerator   │         │   PostgreSQL    │                  │ │
│  │    │     API         │────────▶│   Database      │                  │ │
│  │    │  (Port 5000)    │         │  (Port 5432)    │                  │ │
│  │    └────────┬────────┘         └─────────────────┘                  │ │
│  │             │                                                        │ │
│  └─────────────┼────────────────────────────────────────────────────────┘ │
│                │                                                           │
│                │ HTTP/REST (Port 5000)                                    │
│                │                                                           │
│    ┌───────────┴───────────┬───────────────────┬───────────────────┐     │
│    │                       │                   │                   │     │
│    ▼                       ▼                   ▼                   ▼     │
│ ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐│
│ │ WORKSTATION 1│    │ WORKSTATION 2│    │ WORKSTATION 3│    │   ...    ││
│ │192.168.1.101 │    │192.168.1.102 │    │192.168.1.103 │    │          ││
│ │              │    │              │    │              │    │          ││
│ │┌────────────┐│    │┌────────────┐│    │┌────────────┐│    │          ││
│ ││  Desktop   ││    ││  Desktop   ││    ││  Desktop   ││    │          ││
│ ││  Client    ││    ││  Client    ││    ││  Client    ││    │          ││
│ │└────────────┘│    │└────────────┘│    │└────────────┘│    │          ││
│ │              │    │              │    │              │    │          ││
│ │┌────────────┐│    │┌────────────┐│    │              │    │          ││
│ ││Mail Service││    ││Mail Service││    │ (No Mail    │    │          ││
│ ││ + Outlook  ││    ││ + Outlook  ││    │  Service)   │    │          ││
│ │└────────────┘│    │└────────────┘│    │              │    │          ││
│ └──────────────┘    └──────────────┘    └──────────────┘    └──────────┘│
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Distribution

| Component | Installation Location | Quantity |
|-----------|----------------------|----------|
| PostgreSQL Database | Server | 1 |
| LeadGenerator.Api | Server | 1 |
| LeadGenerator.Desktop | All workstations | N |
| LeadGenerator.MailService | Workstations with Outlook | 1-N |

---

## System Requirements

### Server Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disk Space | 100 GB SSD | 500 GB SSD |
| Network | 1 Gbps | 1 Gbps |
| OS | Windows Server 2019 | Windows Server 2022 |

**Software Requirements (Server)**:
- .NET 8 Runtime (ASP.NET Core)
- PostgreSQL 15+

### Workstation Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk Space | 10 GB | 20 GB |
| Network | 100 Mbps | 1 Gbps |
| OS | Windows 10 Pro | Windows 11 Pro |

**Software Requirements (Workstation)**:
- .NET 8 Desktop Runtime
- Microsoft Outlook 2016+ (only for workstations with Mail Service)

### Network Requirements

| Port | Protocol | Direction | Purpose |
|------|----------|-----------|---------|
| 5000 | TCP | Server ← Workstations | API Access |
| 5432 | TCP | Server only | PostgreSQL (not exposed) |
| 443 | TCP | Outbound | Outlook email sending |

---

## Part 1: Server Installation

### Step 1.1: Prepare the Server

1. Install Windows Server 2019/2022
2. Configure static IP address (e.g., 192.168.1.10)
3. Set server hostname
4. Apply Windows Updates

### Step 1.2: Install .NET 8 Runtime

```powershell
# Download and install .NET 8 ASP.NET Core Runtime
# From: https://dotnet.microsoft.com/download/dotnet/8.0

# Verify installation
dotnet --list-runtimes
```

### Step 1.3: Install PostgreSQL

1. Download PostgreSQL 15+ from https://www.postgresql.org/download/windows/
2. Run installer as Administrator
3. Configuration during installation:
   - **Port**: 5432
   - **Password**: Set strong password for `postgres` user
   - **Locale**: Default
4. Complete installation

### Step 1.4: Configure PostgreSQL for Network Access

Edit `C:\Program Files\PostgreSQL\15\data\postgresql.conf`:

```ini
# Listen on all interfaces (or specific IP)
listen_addresses = 'localhost'  # Keep localhost only for security
```

Edit `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`:

```ini
# Only allow local connections (API on same server)
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
```

Restart PostgreSQL:

```powershell
net stop postgresql-x64-15
net start postgresql-x64-15
```

### Step 1.5: Create Database

Connect to PostgreSQL:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

Execute SQL commands:

```sql
-- Create database
CREATE DATABASE leadgenerator
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create application user
CREATE USER leadgen_user WITH PASSWORD 'YourSecurePassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE leadgenerator TO leadgen_user;

\c leadgenerator

GRANT ALL ON SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO leadgen_user;
```

### Step 1.6: Run Database Scripts

```powershell
cd C:\LeadGenerator\Source

# Create tables
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\002_create_tables.sql"

# Seed admin user
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\003_seed_admin_user.sql"

# Create indexes
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\004_create_indexes.sql"
```

### Step 1.7: Install API Server

Create directories:

```powershell
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Api"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Files"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Logs"
```

Build and publish:

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.Api -c Release -o C:\LeadGenerator\Api
```

### Step 1.8: Configure API

Edit `C:\LeadGenerator\Api\appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=YourSecurePassword123!"
  },
  "Jwt": {
    "Key": "YourVerySecureJWTKeyThatIsAtLeast32CharactersLong!",
    "Issuer": "LeadGenerator",
    "Audience": "LeadGeneratorClients",
    "ExpirationMinutes": 480
  },
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files",
    "MaxFileSizeMB": 10,
    "AllowedExtensions": [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg"]
  },
  "CampaignDefaults": {
    "InterEmailDelayMinutes": 30,
    "SequenceStepDelayDays": 3,
    "SendingWindowStart": "09:00",
    "SendingWindowEnd": "17:00",
    "SendingDays": "Mon,Tue,Wed,Thu,Fri",
    "DailySendLimit": 50
  },
  "Security": {
    "MaxFailedLoginAttempts": 5,
    "LockoutMinutes": 15,
    "PasswordMinLength": 8,
    "RequireUppercase": true,
    "RequireNumber": true
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "AllowedHosts": "*",
  "Urls": "http://0.0.0.0:5000"
}
```

**Important**: Set `Urls` to `http://0.0.0.0:5000` to listen on all interfaces.

### Step 1.9: Install API as Windows Service

```powershell
# Run as Administrator
sc.exe create "LeadGeneratorApi" binPath="C:\LeadGenerator\Api\LeadGenerator.Api.exe" start=auto displayname="Lead Generator API"
sc.exe description "LeadGeneratorApi" "Lead Generator REST API Server"

# Start service
sc.exe start LeadGeneratorApi
```

### Step 1.10: Configure Windows Firewall

```powershell
# Allow API port from internal network only
New-NetFirewallRule -DisplayName "Lead Generator API" `
    -Direction Inbound `
    -Port 5000 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.1.0/24  # Adjust to your network
```

### Step 1.11: Verify Server Installation

Test from the server:

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:5000/health"

# Should return: Healthy
```

Access Swagger UI: http://[SERVER-IP]:5000/swagger

---

## Part 2: Workstation Installation

Repeat these steps on each workstation.

### Step 2.1: Install Prerequisites

1. Install .NET 8 Desktop Runtime
   - Download from: https://dotnet.microsoft.com/download/dotnet/8.0
   - Run installer as Administrator

2. (If Mail Service needed) Install and configure Microsoft Outlook
   - Ensure at least one email account is configured
   - Test sending and receiving emails

### Step 2.2: Install Desktop Client

Create directory and copy files:

```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "C:\Program Files\LeadGenerator\Desktop"

# Copy published files from network share or deployment package
# OR build locally:
# dotnet publish src\LeadGenerator.Desktop -c Release -o "C:\Program Files\LeadGenerator\Desktop"
```

Configure `C:\Program Files\LeadGenerator\Desktop\appsettings.json`:

```json
{
  "ApiSettings": {
    "BaseUrl": "http://192.168.1.10:5000",
    "Timeout": 30
  },
  "AppSettings": {
    "SessionTimeoutMinutes": 480,
    "AutoRefreshIntervalSeconds": 60
  }
}
```

**Important**: Replace `192.168.1.10` with your server's IP address.

Create desktop shortcut:

```powershell
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\Lead Generator.lnk")
$Shortcut.TargetPath = "C:\Program Files\LeadGenerator\Desktop\LeadGenerator.Desktop.exe"
$Shortcut.WorkingDirectory = "C:\Program Files\LeadGenerator\Desktop"
$Shortcut.Description = "Lead Generator Desktop Client"
$Shortcut.Save()
```

### Step 2.3: Install Mail Service (Optional)

Only install on workstations that will send emails.

Create directories:

```powershell
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService\Logs"
```

Copy files:

```powershell
# Copy from network share or deployment package
# OR build locally:
# dotnet publish src\LeadGenerator.MailService -c Release -o C:\LeadGenerator\MailService
```

Configure `C:\LeadGenerator\MailService\appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=192.168.1.10;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=YourSecurePassword123!"
  },
  "ApiSettings": {
    "BaseUrl": "http://192.168.1.10:5000",
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
- Replace `192.168.1.10` with your server's IP address
- Set unique `WorkstationId` for each workstation (e.g., WORKSTATION-01, WORKSTATION-02)

### Step 2.4: Configure Mail Service Account

The Mail Service needs to run under a user account with Outlook access.

**Grant "Log on as a service" permission**:
1. Press `Win + R`, type `secpol.msc`, press Enter
2. Navigate to: Local Policies > User Rights Assignment
3. Double-click "Log on as a service"
4. Add the user account
5. Click OK

**Install service**:

```powershell
# Run as Administrator
sc.exe create "LeadGeneratorMailService" binPath="C:\LeadGenerator\MailService\LeadGenerator.MailService.exe" start=auto displayname="Lead Generator Mail Service"
sc.exe description "LeadGeneratorMailService" "Lead Generator Email Processing Service"

# Configure to run under user account
sc.exe config "LeadGeneratorMailService" obj=".\YourUsername" password="YourPassword"

# Start service
sc.exe start LeadGeneratorMailService
```

### Step 2.5: Configure PostgreSQL Access (If Mail Service Connects Directly)

On the **server**, add workstation IPs to `pg_hba.conf`:

```ini
# Allow Mail Service connections from workstations
host    leadgenerator   leadgen_user    192.168.1.101/32        scram-sha-256
host    leadgenerator   leadgen_user    192.168.1.102/32        scram-sha-256
# Add more workstations as needed
```

Update `postgresql.conf` to listen on network:

```ini
listen_addresses = '192.168.1.10'  # Server IP only
```

Add firewall rule on server:

```powershell
New-NetFirewallRule -DisplayName "PostgreSQL - Mail Services" `
    -Direction Inbound `
    -Port 5432 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.1.101,192.168.1.102  # Specific workstation IPs
```

Restart PostgreSQL:

```powershell
net stop postgresql-x64-15
net start postgresql-x64-15
```

---

## Network Configuration

### DNS Configuration (Recommended)

Configure internal DNS for easier management:

| Hostname | IP Address | Purpose |
|----------|------------|---------|
| leadgen-server.internal | 192.168.1.10 | API Server |
| leadgen-db.internal | 192.168.1.10 | Database |

Update configuration files to use hostnames instead of IPs.

### HTTPS Configuration (Recommended for Production)

For production environments, enable HTTPS:

1. **Obtain SSL Certificate**
   - Purchase from Certificate Authority, or
   - Use internal PKI, or
   - Use Let's Encrypt

2. **Configure API for HTTPS**

Edit `appsettings.json`:

```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://0.0.0.0:5000"
      },
      "Https": {
        "Url": "https://0.0.0.0:5001",
        "Certificate": {
          "Path": "C:\\LeadGenerator\\Certs\\server.pfx",
          "Password": "CertificatePassword"
        }
      }
    }
  }
}
```

3. **Update Firewall**

```powershell
New-NetFirewallRule -DisplayName "Lead Generator API HTTPS" `
    -Direction Inbound `
    -Port 5001 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.1.0/24
```

4. **Update Client Configurations**

Change `BaseUrl` in workstation configs to use `https://`.

---

## Security Considerations

### Network Security

1. **Firewall Rules**
   - Only allow API access from internal network
   - Restrict PostgreSQL to server and authorized workstations only
   - Block all unnecessary ports

2. **Network Segmentation**
   - Consider placing server in a separate VLAN
   - Use internal DNS for service discovery

### Application Security

1. **Change Default Credentials**
   - Change admin password immediately after installation
   - Use strong passwords for all accounts

2. **JWT Configuration**
   - Use a strong, unique JWT key (32+ characters)
   - Consider shorter token expiration for high-security environments

3. **Database Security**
   - Use strong database passwords
   - Limit database user permissions to minimum required
   - Regular backup of database

### Audit and Monitoring

1. **Enable Logging**
   - API logs: `C:\LeadGenerator\Logs`
   - Mail Service logs: `C:\LeadGenerator\MailService\Logs`
   - PostgreSQL logs: `C:\Program Files\PostgreSQL\15\data\log`

2. **Monitor Services**
   - Set up alerts for service failures
   - Monitor disk space and database size

---

## Post-Installation Configuration

### Step 1: Initial Admin Login

1. Open Desktop Client on any workstation
2. Login with default credentials:
   - Username: `admin`
   - Password: `Admin123!`
3. **Immediately change the admin password**

### Step 2: Register Workstations

1. Go to Settings > Workstations
2. Add each workstation with Mail Service:
   - Workstation ID (must match `appsettings.json`)
   - Description
   - Assigned mail accounts

### Step 3: Configure Mail Accounts

1. Go to Settings > Mail Accounts
2. Add Outlook accounts from each workstation
3. Associate accounts with workstations

### Step 4: Create Users

1. Go to Settings > Users
2. Create accounts for team members
3. Assign appropriate roles:
   - **Admin**: Full access
   - **Manager**: Campaign management
   - **User**: Limited access

### Step 5: Test Email Sending

1. Create a test contact list
2. Create a simple test campaign
3. Assign to a workstation with Mail Service
4. Start campaign and verify emails are sent

---

## Verification and Testing

### Server Verification

| Test | Command | Expected Result |
|------|---------|-----------------|
| PostgreSQL Running | `Get-Service postgresql*` | Running |
| API Running | `Get-Service LeadGeneratorApi` | Running |
| API Health | `curl http://localhost:5000/health` | Healthy |
| Database Connection | `psql -U leadgen_user -d leadgenerator -c "SELECT 1"` | Returns 1 |

### Workstation Verification

| Test | Action | Expected Result |
|------|--------|-----------------|
| Network to Server | `ping 192.168.1.10` | Success |
| API Access | Browser: `http://192.168.1.10:5000/health` | Healthy |
| Desktop Client | Launch and login | Login successful |
| Mail Service | `Get-Service LeadGeneratorMailService` | Running |

### End-to-End Test

1. Login to Desktop Client from workstation
2. Create a contact list with test email
3. Create and start a test campaign
4. Verify:
   - Campaign appears in UI
   - Mail Service picks up emails
   - Test email received

---

## Troubleshooting

### Workstation Cannot Connect to API

**Symptoms**: Connection timeout or refused

**Solutions**:
1. Verify network connectivity:
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.10 -Port 5000
   ```
2. Check firewall on server
3. Verify API service is running on server
4. Check `appsettings.json` has correct server IP

### Mail Service Cannot Connect to Database

**Symptoms**: Database connection errors in logs

**Solutions**:
1. Verify PostgreSQL allows connections from workstation IP
2. Check `pg_hba.conf` includes workstation IP
3. Verify `postgresql.conf` listens on server IP
4. Check firewall allows port 5432 from workstation
5. Test connection:
   ```powershell
   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -h 192.168.1.10 -U leadgen_user -d leadgenerator -c "SELECT 1"
   ```

### Mail Service Not Sending Emails

**Symptoms**: Emails stuck in pending state

**Solutions**:
1. Check Mail Service logs
2. Verify Outlook is configured for service account
3. Test Outlook can send manually
4. Verify WorkstationId matches database configuration
5. Check Mail Service is assigned correct mail accounts

### Performance Issues

**Symptoms**: Slow response times, timeouts

**Solutions**:
1. Check server resources (CPU, RAM, disk)
2. Review PostgreSQL performance
3. Consider adding indexes for large tables
4. Review network bandwidth
5. Check for antivirus interference

---

## Appendix: Deployment Checklist

### Server Checklist

- [ ] Windows Server installed and updated
- [ ] Static IP configured
- [ ] .NET 8 Runtime installed
- [ ] PostgreSQL installed and configured
- [ ] Database created and initialized
- [ ] API published and configured
- [ ] API installed as Windows Service
- [ ] Firewall rules configured
- [ ] API health check passing
- [ ] Default admin password changed

### Per-Workstation Checklist

- [ ] .NET 8 Desktop Runtime installed
- [ ] (If needed) Outlook installed and configured
- [ ] Desktop Client installed and configured
- [ ] Desktop Client can connect to API
- [ ] (If needed) Mail Service installed
- [ ] (If needed) Mail Service account configured
- [ ] (If needed) Mail Service running and connected
- [ ] User can login successfully

---

**Document Version**: 1.0
**Last Updated**: January 2026
**Applies to**: Lead Generator v260128-2
