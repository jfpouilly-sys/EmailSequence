# Templates Library

This folder contains shared email templates that can be used across multiple campaigns.

## Purpose

The templates library provides a centralized location for:
- Reusable email templates
- Standard templates that can be copied to new campaigns
- Template sharing between campaigns

## Usage

### Adding Templates to Library

1. **Via GUI**: Use the "Campaigns" tab → "Templates Library" section → "Add Template" button
2. **Manually**: Copy HTML template files directly into this folder

### Using Library Templates

1. Navigate to the "Campaigns" tab in the GUI
2. Click "Browse Library" to view all available templates
3. Templates can be copied to specific campaigns using the Campaign Manager

### Template Format

Templates should be HTML files (.html) with placeholders for dynamic content:

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
  <p>Dear {title} {last_name},</p>

  <p>Your email content here...</p>

  <p>Best regards,<br>
  {sender_name}</p>
</body>
</html>
```

### Available Placeholders

- `{title}` - Contact title (Mr., Mrs., Dr., etc.)
- `{first_name}` - Contact first name
- `{last_name}` - Contact last name
- `{email}` - Contact email address
- `{company}` - Contact company name
- `{sender_name}` - Sender name from campaign config

## Best Practices

1. **File Naming**: Use descriptive names like `initial_partnership.html`, `followup_reminder.html`
2. **Consistency**: Maintain consistent styling across templates
3. **Testing**: Test templates with sample data before using in campaigns
4. **Version Control**: Keep original versions of important templates
5. **Organization**: Consider creating subfolders for different template categories

## Example Templates

You can create templates for common scenarios:
- Initial outreach (`initial_*.html`)
- Follow-ups (`followup_*.html`)
- Thank you messages (`thankyou_*.html`)
- Event invitations (`event_*.html`)
- Product announcements (`announcement_*.html`)
