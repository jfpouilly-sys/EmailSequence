#!/usr/bin/env python3
"""Campaign System Demo

This script demonstrates how to create and manage campaigns in the
Email Sequence Manager.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.campaign_manager import CampaignManager, Campaign
import pandas as pd


def demo_campaign_creation():
    """Demonstrate campaign creation with sample contacts."""
    print("=" * 70)
    print("EMAIL SEQUENCE MANAGER - CAMPAIGN SYSTEM DEMO")
    print("=" * 70)
    print()

    # Initialize campaign manager
    print("1. Initializing Campaign Manager...")
    campaign_manager = CampaignManager("campaigns")
    print(f"   ✓ Campaigns folder: {campaign_manager.base_path}")
    print()

    # Create first campaign
    print("2. Creating campaign: 'my_first_campaign'")
    campaign1 = campaign_manager.create_campaign("my_first_campaign", sample_contacts=True)
    print(f"   ✓ Campaign created at: {campaign1.path}")
    print(f"   ✓ Contacts file: {campaign1.contacts_file}")
    print(f"   ✓ Templates directory: {campaign1.templates_dir}")
    print()

    # Show sample contacts
    print("3. Sample contacts created:")
    if campaign1.contacts_file.exists():
        df = pd.read_excel(campaign1.contacts_file)
        print(f"   ✓ {len(df)} contacts loaded")
        print()
        print("   Contacts:")
        for idx, row in df.iterrows():
            print(f"   {idx+1}. {row['title']} {row['first_name']} {row['last_name']}")
            print(f"      Email: {row['email']}")
            print(f"      Company: {row['company']}")
            print(f"      Status: {row['status']}")
            print()

    # Show templates
    print("4. Email templates created:")
    if campaign1.templates_dir.exists():
        templates = list(campaign1.templates_dir.glob("*.html"))
        for template in sorted(templates):
            print(f"   ✓ {template.name}")
    print()

    # Show campaign configuration
    print("5. Campaign configuration:")
    config = campaign1.get_config()
    print(f"   Name: {config['campaign']['name']}")
    print(f"   Created: {config['campaign']['created']}")
    print(f"   Status: {config['campaign']['status']}")
    print(f"   Follow-up delays:")
    for key, value in config['sequence']['followup_delays'].items():
        print(f"     - {key}: {value} days")
    print()

    # Create another campaign
    print("6. Creating another campaign: 'q1_2024_partners'")
    campaign2 = campaign_manager.create_campaign("q1_2024_partners", sample_contacts=True)
    print(f"   ✓ Campaign created at: {campaign2.path}")
    print()

    # List all campaigns
    print("7. All campaigns:")
    campaigns = campaign_manager.list_campaigns()
    for i, name in enumerate(campaigns, 1):
        campaign = campaign_manager.get_campaign(name)
        config = campaign.get_config()
        print(f"   {i}. {name}")
        print(f"      Created: {config['campaign'].get('created', 'Unknown')}")
        print(f"      Path: {campaign.path}")

        # Count contacts
        if campaign.contacts_file.exists():
            df = pd.read_excel(campaign.contacts_file)
            print(f"      Contacts: {len(df)}")
        print()

    print("=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("Directory structure created:")
    print()
    print("EmailSequence/")
    print("├── campaigns/")
    for campaign_name in campaigns:
        print(f"│   ├── {campaign_name}/")
        print(f"│   │   ├── contacts.xlsx       (3 sample contacts)")
        print(f"│   │   ├── templates/")
        print(f"│   │   │   ├── initial.html")
        print(f"│   │   │   ├── followup_1.html")
        print(f"│   │   │   ├── followup_2.html")
        print(f"│   │   │   └── followup_3.html")
        print(f"│   │   └── campaign_config.yaml")
    print("│")
    print("└── logs/                    (centralized logs for all campaigns)")
    print("    └── sequence.log")
    print()
    print("Next steps:")
    print("1. Run 'python run_gui.py' to launch the GUI")
    print("2. Select a campaign from the dialog")
    print("3. View the 3 sample contacts in the Contacts tab")
    print("4. Edit templates in the Templates tab")
    print("5. Start sending emails!")
    print()


def demo_campaign_operations():
    """Demonstrate various campaign operations."""
    print("\n" + "=" * 70)
    print("CAMPAIGN OPERATIONS DEMO")
    print("=" * 70)
    print()

    campaign_manager = CampaignManager("campaigns")

    print("Available operations:")
    print()
    print("1. List campaigns:")
    print("   campaigns = campaign_manager.list_campaigns()")
    print()
    print("2. Get specific campaign:")
    print("   campaign = campaign_manager.get_campaign('my_campaign')")
    print()
    print("3. Access campaign files:")
    print("   contacts = campaign.contacts_file  # contacts.xlsx path")
    print("   templates = campaign.templates_dir  # templates/ directory")
    print("   config = campaign.config_file  # campaign_config.yaml")
    print()
    print("4. Load campaign data:")
    print("   import pandas as pd")
    print("   df = pd.read_excel(campaign.contacts_file)")
    print()
    print("5. Get campaign configuration:")
    print("   config = campaign.get_config()")
    print("   sender_name = config['email']['sender_name']")
    print()
    print("6. Delete campaign:")
    print("   campaign_manager.delete_campaign('old_campaign')")
    print()


if __name__ == "__main__":
    try:
        # Run demos
        demo_campaign_creation()
        demo_campaign_operations()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
