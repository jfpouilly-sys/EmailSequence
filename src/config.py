"""Configuration management for email sequence system."""
import os
import yaml
from typing import Any


class Config:
    """Load and validate configuration from YAML file."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Load config.yaml and set defaults for missing values.

        Args:
            config_path: Path to config file

        Raises:
            FileNotFoundError: If config doesn't exist
            ValueError: If required fields are invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                "Please create config.yaml or run 'python main.py init'"
            )

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

        self._validate()

    def _validate(self) -> None:
        """Validate configuration values."""
        # Check required fields
        required_fields = ['sender_name', 'default_subject']
        for field in required_fields:
            if not self._config.get(field):
                raise ValueError(f"Required configuration field missing: {field}")

        # Validate followup_delays
        delays = self._config.get('followup_delays', [])
        if not isinstance(delays, list) or len(delays) == 0:
            raise ValueError("followup_delays must be a non-empty list")

        for delay in delays:
            if not isinstance(delay, int) or delay <= 0:
                raise ValueError("All followup_delays must be positive integers")

        # Validate max_followups
        max_followups = self._config.get('max_followups', 3)
        if not isinstance(max_followups, int) or max_followups < 1:
            raise ValueError("max_followups must be a positive integer")

    def _get(self, key: str, default: Any = None) -> Any:
        """Get config value with optional default."""
        return self._config.get(key, default)

    @property
    def contacts_file(self) -> str:
        """Path to contacts Excel file."""
        return self._get('contacts_file', 'contacts.xlsx')

    @property
    def templates_folder(self) -> str:
        """Path to templates folder."""
        return self._get('templates_folder', 'templates')

    @property
    def log_file(self) -> str:
        """Path to log file."""
        return self._get('log_file', 'logs/sequence.log')

    @property
    def sender_name(self) -> str:
        """Display name for sender."""
        return self._get('sender_name')

    @property
    def default_subject(self) -> str:
        """Default email subject line."""
        return self._get('default_subject')

    @property
    def followup_delays(self) -> list[int]:
        """List of delays (in days) for follow-ups."""
        return self._get('followup_delays', [3, 7, 14])

    @property
    def max_followups(self) -> int:
        """Maximum number of follow-ups."""
        return self._get('max_followups', 3)

    @property
    def inbox_scan_days(self) -> int:
        """How many days back to scan inbox."""
        return self._get('inbox_scan_days', 30)

    @property
    def match_by(self) -> str:
        """Reply matching method: 'conversation' or 'subject'."""
        return self._get('match_by', 'conversation')

    @property
    def send_delay_seconds(self) -> int:
        """Delay between sending emails."""
        return self._get('send_delay_seconds', 5)

    @property
    def dry_run(self) -> bool:
        """Whether to display emails instead of sending."""
        return self._get('dry_run', False)
