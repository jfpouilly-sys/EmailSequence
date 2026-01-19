# Email Sequence Manager - GUI User Manual

Complete guide to using the Email Sequence Manager graphical user interface.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Contacts Management](#contacts-management)
4. [Sequence Control](#sequence-control)
5. [Template Editor](#template-editor)
6. [Logs Viewer](#logs-viewer)
7. [Settings](#settings)
8. [Common Workflows](#common-workflows)
9. [Tips and Tricks](#tips-and-tricks)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launching the Application

**Method 1: Standalone Executable**
```
Double-click EmailSequenceManager.exe
```

**Method 2: Python Script**
```bash
cd C:\EmailSequence
python run_gui.py
```

### First Launch

On first launch:
1. The application will create default configuration files
2. You'll see the Dashboard with zero contacts
3. Navigate to Settings to configure paths

---

## Dashboard

The Dashboard is your command center for monitoring sequence progress.

### Overview

The Dashboard displays:
- **Metrics Cards:** Pending, Sent, Replied, Reply Rate
- **Quick Actions:** Start Sequence, Check Replies, Send Follow-ups
- **Recent Activity:** Latest log entries
- **Sequence Status:** Current sequence information

### Metrics Cards

#### Pending
**Shows:** Number of contacts with status "pending"
**Meaning:** Contacts who haven't received the initial email yet

#### Sent
**Shows:** Number of contacts who received emails
**Includes:** sent, followup_1, followup_2, followup_3 statuses
**Meaning:** Total contacts actively in the sequence

#### Replied
**Shows:** Number of contacts who replied
**Meaning:** Successful responses (sequence stops for these contacts)

#### Reply Rate
**Shows:** Percentage of sent emails that got replies
**Formula:** (Replied / Total Contacted) × 100
**Good Rate:** 10-25% is typical for cold outreach

### Quick Actions

#### Start Sequence
**Purpose:** Send initial emails to all pending contacts
**When to Use:** Beginning a new campaign
**Process:**
1. Click "▶ START SEQUENCE"
2. Confirm the action
3. Emails are sent with configured delay
4. Status updates to "sent"
5. Activity logged

**Safety Features:**
- Confirmation dialog (if enabled)
- Delay between sends
- Maximum emails per run limit

#### Check Replies
**Purpose:** Scan Outlook inbox for replies
**When to Use:** Regularly, or before sending follow-ups
**Process:**
1. Click "🔍 CHECK REPLIES"
2. Scans inbox for last N days (configured)
3. Matches replies to sent emails
4. Updates contact status to "replied"
5. Shows results

**Note:** Replied contacts automatically stop receiving follow-ups.

#### Send Follow-ups
**Purpose:** Send follow-up emails to eligible contacts
**When to Use:** After configured delay period
**Eligible Contacts:**
- Status is "sent" or "followup_X"
- Enough days have passed since initial email
- Haven't reached max follow-ups
- Haven't replied or bounced

**Process:**
1. Click "↻ SEND FOLLOW-UPS"
2. System calculates who needs follow-ups
3. Confirm the action
4. Follow-ups are sent
5. Status updates to next follow-up level

### Recent Activity

Shows the last 20 log entries in reverse chronological order.

**Icons:**
- `✓` - Reply received
- `→` - Email sent
- `▶` - Sequence started
- `+` - Contacts imported

**Auto-Refresh:**
Automatically updates every 30 seconds (configurable in Settings).

### Sequence Status

Displays information about current sequence:
- **Current ID:** Sequence identifier (usually seq_YYYYMMDD)
- **Status:** Active, Paused, Stopped, or Ready
- **Started:** When sequence began
- **Total Contacts:** Number of contacts in sequence
- **Next Action:** Upcoming scheduled operation

---

## Contacts Management

The Contacts tab is your contact database interface.

### Contact Table

#### Columns

| Column | Description |
|--------|-------------|
| ☐ | Selection checkbox |
| Title | Mr, Ms, Dr, etc. |
| First Name | Contact's first name |
| Last Name | Contact's last name |
| Email | Email address (unique identifier) |
| Company | Company/organization name |
| Status | Current sequence status with icon |

#### Status Icons

- ○ **Pending** - Not yet contacted (gray)
- ● **Sent** - Initial email sent (blue)
- ● **Follow-up 1/2/3** - Follow-up sent (orange)
- ✓ **Replied** - Contact replied (green)
- ✗ **Bounced** - Email bounced (red)
- ⛔ **Opted Out** - Contact opted out (black)
- ◆ **Completed** - All follow-ups sent, no reply (purple)

### Toolbar Actions

#### Add Contact
**Purpose:** Manually add a single contact

**Steps:**
1. Click "+ Add Contact"
2. Detail panel clears
3. Fill in contact information:
   - Title (dropdown)
   - First name
   - Last name
   - Email (required)
   - Company
4. Click "💾 Save Changes"

**Validation:**
- Email is required
- Email must be unique

#### Import CSV
**Purpose:** Bulk import contacts from CSV file

**Steps:**
1. Click "📥 Import CSV"
2. Select your CSV file
3. **Column Mapping Dialog** opens:
   - Left side: Your CSV columns
   - Right side: System fields
   - Arrows show mapping
4. Adjust mappings if needed
5. Click "Import"
6. Contacts are added to database
7. Duplicates (by email) are skipped

**CSV Requirements:**
- Must have header row
- Encoding: UTF-8
- Delimiter: Comma

**Auto-Mapping:**
The system tries to auto-map common column names:
- "email", "e-mail" → email
- "first", "firstname", "prénom" → first_name
- "last", "lastname", "nom" → last_name
- "company", "société" → company

#### Export
**Purpose:** Save contact list to file

**Formats:**
- Excel (.xlsx) - Default, preserves all data
- CSV (.csv) - Compatible with other tools

**Steps:**
1. Click "📤 Export"
2. Choose save location and format
3. All contacts are exported

**Use Cases:**
- Backup before major changes
- Share with team
- Import to other CRM

#### Delete Selected
**Purpose:** Remove multiple contacts

**Steps:**
1. Check boxes next to contacts to delete
2. Click "🗑 Delete Selected"
3. Confirm deletion (cannot be undone!)
4. Contacts are permanently removed

**Warning:** This action is irreversible. Export first if unsure.

### Filtering and Search

#### Filter by Status
**Dropdown:** Shows all status options
**Purpose:** View only contacts with specific status

**Example Use Cases:**
- Show only "pending" to see who hasn't been contacted
- Show only "replied" to see successful responses
- Show only "sent" to see who needs follow-ups

#### Search
**Real-time search** across:
- First name
- Last name
- Email
- Company

**Tips:**
- Search is case-insensitive
- Partial matches work
- Updates as you type

### Contact Detail Panel

Select a contact in the table to view/edit details in the panel below.

#### Fields

- **Title:** Dropdown (Mr, Ms, Mrs, Dr, Prof)
- **First Name:** Text field
- **Last Name:** Text field
- **Email:** Text field (required, unique)
- **Company:** Text field
- **Status:** Visual badge (read-only)

#### Actions

**Save Changes**
- Updates contact in database
- Validates email
- Shows success message

**Reset Status**
- Changes status back to "pending"
- Useful for re-contacting someone

**Mark Opted-Out**
- Sets status to "opted_out"
- Prevents further emails
- Use when contact requests removal

---

## Sequence Control

The Sequence tab provides control over email sequence execution.

### Current Sequence Status

**Displays:**
- **Sequence ID:** Unique identifier
- **Status:** Current state (Active/Inactive/Paused)
- **Started:** Start date and time
- **Progress Bar:** Visual progress
- **Progress Text:** X% (completed/total)
- **Breakdown:** Replied, In Progress, Remaining

### Main Actions

#### Start New Sequence
**Purpose:** Begin sending initial emails to pending contacts

**When to Use:**
- Starting a new campaign
- After importing new contacts
- After resetting statuses

**Process:**
1. Counts pending contacts
2. Shows confirmation dialog
3. Sends initial emails with delay
4. Updates statuses to "sent"
5. Creates sequence ID
6. Logs all activity

**Safety:**
- Confirmation required (if enabled in settings)
- Only sends to "pending" status
- Respects delay between sends
- Enforces daily send limit

#### Pause Sequence
**Purpose:** Temporarily stop automatic operations

**Effect:**
- Auto-cycling stops (if enabled)
- Manual operations still work
- No emails sent automatically
- Sequence can be resumed later

**Use Cases:**
- Campaign needs review
- Holiday break
- Template updates needed

#### Stop Sequence
**Purpose:** End current sequence

**Effect:**
- Sequence marked as stopped
- Auto-cycling disabled
- Progress saved
- Contact statuses preserved

**Warning:**
- Cannot resume stopped sequence
- Must start new sequence to continue

### Manual Operations

These operations run immediately when clicked:

#### Check Replies Now
**What It Does:**
1. Connects to Outlook
2. Scans inbox for last N days
3. Looks for replies to sent emails
4. Matches by email address and subject
5. Updates status to "replied"
6. Shows count of replies found

**Last Check Time:**
Displays when check was last run.

**Frequency:**
- Before sending follow-ups (recommended)
- Daily for active campaigns
- After receiving notification

#### Send Follow-ups Now
**What It Does:**
1. Checks each contact's status and dates
2. Calculates who needs follow-up
3. Sends appropriate follow-up template
4. Updates status (sent → followup_1, etc.)
5. Logs all sends

**Last Sent Time:**
Displays when follow-ups were last sent.

**Eligibility Rules:**
- Status is "sent" or "followup_X"
- Required days have passed
- Haven't hit max follow-ups
- Not replied/bounced/opted out

#### Run Full Cycle
**What It Does:**
Runs both operations in sequence:
1. Check Replies
2. Send Follow-ups

**When to Use:**
- Regular maintenance
- Before logging off for the day
- Automated via scheduler

### Scheduling

**Purpose:** Automate sequence operations

#### Enable Automatic Cycling
**Checkbox:** Enable/disable automation
**Effect:** When enabled, runs full cycle at specified interval

#### Run Every X Minutes
**Field:** Interval in minutes
**Default:** 30 minutes
**Range:** 5-1440 (24 hours)

**Examples:**
- 15 minutes: Very active monitoring
- 30 minutes: Balanced approach
- 60 minutes: Light monitoring
- 240 minutes: Minimal automation

#### Active Hours
**Fields:** Start time and end time
**Format:** HH:MM (24-hour)
**Purpose:** Only run automation during work hours

**Example:**
- Start: 08:00
- End: 18:00
- Result: No emails sent outside 8 AM - 6 PM

#### Active Days
**Checkboxes:** Select days of week
**Default:** Monday - Friday
**Purpose:** Prevent emails on weekends

**Best Practice:**
- B2B: Monday-Friday only
- B2C: May include weekends

#### Update Schedule
**Button:** Save scheduling changes
**Effect:** Updates Task Scheduler (Windows) or cron (Linux)

**Note:** Requires admin/root permissions on first setup.

### Follow-up Timing

**Purpose:** Configure when follow-ups are sent

#### Days After Initial Email

- **Follow-up #1:** Days to wait before first follow-up
- **Follow-up #2:** Days to wait before second follow-up
- **Follow-up #3:** Days to wait before third follow-up

**Default Values:**
- FU#1: 3 days
- FU#2: 7 days
- FU#3: 14 days

**Important:** These are cumulative from initial send, not from previous follow-up.

**Example:**
- Initial sent: January 1
- FU#1 sent: January 4 (3 days later)
- FU#2 sent: January 8 (7 days after initial)
- FU#3 sent: January 15 (14 days after initial)

#### Max Follow-ups
**Field:** Maximum number of follow-ups to send
**Default:** 3
**Range:** 0-10

**Effect:**
- Controls total email touches
- Higher = more persistent
- Lower = less aggressive

#### Save Timing
**Button:** Save timing configuration
**Effect:** Updates config.yaml file

---

## Template Editor

The Templates tab provides a visual editor for email templates.

### Template Selector

**Dropdown:** Choose which template to edit
**Options:**
- Initial Email
- Follow-up #1
- Follow-up #2
- Follow-up #3

### Subject Line

**Field:** Email subject line
**Supports:** Placeholders (e.g., {company})
**Tip:** Keep under 50 characters for best inbox display

### Split Editor View

#### Left Side: Edit Panel
**Purpose:** Edit HTML template code
**Font:** Monospace for code editing
**Features:**
- Live updates preview
- HTML formatting
- Placeholder support

**Editing Tips:**
- Use `<p>` for paragraphs
- Use `<br>` for line breaks
- Use `<strong>` for bold
- Use `<em>` for italic
- Keep formatting simple

#### Right Side: Preview Panel
**Purpose:** See rendered email
**Updates:** Automatically as you type
**Shows:** Email with placeholders replaced

**Preview Benefits:**
- See final appearance
- Catch formatting errors
- Verify placeholder replacement

### Placeholder Buttons

**Quick Insert:** Click button to insert placeholder at cursor

**Available Placeholders:**
- `{title}` - Mr, Ms, Dr, etc.
- `{first_name}` - Contact's first name
- `{last_name}` - Contact's last name
- `{full_name}` - First + last name
- `{email}` - Contact's email
- `{company}` - Contact's company
- `{sender_name}` - Your name (from config)

**Usage:**
1. Click in editor where you want placeholder
2. Click placeholder button
3. Placeholder is inserted
4. Preview updates automatically

### Preview Contact Selector

**Dropdown:** Choose which contact to use for preview
**Purpose:** See how email looks with real data

**Default:** Uses first contact in database
**Updates:** Preview refreshes with selected contact's data

### Actions

#### Save Template
**Button:** 💾 Save Template
**Effect:**
- Saves subject and body to template file
- Writes to templates/[template_name].html
- Shows success message

**File Format:**
```html
<!-- Subject: Your Subject -->
<p>Email body...</p>
```

#### Revert Changes
**Button:** ↩ Revert Changes
**Effect:**
- Reloads template from file
- Discards unsaved changes
- Useful if you make mistakes

#### Send Test Email
**Button:** 📧 Send Test Email
**Purpose:** Send test to yourself

**Process:**
1. Fills template with preview contact data
2. Sends to your Outlook account
3. Shows confirmation

**Use Cases:**
- Verify formatting in inbox
- Test links
- Check mobile display

---

## Logs Viewer

The Logs tab displays application activity history.

### Log Viewer

**Display:** Scrollable text area with log entries
**Font:** Monospace for easy reading
**Auto-scroll:** Checkbox to auto-scroll to latest entries

### Filters

#### Level Filter
**Dropdown:** Filter by log level
**Options:**
- All Levels
- DEBUG - Everything (very verbose)
- INFO - Normal operations
- WARNING - Potential issues
- ERROR - Failures only

**Color Coding:**
- DEBUG: Gray
- INFO: White
- WARNING: Yellow
- ERROR: Red

#### Date Filter
**Dropdown:** Filter by date range
**Options:**
- Today - Last 24 hours
- Last 7 Days
- Last 30 Days
- All - Complete history

**Performance Note:** "All" may be slow for large log files.

#### Search Box
**Field:** Search within log entries
**Search:** Case-insensitive, real-time
**Highlights:** Matches in results

**Search Tips:**
- Search for email addresses
- Search for error messages
- Search for contact names

### Toolbar Actions

#### Open Folder
**Button:** 📂 Open Folder
**Effect:** Opens logs folder in file explorer

**Use Cases:**
- View log files directly
- Archive old logs
- Share logs for support

#### Clear Logs
**Button:** 🗑 Clear Logs
**Effect:** Permanently deletes log file

**Warning:**
- Cannot be undone
- Creates fresh log file
- Consider backing up first

### Log Statistics

Displays summary at bottom:
- **Today:** Log entries from last 24 hours
- **Errors:** Total error entries
- **Warnings:** Total warning entries
- **Emails:** Email-related entries

**Use Cases:**
- Quick health check
- Identify issues
- Track activity volume

### Understanding Log Entries

**Format:**
```
YYYY-MM-DD HH:MM:SS | LEVEL | Message
```

**Example:**
```
2024-01-17 14:32:15 | INFO | Reply detected: jean@acme.com
2024-01-17 14:30:22 | INFO | Follow-up #2 sent: marie@corp.fr
2024-01-17 10:00:45 | WARNING | Skipped: invalid@bad (invalid format)
2024-01-17 10:00:30 | ERROR | Failed to connect to Outlook
```

---

## Settings

The Settings tab configures all application parameters.

### Paths

**Purpose:** Tell application where to find files

#### Project Folder
**Field:** Root folder containing all files
**Default:** Application directory
**Browse:** Click to select folder

**Important:** All relative paths are relative to this folder.

#### Python Executable
**Field:** Path to Python interpreter
**Default:** "python" or "python3"
**When to Change:** Using specific Python version

#### Contacts File
**Field:** Excel file with contacts
**Default:** "contacts.xlsx"
**Browse:** Click to select file

#### Templates Folder
**Field:** Folder containing email templates
**Default:** "templates"
**Browse:** Click to select folder

**Validation:**
After saving, paths are checked. Missing paths shown in warning.

### Appearance

#### Theme
**Radio Buttons:** Dark, Light, System
**Default:** Dark
**Effect:** Immediate color scheme change

**Options:**
- **Dark:** Black background, white text
- **Light:** White background, black text
- **System:** Match operating system theme

#### Color Scheme
**Dropdown:** Blue, Green, Dark-Blue
**Default:** Blue
**Effect:** Accent color for buttons, highlights

**Choose Based On:**
- Personal preference
- Company branding
- Visual accessibility

### Email Settings

**Note:** These are for display/reference. Core email settings in config.yaml.

#### Sender Name
**Field:** Your name for signatures
**Used In:** {sender_name} placeholder
**Example:** "Jean-François Pouilly"

#### Default Subject
**Field:** Fallback subject line
**Used When:** Template doesn't specify subject

#### Delay Between Sends
**Field:** Seconds to wait between emails
**Default:** 5
**Recommended:** 5-10 for safety

#### Inbox Scan Depth
**Field:** Days to look back in inbox
**Default:** 30
**Range:** 1-365

**Considerations:**
- Higher = slower scan
- Lower = might miss replies

### Behavior

#### Confirm Before Sending Emails
**Checkbox:** Show confirmation dialogs
**Default:** Enabled
**Recommended:** Keep enabled for safety

**Effect:**
- Prompts before start sequence
- Prompts before send follow-ups
- Prevents accidental sends

#### Show System Notifications
**Checkbox:** Display system notifications
**Default:** Enabled

**Notifications For:**
- Sequence started
- Replies detected
- Errors occurred

#### Minimize to System Tray
**Checkbox:** Minimize to tray vs taskbar
**Default:** Enabled

**Effect:**
- App icon in system tray
- Clicking X minimizes instead of closing
- Right-click tray icon to quit

#### Start Minimized
**Checkbox:** Launch application minimized
**Default:** Disabled

**Use Case:**
- Auto-start with Windows
- Background operation

### Outlook Connection

#### Status Display
Shows current connection status:
- ● Connected - Green indicator
- ○ Not Connected - Gray indicator

**Account:** Displays connected email account

#### Test Connection
**Button:** Verify Outlook connectivity

**Process:**
1. Attempts to connect to Outlook
2. Checks if account is configured
3. Shows result message

**Use When:**
- First setup
- After Outlook configuration changes
- Troubleshooting connection issues

#### Reconnect
**Button:** Force reconnection to Outlook

**Use When:**
- Connection lost
- Outlook restarted
- Account switched

### Action Buttons

#### Save Settings
**Button:** 💾 Save Settings
**Effect:**
- Writes gui_config.yaml
- Validates paths
- Shows success/error message

**Validation:**
- Checks if paths exist
- Warns about missing folders
- Suggests creating missing directories

#### Reset to Defaults
**Button:** ↩ Reset to Defaults
**Effect:**
- Restores all default values
- Requires confirmation
- Reloads interface

**Warning:** Current settings are lost.

#### Export Config
**Button:** 📤 Export Config
**Purpose:** Save configuration to file

**Use Cases:**
- Backup before major changes
- Share configuration with team
- Duplicate setup on another machine

**Process:**
1. Click Export Config
2. Choose save location
3. gui_config.yaml saved to location

---

## Common Workflows

### Starting Your First Sequence

1. **Prepare Contacts**
   - Go to Contacts tab
   - Import CSV or add manually
   - Verify all have status "pending"

2. **Create Templates**
   - Go to Templates tab
   - Edit "Initial Email" template
   - Add personalization with placeholders
   - Save template
   - Send test email to yourself

3. **Configure Settings**
   - Go to Settings tab
   - Verify paths are correct
   - Check email settings
   - Enable confirmations for safety
   - Save settings

4. **Start Sequence**
   - Go to Dashboard
   - Click "▶ START SEQUENCE"
   - Confirm action
   - Watch Recent Activity for sends
   - Verify in Outlook sent folder

5. **Monitor Progress**
   - Check Dashboard metrics
   - Review logs for any errors
   - Wait for configured follow-up delay

### Checking for Replies

**Daily Routine:**

1. Go to Dashboard
2. Click "🔍 CHECK REPLIES"
3. Review how many replies found
4. Go to Contacts tab
5. Filter by "replied" status
6. Review who responded
7. Follow up manually in Outlook

### Sending Follow-ups

**Before Sending:**

1. Go to Dashboard
2. Click "🔍 CHECK REPLIES" first
3. Wait for completion
4. Then click "↻ SEND FOLLOW-UPS"
5. Review eligible contacts count
6. Confirm send
7. Monitor Recent Activity

**Frequency:**
- Check eligibility in Sequence tab
- Typically every 3-7 days
- Based on follow-up timing configuration

### Importing Contacts

**From CSV:**

1. Prepare CSV file with columns:
   - Title, First Name, Last Name, Email, Company
2. Go to Contacts tab
3. Click "📥 Import CSV"
4. Select file
5. Review auto-mapping
6. Adjust if needed
7. Click Import
8. Verify import count
9. Check contacts in table

**Tips:**
- Remove header row issues by checking preview
- Map unmapped columns manually
- Status defaults to "pending"
- Duplicates are skipped

### Managing Bounced Emails

**When Email Bounces:**

1. Check Outlook for bounce notification
2. Note bounced email address
3. Go to Contacts tab
4. Search for email address
5. Select contact
6. Click "⛔ Mark Opted-Out" or delete
7. Save changes

**Prevention:**
- Use email verification service before import
- Clean contact list regularly
- Remove obvious invalid emails

### Handling Opt-outs

**When Someone Opts Out:**

1. Note their email address
2. Go to Contacts tab
3. Search and select contact
4. Click "⛔ Mark Opted-Out"
5. Save changes

**Effect:**
- Status changes to "opted_out"
- No further emails sent
- Excluded from all operations

---

## Tips and Tricks

### Productivity Tips

**Keyboard Shortcuts:**
- Use Tab to navigate between fields
- Enter to submit forms
- Escape to close dialogs

**Batch Operations:**
- Select multiple contacts with checkboxes
- Delete or update in bulk
- Export specific groups

**Search Efficiency:**
- Use partial searches
- Search by company to group contacts
- Filter + search for precise results

### Best Practices

**Template Management:**
- Keep templates in version control
- Test with yourself first
- A/B test different versions
- Keep backup of working templates

**Contact Organization:**
- Use consistent company names
- Clean data before import
- Regular exports for backup
- Tag contacts with custom fields (future feature)

**Monitoring:**
- Check Dashboard daily
- Review logs weekly
- Export data monthly for records
- Track reply rate trends

### Performance Optimization

**For Large Contact Lists (>1000):**

- Increase delay between sends (10-15 sec)
- Send in batches
- Disable auto-refresh or increase interval
- Run overnight for large sends

**Database Maintenance:**

- Export and archive completed sequences
- Start fresh file for new campaigns
- Keep active contacts under 5000

### Customization

**Appearance:**
- Match company brand with color scheme
- Use light theme for bright environments
- System theme for consistency

**Behavior:**
- Disable confirmations once comfortable
- Adjust auto-refresh for your workflow
- Configure notifications per preference

---

## Troubleshooting

### Application Won't Start

**Symptoms:** Double-click does nothing or crashes

**Solutions:**
1. Run from command line to see errors:
   ```bash
   python run_gui.py
   ```
2. Check Python version:
   ```bash
   python --version  # Must be 3.8+
   ```
3. Reinstall dependencies:
   ```bash
   pip install -r requirements-gui.txt
   ```

### Contacts Won't Load

**Symptoms:** Empty contacts table or error message

**Solutions:**
1. Verify contacts.xlsx exists
2. Check file isn't open in Excel
3. Verify file has correct columns
4. Check Settings > Paths > Contacts File

### Templates Not Saving

**Symptoms:** Changes disappear after saving

**Solutions:**
1. Check templates folder exists
2. Verify write permissions
3. Check Settings > Paths > Templates Folder
4. Look for errors in Logs tab

### Outlook Connection Failed

**Symptoms:** "Outlook not connected" or errors when sending

**Solutions:**
1. Verify Outlook is running
2. Check Outlook has configured account
3. Settings > Test Connection
4. Restart Outlook
5. Restart application
6. Check Windows permissions

### Emails Not Sending

**Symptoms:** Sequence starts but no emails appear in Sent folder

**Solutions:**
1. Check Logs tab for errors
2. Verify Outlook connection
3. Check contact status (must be "pending")
4. Verify templates exist
5. Send test email from Templates tab
6. Check Outlook isn't in offline mode

### GUI Freezes

**Symptoms:** Application becomes unresponsive

**Causes:**
- Large operation in progress
- Scanning large inbox
- Processing many contacts

**Solutions:**
1. Wait for operation to complete
2. Check Recent Activity for progress
3. If truly frozen, close and restart
4. Reduce batch sizes
5. Increase delays

### High CPU Usage

**Causes:**
- Auto-refresh too frequent
- Large log files
- Many contacts

**Solutions:**
1. Settings > Increase auto_refresh_seconds
2. Logs > Clear old logs
3. Archive completed contacts
4. Close unnecessary browser tabs

---

## Getting Help

### Before Asking for Help

1. **Check Logs Tab**
   - Look for error messages
   - Note the error details
   - Screenshot if helpful

2. **Verify Configuration**
   - Settings > Paths are correct
   - Templates exist
   - config.yaml is valid YAML

3. **Test with Minimal Data**
   - Create test contact
   - Try single send
   - Isolate the problem

### Information to Provide

When reporting issues:

- Application version
- Operating system
- Python version
- Error message (exact text)
- Steps to reproduce
- Log file excerpt
- Screenshot if relevant

### Resources

- **Installation Issues:** See INSTALLATION.md
- **Configuration Questions:** See CONFIGURATION.md
- **GitHub Issues:** Report bugs and feature requests
- **Email Support:** support@example.com

---

## Quick Reference

### Contact Statuses

| Status | Icon | Color | Meaning |
|--------|------|-------|---------|
| pending | ○ | Gray | Not contacted |
| sent | ● | Blue | Initial sent |
| followup_1/2/3 | ● | Orange | Follow-up sent |
| replied | ✓ | Green | Contact replied |
| bounced | ✗ | Red | Email bounced |
| opted_out | ⛔ | Black | Opted out |
| completed | ◆ | Purple | Sequence done |

### Template Placeholders

| Placeholder | Replaced With |
|-------------|---------------|
| {title} | Mr, Ms, Dr, etc. |
| {first_name} | First name |
| {last_name} | Last name |
| {full_name} | First + last |
| {email} | Email address |
| {company} | Company name |
| {sender_name} | Your name |

### Default Follow-up Schedule

| Follow-up | Days After Initial |
|-----------|-------------------|
| #1 | 3 days |
| #2 | 7 days |
| #3 | 14 days |

---

## Version Information

- Manual Version: 1.0.0-20260119
- Application Version: 1.0.0-20260119
- Last Updated: 2026-01-19
- Compatible With: Email Sequence Manager GUI 1.0.0-20260119
