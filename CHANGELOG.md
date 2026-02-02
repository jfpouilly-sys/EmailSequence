# Changelog

All notable changes to the Lead Generator project will be documented in this file.

Version format: `YYMMDD-x` where:
- `YY` = Two last digits of the year
- `MM` = Month (01-12)
- `DD` = Day of the month (01-31)
- `x` = Version number for that day (starting at 1)

---

## [260202-2] - 2026-02-02

### Changed
- **BREAKING**: Upgraded all projects from .NET 8.0 to .NET 10.0
- Updated all NuGet packages to latest compatible versions:

| Package | Old Version | New Version |
|---------|-------------|-------------|
| Microsoft.EntityFrameworkCore | 8.0.0 | 10.0.0 |
| Microsoft.AspNetCore.Authentication.JwtBearer | 8.0.0 | 10.0.0 |
| Npgsql.EntityFrameworkCore.PostgreSQL | 8.0.0 | 10.0.0 |
| Microsoft.Extensions.Hosting | 8.0.0 | 10.0.0 |
| Microsoft.Extensions.Hosting.WindowsServices | 8.0.0 | 10.0.0 |
| Microsoft.Extensions.Http | 8.0.0 | 10.0.0 |
| Microsoft.Extensions.Configuration | 8.0.0 | 10.0.0 |
| Microsoft.Extensions.DependencyInjection | 8.0.0 | 10.0.0 |
| Serilog.AspNetCore | 8.0.0 | 9.0.0 |
| Serilog.Extensions.Hosting | 8.0.0 | 9.0.0 |
| Serilog.Settings.Configuration | 8.0.0 | 9.0.0 |
| Serilog.Enrichers.Environment | 2.3.0 | 3.0.1 |
| Serilog.Enrichers.Thread | 3.1.0 | 4.0.0 |
| Serilog.Sinks.Console | 5.0.0 | 6.0.0 |
| Serilog.Sinks.File | 5.0.0 | 6.0.0 |
| Swashbuckle.AspNetCore | 6.5.0 | 7.2.0 |
| CsvHelper | 30.0.1 | 33.0.1 |
| CommunityToolkit.Mvvm | 8.2.2 | 8.4.0 |

### Requirements
- .NET 10.0 SDK/Runtime required (previously .NET 8.0)

---

## [260202-1] - 2026-02-02

### Added
- **Python Tkinter GUI Client** (`client/` folder)
  - Full-featured desktop client using ttkbootstrap framework
  - Login view with JWT authentication
  - Dashboard with KPI cards and active campaigns
  - Campaign management (create, edit, activate, pause, delete)
  - Contact management with search and filtering
  - CSV import wizard with field mapping and validation
  - Template editor with merge tags picker and live preview
  - Reports view with matplotlib charts
  - Admin views: user management, mail accounts, suppression list
  - Settings view with theme selection (15+ themes)
  - Comprehensive error handling and status feedback

- **Comprehensive Logging System**
  - API logs: `logs/api/api-YYYYMMDD.log`, `logs/api/api-errors-YYYYMMDD.log`
  - Mail Service logs: `logs/mailservice/mailservice-YYYYMMDD.log`
  - GUI logs: `logs/gui/gui.log`, `logs/gui/gui-errors.log`, `logs/gui/api-calls.log`
  - Structured logging with Serilog enrichers (MachineName, ThreadId)
  - Request/response timing for all API calls
  - HTTP request logging middleware in API
  - Configurable log levels and retention periods

- **System Diagnostic Scripts**
  - `scripts/diagnostic.bat` - Windows batch diagnostic with colored output
  - `scripts/diagnostic.py` - Cross-platform Python diagnostic with JSON output
  - Checks: API health, database connection, PostgreSQL service, Mail Service
  - Checks: network ports (5000, 5432), log directories, file storage
  - Provides specific fix instructions for each failure
  - Displays quick start commands and default credentials

- **Backend Startup Scripts**
  - `scripts/start-backend.bat` - Start API and Mail Service (PostgreSQL assumed running)
  - `scripts/stop-backend.bat` - Stop all backend services
  - `scripts/start-all.bat` - Start entire system including GUI
  - Prerequisites checking (.NET SDK, PostgreSQL)
  - Service health verification after startup

- **GUI Build System**
  - `client/build.bat` - Build executable with PyInstaller
  - `client/run.bat` - Run with automatic dependency installation
  - `client/LeadGenerator.pyw` - Double-click launcher (no console)
  - `client/requirements.txt` - Python dependencies

### Fixed
- Added missing `Serilog.Settings.Configuration` package for `ReadFrom.Configuration()`
- Added missing `Serilog.Enrichers.Environment` package for `WithMachineName` enricher
- Added missing `Serilog.Enrichers.Thread` package for `WithThreadId` enricher
- Fixed build.bat to verify main.py exists before building

### Technical Details
- GUI Client: Python 3.9+, ttkbootstrap, requests, pandas, matplotlib, fpdf2
- API Client: REST with JWT Bearer authentication, retry logic, connection pooling
- Data Models: Dataclasses matching .NET DTOs with proper serialization
- Services: Campaign, Contact, Report, Template, CSV services

---

## [260128-2] - 2026-01-28

### Added
- **Version Tracking System**: Implemented version numbering in YYMMDD-x format
- **CHANGELOG.md**: Created comprehensive changelog file to track all version changes
- **About Menu**: Added About dialog in Desktop application displaying version, build date, and system info
- **Version API Endpoint**: Added `/api/version` endpoint in API to expose version information
- **VersionInfo Class**: Created centralized version management in Core project

### Changed
- Desktop application now displays current version in About dialog
- API exposes version information for client applications
- All projects reference centralized version information

---

## [260128-1] - 2026-01-28

### Added
- **Initial Release**: Complete .NET 8 Lead Generator application
- **LeadGenerator.Core**: Domain entities and enums
  - 15 entity classes (User, Contact, Campaign, EmailStep, etc.)
  - 8 enum types for type-safe status management
- **LeadGenerator.Data**: Entity Framework Core 8 with PostgreSQL
  - DbContext with full entity configurations
  - PostgreSQL ENUM type mapping
  - Proper indexing and relationships
- **LeadGenerator.Api**: REST API Server
  - JWT authentication with BCrypt password hashing
  - 5 controllers: Auth, Campaigns, Contacts, Reports, Suppression
  - 6 services with business logic
  - Swagger/OpenAPI documentation
  - Role-based authorization (Admin, Manager, User)
- **LeadGenerator.Desktop**: WPF Client Application
  - MVVM architecture with CommunityToolkit.Mvvm
  - 4 ViewModels, 2 Views (Login, Main)
  - Material Design UI components
  - API client integration
- **LeadGenerator.MailService**: Windows Service
  - Outlook COM Interop integration
  - Email sending with throttling and warmup mode
  - Reply detection service (stops sequences)
  - Unsubscribe detection (EN/FR keywords)
  - Background worker for automated processing

### Database
- **PostgreSQL Schema**: Complete database with 15 tables
  - Users and authentication
  - Mail accounts with rotation
  - Contact lists and contacts (10 custom fields)
  - Campaigns with multi-step sequences
  - Email logs and tracking
  - Suppression list (global/campaign scope)
  - A/B testing support
  - Audit logging
- **Setup Scripts**: 4 SQL scripts for database initialization
  - Database creation
  - Table creation with ENUM types
  - Seed data (default admin user: admin/Admin123!)
  - Performance indexes

### Features
- **Campaign Management**
  - Multi-step email sequences
  - Merge tags for personalization (10 custom fields)
  - Campaign reference tracking (ISIT-YYNNN format)
  - Sending schedules with randomization
  - A/B testing for subject lines and content
- **Contact Management**
  - CSV import with field mapping
  - Contact lists with user/role sharing
  - 10 custom fields per contact
  - Suppression list management
- **Email Automation**
  - Automated sending via Outlook
  - Reply detection (auto-stops sequences)
  - Unsubscribe detection with keywords
  - Warmup mode for new accounts
  - File attachments (direct or tracked links)
  - Sending throttling and randomization
- **Security**
  - JWT token authentication
  - BCrypt password hashing
  - Account lockout after failed attempts
  - Role-based access control
  - Audit logging for all actions
- **Reporting & Analytics**
  - Campaign statistics and metrics
  - Email logs with delivery status
  - Download tracking for attachments
  - Response rate calculations
- **CRM Integration**
  - Sync endpoints for external CRM systems
  - Delta sync support
  - Status change tracking

### Installation
- **PowerShell Scripts**: Automated installation for all components
  - `install-all.ps1`: Complete server installation
  - `install-mailservice.ps1`: Workstation mail service setup
  - `install-desktop.ps1`: Desktop client installation
- **Documentation**
  - README.md with complete setup guide
  - BUILD_INSTRUCTIONS.md with deployment steps
  - Configuration examples

### Technology Stack
- .NET 8 (API, Desktop, Service)
- PostgreSQL 15+ with EF Core 8
- WPF with Material Design
- Outlook COM Interop
- Serilog for logging
- CommunityToolkit.Mvvm for MVVM pattern
- BCrypt.Net for password hashing
- JWT for authentication
- CsvHelper for CSV import

### Notes
- **Default Credentials**: admin / Admin123! (change immediately after first login)
- **Deployment**: Internal network only
- **Requirements**: Windows Server, PostgreSQL 15+, Outlook installed on workstations
