# Lead Generator Standalone — Claude Code Instructions

**Version:** Standalone Lite (Single User)  
**Database:** SQLite (local file)  
**Outlook:** Classic only (COM Interop)  
**No:** API, Login, A/B Testing, Link Mode, CRM Sync

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Feature Comparison](#2-feature-comparison)
3. [Project Structure](#3-project-structure)
4. [Database Schema (SQLite)](#4-database-schema-sqlite)
5. [Claude Code Session Prompts](#5-claude-code-session-prompts)
6. [Migration Tool](#6-migration-tool)
7. [Packaging & Installation](#7-packaging--installation)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    STANDALONE PC (Single User)                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Python Tkinter GUI (ttkbootstrap)            │  │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             │                                   │
│                    ┌────────┴────────┐                          │
│                    │  Services Layer │                          │
│                    │  (Business Logic)│                          │
│                    └────────┬────────┘                          │
│           ┌─────────────────┼─────────────────┐                 │
│           ▼                 ▼                 ▼                 │
│  ┌─────────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │     SQLite      │ │   Outlook   │ │   Config (YAML)     │   │
│  │   (leadgen.db)  │ │  (pywin32)  │ │                     │   │
│  └─────────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Differences from Multi-User Version:**
- No .NET API server — Python accesses SQLite directly
- No authentication — app opens immediately
- Single user — no roles, no permissions checks
- Attachments: only "Attachment" mode (no Link tracking)
- No A/B testing
- No CRM synchronization

---

## 2. Feature Comparison

| Feature | Multi-User | Standalone |
|---------|:----------:|:----------:|
| Campaigns & Sequences | ✅ | ✅ |
| Contact Lists | ✅ | ✅ |
| CSV Import (10 custom fields) | ✅ | ✅ |
| Template Editor + Merge Tags | ✅ | ✅ |
| Email Sending via Outlook | ✅ | ✅ |
| Reply Detection | ✅ | ✅ |
| Unsubscribe Detection (EN+FR) | ✅ | ✅ |
| Suppression List | ✅ | ✅ |
| Basic Reports | ✅ | ✅ |
| Email Attachments (direct) | ✅ | ✅ |
| Attachment Link Tracking | ✅ | ❌ |
| A/B Testing | ✅ | ❌ |
| Multi-User / Roles | ✅ | ❌ |
| CRM Sync | ✅ | ❌ |
| Login / Authentication | ✅ | ❌ |
| PostgreSQL Database | ✅ | ❌ (SQLite) |
| Migration to Multi-User | — | ✅ |

---

## 3. Project Structure

```
leadgenerator-standalone/
├── main.py                         # Application entry point
├── config.yaml                     # User configuration
├── requirements.txt                # Python dependencies
│
├── data/
│   ├── leadgen.db                  # SQLite database (created on first run)
│   └── files/                      # Attachment storage
│
├── core/
│   ├── __init__.py
│   ├── database.py                 # SQLite connection + migrations
│   ├── models.py                   # Data classes
│   └── exceptions.py               # Custom exceptions
│
├── services/
│   ├── __init__.py
│   ├── campaign_service.py         # Campaign CRUD + business logic
│   ├── contact_service.py          # Contact CRUD
│   ├── template_service.py         # Template management
│   ├── email_service.py            # Email queue + sending logic
│   ├── suppression_service.py      # Suppression list management
│   ├── report_service.py           # Report generation
│   └── csv_service.py              # CSV import/export
│
├── outlook/
│   ├── __init__.py
│   ├── outlook_service.py          # Outlook COM Interop (send, scan)
│   ├── reply_detector.py           # Reply detection logic
│   └── unsub_detector.py           # Unsubscribe detection (EN+FR)
│
├── ui/
│   ├── __init__.py
│   ├── app.py                      # Main application window
│   ├── theme.py                    # ttkbootstrap theme
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── data_table.py           # Sortable Treeview table
│   │   ├── status_badge.py         # Status indicator
│   │   ├── progress_card.py        # KPI card widget
│   │   ├── merge_tag_picker.py     # Template merge tags
│   │   └── attachment_picker.py    # File attachment selector
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── confirm_dialog.py
│   │   ├── csv_import_wizard.py    # 3-step CSV import
│   │   ├── campaign_wizard.py      # Campaign creation wizard
│   │   └── migration_dialog.py     # Export for multi-user migration
│   └── views/
│       ├── __init__.py
│       ├── dashboard_view.py       # Overview + KPIs
│       ├── campaign_list_view.py   # Campaign list
│       ├── campaign_detail_view.py # Campaign edit (sequence, contacts)
│       ├── contact_list_view.py    # Contact lists management
│       ├── template_editor_view.py # Email template editor
│       ├── suppression_view.py     # Suppression list
│       ├── reports_view.py         # Basic reports
│       └── settings_view.py        # App settings + migration export
│
├── migration/
│   ├── __init__.py
│   ├── exporter.py                 # Export SQLite to JSON/SQL
│   └── postgresql_importer.py      # Import to PostgreSQL (run on server)
│
├── assets/
│   ├── icon.ico
│   └── logo.png
│
├── scripts/
│   ├── build.bat                   # PyInstaller build
│   └── install.bat                 # Installation script
│
└── tests/
    ├── test_database.py
    ├── test_csv_import.py
    └── test_outlook.py
```

---

## 4. Database Schema (SQLite)

```sql
-- ============================================================
-- Lead Generator Standalone — SQLite Schema
-- ============================================================

-- Settings (key-value store for app configuration)
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Mail Account (single account for standalone)
CREATE TABLE mail_account (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT NOT NULL UNIQUE,
    display_name TEXT,
    daily_limit INTEGER DEFAULT 50,
    hourly_limit INTEGER DEFAULT 10,
    current_daily_count INTEGER DEFAULT 0,
    last_count_reset TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Contact Lists
CREATE TABLE contact_lists (
    list_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    -- Custom field labels for this list
    custom1_label TEXT,
    custom2_label TEXT,
    custom3_label TEXT,
    custom4_label TEXT,
    custom5_label TEXT,
    custom6_label TEXT,
    custom7_label TEXT,
    custom8_label TEXT,
    custom9_label TEXT,
    custom10_label TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Contacts
CREATE TABLE contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL REFERENCES contact_lists(list_id) ON DELETE CASCADE,
    title TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT NOT NULL,
    position TEXT,
    phone TEXT,
    linkedin_url TEXT,
    source TEXT,
    -- 10 Custom fields
    custom1 TEXT,
    custom2 TEXT,
    custom3 TEXT,
    custom4 TEXT,
    custom5 TEXT,
    custom6 TEXT,
    custom7 TEXT,
    custom8 TEXT,
    custom9 TEXT,
    custom10 TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(list_id, email)
);

-- Campaigns
CREATE TABLE campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    campaign_ref TEXT NOT NULL UNIQUE, -- ISIT-25xxxx
    contact_list_id INTEGER REFERENCES contact_lists(list_id),
    status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Active', 'Paused', 'Completed', 'Archived')),
    -- Sending Configuration
    inter_email_delay_minutes INTEGER DEFAULT 30,
    sequence_step_delay_days INTEGER DEFAULT 3,
    sending_window_start TEXT DEFAULT '09:00',
    sending_window_end TEXT DEFAULT '17:00',
    sending_days TEXT DEFAULT 'Mon,Tue,Wed,Thu,Fri',
    randomization_minutes INTEGER DEFAULT 15,
    daily_send_limit INTEGER DEFAULT 50,
    -- Dates
    start_date TEXT,
    end_date TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Email Steps (Sequence)
CREATE TABLE email_steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    delay_days INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(campaign_id, step_number)
);

-- Attachments (Attachment mode only — no Link tracking)
CREATE TABLE attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES email_steps(step_id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Campaign Contacts (per-contact status tracking)
CREATE TABLE campaign_contacts (
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    contact_id INTEGER NOT NULL REFERENCES contacts(contact_id) ON DELETE CASCADE,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'InProgress', 'Responded', 'Completed', 'Bounced', 'Unsubscribed', 'OptedOut', 'Paused')),
    current_step INTEGER DEFAULT 0,
    last_email_sent_at TEXT,
    next_email_scheduled_at TEXT,
    responded_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (campaign_id, contact_id)
);

-- Email Log
CREATE TABLE email_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    contact_id INTEGER REFERENCES contacts(contact_id),
    step_id INTEGER REFERENCES email_steps(step_id),
    subject TEXT,
    sent_at TEXT DEFAULT (datetime('now')),
    status TEXT NOT NULL CHECK(status IN ('Sent', 'Failed', 'Bounced')),
    error_message TEXT,
    outlook_entry_id TEXT
);

-- Suppression List
CREATE TABLE suppression_list (
    email TEXT PRIMARY KEY,
    scope TEXT DEFAULT 'Global' CHECK(scope IN ('Global', 'Campaign')),
    source TEXT NOT NULL CHECK(source IN ('EmailReply', 'Manual', 'Bounce', 'Complaint')),
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    reason TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Email Queue (pending emails to send)
CREATE TABLE email_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id),
    contact_id INTEGER NOT NULL REFERENCES contacts(contact_id),
    step_id INTEGER NOT NULL REFERENCES email_steps(step_id),
    scheduled_at TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Sending', 'Sent', 'Failed', 'Skipped')),
    attempts INTEGER DEFAULT 0,
    last_attempt_at TEXT,
    error_message TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_list ON contacts(list_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX idx_campaign_contacts_next ON campaign_contacts(next_email_scheduled_at);
CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_scheduled ON email_queue(scheduled_at);
CREATE INDEX idx_suppression_email ON suppression_list(email);

-- Initial Settings
INSERT INTO settings (key, value) VALUES 
    ('app_version', '1.0.0'),
    ('last_campaign_number', '0'),
    ('outlook_scan_interval_seconds', '60'),
    ('unsubscribe_keywords_en', 'UNSUBSCRIBE,STOP,REMOVE,OPT OUT,OPT-OUT'),
    ('unsubscribe_keywords_fr', 'DÉSINSCRIRE,DÉSINSCRIPTION,STOP,ARRÊTER,SUPPRIMER'),
    ('scan_folders', 'Inbox,Unsubscribe');
```

---

## 5. Claude Code Session Prompts

### CLAUDE.md (Put in project root)

```markdown
# Lead Generator Standalone

## Overview
Single-user desktop app for email marketing campaigns.
Direct SQLite access (no API). Outlook Classic integration via pywin32.

## Stack
- Python 3.10+
- ttkbootstrap (GUI)
- SQLite (database)
- pywin32 (Outlook COM)
- pandas (CSV)
- matplotlib (charts)

## Key Rules
- No login/authentication (single user)
- No API layer — services access SQLite directly
- No A/B testing
- Attachments: direct only (no Link tracking mode)
- No CRM sync
- Unsubscribe keywords: EN + FR
- Campaign ID format: ISIT-{YY}{NNNN}
- Merge tags: {{FirstName}}, {{Custom1}}...{{Custom10}}
- All timestamps stored as ISO 8601 TEXT in SQLite

## Database
SQLite file at: data/leadgen.db
Schema in: docs/schema.sql

## Coding Style
- Type hints on all functions
- Dataclasses for models
- Services access database via core/database.py
- UI uses ttkbootstrap "cosmo" theme
- Logging via Python logging module
```

---

### Session 1: Project Setup + Database

```
Create the Lead Generator Standalone project structure.

Read CLAUDE.md for context.

Create:
1. main.py (entry point — creates DB if not exists, launches UI)
2. config.yaml (default settings)
3. requirements.txt (ttkbootstrap, pandas, matplotlib, pywin32, pyyaml)
4. core/database.py:
   - SQLite connection manager (context manager pattern)
   - init_database() — creates tables from embedded schema
   - get_setting(key) / set_setting(key, value)
   - generate_campaign_ref() — returns next ISIT-{YY}{NNNN}
5. core/models.py — dataclasses for:
   - Contact, ContactList, Campaign, EmailStep, Attachment
   - CampaignContact, EmailLog, SuppressionEntry, QueuedEmail
6. core/exceptions.py — custom exceptions

Embed the full SQLite schema in database.py.
Database file location: data/leadgen.db (create data/ folder if missing).
```

---

### Session 2: Services — Contacts & CSV Import

```
Create contact management services.

Create:
1. services/contact_service.py:
   - get_all_lists() → List[ContactList]
   - get_list(list_id) → ContactList
   - create_list(name, description, custom_labels) → ContactList
   - delete_list(list_id)
   - get_contacts(list_id) → List[Contact]
   - get_contact(contact_id) → Contact
   - create_contact(list_id, contact_data) → Contact
   - update_contact(contact_id, contact_data)
   - delete_contact(contact_id)
   - search_contacts(list_id, query) → List[Contact]
   - check_duplicate(list_id, email) → bool

2. services/csv_service.py:
   - read_csv_preview(file_path, max_rows=5) → (headers, preview_rows, total_count)
   - auto_map_fields(csv_headers) → dict mapping
   - import_csv(file_path, list_id, field_mapping, custom_labels) → (imported_count, errors)
   - export_csv(list_id, file_path, fields=None)

Field mapping must support:
- Standard fields: title, first_name, last_name, email, company, position, phone, linkedin_url, source
- Custom fields: custom1 through custom10
- Auto-detect common French/English column names

All database access via core/database.py context manager.
```

---

### Session 3: Services — Campaigns & Email Steps

```
Create campaign management services.

Create:
1. services/campaign_service.py:
   - get_all_campaigns(status_filter=None) → List[Campaign]
   - get_campaign(campaign_id) → Campaign with steps and stats
   - create_campaign(data) → Campaign (auto-generate campaign_ref)
   - update_campaign(campaign_id, data)
   - delete_campaign(campaign_id)
   - activate_campaign(campaign_id) — set status='Active', populate email_queue
   - pause_campaign(campaign_id)
   - complete_campaign(campaign_id)
   - get_campaign_stats(campaign_id) → dict with counts by status
   
2. services/template_service.py:
   - get_steps(campaign_id) → List[EmailStep]
   - get_step(step_id) → EmailStep with attachments
   - create_step(campaign_id, step_number, subject, body, delay_days) → EmailStep
   - update_step(step_id, data)
   - delete_step(step_id)
   - reorder_steps(campaign_id, step_ids_in_order)
   - add_attachment(step_id, file_path) → Attachment (copy file to data/files/)
   - remove_attachment(attachment_id)
   - apply_merge_tags(template, contact) → rendered string

Merge tags to support:
{{Title}}, {{FirstName}}, {{LastName}}, {{FullName}}, {{Email}}, {{Company}}, {{Position}}, {{Phone}}
{{Custom1}} through {{Custom10}}
{{CampaignRef}}, {{UnsubscribeText}}

When activating campaign:
- Check all contacts not in suppression list
- Create email_queue entries for step 1 for all valid contacts
- Set campaign_contacts status to 'Pending'
```

---

### Session 4: Services — Email Queue & Suppression

```
Create email sending and suppression services.

Create:
1. services/email_service.py:
   - get_pending_emails(limit=10) → List[QueuedEmail] (with contact & step data)
   - mark_email_sent(queue_id, outlook_entry_id)
   - mark_email_failed(queue_id, error_message)
   - mark_email_skipped(queue_id, reason)
   - schedule_next_step(campaign_id, contact_id) — add next step to queue
   - process_queue_item(queued_email) → bool (checks suppression, returns if should send)
   - calculate_send_time(scheduled_at, randomization_minutes) → datetime

2. services/suppression_service.py:
   - is_suppressed(email) → bool
   - get_suppression_list() → List[SuppressionEntry]
   - add_to_suppression(email, source, scope='Global', campaign_id=None, reason=None)
   - remove_from_suppression(email)
   - import_suppression_list(emails: List[str], source='Manual')
   - export_suppression_list(file_path)

Suppression check must happen BEFORE sending any email.
When contact is suppressed mid-campaign, update campaign_contacts status.
```

---

### Session 5: Outlook Integration

```
Create Outlook COM Interop services using pywin32.

Create:
1. outlook/outlook_service.py:
   - __init__() — initialize COM, get Outlook application
   - is_outlook_running() → bool
   - get_default_account() → email address
   - send_email(to, subject, body, attachments=None, send_at=None) → entry_id
   - get_unread_emails(folder_name='Inbox', since=None) → List[OutlookEmail]
   - mark_as_read(entry_id)
   - move_to_folder(entry_id, folder_name)

2. outlook/reply_detector.py:
   - scan_for_replies() — scan inbox, match to contacts, update status to 'Responded'
   - match_email_to_contact(sender_email) → Contact or None
   - extract_campaign_ref(subject) → campaign_ref or None

3. outlook/unsub_detector.py:
   - scan_for_unsubscribes() — scan inbox + configured folders
   - contains_unsubscribe_keyword(subject, body) → bool
   - Keywords EN: UNSUBSCRIBE, STOP, REMOVE, OPT OUT, OPT-OUT
   - Keywords FR: DÉSINSCRIRE, DÉSINSCRIPTION, STOP, ARRÊTER, SUPPRIMER
   - process_unsubscribe(email_address, campaign_ref=None) — add to suppression, update contacts

Handle Outlook not running gracefully (show warning in UI).
Use pythoncom.CoInitialize() for thread safety.
```

---

### Session 6: Background Worker

```
Create background worker for email processing.

Create:
1. core/worker.py:
   - EmailWorker class that runs in a separate thread
   - start() / stop() methods
   - Main loop (every N seconds from config):
     a. Process email queue (get pending, check suppression, send via Outlook)
     b. Scan for replies (update contact status)
     c. Scan for unsubscribes (add to suppression)
   - Respect sending window (business hours from campaign config)
   - Respect daily/hourly limits from mail_account
   - Apply randomization to send times
   - Handle errors gracefully (retry logic, max 3 attempts)

2. Signals/callbacks to update UI:
   - on_email_sent(campaign_id, contact_id)
   - on_reply_detected(campaign_id, contact_id)
   - on_unsubscribe_detected(email)
   - on_error(message)

Worker should be started when app launches (if a campaign is active).
Worker can be paused/resumed from UI.
```

---

### Session 7: UI — Main Window & Dashboard

```
Create main application UI with ttkbootstrap.

Create:
1. ui/app.py — MainApplication class:
   - ttkbootstrap Window with "cosmo" theme
   - Sidebar navigation (no login, direct to dashboard)
   - Navigation items: Dashboard, Campaigns, Contacts, Templates, Suppression, Reports, Settings
   - Status bar showing: Outlook status, worker status, next scheduled email
   - Content frame that swaps views

2. ui/views/dashboard_view.py:
   - 4 KPI cards: Active Campaigns, Total Contacts, Emails Sent (30d), Response Rate
   - Active campaigns table (Treeview): name, ref, contacts, sent, responded, progress, status
   - Quick actions: New Campaign, Import Contacts
   - Auto-refresh every 30 seconds

3. ui/widgets/progress_card.py — reusable KPI card widget
4. ui/widgets/data_table.py — sortable Treeview with search

App should:
- Initialize database on startup
- Start background worker if any campaign is Active
- Show warning if Outlook not running
```

---

### Session 8: UI — Campaigns

```
Create campaign management views.

Create:
1. ui/views/campaign_list_view.py:
   - Filter by status (All, Draft, Active, Paused, Completed)
   - Search by name
   - Campaigns table: name, ref, status, contacts, progress, created
   - Actions: New, Edit, Duplicate, Delete, Activate, Pause
   - Double-click to open detail view

2. ui/views/campaign_detail_view.py with tabs:
   - Overview tab: name, description, status, stats, progress bar
   - Sequence tab: list of email steps, add/edit/delete/reorder
   - Contacts tab: list with status, can remove or pause individual contacts
   - Settings tab: sending window, delays, limits
   - Actions: Save, Activate, Pause, Complete

3. ui/dialogs/campaign_wizard.py — new campaign creation:
   - Step 1: Name, description
   - Step 2: Select contact list
   - Step 3: Review and create (as Draft)

4. ui/dialogs/step_editor_dialog.py:
   - Subject line input
   - Body editor (ScrolledText)
   - Merge tag picker
   - Attachment list (add/remove files)
   - Delay days setting
```

---

### Session 9: UI — Contacts & CSV Import

```
Create contact management views.

Create:
1. ui/views/contact_list_view.py:
   - Left panel: list of contact lists
   - Right panel: contacts in selected list
   - Contact table: name, email, company, status (if in any campaign)
   - Actions: New List, Delete List, Import CSV, Export CSV
   - Search within list

2. ui/dialogs/csv_import_wizard.py (3 steps):
   - Step 1: Select file, show preview (first 5 rows)
   - Step 2: Field mapping with dropdowns
     - Auto-detect common names
     - Show merge tag for each mapped field
     - Configure custom field labels
   - Step 3: Validation results, import button
   - Progress bar during import
   - Summary: X imported, Y duplicates skipped, Z errors

3. ui/dialogs/contact_edit_dialog.py:
   - Edit single contact
   - All fields including custom1-10
```

---

### Session 10: UI — Template Editor

```
Create template editor view.

Create:
1. ui/views/template_editor_view.py:
   - Left panel: list of campaigns → steps
   - Right panel: editor for selected step
   
2. Editor panel:
   - Subject line entry
   - Body editor (ScrolledText with larger font)
   - Merge tag picker (categorized buttons):
     - Contact: Title, FirstName, LastName, FullName, Email, Company, Position, Phone
     - Custom: Custom1...Custom10 (show labels if set)
     - Campaign: CampaignRef, UnsubscribeText
   - Click tag button → insert at cursor
   - Attachments section: list files, Add/Remove buttons

3. Preview panel (right side):
   - Live preview with sample data
   - Sample contact selector (dropdown of real contacts)
   - Shows rendered subject and body

4. ui/widgets/merge_tag_picker.py — reusable tag picker widget
```

---

### Session 11: UI — Suppression, Reports, Settings

```
Create remaining views.

Create:
1. ui/views/suppression_view.py:
   - Suppression list table: email, scope, source, date
   - Search/filter
   - Actions: Add manually, Remove, Import from CSV, Export to CSV
   - Add dialog: email input, scope selection (Global/Campaign)

2. ui/views/reports_view.py:
   - Campaign selector dropdown
   - Stats cards: Total, Sent, Responded, Bounced, Unsubscribed
   - Simple bar chart (matplotlib): status distribution
   - Email log table: date, contact, subject, status
   - Export button (CSV)

3. ui/views/settings_view.py:
   - Mail Account section: email address, display name, daily/hourly limits
   - Sending defaults: window times, delays, randomization
   - Outlook settings: scan interval, scan folders
   - Data section: database location, attachment folder
   - Migration section: Export button (opens migration dialog)
   - About section: version info

4. ui/dialogs/migration_dialog.py:
   - Export data for multi-user migration
   - Options: All data, or select campaigns
   - Export format: JSON file
   - Shows progress and success message
```

---

### Session 12: Migration Tool

```
Create migration tool for exporting to multi-user PostgreSQL.

Create:
1. migration/exporter.py:
   - export_to_json(output_path, campaign_ids=None) → creates JSON file with:
     - contact_lists (with custom labels)
     - contacts
     - campaigns
     - email_steps
     - attachments (references to files)
     - campaign_contacts (with statuses)
     - email_logs
     - suppression_list
   - copy_attachment_files(output_folder) — copies all attachment files

Export JSON structure:
{
  "export_version": "1.0",
  "exported_at": "ISO timestamp",
  "source": "standalone",
  "data": {
    "contact_lists": [...],
    "contacts": [...],
    "campaigns": [...],
    "email_steps": [...],
    "attachments": [...],
    "campaign_contacts": [...],
    "email_logs": [...],
    "suppression_list": [...]
  }
}

2. migration/postgresql_importer.py (separate script for server):
   - import_from_json(json_path, db_connection_string, target_user_id)
   - Conflict handling:
     - Contacts: skip if email exists in any list
     - Campaigns: generate new campaign_ref (keep old as note in description)
     - Suppression: merge (add if not exists)
   - Maps all data to target_user_id
   - Returns import summary

Create docs/migration_guide.md with instructions.
```

---

### Session 13: Packaging

```
Create build and installation scripts.

Create:
1. scripts/build.bat:
   - PyInstaller command to create single .exe
   - Include: config.yaml, assets/, data/ folder
   - Name: LeadGeneratorStandalone.exe
   - Icon: assets/icon.ico
   - Exclude: unnecessary modules

2. scripts/install.bat:
   - Create C:\LeadGenerator\ folder
   - Copy .exe and assets
   - Create data\ subfolder
   - Create desktop shortcut
   - Show completion message

3. Update config.yaml with sensible defaults:
   - Data path: ./data/
   - Default sending window: 09:00-17:00
   - Default daily limit: 50
   - Scan interval: 60 seconds

4. Create README.md with:
   - Features overview
   - Installation instructions
   - First run guide
   - How to migrate to multi-user version

Test that packaged .exe runs on clean Windows 11 machine.
```

---

## 6. Migration Tool

### Export Format (JSON)

```json
{
  "export_version": "1.0",
  "exported_at": "2025-01-27T14:30:00Z",
  "source": "standalone",
  "source_version": "1.0.0",
  "data": {
    "contact_lists": [
      {
        "list_id": 1,
        "name": "Q1 Prospects",
        "description": "...",
        "custom1_label": "Industry",
        "custom2_label": "Budget",
        ...
      }
    ],
    "contacts": [
      {
        "contact_id": 1,
        "list_id": 1,
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jd@example.com",
        "company": "Acme",
        "custom1": "Manufacturing",
        ...
      }
    ],
    "campaigns": [
      {
        "campaign_id": 1,
        "name": "Q1 Outreach",
        "campaign_ref": "ISIT-250001",
        "status": "Completed",
        ...
      }
    ],
    ...
  }
}
```

### PostgreSQL Import Script Usage

```bash
# Run on the multi-user server
python postgresql_importer.py \
  --json-file export_20250127.json \
  --db-host localhost \
  --db-name leadgenerator \
  --db-user leadgen_user \
  --db-password YourPassword \
  --target-user-id "uuid-of-user-to-assign-data"
```

---

## 7. Packaging & Installation

### requirements.txt

```
ttkbootstrap>=1.10.1
Pillow>=10.0.0
pandas>=2.0.0
matplotlib>=3.7.0
pywin32>=306
pyyaml>=6.0.1
```

### Build Command

```batch
pyinstaller ^
  --name "LeadGeneratorStandalone" ^
  --onefile ^
  --windowed ^
  --icon=assets/icon.ico ^
  --add-data "config.yaml;." ^
  --add-data "assets;assets" ^
  --hidden-import=win32com.client ^
  --hidden-import=win32timezone ^
  main.py
```

### Installation Result

```
C:\LeadGenerator\
├── LeadGeneratorStandalone.exe
├── config.yaml
├── assets\
│   ├── icon.ico
│   └── logo.png
└── data\
    ├── leadgen.db          (created on first run)
    └── files\              (attachments)
```

---

## Quick Start After Installation

1. **First Launch**: App creates database automatically
2. **Configure Mail**: Settings → Mail Account → Enter your Outlook email
3. **Import Contacts**: Contacts → New List → Import CSV
4. **Create Campaign**: Campaigns → New → Select list → Add email steps
5. **Activate**: Campaign → Activate (starts sending)
6. **Monitor**: Dashboard shows progress, replies, unsubscribes

---

**End of Claude Code Instructions**
