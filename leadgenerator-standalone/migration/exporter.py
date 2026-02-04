"""Export SQLite data to JSON for migration to PostgreSQL."""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.database import get_db, get_setting

logger = logging.getLogger(__name__)


def export_to_json(output_path: str, campaign_ids: Optional[List[int]] = None) -> str:
    """
    Export data to JSON file for migration.

    Args:
        output_path: Path for output JSON file
        campaign_ids: Optional list of campaign IDs to export (None = all)

    Returns:
        Path to the exported file
    """
    db = get_db()

    export_data = {
        "export_version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "source": "standalone",
        "source_version": get_setting('app_version', '1.0.0'),
        "data": {}
    }

    # Export contact lists
    if campaign_ids:
        # Get list IDs from selected campaigns
        list_ids = set()
        for cid in campaign_ids:
            row = db.fetchone("SELECT contact_list_id FROM campaigns WHERE campaign_id = ?", (cid,))
            if row and row['contact_list_id']:
                list_ids.add(row['contact_list_id'])

        lists = []
        for lid in list_ids:
            rows = db.fetchall("SELECT * FROM contact_lists WHERE list_id = ?", (lid,))
            lists.extend([dict(row) for row in rows])
    else:
        lists = [dict(row) for row in db.fetchall("SELECT * FROM contact_lists")]

    export_data["data"]["contact_lists"] = lists

    # Export contacts
    if campaign_ids:
        contacts = []
        for lid in list_ids:
            rows = db.fetchall("SELECT * FROM contacts WHERE list_id = ?", (lid,))
            contacts.extend([dict(row) for row in rows])
    else:
        contacts = [dict(row) for row in db.fetchall("SELECT * FROM contacts")]

    export_data["data"]["contacts"] = contacts

    # Export campaigns
    if campaign_ids:
        campaigns = []
        for cid in campaign_ids:
            rows = db.fetchall("SELECT * FROM campaigns WHERE campaign_id = ?", (cid,))
            campaigns.extend([dict(row) for row in rows])
    else:
        campaigns = [dict(row) for row in db.fetchall("SELECT * FROM campaigns")]

    export_data["data"]["campaigns"] = campaigns

    # Get campaign IDs for related data
    if campaign_ids:
        cids = campaign_ids
    else:
        cids = [c['campaign_id'] for c in campaigns]

    # Export email steps
    steps = []
    for cid in cids:
        rows = db.fetchall("SELECT * FROM email_steps WHERE campaign_id = ?", (cid,))
        steps.extend([dict(row) for row in rows])

    export_data["data"]["email_steps"] = steps

    # Export attachments
    step_ids = [s['step_id'] for s in steps]
    attachments = []
    for sid in step_ids:
        rows = db.fetchall("SELECT * FROM attachments WHERE step_id = ?", (sid,))
        attachments.extend([dict(row) for row in rows])

    export_data["data"]["attachments"] = attachments

    # Export campaign contacts
    campaign_contacts = []
    for cid in cids:
        rows = db.fetchall("SELECT * FROM campaign_contacts WHERE campaign_id = ?", (cid,))
        campaign_contacts.extend([dict(row) for row in rows])

    export_data["data"]["campaign_contacts"] = campaign_contacts

    # Export email logs
    email_logs = []
    for cid in cids:
        rows = db.fetchall("SELECT * FROM email_logs WHERE campaign_id = ?", (cid,))
        email_logs.extend([dict(row) for row in rows])

    export_data["data"]["email_logs"] = email_logs

    # Export suppression list (always export all)
    suppression_list = [dict(row) for row in db.fetchall("SELECT * FROM suppression_list")]
    export_data["data"]["suppression_list"] = suppression_list

    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Exported data to {output_path}")
    logger.info(f"  - {len(lists)} contact lists")
    logger.info(f"  - {len(contacts)} contacts")
    logger.info(f"  - {len(campaigns)} campaigns")
    logger.info(f"  - {len(steps)} email steps")
    logger.info(f"  - {len(attachments)} attachments")
    logger.info(f"  - {len(suppression_list)} suppression entries")

    return output_path


def copy_attachment_files(output_folder: str, attachments_path: str = "data/files") -> int:
    """
    Copy attachment files to output folder.

    Args:
        output_folder: Destination folder
        attachments_path: Source attachments folder

    Returns:
        Number of files copied
    """
    source = Path(attachments_path)
    dest = Path(output_folder)
    dest.mkdir(parents=True, exist_ok=True)

    count = 0
    if source.exists():
        for file in source.rglob('*'):
            if file.is_file():
                rel_path = file.relative_to(source)
                dest_file = dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file)
                count += 1

    logger.info(f"Copied {count} attachment files to {output_folder}")
    return count
