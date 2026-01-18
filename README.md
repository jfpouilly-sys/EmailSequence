# Email Sequence Automation System

A Python-based email sequence automation system for Windows 11 that sends personalized emails via Microsoft Outlook, tracks replies automatically, and manages follow-up sequences.

## Features

- **Automated Email Sequences**: Send initial emails and up to 4 follow-ups automatically (5 total emails)
- **Unique Email IDs**: Each email gets a unique tracking ID (Lxxxxxx-y format) appended to subject line
- **Multi-Campaign Management**: Manage multiple campaigns with isolated folders, contacts, and templates
- **Reply Tracking**: Scans Outlook inbox to detect replies and update contact status
- **Excel-Based Contact Management**: Simple contact database using Excel
- **Flexible Contact Status**: Add contacts with any status (pending, sent, followup_1-4, etc.)
- **Multiple Email Sending Options**:
  - Send emails immediately via Outlook
  - Save emails as .msg files in a designated folder for manual review/sending
  - Defer email sending by a specified number of hours using Outlook's deferred delivery
- **Template System**: Customizable HTML email templates with personalization
- **Dry Run Mode**: Test your sequences without actually sending emails
- **Task Scheduler Integration**: Run automated cycles to check replies and send follow-ups
- **Comprehensive Logging**: Detailed logs of all file operations, API calls, and email activities

## Requirements

- Windows 11 (or Windows 10)
- Microsoft Outlook (desktop application) installed and configured
- Python 3.8 or higher

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the system**:
   ```bash
   python main.py init
   ```

   This will create:
   - `contacts.xlsx` - Contact database with sample data
   - `templates/` - Email template directory (already populated)
   - `logs/` - Log file directory
   - `config.yaml` - Configuration file (already exists)

## Outlook Setup

The application connects to Microsoft Outlook using COM automation. **See [OUTLOOK_SETUP.md](OUTLOOK_SETUP.md) for detailed configuration instructions**, including:
- How to verify Outlook connection
- Which email account is used
- Where Outlook is configured in the code
- Complete list of API calls
- Troubleshooting connection issues

### Quick Outlook Checklist
- ✓ Outlook is installed and running
- ✓ At least one email account is configured in Outlook
- ✓ Default email account is set (File > Account Settings)
- ✓ `pywin32` is installed: `pip install pywin32`

**Testing the Connection:**
```python
from src.outlook_manager import OutlookManager
outlook = OutlookManager()  # Should connect without errors
```

See logs for connection details: `grep "\[OUTLOOK API\]" logs/sequence.log`

---

## Configuration

Edit `config.yaml` to customize your settings:

```yaml
# Email settings
sender_name: "Your Name"
default_subject: "Your Subject Line"

# Sequence timing (in days)
followup_delays:
  - 3    # Days after initial send for followup_1
  - 7    # Days after initial send for followup_2
  - 14   # Days after initial send for followup_3
  - 21   # Days after initial send for followup_4

max_followups: 4   # Now supports 4 follow-ups (5 total emails)

# Safety settings
send_delay_seconds: 5        # Pause between emails
dry_run: false               # Set to true for testing

# Email sending options
default_send_mode: "send"    # "send", "msg_file", or "defer"
msg_output_folder: "msg_files"  # Folder for .msg files
default_defer_hours: 1       # Hours to defer when using defer mode

# Campaign ID tracking
campaign_id_state_file: "campaign_id_state.json"  # Tracks unique email IDs
```

## Unique Email ID System

Each email sent by the system receives a unique tracking ID in the format **Lxxxxxx-y**:
- **L**: Literal prefix
- **xxxxxx**: 6-digit sequential number (000001 to 999999, supports 2 years of campaigns)
- **y**: Email sequence number (1=initial, 2=followup_1, 3=followup_2, 4=followup_3, 5=followup_4)

**Example IDs:**
- `L000123-1` - Initial email, 123rd email sent
- `L000124-2` - Follow-up 1, 124th email sent
- `L000125-5` - Follow-up 4, 125th email sent

The ID is automatically appended to the email subject line: `Your Subject [L000123-1]`

This allows for:
- Unique tracking of each email
- Easy identification of which email in the sequence
- Campaign analytics and monitoring
```

## Email Sending Options

The system supports three different modes for sending emails:

### 1. Send Immediately (default)
Emails are sent immediately via Outlook. This is the standard behavior.

```yaml
default_send_mode: "send"
```

### 2. Save as .msg File
Instead of sending, emails are saved as .msg files in the specified folder. This allows you to:
- Review emails before sending
- Manually send them from Outlook
- Archive drafts for compliance

```yaml
default_send_mode: "msg_file"
msg_output_folder: "msg_files"  # Folder where .msg files will be saved
```

The system will create one .msg file per email with the filename format: `YYYYMMDD_HHMMSS_recipient@email.com.msg`

### 3. Defer Sending
Emails are created with Outlook's deferred delivery feature, scheduling them to be sent after a specified number of hours. This is useful for:
- Sending emails during business hours even if you prepare them at night
- Spreading out email sends to avoid spam detection
- Time zone management

```yaml
default_send_mode: "defer"
default_defer_hours: 1  # Send 1 hour from now
```

**Note**: When using GUI, you can override the default send mode for individual contacts or operations.

## Usage

### 1. Add Contacts

Edit `contacts.xlsx` and add your contacts with the following required fields:
- `title` - Mr, Ms, Dr, etc.
- `first_name` - First name
- `last_name` - Last name
- `email` - Email address
- `company` - Company name

Set `status` to `pending` for contacts you want to include in the sequence.

Or add contacts via command line:
```bash
python main.py add --email "john@company.com" --first-name "John" --last-name "Doe" --company "Acme Corp" --status "pending"
```

**Status Options:**
You can add contacts with any status to control when they enter the sequence:
- `pending` (default) - Ready to receive initial email
- `sent` - Already sent initial email (will receive follow-ups if needed)
- `followup_1`, `followup_2`, `followup_3` - Already in follow-up sequence
- `replied` - Contact has replied (will not receive further emails)
- `opted_out` - Contact has opted out (will not receive further emails)

### 2. Customize Email Templates

Edit templates in the `templates/` folder:
- `initial.html` - First email
- `followup_1.html` - First follow-up (sent after 3 days)
- `followup_2.html` - Second follow-up (sent after 7 days)
- `followup_3.html` - Third follow-up (sent after 14 days)

**Available placeholders**:
- `{title}` - Mr, Ms, Dr, etc.
- `{first_name}` - Contact's first name
- `{last_name}` - Contact's last name
- `{full_name}` - Full name (first + last)
- `{email}` - Contact's email
- `{company}` - Company name
- `{sender_name}` - Your name from config

### 3. Test Your Sequence (Dry Run)

```bash
python main.py send --dry-run
```

This will open emails in Outlook without sending them. Review each email before going live.

### 4. Send Initial Emails

```bash
python main.py send
```

This sends the initial email to all contacts with `status=pending`.

### 5. Check for Replies

```bash
python main.py check
```

Scans your Outlook inbox for replies and updates contact statuses.

### 6. Send Follow-ups

```bash
python main.py followup
```

Sends follow-up emails to contacts who haven't replied, based on the timing in `config.yaml`.

### 7. Run Full Cycle

```bash
python main.py cycle
```

Combines steps 5 and 6: checks for replies, then sends follow-ups. **Use this for scheduled tasks.**

### 8. View Status

```bash
python main.py status
```

Shows a summary of your sequence:
- Total contacts
- Breakdown by status
- Reply rate
- Last activity

## CLI Commands Reference

| Command | Description |
|---------|-------------|
| `python main.py init` | Initialize system (create files and folders) |
| `python main.py send [--dry-run]` | Send initial emails to pending contacts |
| `python main.py check` | Check inbox for replies |
| `python main.py followup [--dry-run]` | Send follow-ups to non-responders |
| `python main.py cycle` | Run full cycle (check + followup) |
| `python main.py status` | Show status report |
| `python main.py add` | Add a new contact |
| `python main.py optout --email <email>` | Mark contact as opted-out |
| `python main.py reset --email <email>` | Reset contact to pending |
| `python main.py templates` | List available templates |

## Contact Status Values

- `pending` - Not yet contacted
- `sent` - Initial email sent, awaiting reply
- `followup_1` - First follow-up sent
- `followup_2` - Second follow-up sent
- `followup_3` - Third follow-up sent
- `replied` - Contact replied (sequence complete)
- `bounced` - Email failed to send
- `opted_out` - Contact requested removal
- `completed` - Max follow-ups reached, no reply

## Automation with Windows Task Scheduler

To run the cycle automatically every 30 minutes:

### Option 1: PowerShell Script

1. Create a PowerShell script (e.g., `run_cycle.ps1`):
   ```powershell
   cd "C:\path\to\EmailSequence"
   python main.py cycle
   ```

2. Create scheduled task:
   ```powershell
   $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\path\to\EmailSequence\run_cycle.ps1" -WorkingDirectory "C:\path\to\EmailSequence"
   $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)
   $Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd
   Register-ScheduledTask -TaskName "EmailSequenceCycle" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Check replies and send follow-ups"
   ```

### Option 2: Using Task Scheduler GUI

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Email Sequence Cycle"
4. Trigger: Daily, repeat every 30 minutes
5. Action: Start a program
   - Program: `python`
   - Arguments: `main.py cycle`
   - Start in: `C:\path\to\EmailSequence`

## Troubleshooting

### Outlook Security Prompt

If you see a security prompt when sending emails:

1. **Allow access**: Click "Allow" and "Allow access for 10 minutes"
2. **Disable prompt** (if using your own computer):
   - Add this registry key (requires admin):
     ```
     [HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Security]
     "PromptOOMSend"=dword:00000000
     ```

### Excel File Locked

If you get "file is locked" errors:
- Close `contacts.xlsx` in Excel before running commands
- The system will retry once automatically after 5 seconds

### No Replies Detected

- Check that `inbox_scan_days` in config.yaml is long enough
- Verify the contact is replying to the same email thread
- Check Outlook inbox manually to confirm the reply exists

### Import Errors

If you get import errors when running Python:
```bash
pip install --upgrade -r requirements.txt
```

## Best Practices

1. **Start with dry run**: Always test with `--dry-run` first
2. **Small batches**: Start with 5-10 contacts to test the flow
3. **Personalize templates**: Generic emails get lower response rates
4. **Respect opt-outs**: Always honor unsubscribe requests
5. **Monitor logs**: Check `logs/sequence.log` regularly
6. **Backup contacts**: Keep a backup of `contacts.xlsx`
7. **Professional tone**: Keep emails professional and respectful

## Logging

The application provides **comprehensive logging** of all operations. All activity is logged to `logs/sequence.log`.

### What is Logged

The system logs all major operations with detailed prefixes:

| Prefix | What It Logs |
|--------|--------------|
| `[OUTLOOK API]` | All Outlook COM API calls (connection, sending, inbox scanning) |
| `[FILE READ]` | File read operations with absolute paths and file sizes |
| `[FILE WRITE]` | File write operations with absolute paths and bytes written |
| `[FILE CREATE]` | New file creation operations |
| `[QUERY]` | Database queries (contact lookups, filters) |
| `[UPDATE]` | Contact record updates |
| `[ADD]` | New contact additions |
| `[RENDER]` | Email template rendering operations |
| `[TEMPLATES]` | Template engine initialization and discovery |

### Example Log Output

```
2026-01-18 10:30:15 - INFO - [OUTLOOK API] Successfully connected to Outlook version 16.0
2026-01-18 10:30:20 - INFO - [FILE READ] Loaded 25 contacts from C:\email-sequence\contacts.xlsx
2026-01-18 10:30:30 - INFO - [TEMPLATES] Found 4 templates: followup_1, followup_2, followup_3, initial
2026-01-18 10:30:40 - INFO - [OUTLOOK API] Email sent successfully to john@company.com
2026-01-18 10:30:45 - INFO - [FILE WRITE] Successfully saved to C:\email-sequence\contacts.xlsx (12345 bytes)
```

### Viewing Logs

**Real-time monitoring (PowerShell):**
```powershell
Get-Content -Path "logs\sequence.log" -Wait -Tail 50
```

**Filter by operation type:**
```bash
# Show only Outlook API calls
grep "\[OUTLOOK API\]" logs/sequence.log

# Show only file operations
grep "\[FILE" logs/sequence.log

# Show errors
grep "ERROR" logs/sequence.log
```

### Files Read/Written

The logs show **exact paths** for all file operations:
- **Read:** `contacts.xlsx`, `templates/*.html`, configuration files
- **Written:** `contacts.xlsx`, `logs/sequence.log`, `.msg` files in `msg_files/`

All paths are logged as **absolute paths** for easy verification.

## Data Privacy

- No credentials are stored (uses Outlook's existing authentication)
- `contacts.xlsx` contains personal information - keep it secure
- Consider encrypting the Excel file if it contains sensitive data
- Rotate/delete logs periodically

## Support

For issues or questions:
1. Check the logs in `logs/sequence.log`
2. Run commands with `-v` flag for verbose output
3. Ensure Outlook is running and configured properly

## License

This is a custom tool built for internal use. Modify as needed for your requirements.

## Version

Current Version: 1.0.0
