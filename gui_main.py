"""Main GUI Application for Email Sequence System."""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime

# Import our modules
from src.config import Config
from src.contact_tracker import ContactTracker
from src.sequence_engine import SequenceEngine


class EmailSequenceGUI:
    """Main GUI for Email Sequence Automation."""

    def __init__(self, root):
        """Initialize the main GUI."""
        self.root = root
        self.root.title("Email Sequence Automation System")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Initialize variables
        self.config = None
        self.engine = None
        self.tracker = None

        # Create UI
        self.create_widgets()

        # Load configuration
        self.load_config()

    def load_config(self):
        """Load configuration and initialize components."""
        try:
            self.config = Config()
            self.engine = SequenceEngine(self.config)
            self.tracker = ContactTracker(self.config.contacts_file)

            self.log("Configuration loaded successfully")
            self.update_status_display()

        except FileNotFoundError as e:
            messagebox.showwarning("Configuration Missing",
                                  f"{str(e)}\n\nPlease initialize the system first.")
            self.log("ERROR: Configuration not found")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")
            self.log(f"ERROR: {str(e)}")

    def create_widgets(self):
        """Create GUI widgets."""
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # === TOP MENU BAR ===
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Initialize System", command=self.initialize_system)
        file_menu.add_command(label="Edit Configuration", command=self.open_config_editor)
        file_menu.add_separator()
        file_menu.add_command(label="Reload", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Contacts menu
        contacts_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Contacts", menu=contacts_menu)
        contacts_menu.add_command(label="Add Contact", command=self.add_contact)
        contacts_menu.add_command(label="Open Excel File", command=self.open_excel)

        # Actions menu
        actions_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Actions", menu=actions_menu)
        actions_menu.add_command(label="Send Initial Emails", command=self.send_initial)
        actions_menu.add_command(label="Check for Replies", command=self.check_replies)
        actions_menu.add_command(label="Send Follow-ups", command=self.send_followups)
        actions_menu.add_command(label="Run Full Cycle", command=self.run_cycle)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)

        # === TOOLBAR ===
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Button(toolbar, text="Send Initial", command=self.send_initial).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Check Replies", command=self.check_replies).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Send Follow-ups", command=self.send_followups).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Run Cycle", command=self.run_cycle).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="Refresh Status", command=self.update_status_display).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Contact", command=self.add_contact).pack(side=tk.LEFT, padx=2)

        # === MAIN CONTENT AREA ===
        main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Top: Status Panel
        status_frame = ttk.LabelFrame(main_paned, text="Status Overview", padding="10")
        main_paned.add(status_frame, weight=1)

        # Status text widget
        self.status_text = scrolledtext.ScrolledText(status_frame, height=12, state='disabled',
                                                     font=('Courier New', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Bottom: Log Panel
        log_frame = ttk.LabelFrame(main_paned, text="Activity Log", padding="10")
        main_paned.add(log_frame, weight=2)

        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state='disabled',
                                                  font=('Courier New', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # === STATUS BAR ===
        statusbar = ttk.Frame(self.root)
        statusbar.grid(row=2, column=0, sticky=(tk.W, tk.E))

        self.statusbar_label = ttk.Label(statusbar, text="Ready", relief=tk.SUNKEN)
        self.statusbar_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def log(self, message):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"

        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

        # Also update status bar
        self.statusbar_label.config(text=message)

    def update_status_display(self):
        """Update the status overview panel."""
        if not self.engine:
            return

        try:
            report = self.engine.get_status_report()

            status_lines = []
            status_lines.append("=" * 60)
            status_lines.append("EMAIL SEQUENCE STATUS REPORT")
            status_lines.append("=" * 60)
            status_lines.append("")
            status_lines.append(f"Total Contacts: {report['total_contacts']}")

            if report['sequence_id']:
                status_lines.append(f"Sequence ID: {report['sequence_id']}")

            if report['last_activity']:
                status_lines.append(f"Last Activity: {report['last_activity']}")

            status_lines.append("")
            status_lines.append("Status Breakdown:")
            status_lines.append("-" * 60)

            for status, count in report['by_status'].items():
                if count > 0:
                    status_lines.append(f"  {status:15} {count:4}")

            status_lines.append("")
            reply_rate_pct = report['reply_rate'] * 100
            status_lines.append(f"Reply Rate: {reply_rate_pct:.1f}%")
            status_lines.append("=" * 60)

            # Update display
            self.status_text.config(state='normal')
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', '\n'.join(status_lines))
            self.status_text.config(state='disabled')

            self.log("Status updated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status:\n{str(e)}")
            self.log(f"ERROR: {str(e)}")

    def initialize_system(self):
        """Initialize the system (create files and folders)."""
        try:
            # Create contacts file if missing
            if not os.path.exists('contacts.xlsx'):
                tracker = ContactTracker('contacts.xlsx')
                tracker.add_contact({
                    'title': 'Mr',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@example.com',
                    'company': 'Example Corp',
                    'status': 'pending',
                    'notes': 'Sample contact - replace with real data'
                })
                self.log("Created contacts.xlsx with sample data")

            # Create templates folder if missing
            if not os.path.exists('templates'):
                os.makedirs('templates')
                self.log("Created templates/ folder")

            # Create logs folder if missing
            if not os.path.exists('logs'):
                os.makedirs('logs')
                self.log("Created logs/ folder")

            # Create config if missing
            if not os.path.exists('config.yaml'):
                self.log("WARNING: config.yaml not found")
                messagebox.showwarning("Config Missing",
                                      "config.yaml not found. Please create it manually or use the config editor.")
            else:
                self.log("config.yaml already exists")

            messagebox.showinfo("Success", "System initialized successfully!")

            # Reload config
            self.load_config()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize system:\n{str(e)}")
            self.log(f"ERROR: {str(e)}")

    def open_config_editor(self):
        """Open the configuration editor in a new window."""
        try:
            import gui_config

            config_window = tk.Toplevel(self.root)
            gui_config.ConfigEditorGUI(config_window)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open config editor:\n{str(e)}")

    def open_excel(self):
        """Open contacts.xlsx in Excel."""
        try:
            import subprocess

            if os.path.exists(self.config.contacts_file):
                os.startfile(self.config.contacts_file)
                self.log(f"Opened {self.config.contacts_file}")
            else:
                messagebox.showwarning("File Not Found",
                                      f"Contacts file not found: {self.config.contacts_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Excel:\n{str(e)}")

    def add_contact(self):
        """Show dialog to add a new contact."""
        dialog = AddContactDialog(self.root, self.tracker)

        if dialog.result:
            self.log(f"Added contact: {dialog.result['email']}")
            self.update_status_display()

    def send_initial(self):
        """Send initial emails to pending contacts."""
        if not self.engine:
            messagebox.showwarning("Not Ready", "Please load configuration first")
            return

        if messagebox.askyesno("Confirm", "Send initial emails to all pending contacts?"):
            self.run_in_thread(self._send_initial_worker, "Sending initial emails...")

    def _send_initial_worker(self):
        """Worker thread for sending initial emails."""
        try:
            result = self.engine.start_sequence()

            self.log(f"Initial emails sent: {result['sent']}")
            if result['failed'] > 0:
                self.log(f"Failed: {result['failed']}")

            if result['errors']:
                for error in result['errors']:
                    self.log(f"ERROR: {error}")

            self.root.after(0, self.update_status_display)
            self.root.after(0, lambda: messagebox.showinfo("Complete",
                                                           f"Sent: {result['sent']}\nFailed: {result['failed']}"))

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def check_replies(self):
        """Check inbox for replies."""
        if not self.engine:
            messagebox.showwarning("Not Ready", "Please load configuration first")
            return

        self.run_in_thread(self._check_replies_worker, "Checking for replies...")

    def _check_replies_worker(self):
        """Worker thread for checking replies."""
        try:
            result = self.engine.check_replies()

            self.log(f"Replies found: {result['replies_found']}")

            for email in result['contacts_updated']:
                self.log(f"Reply detected: {email}")

            self.root.after(0, self.update_status_display)
            self.root.after(0, lambda: messagebox.showinfo("Complete",
                                                           f"Replies found: {result['replies_found']}"))

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def send_followups(self):
        """Send follow-up emails."""
        if not self.engine:
            messagebox.showwarning("Not Ready", "Please load configuration first")
            return

        if messagebox.askyesno("Confirm", "Send follow-up emails to non-responders?"):
            self.run_in_thread(self._send_followups_worker, "Sending follow-ups...")

    def _send_followups_worker(self):
        """Worker thread for sending follow-ups."""
        try:
            result = self.engine.send_followups()

            self.log(f"Follow-ups sent: {result['sent']}")
            if result['completed'] > 0:
                self.log(f"Completed: {result['completed']}")
            if result['failed'] > 0:
                self.log(f"Failed: {result['failed']}")

            if result['errors']:
                for error in result['errors']:
                    self.log(f"ERROR: {error}")

            self.root.after(0, self.update_status_display)
            self.root.after(0, lambda: messagebox.showinfo("Complete",
                                                           f"Sent: {result['sent']}\nCompleted: {result['completed']}\nFailed: {result['failed']}"))

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def run_cycle(self):
        """Run full cycle (check replies + send follow-ups)."""
        if not self.engine:
            messagebox.showwarning("Not Ready", "Please load configuration first")
            return

        self.run_in_thread(self._run_cycle_worker, "Running full cycle...")

    def _run_cycle_worker(self):
        """Worker thread for running full cycle."""
        try:
            result = self.engine.run_full_cycle()

            self.log(f"Replies found: {result['replies_found']}")
            self.log(f"Follow-ups sent: {result['followups_sent']}")
            if result['completed'] > 0:
                self.log(f"Completed: {result['completed']}")
            if result['followups_failed'] > 0:
                self.log(f"Failed: {result['followups_failed']}")

            if result['errors']:
                for error in result['errors']:
                    self.log(f"ERROR: {error}")

            self.root.after(0, self.update_status_display)
            self.root.after(0, lambda: messagebox.showinfo("Complete",
                                                           f"Replies: {result['replies_found']}\nFollow-ups sent: {result['followups_sent']}"))

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def run_in_thread(self, target, status_msg):
        """Run a function in a background thread."""
        self.statusbar_label.config(text=status_msg)
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def show_help(self):
        """Show help documentation."""
        help_text = """
EMAIL SEQUENCE AUTOMATION SYSTEM - HELP

GETTING STARTED:
1. Initialize the system (File > Initialize System)
2. Edit configuration (File > Edit Configuration)
3. Add contacts to contacts.xlsx (Contacts > Add Contact or Open Excel File)
4. Create email templates in templates/ folder
5. Test with dry run mode enabled
6. Send initial emails (Actions > Send Initial Emails)

WORKFLOW:
1. Add contacts with status='pending' to contacts.xlsx
2. Send initial emails (this sets status to 'sent')
3. System automatically checks for replies
4. System sends follow-ups to non-responders based on timing
5. Contacts who reply are marked 'replied'
6. After max follow-ups, contacts are marked 'completed'

AUTOMATION:
Use Windows Task Scheduler to run "Run Full Cycle" every 30 minutes.
This will automatically check for replies and send follow-ups.

TROUBLESHOOTING:
- Ensure Microsoft Outlook is running
- Check that contacts.xlsx is not open in Excel
- Review logs for detailed error messages
- Use dry run mode to test without sending

For more information, see README.md
        """

        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x500")

        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Courier New', 9))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', help_text)
        text.config(state='disabled')

        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=5)

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About",
                          "Email Sequence Automation System\n"
                          "Version 1.0.0\n\n"
                          "Automates email sequences via Microsoft Outlook\n"
                          "with intelligent reply tracking and follow-ups.\n\n"
                          "Built with Python, tkinter, and pywin32")


class AddContactDialog:
    """Dialog for adding a new contact."""

    def __init__(self, parent, tracker):
        """Initialize the add contact dialog."""
        self.tracker = tracker
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Contact")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Create form
        form_frame = ttk.Frame(self.dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        row = 0

        # Email (required)
        ttk.Label(form_frame, text="Email *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # First name (required)
        ttk.Label(form_frame, text="First Name *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.first_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.first_name_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Last name (required)
        ttk.Label(form_frame, text="Last Name *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.last_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.last_name_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Title
        ttk.Label(form_frame, text="Title:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.title_var, values=['Mr', 'Ms', 'Dr', 'Prof'],
                    width=28).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Company
        ttk.Label(form_frame, text="Company:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.company_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.notes_var, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Add Contact", command=self.add_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        form_frame.columnconfigure(1, weight=1)

        # Wait for dialog to close
        self.dialog.wait_window()

    def add_contact(self):
        """Add the contact."""
        # Validate
        if not self.email_var.get():
            messagebox.showerror("Validation Error", "Email is required")
            return

        if not self.first_name_var.get():
            messagebox.showerror("Validation Error", "First name is required")
            return

        if not self.last_name_var.get():
            messagebox.showerror("Validation Error", "Last name is required")
            return

        # Create contact data
        contact_data = {
            'email': self.email_var.get(),
            'first_name': self.first_name_var.get(),
            'last_name': self.last_name_var.get(),
            'title': self.title_var.get(),
            'company': self.company_var.get(),
            'notes': self.notes_var.get(),
            'status': 'pending'
        }

        # Add to tracker
        try:
            success = self.tracker.add_contact(contact_data)

            if success:
                self.result = contact_data
                messagebox.showinfo("Success", "Contact added successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Contact with this email already exists")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add contact:\n{str(e)}")


def main():
    """Run the main GUI application."""
    root = tk.Tk()

    # Apply a modern theme if available
    try:
        style = ttk.Style()
        style.theme_use('vista')  # Use Windows Vista theme
    except:
        pass

    app = EmailSequenceGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
