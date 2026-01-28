# Changelog

All notable changes to the Lead Generator project will be documented in this file.

Version format: `YYMMDD-x` where:
- `YY` = Two last digits of the year
- `MM` = Month (01-12)
- `DD` = Day of the month (01-31)
- `x` = Version number for that day (starting at 1)

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
