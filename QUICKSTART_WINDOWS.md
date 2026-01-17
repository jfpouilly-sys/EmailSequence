# Email Sequence Quick Start Guide - Windows 11

Get up and running with Email Sequence Automation in 15 minutes.

---

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Windows 11 or Windows 10
- [ ] Microsoft Outlook installed and configured
- [ ] Internet connection
- [ ] Administrator access (for installation)

---

## 5-Minute Installation

### Step 1: Install Python (5 minutes)

1. Go to https://www.python.org/downloads/
2. Download **Python 3.12** (Windows 64-bit installer)
3. Run installer
4. **☑️ IMPORTANT:** Check "Add Python to PATH"
5. Click "Install Now"
6. Wait for completion
7. Click "Close"

**Verify:**
Open Command Prompt (Win+R → `cmd` → Enter):
```cmd
python --version
```
Should show: `Python 3.12.x`

---

### Step 2: Download Application (1 minute)

1. Download the Email Sequence ZIP file
2. Extract to `C:\EmailSequence`
3. You should see these files:
   - `main.py`
   - `gui_main.py`
   - `gui_config.py`
   - `config.yaml`
   - `requirements.txt`
   - `install_windows.bat`

---

### Step 3: Run Installer (3 minutes)

1. Navigate to `C:\EmailSequence`
2. Right-click **install_windows.bat**
3. Select **"Run as Administrator"**
4. Wait for installation to complete
5. Press any key when prompted

The installer will:
- Install Python packages
- Initialize the system
- Create desktop shortcuts
- Launch the application

---

## 5-Minute Configuration

### Step 1: Edit Configuration (2 minutes)

Double-click **"Email Sequence Config"** on desktop

Or manually edit `C:\EmailSequence\config.yaml`:

```yaml
sender_name: "Your Name Here"          # ← Change this
default_subject: "Your Subject Line"   # ← Change this
```

Click **"Save Configuration"**

---

### Step 2: Add Contacts (2 minutes)

**Option A: Use GUI**
1. Double-click **"Email Sequence"** on desktop
2. Click **"Add Contact"** button
3. Fill in the form
4. Click **"Add Contact"**

**Option B: Edit Excel**
1. Open `C:\EmailSequence\contacts.xlsx`
2. Add rows with:
   - `first_name`, `last_name`, `email`, `company`
   - Set `status` to `pending`
3. Save and close

---

### Step 3: Customize Email Template (1 minute)

1. Open `C:\EmailSequence\templates\initial.html` in Notepad
2. Replace the placeholder text with your message
3. Use these variables:
   - `{title}` - Mr, Ms, Dr
   - `{first_name}` - First name
   - `{last_name}` - Last name
   - `{company}` - Company name
   - `{sender_name}` - Your name

**Example:**
```html
<p>Dear {title} {last_name},</p>
<p>I hope this email finds you well at {company}.</p>
<p>Best regards,<br>{sender_name}</p>
```

4. Save the file

---

## 5-Minute First Run

### Step 1: Test with Dry Run (2 minutes)

1. Open **Email Sequence** (desktop shortcut)
2. In configuration editor, ensure **"Dry Run"** is checked
3. Click **"Send Initial"**
4. Emails will open in Outlook (not sent)
5. Review each email
6. Close Outlook windows

---

### Step 2: Send Real Emails (1 minute)

1. Open **Email Sequence Config**
2. **Uncheck "Dry Run"**
3. Click **"Save Configuration"**
4. Go back to **Email Sequence**
5. Click **File → Reload**
6. Click **"Send Initial"**
7. Click **"Yes"** to confirm

Emails are sent! 🚀

---

### Step 3: Monitor and Automate (2 minutes)

**Check for Replies:**
- Click **"Check Replies"** button
- Any replies are detected automatically

**Send Follow-ups:**
- Click **"Send Follow-ups"** button
- Only non-responders receive follow-ups

**View Status:**
- Click **"Refresh Status"**
- See how many sent, replied, pending, etc.

---

## Command Line Quick Reference

If you prefer CLI over GUI:

```cmd
# Navigate to folder
cd C:\EmailSequence

# Initialize system
python main.py init

# Send initial emails (dry run)
python main.py send --dry-run

# Send initial emails (real)
python main.py send

# Check for replies
python main.py check

# Send follow-ups
python main.py followup

# Run full cycle (check + followup)
python main.py cycle

# View status report
python main.py status

# Add a contact
python main.py add --email "john@company.com" --first-name "John" --last-name "Doe" --company "Acme"

# List templates
python main.py templates
```

---

## Automation Setup (Optional - 5 minutes)

### Create Scheduled Task

Run this in **PowerShell as Administrator**:

```powershell
# Create scheduled task to run every 30 minutes
$Action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "main.py cycle" `
    -WorkingDirectory "C:\EmailSequence"

$Trigger = New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd

Register-ScheduledTask `
    -TaskName "EmailSequenceCycle" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings
```

Now the system will automatically:
- Check for replies every 30 minutes
- Send follow-ups when due
- Update contact statuses

---

## Troubleshooting

### "Python not found"
**Solution:** Reinstall Python, check "Add Python to PATH"

### "Could not connect to Outlook"
**Solution:** Open Outlook first, then run the application

### "File is locked"
**Solution:** Close `contacts.xlsx` in Excel

### "Template not found"
**Solution:** Check that `templates/initial.html` exists

### Outlook asks for permission every time
**Solution:** Click "Allow" and "Allow for 10 minutes", or see INSTALL_WINDOWS.md for permanent fix

---

## Workflow Summary

```
┌─────────────────────────────────────────┐
│ 1. Add contacts (status='pending')     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. Send initial emails                  │
│    → Status changes to 'sent'           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 3. System checks inbox for replies     │
│    → If replied: status='replied'       │
│    → If not: wait for follow-up time    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 4. After 3 days: Send followup_1       │
│    → Status changes to 'followup_1'     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 5. After 7 days: Send followup_2       │
│    → Status changes to 'followup_2'     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 6. After 14 days: Send followup_3      │
│    → Status changes to 'completed'      │
└─────────────────────────────────────────┘
```

---

## Tips for Success

### Before Going Live
1. ✓ Test with dry run mode
2. ✓ Use your own email as a test contact
3. ✓ Verify templates look professional
4. ✓ Check subject line doesn't look like spam
5. ✓ Start with 5-10 contacts, not 50

### Best Practices
1. **Personalize templates** - Generic emails get ignored
2. **Keep it professional** - No marketing speak
3. **Respect replies** - System stops automatically
4. **Monitor logs** - Check `logs/sequence.log` regularly
5. **Backup contacts** - Copy `contacts.xlsx` weekly

### Timing Strategy
- **Initial email:** Morning (9-11 AM) on Tuesday-Thursday
- **Follow-up delays:** 3, 7, 14 days is balanced
- **Avoid weekends:** Check Outlook before Monday
- **Respect time zones:** Consider your audience location

### Email Content
- **Subject line:** Clear, professional, not clickbait
- **Opening:** Address by name, reference context
- **Body:** Brief (3-4 paragraphs), specific value proposition
- **Close:** Clear call-to-action, easy to reply
- **Signature:** Professional, include contact info

---

## Next Steps

1. **Read full documentation:** `README.md`
2. **Installation details:** `INSTALL_WINDOWS.md`
3. **Package information:** `PACKAGES.md`
4. **Technical spec:** `emailSequenceClaudeCode.md`

---

## Support

### Check Logs
```cmd
notepad C:\EmailSequence\logs\sequence.log
```

### Get Status
```cmd
cd C:\EmailSequence
python main.py status
```

### Common Issues
- **Outlook not running:** Open Outlook before running
- **Wrong account:** Set correct account as default in Outlook
- **Emails not sending:** Check internet connection
- **No replies detected:** Increase `inbox_scan_days` in config

---

## Uninstall

To remove the application:

```powershell
# Remove folder
Remove-Item -Path "C:\EmailSequence" -Recurse -Force

# Remove scheduled task
Unregister-ScheduledTask -TaskName "EmailSequenceCycle" -Confirm:$false

# Remove desktop shortcuts
Remove-Item -Path "$env:USERPROFILE\Desktop\Email Sequence*.lnk"
```

---

**You're all set! Start automating your email sequences now.**

For questions or issues, check `INSTALL_WINDOWS.md` for detailed troubleshooting.

---

**Version:** 1.0.0
**Platform:** Windows 11 / Windows 10
**Estimated Setup Time:** 15 minutes
