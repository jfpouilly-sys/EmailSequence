"""Templates Frame

Email template editor with live preview.
"""

import customtkinter as ctk
from gui.dialogs import InfoDialog
from pathlib import Path
import pandas as pd


class TemplatesFrame(ctk.CTkFrame):
    """Template editor with live preview."""

    TEMPLATE_TYPES = ['initial', 'followup_1', 'followup_2', 'followup_3']

    def __init__(self, parent, app):
        """Initialize templates frame.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent, fg_color="transparent")

        self.app = app
        self.gui_config = app.gui_config
        self.current_template = 'initial'
        self.sample_contact = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create components
        self.create_header()
        self.create_template_selector()
        self.create_subject_field()
        self.create_editor_preview()
        self.create_placeholder_buttons()
        self.create_preview_selector()
        self.create_action_buttons()

        # Load initial template
        self.load_template('initial')
        self.load_sample_contact()

    def create_header(self) -> None:
        """Create header with title."""
        title_label = ctk.CTkLabel(
            self,
            text="TEMPLATES",
            font=("Arial Bold", 24),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 20), padx=20)

    def create_template_selector(self) -> None:
        """Create template selector dropdown."""
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(selector_frame, text="Template:", font=("Arial", 12)).pack(side="left", padx=(0, 10))

        self.template_var = ctk.StringVar(value="initial")
        template_menu = ctk.CTkOptionMenu(
            selector_frame,
            variable=self.template_var,
            values=["Initial Email", "Follow-up #1", "Follow-up #2", "Follow-up #3"],
            command=self.on_template_select,
            width=180
        )
        template_menu.pack(side="left", padx=5)

    def create_subject_field(self) -> None:
        """Create subject line field."""
        subject_frame = ctk.CTkFrame(self, fg_color="transparent")
        subject_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        subject_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(subject_frame, text="Subject Line:", font=("Arial", 12)).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        self.subject_var = ctk.StringVar()
        self.subject_var.trace('w', lambda *args: self.update_preview())
        subject_entry = ctk.CTkEntry(
            subject_frame,
            textvariable=self.subject_var,
            font=("Arial", 12)
        )
        subject_entry.grid(row=0, column=1, sticky="ew")

    def create_editor_preview(self) -> None:
        """Create split editor and preview panes."""
        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        editor_frame.grid_columnconfigure((0, 1), weight=1)
        editor_frame.grid_rowconfigure(1, weight=1)

        # Editor side
        edit_label = ctk.CTkLabel(
            editor_frame,
            text="EDIT",
            font=("Arial Bold", 12),
            anchor="w"
        )
        edit_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        self.editor_text = ctk.CTkTextbox(
            editor_frame,
            font=("Courier", 11),
            wrap="word"
        )
        self.editor_text.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=(0, 15))
        self.editor_text.bind('<KeyRelease>', lambda e: self.update_preview())

        # Preview side
        preview_label = ctk.CTkLabel(
            editor_frame,
            text="PREVIEW",
            font=("Arial Bold", 12),
            anchor="w"
        )
        preview_label.grid(row=0, column=1, sticky="w", padx=15, pady=(10, 5))

        self.preview_text = ctk.CTkTextbox(
            editor_frame,
            font=("Arial", 11),
            wrap="word",
            state="disabled"
        )
        self.preview_text.grid(row=1, column=1, sticky="nsew", padx=(5, 15), pady=(0, 15))

    def create_placeholder_buttons(self) -> None:
        """Create placeholder insertion buttons."""
        placeholder_frame = ctk.CTkFrame(self, fg_color="transparent")
        placeholder_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            placeholder_frame,
            text="PLACEHOLDERS - Click to insert:",
            font=("Arial Bold", 11)
        ).pack(side="left", padx=(0, 15))

        placeholders = [
            '{title}', '{first_name}', '{last_name}', '{full_name}',
            '{email}', '{company}', '{sender_name}'
        ]

        for placeholder in placeholders:
            btn = ctk.CTkButton(
                placeholder_frame,
                text=placeholder,
                command=lambda p=placeholder: self.insert_placeholder(p),
                width=100,
                height=28,
                fg_color="gray",
                font=("Courier", 10)
            )
            btn.pack(side="left", padx=2)

    def create_preview_selector(self) -> None:
        """Create preview contact selector."""
        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            preview_frame,
            text="Preview using contact:",
            font=("Arial", 11)
        ).pack(side="left", padx=(0, 10))

        self.preview_contact_var = ctk.StringVar(value="Sample Contact")
        preview_menu = ctk.CTkOptionMenu(
            preview_frame,
            variable=self.preview_contact_var,
            values=["Sample Contact"],
            command=lambda x: self.update_preview(),
            width=300
        )
        preview_menu.pack(side="left", padx=5)

    def create_action_buttons(self) -> None:
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Template",
            command=self.on_save,
            width=150,
            fg_color="#10B981"
        )
        save_btn.pack(side="left", padx=5)

        revert_btn = ctk.CTkButton(
            button_frame,
            text="↩ Revert Changes",
            command=lambda: self.load_template(self.current_template),
            width=150,
            fg_color="gray"
        )
        revert_btn.pack(side="left", padx=5)

        test_btn = ctk.CTkButton(
            button_frame,
            text="📧 Send Test Email",
            command=self.on_send_test,
            width=150,
            fg_color="#3B82F6"
        )
        test_btn.pack(side="left", padx=5)

    def on_template_select(self, value: str) -> None:
        """Handle template selection.

        Args:
            value: Selected template display name
        """
        # Map display name to template file
        template_map = {
            "Initial Email": "initial",
            "Follow-up #1": "followup_1",
            "Follow-up #2": "followup_2",
            "Follow-up #3": "followup_3"
        }
        template_name = template_map.get(value, "initial")
        self.load_template(template_name)

    def load_template(self, template_name: str) -> None:
        """Load template from file.

        Args:
            template_name: Template file name (without extension)
        """
        self.current_template = template_name

        try:
            templates_folder = self.gui_config.get_campaign_templates_path()
            template_file = templates_folder / f"{template_name}.html"

            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract subject (if present in first line as comment)
                lines = content.split('\n')
                if lines and lines[0].startswith('<!-- Subject:'):
                    subject = lines[0].replace('<!-- Subject:', '').replace('-->', '').strip()
                    content = '\n'.join(lines[1:])
                else:
                    subject = f"Email - {template_name}"

                self.subject_var.set(subject)
                self.editor_text.delete("1.0", "end")
                self.editor_text.insert("1.0", content)
            else:
                # Create default template
                default_content = f"""<p>Dear {{title}} {{last_name}},</p>

<p>I hope this message finds you well.</p>

<p>This is a {template_name.replace('_', ' ')} template.</p>

<p>Best regards,<br>
{{sender_name}}</p>"""

                self.subject_var.set(f"Subject for {template_name}")
                self.editor_text.delete("1.0", "end")
                self.editor_text.insert("1.0", default_content)

            self.update_preview()

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to load template:\n{str(e)}")

    def load_sample_contact(self) -> None:
        """Load a sample contact for preview."""
        try:
            contacts_file = self.gui_config.get_absolute_path('contacts_file')
            if contacts_file.exists():
                df = pd.read_excel(contacts_file)
                if len(df) > 0:
                    self.sample_contact = df.iloc[0].to_dict()
                    return
        except:
            pass

        # Default sample
        self.sample_contact = {
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company': 'Example Corp',
            'sender_name': 'Your Name'
        }

    def insert_placeholder(self, placeholder: str) -> None:
        """Insert placeholder at cursor position.

        Args:
            placeholder: Placeholder text to insert
        """
        self.editor_text.insert("insert", placeholder)
        self.update_preview()

    def update_preview(self) -> None:
        """Update preview pane with rendered template."""
        try:
            # Get template content
            content = self.editor_text.get("1.0", "end-1c")

            # Replace placeholders with sample data
            if self.sample_contact:
                for key, value in self.sample_contact.items():
                    placeholder = f"{{{key}}}"
                    content = content.replace(placeholder, str(value))

                # Full name placeholder
                full_name = f"{self.sample_contact.get('first_name', '')} {self.sample_contact.get('last_name', '')}"
                content = content.replace('{full_name}', full_name.strip())

            # Remove HTML tags for preview (simple approach)
            import re
            preview_content = content
            preview_content = re.sub(r'<br\s*/?>', '\n', preview_content)
            preview_content = re.sub(r'<p>', '', preview_content)
            preview_content = re.sub(r'</p>', '\n\n', preview_content)
            preview_content = re.sub(r'<[^>]+>', '', preview_content)

            # Update preview
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", preview_content)
            self.preview_text.configure(state="disabled")

        except Exception as e:
            print(f"Error updating preview: {e}")

    def on_save(self) -> None:
        """Handle Save Template button."""
        try:
            templates_folder = self.gui_config.get_campaign_templates_path()
            templates_folder.mkdir(parents=True, exist_ok=True)

            template_file = templates_folder / f"{self.current_template}.html"

            # Get content
            content = self.editor_text.get("1.0", "end-1c")
            subject = self.subject_var.get()

            # Add subject as comment
            full_content = f"<!-- Subject: {subject} -->\n{content}"

            # Save file
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(full_content)

            InfoDialog.show(self, "Success", "Template saved successfully.")

        except Exception as e:
            InfoDialog.show(self, "Error", f"Failed to save template:\n{str(e)}")

    def on_send_test(self) -> None:
        """Handle Send Test Email button."""
        InfoDialog.show(
            self,
            "Send Test Email",
            "Test email functionality will be connected to Outlook.\n\n"
            "For now, this is a UI demonstration."
        )
