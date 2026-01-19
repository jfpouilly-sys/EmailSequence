# Quick Start Guide - Campaign System

Complete guide to using the new campaign-based architecture in Email Sequence Manager.

## What Are Campaigns?

**Campaigns** are isolated email sequences with their own:
- **Contacts** - Separate contact lists per campaign
- **Templates** - Custom email templates per campaign
- **Configuration** - Independent settings per campaign
- **Centralized Logs** - All campaigns log to one place

## Directory Structure

```
EmailSequence/
├── campaigns/                      # All your campaigns
│   ├── my_campaign_2024/
│   │   ├── contacts.xlsx          # 3 sample contacts created automatically
│   │   ├── templates/             # Email templates
│   │   │   ├── initial.html
│   │   │   ├── followup_1.html
│   │   │   ├── followup_2.html
│   │   │   └── followup_3.html
│   │   └── campaign_config.yaml   # Campaign settings
│   └── another_campaign/
│       └── ...
├── logs/                          # Centralized logs (all campaigns)
│   └── sequence.log
└── gui_config.yaml               # GUI configuration
```

## Getting Started

### Method 1: Using the GUI (Recommended)

1. **Launch the Application:**
   ```bash
   python run_gui.py
   ```

2. **Campaign Dialog Appears:**
   - If no campaign is selected, the dialog opens automatically
   - You'll see a list of existing campaigns (if any)

3. **Create Your First Campaign:**
   - Enter a campaign name (e.g., "my_first_campaign")
   - Click "Create"
   - **3 sample contacts are automatically created!**

4. **Start Working:**
   - The campaign is now active
   - Sidebar shows: "📁 my_first_campaign"
   - Go to Contacts tab to see your 3 sample contacts

5. **View Sample Contacts:**
   - John Doe - john.doe@example.com - Example Corp
   - Jane Smith - jane.smith@company.com - Company Inc
   - Robert Johnson - r.johnson@firm.com - Firm LLC
   - All with status: "pending"

6. **Edit Templates:**
   - Go to Templates tab
   - 4 templates already created and ready to edit

7. **Switch Campaigns:**
   - Click "📁 Change Campaign" in sidebar
   - Select different campaign or create new one

### Method 2: Using the Demo Script

1. **Run the Demo:**
   ```bash
   python demo_campaigns.py
   ```

2. **See the Output:**
   - Creates 2 example campaigns
   - Shows directory structure
   - Displays sample contacts
   - Lists all created files

3. **Explore the Created Files:**
   ```bash
   # View campaigns
   ls -la campaigns/

   # View sample contacts
   # (requires pandas and openpyxl)
   python -c "import pandas as pd; print(pd.read_excel('campaigns/my_first_campaign/contacts.xlsx'))"

   # View templates
   ls -la campaigns/my_first_campaign/templates/
   ```

## Campaign Workflow

### Creating a New Campaign

**In GUI:**
1. Click "📁 Change Campaign" button
2. Enter campaign name (letters, numbers, hyphens, underscores)
3. Click "+ Create"
4. Success! 3 sample contacts added automatically

**Naming Rules:**
- ✓ Valid: `my_campaign`, `Q1-2024`, `partners_outreach`
- ✗ Invalid: `my campaign` (spaces), `my@campaign` (special chars)

### Working with a Campaign

Once a campaign is active:

1. **Contacts Tab:**
   - View the 3 automatically created sample contacts
   - Import more contacts from CSV
   - Add contacts manually
   - All saved to: `campaigns/your_campaign/contacts.xlsx`

2. **Templates Tab:**
   - Edit 4 pre-created templates
   - Customize with placeholders
   - Preview with sample contact data
   - Saved to: `campaigns/your_campaign/templates/`

3. **Sequence Tab:**
   - Configure follow-up timing
   - Set scheduling
   - All settings saved to: `campaigns/your_campaign/campaign_config.yaml`

4. **Dashboard Tab:**
   - View metrics for current campaign only
   - See activity from all campaigns (centralized logs)

5. **Logs Tab:**
   - View logs from ALL campaigns
   - Centralized in: `logs/sequence.log`

### Switching Between Campaigns

**Option 1: Sidebar Button**
1. Click "📁 Change Campaign"
2. Select campaign from list
3. Click "Select Campaign"

**Option 2: Automatic on Startup**
- If no campaign selected, dialog appears automatically

### Deleting a Campaign

**In GUI:**
1. Click "📁 Change Campaign"
2. Select campaign to delete
3. Click "Delete" button (red)
4. Confirm deletion
5. **Warning:** This permanently deletes all contacts, templates, and configuration!

## Sample Contacts Explained

Every new campaign comes with 3 ready-to-use sample contacts:

| Name | Email | Company | Status |
|------|-------|---------|--------|
| John Doe | john.doe@example.com | Example Corp | pending |
| Jane Smith | jane.smith@company.com | Company Inc | pending |
| Robert Johnson | r.johnson@firm.com | Firm LLC | pending |

**Why Sample Contacts?**
- Test the system immediately
- See how templates render with real data
- Practice before importing your actual contacts
- Learn the workflow without risk

**Using Sample Contacts:**
1. Go to Contacts tab
2. Click on a contact to edit
3. Replace with your actual contact data
4. Or keep them for testing!

## Pre-Created Templates

Each campaign includes 4 email templates:

### initial.html
Subject: Partnership Opportunity

First outreach email introducing yourself and your opportunity.

### followup_1.html
Subject: RE: Partnership Opportunity

First follow-up after 3 days (configurable).

### followup_2.html
Subject: RE: Partnership Opportunity - Final Follow-up

Second follow-up after 7 days (configurable).

### followup_3.html
Subject: Closing the Loop

Final follow-up after 14 days (configurable).

**All templates support placeholders:**
- `{title}` - Mr, Ms, Dr, etc.
- `{first_name}` - Contact's first name
- `{last_name}` - Contact's last name
- `{email}` - Contact's email
- `{company}` - Contact's company
- `{sender_name}` - Your name

## Best Practices

### Campaign Naming

```bash
# Good examples
my_campaign_2024
Q1_partners_outreach
tech_companies
startup_founders

# Avoid
My Campaign (spaces)
campaign@2024 (special characters)
```

### Organizing Campaigns

**By Time Period:**
- `january_2024`
- `Q1_2024`
- `spring_outreach`

**By Industry:**
- `tech_companies`
- `healthcare_orgs`
- `finance_sector`

**By Goal:**
- `partnership_outreach`
- `sales_leads`
- `event_invitations`

### Campaign Lifecycle

1. **Create:** New campaign with samples
2. **Setup:** Import contacts, customize templates
3. **Test:** Send to sample contacts first
4. **Launch:** Start sequence with real contacts
5. **Monitor:** Track replies and adjust
6. **Archive:** When complete, create new campaign for next round

## Centralized Logging

**All campaigns log to one place:**
```
logs/sequence.log
```

**Benefits:**
- Monitor all campaigns from one file
- Easy to search across campaigns
- Simplified debugging
- Consistent log format

**Viewing Logs:**
- GUI: Logs tab shows all campaign activity
- Command line: `tail -f logs/sequence.log`

## FAQ

### Q: Can I have multiple campaigns active at once?
**A:** You can only work on one campaign at a time in the GUI, but all campaigns exist independently. Switch between them using the "Change Campaign" button.

### Q: What happens to my contacts when I switch campaigns?
**A:** Nothing! Each campaign's contacts are completely separate and stay in their campaign folder.

### Q: Can I copy contacts between campaigns?
**A:** Yes! Use the Export button in one campaign, then Import in another campaign.

### Q: Do I need to create sample contacts?
**A:** No, when creating a campaign, you can choose not to create samples (though the GUI always creates them). Or just delete them after creation.

### Q: Where are logs stored?
**A:** All campaign logs go to the centralized `logs/` folder in the main project directory, not in campaign folders.

### Q: Can I rename a campaign?
**A:** Not directly through the GUI yet. You would need to rename the folder in `campaigns/` and update the name in `campaign_config.yaml`.

### Q: How do I backup a campaign?
**A:** Copy the entire campaign folder:
```bash
cp -r campaigns/my_campaign campaigns/my_campaign_backup
```

### Q: Can I share a campaign with someone?
**A:** Yes! Zip the campaign folder and send it. They can extract it to their `campaigns/` folder.

## Troubleshooting

### Campaign dialog doesn't appear
- Check `gui_config.yaml`
- Set `show_campaign_on_startup: true`
- Or click "Change Campaign" button in sidebar

### Can't see my contacts
- Ensure a campaign is selected (check sidebar)
- Verify `campaigns/your_campaign/contacts.xlsx` exists
- Check Contacts tab is loaded

### Templates not loading
- Ensure campaign has `templates/` folder
- Check that `.html` files exist
- Verify campaign is selected

### Logs not showing
- Check `logs/` folder exists in project root
- Verify `sequence.log` file exists
- Check Logs tab filters (All Levels, All dates)

## Next Steps

1. **Create your first campaign** using the GUI
2. **Review the 3 sample contacts** in Contacts tab
3. **Customize the templates** with your messaging
4. **Import your real contacts** or replace the samples
5. **Start your sequence!**

---

## Version Information

- Campaign System: 1.0.0-20260119
- Last Updated: 2026-01-19
- Compatible with: Email Sequence Manager 1.0.0-20260119
