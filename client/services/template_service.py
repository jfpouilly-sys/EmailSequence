"""Template rendering and management service."""
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.models import Contact, Campaign

logger = logging.getLogger(__name__)


@dataclass
class MergeTag:
    """Represents a merge tag."""
    tag: str
    label: str
    category: str
    fallback: Optional[str] = None


class TemplateService:
    """Service for email template operations."""

    # Standard merge tags
    MERGE_TAGS: List[MergeTag] = [
        # Contact fields
        MergeTag("{{FirstName}}", "First Name", "Contact"),
        MergeTag("{{LastName}}", "Last Name", "Contact"),
        MergeTag("{{Email}}", "Email", "Contact"),
        MergeTag("{{Company}}", "Company", "Contact"),
        MergeTag("{{Title}}", "Title", "Contact"),
        MergeTag("{{Position}}", "Position", "Contact"),
        MergeTag("{{Phone}}", "Phone", "Contact"),

        # Custom fields
        MergeTag("{{Custom1}}", "Custom Field 1", "Custom"),
        MergeTag("{{Custom2}}", "Custom Field 2", "Custom"),
        MergeTag("{{Custom3}}", "Custom Field 3", "Custom"),
        MergeTag("{{Custom4}}", "Custom Field 4", "Custom"),
        MergeTag("{{Custom5}}", "Custom Field 5", "Custom"),
        MergeTag("{{Custom6}}", "Custom Field 6", "Custom"),
        MergeTag("{{Custom7}}", "Custom Field 7", "Custom"),
        MergeTag("{{Custom8}}", "Custom Field 8", "Custom"),
        MergeTag("{{Custom9}}", "Custom Field 9", "Custom"),
        MergeTag("{{Custom10}}", "Custom Field 10", "Custom"),

        # Sender fields
        MergeTag("{{SenderName}}", "Sender Name", "Sender"),
        MergeTag("{{SenderEmail}}", "Sender Email", "Sender"),
        MergeTag("{{SenderTitle}}", "Sender Title", "Sender"),
        MergeTag("{{SenderCompany}}", "Sender Company", "Sender"),

        # Campaign fields
        MergeTag("{{CampaignName}}", "Campaign Name", "Campaign"),
        MergeTag("{{CampaignRef}}", "Campaign Reference", "Campaign"),
    ]

    # Pattern to match merge tags
    MERGE_TAG_PATTERN = re.compile(r'\{\{(\w+)\}\}')

    def __init__(self):
        self._fallbacks: Dict[str, str] = {}

    def get_all_merge_tags(self) -> List[MergeTag]:
        """Get all available merge tags."""
        return self.MERGE_TAGS.copy()

    def get_merge_tags_by_category(self, category: str) -> List[MergeTag]:
        """Get merge tags filtered by category."""
        return [t for t in self.MERGE_TAGS if t.category == category]

    def get_categories(self) -> List[str]:
        """Get all merge tag categories."""
        return list(set(t.category for t in self.MERGE_TAGS))

    def set_fallback(self, tag: str, fallback: str) -> None:
        """Set fallback value for a merge tag."""
        self._fallbacks[tag] = fallback

    def get_fallback(self, tag: str) -> Optional[str]:
        """Get fallback value for a merge tag."""
        return self._fallbacks.get(tag)

    def clear_fallbacks(self) -> None:
        """Clear all fallback values."""
        self._fallbacks.clear()

    def render_template(
        self,
        template: str,
        contact: Optional[Contact] = None,
        campaign: Optional[Campaign] = None,
        sender: Optional[Dict[str, str]] = None,
        custom_values: Optional[Dict[str, str]] = None
    ) -> str:
        """Render a template with merge tag values."""
        result = template

        # Build value map
        values: Dict[str, str] = {}

        if contact:
            values.update({
                "{{FirstName}}": contact.first_name or "",
                "{{LastName}}": contact.last_name or "",
                "{{Email}}": contact.email or "",
                "{{Company}}": contact.company or "",
                "{{Title}}": contact.title or "",
                "{{Position}}": contact.position or "",
                "{{Phone}}": contact.phone or "",
            })
            # Add custom fields
            for i in range(1, 11):
                key = f"custom{i}"
                values[f"{{{{Custom{i}}}}}"] = contact.custom_fields.get(key, "")

        if campaign:
            values.update({
                "{{CampaignName}}": campaign.name or "",
                "{{CampaignRef}}": campaign.campaign_ref or "",
            })

        if sender:
            values.update({
                "{{SenderName}}": sender.get("name", ""),
                "{{SenderEmail}}": sender.get("email", ""),
                "{{SenderTitle}}": sender.get("title", ""),
                "{{SenderCompany}}": sender.get("company", ""),
            })

        if custom_values:
            values.update(custom_values)

        # Replace merge tags
        for tag, value in values.items():
            if value:
                result = result.replace(tag, value)
            else:
                # Use fallback if available
                fallback = self._fallbacks.get(tag, "")
                result = result.replace(tag, fallback)

        return result

    def find_merge_tags(self, template: str) -> List[str]:
        """Find all merge tags in a template."""
        matches = self.MERGE_TAG_PATTERN.findall(template)
        return [f"{{{{{m}}}}}" for m in matches]

    def validate_template(self, template: str) -> Tuple[bool, List[str]]:
        """Validate template for unknown merge tags."""
        found_tags = self.find_merge_tags(template)
        known_tags = {t.tag for t in self.MERGE_TAGS}
        unknown_tags = [t for t in found_tags if t not in known_tags]
        return len(unknown_tags) == 0, unknown_tags

    def get_sample_contact(self) -> Contact:
        """Get a sample contact for preview."""
        return Contact(
            contact_id="sample",
            list_id="sample",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            company="Acme Corporation",
            title="Mr.",
            position="Sales Director",
            phone="+1 555-123-4567",
            custom_fields={
                "custom1": "Custom Value 1",
                "custom2": "Custom Value 2",
                "custom3": "Custom Value 3",
            }
        )

    def get_sample_campaign(self) -> Campaign:
        """Get a sample campaign for preview."""
        from core.models import CampaignStatus
        return Campaign(
            campaign_id="sample",
            name="Sample Campaign",
            campaign_ref="ISIT-250001",
            status=CampaignStatus.DRAFT
        )

    def preview_template(
        self,
        template: str,
        use_sample_data: bool = True
    ) -> str:
        """Preview template with sample or fallback data."""
        if use_sample_data:
            return self.render_template(
                template,
                contact=self.get_sample_contact(),
                campaign=self.get_sample_campaign(),
                sender={
                    "name": "Jane Smith",
                    "email": "jane.smith@company.com",
                    "title": "Account Executive",
                    "company": "Your Company"
                }
            )
        else:
            # Just use fallbacks
            return self.render_template(template)
