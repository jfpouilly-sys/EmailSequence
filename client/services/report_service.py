"""Report generation service."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from io import BytesIO

from core.api_client import ApiClient
from core.models import OverallStatistics, CampaignStatistics, Campaign

logger = logging.getLogger(__name__)


class ReportService:
    """Service for report generation and statistics."""

    def __init__(self, api_client: ApiClient):
        self.api = api_client

    def get_overall_statistics(self, only_mine: bool = True) -> OverallStatistics:
        """Get overall statistics."""
        return self.api.get_overall_statistics(only_mine=only_mine)

    def get_campaign_statistics(self, campaign_id: str) -> CampaignStatistics:
        """Get campaign-specific statistics."""
        return self.api.get_campaign_statistics(campaign_id)

    def get_dashboard_data(self, only_mine: bool = True) -> Dict[str, Any]:
        """Get all data needed for dashboard view."""
        stats = self.get_overall_statistics(only_mine=only_mine)
        campaigns = self.api.get_campaigns(only_mine=only_mine)

        active_campaigns = [c for c in campaigns if c.status.value == "Active"]

        return {
            "statistics": stats,
            "total_campaigns": stats.total_campaigns,
            "active_campaigns": stats.active_campaigns,
            "total_emails_sent": stats.total_emails_sent,
            "total_contacts": stats.total_contacts,
            "active_campaign_list": active_campaigns,
            "response_rate": self._calculate_response_rate(campaigns)
        }

    def _calculate_response_rate(self, campaigns: List[Campaign]) -> float:
        """Calculate overall response rate from campaigns."""
        total_sent = sum(c.emails_sent for c in campaigns)
        if total_sent == 0:
            return 0.0
        total_responses = sum(
            int(c.emails_sent * c.response_rate / 100)
            for c in campaigns
        )
        return (total_responses / total_sent) * 100 if total_sent > 0 else 0.0

    def generate_campaign_report(self, campaign_id: str) -> Dict[str, Any]:
        """Generate a comprehensive campaign report."""
        campaign = self.api.get_campaign(campaign_id)
        stats = self.get_campaign_statistics(campaign_id)
        steps = self.api.get_campaign_steps(campaign_id)

        return {
            "campaign": campaign,
            "statistics": stats,
            "steps": steps,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "name": campaign.name,
                "status": campaign.status.value,
                "total_contacts": stats.total_contacts,
                "emails_sent": stats.emails_sent,
                "replies": stats.replies,
                "unsubscribes": stats.unsubscribes,
                "bounces": stats.bounces,
                "response_rate": stats.response_rate,
                "completion_rate": stats.completion_rate
            }
        }

    def export_campaign_report_csv(self, campaign_id: str) -> BytesIO:
        """Export campaign report as CSV."""
        import csv

        report = self.generate_campaign_report(campaign_id)
        output = BytesIO()

        # Write as text then encode
        text_output = []
        text_output.append("Campaign Report")
        text_output.append(f"Generated: {report['generated_at']}")
        text_output.append("")
        text_output.append("Summary")
        for key, value in report['summary'].items():
            text_output.append(f"{key},{value}")

        output.write('\n'.join(text_output).encode('utf-8'))
        output.seek(0)
        return output

    def export_campaign_report_pdf(self, campaign_id: str) -> BytesIO:
        """Export campaign report as PDF."""
        try:
            from fpdf import FPDF
        except ImportError:
            logger.warning("fpdf2 not installed, PDF export unavailable")
            raise ImportError("fpdf2 is required for PDF export")

        report = self.generate_campaign_report(campaign_id)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Campaign Report: {report['summary']['name']}", ln=True)

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Generated: {report['generated_at']}", ln=True)
        pdf.cell(0, 8, f"Status: {report['summary']['status']}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Statistics", ln=True)
        pdf.set_font("Arial", "", 10)

        stats = [
            ("Total Contacts", report['summary']['total_contacts']),
            ("Emails Sent", report['summary']['emails_sent']),
            ("Replies", report['summary']['replies']),
            ("Unsubscribes", report['summary']['unsubscribes']),
            ("Bounces", report['summary']['bounces']),
            ("Response Rate", f"{report['summary']['response_rate']:.1f}%"),
            ("Completion Rate", f"{report['summary']['completion_rate']:.1f}%"),
        ]

        for label, value in stats:
            pdf.cell(60, 6, label, border=1)
            pdf.cell(40, 6, str(value), border=1, ln=True)

        output = BytesIO()
        pdf.output(output)
        output.seek(0)
        return output
