-- ============================================================
-- Seed Tutorial Campaign (Standalone / SQLite)
-- Creates a sample "Tutorial" campaign with:
--   - 1 contact list with 5 example contacts
--   - 1 campaign with 5 email steps (sequence)
--   - 5 campaign_contact records linking contacts to the campaign
-- Run this AFTER schema.sql
-- ============================================================

-- -------------------------------------------------------
-- 1. Contact List: "Tutorial Contacts"
-- -------------------------------------------------------
INSERT OR IGNORE INTO contact_lists (name, description)
VALUES (
    'Tutorial Contacts',
    'Sample contact list created for the Tutorial campaign. These are fictional contacts to help you explore the application.'
);

-- -------------------------------------------------------
-- 2. Contacts (5 fictional contacts)
-- -------------------------------------------------------
INSERT OR IGNORE INTO contacts (list_id, first_name, last_name, email, company, position, phone, linkedin_url, source)
VALUES
    ((SELECT list_id FROM contact_lists WHERE name = 'Tutorial Contacts'), 'Alice',  'Martin',  'alice.martin@example.com',  'Acme Corp',        'Marketing Director', '+1-555-0101', 'https://linkedin.com/in/alicemartin',  'Tutorial'),
    ((SELECT list_id FROM contact_lists WHERE name = 'Tutorial Contacts'), 'Bob',    'Johnson', 'bob.johnson@example.com',   'Globex Inc',       'VP of Sales',        '+1-555-0102', 'https://linkedin.com/in/bobjohnson',  'Tutorial'),
    ((SELECT list_id FROM contact_lists WHERE name = 'Tutorial Contacts'), 'Clara',  'Dubois',  'clara.dubois@example.com',  'Initech Ltd',      'CTO',                '+1-555-0103', 'https://linkedin.com/in/claradubois', 'Tutorial'),
    ((SELECT list_id FROM contact_lists WHERE name = 'Tutorial Contacts'), 'David',  'Chen',    'david.chen@example.com',    'Umbrella Corp',    'Head of Operations', '+1-555-0104', 'https://linkedin.com/in/davidchen',   'Tutorial'),
    ((SELECT list_id FROM contact_lists WHERE name = 'Tutorial Contacts'), 'Emma',   'Wilson',  'emma.wilson@example.com',   'Stark Industries', 'Product Manager',    '+1-555-0105', 'https://linkedin.com/in/emmawilson',  'Tutorial');

-- -------------------------------------------------------
-- 3. Campaign: "Tutorial"
-- -------------------------------------------------------
INSERT OR IGNORE INTO campaigns (name, description, campaign_ref, contact_list_id, status,
                                  inter_email_delay_minutes, sequence_step_delay_days,
                                  sending_window_start, sending_window_end, sending_days,
                                  randomization_minutes, daily_send_limit)
VALUES (
    'Tutorial',
    'Example campaign to help you get started. It contains 5 email steps and 5 sample contacts. Review the email templates to understand how merge tags like {{FirstName}} and {{Company}} work.',
    'ISIT-250000',
    (SELECT list_id FROM contact_lists WHERE name = 'Tutorial Contacts'),
    'Draft',
    30,
    3,
    '09:00',
    '17:00',
    'Mon,Tue,Wed,Thu,Fri',
    15,
    50
);

-- Update the last_campaign_number setting
UPDATE settings SET value = '0' WHERE key = 'last_campaign_number' AND CAST(value AS INTEGER) < 0;

-- -------------------------------------------------------
-- 4. Email Steps (5-step sequence)
-- -------------------------------------------------------

-- Step 1: Introduction (sent immediately)
INSERT OR IGNORE INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days, is_active)
VALUES (
    (SELECT campaign_id FROM campaigns WHERE campaign_ref = 'ISIT-250000'),
    1,
    'Hi {{FirstName}}, quick introduction',
    'Hi {{FirstName}},

I hope this message finds you well. My name is [Your Name] and I work with companies like {{Company}} to help them [describe your value proposition].

I noticed your role as {{Position}} and thought this could be relevant to your team.

Would you be open to a brief conversation this week?

Best regards,
[Your Name]',
    0,
    1
);

-- Step 2: Value proposition (Day 3)
INSERT OR IGNORE INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days, is_active)
VALUES (
    (SELECT campaign_id FROM campaigns WHERE campaign_ref = 'ISIT-250000'),
    2,
    'A quick idea for {{Company}}',
    'Hi {{FirstName}},

I wanted to follow up on my previous email. I have been researching {{Company}} and I believe we could help your team with [specific benefit].

Here are a few results our clients have seen:
- 30% increase in efficiency
- Reduced manual workload
- Faster time to market

Would any of these outcomes be valuable for your team at {{Company}}?

Looking forward to hearing from you.

Best,
[Your Name]',
    3,
    1
);

-- Step 3: Social proof (Day 6)
INSERT OR IGNORE INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days, is_active)
VALUES (
    (SELECT campaign_id FROM campaigns WHERE campaign_ref = 'ISIT-250000'),
    3,
    '{{FirstName}}, how companies like {{Company}} are succeeding',
    'Hi {{FirstName}},

I wanted to share a quick case study that might resonate with you.

One of our clients in a similar industry to {{Company}} was facing [common challenge]. After working with us, they achieved [specific result] within just 3 months.

I would love to walk you through how we could replicate this for your team.

Are you available for a 15-minute call next week?

Regards,
[Your Name]',
    3,
    1
);

-- Step 4: Direct ask (Day 9)
INSERT OR IGNORE INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days, is_active)
VALUES (
    (SELECT campaign_id FROM campaigns WHERE campaign_ref = 'ISIT-250000'),
    4,
    'Quick question, {{FirstName}}',
    'Hi {{FirstName}},

I have sent a few messages and want to make sure I am reaching the right person at {{Company}}.

Are you the best person to discuss [topic]? If not, could you point me in the right direction?

Either way, I appreciate your time.

Thanks,
[Your Name]',
    3,
    1
);

-- Step 5: Breakup / last chance (Day 12)
INSERT OR IGNORE INTO email_steps (campaign_id, step_number, subject_template, body_template, delay_days, is_active)
VALUES (
    (SELECT campaign_id FROM campaigns WHERE campaign_ref = 'ISIT-250000'),
    5,
    'Closing the loop, {{FirstName}}',
    'Hi {{FirstName}},

I understand things are busy at {{Company}}, so I will keep this brief.

This will be my last email on this topic. If timing is not right, no worries at all. But if you are interested in exploring how we can help {{Company}} with [value proposition], I am happy to chat whenever it works for you.

Just reply to this email and we can set something up.

Wishing you and your team all the best.

Kind regards,
[Your Name]',
    3,
    1
);

-- -------------------------------------------------------
-- 5. Campaign Contacts (enroll all 5 contacts)
-- -------------------------------------------------------
INSERT OR IGNORE INTO campaign_contacts (campaign_id, contact_id, status, current_step)
SELECT
    c.campaign_id,
    ct.contact_id,
    'Pending',
    0
FROM campaigns c
CROSS JOIN contacts ct
WHERE c.campaign_ref = 'ISIT-250000'
  AND ct.list_id = c.contact_list_id;
