# Lead Generator — Digital Marketing Campaign Tool

## Project Overview

Multi-user desktop application for managing email marketing campaigns with automated sequences, reply/unsubscribe detection, and CRM synchronization.

## Architecture

- **API Server**: .NET 8 REST API (LeadGenerator.Api)
- **Database**: PostgreSQL 15+
- **Desktop Client**: Python 3.10+ with ttkbootstrap (OR WPF .NET 8)
- **Mail Service**: Python pywin32 for Outlook COM Interop (OR .NET Windows Service)
- **ORM**: Entity Framework Core 8 (API), requests (Python client)

## Key Constraints

- ALL components run on internal network only — no public endpoints
- Standalone authentication (JWT) — no AD/LDAP
- Email-based unsubscribe — no web forms (EN + FR keywords)
- Hybrid attachments: user chooses Attachment (no tracking) or Link (internal network click tracking)
- CRM is a client app, not a server — CRM pulls from our API, not the other way around
- 10 custom fields from CSV import available as merge tags in templates

## Technology Stack

### Backend (.NET 8)
- ASP.NET Core 8 Web API
- Entity Framework Core 8 + PostgreSQL (Npgsql)
- JWT Bearer authentication (BCrypt password hashing)
- Serilog for logging
- FluentValidation for request validation

### Python Desktop Client
- Python 3.10+
- ttkbootstrap (modern Tkinter)
- requests (HTTP client)
- pandas (CSV handling)
- matplotlib (charts)
- pywin32 (Outlook COM Interop)
- keyring (token storage)
- PyInstaller (packaging)

## Database

PostgreSQL 15+ with these main tables:
- users, mail_accounts, user_mail_accounts
- contact_lists, contacts (10 custom fields: custom1-custom10)
- campaigns, campaign_mail_accounts
- email_steps, attachments (delivery_mode: Attachment/Link)
- campaign_contacts (status tracking per campaign)
- email_logs, download_logs
- suppression_list (global/campaign scope)
- ab_tests
- audit_logs

## User Roles

- **Admin**: Full access (users, mail accounts, CRM config, all campaigns)
- **Manager**: Create/manage campaigns, view all campaigns, manage suppression list
- **User**: Create/manage own campaigns only, limited reports

## Sending Engine Rules

- Emails sent via Outlook COM Interop on each workstation
- Anti-spam: daily/hourly limits per account, randomized delays (±15min), business hours only (Mon-Fri 09:00-17:00)
- Warmup mode: gradual volume increase over 22 days for new accounts
- Bounce circuit breaker: pause campaign if bounce rate > 10%

## Unsubscribe Detection (EN + FR)

Keywords scanned in inbox/dedicated folder:
- EN: UNSUBSCRIBE, STOP, REMOVE, OPT OUT, OPT-OUT
- FR: DÉSINSCRIRE, DÉSINSCRIPTION, STOP, ARRÊTER, SUPPRIMER
- Unsubscribe emails received on same sending accounts (no dedicated address)

## CRM Integration

- CRM is a desktop client — it connects to our API, not the reverse
- Sync endpoints: GET /api/sync/contacts, /status-changes, /activities
- CRM posts back updates: POST /api/sync/crm-updates, /acknowledge
- Internal network / VPN access only

## File Organization

```
LeadGenerator/
├── CLAUDE.md                        # This file
├── docs/
│   ├── FunctionalSpec.md            # Full functional specification
│   ├── ClaudeCodeGuide.md           # .NET implementation guide
│   └── TkinterClientGuide.md        # Python client guide
├── src/
│   ├── LeadGenerator.Api/           # .NET 8 Web API
│   ├── LeadGenerator.Core/          # Shared domain models
│   ├── LeadGenerator.Data/          # EF Core DbContext
│   └── LeadGenerator.MailService/   # .NET Windows Service (optional)
├── client/                          # Python Tkinter client
│   ├── main.py
│   ├── config.yaml
│   ├── core/
│   ├── services/
│   ├── ui/
│   └── mail_worker/
├── scripts/
│   └── database/
└── LeadGenerator.sln
```

## Coding Conventions

### .NET (Backend)
- Use async/await everywhere
- Use repository pattern with EF Core
- DTOs for API responses (never expose entities directly)
- Use FluentValidation for all request validation
- Log with Serilog structured logging

### Python (Client)
- Type hints on all functions
- Dataclasses for models
- MVVM-like: Views (UI) → Services (logic) → ApiClient (HTTP)
- Logging via built-in logging module
- Config via config.yaml

## Important Implementation Notes

- Campaign identifier format: ISIT-{YY}{NNNN} (e.g., ISIT-250042)
- Campaign identifier in email footer only (small text) + X-Campaign-ID header
- Merge tags format: {{FieldName}} — e.g., {{FirstName}}, {{Custom1}}
- Custom field labels are stored per contact list (custom1_label...custom10_label)
- Suppression list checked BEFORE every email send
- Download tracking: token-based URLs, logged in download_logs table
- All timestamps in UTC
