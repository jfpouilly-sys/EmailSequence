"""UI views module."""
from .login_view import LoginView
from .dashboard_view import DashboardView
from .campaign_list_view import CampaignListView
from .campaign_detail_view import CampaignDetailView
from .contact_list_view import ContactListView
from .template_editor_view import TemplateEditorView
from .reports_view import ReportsView
from .user_management_view import UserManagementView
from .mail_accounts_view import MailAccountsView
from .suppression_view import SuppressionView
from .settings_view import SettingsView

__all__ = [
    'LoginView',
    'DashboardView',
    'CampaignListView',
    'CampaignDetailView',
    'ContactListView',
    'TemplateEditorView',
    'ReportsView',
    'UserManagementView',
    'MailAccountsView',
    'SuppressionView',
    'SettingsView'
]
