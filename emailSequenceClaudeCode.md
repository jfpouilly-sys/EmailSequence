# Email Sequence System - Technical Specification for Claude Code

## Overview

Build a Python-based email sequence automation system for Windows 11 that:
- Sends personalized emails via Microsoft Outlook (desktop app)
- Tracks replies automatically by scanning the Outlook inbox
- Updates contact status in an Excel file
- Sends follow-up emails to non-responders after configurable delays

Target: 1-50 contacts per sequence. Single user. Local execution.

---

## Project Structure

```
email-sequence/
├── config.yaml              # User configuration (paths, timing, templates)
├── contacts.xlsx            # Contact database (created if missing)
├── templates/
│   ├── initial.html         # First email template
│   ├── followup_1.html      # First follow-up template
│   ├── followup_2.html      # Second follow-up template
│   └── followup_3.html      # Third follow-up template
├── logs/
│   └── sequence.log         # Activity log (auto-created)
├── src/
│   ├── __init__.py
│   ├── config.py            # Load and validate config.yaml
│   ├── contact_tracker.py   # Excel read/write operations
│   ├── outlook_manager.py   # Outlook COM automation
│   ├── sequence_engine.py   # Main orchestration logic
│   └── template_engine.py   # Email personalization
├── main.py                  # CLI entry point
└── requirements.txt         # Python dependencies
```

---

## Dependencies

**requirements.txt:**
```
pywin32>=306
pandas>=2.0.0
openpyxl>=3.1.0
pyyaml>=6.0
click>=8.0.0
```

---

## Configuration File

**config.yaml:**
```yaml
# Paths
contacts_file: "contacts.xlsx"
templates_folder: "templates"
log_file: "logs/sequence.log"

# Email settings
sender_name: "Jean-François"           # Display name for From field
default_subject: "Partnership Opportunity - ISIT"

# Sequence timing (in days)
followup_delays:
  - 3    # Days after initial send for followup_1
  - 7    # Days after initial send for followup_2
  - 14   # Days after initial send for followup_3

max_followups: 3   # Stop after this many follow-ups

# Reply detection
inbox_scan_days: 30          # How far back to scan inbox
match_by: "conversation"     # "conversation" or "subject"

# Safety settings
send_delay_seconds: 5        # Pause between emails (avoid spam flags)
dry_run: false               # If true, display emails but don't send
```

---

## Data Model

### Excel File: contacts.xlsx

**Required columns (create if missing):**

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| title | string | Salutation | Mr, Ms, Dr |
| first_name | string | First name | Jean |
| last_name | string | Last name | Dupont |
| email | string | Email address | jean@company.com |
| company | string | Company name | Acme Corp |
| status | string | Current state (see below) | pending |
| sequence_id | string | Unique ID for this sequence run | seq_20260117 |
| initial_sent_date | datetime | When first email was sent | 2026-01-10 14:30:00 |
| last_contact_date | datetime | When last email was sent | 2026-01-13 09:00:00 |
| followup_count | integer | Number of follow-ups sent (0-3) | 1 |
| conversation_id | string | Outlook ConversationTopic | Partnership Opportunity - ISIT |
| replied_date | datetime | When reply was received | 2026-01-12 16:45:00 |
| notes | string | Free-form notes | Met at trade show |

**Status values (enum):**
- `pending` - Not yet contacted in this sequence
- `sent` - Initial email sent, awaiting reply
- `followup_1` - First follow-up sent
- `followup_2` - Second follow-up sent
- `followup_3` - Third follow-up sent
- `replied` - Contact replied (sequence complete)
- `bounced` - Email bounced/failed
- `opted_out` - Contact requested removal
- `completed` - Max follow-ups reached, no reply

---

## Class Specifications

### 1. Config (src/config.py)

```python
class Config:
    """Load and validate configuration from YAML file."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Load config.yaml and set defaults for missing values.
        Raise FileNotFoundError if config doesn't exist.
        Raise ValueError if required fields are invalid.
        """
        pass
    
    @property
    def contacts_file(self) -> str: ...
    
    @property
    def templates_folder(self) -> str: ...
    
    @property
    def followup_delays(self) -> list[int]: ...
    
    @property
    def dry_run(self) -> bool: ...
    
    # ... other properties matching config.yaml fields
```

---

### 2. ContactTracker (src/contact_tracker.py)

```python
from pandas import DataFrame
from datetime import datetime

class ContactTracker:
    """Manage contact database in Excel file."""
    
    def __init__(self, excel_path: str):
        """
        Load Excel file into pandas DataFrame.
        Create file with headers if it doesn't exist.
        Validate required columns exist.
        """
        pass
    
    def get_all_contacts(self) -> DataFrame:
        """Return all contacts as DataFrame."""
        pass
    
    def get_pending_contacts(self) -> DataFrame:
        """Return contacts with status='pending'."""
        pass
    
    def get_contacts_needing_followup(self, followup_delays: list[int]) -> DataFrame:
        """
        Return contacts eligible for follow-up based on:
        - status in ['sent', 'followup_1', 'followup_2']
        - followup_count < max_followups
        - days since last_contact_date >= appropriate delay from followup_delays
        
        Example: If followup_delays=[3,7,14] and contact has followup_count=1,
        they need followup_2 if 7+ days have passed since last_contact_date.
        """
        pass
    
    def update_contact(self, email: str, updates: dict) -> bool:
        """
        Update a contact's fields by email address.
        
        Args:
            email: Contact's email address (case-insensitive match)
            updates: Dict of column->value to update
                     e.g., {"status": "sent", "initial_sent_date": datetime.now()}
        
        Returns:
            True if contact found and updated, False if not found.
        
        Automatically saves to Excel after update.
        """
        pass
    
    def add_contact(self, contact_data: dict) -> bool:
        """
        Add a new contact row.
        Validates required fields: first_name, last_name, email.
        Sets status='pending' if not provided.
        Returns False if email already exists.
        """
        pass
    
    def save(self) -> None:
        """Save current DataFrame to Excel file."""
        pass
    
    def get_contact_by_email(self, email: str) -> dict | None:
        """Return contact as dict or None if not found."""
        pass
```

---

### 3. OutlookManager (src/outlook_manager.py)

```python
from typing import Optional
from datetime import datetime

class OutlookManager:
    """Handle all Outlook COM automation."""
    
    def __init__(self):
        """
        Initialize Outlook COM connection.
        Raise ConnectionError if Outlook is not running/available.
        
        Use: win32com.client.Dispatch('Outlook.Application')
        """
        pass
    
    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        dry_run: bool = False
    ) -> dict:
        """
        Send an email via Outlook.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            html_body: HTML-formatted email body
            dry_run: If True, display email instead of sending
        
        Returns:
            {
                "success": bool,
                "conversation_id": str,  # From mail.ConversationTopic
                "sent_time": datetime,
                "error": str | None
            }
        
        Implementation notes:
        - Use outlook.CreateItem(0) for new email
        - Set mail.To, mail.Subject, mail.HTMLBody
        - If dry_run: call mail.Display() instead of mail.Send()
        - Capture ConversationTopic AFTER sending (it's assigned by Outlook)
        """
        pass
    
    def check_for_reply(
        self,
        original_subject: str,
        sender_email: str,
        since_date: datetime
    ) -> dict | None:
        """
        Check inbox for reply from a specific sender.
        
        Args:
            original_subject: The subject line we sent (or ConversationTopic)
            sender_email: Email address to look for
            since_date: Only check emails received after this date
        
        Returns:
            None if no reply found, or:
            {
                "received_time": datetime,
                "subject": str,
                "preview": str  # First 200 chars of body
            }
        
        Implementation notes:
        - Access inbox: namespace.GetDefaultFolder(6)
        - Iterate inbox.Items
        - Match by ConversationTopic containing original_subject
        - Match sender via SenderEmailAddress (handle both SMTP and Exchange format)
        - Only consider items with ReceivedTime > since_date
        """
        pass
    
    def get_recent_replies(
        self,
        known_contacts: list[str],
        days_back: int = 30
    ) -> list[dict]:
        """
        Batch scan inbox for replies from any known contact.
        
        Args:
            known_contacts: List of email addresses to look for
            days_back: How many days back to scan
        
        Returns:
            List of {
                "sender_email": str,
                "received_time": datetime,
                "subject": str,
                "conversation_topic": str
            }
        
        More efficient than calling check_for_reply() per contact.
        """
        pass
    
    def is_outlook_running(self) -> bool:
        """Check if Outlook application is available."""
        pass
```

---

### 4. TemplateEngine (src/template_engine.py)

```python
class TemplateEngine:
    """Load and personalize email templates."""
    
    def __init__(self, templates_folder: str):
        """
        Initialize with path to templates folder.
        Verify folder exists.
        """
        pass
    
    def load_template(self, template_name: str) -> str:
        """
        Load template file content.
        
        Args:
            template_name: e.g., "initial" loads "initial.html"
        
        Returns:
            Raw HTML content of template file.
        
        Raises:
            FileNotFoundError if template doesn't exist.
        """
        pass
    
    def render(self, template_name: str, contact: dict) -> str:
        """
        Load template and replace placeholders with contact data.
        
        Placeholders use format: {field_name}
        Available placeholders:
        - {title} - Mr, Ms, Dr, etc.
        - {first_name}
        - {last_name}
        - {full_name} - Computed: "{first_name} {last_name}"
        - {email}
        - {company}
        - {sender_name} - From config
        
        Example template:
        ```html
        <p>Dear {title} {last_name},</p>
        <p>I hope this email finds you well...</p>
        <p>Best regards,<br>{sender_name}</p>
        ```
        
        Missing placeholders should remain as-is (don't crash).
        """
        pass
    
    def get_available_templates(self) -> list[str]:
        """Return list of available template names (without .html)."""
        pass
```

---

### 5. SequenceEngine (src/sequence_engine.py)

```python
from datetime import datetime
import logging

class SequenceEngine:
    """Main orchestrator for email sequences."""
    
    def __init__(self, config: Config):
        """
        Initialize with config.
        Create instances of ContactTracker, OutlookManager, TemplateEngine.
        Set up logging to config.log_file.
        """
        pass
    
    def start_sequence(self, sequence_id: str = None) -> dict:
        """
        Send initial emails to all pending contacts.
        
        Args:
            sequence_id: Optional ID for this run. 
                        Defaults to "seq_YYYYMMDD_HHMMSS"
        
        Process:
        1. Get all contacts with status='pending'
        2. For each contact:
           a. Render 'initial' template
           b. Send email via OutlookManager
           c. Update contact: status='sent', initial_sent_date=now,
              last_contact_date=now, followup_count=0, 
              conversation_id=<from Outlook>, sequence_id=<current>
           d. Wait send_delay_seconds between sends
           e. Log success/failure
        
        Returns:
            {
                "sent": int,
                "failed": int,
                "errors": list[str]
            }
        """
        pass
    
    def check_replies(self) -> dict:
        """
        Scan inbox and update contacts who have replied.
        
        Process:
        1. Get all contacts with status in ['sent', 'followup_1', 'followup_2', 'followup_3']
        2. Use OutlookManager.get_recent_replies() for efficiency
        3. For each reply found:
           a. Update contact: status='replied', replied_date=<received_time>
           b. Log the reply
        
        Returns:
            {
                "replies_found": int,
                "contacts_updated": list[str]  # email addresses
            }
        """
        pass
    
    def send_followups(self) -> dict:
        """
        Send follow-up emails to non-responders.
        
        Process:
        1. Call check_replies() first to ensure status is current
        2. Get contacts needing follow-up via ContactTracker
        3. For each contact:
           a. Determine which follow-up (followup_count + 1)
           b. Render appropriate template (followup_1, followup_2, etc.)
           c. Send email with same subject line (creates thread)
           d. Update contact: status='followup_N', followup_count+=1,
              last_contact_date=now
           e. If followup_count reaches max_followups with no reply,
              set status='completed'
        
        Returns:
            {
                "sent": int,
                "failed": int,
                "completed": int,  # Contacts who reached max followups
                "errors": list[str]
            }
        """
        pass
    
    def get_status_report(self) -> dict:
        """
        Generate summary of current sequence status.
        
        Returns:
            {
                "total_contacts": int,
                "by_status": {
                    "pending": int,
                    "sent": int,
                    "followup_1": int,
                    "followup_2": int,
                    "followup_3": int,
                    "replied": int,
                    "bounced": int,
                    "completed": int,
                    "opted_out": int
                },
                "reply_rate": float,  # replied / (total - pending - bounced - opted_out)
                "sequence_id": str,
                "last_activity": datetime
            }
        """
        pass
    
    def run_full_cycle(self) -> dict:
        """
        Execute complete cycle: check replies → send follow-ups.
        This is what Task Scheduler should call.
        
        Returns combined results from check_replies() and send_followups().
        """
        pass
```

---

## CLI Commands (main.py)

Use the `click` library for CLI. Implement these commands:

```bash
# Initialize new contacts file with sample row
python main.py init

# Send initial emails to all pending contacts
python main.py send [--dry-run]

# Check inbox for replies and update statuses
python main.py check

# Send follow-ups to non-responders
python main.py followup [--dry-run]

# Run full cycle (check + followup) - for scheduler
python main.py cycle

# Show current status report
python main.py status

# Add a new contact interactively or from args
python main.py add --email "john@company.com" --first-name "John" --last-name "Doe"

# Mark a contact as opted-out
python main.py optout --email "john@company.com"

# Reset a contact to pending (for re-running sequence)
python main.py reset --email "john@company.com"

# List all templates
python main.py templates
```

**CLI Output Formatting:**
- Use colors for status: green=success, yellow=warning, red=error
- Show progress during batch operations
- Always show summary at end

---

## Email Templates

**templates/initial.html:**
```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
  <p>Dear {title} {last_name},</p>
  
  <p>I hope this message finds you well.</p>
  
  <p>[Your initial message here]</p>
  
  <p>I would welcome the opportunity to discuss this further at your convenience.</p>
  
  <p>Best regards,<br>
  {sender_name}</p>
</body>
</html>
```

**templates/followup_1.html:**
```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
  <p>Dear {title} {last_name},</p>
  
  <p>I wanted to follow up on my previous email regarding [topic].</p>
  
  <p>[Follow-up message]</p>
  
  <p>Best regards,<br>
  {sender_name}</p>
</body>
</html>
```

Follow-up emails should use **the same subject line** as the initial email to maintain the conversation thread in Outlook.

---

## Error Handling

### Expected errors and responses:

| Error | Handling |
|-------|----------|
| Outlook not running | Raise clear error: "Please start Microsoft Outlook and try again" |
| Excel file locked | Wait 5 seconds, retry once, then fail with message |
| Invalid email address | Skip contact, log warning, continue with others |
| Template not found | Raise error with list of available templates |
| Network/send failure | Mark contact as 'bounced', log error, continue |
| Config file missing | Create default config.yaml with comments |

### Logging format:
```
2026-01-17 14:30:00 - INFO - Starting sequence: seq_20260117_143000
2026-01-17 14:30:01 - INFO - Sent initial email to: jean@company.com
2026-01-17 14:30:06 - WARNING - Failed to send to: invalid@bad (bounced)
2026-01-17 14:30:06 - INFO - Sequence complete: 5 sent, 1 failed
```

---

## Edge Cases to Handle

1. **Contact has no email** → Skip, log warning
2. **Duplicate email in file** → Process only first occurrence, log warning
3. **Template placeholder missing in contact** → Leave placeholder as-is, log warning
4. **Outlook security prompt** → Document in README how to suppress (registry or antivirus)
5. **Email sent but conversation_id not captured** → Use subject line for matching
6. **Reply from different email** (e.g., assistant) → Won't match, contact stays in sequence
7. **Contact replies then emails again** → Already marked 'replied', no action needed
8. **System clock issues** → Use UTC internally, convert for display

---

## Windows Task Scheduler Setup

To run automatically every 30 minutes:

```powershell
# Create scheduled task (run as admin)
$Action = New-ScheduledTaskAction -Execute "python" -Argument "C:\email-sequence\main.py cycle" -WorkingDirectory "C:\email-sequence"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd
Register-ScheduledTask -TaskName "EmailSequenceCycle" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Check replies and send follow-ups"
```

---

## Implementation Order for Claude Code

Build and test in this sequence:

1. **config.py** - Load YAML, provide defaults
2. **contact_tracker.py** - Excel CRUD operations  
3. **template_engine.py** - Load and render templates
4. **outlook_manager.py** - COM automation (test with dry_run)
5. **sequence_engine.py** - Orchestration logic
6. **main.py** - CLI commands
7. **Integration testing** - Full cycle with test contacts
8. **Documentation** - README with setup instructions

---

## Testing Checklist

Before going live:

- [ ] Can send single email (dry_run=true shows in Outlook)
- [ ] Can send single email (dry_run=false actually sends)
- [ ] Reply from contact is detected within 1 minute
- [ ] Contact status updates correctly in Excel
- [ ] Follow-up respects delay timing
- [ ] Same subject line creates thread in recipient's inbox
- [ ] Status report shows accurate counts
- [ ] Logging captures all actions
- [ ] Handles Outlook being closed gracefully
- [ ] Works after Windows restart

---

## Security Notes

- **No credentials stored** - Uses Outlook's existing authentication
- **Excel file contains PII** - Keep in secure location, consider encryption
- **Logs may contain emails** - Rotate/delete logs periodically
- **Rate limiting** - 5-second delay prevents being flagged as spam
