# Lead Generator

**Version: 260128-2** | Built with .NET 8 | PostgreSQL 15+

A multi-user desktop application for managing digital marketing email campaigns with Outlook integration.

## Overview

Lead Generator is a comprehensive email campaign management system built on .NET 8, featuring:

- **API Server**: REST API with PostgreSQL database for campaign, contact, and email management
- **Desktop Client**: WPF Windows application for campaign creation and monitoring
- **Mail Service**: Windows Service with Outlook COM Interop for automated email sending and reply detection
- **CRM Integration**: Sync endpoints for integration with external CRM systems

## Features

- ✅ Multi-user authentication with role-based access (Admin, Manager, User)
- ✅ Campaign management with email sequences
- ✅ Contact list management with CSV import
- ✅ Template editor with merge tags for personalization
- ✅ Outlook integration for email sending
- ✅ Automatic reply and unsubscribe detection
- ✅ Campaign analytics and reporting
- ✅ Suppression list management
- ✅ A/B testing support
- ✅ File attachment support (direct or tracked links)
- ✅ Sending throttling and warmup mode
- ✅ Internal network only (no public endpoints)

## Technology Stack

- **.NET 8** - Modern cross-platform framework
- **PostgreSQL 15+** - Robust relational database
- **Entity Framework Core 8** - ORM for database access
- **WPF** - Rich desktop UI framework
- **Outlook COM Interop** - Email integration
- **JWT Authentication** - Secure API access
- **BCrypt** - Password hashing
- **Serilog** - Structured logging

## Project Structure

```
LeadGenerator/
├── src/
│   ├── LeadGenerator.Core/          # Domain entities and enums
│   ├── LeadGenerator.Data/          # EF Core DbContext and configurations
│   ├── LeadGenerator.Api/           # REST API server
│   ├── LeadGenerator.Desktop/       # WPF client application
│   └── LeadGenerator.MailService/   # Windows Service for email processing
├── scripts/
│   ├── database/                    # SQL scripts for database setup
│   └── install/                     # PowerShell installation scripts
├── docs/                            # Documentation
└── LeadGenerator.sln                # Visual Studio solution
```

## System Requirements

### Server (API + Database)
- Windows Server 2019+ or Windows 10/11 Pro
- 4 GB RAM minimum (8 GB recommended)
- 50 GB disk space
- .NET 8 Runtime
- PostgreSQL 15+

### Workstations (Desktop Client + Mail Service)
- Windows 10/11
- 4 GB RAM minimum
- .NET 8 Desktop Runtime
- Microsoft Outlook 2016+ (installed and configured)
- Network access to API server

### Network
- All components on internal network or VPN
- Port 5000 (or configured) open for API
- Port 5432 open for PostgreSQL (server only)

## Installation

### Prerequisites

1. Install **.NET 8 SDK** from https://dotnet.microsoft.com/download
2. Install **PostgreSQL 15+** from https://www.postgresql.org/download/
3. Install **Microsoft Outlook** on workstations that will send emails

### Quick Build (Recommended)

**Using the Makefile-style build system:**

```powershell
# Show available commands
.\build.ps1 -Target help

# Complete build and installation (interactive)
.\build.ps1 -Target install-all

# Or using batch launcher
make help
make install-all
```

**Or build step-by-step:**

```powershell
# Clean, build, and publish
.\build.ps1 -Target publish

# Setup database
.\build.ps1 -Target database-setup -DatabasePassword "YourPassword"
```

See `QUICKSTART.md` for detailed first-time installation guide.

### Manual Build (Alternative)

```powershell
# Clone the repository
git clone <repository-url>
cd LeadGenerator

# Restore dependencies
dotnet restore

# Build the solution
dotnet build LeadGenerator.sln -c Release

# Publish all projects
dotnet publish src/LeadGenerator.Api -c Release -o ./publish/Api
dotnet publish src/LeadGenerator.MailService -c Release -o ./publish/MailService
dotnet publish src/LeadGenerator.Desktop -c Release -o ./publish/Desktop
```

### Database Setup

```powershell
# Run as postgres superuser
psql -U postgres -f scripts/database/001_create_database.sql

# Run as leadgen_user
psql -U leadgen_user -d leadgenerator -f scripts/database/002_create_tables.sql
psql -U leadgen_user -d leadgenerator -f scripts/database/003_seed_admin_user.sql
psql -U leadgen_user -d leadgenerator -f scripts/database/004_create_indexes.sql
```

### Install API Server

```powershell
# Run as Administrator
cd scripts/install
.\install-all.ps1 -ServerName "localhost" -DatabasePassword "YourPassword" -ApiServerUrl "http://localhost:5000"
```

### Install Mail Service (on each workstation)

```powershell
# Run as Administrator
cd scripts/install
.\install-mailservice.ps1 -ApiServerUrl "http://your-server:5000" -WorkstationId "WORKSTATION-01"
```

### Install Desktop Client (on each workstation)

```powershell
cd scripts/install
.\install-desktop.ps1 -ApiServerUrl "http://your-server:5000"
```

## Configuration

### API Server (appsettings.json)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=leadgenerator;Username=leadgen_user;Password=YourPassword"
  },
  "Jwt": {
    "Key": "YourSuperSecretKeyAtLeast32Characters!",
    "ExpirationMinutes": 480
  },
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files"
  }
}
```

### Mail Service (appsettings.json)

```json
{
  "ApiBaseUrl": "http://your-server:5000",
  "WorkstationId": "WORKSTATION-01",
  "ScanIntervalSeconds": 60
}
```

## Default Credentials

**Username:** admin
**Password:** Admin123!

**⚠️ IMPORTANT: Change the admin password immediately after first login!**

## Usage

1. **Login**: Launch the desktop client and login with admin credentials
2. **Create Mail Accounts**: Settings → Mail Accounts → Add mail accounts for each Outlook profile
3. **Import Contacts**: Create a contact list and import contacts from CSV
4. **Create Campaign**: Create a new campaign and define email sequence steps
5. **Activate Campaign**: Start the campaign to begin sending emails
6. **Monitor Results**: View reports and statistics in the Reports section

## API Documentation

Once the API server is running, access the Swagger documentation at:

```
http://localhost:5000/swagger
```

## Key Endpoints

- `POST /api/auth/login` - Authenticate and get JWT token
- `GET /api/version` - Get application version information
- `GET /api/version/health` - Get API health status
- `GET /api/campaigns` - List all campaigns
- `POST /api/campaigns` - Create new campaign
- `GET /api/contacts/list/{listId}` - Get contacts for a list
- `POST /api/contacts/import/{listId}` - Import contacts from CSV
- `GET /api/reports/campaign/{campaignId}` - Get campaign statistics

## Version Information

### Version Format

Versions follow the format: **YYMMDD-x**

- `YY` = Last two digits of the year
- `MM` = Month (01-12)
- `DD` = Day (01-31)
- `x` = Build number for that day (starting at 1)

Example: `260128-2` = January 28, 2026, Build 2

### Viewing Version

- **Desktop Client**: Help → About menu displays current version and system information
- **API Server**: Access `/api/version` endpoint for detailed version information
- **CHANGELOG**: See `CHANGELOG.md` for version history and changes between releases

### Changelog

All version changes are documented in the `CHANGELOG.md` file. Each version entry includes:
- Added features
- Changed functionality
- Fixed bugs
- Breaking changes (if any)

## Security Features

- JWT token-based authentication
- BCrypt password hashing
- Role-based authorization
- Account lockout after failed login attempts
- Internal network only (no public exposure)
- Audit logging for security events

## Campaign Reference Format

All campaigns are identified by a unique reference in the format: **ISIT-YYNNN**

Example: `ISIT-26001`

This reference is automatically added to email subjects for tracking replies and unsubscribes.

## Unsubscribe Detection

The system automatically detects unsubscribe requests using keywords in email replies:

**English:** UNSUBSCRIBE, STOP, REMOVE, OPT OUT, OPT-OUT
**French:** DÉSINSCRIRE, DÉSINSCRIPTION, STOP, ARRÊTER, SUPPRIMER

## Troubleshooting

### API Server Not Starting

- Check PostgreSQL is running: `sc query postgresql-x64-15`
- Verify connection string in appsettings.json
- Check logs in `C:\LeadGenerator\Logs`

### Mail Service Not Sending Emails

- Ensure Outlook is installed and configured on the workstation
- Verify the service is running as a user with Outlook access
- Check workstation ID matches mail account assignment
- Review logs in `C:\LeadGenerator\MailService\logs`

### Desktop Client Cannot Connect

- Verify API server URL in appsettings.json
- Test API health: `Invoke-RestMethod -Uri "http://your-server:5000/health"`
- Check firewall settings

## Development

### Running in Development

```powershell
# API Server
cd src/LeadGenerator.Api
dotnet run

# Desktop Client
cd src/LeadGenerator.Desktop
dotnet run

# Mail Service
cd src/LeadGenerator.MailService
dotnet run
```

### Database Migrations

```powershell
# Add migration
cd src/LeadGenerator.Data
dotnet ef migrations add MigrationName --startup-project ../LeadGenerator.Api

# Update database
dotnet ef database update --startup-project ../LeadGenerator.Api
```

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact your system administrator.

---

Built with ❤️ using .NET 8 and PostgreSQL
