"""GUI Configuration Editor for Email Sequence System."""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yaml


class ConfigEditorGUI:
    """Graphical configuration editor for config.yaml."""

    def __init__(self, root, config_path="config.yaml"):
        """Initialize the configuration editor GUI."""
        self.root = root
        self.config_path = config_path
        self.config = {}

        self.root.title("Email Sequence - Configuration Editor")
        self.root.geometry("700x650")
        self.root.resizable(True, True)

        # Load config
        self.load_config()

        # Create UI
        self.create_widgets()

    def load_config(self):
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Default configuration
            self.config = {
                'contacts_file': 'contacts.xlsx',
                'templates_folder': 'templates',
                'log_file': 'logs/sequence.log',
                'sender_name': 'Your Name',
                'default_subject': 'Partnership Opportunity',
                'followup_delays': [3, 7, 14],
                'max_followups': 3,
                'inbox_scan_days': 30,
                'match_by': 'conversation',
                'send_delay_seconds': 5,
                'dry_run': False
            }

    def save_config(self):
        """Save configuration to YAML file."""
        try:
            # Update config from form fields
            self.config['contacts_file'] = self.contacts_file_var.get()
            self.config['templates_folder'] = self.templates_folder_var.get()
            self.config['log_file'] = self.log_file_var.get()
            self.config['sender_name'] = self.sender_name_var.get()
            self.config['default_subject'] = self.default_subject_var.get()

            # Parse followup delays
            delays_text = self.followup_delays_var.get()
            try:
                delays = [int(x.strip()) for x in delays_text.split(',')]
                self.config['followup_delays'] = delays
            except ValueError:
                messagebox.showerror("Error", "Follow-up delays must be comma-separated numbers (e.g., 3, 7, 14)")
                return

            self.config['max_followups'] = int(self.max_followups_var.get())
            self.config['inbox_scan_days'] = int(self.inbox_scan_days_var.get())
            self.config['match_by'] = self.match_by_var.get()
            self.config['send_delay_seconds'] = int(self.send_delay_var.get())
            self.config['dry_run'] = self.dry_run_var.get()

            # Write to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

            messagebox.showinfo("Success", f"Configuration saved to {self.config_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")

    def create_widgets(self):
        """Create GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        row = 0

        # Title
        title_label = ttk.Label(main_frame, text="Email Sequence Configuration",
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 15))
        row += 1

        # === PATHS SECTION ===
        section_label = ttk.Label(main_frame, text="File Paths", font=('Arial', 10, 'bold'))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 5))
        row += 1

        # Contacts file
        ttk.Label(main_frame, text="Contacts File:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.contacts_file_var = tk.StringVar(value=self.config.get('contacts_file', 'contacts.xlsx'))
        ttk.Entry(main_frame, textvariable=self.contacts_file_var, width=40).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse...", command=lambda: self.browse_file(self.contacts_file_var)).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Templates folder
        ttk.Label(main_frame, text="Templates Folder:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.templates_folder_var = tk.StringVar(value=self.config.get('templates_folder', 'templates'))
        ttk.Entry(main_frame, textvariable=self.templates_folder_var, width=40).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse...", command=lambda: self.browse_folder(self.templates_folder_var)).grid(
            row=row, column=2, padx=(5, 0), pady=5)
        row += 1

        # Log file
        ttk.Label(main_frame, text="Log File:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.log_file_var = tk.StringVar(value=self.config.get('log_file', 'logs/sequence.log'))
        ttk.Entry(main_frame, textvariable=self.log_file_var, width=40).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # === EMAIL SETTINGS ===
        section_label = ttk.Label(main_frame, text="Email Settings", font=('Arial', 10, 'bold'))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        row += 1

        # Sender name
        ttk.Label(main_frame, text="Sender Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sender_name_var = tk.StringVar(value=self.config.get('sender_name', 'Your Name'))
        ttk.Entry(main_frame, textvariable=self.sender_name_var, width=40).grid(
            row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Default subject
        ttk.Label(main_frame, text="Default Subject:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.default_subject_var = tk.StringVar(value=self.config.get('default_subject', 'Partnership Opportunity'))
        ttk.Entry(main_frame, textvariable=self.default_subject_var, width=40).grid(
            row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # === SEQUENCE TIMING ===
        section_label = ttk.Label(main_frame, text="Sequence Timing", font=('Arial', 10, 'bold'))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        row += 1

        # Follow-up delays
        ttk.Label(main_frame, text="Follow-up Delays (days):").grid(row=row, column=0, sticky=tk.W, pady=5)
        delays = self.config.get('followup_delays', [3, 7, 14])
        delays_str = ', '.join(str(d) for d in delays)
        self.followup_delays_var = tk.StringVar(value=delays_str)
        delay_entry = ttk.Entry(main_frame, textvariable=self.followup_delays_var, width=40)
        delay_entry.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Help text for delays
        help_label = ttk.Label(main_frame, text="(Comma-separated, e.g., 3, 7, 14)",
                              foreground='gray', font=('Arial', 8))
        help_label.grid(row=row, column=1, columnspan=2, sticky=tk.W)
        row += 1

        # Max follow-ups
        ttk.Label(main_frame, text="Max Follow-ups:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.max_followups_var = tk.StringVar(value=str(self.config.get('max_followups', 3)))
        ttk.Spinbox(main_frame, from_=1, to=10, textvariable=self.max_followups_var, width=10).grid(
            row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # === REPLY DETECTION ===
        section_label = ttk.Label(main_frame, text="Reply Detection", font=('Arial', 10, 'bold'))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        row += 1

        # Inbox scan days
        ttk.Label(main_frame, text="Inbox Scan Days:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.inbox_scan_days_var = tk.StringVar(value=str(self.config.get('inbox_scan_days', 30)))
        ttk.Spinbox(main_frame, from_=1, to=90, textvariable=self.inbox_scan_days_var, width=10).grid(
            row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Match by
        ttk.Label(main_frame, text="Match By:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.match_by_var = tk.StringVar(value=self.config.get('match_by', 'conversation'))
        match_frame = ttk.Frame(main_frame)
        match_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(match_frame, text="Conversation", variable=self.match_by_var,
                       value='conversation').pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(match_frame, text="Subject", variable=self.match_by_var,
                       value='subject').pack(side=tk.LEFT)
        row += 1

        # === SAFETY SETTINGS ===
        section_label = ttk.Label(main_frame, text="Safety Settings", font=('Arial', 10, 'bold'))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        row += 1

        # Send delay
        ttk.Label(main_frame, text="Send Delay (seconds):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.send_delay_var = tk.StringVar(value=str(self.config.get('send_delay_seconds', 5)))
        ttk.Spinbox(main_frame, from_=0, to=60, textvariable=self.send_delay_var, width=10).grid(
            row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Dry run
        self.dry_run_var = tk.BooleanVar(value=self.config.get('dry_run', False))
        ttk.Checkbutton(main_frame, text="Dry Run (display emails instead of sending)",
                       variable=self.dry_run_var).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=10)
        row += 1

        # === BUTTONS ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(20, 0))

        ttk.Button(button_frame, text="Save Configuration", command=self.save_config,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.root.destroy).pack(side=tk.LEFT, padx=5)

    def browse_file(self, var):
        """Browse for a file."""
        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)

    def browse_folder(self, var):
        """Browse for a folder."""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            var.set(folder)

    def reset_defaults(self):
        """Reset all fields to default values."""
        if messagebox.askyesno("Reset Configuration",
                              "Reset all settings to default values?"):
            self.contacts_file_var.set('contacts.xlsx')
            self.templates_folder_var.set('templates')
            self.log_file_var.set('logs/sequence.log')
            self.sender_name_var.set('Your Name')
            self.default_subject_var.set('Partnership Opportunity')
            self.followup_delays_var.set('3, 7, 14')
            self.max_followups_var.set('3')
            self.inbox_scan_days_var.set('30')
            self.match_by_var.set('conversation')
            self.send_delay_var.set('5')
            self.dry_run_var.set(False)


def main():
    """Run the configuration editor."""
    root = tk.Tk()

    # Apply a modern theme if available
    try:
        style = ttk.Style()
        style.theme_use('vista')  # Use Windows Vista theme
    except:
        pass

    app = ConfigEditorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
