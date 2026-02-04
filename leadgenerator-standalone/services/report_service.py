"""Report generation service for Lead Generator Standalone."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from core.database import get_db
from core.models import EmailLog, Campaign

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating campaign reports."""

    def __init__(self):
        self.db = get_db()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get overview statistics for dashboard."""
        stats = {
            'active_campaigns': 0,
            'total_contacts': 0,
            'emails_sent_30d': 0,
            'response_rate': 0.0
        }

        # Active campaigns
        row = self.db.fetchone("""
            SELECT COUNT(*) as count FROM campaigns WHERE status = 'Active'
        """)
        stats['active_campaigns'] = row['count'] if row else 0

        # Total contacts
        row = self.db.fetchone("""
            SELECT COUNT(*) as count FROM contacts
        """)
        stats['total_contacts'] = row['count'] if row else 0

        # Emails sent in last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        row = self.db.fetchone("""
            SELECT COUNT(*) as count FROM email_logs
            WHERE status = 'Sent' AND sent_at >= ?
        """, (thirty_days_ago,))
        stats['emails_sent_30d'] = row['count'] if row else 0

        # Response rate (responded / total sent in active + completed campaigns)
        response_row = self.db.fetchone("""
            SELECT
                COALESCE(SUM(CASE WHEN cc.status = 'Responded' THEN 1 ELSE 0 END), 0) as responded,
                COUNT(*) as total
            FROM campaign_contacts cc
            JOIN campaigns c ON cc.campaign_id = c.campaign_id
            WHERE c.status IN ('Active', 'Completed')
        """)
        if response_row and response_row['total'] > 0:
            stats['response_rate'] = round(
                (response_row['responded'] / response_row['total']) * 100, 1
            )

        return stats

    def get_campaign_report(self, campaign_id: int) -> Dict[str, Any]:
        """Get detailed report for a specific campaign."""
        campaign_row = self.db.fetchone("""
            SELECT c.*, cl.name as contact_list_name
            FROM campaigns c
            LEFT JOIN contact_lists cl ON c.contact_list_id = cl.list_id
            WHERE c.campaign_id = ?
        """, (campaign_id,))

        if not campaign_row:
            return {}

        report = {
            'campaign': {
                'id': campaign_row['campaign_id'],
                'name': campaign_row['name'],
                'ref': campaign_row['campaign_ref'],
                'status': campaign_row['status'],
                'contact_list': campaign_row['contact_list_name'],
                'start_date': campaign_row['start_date'],
                'end_date': campaign_row['end_date']
            },
            'stats': self._get_campaign_stats(campaign_id),
            'daily_sends': self._get_daily_send_stats(campaign_id),
            'step_performance': self._get_step_performance(campaign_id)
        }

        return report

    def _get_campaign_stats(self, campaign_id: int) -> Dict[str, int]:
        """Get campaign contact statistics."""
        stats = {
            'total': 0,
            'pending': 0,
            'in_progress': 0,
            'responded': 0,
            'completed': 0,
            'bounced': 0,
            'unsubscribed': 0
        }

        rows = self.db.fetchall("""
            SELECT status, COUNT(*) as count
            FROM campaign_contacts
            WHERE campaign_id = ?
            GROUP BY status
        """, (campaign_id,))

        for row in rows:
            status = row['status'].lower()
            if status == 'inprogress':
                status = 'in_progress'
            if status in stats:
                stats[status] = row['count']
            stats['total'] += row['count']

        return stats

    def _get_daily_send_stats(self, campaign_id: int, days: int = 14) -> List[Dict[str, Any]]:
        """Get daily email send statistics."""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        rows = self.db.fetchall("""
            SELECT DATE(sent_at) as date, status, COUNT(*) as count
            FROM email_logs
            WHERE campaign_id = ? AND sent_at >= ?
            GROUP BY DATE(sent_at), status
            ORDER BY date
        """, (campaign_id, start_date))

        # Aggregate by date
        daily_stats = {}
        for row in rows:
            date = row['date']
            if date not in daily_stats:
                daily_stats[date] = {'date': date, 'sent': 0, 'failed': 0}

            if row['status'] == 'Sent':
                daily_stats[date]['sent'] = row['count']
            elif row['status'] == 'Failed':
                daily_stats[date]['failed'] = row['count']

        return list(daily_stats.values())

    def _get_step_performance(self, campaign_id: int) -> List[Dict[str, Any]]:
        """Get performance metrics for each email step."""
        rows = self.db.fetchall("""
            SELECT
                es.step_number,
                es.subject_template,
                COUNT(DISTINCT el.contact_id) as sent_count,
                (SELECT COUNT(*) FROM campaign_contacts cc
                 WHERE cc.campaign_id = es.campaign_id
                   AND cc.status = 'Responded'
                   AND cc.current_step >= es.step_number) as responses_after
            FROM email_steps es
            LEFT JOIN email_logs el ON es.step_id = el.step_id AND el.status = 'Sent'
            WHERE es.campaign_id = ?
            GROUP BY es.step_id
            ORDER BY es.step_number
        """, (campaign_id,))

        return [dict(row) for row in rows]

    def get_email_logs(
        self,
        campaign_id: Optional[int] = None,
        contact_id: Optional[int] = None,
        status: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
        offset: int = 0
    ) -> List[EmailLog]:
        """Get email logs with optional filtering."""
        conditions = []
        params = []

        if campaign_id:
            conditions.append("el.campaign_id = ?")
            params.append(campaign_id)

        if contact_id:
            conditions.append("el.contact_id = ?")
            params.append(contact_id)

        if status:
            conditions.append("el.status = ?")
            params.append(status)

        if days:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("el.sent_at >= ?")
            params.append(start_date)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT el.*,
                   c.first_name, c.last_name, c.email as contact_email
            FROM email_logs el
            LEFT JOIN contacts c ON el.contact_id = c.contact_id
            {where_clause}
            ORDER BY el.sent_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        rows = self.db.fetchall(query, tuple(params))
        return [self._row_to_email_log(row) for row in rows]

    def export_campaign_report(self, campaign_id: int, file_path: str) -> None:
        """Export campaign report to CSV file."""
        report = self.get_campaign_report(campaign_id)

        with open(file_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"Campaign Report: {report['campaign']['name']}\n")
            f.write(f"Reference: {report['campaign']['ref']}\n")
            f.write(f"Status: {report['campaign']['status']}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")

            # Stats
            f.write("Statistics\n")
            f.write("-" * 40 + "\n")
            stats = report['stats']
            f.write(f"Total Contacts: {stats['total']}\n")
            f.write(f"Pending: {stats['pending']}\n")
            f.write(f"In Progress: {stats['in_progress']}\n")
            f.write(f"Responded: {stats['responded']}\n")
            f.write(f"Completed: {stats['completed']}\n")
            f.write(f"Bounced: {stats['bounced']}\n")
            f.write(f"Unsubscribed: {stats['unsubscribed']}\n\n")

            # Response rate
            if stats['total'] > 0:
                response_rate = (stats['responded'] / stats['total']) * 100
                f.write(f"Response Rate: {response_rate:.1f}%\n\n")

            # Email logs
            f.write("Email Log\n")
            f.write("-" * 40 + "\n")
            f.write("date,contact_name,contact_email,subject,status,error\n")

            logs = self.get_email_logs(campaign_id=campaign_id, days=365, limit=10000)
            for log in logs:
                name = f"{log.contact_name or ''}"
                email = log.contact_email or ''
                subject = (log.subject or '').replace(',', ';')
                error = (log.error_message or '').replace(',', ';')
                f.write(f"{log.sent_at},{name},{email},{subject},{log.status},{error}\n")

        logger.info(f"Exported campaign report to {file_path}")

    def get_activity_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activity feed for dashboard."""
        activities = []

        # Recent emails sent
        email_rows = self.db.fetchall("""
            SELECT el.sent_at, c.first_name, c.last_name, c.email, cam.name as campaign_name, el.status
            FROM email_logs el
            JOIN contacts c ON el.contact_id = c.contact_id
            JOIN campaigns cam ON el.campaign_id = cam.campaign_id
            ORDER BY el.sent_at DESC
            LIMIT ?
        """, (limit // 2,))

        for row in email_rows:
            activities.append({
                'type': 'email_sent' if row['status'] == 'Sent' else 'email_failed',
                'time': row['sent_at'],
                'contact': f"{row['first_name']} {row['last_name']}",
                'email': row['email'],
                'campaign': row['campaign_name']
            })

        # Recent responses
        response_rows = self.db.fetchall("""
            SELECT cc.responded_at, c.first_name, c.last_name, c.email, cam.name as campaign_name
            FROM campaign_contacts cc
            JOIN contacts c ON cc.contact_id = c.contact_id
            JOIN campaigns cam ON cc.campaign_id = cam.campaign_id
            WHERE cc.status = 'Responded' AND cc.responded_at IS NOT NULL
            ORDER BY cc.responded_at DESC
            LIMIT ?
        """, (limit // 2,))

        for row in response_rows:
            activities.append({
                'type': 'response',
                'time': row['responded_at'],
                'contact': f"{row['first_name']} {row['last_name']}",
                'email': row['email'],
                'campaign': row['campaign_name']
            })

        # Sort by time descending
        activities.sort(key=lambda x: x['time'] or '', reverse=True)
        return activities[:limit]

    def _row_to_email_log(self, row) -> EmailLog:
        """Convert database row to EmailLog model."""
        return EmailLog(
            log_id=row['log_id'],
            campaign_id=row['campaign_id'],
            contact_id=row['contact_id'],
            step_id=row['step_id'],
            subject=row['subject'],
            sent_at=row['sent_at'],
            status=row['status'],
            error_message=row['error_message'],
            outlook_entry_id=row['outlook_entry_id'],
            contact_name=f"{row['first_name'] or ''} {row['last_name'] or ''}".strip() if 'first_name' in row.keys() else None,
            contact_email=row['contact_email'] if 'contact_email' in row.keys() else None
        )
