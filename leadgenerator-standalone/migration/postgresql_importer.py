#!/usr/bin/env python3
"""
Import standalone export data into PostgreSQL (multi-user version).

This script is meant to be run on the server with the multi-user version.
It reads a JSON export file from the standalone version and imports the data.

Usage:
    python postgresql_importer.py \\
        --json-file export.json \\
        --db-host localhost \\
        --db-name leadgenerator \\
        --db-user leadgen_user \\
        --db-password YourPassword \\
        --target-user-id "uuid-of-user"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

# Note: This script requires psycopg2 which should be installed on the server
try:
    import psycopg2
    from psycopg2.extras import execute_values
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def import_from_json(
    json_path: str,
    db_host: str,
    db_name: str,
    db_user: str,
    db_password: str,
    target_user_id: str,
    db_port: int = 5432
) -> Dict[str, int]:
    """
    Import data from JSON export into PostgreSQL.

    Args:
        json_path: Path to JSON export file
        db_host: PostgreSQL host
        db_name: Database name
        db_user: Database user
        db_password: Database password
        target_user_id: UUID of user to assign imported data to
        db_port: Database port

    Returns:
        Dict with import counts
    """
    if not PSYCOPG2_AVAILABLE:
        raise ImportError("psycopg2 is required for PostgreSQL import")

    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        export_data = json.load(f)

    logger.info(f"Loaded export file: {json_path}")
    logger.info(f"Export version: {export_data.get('export_version')}")
    logger.info(f"Exported at: {export_data.get('exported_at')}")

    data = export_data.get('data', {})

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )

    stats = {
        'contact_lists': 0,
        'contacts': 0,
        'campaigns': 0,
        'email_steps': 0,
        'campaign_contacts': 0,
        'suppression': 0,
        'skipped': 0
    }

    try:
        with conn.cursor() as cur:
            # ID mappings (old ID -> new ID)
            list_id_map = {}
            contact_id_map = {}
            campaign_id_map = {}
            step_id_map = {}

            # Import contact lists
            for cl in data.get('contact_lists', []):
                old_id = cl['list_id']
                cur.execute("""
                    INSERT INTO contact_lists (user_id, name, description,
                        custom1_label, custom2_label, custom3_label, custom4_label, custom5_label,
                        custom6_label, custom7_label, custom8_label, custom9_label, custom10_label)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING list_id
                """, (
                    target_user_id, cl['name'], cl.get('description'),
                    cl.get('custom1_label'), cl.get('custom2_label'), cl.get('custom3_label'),
                    cl.get('custom4_label'), cl.get('custom5_label'), cl.get('custom6_label'),
                    cl.get('custom7_label'), cl.get('custom8_label'), cl.get('custom9_label'),
                    cl.get('custom10_label')
                ))
                new_id = cur.fetchone()[0]
                list_id_map[old_id] = new_id
                stats['contact_lists'] += 1

            # Import contacts
            for contact in data.get('contacts', []):
                old_id = contact['contact_id']
                new_list_id = list_id_map.get(contact['list_id'])
                if not new_list_id:
                    stats['skipped'] += 1
                    continue

                # Check for duplicate email in list
                cur.execute(
                    "SELECT 1 FROM contacts WHERE list_id = %s AND email = %s",
                    (new_list_id, contact['email'].lower())
                )
                if cur.fetchone():
                    logger.debug(f"Skipping duplicate contact: {contact['email']}")
                    stats['skipped'] += 1
                    continue

                cur.execute("""
                    INSERT INTO contacts (list_id, title, first_name, last_name, email, company,
                        position, phone, linkedin_url, source,
                        custom1, custom2, custom3, custom4, custom5,
                        custom6, custom7, custom8, custom9, custom10)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING contact_id
                """, (
                    new_list_id, contact.get('title'), contact['first_name'], contact['last_name'],
                    contact['email'].lower(), contact['company'], contact.get('position'),
                    contact.get('phone'), contact.get('linkedin_url'), contact.get('source'),
                    contact.get('custom1'), contact.get('custom2'), contact.get('custom3'),
                    contact.get('custom4'), contact.get('custom5'), contact.get('custom6'),
                    contact.get('custom7'), contact.get('custom8'), contact.get('custom9'),
                    contact.get('custom10')
                ))
                new_id = cur.fetchone()[0]
                contact_id_map[old_id] = new_id
                stats['contacts'] += 1

            # Import campaigns
            for campaign in data.get('campaigns', []):
                old_id = campaign['campaign_id']
                new_list_id = list_id_map.get(campaign.get('contact_list_id'))

                # Generate new campaign ref
                cur.execute("SELECT nextval('campaign_ref_seq')")
                seq = cur.fetchone()[0]
                year = datetime.now().strftime('%y')
                new_ref = f"ISIT-{year}{seq:04d}"

                # Store old ref in description
                desc = campaign.get('description') or ''
                desc = f"{desc}\n[Imported from standalone: {campaign['campaign_ref']}]".strip()

                cur.execute("""
                    INSERT INTO campaigns (user_id, name, description, campaign_ref, contact_list_id,
                        status, inter_email_delay_minutes, sequence_step_delay_days,
                        sending_window_start, sending_window_end, sending_days,
                        randomization_minutes, daily_send_limit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING campaign_id
                """, (
                    target_user_id, campaign['name'], desc, new_ref, new_list_id,
                    campaign.get('status', 'Draft'), campaign.get('inter_email_delay_minutes', 30),
                    campaign.get('sequence_step_delay_days', 3), campaign.get('sending_window_start', '09:00'),
                    campaign.get('sending_window_end', '17:00'), campaign.get('sending_days', 'Mon,Tue,Wed,Thu,Fri'),
                    campaign.get('randomization_minutes', 15), campaign.get('daily_send_limit', 50)
                ))
                new_id = cur.fetchone()[0]
                campaign_id_map[old_id] = new_id
                stats['campaigns'] += 1

            # Import email steps
            for step in data.get('email_steps', []):
                old_id = step['step_id']
                new_campaign_id = campaign_id_map.get(step['campaign_id'])
                if not new_campaign_id:
                    stats['skipped'] += 1
                    continue

                cur.execute("""
                    INSERT INTO email_steps (campaign_id, step_number, subject_template,
                        body_template, delay_days, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING step_id
                """, (
                    new_campaign_id, step['step_number'], step['subject_template'],
                    step['body_template'], step.get('delay_days', 0), step.get('is_active', True)
                ))
                new_id = cur.fetchone()[0]
                step_id_map[old_id] = new_id
                stats['email_steps'] += 1

            # Import campaign contacts
            for cc in data.get('campaign_contacts', []):
                new_campaign_id = campaign_id_map.get(cc['campaign_id'])
                new_contact_id = contact_id_map.get(cc['contact_id'])
                if not new_campaign_id or not new_contact_id:
                    stats['skipped'] += 1
                    continue

                cur.execute("""
                    INSERT INTO campaign_contacts (campaign_id, contact_id, status, current_step,
                        last_email_sent_at, responded_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (campaign_id, contact_id) DO NOTHING
                """, (
                    new_campaign_id, new_contact_id, cc.get('status', 'Pending'),
                    cc.get('current_step', 0), cc.get('last_email_sent_at'), cc.get('responded_at')
                ))
                stats['campaign_contacts'] += 1

            # Import suppression list
            for entry in data.get('suppression_list', []):
                new_campaign_id = campaign_id_map.get(entry.get('campaign_id')) if entry.get('campaign_id') else None

                cur.execute("""
                    INSERT INTO suppression_list (email, scope, source, campaign_id, reason)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                """, (
                    entry['email'].lower(), entry.get('scope', 'Global'),
                    entry.get('source', 'Manual'), new_campaign_id, entry.get('reason')
                ))
                stats['suppression'] += 1

            conn.commit()

    except Exception as e:
        conn.rollback()
        logger.error(f"Import failed: {e}")
        raise
    finally:
        conn.close()

    logger.info("Import complete!")
    logger.info(f"  - {stats['contact_lists']} contact lists")
    logger.info(f"  - {stats['contacts']} contacts")
    logger.info(f"  - {stats['campaigns']} campaigns")
    logger.info(f"  - {stats['email_steps']} email steps")
    logger.info(f"  - {stats['campaign_contacts']} campaign contacts")
    logger.info(f"  - {stats['suppression']} suppression entries")
    logger.info(f"  - {stats['skipped']} items skipped")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Import standalone export into PostgreSQL')
    parser.add_argument('--json-file', required=True, help='Path to JSON export file')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', type=int, default=5432, help='Database port')
    parser.add_argument('--db-name', required=True, help='Database name')
    parser.add_argument('--db-user', required=True, help='Database user')
    parser.add_argument('--db-password', required=True, help='Database password')
    parser.add_argument('--target-user-id', required=True, help='UUID of user to assign data to')

    args = parser.parse_args()

    try:
        import_from_json(
            json_path=args.json_file,
            db_host=args.db_host,
            db_port=args.db_port,
            db_name=args.db_name,
            db_user=args.db_user,
            db_password=args.db_password,
            target_user_id=args.target_user_id
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
