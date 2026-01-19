# Email Sequence System - Complete Technical Specification v2.1

**Version:** 2.1 - Multi-Campaign Architecture + GUI + Smart Scheduling  
**Target Platform:** Windows 11  
**Python Version:** 3.10+  
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Configuration Files](#configuration-files)
5. [Data Models](#data-models)
6. [Core Classes](#core-classes)
7. [GUI Application](#gui-application)
8. [Smart Scheduling](#smart-scheduling)
9. [CLI Interface](#cli-interface)
10. [Error Handling & Logging](#error-handling--logging)
11. [Implementation Order](#implementation-order)
12. [Testing Requirements](#testing-requirements)
13. [Migration Guide](#migration-guide)

---

## Overview

### Purpose

Build a Python-based email sequence automation system that manages multiple marketing campaigns, each containing multiple email sequences. The system integrates with Microsoft Outlook to send personalized emails, track replies, and automatically send follow-ups. Includes both CLI and GUI interfaces with smart scheduling capabilities.

### Key Features

- **Multi-Campaign Management:** Organize sequences into campaigns
- **Hierarchical Structure:** Campaign → Sequences → Contacts
- **Outlook Integration:** Send emails via desktop Outlook (COM automation)
- **Automatic Reply Tracking:** Scan inbox and update contact status
- **Flexible Follow-ups:** Configurable timing per sequence
- **Template Engine:** Personalized HTML email templates
- **Excel-Based Storage:** Simple, editable contact databases
- **GUI Application:** Modern CustomTkinter interface for visual management
- **Smart Scheduling:** AI-powered optimal send time detection
- **Comprehensive Logging:** Campaign-specific logs for debugging

### Target Users

- Business development managers
- Sales teams
- Marketing professionals
- 1-100 contacts per sequence
- Single user, local execution

---

## System Architecture

### Hierarchy

```
Application
    │
    ├── Campaign 1 (e.g., "Partnership Outreach 2026")
    │   │
    │   ├── Templates (shared across sequences)
    │   │   ├── initial.html
    │   │   ├── followup_1.html
    │   │   ├── followup_2.html
    │   │   └── followup_3.html
    │   │
    │   ├── Sequence 1 (e.g., "Automotive Industry")
    │   │   └── Contacts (25)
    │   │
    │   ├── Sequence 2 (e.g., "Aerospace Partners")
    │   │   └── Contacts (30)
    │   │
    │   └── Sequence 3 (e.g., "Medical Devices")
    │       └── Contacts (20)
    │
    └── Campaign 2 (e.g., "Product Launch Q1")
        ├── Templates
        ├── Sequence 1
        └── Sequence 2
```

### Workflow

1. **Create Campaign** → Define campaign name, description, email settings
2. **Create Sequence(s)** → Add sequences to campaign with specific contacts
3. **Import Contacts** → Add contacts to each sequence via CSV or manual entry
4. **Configure Smart Scheduling** → Enable optimal send times (optional)
5. **Start Sequence** → Send initial emails to all pending contacts
6. **Auto-Check Replies** → System scans inbox periodically
7. **Send Follow-ups** → Automated follow-ups based on timing rules and smart scheduling
8. **Track Results** → View statistics at sequence and campaign level via CLI or GUI

---

## Project Structure

```
email-sequence/
├── config.yaml                  # Global application configuration
├── campaigns/                   # All campaigns stored here
│   ├── campaign_001_partnership_outreach/
│   │   ├── campaign_config.yaml
│   │   ├── sequences.xlsx       # Registry of sequences in campaign
│   │   ├── templates/
│   │   │   ├── initial.html
│   │   │   ├── followup_1.html
│   │   │   ├── followup_2.html
│   │   │   └── followup_3.html
│   │   └── sequences/
│   │       ├── seq_20260117_automotive/
│   │       │   ├── contacts.xlsx
│   │       │   └── sequence_config.yaml
│   │       └── seq_20260118_aerospace/
│   │           ├── contacts.xlsx
│   │           └── sequence_config.yaml
│   └── campaign_002_product_launch/
│       ├── campaign_config.yaml
│       ├── sequences.xlsx
│       ├── templates/
│       └── sequences/
├── data/
│   └── scheduling_data.db       # SQLite database for smart scheduling
├── logs/
│   ├── app.log                  # Application-level logs
│   └── campaigns/               # Campaign-specific logs
│       ├── campaign_001.log
│       └── campaign_002.log
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── campaign_manager.py      # Campaign CRUD operations
│   ├── sequence_manager.py      # Sequence CRUD operations
│   ├── contact_tracker.py       # Contact management per sequence
│   ├── outlook_manager.py       # Outlook COM automation
│   ├── sequence_engine.py       # Email sending orchestration
│   ├── template_engine.py       # Email personalization
│   └── smart_scheduler.py       # Smart scheduling engine
├── gui/
│   ├── __init__.py
│   ├── app.py                   # Main GUI application
│   ├── frames/
│   │   ├── __init__.py
│   │   ├── dashboard.py         # Dashboard/home frame
│   │   ├── campaigns.py         # Campaign management frame
│   │   ├── sequences.py         # Sequence management frame
│   │   ├── contacts.py          # Contact management frame
│   │   ├── templates.py         # Template editor frame
│   │   ├── scheduler.py         # Smart scheduling configuration
│   │   ├── logs.py              # Log viewer frame
│   │   └── settings.py          # Settings frame
│   ├── components/
│   │   ├── __init__.py
│   │   ├── contact_table.py     # Reusable contact table widget
│   │   ├── status_badge.py      # Status indicator widget
│   │   ├── progress_card.py     # Metric card widget
│   │   └── dialogs.py           # Common dialogs
│   └── assets/
│       ├── icon.ico             # App icon
│       └── logo.png             # Company logo
├── gui_config.yaml              # GUI-specific configuration
├── main.py                      # CLI entry point
├── run_gui.py                   # GUI entry point
├── requirements.txt
└── README.md
```

---

## Configuration Files

### 1. Global Configuration (config.yaml)

Located at project root. Contains application-wide settings.

```yaml
# Global application settings
app:
  campaigns_folder: "campaigns"
  logs_folder: "logs"
  data_folder: "data"
  default_campaign: null  # Last used campaign ID (auto-updated)

# Default email settings (can be overridden per campaign)
email_defaults:
  sender_name: "Jean-François"
  send_delay_seconds: 5        # Pause between emails to avoid spam flags
  inbox_scan_days: 30          # How far back to scan for replies
  match_by: "conversation"     # "conversation" or "subject"

# Default sequence timing (can be overridden per sequence)
sequence_defaults:
  followup_delays: [3, 7, 14]  # Days after initial email
  max_followups: 3

# Smart scheduling settings
smart_scheduling:
  enabled: false               # Enable smart scheduling globally
  analysis_window_days: 90     # Days of history to analyze
  timezone: "Europe/Paris"     # User's timezone
  business_hours_start: "09:00"
  business_hours_end: "18:00"
  preferred_days: ["Mon", "Tue", "Wed", "Thu", "Fri"]  # Days to send
  avoid_holidays: true
  min_delay_hours: 1           # Minimum delay before sending scheduled email
  max_delay_hours: 48          # Maximum delay for scheduling

# Safety settings
safety:
  dry_run: false               # If true, display emails but don't send
  confirm_before_send: true    # Ask for confirmation before sending
  
# Logging
logging:
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(levelname)s - %(message)s"
```

### 2. Campaign Configuration (campaign_config.yaml)

Located at `campaigns/campaign_XXX/campaign_config.yaml`

```yaml
campaign:
  id: "campaign_001"
  name: "Partnership Outreach 2026"
  description: "Outreach to potential partners in automotive and aerospace sectors"
  created_date: "2026-01-17T10:00:00"
  status: "active"  # active, paused, completed, archived
  
# Campaign-level email settings (override global defaults)
email:
  sender_name: "Jean-François"
  default_subject: "Partnership Opportunity - ISIT"
  send_delay_seconds: 5
  inbox_scan_days: 30
  
# Campaign-level sequence defaults
sequence_defaults:
  followup_delays: [3, 7, 14]
  max_followups: 3
  
# Campaign-level smart scheduling
smart_scheduling:
  enabled: true                # Override global setting
  preferred_send_times:        # Optimal times based on industry/target
    - "09:00"
    - "14:00"
  
# Folder locations (relative to campaign folder)
folders:
  templates: "templates"
  sequences: "sequences"
  sequences_registry: "sequences.xlsx"
```

### 3. Sequence Configuration (sequence_config.yaml)

Located at `campaigns/campaign_XXX/sequences/seq_XXX/sequence_config.yaml`

```yaml
sequence:
  id: "seq_20260117_automotive"
  name: "Automotive Industry Contacts"
  campaign_id: "campaign_001"
  created_date: "2026-01-17T10:00:00"
  started_date: null            # Set when first email sent
  completed_date: null          # Set when sequence completes
  status: "pending"             # pending, active, paused, completed
  
# Sequence-specific timing (overrides campaign defaults)
timing:
  followup_delays: [3, 7, 14]
  max_followups: 3
  
# Smart scheduling for this sequence
smart_scheduling:
  enabled: true
  target_timezone: "Europe/Paris"  # Recipient's timezone if known
  
# Sequence-specific email settings
email:
  subject: "Partnership Opportunity - ISIT Automotive Solutions"
  
# Templates to use (from campaign templates folder)
templates:
  initial: "initial.html"
  followup_1: "followup_1.html"
  followup_2: "followup_2.html"
  followup_3: "followup_3.html"

# Contacts file
contacts_file: "contacts.xlsx"

# Statistics (auto-updated by system)
stats:
  total_contacts: 0
  pending: 0
  sent: 0
  replied: 0
  bounced: 0
  opted_out: 0
  completed: 0
  reply_rate: 0.0
  last_updated: null
```

### 4. GUI Configuration (gui_config.yaml)

Located at project root. GUI-specific settings.

```yaml
# Paths (configurable by user)
paths:
  project_folder: "."
  python_executable: "python"

# GUI appearance
appearance:
  theme: "dark"                # "dark", "light", or "system"
  color_scheme: "blue"         # "blue", "green", "dark-blue"
  window_width: 1400
  window_height: 900
  sidebar_width: 220

# Behavior
behavior:
  auto_refresh_seconds: 30     # Dashboard auto-refresh interval
  confirm_before_send: true    # Show confirmation dialog before sending
  show_notifications: true     # Windows toast notifications
  minimize_to_tray: false      # Minimize to system tray
  start_minimized: false       # Start application minimized

# Recent files (auto-populated)
recent_campaigns: []
```

---

## Data Models

### 1. Sequences Registry (sequences.xlsx)

Located at `campaigns/campaign_XXX/sequences.xlsx`

Tracks all sequences within a campaign.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| sequence_id | string | Unique sequence identifier | seq_20260117_automotive |
| name | string | Human-readable name | Automotive Industry |
| status | string | pending, active, paused, completed | active |
| created_date | datetime | When sequence was created | 2026-01-17 10:00:00 |
| started_date | datetime | When first email sent | 2026-01-17 10:30:00 |
| completed_date | datetime | When sequence finished | 2026-01-25 16:00:00 |
| total_contacts | integer | Number of contacts | 25 |
| pending_count | integer | Contacts not yet contacted | 5 |
| sent_count | integer | Initial emails sent | 15 |
| replied_count | integer | Contacts who replied | 5 |
| bounced_count | integer | Failed emails | 0 |
| reply_rate | float | Percentage replied | 20.0 |
| smart_scheduling | boolean | Using smart scheduling | True |
| notes | string | Free-form notes | Q1 automotive targets |

### 2. Contacts (contacts.xlsx)

Located at `campaigns/campaign_XXX/sequences/seq_XXX/contacts.xlsx`

Stores contact information and tracking data for a specific sequence.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| sequence_id | string | Parent sequence ID | seq_20260117_automotive |
| title | string | Salutation | Mr, Ms, Dr, Prof |
| first_name | string | First name | Jean |
| last_name | string | Last name | Dupont |
| email | string | Email address (unique) | jean.dupont@acme.com |
| company | string | Company name | Acme Corp |
| industry | string | Industry sector | Automotive |
| timezone | string | Contact's timezone (for smart scheduling) | Europe/Paris |
| status | string | Current state (see below) | sent |
| initial_sent_date | datetime | When first email sent | 2026-01-17 10:30:00 |
| scheduled_send_time | datetime | Smart-scheduled send time | 2026-01-17 14:00:00 |
| last_contact_date | datetime | When last email sent | 2026-01-20 14:00:00 |
| followup_count | integer | Number of follow-ups sent (0-3) | 1 |
| conversation_id | string | Outlook ConversationTopic | Partnership Opportunity |
| replied_date | datetime | When reply received | 2026-01-19 16:45:00 |
| notes | string | Free-form notes | Met at trade show 2025 |

**Status Values:**

- `pending` - Not yet contacted in this sequence
- `scheduled` - Smart-scheduled for future send
- `sent` - Initial email sent, awaiting reply
- `followup_1` - First follow-up sent
- `followup_2` - Second follow-up sent
- `followup_3` - Third follow-up sent
- `replied` - Contact replied (sequence complete for them)
- `bounced` - Email bounced/failed to send
- `opted_out` - Contact requested removal
- `completed` - Max follow-ups reached, no reply

### 3. Scheduling Data (scheduling_data.db)

SQLite database storing smart scheduling analytics.

**Table: reply_patterns**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique ID |
| campaign_id | TEXT | Campaign identifier |
| sequence_id | TEXT | Sequence identifier |
| contact_email | TEXT | Contact email |
| sent_datetime | DATETIME | When email was sent |
| sent_day_of_week | INTEGER | 0=Monday, 6=Sunday |
| sent_hour | INTEGER | Hour of day (0-23) |
| replied_datetime | DATETIME | When reply received (if any) |
| time_to_reply_hours | FLOAT | Hours between send and reply |
| created_at | DATETIME | Record creation time |

**Table: optimal_send_times**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique ID |
| industry | TEXT | Industry sector |
| day_of_week | INTEGER | 0=Monday, 6=Sunday |
| hour | INTEGER | Hour of day (0-23) |
| reply_rate | FLOAT | Historical reply rate (0-100) |
| sample_size | INTEGER | Number of emails sent |
| last_updated | DATETIME | Last calculation time |

---

## Core Classes

### 1. Config (src/config.py)

Manages configuration loading and validation.

```python
"""Configuration management for email sequence system."""

import yaml
from pathlib import Path
from typing import Any, Optional

class Config:
    """Load and manage application configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Load global configuration from YAML file.
        Create with defaults if file doesn't exist.
        
        Args:
            config_path: Path to config.yaml
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config_path = Path(config_path)
        self.data = {}
        self._load_config()
        self._validate_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create defaults."""
        if not self.config_path.exists():
            self._create_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = {
            'app': {
                'campaigns_folder': 'campaigns',
                'logs_folder': 'logs',
                'data_folder': 'data',
                'default_campaign': None
            },
            'email_defaults': {
                'sender_name': 'Your Name',
                'send_delay_seconds': 5,
                'inbox_scan_days': 30,
                'match_by': 'conversation'
            },
            'sequence_defaults': {
                'followup_delays': [3, 7, 14],
                'max_followups': 3
            },
            'smart_scheduling': {
                'enabled': False,
                'analysis_window_days': 90,
                'timezone': 'Europe/Paris',
                'business_hours_start': '09:00',
                'business_hours_end': '18:00',
                'preferred_days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                'avoid_holidays': True,
                'min_delay_hours': 1,
                'max_delay_hours': 48
            },
            'safety': {
                'dry_run': False,
                'confirm_before_send': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            }
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        self.data = default_config
    
    def _validate_config(self) -> None:
        """Validate configuration structure and values."""
        required_sections = ['app', 'email_defaults', 'sequence_defaults', 'safety']
        for section in required_sections:
            if section not in self.data:
                raise ValueError(f"Missing required config section: {section}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Example:
            config.get('email_defaults.sender_name')
        
        Args:
            key: Configuration key (dot-separated path)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (dot-separated path)
            value: Value to set
        """
        keys = key.split('.')
        data = self.data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    def save(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f, default_flow_style=False)
    
    # Convenience properties
    @property
    def campaigns_folder(self) -> Path:
        return Path(self.get('app.campaigns_folder', 'campaigns'))
    
    @property
    def logs_folder(self) -> Path:
        return Path(self.get('app.logs_folder', 'logs'))
    
    @property
    def data_folder(self) -> Path:
        return Path(self.get('app.data_folder', 'data'))
    
    @property
    def sender_name(self) -> str:
        return self.get('email_defaults.sender_name', 'Your Name')
    
    @property
    def send_delay_seconds(self) -> int:
        return self.get('email_defaults.send_delay_seconds', 5)
    
    @property
    def followup_delays(self) -> list:
        return self.get('sequence_defaults.followup_delays', [3, 7, 14])
    
    @property
    def max_followups(self) -> int:
        return self.get('sequence_defaults.max_followups', 3)
    
    @property
    def dry_run(self) -> bool:
        return self.get('safety.dry_run', False)
    
    @property
    def smart_scheduling_enabled(self) -> bool:
        return self.get('smart_scheduling.enabled', False)
```

### 2-6. CampaignManager, SequenceManager, ContactTracker, OutlookManager, TemplateEngine

*[These classes remain exactly as specified in the original specification above. No changes needed.]*

### 7. SmartScheduler (src/smart_scheduler.py)

NEW: Analyzes historical data to determine optimal send times.

```python
"""Smart scheduling engine for optimal email send times."""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from collections import defaultdict

class SmartScheduler:
    """Analyze historical data and schedule emails at optimal times."""
    
    def __init__(self, data_folder: str = "data", config=None):
        """
        Initialize smart scheduler.
        
        Args:
            data_folder: Path to data folder
            config: Config instance
        """
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_folder / "scheduling_data.db"
        self.config = config
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Reply patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reply_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                sequence_id TEXT,
                contact_email TEXT,
                sent_datetime DATETIME,
                sent_day_of_week INTEGER,
                sent_hour INTEGER,
                replied_datetime DATETIME,
                time_to_reply_hours REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Optimal send times table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimal_send_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                industry TEXT,
                day_of_week INTEGER,
                hour INTEGER,
                reply_rate REAL,
                sample_size INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scheduled sends table (pending scheduled emails)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_sends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                sequence_id TEXT,
                contact_email TEXT,
                scheduled_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_send(
        self,
        campaign_id: str,
        sequence_id: str,
        contact_email: str,
        sent_datetime: datetime
    ) -> None:
        """
        Record an email send event.
        
        Args:
            campaign_id: Campaign identifier
            sequence_id: Sequence identifier
            contact_email: Contact email
            sent_datetime: When email was sent
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reply_patterns 
            (campaign_id, sequence_id, contact_email, sent_datetime, 
             sent_day_of_week, sent_hour)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id,
            sequence_id,
            contact_email,
            sent_datetime.isoformat(),
            sent_datetime.weekday(),
            sent_datetime.hour
        ))
        
        conn.commit()
        conn.close()
    
    def record_reply(
        self,
        contact_email: str,
        replied_datetime: datetime
    ) -> None:
        """
        Record a reply event and calculate time to reply.
        
        Args:
            contact_email: Contact email
            replied_datetime: When reply was received
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find the most recent send to this contact
        cursor.execute('''
            SELECT id, sent_datetime
            FROM reply_patterns
            WHERE contact_email = ?
            AND replied_datetime IS NULL
            ORDER BY sent_datetime DESC
            LIMIT 1
        ''', (contact_email,))
        
        result = cursor.fetchone()
        
        if result:
            record_id, sent_datetime_str = result
            sent_datetime = datetime.fromisoformat(sent_datetime_str)
            
            # Calculate time to reply in hours
            time_to_reply = (replied_datetime - sent_datetime).total_seconds() / 3600
            
            cursor.execute('''
                UPDATE reply_patterns
                SET replied_datetime = ?,
                    time_to_reply_hours = ?
                WHERE id = ?
            ''', (replied_datetime.isoformat(), time_to_reply, record_id))
            
            conn.commit()
        
        conn.close()
    
    def analyze_optimal_times(
        self,
        industry: Optional[str] = None,
        min_sample_size: int = 5
    ) -> Dict[Tuple[int, int], float]:
        """
        Analyze historical data to find optimal send times.
        
        Args:
            industry: Filter by industry (optional)
            min_sample_size: Minimum emails sent for valid analysis
            
        Returns:
            Dict mapping (day_of_week, hour) to reply_rate
        """
        conn = sqlite3.connect(self.db_path)
        
        # Query reply patterns
        query = '''
            SELECT sent_day_of_week, sent_hour,
                   COUNT(*) as total,
                   SUM(CASE WHEN replied_datetime IS NOT NULL THEN 1 ELSE 0 END) as replied
            FROM reply_patterns
            WHERE sent_datetime >= datetime('now', '-90 days')
        '''
        
        # TODO: Add industry filtering when we track industry in reply_patterns
        query += '''
            GROUP BY sent_day_of_week, sent_hour
            HAVING total >= ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(min_sample_size,))
        conn.close()
        
        if df.empty:
            return {}
        
        # Calculate reply rates
        df['reply_rate'] = (df['replied'] / df['total']) * 100
        
        # Convert to dict
        optimal_times = {}
        for _, row in df.iterrows():
            key = (int(row['sent_day_of_week']), int(row['sent_hour']))
            optimal_times[key] = float(row['reply_rate'])
        
        return optimal_times
    
    def get_optimal_send_time(
        self,
        contact: Dict,
        earliest_time: Optional[datetime] = None,
        business_hours_only: bool = True
    ) -> datetime:
        """
        Calculate optimal send time for a contact.
        
        Args:
            contact: Contact dict with timezone info
            earliest_time: Earliest possible send time
            business_hours_only: Only suggest business hours
            
        Returns:
            Optimal send datetime
        """
        if earliest_time is None:
            earliest_time = datetime.now()
        
        # Get configuration
        min_delay_hours = self.config.get('smart_scheduling.min_delay_hours', 1) if self.config else 1
        max_delay_hours = self.config.get('smart_scheduling.max_delay_hours', 48) if self.config else 48
        business_start = self.config.get('smart_scheduling.business_hours_start', '09:00') if self.config else '09:00'
        business_end = self.config.get('smart_scheduling.business_hours_end', '18:00') if self.config else '18:00'
        preferred_days = self.config.get('smart_scheduling.preferred_days', ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']) if self.config else ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        
        # Convert day names to numbers
        day_name_to_num = {
            'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
        }
        preferred_day_nums = [day_name_to_num[day] for day in preferred_days if day in day_name_to_num]
        
        # Parse business hours
        start_hour = int(business_start.split(':')[0])
        end_hour = int(business_end.split(':')[0])
        
        # Get optimal times from analysis
        industry = contact.get('industry', None)
        optimal_times = self.analyze_optimal_times(industry=industry)
        
        # If no historical data, use default best practices
        if not optimal_times:
            optimal_times = self._get_default_optimal_times()
        
        # Find best time within constraints
        latest_time = earliest_time + timedelta(hours=max_delay_hours)
        current_check = earliest_time + timedelta(hours=min_delay_hours)
        
        best_time = None
        best_score = -1
        
        while current_check <= latest_time:
            # Check if this time meets constraints
            if business_hours_only:
                if current_check.hour < start_hour or current_check.hour >= end_hour:
                    current_check += timedelta(hours=1)
                    continue
            
            if current_check.weekday() not in preferred_day_nums:
                current_check += timedelta(hours=1)
                continue
            
            # Get score for this time
            key = (current_check.weekday(), current_check.hour)
            score = optimal_times.get(key, 0)
            
            if score > best_score:
                best_score = score
                best_time = current_check
            
            current_check += timedelta(hours=1)
        
        # If no optimal time found, use next business day at 9 AM
        if best_time is None:
            best_time = earliest_time + timedelta(hours=min_delay_hours)
            while best_time.weekday() not in preferred_day_nums or best_time.hour < start_hour:
                best_time += timedelta(hours=1)
            best_time = best_time.replace(hour=start_hour, minute=0, second=0)
        
        return best_time
    
    def _get_default_optimal_times(self) -> Dict[Tuple[int, int], float]:
        """
        Get default optimal times based on best practices.
        
        Returns:
            Dict mapping (day_of_week, hour) to reply_rate estimate
        """
        # Default best practices (approximate reply rates)
        optimal_times = {}
        
        # Weekdays 9-10 AM (good)
        for day in range(5):  # Monday-Friday
            optimal_times[(day, 9)] = 15.0
            optimal_times[(day, 10)] = 14.0
        
        # Weekdays 2-3 PM (best)
        for day in range(5):
            optimal_times[(day, 14)] = 18.0
            optimal_times[(day, 15)] = 16.0
        
        # Weekdays 4-5 PM (good)
        for day in range(5):
            optimal_times[(day, 16)] = 13.0
            optimal_times[(day, 17)] = 12.0
        
        # Other business hours (average)
        for day in range(5):
            for hour in [11, 12, 13]:
                optimal_times[(day, hour)] = 10.0
        
        return optimal_times
    
    def schedule_email(
        self,
        campaign_id: str,
        sequence_id: str,
        contact: Dict
    ) -> datetime:
        """
        Schedule an email for optimal send time.
        
        Args:
            campaign_id: Campaign identifier
            sequence_id: Sequence identifier
            contact: Contact dict
            
        Returns:
            Scheduled send time
        """
        optimal_time = self.get_optimal_send_time(contact)
        
        # Record in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_sends
            (campaign_id, sequence_id, contact_email, scheduled_time)
            VALUES (?, ?, ?, ?)
        ''', (campaign_id, sequence_id, contact['email'], optimal_time.isoformat()))
        
        conn.commit()
        conn.close()
        
        return optimal_time
    
    def get_pending_scheduled_sends(self) -> List[Dict]:
        """
        Get all pending scheduled sends that are ready to send.
        
        Returns:
            List of scheduled send dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            SELECT id, campaign_id, sequence_id, contact_email, scheduled_time
            FROM scheduled_sends
            WHERE status = 'pending'
            AND scheduled_time <= ?
            ORDER BY scheduled_time
        ''', (now,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'campaign_id': row[1],
                'sequence_id': row[2],
                'contact_email': row[3],
                'scheduled_time': datetime.fromisoformat(row[4])
            })
        
        return results
    
    def mark_scheduled_send_complete(self, scheduled_send_id: int) -> None:
        """
        Mark a scheduled send as complete.
        
        Args:
            scheduled_send_id: Scheduled send ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_sends
            SET status = 'sent'
            WHERE id = ?
        ''', (scheduled_send_id,))
        
        conn.commit()
        conn.close()
    
    def get_scheduling_report(
        self,
        campaign_id: Optional[str] = None,
        days_back: int = 30
    ) -> Dict:
        """
        Generate scheduling performance report.
        
        Args:
            campaign_id: Filter by campaign (optional)
            days_back: Days of history to analyze
            
        Returns:
            Report dict with statistics
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                COUNT(*) as total_emails,
                SUM(CASE WHEN replied_datetime IS NOT NULL THEN 1 ELSE 0 END) as total_replies,
                AVG(time_to_reply_hours) as avg_reply_time_hours,
                MIN(time_to_reply_hours) as min_reply_time_hours,
                MAX(time_to_reply_hours) as max_reply_time_hours
            FROM reply_patterns
            WHERE sent_datetime >= datetime('now', '-' || ? || ' days')
        '''
        
        params = [days_back]
        
        if campaign_id:
            query += ' AND campaign_id = ?'
            params.append(campaign_id)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty or df['total_emails'].iloc[0] == 0:
            return {
                'total_emails': 0,
                'total_replies': 0,
                'reply_rate': 0.0,
                'avg_reply_time_hours': 0.0,
                'best_day': None,
                'best_hour': None
            }
        
        row = df.iloc[0]
        reply_rate = (row['total_replies'] / row['total_emails'] * 100) if row['total_emails'] > 0 else 0.0
        
        # Find best day and hour
        optimal_times = self.analyze_optimal_times()
        best_time = max(optimal_times.items(), key=lambda x: x[1]) if optimal_times else ((0, 9), 0)
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'total_emails': int(row['total_emails']),
            'total_replies': int(row['total_replies']),
            'reply_rate': round(reply_rate, 2),
            'avg_reply_time_hours': round(row['avg_reply_time_hours'], 2) if pd.notna(row['avg_reply_time_hours']) else 0.0,
            'min_reply_time_hours': round(row['min_reply_time_hours'], 2) if pd.notna(row['min_reply_time_hours']) else 0.0,
            'max_reply_time_hours': round(row['max_reply_time_hours'], 2) if pd.notna(row['max_reply_time_hours']) else 0.0,
            'best_day': day_names[best_time[0][0]],
            'best_hour': f"{best_time[0][1]:02d}:00",
            'best_reply_rate': round(best_time[1], 2)
        }
```

### 8. SequenceEngine (src/sequence_engine.py) - UPDATED

Modified to integrate smart scheduling.

```python
"""Sequence orchestration engine with smart scheduling."""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class SequenceEngine:
    """Orchestrate email sequences within a campaign."""
    
    def __init__(self, sequence_id: str, sequence_manager, config):
        """
        Initialize for specific sequence.
        
        Args:
            sequence_id: Sequence identifier
            sequence_manager: SequenceManager instance
            config: Config instance
        """
        self.sequence_id = sequence_id
        self.sequence_manager = sequence_manager
        self.config = config
        
        # Load sequence and campaign data
        self.sequence = sequence_manager.get_sequence(sequence_id)
        self.campaign = sequence_manager.campaign
        
        # Initialize components
        from .contact_tracker import ContactTracker
        from .outlook_manager import OutlookManager
        from .template_engine import TemplateEngine
        from .smart_scheduler import SmartScheduler
        
        self.contact_tracker = ContactTracker(sequence_id, sequence_manager)
        self.outlook_manager = OutlookManager()
        
        # Templates are in campaign folder
        templates_folder = self.campaign['folder_path'] / "templates"
        self.template_engine = TemplateEngine(str(templates_folder))
        
        # Smart scheduler
        self.smart_scheduler = SmartScheduler(str(config.data_folder), config)
        
        # Check if smart scheduling is enabled for this sequence
        self.smart_scheduling_enabled = (
            self.config.smart_scheduling_enabled and
            self.sequence['config'].get('smart_scheduling', {}).get('enabled', False)
        )
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging to campaign-specific log file."""
        logs_folder = Path(self.config.logs_folder) / "campaigns"
        logs_folder.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_folder / f"{self.campaign['id']}.log"
        
        self.logger = logging.getLogger(f"sequence_{self.sequence_id}")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
    
    def start_sequence(self) -> Dict:
        """
        Send initial emails to all pending contacts.
        Uses smart scheduling if enabled.
        
        Returns:
            Results dict with counts
        """
        self.logger.info(f"Starting sequence: {self.sequence_id}")
        
        # Get pending contacts
        pending_contacts = self.contact_tracker.get_pending_contacts()
        
        if pending_contacts.empty:
            self.logger.info("No pending contacts to process")
            return {'sent': 0, 'scheduled': 0, 'failed': 0, 'errors': []}
        
        sent = 0
        scheduled = 0
        failed = 0
        errors = []
        
        # Get email settings
        sender_name = self.campaign['config']['email']['sender_name']
        subject = self.sequence['config']['email']['subject']
        send_delay = self.campaign['config']['email']['send_delay_seconds']
        dry_run = self.config.dry_run
        
        for _, contact in pending_contacts.iterrows():
            try:
                # Determine if we should schedule or send immediately
                if self.smart_scheduling_enabled:
                    # Schedule for optimal time
                    optimal_time = self.smart_scheduler.schedule_email(
                        self.campaign['id'],
                        self.sequence_id,
                        contact.to_dict()
                    )
                    
                    # Update contact status to scheduled
                    self.contact_tracker.update_contact(
                        contact['email'],
                        {
                            'status': 'scheduled',
                            'scheduled_send_time': optimal_time
                        }
                    )
                    scheduled += 1
                    self.logger.info(f"Scheduled email to: {contact['email']} at {optimal_time}")
                    
                else:
                    # Send immediately
                    html_body = self.template_engine.render(
                        'initial',
                        contact.to_dict(),
                        sender_name
                    )
                    
                    result = self.outlook_manager.send_email(
                        to=contact['email'],
                        subject=subject,
                        html_body=html_body,
                        dry_run=dry_run
                    )
                    
                    if result['success']:
                        # Record send in smart scheduler
                        self.smart_scheduler.record_send(
                            self.campaign['id'],
                            self.sequence_id,
                            contact['email'],
                            result['sent_time']
                        )
                        
                        # Update contact status
                        self.contact_tracker.update_contact(
                            contact['email'],
                            {
                                'status': 'sent',
                                'initial_sent_date': result['sent_time'],
                                'last_contact_date': result['sent_time'],
                                'followup_count': 0,
                                'conversation_id': result['conversation_id']
                            }
                        )
                        sent += 1
                        self.logger.info(f"Sent initial email to: {contact['email']}")
                    else:
                        # Mark as bounced
                        self.contact_tracker.update_contact(
                            contact['email'],
                            {'status': 'bounced'}
                        )
                        failed += 1
                        error_msg = f"Failed to send to {contact['email']}: {result['error']}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
                    
                    # Delay between sends
                    if sent + failed < len(pending_contacts):
                        time.sleep(send_delay)
                
            except Exception as e:
                failed += 1
                error_msg = f"Exception sending to {contact['email']}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        # Update sequence status
        if sent > 0 or scheduled > 0:
            self.sequence_manager.update_sequence(
                self.sequence_id,
                {
                    'status': 'active',
                    'started_date': datetime.now().isoformat()
                }
            )
        
        # Update statistics
        self.sequence_manager.update_sequence_stats(self.sequence_id)
        
        self.logger.info(f"Sequence started: {sent} sent, {scheduled} scheduled, {failed} failed")
        
        return {
            'sent': sent,
            'scheduled': scheduled,
            'failed': failed,
            'errors': errors
        }
    
    def process_scheduled_sends(self) -> Dict:
        """
        Process pending scheduled sends that are due.
        
        Returns:
            Results dict with counts
        """
        self.logger.info("Processing scheduled sends")
        
        # Get pending scheduled sends
        pending_sends = self.smart_scheduler.get_pending_scheduled_sends()
        
        # Filter for this sequence
        sequence_sends = [
            send for send in pending_sends
            if send['sequence_id'] == self.sequence_id
        ]
        
        if not sequence_sends:
            return {'sent': 0, 'failed': 0, 'errors': []}
        
        sent = 0
        failed = 0
        errors = []
        
        sender_name = self.campaign['config']['email']['sender_name']
        subject = self.sequence['config']['email']['subject']
        send_delay = self.campaign['config']['email']['send_delay_seconds']
        
        for scheduled_send in sequence_sends:
            try:
                # Get contact
                contact = self.contact_tracker.get_contact_by_email(
                    scheduled_send['contact_email']
                )
                
                if not contact:
                    self.logger.warning(f"Contact not found: {scheduled_send['contact_email']}")
                    continue
                
                # Render email
                html_body = self.template_engine.render(
                    'initial',
                    contact,
                    sender_name
                )
                
                # Send email
                result = self.outlook_manager.send_email(
                    to=contact['email'],
                    subject=subject,
                    html_body=html_body,
                    dry_run=self.config.dry_run
                )
                
                if result['success']:
                    # Record send
                    self.smart_scheduler.record_send(
                        self.campaign['id'],
                        self.sequence_id,
                        contact['email'],
                        result['sent_time']
                    )
                    
                    # Update contact
                    self.contact_tracker.update_contact(
                        contact['email'],
                        {
                            'status': 'sent',
                            'initial_sent_date': result['sent_time'],
                            'last_contact_date': result['sent_time'],
                            'followup_count': 0,
                            'conversation_id': result['conversation_id']
                        }
                    )
                    
                    # Mark scheduled send as complete
                    self.smart_scheduler.mark_scheduled_send_complete(
                        scheduled_send['id']
                    )
                    
                    sent += 1
                    self.logger.info(f"Sent scheduled email to: {contact['email']}")
                else:
                    failed += 1
                    error_msg = f"Failed to send to {contact['email']}: {result['error']}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
                
                time.sleep(send_delay)
                
            except Exception as e:
                failed += 1
                error_msg = f"Exception processing scheduled send: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        # Update statistics
        if sent > 0:
            self.sequence_manager.update_sequence_stats(self.sequence_id)
        
        return {
            'sent': sent,
            'failed': failed,
            'errors': errors
        }
    
    def check_replies(self) -> Dict:
        """
        Scan inbox and update contacts who have replied.
        Records replies in smart scheduler for analysis.
        
        Returns:
            Results dict
        """
        self.logger.info("Checking for replies")
        
        # Get all active contacts
        all_contacts = self.contact_tracker.get_all_contacts()
        active_contacts = all_contacts[
            all_contacts['status'].isin(['sent', 'followup_1', 'followup_2', 'followup_3'])
        ]
        
        if active_contacts.empty:
            self.logger.info("No active contacts to check")
            return {'replies_found': 0, 'contacts_updated': []}
        
        # Get email list
        contact_emails = active_contacts['email'].tolist()
        
        # Check inbox
        scan_days = self.campaign['config']['email']['inbox_scan_days']
        replies = self.outlook_manager.get_recent_replies(contact_emails, scan_days)
        
        replies_found = 0
        contacts_updated = []
        
        for reply in replies:
            sender_email = reply['sender_email']
            
            # Record reply in smart scheduler
            self.smart_scheduler.record_reply(
                sender_email,
                reply['received_time']
            )
            
            # Update contact
            success = self.contact_tracker.update_contact(
                sender_email,
                {
                    'status': 'replied',
                    'replied_date': reply['received_time']
                }
            )
            
            if success:
                replies_found += 1
                contacts_updated.append(sender_email)
                self.logger.info(f"Reply detected from: {sender_email}")
        
        # Update statistics
        if replies_found > 0:
            self.sequence_manager.update_sequence_stats(self.sequence_id)
        
        self.logger.info(f"Found {replies_found} replies")
        
        return {
            'replies_found': replies_found,
            'contacts_updated': contacts_updated
        }
    
    def send_followups(self) -> Dict:
        """
        Send follow-up emails to non-responders.
        Uses smart scheduling if enabled.
        
        Returns:
            Results dict
        """
        self.logger.info("Checking for follow-ups to send")
        
        # Check replies first
        self.check_replies()
        
        # Get timing config
        followup_delays = self.sequence['config']['timing']['followup_delays']
        max_followups = self.sequence['config']['timing']['max_followups']
        
        # Get contacts needing follow-up
        contacts = self.contact_tracker.get_contacts_needing_followup(followup_delays)
        
        if contacts.empty:
            self.logger.info("No follow-ups needed")
            return {'sent': 0, 'scheduled': 0, 'failed': 0, 'completed': 0, 'errors': []}
        
        sent = 0
        scheduled = 0
        failed = 0
        completed = 0
        errors = []
        
        # Get email settings
        sender_name = self.campaign['config']['email']['sender_name']
        subject = self.sequence['config']['email']['subject']
        send_delay = self.campaign['config']['email']['send_delay_seconds']
        dry_run = self.config.dry_run
        
        for _, contact in contacts.iterrows():
            try:
                next_followup = contact['followup_count'] + 1
                
                # Check if this exceeds max follow-ups
                if next_followup > max_followups:
                    self.contact_tracker.update_contact(
                        contact['email'],
                        {'status': 'completed'}
                    )
                    completed += 1
                    self.logger.info(f"Completed (max follow-ups): {contact['email']}")
                    continue
                
                template_name = f"followup_{next_followup}"
                
                # Determine new status
                new_status = f"followup_{next_followup}"
                if next_followup >= max_followups:
                    new_status = 'completed'
                
                # Smart scheduling for follow-ups
                if self.smart_scheduling_enabled:
                    optimal_time = self.smart_scheduler.schedule_email(
                        self.campaign['id'],
                        self.sequence_id,
                        contact.to_dict()
                    )
                    
                    self.contact_tracker.update_contact(
                        contact['email'],
                        {
                            'status': 'scheduled',
                            'scheduled_send_time': optimal_time,
                            'followup_count': next_followup
                        }
                    )
                    scheduled += 1
                    self.logger.info(f"Scheduled {template_name} to: {contact['email']} at {optimal_time}")
                    
                else:
                    # Send immediately
                    html_body = self.template_engine.render(
                        template_name,
                        contact.to_dict(),
                        sender_name
                    )
                    
                    result = self.outlook_manager.send_email(
                        to=contact['email'],
                        subject=subject,
                        html_body=html_body,
                        dry_run=dry_run
                    )
                    
                    if result['success']:
                        # Record send
                        self.smart_scheduler.record_send(
                            self.campaign['id'],
                            self.sequence_id,
                            contact['email'],
                            result['sent_time']
                        )
                        
                        # Update contact
                        self.contact_tracker.update_contact(
                            contact['email'],
                            {
                                'status': new_status,
                                'last_contact_date': result['sent_time'],
                                'followup_count': next_followup
                            }
                        )
                        
                        if next_followup >= max_followups:
                            completed += 1
                        
                        sent += 1
                        self.logger.info(f"Sent {template_name} to: {contact['email']}")
                    else:
                        failed += 1
                        error_msg = f"Failed to send follow-up to {contact['email']}: {result['error']}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
                    
                    time.sleep(send_delay)
                
            except Exception as e:
                failed += 1
                error_msg = f"Exception sending follow-up to {contact['email']}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        # Update statistics
        self.sequence_manager.update_sequence_stats(self.sequence_id)
        
        self.logger.info(f"Follow-ups: {sent} sent, {scheduled} scheduled, {failed} failed, {completed} completed")
        
        return {
            'sent': sent,
            'scheduled': scheduled,
            'failed': failed,
            'completed': completed,
            'errors': errors
        }
    
    def run_full_cycle(self) -> Dict:
        """
        Execute complete cycle: process scheduled → check replies → send follow-ups.
        
        Returns:
            Combined results
        """
        self.logger.info("Running full cycle")
        
        scheduled_results = self.process_scheduled_sends()
        reply_results = self.check_replies()
        followup_results = self.send_followups()
        
        return {
            'scheduled_sends': scheduled_results,
            'replies': reply_results,
            'followups': followup_results
        }
    
    def get_status_report(self) -> Dict:
        """
        Generate summary of current sequence status.
        
        Returns:
            Status report dict
        """
        all_contacts = self.contact_tracker.get_all_contacts()
        
        if all_contacts.empty:
            return {
                'sequence_id': self.sequence_id,
                'sequence_name': self.sequence['name'],
                'total_contacts': 0,
                'by_status': {},
                'reply_rate': 0.0,
                'last_activity': None,
                'smart_scheduling_enabled': self.smart_scheduling_enabled
            }
        
        status_counts = all_contacts['status'].value_counts().to_dict()
        total = len(all_contacts)
        replied = status_counts.get('replied', 0)
        
        # Find last activity
        last_activity = None
        if not all_contacts['last_contact_date'].isna().all():
            last_activity = all_contacts['last_contact_date'].max()
        
        return {
            'sequence_id': self.sequence_id,
            'sequence_name': self.sequence['name'],
            'campaign_id': self.campaign['id'],
            'campaign_name': self.campaign['name'],
            'total_contacts': total,
            'by_status': status_counts,
            'reply_rate': round((replied / total * 100) if total > 0 else 0.0, 2),
            'last_activity': last_activity,
            'smart_scheduling_enabled': self.smart_scheduling_enabled
        }
```

---

## GUI Application

### Technology Stack

**Framework:** CustomTkinter (modern Tkinter wrapper)  
**Why:** Native Windows look, pure Python, easy packaging, excellent for desktop applications

**Dependencies:**
```
customtkinter>=5.2.0
pillow>=10.0.0          # For icons/images
matplotlib>=3.7.0       # For charts in scheduler
```

### Window Layout

```
┌───────────────────────────────────────────────────────────────────┐
│  Email Sequence Manager                          [─] [□] [×]      │
├────────────┬──────────────────────────────────────────────────────┤
│            │                                                      │
│  ┌──────┐  │  ┌──────────────────────────────────────────────────┐│
│  │ 🏠   │  │  │                                                  ││
│  │ HOME │  │  │              CONTENT AREA                        ││
│  └──────┘  │  │                                                  ││
│            │  │          (Changes based on selected              ││
│  ┌──────┐  │  │               navigation item)                   ││
│  │ 📁   │  │  │                                                  ││
│  │CAMPAIGNS│  │                                                  ││
│  └──────┘  │  │                                                  ││
│            │  │                                                  ││
│  ┌──────┐  │  │                                                  ││
│  │ 📊   │  │  │                                                  ││
│  │SEQUENCES│  │                                                  ││
│  └──────┘  │  │                                                  ││
│            │  │                                                  ││
│  ┌──────┐  │  │                                                  ││
│  │ 👥   │  │  │                                                  ││
│  │CONTACTS│  │                                                  ││
│  └──────┘  │  │                                                  ││
│            │  │                                                  ││
│  ┌──────┐  │  │                                                  ││
│  │ 📝   │  │  │                                                  ││
│  │TEMPLATES│  │                                                  ││
│  └──────┘  │  │                                                  ││
│            │  │                                                  ││
│  ┌──────┐  │  │                                                  ││
│  │ ⏰   │  │  │                                                  ││
│  │SCHEDULER│  │                                                  ││
│  └──────┘  │  │                                                  ││
│            │  │                                                  ││
│  ┌──────┐  │  │                                                  ││
│  │ 📋   │  │  │                                                  ││
│  │ LOGS │  │  │                                                  ││
│  └──────┘  │  │                                                  ││
│            │  │                                                  ││
│  ┌──────┐  │  │                                                  ││
│  │ ⚙️   │  │  │                                                  ││
│  │SETTINGS│  └──────────────────────────────────────────────────┘│
│  └──────┘  │                                                      │
│            │                                                      │
├────────────┴──────────────────────────────────────────────────────┤
│  Status: Ready │ Outlook: Connected │ Last sync: 14:30           │
└───────────────────────────────────────────────────────────────────┘
```

### GUI Frames

#### 1. Dashboard Frame (gui/frames/dashboard.py)

Shows overview with campaign selector and key metrics.

```python
"""Dashboard frame for GUI."""

import customtkinter as ctk
from typing import Dict

class DashboardFrame(ctk.CTkFrame):
    """Dashboard with metrics, quick actions, and activity feed."""
    
    def __init__(self, parent, app_controller):
        """
        Initialize dashboard.
        
        Args:
            parent: Parent widget
            app_controller: Main application controller
        """
        super().__init__(parent)
        self.app_controller = app_controller
        
        self.create_campaign_selector()
        self.create_metric_cards()
        self.create_quick_actions()
        self.create_active_sequences()
        self.create_activity_feed()
        
        # Auto-refresh timer
        self.auto_refresh_enabled = True
        self.schedule_refresh()
    
    def create_campaign_selector(self) -> None:
        """Create campaign dropdown selector."""
        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(fill="x", padx=20, pady=10)
        
        label = ctk.CTkLabel(
            selector_frame,
            text="Campaign:",
            font=("Arial", 14, "bold")
        )
        label.pack(side="left", padx=10)
        
        self.campaign_dropdown = ctk.CTkOptionMenu(
            selector_frame,
            values=self._get_campaign_names(),
            command=self.on_campaign_change
        )
        self.campaign_dropdown.pack(side="left", padx=10)
    
    def create_metric_cards(self) -> None:
        """Create top row of metric cards."""
        metrics_frame = ctk.CTkFrame(self)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Card layout: 4 cards across
        cards = [
            ("SEQUENCES", "📊", "0", "active"),
            ("CONTACTS", "👥", "0", "total"),
            ("REPLIED", "✉️", "0", "count"),
            ("REPLY RATE", "📈", "0%", "percentage")
        ]
        
        for i, (title, icon, value, type_) in enumerate(cards):
            card = self.create_metric_card(metrics_frame, title, icon, value, type_)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
    def create_metric_card(
        self,
        parent,
        title: str,
        icon: str,
        value: str,
        type_: str
    ) -> ctk.CTkFrame:
        """Create a single metric card."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 32)
        )
        icon_label.pack(pady=(20, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 28, "bold")
        )
        value_label.pack()
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12)
        )
        title_label.pack(pady=(5, 20))
        
        # Store labels for updates
        setattr(card, 'value_label', value_label)
        setattr(card, 'type', type_)
        
        return card
    
    def create_quick_actions(self) -> None:
        """Create quick action buttons."""
        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            actions_frame,
            text="QUICK ACTIONS",
            font=("Arial", 14, "bold")
        )
        title.pack(anchor="w", padx=10, pady=5)
        
        buttons_frame = ctk.CTkFrame(actions_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        actions = [
            ("+ CREATE NEW\nSEQUENCE", self.on_create_sequence),
            ("▶ RUN ALL\nSEQUENCES", self.on_run_all),
            ("📊 CAMPAIGN\nREPORT", self.on_campaign_report)
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                height=80,
                font=("Arial", 12, "bold")
            )
            btn.grid(row=0, column=i, padx=10, sticky="ew")
        
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
    
    def create_active_sequences(self) -> None:
        """Create active sequences list."""
        sequences_frame = ctk.CTkFrame(self)
        sequences_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        title = ctk.CTkLabel(
            sequences_frame,
            text="ACTIVE SEQUENCES",
            font=("Arial", 14, "bold")
        )
        title.pack(anchor="w", padx=10, pady=5)
        
        # Scrollable frame for sequences
        self.sequences_list = ctk.CTkScrollableFrame(sequences_frame, height=200)
        self.sequences_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_activity_feed(self) -> None:
        """Create recent activity feed."""
        activity_frame = ctk.CTkFrame(self)
        activity_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        title = ctk.CTkLabel(
            activity_frame,
            text="RECENT ACTIVITY",
            font=("Arial", 14, "bold")
        )
        title.pack(anchor="w", padx=10, pady=5)
        
        # Scrollable frame for activity
        self.activity_list = ctk.CTkScrollableFrame(activity_frame, height=150)
        self.activity_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    def refresh_data(self) -> None:
        """Reload all metrics and activity."""
        # Get selected campaign
        selected_campaign = self.campaign_dropdown.get()
        # TODO: Load campaign data and update UI
        pass
    
    def schedule_refresh(self) -> None:
        """Schedule periodic refresh."""
        if self.auto_refresh_enabled:
            self.refresh_data()
            self.after(30000, self.schedule_refresh)  # 30 seconds
    
    def on_campaign_change(self, value: str) -> None:
        """Handle campaign selection change."""
        self.refresh_data()
    
    def on_create_sequence(self) -> None:
        """Handle create sequence button."""
        self.app_controller.navigate_to("sequences")
    
    def on_run_all(self) -> None:
        """Handle run all sequences button."""
        # TODO: Show confirmation dialog and run all
        pass
    
    def on_campaign_report(self) -> None:
        """Handle campaign report button."""
        # TODO: Generate and show report
        pass
    
    def _get_campaign_names(self) -> list:
        """Get list of campaign names for dropdown."""
        # TODO: Load from campaign manager
        return ["Campaign 1", "Campaign 2"]
```

#### 2. Campaigns Frame (gui/frames/campaigns.py)

Manage campaigns (create, edit, delete).

*[Implementation similar to dashboard - table with campaign list, detail panel for editing]*

#### 3. Sequences Frame (gui/frames/sequences.py)

Manage sequences within selected campaign.

*[Implementation: List sequences, create/edit/delete, show statistics]*

#### 4. Contacts Frame (gui/frames/contacts.py)

Manage contacts within selected sequence.

*[Implementation: Contact table, add/import/edit, status management]*

#### 5. Templates Frame (gui/frames/templates.py)

Edit email templates with live preview.

*[Implementation: Template selector, HTML editor, preview pane]*

#### 6. Scheduler Frame (gui/frames/scheduler.py)

NEW: Smart scheduling configuration and analytics.

```python
"""Smart scheduler frame for GUI."""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class SchedulerFrame(ctk.CTkFrame):
    """Smart scheduling configuration and analytics."""
    
    def __init__(self, parent, app_controller):
        """
        Initialize scheduler frame.
        
        Args:
            parent: Parent widget
            app_controller: Main application controller
        """
        super().__init__(parent)
        self.app_controller = app_controller
        self.smart_scheduler = app_controller.smart_scheduler
        
        self.create_header()
        self.create_configuration_section()
        self.create_analytics_section()
        self.create_optimal_times_chart()
        
        self.load_data()
    
    def create_header(self) -> None:
        """Create frame header."""
        header = ctk.CTkLabel(
            self,
            text="SMART SCHEDULING",
            font=("Arial", 24, "bold")
        )
        header.pack(pady=20)
    
    def create_configuration_section(self) -> None:
        """Create scheduling configuration controls."""
        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            config_frame,
            text="Configuration",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", padx=10, pady=10)
        
        # Enable/disable switch
        switch_frame = ctk.CTkFrame(config_frame)
        switch_frame.pack(fill="x", padx=10, pady=5)
        
        self.enable_switch = ctk.CTkSwitch(
            switch_frame,
            text="Enable Smart Scheduling",
            command=self.on_toggle_scheduling
        )
        self.enable_switch.pack(side="left", padx=10)
        
        # Business hours
        hours_frame = ctk.CTkFrame(config_frame)
        hours_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(hours_frame, text="Business Hours:").pack(side="left", padx=10)
        
        self.start_hour_entry = ctk.CTkEntry(hours_frame, width=60)
        self.start_hour_entry.pack(side="left", padx=5)
        self.start_hour_entry.insert(0, "09:00")
        
        ctk.CTkLabel(hours_frame, text="to").pack(side="left", padx=5)
        
        self.end_hour_entry = ctk.CTkEntry(hours_frame, width=60)
        self.end_hour_entry.pack(side="left", padx=5)
        self.end_hour_entry.insert(0, "18:00")
        
        # Preferred days
        days_frame = ctk.CTkFrame(config_frame)
        days_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(days_frame, text="Preferred Days:").pack(side="left", padx=10)
        
        self.day_checkboxes = {}
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            var = ctk.BooleanVar(value=day not in ["Sat", "Sun"])
            cb = ctk.CTkCheckBox(days_frame, text=day, variable=var)
            cb.pack(side="left", padx=5)
            self.day_checkboxes[day] = var
        
        # Save button
        save_btn = ctk.CTkButton(
            config_frame,
            text="Save Configuration",
            command=self.save_configuration
        )
        save_btn.pack(pady=10)
    
    def create_analytics_section(self) -> None:
        """Create analytics display."""
        analytics_frame = ctk.CTkFrame(self)
        analytics_frame.pack(fill="x", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            analytics_frame,
            text="Performance Analytics",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", padx=10, pady=10)
        
        # Stats grid
        stats_frame = ctk.CTkFrame(analytics_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.stats_labels = {}
        stats = [
            ("Total Emails", "0"),
            ("Total Replies", "0"),
            ("Reply Rate", "0%"),
            ("Avg Reply Time", "0h")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(stats_frame)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            value_label = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Arial", 24, "bold")
            )
            value_label.pack(pady=5)
            
            label_widget = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Arial", 12)
            )
            label_widget.pack(pady=5)
            
            self.stats_labels[label] = value_label
        
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Best times
        best_times_frame = ctk.CTkFrame(analytics_frame)
        best_times_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            best_times_frame,
            text="Optimal Send Times:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        self.best_times_label = ctk.CTkLabel(
            best_times_frame,
            text="No data available yet",
            font=("Arial", 12)
        )
        self.best_times_label.pack(anchor="w", padx=10, pady=5)
    
    def create_optimal_times_chart(self) -> None:
        """Create chart showing optimal send times."""
        chart_frame = ctk.CTkFrame(self)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        title = ctk.CTkLabel(
            chart_frame,
            text="Reply Rate by Day and Hour",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_data(self) -> None:
        """Load scheduling data and update display."""
        # Load configuration
        config = self.app_controller.config
        enabled = config.smart_scheduling_enabled
        self.enable_switch.select() if enabled else self.enable_switch.deselect()
        
        # Load analytics
        report = self.smart_scheduler.get_scheduling_report()
        
        self.stats_labels["Total Emails"].configure(text=str(report['total_emails']))
        self.stats_labels["Total Replies"].configure(text=str(report['total_replies']))
        self.stats_labels["Reply Rate"].configure(text=f"{report['reply_rate']}%")
        self.stats_labels["Avg Reply Time"].configure(
            text=f"{report['avg_reply_time_hours']:.1f}h"
        )
        
        if report['best_day']:
            best_times_text = (
                f"Best day: {report['best_day']} at {report['best_hour']} "
                f"({report['best_reply_rate']}% reply rate)"
            )
            self.best_times_label.configure(text=best_times_text)
        
        # Update chart
        self.update_chart()
    
    def update_chart(self) -> None:
        """Update heatmap chart with optimal times."""
        self.ax.clear()
        
        # Get optimal times data
        optimal_times = self.smart_scheduler.analyze_optimal_times()
        
        if not optimal_times:
            self.ax.text(
                0.5, 0.5,
                "No data available\nSend some emails to see analytics!",
                ha='center', va='center',
                fontsize=14
            )
            self.canvas.draw()
            return
        
        # Create heatmap data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(7, 20))  # 7 AM to 7 PM
        
        data = []
        for day_idx in range(7):
            day_data = []
            for hour in hours:
                reply_rate = optimal_times.get((day_idx, hour), 0)
                day_data.append(reply_rate)
            data.append(day_data)
        
        # Plot heatmap
        im = self.ax.imshow(data, cmap='YlOrRd', aspect='auto')
        
        # Set ticks
        self.ax.set_xticks(range(len(hours)))
        self.ax.set_xticklabels([f"{h}:00" for h in hours])
        self.ax.set_yticks(range(len(days)))
        self.ax.set_yticklabels(days)
        
        # Labels
        self.ax.set_xlabel('Hour of Day')
        self.ax.set_ylabel('Day of Week')
        
        # Colorbar
        cbar = self.fig.colorbar(im, ax=self.ax)
        cbar.set_label('Reply Rate (%)')
        
        self.canvas.draw()
    
    def on_toggle_scheduling(self) -> None:
        """Handle scheduling toggle."""
        enabled = self.enable_switch.get()
        self.app_controller.config.set('smart_scheduling.enabled', enabled)
        self.app_controller.config.save()
    
    def save_configuration(self) -> None:
        """Save scheduling configuration."""
        config = self.app_controller.config
        
        # Save business hours
        start_hour = self.start_hour_entry.get()
        end_hour = self.end_hour_entry.get()
        config.set('smart_scheduling.business_hours_start', start_hour)
        config.set('smart_scheduling.business_hours_end', end_hour)
        
        # Save preferred days
        preferred_days = [
            day for day, var in self.day_checkboxes.items()
            if var.get()
        ]
        config.set('smart_scheduling.preferred_days', preferred_days)
        
        config.save()
        
        # Show success message
        # TODO: Show toast notification
```

#### 7. Logs Frame (gui/frames/logs.py)

View logs with filtering.

*[Implementation: Log viewer with filters for level, campaign, date]*

#### 8. Settings Frame (gui/frames/settings.py)

Configure application settings.

*[Implementation: Path settings, appearance, behavior, Outlook connection]*

### Main GUI Application (gui/app.py)

```python
"""Main GUI application."""

import customtkinter as ctk
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.config import Config
from src.campaign_manager import CampaignManager
from src.smart_scheduler import SmartScheduler

from .frames.dashboard import DashboardFrame
from .frames.campaigns import CampaignsFrame
from .frames.sequences import SequencesFrame
from .frames.contacts import ContactsFrame
from .frames.templates import TemplatesFrame
from .frames.scheduler import SchedulerFrame
from .frames.logs import LogsFrame
from .frames.settings import SettingsFrame

class EmailSequenceApp(ctk.CTk):
    """Main application window with sidebar navigation."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Load configuration
        self.config = Config()
        self.campaign_manager = CampaignManager(str(self.config.campaigns_folder))
        self.smart_scheduler = SmartScheduler(str(self.config.data_folder), self.config)
        
        # Load GUI config
        self.gui_config = self._load_gui_config()
        
        # Setup window
        self.title("Email Sequence Manager")
        self.geometry(f"{self.gui_config['window_width']}x{self.gui_config['window_height']}")
        
        # Set theme
        ctk.set_appearance_mode(self.gui_config['theme'])
        ctk.set_default_color_theme(self.gui_config['color_scheme'])
        
        # Create UI
        self.create_sidebar()
        self.create_content_area()
        self.create_status_bar()
        
        # Load default frame
        self.navigate_to("dashboard")
    
    def _load_gui_config(self) -> dict:
        """Load GUI configuration."""
        # TODO: Load from gui_config.yaml
        return {
            'theme': 'dark',
            'color_scheme': 'blue',
            'window_width': 1400,
            'window_height': 900,
            'sidebar_width': 220
        }
    
    def create_sidebar(self) -> None:
        """Create left sidebar with navigation buttons."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo
        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Email Sequence\nManager",
            font=("Arial", 18, "bold")
        )
        logo_label.pack(pady=30)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("🏠 Home", "dashboard"),
            ("📁 Campaigns", "campaigns"),
            ("📊 Sequences", "sequences"),
            ("👥 Contacts", "contacts"),
            ("📝 Templates", "templates"),
            ("⏰ Scheduler", "scheduler"),
            ("📋 Logs", "logs"),
            ("⚙️ Settings", "settings")
        ]
        
        for text, frame_name in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda f=frame_name: self.navigate_to(f),
                height=40,
                anchor="w",
                font=("Arial", 13)
            )
            btn.pack(padx=10, pady=5, fill="x")
            self.nav_buttons[frame_name] = btn
    
    def create_content_area(self) -> None:
        """Create main content area."""
        self.content_area = ctk.CTkFrame(self, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)
        
        self.current_frame = None
    
    def create_status_bar(self) -> None:
        """Create bottom status bar."""
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=("Arial", 11)
        )
        self.status_label.pack(side="left", padx=10)
        
        self.outlook_status_label = ctk.CTkLabel(
            self.status_bar,
            text="Outlook: Checking...",
            font=("Arial", 11)
        )
        self.outlook_status_label.pack(side="left", padx=10)
        
        self.last_sync_label = ctk.CTkLabel(
            self.status_bar,
            text="Last sync: Never",
            font=("Arial", 11)
        )
        self.last_sync_label.pack(side="right", padx=10)
    
    def navigate_to(self, frame_name: str) -> None:
        """
        Switch content area to specified frame.
        
        Args:
            frame_name: Name of frame to display
        """
        # Destroy current frame
        if self.current_frame:
            self.current_frame.destroy()
        
        # Create new frame
        frame_classes = {
            'dashboard': DashboardFrame,
            'campaigns': CampaignsFrame,
            'sequences': SequencesFrame,
            'contacts': ContactsFrame,
            'templates': TemplatesFrame,
            'scheduler': SchedulerFrame,
            'logs': LogsFrame,
            'settings': SettingsFrame
        }
        
        frame_class = frame_classes.get(frame_name)
        if frame_class:
            self.current_frame = frame_class(self.content_area, self)
            self.current_frame.pack(fill="both", expand=True)
        
        # Update button highlighting
        for name, btn in self.nav_buttons.items():
            if name == frame_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
    
    def update_status(self, message: str) -> None:
        """Update status bar message."""
        self.status_label.configure(text=message)

def main():
    """Run GUI application."""
    app = EmailSequenceApp()
    app.mainloop()

if __name__ == "__main__":
    main()
```

### GUI Entry Point (run_gui.py)

```python
#!/usr/bin/env python3
"""
Email Sequence Manager - GUI Entry Point
"""

from gui.app import main

if __name__ == "__main__":
    main()
```

---

## Smart Scheduling

### Overview

Smart scheduling analyzes historical email send and reply patterns to determine optimal send times for maximum engagement. The system learns from your data and automatically schedules emails when recipients are most likely to respond.

### Features

1. **Historical Analysis:** Tracks send times and reply patterns
2. **Optimal Time Calculation:** Identifies best days/hours for sending
3. **Automatic Scheduling:** Queues emails for optimal delivery
4. **Performance Analytics:** Visualizes reply rates by time
5. **Industry Awareness:** (Future) Adapts to industry-specific patterns
6. **Timezone Support:** (Future) Respects recipient timezones

### How It Works

#### 1. Data Collection

Every time an email is sent, the system records:
- Send date/time (day of week, hour)
- Campaign and sequence
- Contact information

When a reply is received, the system records:
- Reply date/time
- Time to reply (in hours)

#### 2. Analysis

The `SmartScheduler` class analyzes historical data to calculate:
- Reply rates by day of week
- Reply rates by hour of day
- Average time to reply
- Best performing time slots

#### 3. Scheduling

When scheduling an email, the system:
1. Calculates earliest possible send time (current time + min delay)
2. Calculates latest possible send time (earliest + max delay window)
3. Evaluates all time slots within window
4. Filters by business hours and preferred days
5. Selects time with highest historical reply rate
6. Schedules email in database

#### 4. Execution

A background process (or scheduler task) periodically:
1. Checks for pending scheduled sends
2. Sends emails that are due
3. Records send in analytics database
4. Updates contact status

### Configuration Options

**Global Settings (config.yaml):**
```yaml
smart_scheduling:
  enabled: false
  analysis_window_days: 90      # History to analyze
  timezone: "Europe/Paris"
  business_hours_start: "09:00"
  business_hours_end: "18:00"
  preferred_days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
  avoid_holidays: true
  min_delay_hours: 1            # Minimum delay before sending
  max_delay_hours: 48           # Maximum scheduling window
```

**Campaign/Sequence Override:**
Each campaign and sequence can override global settings.

### Default Optimal Times

When no historical data exists, the system uses industry best practices:

| Time Slot | Day | Est. Reply Rate |
|-----------|-----|-----------------|
| 9-10 AM | Weekdays | 15% |
| 2-3 PM | Weekdays | 18% (best) |
| 4-5 PM | Weekdays | 12% |

