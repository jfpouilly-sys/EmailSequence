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
        'paths': {
            'project_folder': os.getcwd(),
            'python_executable': 'python3',
            'config_file': 'config.yaml',
            'contacts_file': 'contacts.xlsx',
            'templates_folder': 'templates',
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
            'start_minimized': False
        },
        'recent_projects': []
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
