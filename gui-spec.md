# Email Sequence GUI - Technical Specification

## Technology Stack

**Framework:** CustomTkinter (modern Tkinter wrapper)
**Why:** Native Windows look, pure Python, easy packaging, excellent AI code generation

**Additional dependencies:**
```
customtkinter>=5.2.0
pillow>=10.0.0          # For icons/images
tkcalendar>=1.6.1       # Date picker widgets
```

---

## Project Structure Addition

```
email-sequence/
├── ... (existing files from core spec)
├── gui/
│   ├── __init__.py
│   ├── app.py              # Main application window
│   ├── frames/
│   │   ├── __init__.py
│   │   ├── dashboard.py    # Dashboard/home frame
│   │   ├── contacts.py     # Contact management frame
│   │   ├── sequence.py     # Sequence control frame
│   │   ├── templates.py    # Template editor frame
│   │   ├── logs.py         # Log viewer frame
│   │   └── settings.py     # Settings frame
│   ├── components/
│   │   ├── __init__.py
│   │   ├── contact_table.py    # Reusable contact table widget
│   │   ├── status_badge.py     # Status indicator widget
│   │   └── progress_card.py    # Metric card widget
│   └── assets/
│       ├── icon.ico            # App icon
│       └── logo.png            # ISIT logo (optional)
├── gui_config.yaml         # GUI-specific configuration
└── run_gui.py              # GUI entry point
```

---

## GUI Configuration File

**gui_config.yaml:**
```yaml
# Paths (configurable by user)
paths:
  project_folder: "C:/email-sequence"      # Root folder
  python_executable: "python"               # Or full path to python.exe
  config_file: "config.yaml"                # Relative to project_folder
  contacts_file: "contacts.xlsx"            # Relative to project_folder
  templates_folder: "templates"             # Relative to project_folder
  logs_folder: "logs"                       # Relative to project_folder

# GUI appearance
appearance:
  theme: "dark"                # "dark", "light", or "system"
  color_scheme: "blue"         # "blue", "green", "dark-blue"
  window_width: 1200
  window_height: 800
  sidebar_width: 200

# Behavior
behavior:
  auto_refresh_seconds: 30     # Dashboard auto-refresh interval
  confirm_before_send: true    # Show confirmation dialog before sending
  show_notifications: true     # Windows toast notifications
  minimize_to_tray: true       # Minimize to system tray instead of taskbar

# Recent files (auto-populated)
recent_projects: []
```

---

## Window Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Email Sequence Manager                                    [─] [□] [×]  │
├────────────┬────────────────────────────────────────────────────────────┤
│            │                                                            │
│  ┌──────┐  │  ┌──────────────────────────────────────────────────────┐  │
│  │ 🏠   │  │  │                                                      │  │
│  │ HOME │  │  │                   CONTENT AREA                       │  │
│  └──────┘  │  │                                                      │  │
│            │  │              (Changes based on selected              │  │
│  ┌──────┐  │  │                   navigation item)                   │  │
│  │ 👥   │  │  │                                                      │  │
│  │CONTACTS│ │  │                                                      │  │
│  └──────┘  │  │                                                      │  │
│            │  │                                                      │  │
│  ┌──────┐  │  │                                                      │  │
│  │ ▶️   │  │  │                                                      │  │
│  │SEQUENCE│ │  │                                                      │  │
│  └──────┘  │  │                                                      │  │
│            │  │                                                      │  │
│  ┌──────┐  │  │                                                      │  │
│  │ 📝   │  │  │                                                      │  │
│  │TEMPLATES│ │                                                      │  │
│  └──────┘  │  │                                                      │  │
│            │  │                                                      │  │
│  ┌──────┐  │  │                                                      │  │
│  │ 📋   │  │  │                                                      │  │
│  │ LOGS │  │  │                                                      │  │
│  └──────┘  │  │                                                      │  │
│            │  │                                                      │  │
│  ┌──────┐  │  └──────────────────────────────────────────────────────┘  │
│  │ ⚙️   │  │                                                            │
│  │SETTINGS│ ├──────────────────────────────────────────────────────────┤
│  └──────┘  │  Status: Ready │ Outlook: Connected │ Last sync: 14:30    │
│            │                                                            │
└────────────┴────────────────────────────────────────────────────────────┘
```

---

## Frame Specifications

### 1. Dashboard Frame (Home)

**Purpose:** Overview of sequence status and quick actions

```
┌─────────────────────────────────────────────────────────────────────┐
│  DASHBOARD                                          [🔄 Refresh]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │     12      │ │      5      │ │      3      │ │    25%      │   │
│  │   PENDING   │ │    SENT     │ │   REPLIED   │ │ REPLY RATE  │   │
│  │  ○ ○ ○ ○    │ │  ● ● ● ○    │ │  ✓ ✓ ✓      │ │  ████░░░░   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│  QUICK ACTIONS                                                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐    │
│  │  ▶ START         │ │  🔍 CHECK        │ │  ↻ SEND          │    │
│  │    SEQUENCE      │ │    REPLIES       │ │    FOLLOW-UPS    │    │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘    │
│                                                                     │
│  RECENT ACTIVITY                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 14:32  ✓  Reply received from jean.dupont@acme.com          │   │
│  │ 14:30  →  Follow-up #2 sent to marie.martin@corp.fr         │   │
│  │ 14:30  →  Follow-up #1 sent to pierre.durand@company.com    │   │
│  │ 10:00  ▶  Sequence started: 5 initial emails sent           │   │
│  │ 09:45  +  3 contacts imported from CSV                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  SEQUENCE STATUS                     NEXT SCHEDULED ACTION          │
│  ┌─────────────────────────┐        ┌─────────────────────────┐    │
│  │ Current: seq_20260117   │        │ 3 follow-ups due        │    │
│  │ Started: Jan 17, 10:00  │        │ Next check: 15:00       │    │
│  │ Total contacts: 20      │        │ [Run Now]               │    │
│  └─────────────────────────┘        └─────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Widgets:**
- `ProgressCard` - Metric display with icon, number, label, optional progress bar
- `ActivityList` - Scrollable list of recent log entries
- `QuickActionButton` - Large buttons for common actions

---

### 2. Contacts Frame

**Purpose:** View, edit, import/export contacts

```
┌─────────────────────────────────────────────────────────────────────┐
│  CONTACTS                                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [+ Add Contact]  [📥 Import CSV]  [📤 Export]  [🗑 Delete Selected] │
│                                                                     │
│  Filter: [All Statuses     ▼]  Search: [____________________] 🔍   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ☐ │ Name           │ Email              │ Company    │Status│   │
│  ├───┼────────────────┼────────────────────┼────────────┼──────┤   │
│  │ ☐ │ Mr Jean Dupont │ jean@acme.com      │ Acme Corp  │●SENT │   │
│  │ ☐ │ Ms Marie Martin│ marie@corp.fr      │ Corp SA    │●FU-2 │   │
│  │ ☐ │ Dr P. Durand   │ pierre@company.com │ Company    │✓REPLIED│ │
│  │ ☐ │ Mr Louis Petit │ louis@firm.com     │ Firm Ltd   │○PENDING│ │
│  │ ☐ │ Ms Claire Roy  │ claire@group.fr    │ Group SAS  │✗BOUNCED│ │
│  │   │                │                    │            │      │   │
│  │   │                │                    │            │      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                     Page 1 of 3 [<][>]│
│                                                                     │
│  CONTACT DETAILS (select a row above)                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Title: [Mr     ▼]  First: [Jean      ]  Last: [Dupont    ] │   │
│  │  Email: [jean@acme.com                ]  Company: [Acme Corp]│   │
│  │  Status: SENT        Sequence: seq_20260117                  │   │
│  │  Initial sent: 2026-01-15 10:30    Follow-ups: 1            │   │
│  │  Last contact: 2026-01-18 14:30    Notes: [_______________] │   │
│  │                                                              │   │
│  │  [💾 Save Changes]  [↻ Reset Status]  [⛔ Mark Opted-Out]    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Sortable columns (click header)
- Multi-select with checkboxes
- Status filter dropdown
- Search box (filters as you type)
- Inline status badges with colors
- Detail panel for selected contact
- CSV import with column mapping dialog

**Status colors:**
- `pending` → Gray ○
- `sent` → Blue ●
- `followup_1/2/3` → Orange ●
- `replied` → Green ✓
- `bounced` → Red ✗
- `opted_out` → Black ⛔
- `completed` → Purple ◆

---

### 3. Sequence Frame

**Purpose:** Control sequence execution and timing

```
┌─────────────────────────────────────────────────────────────────────┐
│  SEQUENCE CONTROL                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CURRENT SEQUENCE                                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ID: seq_20260117_100000                                     │   │
│  │  Status: ● ACTIVE                                            │   │
│  │  Started: January 17, 2026 at 10:00                          │   │
│  │                                                              │   │
│  │  Progress:  ████████████████░░░░░░░░░░░░░░  45% (9/20)       │   │
│  │             Replied: 3  |  In progress: 6  |  Remaining: 11  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ACTIONS                                                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │
│  │                 │ │                 │ │                 │       │
│  │   ▶ START NEW   │ │  ⏸ PAUSE       │ │  ⏹ STOP        │       │
│  │     SEQUENCE    │ │    SEQUENCE     │ │    SEQUENCE     │       │
│  │                 │ │                 │ │                 │       │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘       │
│                                                                     │
│  MANUAL OPERATIONS                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  [🔍 Check Replies Now]     Last check: 14:30 (2 found)     │   │
│  │  [↻ Send Follow-ups Now]    Last sent: 14:30 (3 sent)       │   │
│  │  [▶ Run Full Cycle]         Runs both operations            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  SCHEDULING                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ☑ Enable automatic cycling                                  │   │
│  │  Run every: [30    ] minutes                                 │   │
│  │  Active hours: [08:00] to [18:00]                           │   │
│  │  Active days: ☑Mon ☑Tue ☑Wed ☑Thu ☑Fri ☐Sat ☐Sun           │   │
│  │                                                              │   │
│  │  Task Scheduler status: ● Configured                         │   │
│  │  [Update Schedule]  [View in Task Scheduler]                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  FOLLOW-UP TIMING                                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Days after initial email:                                   │   │
│  │  Follow-up #1: [3  ] days    Follow-up #2: [7  ] days       │   │
│  │  Follow-up #3: [14 ] days    Max follow-ups: [3  ]          │   │
│  │                                              [Save Timing]   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time progress visualization
- Start new sequence with confirmation dialog
- Pause/resume capability (paused contacts don't receive follow-ups)
- Manual trigger buttons with last-run timestamps
- Schedule configuration that updates Windows Task Scheduler
- Follow-up timing adjustment (saves to config.yaml)

---

### 4. Templates Frame

**Purpose:** View and edit email templates

```
┌─────────────────────────────────────────────────────────────────────┐
│  TEMPLATES                                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Template: [Initial Email    ▼]  [+ New Template]  [🗑 Delete]      │
│                                                                     │
│  Subject Line:                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Partnership Opportunity - ISIT                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ EDIT                              │ PREVIEW                  │   │
│  ├───────────────────────────────────┼──────────────────────────┤   │
│  │ <p>Dear {title} {last_name},</p>  │ Dear Mr Dupont,          │   │
│  │                                   │                          │   │
│  │ <p>I hope this message finds you  │ I hope this message finds│   │
│  │ well.</p>                         │ you well.                │   │
│  │                                   │                          │   │
│  │ <p>I am reaching out regarding    │ I am reaching out        │   │
│  │ potential collaboration between   │ regarding potential      │   │
│  │ {company} and ISIT...</p>         │ collaboration between    │   │
│  │                                   │ Acme Corp and ISIT...    │   │
│  │ <p>Best regards,<br>              │                          │   │
│  │ {sender_name}</p>                 │ Best regards,            │   │
│  │                                   │ Jean-François            │   │
│  │                                   │                          │   │
│  └───────────────────────────────────┴──────────────────────────┘   │
│                                                                     │
│  PLACEHOLDERS                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Click to insert: {title} {first_name} {last_name} {full_name}│   │
│  │                  {email} {company} {sender_name}             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Preview using contact: [Jean Dupont (jean@acme.com)    ▼]         │
│                                                                     │
│  [💾 Save Template]  [↩ Revert Changes]  [📧 Send Test Email]      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Template selector dropdown (initial, followup_1, followup_2, followup_3)
- Split view: HTML editor (left) and rendered preview (right)
- Live preview updates as you type
- Placeholder insertion buttons
- Preview with real contact data (dropdown to select contact)
- Send test email to yourself
- Syntax highlighting for HTML (optional enhancement)

---

### 5. Logs Frame

**Purpose:** View activity history and debug issues

```
┌─────────────────────────────────────────────────────────────────────┐
│  LOGS                                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Log file: sequence.log    Size: 45 KB    [📂 Open Folder] [🗑 Clear]│
│                                                                     │
│  Filter: [All Levels  ▼]  Date: [Today      ▼]  [🔍 __________]    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 2026-01-17 14:32:15 │ INFO    │ Reply detected: jean@acme   │   │
│  │ 2026-01-17 14:32:14 │ INFO    │ Checking inbox for replies  │   │
│  │ 2026-01-17 14:30:22 │ INFO    │ Follow-up #2 sent: marie@   │   │
│  │ 2026-01-17 14:30:17 │ INFO    │ Follow-up #1 sent: pierre@  │   │
│  │ 2026-01-17 14:30:12 │ INFO    │ Starting follow-up cycle    │   │
│  │ 2026-01-17 10:00:45 │ WARNING │ Skipped: invalid@bad (no @) │   │
│  │ 2026-01-17 10:00:30 │ INFO    │ Initial email sent: louis@  │   │
│  │ 2026-01-17 10:00:25 │ INFO    │ Initial email sent: claire@ │   │
│  │ 2026-01-17 10:00:20 │ INFO    │ Initial email sent: jean@   │   │
│  │ 2026-01-17 10:00:15 │ INFO    │ Starting sequence: seq_2026 │   │
│  │ 2026-01-17 10:00:10 │ INFO    │ Loaded 20 pending contacts  │   │
│  │ 2026-01-17 10:00:05 │ INFO    │ Outlook connection: OK      │   │
│  │ 2026-01-17 09:45:00 │ INFO    │ Imported 3 contacts from CSV│   │
│  │                     │         │                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                     [Auto-scroll ☑] │
│                                                                     │
│  LOG STATISTICS                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Today: 45 entries │ Errors: 0 │ Warnings: 2 │ Emails: 12   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time log display with auto-scroll
- Level filter (DEBUG, INFO, WARNING, ERROR)
- Date filter (Today, Last 7 days, All)
- Text search within logs
- Color coding by level (INFO=white, WARNING=yellow, ERROR=red)
- Statistics summary
- Open logs folder in Explorer
- Clear log file option

---

### 6. Settings Frame

**Purpose:** Configure application paths and behavior

```
┌─────────────────────────────────────────────────────────────────────┐
│  SETTINGS                                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PATHS                                                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Project folder:                                             │   │
│  │  [C:\email-sequence                              ] [Browse]  │   │
│  │                                                              │   │
│  │  Python executable:                                          │   │
│  │  [python                                         ] [Browse]  │   │
│  │                                                              │   │
│  │  Contacts file (relative to project):                        │   │
│  │  [contacts.xlsx                                  ] [Browse]  │   │
│  │                                                              │   │
│  │  Templates folder (relative to project):                     │   │
│  │  [templates                                      ] [Browse]  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  APPEARANCE                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Theme:        [● Dark  ○ Light  ○ System]                   │   │
│  │  Color scheme: [Blue           ▼]                            │   │
│  │  Language:     [English        ▼]                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  EMAIL SETTINGS                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Sender name:        [Jean-François                     ]    │   │
│  │  Default subject:    [Partnership Opportunity - ISIT    ]    │   │
│  │  Delay between sends: [5    ] seconds                        │   │
│  │  Inbox scan depth:    [30   ] days                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  BEHAVIOR                                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ☑ Confirm before sending emails                             │   │
│  │  ☑ Show Windows notifications                                │   │
│  │  ☑ Minimize to system tray                                   │   │
│  │  ☑ Start minimized                                           │   │
│  │  ☐ Launch at Windows startup                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  OUTLOOK CONNECTION                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Status: ● Connected to Outlook                              │   │
│  │  Account: jf.example@isit.fr                                │   │
│  │  [Test Connection]  [Reconnect]                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  [💾 Save Settings]  [↩ Reset to Defaults]  [📤 Export Config]     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- All paths configurable with browse dialogs
- Theme switching (applies immediately)
- Email settings sync with config.yaml
- Outlook connection test
- Export full configuration (for backup/sharing)
- Validate paths on save (show error if invalid)

---

## Class Specifications (GUI)

### MainApp (gui/app.py)

```python
import customtkinter as ctk
from typing import Optional

class MainApp(ctk.CTk):
    """Main application window with sidebar navigation."""
    
    def __init__(self, config_path: str = "gui_config.yaml"):
        """
        Initialize main window.
        - Load GUI configuration
        - Set theme and appearance
        - Create sidebar navigation
        - Create content frame container
        - Initialize status bar
        - Load dashboard frame by default
        """
        pass
    
    def create_sidebar(self) -> None:
        """
        Create left sidebar with navigation buttons.
        Buttons: Dashboard, Contacts, Sequence, Templates, Logs, Settings
        Highlight active button.
        """
        pass
    
    def navigate_to(self, frame_name: str) -> None:
        """
        Switch content area to specified frame.
        Destroy current frame, instantiate new one.
        Update sidebar button highlighting.
        """
        pass
    
    def update_status_bar(
        self, 
        message: str, 
        outlook_status: bool,
        last_sync: Optional[str] = None
    ) -> None:
        """Update bottom status bar with current state."""
        pass
    
    def show_notification(self, title: str, message: str) -> None:
        """Show Windows toast notification if enabled."""
        pass
    
    def on_close(self) -> None:
        """
        Handle window close.
        If minimize_to_tray enabled, minimize instead of exit.
        Otherwise, confirm and exit.
        """
        pass
```

### DashboardFrame (gui/frames/dashboard.py)

```python
class DashboardFrame(ctk.CTkFrame):
    """Dashboard with metrics, quick actions, and activity feed."""
    
    def __init__(self, parent, sequence_engine: SequenceEngine):
        """Initialize dashboard components."""
        pass
    
    def create_metric_cards(self) -> None:
        """Create top row of metric cards (pending, sent, replied, rate)."""
        pass
    
    def create_quick_actions(self) -> None:
        """Create quick action buttons with callbacks."""
        pass
    
    def create_activity_feed(self) -> None:
        """Create scrollable recent activity list."""
        pass
    
    def refresh_data(self) -> None:
        """
        Reload all metrics and activity from SequenceEngine.
        Called on init and periodically (auto_refresh_seconds).
        """
        pass
    
    def on_start_sequence(self) -> None:
        """Handle Start Sequence button click with confirmation."""
        pass
    
    def on_check_replies(self) -> None:
        """Handle Check Replies button click, show results."""
        pass
    
    def on_send_followups(self) -> None:
        """Handle Send Follow-ups button click with confirmation."""
        pass
```

### ContactsFrame (gui/frames/contacts.py)

```python
class ContactsFrame(ctk.CTkFrame):
    """Contact management with table and detail panel."""
    
    def __init__(self, parent, contact_tracker: ContactTracker):
        pass
    
    def create_toolbar(self) -> None:
        """Add, Import, Export, Delete buttons and search/filter."""
        pass
    
    def create_contact_table(self) -> None:
        """Scrollable table with sortable columns."""
        pass
    
    def create_detail_panel(self) -> None:
        """Editable detail form for selected contact."""
        pass
    
    def load_contacts(self, filter_status: str = None, search: str = None) -> None:
        """Load contacts into table with optional filters."""
        pass
    
    def on_row_select(self, email: str) -> None:
        """Populate detail panel with selected contact."""
        pass
    
    def on_import_csv(self) -> None:
        """
        Open file dialog, show column mapping dialog, import contacts.
        Mapping dialog: CSV column → System field (dropdown).
        """
        pass
    
    def on_save_contact(self) -> None:
        """Save detail panel changes to ContactTracker."""
        pass
```

### SequenceFrame (gui/frames/sequence.py)

```python
class SequenceFrame(ctk.CTkFrame):
    """Sequence control and scheduling configuration."""
    
    def __init__(self, parent, sequence_engine: SequenceEngine, config: Config):
        pass
    
    def create_status_section(self) -> None:
        """Current sequence info and progress bar."""
        pass
    
    def create_action_buttons(self) -> None:
        """Start, Pause, Stop buttons."""
        pass
    
    def create_manual_operations(self) -> None:
        """Check replies, send follow-ups, run cycle buttons."""
        pass
    
    def create_scheduling_section(self) -> None:
        """Auto-cycle toggle, interval, active hours, days."""
        pass
    
    def create_timing_section(self) -> None:
        """Follow-up delay configuration."""
        pass
    
    def update_task_scheduler(self) -> None:
        """
        Create or update Windows Task Scheduler task.
        Uses schtasks.exe or PowerShell commands.
        """
        pass
    
    def run_operation_async(self, operation: str) -> None:
        """
        Run check_replies/send_followups/cycle in background thread.
        Show progress indicator, update UI on completion.
        """
        pass
```

### TemplatesFrame (gui/frames/templates.py)

```python
class TemplatesFrame(ctk.CTkFrame):
    """Template editor with live preview."""
    
    def __init__(self, parent, template_engine: TemplateEngine, contact_tracker: ContactTracker):
        pass
    
    def create_template_selector(self) -> None:
        """Dropdown to select template, new/delete buttons."""
        pass
    
    def create_editor_preview(self) -> None:
        """Split pane: HTML editor left, rendered preview right."""
        pass
    
    def create_placeholder_buttons(self) -> None:
        """Clickable placeholder tags that insert into editor."""
        pass
    
    def on_template_select(self, template_name: str) -> None:
        """Load template into editor."""
        pass
    
    def on_editor_change(self, event) -> None:
        """Update preview pane with rendered template (debounced)."""
        pass
    
    def on_preview_contact_change(self, email: str) -> None:
        """Re-render preview with selected contact's data."""
        pass
    
    def on_save(self) -> None:
        """Save editor content to template file."""
        pass
    
    def on_send_test(self) -> None:
        """Send test email to current user's address."""
        pass
```

---

## Dialogs

### ConfirmationDialog

```python
class ConfirmationDialog(ctk.CTkToplevel):
    """Modal dialog for confirming destructive actions."""
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        danger: bool = False  # Red confirm button if True
    ):
        pass
    
    def get_result(self) -> bool:
        """Show dialog and return True if confirmed."""
        pass
```

### CSVImportDialog

```python
class CSVImportDialog(ctk.CTkToplevel):
    """Column mapping dialog for CSV import."""
    
    def __init__(self, parent, csv_columns: list[str], system_fields: list[str]):
        """
        Show mapping interface:
        CSV Column    →    System Field
        [Name       ] →    [first_name  ▼]
        [Surname    ] →    [last_name   ▼]
        [E-mail     ] →    [email       ▼]
        ...
        """
        pass
    
    def get_mapping(self) -> dict[str, str] | None:
        """Return {csv_col: system_field} or None if cancelled."""
        pass
```

### ProgressDialog

```python
class ProgressDialog(ctk.CTkToplevel):
    """Non-blocking progress dialog for long operations."""
    
    def __init__(self, parent, title: str, total: int):
        pass
    
    def update(self, current: int, message: str) -> None:
        """Update progress bar and message."""
        pass
    
    def close(self) -> None:
        """Close dialog."""
        pass
```

---

## Implementation Order for Claude Code (GUI)

1. **gui_config.yaml** - Configuration file handling
2. **app.py** - Main window with sidebar (empty frames)
3. **settings.py** - Settings frame (to configure paths early)
4. **dashboard.py** - Dashboard with metrics and quick actions
5. **contacts.py** - Contact table and detail panel
6. **sequence.py** - Sequence control
7. **templates.py** - Template editor
8. **logs.py** - Log viewer
9. **Dialogs** - Confirmation, CSV import, Progress
10. **System tray** - Minimize to tray functionality
11. **Task Scheduler integration** - Auto-update scheduled tasks
12. **Packaging** - PyInstaller spec for .exe

---

## Entry Point

**run_gui.py:**
```python
import customtkinter as ctk
from gui.app import MainApp

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    main()
```

---

## Packaging as .exe

**pyinstaller.spec** (create after development):
```bash
pyinstaller --onefile --windowed --icon=gui/assets/icon.ico --name="EmailSequence" run_gui.py
```

This creates a single `EmailSequence.exe` that can be distributed without Python installation.
