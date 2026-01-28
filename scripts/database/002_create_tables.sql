-- Lead Generator Database Schema
-- Run this script after creating the database

-- ENUM Types
CREATE TYPE user_role AS ENUM ('Admin', 'Manager', 'User');
CREATE TYPE campaign_status AS ENUM ('Draft', 'Active', 'Paused', 'Completed', 'Archived');
CREATE TYPE contact_status AS ENUM ('Pending', 'InProgress', 'Responded', 'Completed', 'Bounced', 'Unsubscribed', 'OptedOut', 'Paused');
CREATE TYPE delivery_mode AS ENUM ('Attachment', 'Link');
CREATE TYPE unsubscribe_scope AS ENUM ('Global', 'Campaign');
CREATE TYPE unsubscribe_source AS ENUM ('EmailReply', 'Manual', 'Bounce', 'Complaint');
CREATE TYPE ab_test_element AS ENUM ('Subject', 'Body', 'SendTime');
CREATE TYPE ab_test_status AS ENUM ('Running', 'Completed', 'Cancelled');

-- Users
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'User',
    is_active BOOLEAN NOT NULL DEFAULT true,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Mail Accounts
CREATE TABLE mail_accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    workstation_id VARCHAR(100),
    daily_limit INT NOT NULL DEFAULT 50,
    hourly_limit INT NOT NULL DEFAULT 10,
    current_daily_count INT NOT NULL DEFAULT 0,
    last_count_reset DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    warmup_mode BOOLEAN NOT NULL DEFAULT false,
    warmup_start_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- User Mail Account Assignments
CREATE TABLE user_mail_accounts (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    account_id UUID REFERENCES mail_accounts(account_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, account_id)
);

-- Contact Lists
CREATE TABLE contact_lists (
    list_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    owner_user_id UUID REFERENCES users(user_id),
    is_shared BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Contacts
CREATE TABLE contacts (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id UUID NOT NULL REFERENCES contact_lists(list_id) ON DELETE CASCADE,
    title VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(200) NOT NULL,
    position VARCHAR(100),
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    source VARCHAR(100),
    custom1 VARCHAR(500),
    custom2 VARCHAR(500),
    custom3 VARCHAR(500),
    custom4 VARCHAR(500),
    custom5 VARCHAR(500),
    custom6 VARCHAR(500),
    custom7 VARCHAR(500),
    custom8 VARCHAR(500),
    custom9 VARCHAR(500),
    custom10 VARCHAR(500),
    custom1_label VARCHAR(50),
    custom2_label VARCHAR(50),
    custom3_label VARCHAR(50),
    custom4_label VARCHAR(50),
    custom5_label VARCHAR(50),
    custom6_label VARCHAR(50),
    custom7_label VARCHAR(50),
    custom8_label VARCHAR(50),
    custom9_label VARCHAR(50),
    custom10_label VARCHAR(50),
    crm_lead_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(list_id, email)
);

-- Campaigns
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    campaign_ref VARCHAR(20) NOT NULL UNIQUE,
    owner_user_id UUID REFERENCES users(user_id),
    contact_list_id UUID REFERENCES contact_lists(list_id),
    status campaign_status NOT NULL DEFAULT 'Draft',
    inter_email_delay_minutes INT NOT NULL DEFAULT 30,
    sequence_step_delay_days INT NOT NULL DEFAULT 3,
    sending_window_start TIME NOT NULL DEFAULT '09:00',
    sending_window_end TIME NOT NULL DEFAULT '17:00',
    sending_days VARCHAR(20) NOT NULL DEFAULT 'Mon,Tue,Wed,Thu,Fri',
    randomization_minutes INT NOT NULL DEFAULT 15,
    daily_send_limit INT NOT NULL DEFAULT 50,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Campaign Mail Accounts
CREATE TABLE campaign_mail_accounts (
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    account_id UUID REFERENCES mail_accounts(account_id) ON DELETE CASCADE,
    distribution_weight DECIMAL(3,2) DEFAULT 1.0,
    PRIMARY KEY (campaign_id, account_id)
);

-- Email Steps (Sequence)
CREATE TABLE email_steps (
    step_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    delay_days INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, step_number)
);

-- Attachments
CREATE TABLE attachments (
    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID NOT NULL REFERENCES email_steps(step_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    delivery_mode delivery_mode NOT NULL DEFAULT 'Attachment',
    link_text VARCHAR(200),
    expiration_days INT,
    download_token VARCHAR(100) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Campaign Contacts (Junction + Status)
CREATE TABLE campaign_contacts (
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(contact_id) ON DELETE CASCADE,
    status contact_status NOT NULL DEFAULT 'Pending',
    assigned_mail_account_id UUID REFERENCES mail_accounts(account_id),
    current_step INT NOT NULL DEFAULT 0,
    last_email_sent_at TIMESTAMP,
    next_email_scheduled_at TIMESTAMP,
    responded_at TIMESTAMP,
    ab_test_variant CHAR(1),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (campaign_id, contact_id)
);

-- Email Log
CREATE TABLE email_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    contact_id UUID REFERENCES contacts(contact_id),
    step_id UUID REFERENCES email_steps(step_id),
    mail_account_id UUID REFERENCES mail_accounts(account_id),
    subject VARCHAR(500),
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    outlook_entry_id VARCHAR(500)
);

-- Download Log (for Link mode tracking)
CREATE TABLE download_logs (
    download_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attachment_id UUID NOT NULL REFERENCES attachments(attachment_id),
    contact_id UUID REFERENCES contacts(contact_id),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    downloaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500)
);

-- Suppression List
CREATE TABLE suppression_list (
    email VARCHAR(255) PRIMARY KEY,
    scope unsubscribe_scope NOT NULL DEFAULT 'Global',
    source unsubscribe_source NOT NULL,
    campaign_id UUID REFERENCES campaigns(campaign_id),
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- A/B Tests
CREATE TABLE ab_tests (
    test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES email_steps(step_id) ON DELETE CASCADE,
    test_element ab_test_element NOT NULL,
    variant_a_content TEXT NOT NULL,
    variant_b_content TEXT NOT NULL,
    split_ratio DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    success_metric VARCHAR(50) NOT NULL DEFAULT 'ResponseRate',
    min_sample_size INT NOT NULL DEFAULT 100,
    max_duration_days INT NOT NULL DEFAULT 14,
    status ab_test_status NOT NULL DEFAULT 'Running',
    winner_variant CHAR(1),
    confidence_level DECIMAL(5,2),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Audit Log
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
