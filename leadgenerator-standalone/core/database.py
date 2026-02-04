"""SQLite database management for Lead Generator Standalone."""

import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Generator

from .exceptions import DatabaseError

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = "data/leadgen.db"

# SQLite schema
SCHEMA = """
-- ============================================================
-- Lead Generator Standalone — SQLite Schema
-- ============================================================

-- Settings (key-value store for app configuration)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Mail Account (single account for standalone)
CREATE TABLE IF NOT EXISTS mail_account (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT NOT NULL UNIQUE,
    display_name TEXT,
    daily_limit INTEGER DEFAULT 50,
    hourly_limit INTEGER DEFAULT 10,
    current_daily_count INTEGER DEFAULT 0,
    last_count_reset TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Contact Lists
CREATE TABLE IF NOT EXISTS contact_lists (
    list_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    custom1_label TEXT,
    custom2_label TEXT,
    custom3_label TEXT,
    custom4_label TEXT,
    custom5_label TEXT,
    custom6_label TEXT,
    custom7_label TEXT,
    custom8_label TEXT,
    custom9_label TEXT,
    custom10_label TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Contacts
CREATE TABLE IF NOT EXISTS contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL REFERENCES contact_lists(list_id) ON DELETE CASCADE,
    title TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    company TEXT NOT NULL,
    position TEXT,
    phone TEXT,
    linkedin_url TEXT,
    source TEXT,
    custom1 TEXT,
    custom2 TEXT,
    custom3 TEXT,
    custom4 TEXT,
    custom5 TEXT,
    custom6 TEXT,
    custom7 TEXT,
    custom8 TEXT,
    custom9 TEXT,
    custom10 TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(list_id, email)
);

-- Campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    campaign_ref TEXT NOT NULL UNIQUE,
    contact_list_id INTEGER REFERENCES contact_lists(list_id),
    status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Active', 'Paused', 'Completed', 'Archived')),
    inter_email_delay_minutes INTEGER DEFAULT 30,
    sequence_step_delay_days INTEGER DEFAULT 3,
    sending_window_start TEXT DEFAULT '09:00',
    sending_window_end TEXT DEFAULT '17:00',
    sending_days TEXT DEFAULT 'Mon,Tue,Wed,Thu,Fri',
    randomization_minutes INTEGER DEFAULT 15,
    daily_send_limit INTEGER DEFAULT 50,
    start_date TEXT,
    end_date TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Email Steps (Sequence)
CREATE TABLE IF NOT EXISTS email_steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    delay_days INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(campaign_id, step_number)
);

-- Attachments (Attachment mode only — no Link tracking)
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id INTEGER NOT NULL REFERENCES email_steps(step_id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Campaign Contacts (per-contact status tracking)
CREATE TABLE IF NOT EXISTS campaign_contacts (
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    contact_id INTEGER NOT NULL REFERENCES contacts(contact_id) ON DELETE CASCADE,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'InProgress', 'Responded', 'Completed', 'Bounced', 'Unsubscribed', 'OptedOut', 'Paused')),
    current_step INTEGER DEFAULT 0,
    last_email_sent_at TEXT,
    next_email_scheduled_at TEXT,
    responded_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (campaign_id, contact_id)
);

-- Email Log
CREATE TABLE IF NOT EXISTS email_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    contact_id INTEGER REFERENCES contacts(contact_id),
    step_id INTEGER REFERENCES email_steps(step_id),
    subject TEXT,
    sent_at TEXT DEFAULT (datetime('now')),
    status TEXT NOT NULL CHECK(status IN ('Sent', 'Failed', 'Bounced')),
    error_message TEXT,
    outlook_entry_id TEXT
);

-- Suppression List
CREATE TABLE IF NOT EXISTS suppression_list (
    email TEXT PRIMARY KEY,
    scope TEXT DEFAULT 'Global' CHECK(scope IN ('Global', 'Campaign')),
    source TEXT NOT NULL CHECK(source IN ('EmailReply', 'Manual', 'Bounce', 'Complaint')),
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    reason TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Email Queue (pending emails to send)
CREATE TABLE IF NOT EXISTS email_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(campaign_id),
    contact_id INTEGER NOT NULL REFERENCES contacts(contact_id),
    step_id INTEGER NOT NULL REFERENCES email_steps(step_id),
    scheduled_at TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Sending', 'Sent', 'Failed', 'Skipped')),
    attempts INTEGER DEFAULT 0,
    last_attempt_at TEXT,
    error_message TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_list ON contacts(list_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_next ON campaign_contacts(next_email_scheduled_at);
CREATE INDEX IF NOT EXISTS idx_email_queue_status ON email_queue(status);
CREATE INDEX IF NOT EXISTS idx_email_queue_scheduled ON email_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_suppression_email ON suppression_list(email);
"""

# Initial settings
INITIAL_SETTINGS = [
    ('app_version', '1.0.0'),
    ('last_campaign_number', '0'),
    ('outlook_scan_interval_seconds', '60'),
    ('unsubscribe_keywords_en', 'UNSUBSCRIBE,STOP,REMOVE,OPT OUT,OPT-OUT'),
    ('unsubscribe_keywords_fr', 'DÉSINSCRIRE,DÉSINSCRIPTION,STOP,ARRÊTER,SUPPRIMER'),
    ('scan_folders', 'Inbox,Unsubscribe'),
]


class Database:
    """SQLite database connection manager."""

    _instance: Optional['Database'] = None
    _db_path: str = DEFAULT_DB_PATH

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path:
            self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @classmethod
    def set_path(cls, db_path: str) -> None:
        """Set the database path for all instances."""
        cls._db_path = db_path

    @classmethod
    def get_instance(cls) -> 'Database':
        """Get singleton database instance."""
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            # Ensure directory exists
            db_dir = os.path.dirname(self._db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            self._connection = sqlite3.connect(
                self._db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Get database cursor as context manager."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(str(e)) from e
        finally:
            cursor.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(str(e)) from e

    def executemany(self, query: str, params_list: list) -> None:
        """Execute a query with multiple parameter sets."""
        conn = self._get_connection()
        try:
            conn.executemany(query, params_list)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(str(e)) from e

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one result."""
        conn = self._get_connection()
        cursor = conn.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list:
        """Execute query and fetch all results."""
        conn = self._get_connection()
        cursor = conn.execute(query, params)
        return cursor.fetchall()

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None


def get_db() -> Database:
    """Get database instance."""
    return Database.get_instance()


def init_database(db_path: Optional[str] = None) -> None:
    """Initialize database with schema and default settings."""
    if db_path:
        Database.set_path(db_path)

    db = get_db()

    # Create schema
    conn = db._get_connection()
    conn.executescript(SCHEMA)
    conn.commit()

    # Insert initial settings if not exist
    for key, value in INITIAL_SETTINGS:
        db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    logger.info(f"Database initialized at {db._db_path}")


def get_setting(key: str, default: Any = None) -> Any:
    """Get setting value by key."""
    db = get_db()
    row = db.fetchone("SELECT value FROM settings WHERE key = ?", (key,))
    if row:
        return row['value']
    return default


def set_setting(key: str, value: Any) -> None:
    """Set setting value."""
    db = get_db()
    db.execute(
        """INSERT INTO settings (key, value, updated_at)
           VALUES (?, ?, datetime('now'))
           ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
        (key, str(value), str(value))
    )


def generate_campaign_ref() -> str:
    """Generate next campaign reference in format ISIT-{YY}{NNNN}."""
    db = get_db()

    # Get last campaign number
    last_number = int(get_setting('last_campaign_number', '0'))
    next_number = last_number + 1

    # Get current year (2 digits)
    year = datetime.now().strftime('%y')

    # Format: ISIT-YYNNNN (e.g., ISIT-250001)
    campaign_ref = f"ISIT-{year}{next_number:04d}"

    # Update last campaign number
    set_setting('last_campaign_number', next_number)

    return campaign_ref
