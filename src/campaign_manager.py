"""Campaign management for multiple email sequences.

Manages multiple campaigns with isolated folders, contacts, and templates.
"""
import os
import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime


class Campaign:
    """Represents a single email campaign."""

    def __init__(self, name: str, folder_path: str):
        """
        Initialize campaign.

        Args:
            name: Campaign name
            folder_path: Path to campaign folder
        """
        self.name = name
        self.folder_path = Path(folder_path)
        self.contacts_file = self.folder_path / "contacts.xlsx"
        self.templates_folder = self.folder_path / "templates"
        self.config_file = self.folder_path / "campaign_config.yaml"
        self.logs_folder = self.folder_path / "logs"

    def exists(self) -> bool:
        """Check if campaign folder exists."""
        return self.folder_path.exists()

    def get_config_path(self) -> Path:
        """Get path to campaign config file."""
        return self.config_file

    def get_contacts_path(self) -> Path:
        """Get path to contacts file."""
        return self.contacts_file

    def get_templates_path(self) -> Path:
        """Get path to templates folder."""
        return self.templates_folder

    def get_logs_path(self) -> Path:
        """Get path to logs folder."""
        return self.logs_folder

    def to_dict(self) -> Dict:
        """Convert campaign to dictionary."""
        return {
            'name': self.name,
            'folder_path': str(self.folder_path),
            'created': self.folder_path.stat().st_ctime if self.exists() else None,
            'contacts_count': self._get_contacts_count()
        }

    def _get_contacts_count(self) -> int:
        """Get number of contacts in campaign."""
        try:
            if self.contacts_file.exists():
                import pandas as pd
                df = pd.read_excel(self.contacts_file)
                return len(df)
        except:
            pass
        return 0


class CampaignManager:
    """Manage multiple email campaigns."""

    def __init__(self, campaigns_root: str = "campaigns"):
        """
        Initialize campaign manager.

        Args:
            campaigns_root: Root folder for all campaigns
        """
        self.campaigns_root = Path(campaigns_root)
        self.logger = logging.getLogger(__name__)
        self.state_file = self.campaigns_root / "campaigns_state.json"

        # Create campaigns root if it doesn't exist
        self.campaigns_root.mkdir(exist_ok=True)
        self.logger.info(f"[CAMPAIGNS] Campaigns root: {self.campaigns_root.absolute()}")

    def list_campaigns(self) -> List[Campaign]:
        """
        List all campaigns.

        Returns:
            List of Campaign objects
        """
        campaigns = []

        if not self.campaigns_root.exists():
            return campaigns

        for folder in self.campaigns_root.iterdir():
            if folder.is_dir():
                campaign = Campaign(folder.name, str(folder))
                campaigns.append(campaign)
                self.logger.debug(f"[CAMPAIGNS] Found campaign: {campaign.name}")

        self.logger.info(f"[CAMPAIGNS] Found {len(campaigns)} campaigns")
        return sorted(campaigns, key=lambda c: c.name)

    def get_campaign(self, name: str) -> Optional[Campaign]:
        """
        Get campaign by name.

        Args:
            name: Campaign name

        Returns:
            Campaign object or None if not found
        """
        folder_path = self.campaigns_root / name
        if folder_path.exists():
            return Campaign(name, str(folder_path))
        return None

    def create_campaign(
        self,
        name: str,
        sender_name: str = "",
        subject: str = "",
        copy_from: Optional[str] = None
    ) -> Campaign:
        """
        Create a new campaign.

        Args:
            name: Campaign name (will be used as folder name)
            sender_name: Sender name for config
            subject: Default subject for config
            copy_from: Optional campaign name to copy templates from

        Returns:
            Created Campaign object

        Raises:
            ValueError: If campaign already exists or name is invalid
        """
        # Validate name
        if not name or name.strip() == "":
            raise ValueError("Campaign name cannot be empty")

        # Sanitize name for folder
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')

        campaign_folder = self.campaigns_root / safe_name

        if campaign_folder.exists():
            raise ValueError(f"Campaign '{name}' already exists")

        self.logger.info(f"[CAMPAIGNS] Creating campaign: {name} at {campaign_folder.absolute()}")

        # Create folder structure
        campaign_folder.mkdir(parents=True)
        (campaign_folder / "templates").mkdir()
        (campaign_folder / "logs").mkdir()

        self.logger.info(f"[FILE CREATE] Created campaign folders: {campaign_folder.absolute()}")

        # Create empty contacts file
        import pandas as pd
        from src.contact_tracker import ContactTracker

        contacts_file = campaign_folder / "contacts.xlsx"
        df = pd.DataFrame(columns=ContactTracker.REQUIRED_COLUMNS)
        df.to_excel(contacts_file, index=False)
        self.logger.info(f"[FILE CREATE] Created contacts file: {contacts_file.absolute()}")

        # Create campaign config
        config_content = self._generate_campaign_config(name, sender_name, subject)
        config_file = campaign_folder / "campaign_config.yaml"
        with open(config_file, 'w') as f:
            f.write(config_content)
        self.logger.info(f"[FILE CREATE] Created config file: {config_file.absolute()}")

        # Copy templates if specified
        if copy_from:
            source_campaign = self.get_campaign(copy_from)
            if source_campaign and source_campaign.get_templates_path().exists():
                self._copy_templates(
                    source_campaign.get_templates_path(),
                    campaign_folder / "templates"
                )
        else:
            # Create default templates
            self._create_default_templates(campaign_folder / "templates")

        campaign = Campaign(safe_name, str(campaign_folder))
        self.logger.info(f"[CAMPAIGNS] Successfully created campaign: {name}")
        return campaign

    def delete_campaign(self, name: str) -> bool:
        """
        Delete a campaign.

        Args:
            name: Campaign name

        Returns:
            True if deleted, False if not found
        """
        campaign = self.get_campaign(name)
        if not campaign or not campaign.exists():
            return False

        self.logger.warning(f"[CAMPAIGNS] Deleting campaign: {name} at {campaign.folder_path.absolute()}")
        shutil.rmtree(campaign.folder_path)
        self.logger.info(f"[CAMPAIGNS] Deleted campaign: {name}")
        return True

    def _generate_campaign_config(self, name: str, sender_name: str, subject: str) -> str:
        """Generate campaign config YAML content."""
        return f"""# Campaign Configuration: {name}

# Paths (relative to campaign folder)
contacts_file: "contacts.xlsx"
templates_folder: "templates"
log_file: "logs/sequence.log"

# Email settings
sender_name: "{sender_name or 'Your Name'}"
default_subject: "{subject or 'Email Subject'}"

# Sequence timing (in days)
followup_delays:
  - 3    # Days after initial send for followup_1
  - 7    # Days after initial send for followup_2
  - 14   # Days after initial send for followup_3
  - 21   # Days after initial send for followup_4

max_followups: 4   # Stop after this many follow-ups (now supports 4)

# Reply detection
inbox_scan_days: 30          # How far back to scan inbox
match_by: "conversation"     # "conversation" or "subject"

# Safety settings
send_delay_seconds: 5        # Pause between emails (avoid spam flags)
dry_run: false               # If true, display emails but don't send

# Email sending options
default_send_mode: "send"    # "send" (immediate), "msg_file" (save as .msg), or "defer" (delay)
msg_output_folder: "msg_files"  # Folder for saving .msg files
default_defer_hours: 1       # Hours to defer when using "defer" mode

# Campaign ID tracking
campaign_id_state_file: "campaign_id_state.json"  # Tracks unique email IDs
"""

    def _create_default_templates(self, templates_folder: Path) -> None:
        """Create default email templates."""
        templates = {
            "initial.html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>Dear {title} {last_name},</p>

    <p>This is the initial email template.</p>

    <p>Best regards,<br>
    {sender_name}</p>
</body>
</html>""",
            "followup_1.html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>Dear {title} {last_name},</p>

    <p>This is the first follow-up email template.</p>

    <p>Best regards,<br>
    {sender_name}</p>
</body>
</html>""",
            "followup_2.html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>Dear {title} {last_name},</p>

    <p>This is the second follow-up email template.</p>

    <p>Best regards,<br>
    {sender_name}</p>
</body>
</html>""",
            "followup_3.html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>Dear {title} {last_name},</p>

    <p>This is the third follow-up email template.</p>

    <p>Best regards,<br>
    {sender_name}</p>
</body>
</html>""",
            "followup_4.html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>Dear {title} {last_name},</p>

    <p>This is the fourth follow-up email template.</p>

    <p>Best regards,<br>
    {sender_name}</p>
</body>
</html>"""
        }

        for filename, content in templates.items():
            template_file = templates_folder / filename
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"[FILE CREATE] Created template: {template_file.absolute()}")

    def _copy_templates(self, source_folder: Path, dest_folder: Path) -> None:
        """Copy templates from source campaign to new campaign."""
        for template_file in source_folder.glob("*.html"):
            dest_file = dest_folder / template_file.name
            shutil.copy2(template_file, dest_file)
            self.logger.info(f"[FILE COPY] Copied template: {template_file.name}")

    def get_active_campaign(self) -> Optional[str]:
        """
        Get name of currently active campaign.

        Returns:
            Campaign name or None
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                return data.get('active_campaign')
            except:
                pass
        return None

    def set_active_campaign(self, campaign_name: str) -> bool:
        """
        Set active campaign.

        Args:
            campaign_name: Name of campaign to activate

        Returns:
            True if successful, False if campaign not found
        """
        campaign = self.get_campaign(campaign_name)
        if not campaign or not campaign.exists():
            return False

        data = {
            'active_campaign': campaign_name,
            'last_updated': datetime.now().isoformat()
        }

        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"[CAMPAIGNS] Set active campaign: {campaign_name}")
        return True
