# Lead Generator — Digital Marketing Campaign Tool

## Project Overview

Multi-user desktop application for managing email marketing campaigns with automated sequences, reply/unsubscribe detection, and CRM synchronization.

## Existing Backend (Already Implemented)

The .NET 8 backend is already built and available in the GitHub repository. **Do not recreate or modify the backend.** The Python client connects to it via REST API.

### Backend Components (DO NOT MODIFY)
- **API Server**: .NET 8 REST API (LeadGenerator.Api)
- **Database**: PostgreSQL 15+ (schema already created)
- **ORM**: Entity Framework Core 8
- **Authentication**: JWT Bearer tokens with BCrypt
- **Mail Service**: .NET Windows Service with Outlook COM Interop

### API Base URL
Configure in `client/config.yaml` → `api.base_url`

## What We're Building Here

**Python Tkinter desktop client** that connects to the existing .NET 8 API backend.

This is an alternative/complementary client to the existing WPF client — both connect to the same API.

## Key Constraints

- ALL components run on internal network only — no public endpoints
- Standalone authentication (JWT) — no AD/LDAP
- Email-based unsubscribe — no web forms (EN + FR keywords)
- Hybrid attachments: user chooses Attachment (no tracking) or Link (internal network click tracking)
- CRM is a client app — CRM pulls from our API, not the other way around
- 10 custom fields from CSV import available as merge tags in templates

## Python Client Technology Stack

- Python 3.10+
- ttkbootstrap (modern Tkinter for Windows 11 look)
- requests (HTTP client to connect to .NET API)
- pandas (CSV handling)
- matplotlib (charts embedded in Tkinter)
- fpdf2 (PDF report export)
- pywin32 (Outlook COM Interop for mail worker)
- keyring (secure JWT token storage)
- schedule (background task scheduling)
- PyInstaller (packaging into single .exe)

## Python Client Structure

```
client/
├── main.py                         # Application entry point
├── config.yaml                     # Configuration (API URL, etc.)
├── requirements.txt                # Python dependencies
│
├── core/
│   ├── api_client.py               # REST API communication (JWT auth)
│   ├── auth.py                     # Token management
│   ├── models.py                   # Data classes matching API DTOs
│   └── exceptions.py               # Custom exceptions
│
├── services/
│   ├── campaign_service.py         # Campaign business logic
│   ├── contact_service.py          # Contact operations
│   ├── template_service.py         # Template management
│   ├── report_service.py           # Report generation
│   └── csv_service.py              # CSV import/export with pandas
│
├── ui/
│   ├── app.py                      # Main application window
│   ├── theme.py                    # ttkbootstrap theme config
│   ├── widgets/                    # Reusable custom widgets
│   │   ├── data_table.py           # Sortable/filterable Treeview
│   │   ├── status_badge.py         # Colored status indicators
│   │   ├── progress_card.py        # KPI cards
│   │   ├── merge_tag_picker.py     # Template merge tag selector
│   │   ├── file_attachment.py      # Attachment mode selector
│   │   └── chart_widget.py         # Matplotlib embedded chart
│   ├── dialogs/
│   │   ├── confirm_dialog.py
│   │   ├── csv_import_wizard.py    # 3-step CSV import
│   │   └── user_form_dialog.py
│   └── views/
│       ├── login_view.py
│       ├── dashboard_view.py
│       ├── campaign_list_view.py
│       ├── campaign_detail_view.py
│       ├── contact_list_view.py
│       ├── template_editor_view.py
│       ├── ab_test_view.py
│       ├── reports_view.py
│       ├── user_management_view.py
│       ├── mail_accounts_view.py
│       ├── suppression_view.py
│       └── settings_view.py
│
├── mail_worker/                    # Background mail service (Python)
│   ├── worker.py                   # Main worker loop
│   ├── outlook_service.py          # Outlook COM Interop via pywin32
│   ├── reply_detector.py           # Reply detection
│   └── unsub_detector.py           # Unsubscribe detection (EN + FR)
│
├── assets/
│   ├── icon.ico
│   └── logo.png
│
└── scripts/
    ├── build.bat                   # PyInstaller build
    └── install.bat                 # Installation script
```

## API Endpoints (Existing Backend)

### Authentication
- POST /api/auth/login → returns JWT token
- POST /api/auth/refresh → refresh token

### Campaigns
- GET/POST /api/campaigns
- GET/PUT/DELETE /api/campaigns/{id}
- GET/POST /api/campaigns/{id}/steps

### Contacts
- GET/POST /api/contactlists
- GET /api/contactlists/{id}/contacts
- POST /api/contactlists/{id}/contacts/import

### Email Steps & Attachments
- GET/POST/PUT /api/emailsteps/{id}
- POST /api/emailsteps/{id}/attachments
- GET /api/download/{token} — tracked download

### Reports
- GET /api/reports/campaign/{id}
- GET /api/reports/downloads/{id}

### Users & Mail Accounts (Admin)
- GET/POST/PUT /api/users
- GET/POST/PUT /api/mailaccounts

### Suppression List
- GET /api/suppression
- POST /api/suppression
- GET /api/suppression/check?email=...

### Email Queue (Mail Service)
- GET /api/emailqueue/pending
- POST /api/emailqueue/{id}/sent
- POST /api/emailqueue/{id}/skip

### CRM Sync (for external CRM)
- GET /api/sync/contacts?since=...
- GET /api/sync/status-changes?since=...
- GET /api/sync/activities?since=...
- POST /api/sync/crm-updates
- POST /api/sync/acknowledge

## Database Schema (Existing)

Main tables (already created in PostgreSQL):
- **users**: standalone auth with BCrypt, roles (Admin/Manager/User)
- **mail_accounts**: email accounts with daily/hourly limits, warmup mode
- **contact_lists** → **contacts**: 10 custom fields (custom1-custom10) with labels
- **campaigns**: status (Draft/Active/Paused/Completed), sending config
- **email_steps**: sequence with subject/body templates
- **attachments**: delivery_mode (Attachment/Link), download_token
- **campaign_contacts**: per-contact status tracking
- **email_logs**: sent email history
- **download_logs**: file download click tracking
- **suppression_list**: global/campaign unsubscribe
- **ab_tests**: A/B test configuration and results
- **audit_logs**: security events

## User Roles & Permissions

- **Admin**: Full access (users, mail accounts, CRM config, all campaigns)
- **Manager**: Create/manage campaigns, view all campaigns, manage suppression
- **User**: Create/manage own campaigns only, limited reports

## Key Business Rules

- Campaign ID format: ISIT-{YY}{NNNN} (e.g., ISIT-250042)
- Merge tags: {{FirstName}}, {{Company}}, {{Custom1}} ... {{Custom10}}
- Unsubscribe keywords EN: UNSUBSCRIBE, STOP, REMOVE, OPT OUT, OPT-OUT
- Unsubscribe keywords FR: DÉSINSCRIRE, DÉSINSCRIPTION, STOP, ARRÊTER, SUPPRIMER
- Suppression list checked BEFORE every email send
- All timestamps in UTC
- Anti-spam: randomized delays ±15min, business hours Mon-Fri 09:00-17:00
- Warmup: 20% → 40% → 60% → 80% → 100% over 22 days

## Coding Conventions (Python)

- Type hints on all functions
- Dataclasses for models
- Views (UI) → Services (logic) → ApiClient (HTTP)
- Logging via built-in logging module
- Config via config.yaml
- ttkbootstrap "cosmo" theme for Windows 11 look
- All strings support French characters (UTF-8)

## Claude Code Session Prompts

Use these prompts in order to build the Python client:

### Session 1: Project Setup + API Client
```
Read CLAUDE.md and docs/TkinterClientGuide.md.
Create the Python project in client/ with:
- main.py, config.yaml, requirements.txt
- core/api_client.py (full REST client with JWT auth, all endpoints listed in CLAUDE.md)
- core/models.py (dataclasses for User, Campaign, Contact, EmailStep, etc.)
- core/exceptions.py
Test the API client can connect and login to the existing backend.
```

### Session 2: Login + Main Window
```
Implement:
- ui/views/login_view.py (login form with ttkbootstrap "cosmo" theme)
- ui/app.py (main window with sidebar navigation, role-aware menu items)
Include logout, session timeout handling, and connection error display.
```

### Session 3: Dashboard
```
Implement ui/views/dashboard_view.py with:
- 4 KPI cards (Active Campaigns, Total Contacts, Emails Sent 30d, Response Rate)
- Active campaigns table (Treeview with status, progress, contacts)
- Auto-refresh button
Load all data from the existing API.
```

### Session 4: Campaign Management
```
Implement:
- ui/views/campaign_list_view.py (list with filters, search, create/edit/delete)
- ui/views/campaign_detail_view.py with tabs:
  - Overview (stats, progress)
  - Sequence (email steps, add/edit/reorder)
  - Contacts (status table)
  - A/B Tests
  - Reports
```

### Session 5: Contact Management + CSV Import
```
Implement:
- ui/views/contact_list_view.py (list, search, export CSV)
- ui/dialogs/csv_import_wizard.py (3-step wizard):
  Step 1: Upload & preview CSV
  Step 2: Field mapping with auto-detect (10 custom fields)
  Step 3: Validation & import
- services/csv_service.py using pandas
```

### Session 6: Template Editor
```
Implement ui/views/template_editor_view.py with:
- Subject line editor
- Body editor (ScrolledText)
- Merge tag picker (Contact, Custom1-10, Sender, Campaign)
- Live preview with sample contact data
- Fallback value configuration for empty fields
```

### Session 7: Attachments + Reports
```
Implement:
- ui/widgets/file_attachment.py (add file, choose Attachment/Link mode)
  Show warning for Link mode: internal network only
- ui/views/reports_view.py with matplotlib charts:
  Campaign progress, response rates, status distribution, download stats
- PDF/CSV export using fpdf2 and pandas
```

### Session 8: Admin Screens
```
Implement (Admin role only):
- ui/views/user_management_view.py (create, edit, deactivate, reset password)
- ui/views/mail_accounts_view.py (add accounts, set limits, warmup toggle)
- ui/views/suppression_view.py (search, add/remove, import/export)
- ui/views/settings_view.py (API connection test, theme selection)
```

### Session 9: Mail Worker
```
Implement mail_worker/ with pywin32:
- outlook_service.py (send email, scan folders, mark read, move)
- reply_detector.py (match replies to contacts, stop sequence)
- unsub_detector.py (EN + FR keywords, add to suppression)
- worker.py (main loop with schedule library)
Test with the existing .NET API email queue endpoints.
```

### Session 10: Packaging
```
Create scripts/build.bat (PyInstaller → single .exe)
Create scripts/install.bat (create folders, copy files, desktop shortcut)
Create scripts/install-mailservice.bat (NSSM Windows Service)
Test the packaged .exe runs standalone on a clean Windows machine.
```
