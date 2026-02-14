# Functional Specification v2.0
## Lead Generation & Digital Marketing Campaign Tool

**Document Version:** 2.0  
**Last Updated:** January 2025  
**Status:** ✅ Complete — Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack](#2-technology-stack)
3. [Deployment Architecture](#3-deployment-architecture)
4. [User Management](#4-user-management)
5. [Mail Account Management](#5-mail-account-management)
6. [Campaign Management](#6-campaign-management)
7. [Contact List Management](#7-contact-list-management)
8. [Email Sequence & Templates](#8-email-sequence--templates)
9. [Contact Status & Workflow](#9-contact-status--workflow)
10. [Sending Engine](#10-sending-engine)
11. [Unsubscribe Management](#11-unsubscribe-management)
12. [A/B Testing Framework](#12-ab-testing-framework)
13. [CRM Integration](#13-crm-integration)
14. [Reporting & KPIs](#14-reporting--kpis)
15. [Data Model](#15-data-model)
16. [User Interface](#16-user-interface)
17. [Implementation Phases](#17-implementation-phases)
18. [Open Questions](#18-open-questions)

---

## 1. Executive Summary

This document defines the functional requirements for a **multi-user desktop application** enabling business development teams to manage multi-touch email campaigns. The tool automates personalized email sequences through local mail clients while tracking engagement and preventing contact fatigue across campaigns.

### Key Features

- Multi-user access with role-based permissions
- Multiple mail account support with intelligent distribution
- A/B testing framework for campaign optimization
- Bidirectional CRM integration
- Unsubscribe management and compliance
- Cross-campaign contact intelligence

---

## 2. Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Architecture** | Client-Server | Multi-user concurrent access |
| **Database** | PostgreSQL | Concurrent writes, network access, robust |
| **Server** | .NET 8 API (REST) | Central business logic, CRM sync |
| **Client** | WPF + API client | Thin client, shared data |
| **Mail Service** | Windows Service | Background processing, multiple accounts |
| **Mail Integration** | Outlook COM Interop / MAPI | Native integration with default mailer |
| **CRM Integration** | REST API + Webhooks | Bi-directional sync |
| **Reporting** | LiveCharts2 or ScottPlot | Open-source charting for .NET |
| **CSV Handling** | CsvHelper library | Robust parsing with mapping support |

---

## 3. Deployment Architecture

> **All components run on the internal network.** No external/public endpoints required.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTERNAL NETWORK / VPN                              │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │   PostgreSQL    │◄──►│   API Server    │◄───│   Home-made CRM         │  │
│  │   Database      │    │   (.NET 8)      │    │   (pulls data)          │  │
│  └─────────────────┘    └────────┬────────┘    │   ⚠️ On-site or VPN only │  │
│                                  │             └─────────────────────────┘  │
│                                  │ HTTPS/REST                               │
│        ┌─────────────────────────┼─────────────────────────┐                │
│        │                         │                         │                │
│        ▼                         ▼                         ▼                │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐     │
│  │   WORKSTATION 1   │   │   WORKSTATION 2   │   │   WORKSTATION 3   │     │
│  │  ┌─────────────┐  │   │  ┌─────────────┐  │   │  ┌─────────────┐  │     │
│  │  │ WPF Client  │  │   │  │ WPF Client  │  │   │  │ WPF Client  │  │     │
│  │  └─────────────┘  │   │  └─────────────┘  │   │  └─────────────┘  │     │
│  │  ┌─────────────┐  │   │  ┌─────────────┐  │   │  ┌─────────────┐  │     │
│  │  │ Mail Service│  │   │  │ Mail Service│  │   │  │ Mail Service│  │     │
│  │  │ • Send      │  │   │  │ • Send      │  │   │  │ • Send      │  │     │
│  │  │ • Reply Det.│  │   │  │ • Reply Det.│  │   │  │ • Reply Det.│  │     │
│  │  │ • Unsub Det.│  │   │  │ • Unsub Det.│  │   │  │ • Unsub Det.│  │     │
│  │  └─────────────┘  │   │  └─────────────┘  │   │  └─────────────┘  │     │
│  │  ┌─────────────┐  │   │  ┌─────────────┐  │   │  ┌─────────────┐  │     │
│  │  │   Outlook   │  │   │  │   Outlook   │  │   │  │   Outlook   │  │     │
│  │  └─────────────┘  │   │  └─────────────┘  │   │  └─────────────┘  │     │
│  └───────────────────┘   └───────────────────┘   └───────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Network Access Summary:**

| Component | Network Access |
|-----------|----------------|
| API Server | Internal only |
| PostgreSQL | Internal only |
| WPF Clients | Internal or VPN |
| CRM Integration | Internal or VPN |
| Download Links (Link mode) | Internal or VPN |

**Mail Service responsibilities per workstation:**
- **Send:** Queue and send emails via local Outlook
- **Reply Detection:** Monitor inbox for contact replies → stop sequence
- **Unsubscribe Detection:** Monitor inbox/folder for unsubscribe requests → update status

---

## 4. User Management

### 4.1 Authentication

> **Standalone accounts:** The application uses its own user database for authentication. No dependency on Windows AD/LDAP.

**Login Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     LEAD GENERATOR LOGIN                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        [Logo]                                   │
│                                                                 │
│     Username:    [________________________]                     │
│                                                                 │
│     Password:    [________________________]                     │
│                                                                 │
│     ☐ Remember me                                               │
│                                                                 │
│                      [    Login    ]                            │
│                                                                 │
│     Forgot password?                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Security Features:**

| Feature | Implementation |
|---------|----------------|
| Password hashing | BCrypt or Argon2 |
| Password policy | Min 8 chars, mixed case, number required |
| Session timeout | Configurable (default: 8 hours) |
| Failed login lockout | 5 attempts → 15 min lockout |
| Password reset | Email-based reset link (if SMTP configured) or Admin reset |
| Audit log | All logins logged (success/failure, IP, timestamp) |

### 4.2 User Data Model

| Field | Type | Description |
|-------|------|-------------|
| UserID | GUID | Primary key |
| Username | String | Login name |
| Email | String | User's email |
| PasswordHash | String | Encrypted password |
| Role | Enum | Admin / Manager / User |
| AssignedMailAccounts | List | Mail accounts user can send from |
| IsActive | Boolean | Account status |
| CreatedDate | DateTime | |
| LastLogin | DateTime | |

### 4.2 Role Permissions

| Permission | Admin | Manager | User |
|------------|:-----:|:-------:|:----:|
| Create/manage users | ✓ | — | — |
| Configure mail accounts | ✓ | — | — |
| Create campaigns | ✓ | ✓ | ✓ |
| Delete any campaign | ✓ | ✓ | — |
| Delete own campaign | ✓ | ✓ | ✓ |
| View all campaigns | ✓ | ✓ | — |
| View own campaigns | ✓ | ✓ | ✓ |
| Manage contact lists | ✓ | ✓ | ✓ |
| Access reports | ✓ | ✓ | Limited |
| Configure CRM integration | ✓ | — | — |
| Manage unsubscribe list | ✓ | ✓ | — |

### 4.3 Concurrency Handling

| Scenario | Resolution |
|----------|------------|
| Two users edit same campaign | Optimistic locking with conflict notification |
| Contact list being imported | Row-level locking, progress visible to others |
| Same contact in two campaigns | Cross-campaign check runs server-side |

---

## 5. Mail Account Management

### 5.1 Mail Account Data Model

| Field | Type | Description |
|-------|------|-------------|
| AccountID | GUID | Primary key |
| AccountName | String | Friendly name (e.g., "Sales Team 1") |
| EmailAddress | String | sender@company.com |
| AccountType | Enum | Outlook / Microsoft365 / SMTP |
| WorkstationID | String | Machine where Outlook is configured |
| DailyLimit | Int | Max emails/day for this account |
| HourlyLimit | Int | Max emails/hour |
| CurrentDailyCount | Int | Today's sent count |
| IsActive | Boolean | Available for sending |
| WarmupMode | Boolean | Gradual volume increase |
| WarmupDayCount | Int | Days in warmup |

### 5.2 Mail Account Distribution Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMPAIGN: Q1 Outreach                        │
│                    Contacts: 500                                │
│                                                                 │
│   Assigned Mail Accounts:                                       │
│   ┌─────────────────┬─────────────┬─────────────┬────────────┐  │
│   │ sales1@co.com   │ sales2@co.com│ biz@co.com  │ TOTAL      │  │
│   │ Limit: 50/day   │ Limit: 50/day│ Limit: 30/day│ 130/day   │  │
│   │ Assigned: 192   │ Assigned: 192│ Assigned: 116│ 500       │  │
│   └─────────────────┴─────────────┴─────────────┴────────────┘  │
│                                                                 │
│   Distribution Mode:  ○ Round-robin  ● Proportional  ○ Manual   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Account Assignment Options

| Mode | Description |
|------|-------------|
| **Round-robin** | Contacts distributed equally across accounts |
| **Proportional** | Distributed based on daily limit ratios |
| **Manual** | User assigns specific contacts to specific accounts |
| **Domain-based** | Match sender domain to recipient domain pattern |

### 5.4 Warmup Mode Protocol

| Day | Volume (% of limit) |
|-----|---------------------|
| 1–3 | 20% |
| 4–7 | 40% |
| 8–14 | 60% |
| 15–21 | 80% |
| 22+ | 100% |

---

## 6. Campaign Management

### 6.1 Campaign Creation

Each campaign contains:

- Campaign name and description
- Associated contact list (reusable or dedicated)
- Email sequence (1–10 emails, configurable)
- Sending configuration (delays, schedules)
- Assigned mail accounts
- Start/end dates
- Status: Draft / Active / Paused / Completed

### 6.2 Campaign Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Inter-email delay | 30 min | Minimum time between individual emails |
| Sequence step delay | 3 days | Time between sequence steps (Email 1 → Email 2) |
| Sending window | 09:00–17:00 | Business hours only |
| Sending days | Mon–Fri | Weekdays only |
| Daily send limit | 50/day | Per mail account |
| Randomization | ±15 min | Time variance to appear more human |

### 6.3 Campaign Identifier

- Format: `ISIT-{YY}{NNNN}` where YY = year, NNNN = auto-incremented
- Placed in email footer (small text) for compliance
- Hidden tracking ID in email headers (X-Campaign-ID) for internal tracking

---

## 7. Contact List Management

### 7.1 Contact Data Model

**Standard Fields (built-in):**

| Field | Type | Required | Merge Tag |
|-------|------|----------|-----------|
| ContactID | GUID | Auto | — |
| Title | String | No | `{{Title}}` |
| First Name | String | Yes | `{{FirstName}}` |
| Last Name | String | Yes | `{{LastName}}` |
| Email | String | Yes | `{{Email}}` |
| Company | String | Yes | `{{Company}}` |
| Position | String | No | `{{Position}}` |
| Phone | String | No | `{{Phone}}` |
| LinkedIn URL | String | No | `{{LinkedIn}}` |
| Source | String | No | `{{Source}}` |
| CRM_LeadID | String | No | — |
| CreatedDate | DateTime | Auto | — |
| ListID | GUID | Yes | — |

**Custom Fields (from CSV import):**

| Field | Type | Merge Tag | Description |
|-------|------|-----------|-------------|
| Custom1 | String | `{{Custom1}}` | User-defined field |
| Custom2 | String | `{{Custom2}}` | User-defined field |
| Custom3 | String | `{{Custom3}}` | User-defined field |
| Custom4 | String | `{{Custom4}}` | User-defined field |
| Custom5 | String | `{{Custom5}}` | User-defined field |
| Custom6 | String | `{{Custom6}}` | User-defined field |
| Custom7 | String | `{{Custom7}}` | User-defined field |
| Custom8 | String | `{{Custom8}}` | User-defined field |
| Custom9 | String | `{{Custom9}}` | User-defined field |
| Custom10 | String | `{{Custom10}}` | User-defined field |

> **Dynamic Fields:** During CSV import, users can map any CSV column to a Custom field. The custom field can be renamed for clarity (e.g., Custom1 → "Industry", Custom2 → "Pain Point").

### 7.2 CSV Import Wizard

> **Any column from the CSV can be mapped to a standard or custom field, then used as a merge tag in email templates.**

**Step 1: Upload & Preview**

```
┌─────────────────────────────────────────────────────────────────┐
│              CSV IMPORT - Step 1: Upload                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  File: contacts_Q1_campaign.csv                    [Change]     │
│  Encoding: UTF-8 (auto-detected)                                │
│  Rows: 523 (excluding header)                                   │
│                                                                 │
│  Preview (first 5 rows):                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ prenom  │ nom    │ email          │ societe │ secteur │ pb │ │
│  ├─────────┼────────┼────────────────┼─────────┼─────────┼────┤ │
│  │ Jean    │ Dupont │ jd@acme.fr     │ Acme    │ Indust. │ x  │ │
│  │ Marie   │ Martin │ mm@beta.com    │ Beta    │ Finance │ y  │ │
│  │ ...     │ ...    │ ...            │ ...     │ ...     │... │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                              [Next: Mapping →]  │
└─────────────────────────────────────────────────────────────────┘
```

**Step 2: Field Mapping**

```
┌─────────────────────────────────────────────────────────────────┐
│              CSV IMPORT - Step 2: Field Mapping                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Map your CSV columns to contact fields:                        │
│                                                                 │
│  CSV Column          →    Contact Field         Merge Tag       │
│  ──────────────────────────────────────────────────────────     │
│  "prenom"            →    [First Name      ▼]   {{FirstName}}   │
│  "nom"               →    [Last Name       ▼]   {{LastName}}    │
│  "email"             →    [Email           ▼]   {{Email}}       │
│  "societe"           →    [Company         ▼]   {{Company}}     │
│  "secteur"           →    [Custom1         ▼]   {{Custom1}}     │
│  "probleme"          →    [Custom2         ▼]   {{Custom2}}     │
│  "budget"            →    [Custom3         ▼]   {{Custom3}}     │
│  "source"            →    [Custom4         ▼]   {{Custom4}}     │
│  "telephone"         →    [Phone           ▼]   {{Phone}}       │
│  "notes"             →    [— Do not import ▼]   —               │
│                                                                 │
│  Available: Custom1–Custom10 (10 custom fields)                 │
│                                                                 │
│  ☑ Save this mapping for future imports                         │
│                                                                 │
│  Custom Field Labels (optional, for clarity):                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Custom1 display name: [Industry        ]  (was: "secteur") │ │
│  │ Custom2 display name: [Pain Point      ]  (was: "probleme")│ │
│  │ Custom3 display name: [Budget          ]  (was: "budget")  │ │
│  │ Custom4 display name: [Lead Source     ]  (was: "source")  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                              [← Back]   [Next: Validation →]    │
└─────────────────────────────────────────────────────────────────┘
```

**Step 3: Validation & Import**

```
┌─────────────────────────────────────────────────────────────────┐
│              CSV IMPORT - Step 3: Validation                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Validation Results:                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ✅ 518 contacts ready to import                            │ │
│  │ ⚠️  3 contacts with invalid email (will be skipped)        │ │
│  │ ⚠️  2 duplicate emails (will be merged)                    │ │
│  │ ❌  0 contacts missing required fields                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ☑ Skip contacts already in suppression list (found: 12)       │
│  ☑ Check for duplicates in existing contact lists              │
│  ○ Update existing contacts if email matches                    │
│  ● Create new contacts only, skip duplicates                    │
│                                                                 │
│  Import to list: [Q1 2025 Prospects      ▼]  or [+ New List]   │
│                                                                 │
│                              [← Back]   [Import 518 Contacts]   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Contact List Operations

- Import from CSV (with field mapping wizard)
- Export to CSV
- Duplicate detection (by email address)
- Bulk edit and delete
- Filter and search
- Reuse across multiple campaigns
- Shared vs. private lists

### 7.3 Cross-Campaign Intelligence

- When adding contacts to a campaign, system flags contacts already active in another campaign
- User options: exclude, include anyway, or delay until other campaign completes
- Visual indicator showing campaign overlap

---

## 8. Email Sequence & Templates

### 8.1 Sequence Structure

- Each sequence contains 1–10 ordered email steps (configurable)
- Each step has:
  - Step number
  - Subject line template
  - Body template (HTML or plain text)
  - Delay from previous step (configurable)
  - Optional A/B test variant

### 8.2 Template Personalization

> **All fields from the contact list — including custom fields from CSV import — can be used in both subject line AND email body.**

**Available Merge Tags:**

| Category | Tags |
|----------|------|
| **Contact Info** | `{{Title}}`, `{{FirstName}}`, `{{LastName}}`, `{{FullName}}`, `{{Email}}`, `{{Company}}`, `{{Position}}`, `{{Phone}}` |
| **Custom Fields** | `{{Custom1}}` ... `{{Custom10}}` |
| **Sender Info** | `{{SenderName}}`, `{{SenderEmail}}`, `{{SenderCompany}}` |
| **Campaign Info** | `{{CampaignRef}}`, `{{UnsubscribeText}}` |

**Example — Subject Line with Custom Field:**

```
CSV columns: FirstName, LastName, Email, Company, Industry, Pain_Point
                                                    ↓           ↓
                                              mapped to    mapped to
                                               Custom1      Custom2
```

Subject template:
```
{{FirstName}}, a solution for {{Custom1}} companies facing {{Custom2}}
```

Result for contact "John Doe, Acme Corp, Manufacturing, supply chain delays":
```
John, a solution for Manufacturing companies facing supply chain delays
```

**Example — Email Body:**

```
Hello {{Title}} {{LastName}},

I noticed that {{Company}} operates in the {{Custom1}} sector. 
Many of our clients in this industry have faced {{Custom2}}.

We helped them reduce costs by 30%...

Best regards,
{{SenderName}}
```

**Fallback Values:**

If a merge field is empty for a contact, the system can:

| Option | Behavior | Example |
|--------|----------|---------|
| **Leave blank** | Field replaced with empty string | "Hello , how are you?" |
| **Use fallback** | Field replaced with default value | "Hello there, how are you?" |
| **Skip contact** | Contact not sent this email | Contact stays in queue |

Configuration per template:
```
┌─────────────────────────────────────────────────────────────────┐
│  Fallback Settings                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ {{FirstName}}  →  Fallback: [there         ]  or ○ Skip   │ │
│  │ {{Custom1}}    →  Fallback: [your industry ]  or ○ Skip   │ │
│  │ {{Custom2}}    →  Fallback: [               ]  or ● Skip  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 Template Editor

**Email Template Editor with Merge Tag Insertion:**

```
┌─────────────────────────────────────────────────────────────────┐
│              EMAIL TEMPLATE EDITOR                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Subject Line:                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ {{FirstName}}, a solution for {{Custom1}} companies        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  [+ Insert Field ▼]  Available: FirstName, LastName, Company... │
│                                                                 │
│  Email Body:                                          [B][I][U] │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Hello {{Title}} {{LastName}},                              │ │
│  │                                                            │ │
│  │ I noticed that {{Company}} operates in the {{Custom1}}     │ │
│  │ sector. Many of our clients have faced {{Custom2}}.        │ │
│  │                                                            │ │
│  │ Would you be available for a quick call next week?         │ │
│  │                                                            │ │
│  │ Best regards,                                              │ │
│  │ {{SenderName}}                                             │ │
│  │                                                            │ │
│  │ ---                                                        │ │
│  │ {{UnsubscribeText}}                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  [+ Insert Field ▼]                                             │
│  ┌────────────────────┐                                         │
│  │ ▸ Contact Fields   │                                         │
│  │   {{FirstName}}    │                                         │
│  │   {{LastName}}     │                                         │
│  │   {{Company}}      │                                         │
│  │   {{Position}}     │                                         │
│  │ ▸ Custom Fields    │                                         │
│  │   {{Custom1}} [Industry]                                     │
│  │   {{Custom2}} [Pain Point]                                   │
│  │   {{Custom3}} [Budget]                                       │
│  │   ... up to Custom10                                         │
│  │ ▸ Sender Info      │                                         │
│  │   {{SenderName}}   │                                         │
│  └────────────────────┘                                         │
│                                                                 │
│                    [Preview with Sample Contact]   [Save]       │
└─────────────────────────────────────────────────────────────────┘
```

**Preview Mode:**

```
┌─────────────────────────────────────────────────────────────────┐
│              TEMPLATE PREVIEW                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Preview with contact: [Jean Dupont - Acme Corp        ▼]       │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ From: Pierre Martin <pierre@company.com>                   │ │
│  │ To: Jean Dupont <jd@acme.fr>                               │ │
│  │ Subject: Jean, a solution for Manufacturing companies      │ │
│  │ ──────────────────────────────────────────────────────     │ │
│  │                                                            │ │
│  │ Hello Mr Dupont,                                           │ │
│  │                                                            │ │
│  │ I noticed that Acme Corp operates in the Manufacturing     │ │
│  │ sector. Many of our clients have faced supply chain delays.│ │
│  │                                                            │ │
│  │ Would you be available for a quick call next week?         │ │
│  │                                                            │ │
│  │ Best regards,                                              │ │
│  │ Pierre Martin                                              │ │
│  │                                                            │ │
│  │ ---                                                        │ │
│  │ To unsubscribe, reply with UNSUBSCRIBE. Ref: ISIT-250142   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ⚠️ 3 contacts have empty {{Custom2}} field (will use fallback) │
│                                                                 │
│                              [← Edit]   [Looks Good ✓]          │
└─────────────────────────────────────────────────────────────────┘
```

### 8.4 Template Management

- Global template library (reusable across campaigns)
- Campaign-specific templates
- Version history
- Preview with sample contact data

### 8.5 Attachments — Hybrid Mode

> **User Choice:** For each attached file, the user selects the delivery method — direct attachment (no tracking) or download link (click tracking).

**Delivery Modes:**

| Mode | Description | Tracking | Recipient Access |
|------|-------------|----------|------------------|
| **Attachment** | File embedded in email | ❌ None | Anyone (recommended for external prospects) |
| **Link** | File hosted internally, link in email | ✅ Click tracked | Internal network / VPN only |

> ⚠️ **Limitation:** Link mode requires the recipient to access your internal network. For external prospects without VPN access, use Attachment mode.

**User Interface:**

```
┌─────────────────────────────────────────────────────────────────┐
│              EMAIL STEP 2 - ATTACHMENTS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Attached Files:                                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 📎 Proposal_{{Company}}.pdf                     [🗑 Remove] │ │
│  │    Delivery: ○ Attachment (no tracking)                    │ │
│  │              ● Link (click tracking) ✅                    │ │
│  │    ⚠️ Link only accessible on internal network / VPN       │ │
│  │    Link text: [Download our proposal]                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 📎 Brochure_2025.pdf                            [🗑 Remove] │ │
│  │    Delivery: ● Attachment (no tracking)                    │ │
│  │              ○ Link (click tracking)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [+ Add File]                       Max file size: 10 MB        │
│                                                                 │
│  💡 Use "Link" for internal/VPN contacts to track downloads     │
│  💡 Use "Attachment" for external prospects (no tracking)       │
└─────────────────────────────────────────────────────────────────┘
```

**Link Mode — How It Works:**

```
┌─────────────────────────────────────────────────────────────────┐
│   EMAIL SENT                                                    │
│   "Please find our proposal: [Download Proposal]"               │
│                    │                                            │
│                    │ Link: https://internal-server/dl/{token}   │
│                    ▼                                            │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │   LEAD GENERATOR API (Internal Network)                 │   │
│   │   GET /dl/{token}                                       │   │
│   │                                                         │   │
│   │   1. Decode token → ContactID, CampaignID, FileID       │   │
│   │   2. Log click event (timestamp, IP, user agent)        │   │
│   │   3. Return file for download                           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                    │                                            │
│                    ▼                                            │
│   CONTACT DOWNLOADS FILE (must be on internal network/VPN)      │
│   ✅ Click tracked in database                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Link Mode — Access Requirement:**

| Recipient Type | Can Access Link? | Recommendation |
|----------------|------------------|----------------|
| Internal employees | ✅ Yes | Use Link mode |
| Partners with VPN | ✅ Yes | Use Link mode |
| External prospects | ❌ No | Use Attachment mode |

**Configuration (per campaign):**

| Setting | Default | Description |
|---------|---------|-------------|
| Default delivery mode | Attachment | Pre-selected mode for new files |
| Link expiration | 30 days | How long download links remain valid |
| Track downloads | Enabled | Log all download events |
| Custom link text | "Download {filename}" | Text shown in email |
| Warning for external | Enabled | Show warning when using Link mode |

**Attachment Data Model:**

| Field | Type | Description |
|-------|------|-------------|
| AttachmentID | GUID | Primary key |
| SequenceStepID | GUID | Parent email step |
| FileName | String | Original file name |
| FileSize | Int | Size in bytes |
| FilePath | String | Storage location |
| DeliveryMode | Enum | Attachment / Link |
| LinkText | String | Display text for link mode |
| ExpirationDays | Int | Link validity (null = no expiration) |
| IsPublic | Boolean | Accessible from internet |
| CreatedDate | DateTime | Upload timestamp |

**Download Tracking Data Model:**

| Field | Type | Description |
|-------|------|-------------|
| DownloadID | GUID | Primary key |
| AttachmentID | GUID | Which file |
| ContactID | GUID | Who clicked |
| CampaignID | GUID | Which campaign |
| DownloadedAt | DateTime | Click timestamp |
| IPAddress | String | Client IP |
| UserAgent | String | Browser/client info |
| Referrer | String | Email client if available |

---

## 9. Contact Status & Workflow

### 9.1 Contact Status per Campaign

```
┌─────────┐    Email Sent    ┌───────────┐    Reply Detected    ┌───────────┐
│ PENDING │ ───────────────► │ IN_PROGRESS│ ───────────────────► │ RESPONDED │
└─────────┘                  └───────────┘                       └───────────┘
                                   │                                   
                                   │ Sequence Complete                 
                                   ▼                                   
                             ┌───────────┐                             
                             │ COMPLETED │                             
                             └───────────┘                             
                                   
     Other statuses: BOUNCED, UNSUBSCRIBED, OPTED_OUT, PAUSED
```

### 9.2 Status Definitions

| Status | Description |
|--------|-------------|
| PENDING | Contact added, no emails sent yet |
| IN_PROGRESS | At least one email sent, sequence ongoing |
| RESPONDED | Reply detected, sequence stopped |
| COMPLETED | All sequence emails sent, no reply |
| BOUNCED | Email delivery failed |
| UNSUBSCRIBED | Contact clicked unsubscribe link |
| OPTED_OUT | Manually marked as do-not-contact |
| PAUSED | Temporarily halted by user |

### 9.3 Reply Detection

- Application periodically scans Outlook Inbox/folders for replies
- Matching based on: sender email + campaign identifier or thread reference
- Upon reply detection: sequence stops, status changes to RESPONDED
- Manual confirmation option for ambiguous matches
- CRM notified of status change

---

## 10. Sending Engine

### 10.1 Integration with Local Mailer

- Uses Outlook COM Automation (or MAPI fallback)
- Emails placed in Outbox with deferred send time
- Respects user's Outlook signature settings (configurable)
- Windows Service handles background scheduling

### 10.2 Anti-Spam Measures

| Measure | Implementation |
|---------|----------------|
| Volume throttling | Max emails/hour and /day per account |
| Time randomization | ±10–20 min variance on scheduled times |
| Business hours | Restrict sending to working hours |
| Warmup mode | Gradually increase volume for new accounts |
| Bounce monitoring | Pause campaign if bounce rate > 10% |
| Domain rotation | Distribute across multiple sender domains |

### 10.3 Sending Queue

- Centralized queue managed by API server
- Each workstation's mail service pulls tasks for its assigned accounts
- Retry logic for temporary failures (max 3 attempts)
- Dead-letter queue for permanent failures

---

## 11. Unsubscribe Management

### 11.1 Unsubscribe Mechanism

> **Note:** Internal servers are not accessible from the internet. The unsubscribe landing page must be hosted on a **public cloud service**.

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│   CONTACT receives email with:                                          │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  1. List-Unsubscribe Header (RFC 8058) → One-click in Gmail   │    │
│   │  2. Footer Link → https://unsubscribe.yourcompany.com/{token} │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │       CLOUD MICRO-SERVICE (Public Internet)                   │    │
│   │       Azure Static Web App / Cloudflare Pages / Vercel        │    │
│   │       Cost: Free tier or ~€5-10/month                         │    │
│   │                                                               │    │
│   │   • Validates signed token                                    │    │
│   │   • Displays confirmation page                                │    │
│   │   • Calls internal API via secure callback                    │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              │ Secure callback (API Key + HTTPS)        │
│                              ▼                                          │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │       INTERNAL LEAD GENERATOR API                             │    │
│   │       POST /api/internal/unsubscribe                          │    │
│   └───────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Cloud Hosting Options:**

| Provider | Service | Cost | Notes |
|----------|---------|------|-------|
| Azure | Static Web Apps + Function | Free tier | Easy if using Azure |
| Cloudflare | Pages + Workers | Free tier | Very fast, simple |
| Vercel | Serverless Functions | Free tier | Easiest setup |
| AWS | S3 + Lambda | ~€5/mo | More complex |

**Link Generation:**
- Each email includes a unique unsubscribe link in the footer
- Format: `https://unsubscribe.yourcompany.com/{signed-token}`
- Token is HMAC-signed and contains: ContactID + CampaignID + Expiration
- Token validated by cloud service before processing

**Landing Page Options:**
- Unsubscribe from this campaign only
- Unsubscribe from all communications (global opt-out)
- Optional: feedback form (why unsubscribing)

**Security:**
- Tokens signed with HMAC-SHA256 (secret shared between cloud and internal API)
- Tokens expire after 30 days
- Internal API protected by API key + IP whitelist
- Rate limiting on cloud service to prevent abuse

### 11.2 Global Suppression List

| Field | Type | Description |
|-------|------|-------------|
| Email | String | Primary key |
| UnsubscribeDate | DateTime | When opted out |
| UnsubscribeSource | Enum | Link / Manual / Bounce / Complaint |
| Scope | Enum | Global / CampaignSpecific |
| CampaignID | GUID | If campaign-specific |
| Reason | String | Optional feedback |

### 11.3 Enforcement Rules

```
BEFORE any email is sent:
  ├── Check Global Suppression List
  │     └── If FOUND (Global) → BLOCK, log "Suppressed: Global Opt-out"
  │
  ├── Check Campaign Suppression
  │     └── If FOUND (This Campaign) → BLOCK, log "Suppressed: Campaign Opt-out"
  │
  └── Proceed with sending
```

### 11.4 Compliance Features

| Feature | Description |
|---------|-------------|
| Auto-footer injection | Unsubscribe instructions automatically added if missing |
| List-Unsubscribe header | RFC 2369 mailto header for email clients |
| Multi-language support | Keywords in multiple languages (configurable) |
| Audit trail | All unsubscribe events logged immutably |
| Re-subscribe protection | Manual admin action required to remove from suppression |
| Outlook rule suggestion | Tool can create Outlook rule to route unsubscribe emails |

---

## 12. A/B Testing Framework

### 12.1 Test Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│           A/B TEST: Email Step 1 - Subject Line Test            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Test Element:   ● Subject Line   ○ Body Content   ○ Send Time  │
│                                                                 │
│  VARIANT A (Control) - 50%                                      │
│  Subject: "Quick question about {{Company}}"                    │
│                                                                 │
│  VARIANT B - 50%                                                │
│  Subject: "{{FirstName}}, partnership opportunity"              │
│                                                                 │
│  Split:  50/50     Sample Size: 200 contacts                    │
│                                                                 │
│  Success Metric: ● Response Rate  ○ Click Rate  ○ Open Rate     │
│                                                                 │
│  Auto-select winner after: 100 responses or 14 days             │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 A/B Test Data Model

| Field | Type | Description |
|-------|------|-------------|
| TestID | GUID | Primary key |
| CampaignID | GUID | Parent campaign |
| SequenceStep | Int | Which email in sequence |
| TestElement | Enum | Subject / Body / SendTime |
| VariantA_Content | String | Control version |
| VariantB_Content | String | Test version |
| SplitRatio | Decimal | e.g., 0.5 for 50/50 |
| SuccessMetric | Enum | ResponseRate / ClickRate |
| MinSampleSize | Int | Minimum before declaring winner |
| MaxDuration | Int | Days before auto-selection |
| WinnerVariant | Enum | A / B / None / Inconclusive |
| Status | Enum | Running / Completed / Cancelled |

### 12.3 Statistical Significance

- System calculates confidence level using chi-square test
- Winner declared only when confidence ≥ 95%
- If inconclusive after max duration, user notified to choose

### 12.4 Testable Elements

| Element | Variants | Notes |
|---------|----------|-------|
| Subject line | 2–4 versions | Most common test |
| Email body | 2 versions | Different messaging/tone |
| CTA text | 2–4 versions | Button/link text |
| Send time | 2–3 time slots | Morning vs. afternoon |
| Send day | 2–3 days | Tuesday vs. Thursday |
| Sender name | 2 versions | "John Smith" vs. "John from Company" |

---

## 13. CRM Integration

### 13.1 Integration Architecture

> **Note:** The CRM is a desktop client application, not a server. It cannot expose APIs. Therefore, the Lead Generator exposes sync endpoints that the CRM consumes.

> **Network Requirement:** The Lead Generator API is only accessible on the internal network. CRM must be on-site or connected via VPN to sync.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNAL NETWORK / VPN                       │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   PostgreSQL    │◄──►│   API Server (.NET 8)               │ │
│  │   Database      │    │                                     │ │
│  └─────────────────┘    │   Endpoints exposed for CRM:        │ │
│                         │   • GET  /api/sync/contacts         │ │
│                         │   • GET  /api/sync/campaigns        │ │
│                         │   • GET  /api/sync/activities       │ │
│                         │   • GET  /api/sync/status-changes   │ │
│                         │   • POST /api/sync/crm-updates      │ │
│                         │   • POST /api/sync/acknowledge      │ │
│                         └──────────────┬──────────────────────┘ │
│                                        │                        │
│                                        │ HTTPS (internal only)  │
│                                        ▼                        │
│                    ┌─────────────────────────────────────────┐  │
│                    │         HOME-MADE CRM (Client)          │  │
│                    │                                         │  │
│                    │   • Polls Lead Generator API            │  │
│                    │   • Imports new/updated contacts        │  │
│                    │   • Retrieves campaign status changes   │  │
│                    │   • Pushes CRM updates (conversions)    │  │
│                    │                                         │  │
│                    │   ⚠️ Must be on internal network or VPN  │  │
│                    └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2 Sync API Endpoints (exposed by Lead Generator)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sync/contacts` | GET | Get new/modified contacts since last sync |
| `/api/sync/contacts/{id}` | GET | Get single contact with full details |
| `/api/sync/campaigns` | GET | List campaigns (active, completed) |
| `/api/sync/activities` | GET | Get email activities (sent, opened, bounced) |
| `/api/sync/status-changes` | GET | Get contacts whose status changed since timestamp |
| `/api/sync/crm-updates` | POST | CRM sends updates (lead converted, notes, etc.) |
| `/api/sync/acknowledge` | POST | CRM confirms sync completed (for delta tracking) |

### 13.3 Sync Configuration

| Setting | Options | Description |
|---------|---------|-------------|
| Sync Frequency | On-demand / Scheduled (hourly/daily) | When CRM polls |
| Delta Sync | Enabled / Disabled | Only fetch changes since last sync |
| Conflict Resolution | CRM wins / Lead Generator wins / Newest wins | On data conflict |
| Field Mapping | Configurable | Map Lead Generator fields to CRM fields |
| Authentication | API Key / OAuth2 | Secure CRM access to API |

### 13.4 Sync Flow Sequence

```
CRM Application                          Lead Generator API
      │                                         │
      │  1. GET /sync/status-changes?since=...  │
      │────────────────────────────────────────►│
      │                                         │
      │  2. Returns: [{contactId, newStatus,    │
      │               campaignId, timestamp}]   │
      │◄────────────────────────────────────────│
      │                                         │
      │  3. CRM updates its local database      │
      │                                         │
      │  4. POST /sync/acknowledge              │
      │     {lastSyncTimestamp: "..."}          │
      │────────────────────────────────────────►│
      │                                         │
      │  5. POST /sync/crm-updates              │
      │     {contactId, crmStatus: "Converted"} │
      │────────────────────────────────────────►│
      │                                         │
```

### 13.5 Field Mapping Configuration

| Campaign Tool Field | CRM Field |
|---------------------|-----------|
| FirstName | first_name |
| LastName | last_name |
| Email | email_primary |
| Company | company_name |
| Position | job_title |
| Phone | phone_business |
| Campaign Status | lead_status |
| Last Contact Date | last_activity |
| Response Date | converted_date |

### 13.4 Status Mapping

| Campaign Status | CRM Status |
|-----------------|------------|
| PENDING | New Lead |
| IN_PROGRESS | Contacted |
| RESPONDED | Qualified |
| COMPLETED | Nurturing |
| BOUNCED | Invalid |
| UNSUBSCRIBED | Opted Out |

### 13.6 CRM Implementation Requirements

For the CRM to integrate with the Lead Generator, the CRM must implement:

| Component | Description |
|-----------|-------------|
| HTTP Client | Ability to make REST API calls (GET/POST) |
| Scheduler | Background task to poll API periodically |
| Sync State | Store last sync timestamp for delta queries |
| Field Mapper | Map Lead Generator fields to CRM data model |
| Conflict Handler | Logic to resolve data conflicts |
| Error Handler | Retry logic for failed syncs |

### 13.7 Sync Events

| Campaign Event | CRM Action |
|----------------|------------|
| Contact added to campaign | Create/update lead with source = "Campaign: X" |
| First email sent | Update lead status, set "First Contact Date" |
| Contact responded | Update status to "Responded/Qualified" |
| Contact unsubscribed | Update status, add to "Do Not Contact" |
| Email bounced | Flag lead as "Invalid Email" |
| Campaign completed | Update lead status, add completion note |

---

## 14. Reporting & KPIs

### 14.1 Campaign Dashboard KPIs

| KPI | Description |
|-----|-------------|
| Total contacts | Count in campaign |
| Emails sent | Total across all steps |
| Sequence completion rate | % contacts who received all emails |
| Response rate | % contacts who replied |
| Bounce rate | % emails bounced |
| Unsubscribe rate | % contacts who opted out |
| Contacts per status | Breakdown by status |
| **Download rate** | % contacts who clicked download links |
| **Downloads per file** | Click count per attachment |

### 14.2 Reports

| Report | Description |
|--------|-------------|
| Campaign summary | Overview with all KPIs (PDF/CSV export) |
| Contact activity timeline | Per-contact email history |
| Cross-campaign overlap | Contacts in multiple campaigns |
| A/B test results | Variant performance comparison |
| Mail account utilization | Volume per account over time |
| Email delivery log | Timestamps and status per email |
| **Attachment downloads** | Which contacts downloaded which files, when |

### 14.3 Logging

- All sent emails logged with: timestamp, recipient, subject, campaign, sequence step, mail account
- **All file downloads logged with: timestamp, contact, file, IP address**
- Log retention configurable (default: 2 years)
- Immutable audit trail for compliance

### 14.4 File Storage

**Storage Location:**
- Attachments stored on configurable path (local or network drive)
- Structure: `{StorageRoot}/campaigns/{CampaignID}/attachments/{AttachmentID}/{filename}`
- Automatic cleanup of orphaned files (deleted campaigns)

**Storage Configuration:**

| Setting | Default | Description |
|---------|---------|-------------|
| Storage root | `C:\LeadGenerator\Files` | Base path for all files |
| Max file size | 10 MB | Per attachment limit |
| Allowed extensions | pdf, docx, xlsx, pptx, png, jpg | Whitelist |
| Retention period | 1 year after campaign end | Auto-cleanup |

---

## 15. Data Model

### 15.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│    USER     │       │  CAMPAIGN   │       │  CONTACT_LIST   │
├─────────────┤       ├─────────────┤       ├─────────────────┤
│ UserID (PK) │──┐    │CampaignID(PK)│◄─────│ ListID (PK)     │
│ Username    │  │    │ Name        │       │ Name            │
│ Role        │  │    │ OwnerUserID │───────│ OwnerUserID     │
└─────────────┘  │    │ ContactListID│      │ IsShared        │
                 │    │ Status      │       └────────┬────────┘
                 │    └──────┬──────┘                │
                 │           │                       │
                 │           │                       ▼
                 │           │              ┌─────────────────┐
                 │           │              │    CONTACT      │
                 │           │              ├─────────────────┤
                 │           │              │ ContactID (PK)  │
                 │           │              │ ListID (FK)     │
                 │           │              │ Email           │
                 │           │              │ FirstName       │
                 │           │              │ CRM_LeadID      │──► CRM
                 │           │              └────────┬────────┘
                 │           │                       │
                 │           ▼                       │
                 │    ┌─────────────────┐           │
                 │    │ EMAIL_SEQUENCE  │           │
                 │    ├─────────────────┤           │
                 │    │ SequenceID (PK) │           │
                 │    │ CampaignID (FK) │           │
                 │    │ StepNumber      │           │
                 │    │ SubjectTemplate │           │
                 │    │ BodyTemplate    │           │
                 │    └───────┬─────────┘           │
                 │            │                     │
                 │      ┌─────┴─────┐               │
                 │      │           │               │
                 │      ▼           ▼               │
                 │ ┌──────────┐ ┌──────────────┐    │
                 │ │ AB_TEST  │ │ ATTACHMENT   │    │
                 │ ├──────────┤ ├──────────────┤    │
                 │ │TestID(PK)│ │AttachID (PK) │    │
                 │ │SequenceID│ │SequenceID(FK)│    │
                 │ │VariantA/B│ │ FileName     │    │
                 │ └──────────┘ │ DeliveryMode │    │
                 │              │ FilePath     │    │
                 │              └──────┬───────┘    │
                 │                     │            │
                 │    ┌─────────────────┐          │
                 │    │CAMPAIGN_CONTACT │◄─────────┘
                 │    ├─────────────────┤
                 │    │ CampaignID (FK) │
                 │    │ ContactID (FK)  │
                 │    │ Status          │
                 │    │ AssignedVariant │
                 │    │ MailAccountID   │
                 │    └────────┬────────┘
                 │             │
                 │      ┌──────┴──────┐
                 │      ▼             ▼
                 │ ┌───────────┐ ┌───────────────┐
                 │ │ EMAIL_LOG │ │ DOWNLOAD_LOG  │
                 │ ├───────────┤ ├───────────────┤
                 └►│LogID (PK) │ │DownloadID(PK)│
                   │CampaignID │ │AttachmentID  │
                   │ContactID  │ │ContactID     │
                   │MailAcctID │ │DownloadedAt  │
                   │SentAt     │ │IPAddress     │
                   │Status     │ │UserAgent     │
                   └───────────┘ └───────────────┘
                      
┌─────────────────┐     ┌─────────────────┐
│SUPPRESSION_LIST │     │  MAIL_ACCOUNT   │
├─────────────────┤     ├─────────────────┤
│ Email (PK)      │     │ AccountID (PK)  │
│ Scope           │     │ EmailAddress    │
│ Source          │     │ DailyLimit      │
│ UnsubscribeDate │     │ WorkstationID   │
└─────────────────┘     └─────────────────┘
```

---

## 16. User Interface

### 16.1 Main Application Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  File   Campaigns   Contacts   Templates   Reports   CRM   Settings   Help  │
│                                                          [User: JSmith ▼]   │
├─────────────┬───────────────────────────────────────────────────────────────┤
│             │  CAMPAIGN: Q1 2025 Tech Outreach                    [⚙][▶][⏸] │
│  CAMPAIGNS  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  ─────────  │                                                               │
│             │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐    │
│  📁 Active  │  │ Overview │ Sequence │ Contacts │ A/B Tests│ Reports  │    │
│   ├─ Q1 Tech│  └──────────┴──────────┴──────────┴──────────┴──────────┘    │
│   └─ Partner│                                                               │
│  📁 Draft   │  Status: ACTIVE              Owner: J. Smith                  │
│   └─ Event  │  Mail Accounts: sales1@, sales2@ (2)                          │
│  📁 Archive │  CRM Sync: ✓ Enabled         Last Sync: 2 min ago            │
│             │                                                               │
│             │  ┌─────────────────────────────────────────────────────────┐  │
│  ─────────  │  │  PROGRESS                                              │  │
│  QUICK STATS│  │  ████████████████████░░░░░░░░░░  68% Complete          │  │
│  ─────────  │  │                                                        │  │
│  Pending:123│  │  Pending    In Progress   Responded   Completed        │  │
│  Sent: 2,341│  │    123         234           45          98            │  │
│  Responded:45│  │                                                        │  │
│  Bounced: 12│  │  ┌──────────────────────────────────────────────────┐  │  │
│             │  │  │ A/B TEST RUNNING: Subject Line Test              │  │  │
│             │  │  │ Variant A: 12% response   Variant B: 18% response│  │  │
│             │  │  │ Confidence: 87% (need 95% to declare winner)     │  │  │
│             │  │  └──────────────────────────────────────────────────┘  │  │
│  [+ New]    │  └─────────────────────────────────────────────────────────┘  │
└─────────────┴───────────────────────────────────────────────────────────────┘
```

### 16.2 Key Screens

| Screen | Purpose |
|--------|---------|
| **Login** | Standalone authentication |
| Dashboard | Overview of all campaigns, recent activity |
| Campaign Detail | Full campaign management with tabs |
| Contact List Manager | Import, edit, search contacts |
| Template Editor | Create/edit email templates with preview |
| **Attachment Manager** | Add files, choose delivery mode (attach/link) |
| A/B Test Setup | Configure and monitor tests |
| Reports | View and export campaign analytics |
| **Download Report** | View who downloaded which files, when |
| CRM Settings | Configure integration and field mapping |
| User Management | Admin: create/edit users, reset passwords |
| Mail Account Setup | Configure sending accounts |
| Suppression List | View and manage opt-outs |

---

## 17. Implementation Phases

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Core Infrastructure** | 8 weeks | Database schema, API server, authentication, basic UI shell |
| **Phase 2: Campaign Management** | 6 weeks | Campaign CRUD, contact lists, email sequences, CSV import/export |
| **Phase 3: Sending Engine** | 4 weeks | Outlook integration, scheduling, queue management |
| **Phase 4: Multi-user** | 4 weeks | Role-based access, concurrency handling, user management |
| **Phase 5: Multi-account** | 3 weeks | Multiple mail accounts, distribution strategies, warmup mode |
| **Phase 6: Compliance** | 3 weeks | Unsubscribe management, suppression list, audit logging |
| **Phase 7: A/B Testing** | 3 weeks | Test framework, statistical analysis, auto-winner selection |
| **Phase 8: CRM Integration** | 4 weeks | API integration, field mapping, sync engine, webhooks |
| **Phase 9: Reporting** | 3 weeks | Dashboards, KPIs, export capabilities |
| **Phase 10: Polish & Testing** | 4 weeks | UI refinement, QA testing, documentation, deployment |

**Total estimated duration: 42 weeks (~10 months)**

---

## 18. Open Questions

### Resolved Questions ✓

| # | Question | Resolution |
|---|----------|------------|
| ✓ | CRM API availability | CRM is a client, not a server. Lead Generator exposes API for CRM to consume. |
| ✓ | Unsubscribe hosting | Email-based unsubscribe. Tool monitors Outlook inbox/folder for unsubscribe requests. No external hosting needed. |
| ✓ | Attachment tracking | Hybrid mode: user chooses per file — Attachment (no tracking) or Link (click tracking). |
| ✓ | Download links accessibility | Internal network only. Link mode for internal/VPN contacts; Attachment mode for external prospects. |
| ✓ | Custom fields in templates | Yes. Any CSV column can be mapped to Custom1–10 fields and used as merge tags in subject and body. |
| ✓ | Unsubscribe keywords | English + French keywords supported for detection. |
| ✓ | Unsubscribe email address | Same as sending account. No dedicated address needed. |
| ✓ | Authentication method | Standalone accounts (own user database). No AD/LDAP dependency. |
| ✓ | API network access | Internal network / VPN only. CRM must be on-site or connected via VPN to sync. |

### All Questions Resolved ✓

The functional specification is complete and ready for implementation.

### Feature Questions

5. **Open rate tracking:** Do you want email open tracking (requires tracking pixel, has privacy implications)?
6. **Click tracking:** Do you want link click tracking (requires redirect URLs)?
7. **Attachment support:** Should campaigns support file attachments?
8. **Multi-language:** Do you need support for multiple languages/locales?

### Business Questions

9. **Compliance requirements:** Any specific regulations to comply with (GDPR, CAN-SPAM, etc.)?
10. **Number of users:** Expected concurrent users for capacity planning?
11. **Email volume:** Expected monthly email volume?

---

## Appendix A: Original Specification Challenges

| Spec # | Original | Challenge / Recommendation |
|--------|----------|---------------------------|
| #05 | Minimal contact fields | Added: Position, Phone, LinkedIn, 10 Custom fields from CSV |
| #09 | Fixed 4–6 emails | Made configurable: 1–10 emails |
| #10 | Template with basic fields | Extended: any CSV field usable via Custom1–5 merge tags |
| #12 | Fixed 30 min delay | Added: randomization, daily caps, business hours |
| #15 | Auto reply detection | Added: manual confirmation for ambiguous matches |
| #20 | ID in subject + body | Moved to footer only + hidden header |
| — | Not specified | Added: warmup mode for new accounts |
| — | Not specified | Added: bounce rate circuit breaker |
| — | Not specified | Added: multi-user support |
| — | Not specified | Added: A/B testing framework |
| — | Not specified | Added: unsubscribe management (email-based) |
| — | Not specified | Added: attachment tracking (hybrid mode with user choice) |
| — | Not specified | CRM integration reversed (CRM pulls from Lead Generator) |
| — | Not specified | Added: CSV import wizard with field mapping |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Campaign** | A complete marketing initiative with contacts, email sequence, and configuration |
| **Sequence** | Ordered set of emails sent to contacts over time |
| **Suppression List** | Global list of emails that should never receive communications |
| **Warmup** | Gradual increase in sending volume for new mail accounts |
| **A/B Test** | Experiment comparing two variants to determine better performance |
| **Bounce** | Failed email delivery (hard bounce = permanent, soft bounce = temporary) |
| **Attachment Mode** | Direct file attachment to email — no tracking, works for all recipients |
| **Link Mode** | File hosted internally, download link in email — click tracking enabled, internal/VPN recipients only |
| **Download Token** | Unique identifier in download URL to track who clicked |
| **Merge Tag** | Placeholder in templates (e.g., `{{FirstName}}`) replaced with contact data when sending |
| **Custom Field** | User-defined contact field mapped from CSV column (Custom1–10) |
| **Field Mapping** | Process of associating CSV columns with contact database fields during import |
| **Fallback Value** | Default text used when a merge tag field is empty for a contact |

---

**Document prepared for internal review.**  
**Next step:** Address open questions, then proceed to detailed technical design.
