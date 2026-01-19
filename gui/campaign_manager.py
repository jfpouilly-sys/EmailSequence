"""Campaign Management System

Handles creation, selection, and management of email campaigns.
Each campaign has its own contacts, templates, and configuration.
"""

import yaml
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


class Campaign:
    """Represents a single email campaign."""

    def __init__(self, name: str, base_path: Path):
        """Initialize campaign.

        Args:
            name: Campaign name
            base_path: Base campaigns directory path
        """
        self.name = name
        self.path = base_path / name
        self.contacts_file = self.path / "contacts.xlsx"
        self.templates_dir = self.path / "templates"
        self.config_file = self.path / "campaign_config.yaml"

    def exists(self) -> bool:
        """Check if campaign directory exists.

        Returns:
            True if campaign exists
        """
        return self.path.exists()

    def create(self, sample_contacts: bool = True) -> None:
        """Create campaign directory structure.

        Args:
            sample_contacts: Whether to create sample contacts
        """
        # Create directories
        self.path.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)

        # Create sample contacts if requested
        if sample_contacts:
            self._create_sample_contacts()

        # Create campaign configuration
        self._create_config()

        # Create template files
        self._create_default_templates()

    def _create_sample_contacts(self) -> None:
        """Create sample contacts.xlsx with 3 contacts."""
        sample_data = [
            {
                'title': 'Mr',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'company': 'Example Corp',
                'status': 'pending'
            },
            {
                'title': 'Ms',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@company.com',
                'company': 'Company Inc',
                'status': 'pending'
            },
            {
                'title': 'Dr',
                'first_name': 'Robert',
                'last_name': 'Johnson',
                'email': 'r.johnson@firm.com',
                'company': 'Firm LLC',
                'status': 'pending'
            }
        ]

        df = pd.DataFrame(sample_data)
        df.to_excel(self.contacts_file, index=False)

    def _create_config(self) -> None:
        """Create campaign configuration file."""
        config = {
            'campaign': {
                'name': self.name,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'description': '',
                'status': 'active'
            },
            'sequence': {
                'followup_delays': {
                    'followup_1': 3,
                    'followup_2': 7,
                    'followup_3': 14
                },
                'max_followups': 3
            },
            'email': {
                'sender_name': 'Your Name',
                'delay_between_sends': 5
            }
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def _create_default_templates(self) -> None:
        """Create default email templates."""
        templates = {
            'initial.html': '''<!-- Subject: Partnership Opportunity -->
<p>Dear {title} {last_name},</p>

<p>I hope this message finds you well.</p>

<p>I am reaching out to discuss a potential partnership opportunity between {company} and our organization.</p>

<p>Would you be available for a brief call to explore this further?</p>

<p>Best regards,<br>
{sender_name}</p>''',
            'followup_1.html': '''<!-- Subject: RE: Partnership Opportunity -->
<p>Dear {title} {last_name},</p>

<p>I wanted to follow up on my previous email regarding a potential partnership with {company}.</p>

<p>I believe this could be mutually beneficial. Would you have 15 minutes this week for a quick conversation?</p>

<p>Best regards,<br>
{sender_name}</p>''',
            'followup_2.html': '''<!-- Subject: RE: Partnership Opportunity - Final Follow-up -->
<p>Dear {title} {last_name},</p>

<p>I wanted to reach out one more time regarding the partnership opportunity.</p>

<p>If you're interested, I'd be happy to discuss. If not, I completely understand and won't take up any more of your time.</p>

<p>Best regards,<br>
{sender_name}</p>''',
            'followup_3.html': '''<!-- Subject: Closing the Loop -->
<p>Dear {title} {last_name},</p>

<p>I wanted to close the loop on my previous messages.</p>

<p>If circumstances change and you'd like to explore this opportunity in the future, please feel free to reach out.</p>

<p>Wishing you all the best.</p>

<p>Best regards,<br>
{sender_name}</p>'''
        }

        for filename, content in templates.items():
            template_file = self.templates_dir / filename
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)

    def get_config(self) -> Dict:
        """Load campaign configuration.

        Returns:
            Campaign configuration dictionary
        """
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def save_config(self, config: Dict) -> None:
        """Save campaign configuration.

        Args:
            config: Configuration dictionary
        """
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)


class CampaignManager:
    """Manages all campaigns."""

    def __init__(self, base_path: str = "campaigns"):
        """Initialize campaign manager.

        Args:
            base_path: Base directory for all campaigns
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def list_campaigns(self) -> List[str]:
        """Get list of all campaign names.

        Returns:
            List of campaign names
        """
        if not self.base_path.exists():
            return []

        campaigns = []
        for item in self.base_path.iterdir():
            if item.is_dir():
                campaigns.append(item.name)

        return sorted(campaigns)

    def get_campaign(self, name: str) -> Campaign:
        """Get campaign by name.

        Args:
            name: Campaign name

        Returns:
            Campaign object
        """
        return Campaign(name, self.base_path)

    def create_campaign(self, name: str, sample_contacts: bool = True) -> Campaign:
        """Create new campaign.

        Args:
            name: Campaign name
            sample_contacts: Whether to create sample contacts

        Returns:
            Created campaign object
        """
        campaign = self.get_campaign(name)
        campaign.create(sample_contacts=sample_contacts)
        return campaign

    def delete_campaign(self, name: str) -> bool:
        """Delete campaign.

        Args:
            name: Campaign name to delete

        Returns:
            True if successful
        """
        campaign = self.get_campaign(name)
        if campaign.exists():
            import shutil
            shutil.rmtree(campaign.path)
            return True
        return False

    def campaign_exists(self, name: str) -> bool:
        """Check if campaign exists.

        Args:
            name: Campaign name

        Returns:
            True if campaign exists
        """
        return self.get_campaign(name).exists()
