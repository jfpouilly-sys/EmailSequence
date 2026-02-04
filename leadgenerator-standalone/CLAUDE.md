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
