"""Email template loading and personalization."""
import os
from typing import Optional


class TemplateEngine:
    """Load and personalize email templates."""

    def __init__(self, templates_folder: str):
        """
        Initialize with path to templates folder.
        Verify folder exists.

        Args:
            templates_folder: Path to templates directory

        Raises:
            FileNotFoundError: If templates folder doesn't exist
        """
        self.templates_folder = templates_folder

        if not os.path.exists(templates_folder):
            raise FileNotFoundError(
                f"Templates folder not found: {templates_folder}\n"
                "Please create the templates folder and add template files."
            )

        if not os.path.isdir(templates_folder):
            raise ValueError(
                f"{templates_folder} is not a directory"
            )

    def load_template(self, template_name: str) -> str:
        """
        Load template file content.

        Args:
            template_name: e.g., "initial" loads "initial.html"

        Returns:
            Raw HTML content of template file

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_path = os.path.join(self.templates_folder, f"{template_name}.html")

        if not os.path.exists(template_path):
            available = self.get_available_templates()
            available_str = ', '.join(available) if available else 'none'
            raise FileNotFoundError(
                f"Template not found: {template_name}.html\n"
                f"Available templates: {available_str}"
            )

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def render(self, template_name: str, contact: dict, sender_name: Optional[str] = None) -> str:
        """
        Load template and replace placeholders with contact data.

        Placeholders use format: {field_name}
        Available placeholders:
        - {title} - Mr, Ms, Dr, etc.
        - {first_name}
        - {last_name}
        - {full_name} - Computed: "{first_name} {last_name}"
        - {email}
        - {company}
        - {sender_name} - From config

        Args:
            template_name: Name of template to load
            contact: Dictionary with contact data
            sender_name: Optional sender name from config

        Returns:
            Rendered HTML with placeholders replaced

        Note:
            Missing placeholders remain as-is (don't crash).
        """
        template = self.load_template(template_name)

        # Create substitution dictionary
        subs = {}

        # Add contact fields
        for key, value in contact.items():
            if value is not None:
                subs[key] = str(value)

        # Add computed fields
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        if first_name and last_name:
            subs['full_name'] = f"{first_name} {last_name}"

        # Add sender_name if provided
        if sender_name:
            subs['sender_name'] = sender_name

        # Replace placeholders
        # Use a safer replacement that doesn't crash on missing keys
        rendered = template
        for key, value in subs.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, value)

        return rendered

    def get_available_templates(self) -> list[str]:
        """
        Return list of available template names (without .html).

        Returns:
            List of template names
        """
        if not os.path.exists(self.templates_folder):
            return []

        templates = []
        for filename in os.listdir(self.templates_folder):
            if filename.endswith('.html'):
                template_name = filename[:-5]  # Remove .html
                templates.append(template_name)

        return sorted(templates)
