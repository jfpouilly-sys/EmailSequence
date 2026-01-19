# Email Sequence Manager - Configuration Manual

Complete guide to configuring the Email Sequence Manager application.

## Table of Contents

1. [Configuration Files Overview](#configuration-files-overview)
2. [Core Configuration (config.yaml)](#core-configuration-configyaml)
3. [GUI Configuration (gui_config.yaml)](#gui-configuration-gui_configyaml)
4. [Contact File Format](#contact-file-format)
5. [Email Templates](#email-templates)
6. [Advanced Settings](#advanced-settings)
7. [Best Practices](#best-practices)

---

## Configuration Files Overview

The Email Sequence Manager uses multiple configuration files:

| File | Purpose | Required |
|------|---------|----------|
| `config.yaml` | Core application settings, email configuration | Yes |
| `gui_config.yaml` | GUI appearance and behavior settings | Yes (for GUI) |
| `contacts.xlsx` | Contact database | Yes |
| `templates/*.html` | Email templates | Yes |

### File Locations

Default locations (relative to project folder):

```
EmailSequence/
├── config.yaml              # Core configuration
├── gui_config.yaml          # GUI configuration
├── contacts.xlsx            # Contact database
├── templates/               # Email templates folder
│   ├── initial.html
│   ├── followup_1.html
│   ├── followup_2.html
│   └── followup_3.html
└── logs/                    # Log files
    └── sequence.log
```

---

## Core Configuration (config.yaml)

### Complete Example

```yaml
# Core Email Sequence Configuration

email:
  sender_name: "Jean-François Pouilly"
  subject_template: "Partnership Opportunity - ISIT"
  delay_between_sends: 5  # Seconds between emails
  signature: |
    Best regards,
    Jean-François Pouilly
    ISIT Director

sequence:
  followup_delays:
    followup_1: 3   # Days after initial email
    followup_2: 7   # Days after initial email
    followup_3: 14  # Days after initial email
  max_followups: 3
  stop_on_reply: true
  stop_on_bounce: true
  stop_on_optout: true

outlook:
  inbox_scan_days: 30
  folder_name: "Inbox"
  sent_folder: "Sent Items"
  mark_as_read: false
  use_default_account: true

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/sequence.log"
  max_size_mb: 10
  backup_count: 5
  format: "%(asctime)s | %(levelname)s | %(message)s"

safety:
  max_emails_per_run: 100
  require_confirmation: false  # CLI only
  test_mode: false  # Don't actually send emails
```

### Email Settings

#### sender_name
**Type:** String
**Required:** Yes
**Description:** Your name as it appears in email signatures and placeholders.

```yaml
sender_name: "Dr. Sarah Johnson"
```

#### subject_template
**Type:** String
**Required:** No (can be set in templates)
**Description:** Default subject line template.

```yaml
subject_template: "RE: {topic} - Follow-up"
```

#### delay_between_sends
**Type:** Integer (seconds)
**Default:** 5
**Description:** Delay between sending emails to avoid rate limiting.

```yaml
delay_between_sends: 10  # Wait 10 seconds between emails
```

**Recommendations:**
- Standard: 5-10 seconds
- Conservative: 15-30 seconds
- Bulk sending: 3-5 seconds (monitor for issues)

---

### Sequence Settings

#### followup_delays
**Type:** Dictionary
**Required:** Yes
**Description:** Days to wait before sending each follow-up.

```yaml
followup_delays:
  followup_1: 3   # First follow-up after 3 days
  followup_2: 7   # Second follow-up after 7 days (from initial)
  followup_3: 14  # Third follow-up after 14 days (from initial)
```

**Important Notes:**
- Delays are cumulative from the initial email, not from previous follow-ups
- Contact must have status "sent" or "followup_X" to receive next follow-up
- Contacts who reply are automatically marked "replied" and stop receiving follow-ups

#### max_followups
**Type:** Integer
**Default:** 3
**Range:** 0-10
**Description:** Maximum number of follow-up emails to send.

```yaml
max_followups: 2  # Only send initial + 2 follow-ups
```

#### stop_on_reply
**Type:** Boolean
**Default:** true
**Description:** Stop sending follow-ups when contact replies.

```yaml
stop_on_reply: true  # Recommended
```

#### stop_on_bounce
**Type:** Boolean
**Default:** true
**Description:** Stop sending to contacts whose emails bounce.

```yaml
stop_on_bounce: true  # Recommended
```

---

### Outlook Settings

#### inbox_scan_days
**Type:** Integer
**Default:** 30
**Description:** How many days back to scan inbox for replies.

```yaml
inbox_scan_days: 60  # Scan last 60 days
```

**Performance Note:** Larger values take longer to scan.

#### folder_name
**Type:** String
**Default:** "Inbox"
**Description:** Outlook folder to scan for replies.

```yaml
folder_name: "Inbox"  # Or "All Mail", "Archive", etc.
```

#### use_default_account
**Type:** Boolean
**Default:** true
**Description:** Use Outlook's default email account.

```yaml
use_default_account: true
```

---

### Logging Settings

#### level
**Type:** String
**Options:** DEBUG, INFO, WARNING, ERROR
**Default:** INFO
**Description:** Logging verbosity level.

```yaml
level: "DEBUG"  # Show all messages (for troubleshooting)
```

**Levels:**
- **DEBUG:** Everything (very verbose)
- **INFO:** Normal operations, emails sent, replies detected
- **WARNING:** Potential issues, skipped contacts
- **ERROR:** Failures only

#### file
**Type:** String
**Default:** "logs/sequence.log"
**Description:** Log file path.

```yaml
file: "logs/sequence_2024.log"
```

---

## GUI Configuration (gui_config.yaml)

### Complete Example

```yaml
# GUI Configuration

paths:
  project_folder: "C:/EmailSequence"
  python_executable: "python"
  config_file: "config.yaml"
  contacts_file: "contacts.xlsx"
  templates_folder: "templates"
  logs_folder: "logs"

appearance:
  theme: "dark"  # dark, light, system
  color_scheme: "blue"  # blue, green, dark-blue
  window_width: 1200
  window_height: 800
  sidebar_width: 200

behavior:
  auto_refresh_seconds: 30
  confirm_before_send: true
  show_notifications: true
  minimize_to_tray: true
  start_minimized: false

recent_projects: []
```

### Paths Configuration

#### project_folder
**Type:** String (Path)
**Required:** Yes
**Description:** Root folder containing all project files.

```yaml
project_folder: "C:/Users/John/Documents/EmailSequence"
# or
project_folder: "/home/john/EmailSequence"
```

**Important:** Use forward slashes `/` even on Windows, or escape backslashes `\\`.

#### contacts_file
**Type:** String (Relative path)
**Default:** "contacts.xlsx"
**Description:** Contact database filename (relative to project_folder).

```yaml
contacts_file: "data/contacts_2024.xlsx"
```

---

### Appearance Settings

#### theme
**Type:** String
**Options:** dark, light, system
**Default:** dark
**Description:** Application color theme.

```yaml
theme: "system"  # Match OS theme
```

#### color_scheme
**Type:** String
**Options:** blue, green, dark-blue
**Default:** blue
**Description:** Accent color scheme.

```yaml
color_scheme: "green"
```

#### window_width / window_height
**Type:** Integer (pixels)
**Defaults:** 1200 x 800
**Description:** Initial window size.

```yaml
window_width: 1920
window_height: 1080
```

---

### Behavior Settings

#### auto_refresh_seconds
**Type:** Integer (seconds)
**Default:** 30
**Range:** 5-300
**Description:** Dashboard auto-refresh interval.

```yaml
auto_refresh_seconds: 60  # Refresh every minute
```

Set to `0` to disable auto-refresh.

#### confirm_before_send
**Type:** Boolean
**Default:** true
**Description:** Show confirmation dialog before sending emails.

```yaml
confirm_before_send: true  # Recommended for safety
```

#### show_notifications
**Type:** Boolean
**Default:** true
**Description:** Show system notifications for events.

```yaml
show_notifications: false  # Disable notifications
```

#### minimize_to_tray
**Type:** Boolean
**Default:** true
**Description:** Minimize to system tray instead of taskbar.

```yaml
minimize_to_tray: false  # Minimize normally
```

---

## Contact File Format

### Excel Structure

The `contacts.xlsx` file must have these columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| title | Text | Yes | Mr, Ms, Dr, Prof, etc. |
| first_name | Text | Yes | Contact's first name |
| last_name | Text | Yes | Contact's last name |
| email | Text | Yes | Contact's email address (unique) |
| company | Text | Yes | Company name |
| status | Text | Yes | Current status (see below) |

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not yet contacted |
| `sent` | Initial email sent |
| `followup_1` | First follow-up sent |
| `followup_2` | Second follow-up sent |
| `followup_3` | Third follow-up sent |
| `replied` | Contact replied (stops sequence) |
| `bounced` | Email bounced (stops sequence) |
| `opted_out` | Contact opted out (stops sequence) |
| `completed` | Sequence completed (all follow-ups sent, no reply) |

### Example Contact File

```
title    first_name  last_name  email                    company         status
Mr       Jean        Dupont     jean.dupont@acme.com    Acme Corp      pending
Ms       Marie       Martin     marie@corp.fr           Corp SA        sent
Dr       Pierre      Durand     pierre@company.com      Company Inc    replied
```

### Creating Contacts File

**Option 1: Excel**
1. Open Excel
2. Create headers as shown above
3. Fill in contact data
4. Save as `contacts.xlsx`

**Option 2: GUI Import**
1. Open GUI
2. Go to Contacts tab
3. Click "Import CSV"
4. Map columns to fields

**Option 3: Python Script**
```python
import pandas as pd

contacts = [
    {
        'title': 'Mr',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Example Corp',
        'status': 'pending'
    },
    # Add more contacts...
]

df = pd.DataFrame(contacts)
df.to_excel('contacts.xlsx', index=False)
```

---

## Email Templates

### Template File Format

Templates are HTML files with placeholders.

#### Location
`templates/{template_name}.html`

#### Available Templates
- `initial.html` - Initial outreach email
- `followup_1.html` - First follow-up
- `followup_2.html` - Second follow-up
- `followup_3.html` - Third follow-up

### Placeholders

Available placeholders in templates:

| Placeholder | Replaced With | Example |
|-------------|---------------|---------|
| `{title}` | Contact's title | Mr |
| `{first_name}` | Contact's first name | John |
| `{last_name}` | Contact's last name | Doe |
| `{full_name}` | First + last name | John Doe |
| `{email}` | Contact's email | john@example.com |
| `{company}` | Contact's company | Acme Corp |
| `{sender_name}` | Your name (from config) | Jane Smith |

### Template Structure

```html
<!-- Subject: Your Subject Line Here -->
<p>Dear {title} {last_name},</p>

<p>Email body with {placeholders}.</p>

<p>Best regards,<br>
{sender_name}</p>
```

**Important:**
- Subject must be in first line as HTML comment
- Use HTML tags for formatting: `<p>`, `<br>`, `<strong>`, `<em>`
- Keep formatting simple for better compatibility

### Example: Initial Email

```html
<!-- Subject: Partnership Opportunity - ISIT -->
<p>Dear {title} {last_name},</p>

<p>I hope this message finds you well.</p>

<p>I am reaching out to discuss a potential partnership opportunity between {company} and ISIT. We specialize in innovative technology solutions and believe there could be synergies with your organization.</p>

<p>Would you be available for a brief call next week to explore this further?</p>

<p>Best regards,<br>
{sender_name}<br>
Director, ISIT</p>
```

### Example: Follow-up Email

```html
<!-- Subject: RE: Partnership Opportunity - ISIT -->
<p>Dear {title} {last_name},</p>

<p>I wanted to follow up on my previous email regarding a potential partnership between {company} and ISIT.</p>

<p>I understand you may be busy, but I believe this opportunity could be mutually beneficial. Would you have 15 minutes this week for a quick conversation?</p>

<p>Looking forward to hearing from you.</p>

<p>Best regards,<br>
{sender_name}</p>
```

---

## Advanced Settings

### Custom Status Workflow

You can add custom status values by modifying the application logic.

### Multiple Projects

To manage multiple campaigns:

1. Create separate folders:
```
EmailSequence/
├── Campaign_2024_Q1/
│   ├── contacts.xlsx
│   ├── templates/
│   └── logs/
└── Campaign_2024_Q2/
    ├── contacts.xlsx
    ├── templates/
    └── logs/
```

2. Update `gui_config.yaml` to point to active campaign folder

### Testing Mode

To test without sending emails:

```yaml
# config.yaml
safety:
  test_mode: true
```

This will:
- Log what would be sent
- Not actually send emails
- Update contact status normally

---

## Best Practices

### Email Configuration

1. **Start Conservative**
   - Use longer delays (10-15 seconds)
   - Lower max_emails_per_run (20-50)
   - Monitor for any issues

2. **Follow-up Timing**
   - B2B: 3-5 days between follow-ups
   - B2C: 2-3 days between follow-ups
   - Adjust based on response rate

3. **Subject Lines**
   - Keep under 50 characters
   - Personalize when possible
   - A/B test different variations

### Contact Management

1. **Data Quality**
   - Verify emails before importing
   - Remove duplicates
   - Keep company names consistent

2. **Segmentation**
   - Create separate contact files by industry/region
   - Run separate sequences for each segment
   - Track performance separately

3. **Regular Cleanup**
   - Remove bounced emails
   - Update opted-out contacts
   - Archive completed sequences

### Template Best Practices

1. **Keep It Simple**
   - Plain HTML only
   - No embedded images
   - No complex CSS

2. **Personalization**
   - Use placeholders effectively
   - Reference their company/industry
   - Show you researched them

3. **Call to Action**
   - Clear next step
   - Specific ask (call, meeting, demo)
   - Make it easy to respond

### Logging

1. **Development:** Use DEBUG level
2. **Production:** Use INFO level
3. **Troubleshooting:** Enable DEBUG temporarily
4. **Rotate Logs:** Set reasonable max_size_mb

---

## Configuration Checklist

Before starting a sequence:

- [ ] `config.yaml` exists with correct settings
- [ ] `gui_config.yaml` exists and paths are correct
- [ ] All template files created and tested
- [ ] `contacts.xlsx` has valid data
- [ ] All contacts have status "pending"
- [ ] Templates folder exists
- [ ] Logs folder exists
- [ ] Outlook is configured and running
- [ ] Test mode enabled for first run
- [ ] Reviewed all placeholders in templates

---

## Troubleshooting

### Configuration Not Loading

**Check:**
- YAML syntax is correct (use yamllint.com)
- No tabs (use spaces for indentation)
- Strings with special characters are quoted

### Paths Not Working

**Windows:**
```yaml
# Good
project_folder: "C:/EmailSequence"
project_folder: "C:\\EmailSequence"

# Bad
project_folder: "C:\EmailSequence"  # Backslashes need escaping
```

### Templates Not Found

**Check:**
- Template files are in templates/ folder
- File names exactly match (case-sensitive on Linux)
- Files have .html extension

---

## Next Steps

1. Review [INSTALLATION.md](INSTALLATION.md) if not installed
2. Read [GUI_MANUAL.md](GUI_MANUAL.md) for usage instructions
3. Set up your first test sequence
4. Monitor logs and adjust configuration as needed

---

## Version Information

- Configuration Version: 1.0.0-20260119
- Last Updated: 2026-01-19
- Compatible with: Email Sequence Manager 1.0.0-20260119
