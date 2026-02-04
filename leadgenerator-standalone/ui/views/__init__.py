"""Views module for Lead Generator Standalone UI."""

from .dashboard_view import DashboardView
from .campaign_list_view import CampaignListView
from .campaign_detail_view import CampaignDetailView
from .contact_list_view import ContactListView
from .template_editor_view import TemplateEditorView
from .suppression_view import SuppressionView
from .reports_view import ReportsView
from .settings_view import SettingsView

__all__ = [
    'DashboardView',
    'CampaignListView',
    'CampaignDetailView',
    'ContactListView',
    'TemplateEditorView',
    'SuppressionView',
    'ReportsView',
    'SettingsView',
]
