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

-- Initial Settings
INSERT OR IGNORE INTO settings (key, value) VALUES
    ('app_version', '1.0.0'),
    ('last_campaign_number', '0'),
    ('outlook_scan_interval_seconds', '60'),
    ('unsubscribe_keywords_en', 'UNSUBSCRIBE,STOP,REMOVE,OPT OUT,OPT-OUT'),
    ('unsubscribe_keywords_fr', 'DÉSINSCRIRE,DÉSINSCRIPTION,STOP,ARRÊTER,SUPPRIMER'),
    ('scan_folders', 'Inbox,Unsubscribe');
