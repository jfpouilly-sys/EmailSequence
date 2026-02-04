# Lead Generator Standalone

Single-user desktop application for email marketing campaigns with Microsoft Outlook integration.

## Features

- **Campaign Management**: Create and manage email marketing campaigns with multi-step sequences
- **Contact Lists**: Organize contacts into lists with 10 customizable fields
- **CSV Import/Export**: Import contacts from CSV with auto-field mapping
- **Email Templates**: Create email templates with merge tags ({{FirstName}}, {{Company}}, etc.)
- **Outlook Integration**: Send emails directly through Microsoft Outlook (Classic)
- **Reply Detection**: Automatically detect and track email replies
- **Unsubscribe Detection**: Detect unsubscribe requests (English + French keywords)
- **Suppression List**: Manage global suppression/unsubscribe list
- **Basic Reports**: View campaign statistics and email logs
- **Migration**: Export data for migration to multi-user version

## Requirements

- Windows 10/11
- Python 3.10+
- Microsoft Outlook (Classic version, not New Outlook)

## Installation

### From Source

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Build Executable

1. Install dependencies (including PyInstaller)
2. Run the build script:
   ```bash
   scripts\build.bat
   ```
3. The executable will be in `dist\LeadGeneratorStandalone.exe`

### Install to System

After building:
1. Run `scripts\install.bat` as Administrator
2. The application will be installed to `C:\LeadGenerator`
3. A desktop shortcut will be created

## Quick Start

1. **First Launch**: The application creates the database automatically on first run
2. **Configure Mail**: Go to Settings → Mail Account → Enter your Outlook email address
3. **Import Contacts**:
   - Go to Contacts → New List → Enter a name
   - Click Import CSV → Select your file
   - Map columns to fields and import
4. **Create Campaign**:
   - Go to Campaigns → New Campaign
   - Enter name and select contact list
   - Add email steps in the Sequence tab
5. **Activate Campaign**:
   - Click Activate on the campaign
   - Start the Worker from the Dashboard
6. **Monitor**: View progress on the Dashboard

## Merge Tags

Use these tags in your email templates:

| Tag | Description |
|-----|-------------|
| `{{Title}}` | Contact's title (Mr., Ms., etc.) |
| `{{FirstName}}` | First name |
| `{{LastName}}` | Last name |
| `{{FullName}}` | Full name |
| `{{Email}}` | Email address |
| `{{Company}}` | Company name |
| `{{Position}}` | Job title/position |
| `{{Phone}}` | Phone number |
| `{{Custom1}}` - `{{Custom10}}` | Custom fields |
| `{{CampaignRef}}` | Campaign reference (ISIT-YYNNNN) |
| `{{UnsubscribeText}}` | Unsubscribe instruction text |

## Configuration

Edit `config.yaml` to customize:

- Sending window (business hours)
- Daily/hourly email limits
- Outlook scan interval
- Unsubscribe keywords

## Data Location

- Database: `data/leadgen.db` (SQLite)
- Attachments: `data/files/`
- Logs: `data/app.log`

## Migration to Multi-User Version

To migrate your data to the multi-user version:

1. Go to Settings → About → Export Data for Migration
2. Select campaigns to export (or all)
3. Save the JSON file
4. Run the import script on the server:
   ```bash
   python postgresql_importer.py \
     --json-file export.json \
     --db-host localhost \
     --db-name leadgenerator \
     --db-user your_user \
     --db-password your_password \
     --target-user-id "uuid-of-target-user"
   ```

## Troubleshooting

### Outlook Not Detected
- Ensure Microsoft Outlook (Classic) is installed and running
- The "New Outlook" is not supported - use the classic version
- Try restarting Outlook before launching Lead Generator

### Emails Not Sending
- Check that a campaign is Active and the Worker is Running
- Verify the sending window times match your current time
- Check the email queue in the database for errors

### Import Issues
- Ensure your CSV uses UTF-8 encoding
- Required fields: email, first_name, last_name, company
- Check for duplicate email addresses

## License

Proprietary - Internal use only.

## Support

For issues or feature requests, contact your IT administrator.
