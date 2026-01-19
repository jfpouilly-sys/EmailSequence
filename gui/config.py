"""GUI Configuration Manager

Handles loading, saving, and accessing GUI configuration from gui_config.yaml
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional


class GUIConfig:
    """Manages GUI configuration with defaults and validation."""

    DEFAULT_CONFIG = {
        'campaigns': {
            'base_folder': 'campaigns',
            'current_campaign': None
        },
        'paths': {
            'project_folder': os.getcwd(),
            'python_executable': 'python3',
            'logs_folder': 'logs'
        },
        'appearance': {
            'theme': 'dark',
            'color_scheme': 'blue',
            'window_width': 1200,
            'window_height': 800,
            'sidebar_width': 200
        },
        'behavior': {
            'auto_refresh_seconds': 30,
            'confirm_before_send': True,
            'show_notifications': True,
            'minimize_to_tray': True,
            'start_minimized': False,
            'show_campaign_on_startup': True
        },
        'recent_campaigns': []
    }

    def __init__(self, config_path: str = "gui_config.yaml"):
        """Initialize configuration manager.

        Args:
            config_path: Path to GUI configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file or create with defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                # Merge with defaults for any missing keys
                self.config = self._merge_with_defaults(self.config)
            except Exception as e:
                print(f"Error loading GUI config: {e}. Using defaults.")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error saving GUI config: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'appearance.theme')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'appearance.theme')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def get_absolute_path(self, relative_key: str) -> Path:
        """Get absolute path for a configured relative path.

        Args:
            relative_key: Key in paths section (e.g., 'contacts_file')

        Returns:
            Absolute Path object
        """
        project_folder = Path(self.get('paths.project_folder', os.getcwd()))
        relative_path = self.get(f'paths.{relative_key}', '')

        # If it's already absolute, return as-is
        rel_path = Path(relative_path)
        if rel_path.is_absolute():
            return rel_path

        # Otherwise, make it relative to project folder
        return project_folder / relative_path

    def add_recent_project(self, project_path: str) -> None:
        """Add project to recent projects list.

        Args:
            project_path: Path to add to recent list
        """
        recent = self.get('recent_projects', [])

        # Remove if already exists
        if project_path in recent:
            recent.remove(project_path)

        # Add to front
        recent.insert(0, project_path)

        # Keep only last 10
        self.config['recent_projects'] = recent[:10]
        self.save()

    def validate_paths(self) -> Dict[str, bool]:
        """Validate that configured paths exist.

        Returns:
            Dictionary mapping path keys to existence status
        """
        results = {}

        project_folder = Path(self.get('paths.project_folder', ''))
        results['project_folder'] = project_folder.exists()

        # Check relative paths
        for key in ['config_file', 'contacts_file', 'templates_folder', 'logs_folder']:
            path = self.get_absolute_path(key)
            results[key] = path.exists()

        return results

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to ensure all keys exist.

        Args:
            config: Loaded configuration

        Returns:
            Merged configuration
        """
        merged = self.DEFAULT_CONFIG.copy()

        for section_key, section_value in config.items():
            if section_key in merged and isinstance(section_value, dict):
                merged[section_key].update(section_value)
            else:
                merged[section_key] = section_value

        return merged

    def export_config(self, export_path: str) -> bool:
        """Export configuration to another file.

        Args:
            export_path: Path to export configuration to

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(export_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()

    # Campaign-specific methods

    def get_current_campaign(self) -> Optional[str]:
        """Get currently selected campaign name.

        Returns:
            Campaign name or None
        """
        return self.get('campaigns.current_campaign')

    def set_current_campaign(self, campaign_name: Optional[str]) -> None:
        """Set current campaign.

        Args:
            campaign_name: Campaign name or None
        """
        self.set('campaigns.current_campaign', campaign_name)
        self.save()

    def get_campaigns_base_path(self) -> Path:
        """Get campaigns base directory path.

        Returns:
            Absolute Path to campaigns directory
        """
        project_folder = Path(self.get('paths.project_folder', os.getcwd()))
        base_folder = self.get('campaigns.base_folder', 'campaigns')
        return project_folder / base_folder

    def get_campaign_path(self, campaign_name: str) -> Path:
        """Get path to specific campaign directory.

        Args:
            campaign_name: Campaign name

        Returns:
            Absolute Path to campaign directory
        """
        return self.get_campaigns_base_path() / campaign_name

    def get_campaign_contacts_file(self, campaign_name: Optional[str] = None) -> Path:
        """Get path to campaign contacts file.

        Args:
            campaign_name: Campaign name (uses current if None)

        Returns:
            Absolute Path to contacts.xlsx
        """
        if campaign_name is None:
            campaign_name = self.get_current_campaign()
        
        if campaign_name is None:
            raise ValueError("No campaign selected")

        return self.get_campaign_path(campaign_name) / "contacts.xlsx"

    def get_campaign_templates_path(self, campaign_name: Optional[str] = None) -> Path:
        """Get path to campaign templates directory.

        Args:
            campaign_name: Campaign name (uses current if None)

        Returns:
            Absolute Path to templates directory
        """
        if campaign_name is None:
            campaign_name = self.get_current_campaign()
        
        if campaign_name is None:
            raise ValueError("No campaign selected")

        return self.get_campaign_path(campaign_name) / "templates"

    def get_campaign_config_file(self, campaign_name: Optional[str] = None) -> Path:
        """Get path to campaign configuration file.

        Args:
            campaign_name: Campaign name (uses current if None)

        Returns:
            Absolute Path to campaign_config.yaml
        """
        if campaign_name is None:
            campaign_name = self.get_current_campaign()
        
        if campaign_name is None:
            raise ValueError("No campaign selected")

        return self.get_campaign_path(campaign_name) / "campaign_config.yaml"

    def get_logs_path(self) -> Path:
        """Get centralized logs directory path.

        Returns:
            Absolute Path to logs directory
        """
        project_folder = Path(self.get('paths.project_folder', os.getcwd()))
        logs_folder = self.get('paths.logs_folder', 'logs')
        return project_folder / logs_folder

    def add_recent_campaign(self, campaign_name: str) -> None:
        """Add campaign to recent campaigns list.

        Args:
            campaign_name: Campaign name
        """
        recent = self.get('recent_campaigns', [])

        # Remove if already exists
        if campaign_name in recent:
            recent.remove(campaign_name)

        # Add to front
        recent.insert(0, campaign_name)

        # Keep only last 10
        self.config['recent_campaigns'] = recent[:10]
        self.save()
