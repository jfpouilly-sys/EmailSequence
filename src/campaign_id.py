"""Campaign ID generation and management.

Generates unique email IDs in format Lxxxxxx-y where:
- L: Literal prefix
- xxxxxx: 6-digit sequential number (000001 to 999999)
- y: Email sequence number (1=initial, 2=followup_1, 3=followup_2, 4=followup_3, 5=followup_4)
"""
import os
import json
import logging
from typing import Optional
from datetime import datetime


class CampaignIDGenerator:
    """Generate and track unique campaign IDs."""

    def __init__(self, state_file: str = "campaign_id_state.json"):
        """
        Initialize campaign ID generator.

        Args:
            state_file: Path to file storing the current ID counter
        """
        self.state_file = state_file
        self.logger = logging.getLogger(__name__)
        self.current_id = self._load_state()

    def _load_state(self) -> int:
        """
        Load current ID counter from state file.

        Returns:
            Current ID counter (1 to 999999)
        """
        if os.path.exists(self.state_file):
            try:
                abs_path = os.path.abspath(self.state_file)
                self.logger.info(f"[FILE READ] Loading campaign ID state from: {abs_path}")
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                current_id = data.get('current_id', 1)
                self.logger.info(f"[CAMPAIGN ID] Loaded current ID: {current_id}")
                return current_id
            except Exception as e:
                self.logger.warning(f"[CAMPAIGN ID] Failed to load state, starting from 1: {e}")
                return 1
        else:
            self.logger.info("[CAMPAIGN ID] State file not found, starting from 1")
            return 1

    def _save_state(self) -> None:
        """Save current ID counter to state file."""
        try:
            abs_path = os.path.abspath(self.state_file)
            data = {
                'current_id': self.current_id,
                'last_updated': datetime.now().isoformat()
            }
            self.logger.info(f"[FILE WRITE] Saving campaign ID state to: {abs_path}")
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"[CAMPAIGN ID] Saved state with current ID: {self.current_id}")
        except Exception as e:
            self.logger.error(f"[CAMPAIGN ID] Failed to save state: {e}")

    def generate_email_id(self, sequence_number: int) -> str:
        """
        Generate unique email ID in format Lxxxxxx-y.

        Args:
            sequence_number: Email sequence number (1=initial, 2=followup_1, 3=followup_2, etc.)

        Returns:
            Unique email ID (e.g., "L000123-2")

        Raises:
            ValueError: If ID counter exceeds 999999
        """
        if self.current_id > 999999:
            raise ValueError(
                "Campaign ID counter exceeded maximum value (999999). "
                "Please reset the counter or use a new state file."
            )

        # Format: Lxxxxxx-y
        email_id = f"L{self.current_id:06d}-{sequence_number}"

        self.logger.info(f"[CAMPAIGN ID] Generated email ID: {email_id} (counter: {self.current_id}, sequence: {sequence_number})")

        # Increment counter for next email
        self.current_id += 1
        self._save_state()

        return email_id

    def parse_email_id(self, email_id: str) -> Optional[dict]:
        """
        Parse email ID to extract components.

        Args:
            email_id: Email ID string (e.g., "L000123-2")

        Returns:
            Dict with 'counter' and 'sequence_number', or None if invalid

        Example:
            >>> parse_email_id("L000123-2")
            {'counter': 123, 'sequence_number': 2}
        """
        try:
            if not email_id or not email_id.startswith('L'):
                return None

            # Remove 'L' prefix
            rest = email_id[1:]

            # Split by '-'
            parts = rest.split('-')
            if len(parts) != 2:
                return None

            counter = int(parts[0])
            sequence_number = int(parts[1])

            return {
                'counter': counter,
                'sequence_number': sequence_number
            }
        except (ValueError, IndexError):
            return None

    def get_sequence_name(self, sequence_number: int) -> str:
        """
        Get template name for sequence number.

        Args:
            sequence_number: Sequence number (1-5)

        Returns:
            Template name (e.g., "initial", "followup_1")
        """
        mapping = {
            1: "initial",
            2: "followup_1",
            3: "followup_2",
            4: "followup_3",
            5: "followup_4"
        }
        return mapping.get(sequence_number, "initial")

    def get_sequence_number(self, template_name: str) -> int:
        """
        Get sequence number for template name.

        Args:
            template_name: Template name (e.g., "followup_2")

        Returns:
            Sequence number (1-5)
        """
        mapping = {
            "initial": 1,
            "followup_1": 2,
            "followup_2": 3,
            "followup_3": 4,
            "followup_4": 5
        }
        return mapping.get(template_name, 1)

    def reset_counter(self, new_value: int = 1) -> None:
        """
        Reset ID counter to specified value.

        Args:
            new_value: New counter value (1 to 999999)

        Raises:
            ValueError: If new_value is out of range
        """
        if new_value < 1 or new_value > 999999:
            raise ValueError("Counter value must be between 1 and 999999")

        self.logger.warning(f"[CAMPAIGN ID] Resetting counter from {self.current_id} to {new_value}")
        self.current_id = new_value
        self._save_state()
