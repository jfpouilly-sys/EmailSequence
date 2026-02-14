-- ============================================================
-- Seed Tutorial Campaign
-- Creates a sample "Tutorial" campaign with:
--   - 1 contact list with 5 example contacts
--   - 1 campaign with 5 email steps (sequence)
--   - 5 campaign_contact records linking contacts to the campaign
-- Run this AFTER 003_seed_admin_user.sql
-- ============================================================

BEGIN;

-- Fixed UUIDs for reproducibility and cross-reference
-- Contact List
DO $$
DECLARE
    v_admin_id UUID;
    v_list_id UUID := 'a0000000-0000-0000-0000-000000000001';
    v_campaign_id UUID := 'b0000000-0000-0000-0000-000000000001';
    v_contact1_id UUID := 'c0000000-0000-0000-0000-000000000001';
    v_contact2_id UUID := 'c0000000-0000-0000-0000-000000000002';
    v_contact3_id UUID := 'c0000000-0000-0000-0000-000000000003';
    v_contact4_id UUID := 'c0000000-0000-0000-0000-000000000004';
    v_contact5_id UUID := 'c0000000-0000-0000-0000-000000000005';
    v_step1_id UUID := 'd0000000-0000-0000-0000-000000000001';
    v_step2_id UUID := 'd0000000-0000-0000-0000-000000000002';
    v_step3_id UUID := 'd0000000-0000-0000-0000-000000000003';
    v_step4_id UUID := 'd0000000-0000-0000-0000-000000000004';
    v_step5_id UUID := 'd0000000-0000-0000-0000-000000000005';
BEGIN
    -- Get admin user ID
    SELECT user_id INTO v_admin_id FROM users WHERE username = 'admin' LIMIT 1;

    -- -------------------------------------------------------
    -- 1. Contact List: "Tutorial Contacts"
    -- -------------------------------------------------------
    INSERT INTO contact_lists (list_id, name, description, owner_user_id, is_shared)
    VALUES (
        v_list_id,
        'Tutorial Contacts',
        'Sample contact list created for the Tutorial campaign. These are fictional contacts to help you explore the application.',
        v_admin_id,
        false
    )
    ON CONFLICT (list_id) DO NOTHING;

    -- -------------------------------------------------------
    -- 2. Contacts (5 fictional contacts)
    -- -------------------------------------------------------
    INSERT INTO contacts (contact_id, list_id, first_name, last_name, email, company, position, phone, linkedin_url, source)
    VALUES
        (v_contact1_id, v_list_id, 'Alice',   'Martin',   'alice.martin@example.com',   'Acme Corp',       'Marketing Director',  '+1-555-0101', 'https://linkedin.com/in/alicemartin',   'Tutorial'),
        (v_contact2_id, v_list_id, 'Bob',     'Johnson',  'bob.johnson@example.com',    'Globex Inc',      'VP of Sales',         '+1-555-0102', 'https://linkedin.com/in/bobjohnson',   'Tutorial'),
        (v_contact3_id, v_list_id, 'Clara',   'Dubois',   'clara.dubois@example.com',   'Initech Ltd',     'CTO',                 '+1-555-0103', 'https://linkedin.com/in/claradubois',  'Tutorial'),
        (v_contact4_id, v_list_id, 'David',   'Chen',     'david.chen@example.com',     'Umbrella Corp',   'Head of Operations',  '+1-555-0104', 'https://linkedin.com/in/davidchen',    'Tutorial'),
        (v_contact5_id, v_list_id, 'Emma',    'Wilson',   'emma.wilson@example.com',    'Stark Industries', 'Product Manager',     '+1-555-0105', 'https://linkedin.com/in/emmawilson',   'Tutorial')
    ON CONFLICT (list_id, email) DO NOTHING;

    -- -------------------------------------------------------
    -- 3. Campaign: "Tutorial"
    -- -------------------------------------------------------
    INSERT INTO campaigns (campaign_id, name, description, campaign_ref, owner_user_id, contact_list_id, status,
                           inter_email_delay_minutes, sequence_step_delay_days,
                           sending_window_start, sending_window_end, sending_days,
                           randomization_minutes, daily_send_limit)
    VALUES (
        v_campaign_id,
        'Tutorial',
        'Example campaign to help you get started. It contains 5 email steps and 5 sample contacts. Review the email templates to understand how merge tags like {{FirstName}} and {{Company}} work.',
        'ISIT-250000',
        v_admin_id,
        v_list_id,
        'Draft',
        30,     -- 30 min between emails
        3,      -- 3 days between steps
        '09:00',
        '17:00',
        'Mon,Tue,Wed,Thu,Fri',
        15,     -- 15 min randomization window
        50      -- daily limit
    )
    ON CONFLICT (campaign_ref) DO NOTHING;

    -- -------------------------------------------------------
    -- 4. Email Steps (5-step sequence)
    -- -------------------------------------------------------

    -- Step 1: Introduction (sent immediately)
    INSERT INTO email_steps (step_id, campaign_id, step_number, subject_template, body_template, delay_days, is_active)
    VALUES (
        v_step1_id,
        v_campaign_id,
        1,
        'Hi {{FirstName}}, quick introduction',
        'Hi {{FirstName}},

I hope this message finds you well. My name is [Your Name] and I work with companies like {{Company}} to help them [describe your value proposition].

I noticed your role as {{Position}} and thought this could be relevant to your team.

Would you be open to a brief conversation this week?

Best regards,
[Your Name]',
        0,
        true
    )
    ON CONFLICT (campaign_id, step_number) DO NOTHING;

    -- Step 2: Value proposition (Day 3)
    INSERT INTO email_steps (step_id, campaign_id, step_number, subject_template, body_template, delay_days, is_active)
    VALUES (
        v_step2_id,
        v_campaign_id,
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
        true
    )
    ON CONFLICT (campaign_id, step_number) DO NOTHING;

    -- Step 3: Social proof (Day 6)
    INSERT INTO email_steps (step_id, campaign_id, step_number, subject_template, body_template, delay_days, is_active)
    VALUES (
        v_step3_id,
        v_campaign_id,
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
        true
    )
    ON CONFLICT (campaign_id, step_number) DO NOTHING;

    -- Step 4: Direct ask (Day 9)
    INSERT INTO email_steps (step_id, campaign_id, step_number, subject_template, body_template, delay_days, is_active)
    VALUES (
        v_step4_id,
        v_campaign_id,
        4,
        'Quick question, {{FirstName}}',
        'Hi {{FirstName}},

I have sent a few messages and want to make sure I am reaching the right person at {{Company}}.

Are you the best person to discuss [topic]? If not, could you point me in the right direction?

Either way, I appreciate your time.

Thanks,
[Your Name]',
        3,
        true
    )
    ON CONFLICT (campaign_id, step_number) DO NOTHING;

    -- Step 5: Breakup / last chance (Day 12)
    INSERT INTO email_steps (step_id, campaign_id, step_number, subject_template, body_template, delay_days, is_active)
    VALUES (
        v_step5_id,
        v_campaign_id,
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
        true
    )
    ON CONFLICT (campaign_id, step_number) DO NOTHING;

    -- -------------------------------------------------------
    -- 5. Campaign Contacts (enroll all 5 contacts)
    -- -------------------------------------------------------
    INSERT INTO campaign_contacts (campaign_id, contact_id, status, current_step)
    VALUES
        (v_campaign_id, v_contact1_id, 'Pending', 0),
        (v_campaign_id, v_contact2_id, 'Pending', 0),
        (v_campaign_id, v_contact3_id, 'Pending', 0),
        (v_campaign_id, v_contact4_id, 'Pending', 0),
        (v_campaign_id, v_contact5_id, 'Pending', 0)
    ON CONFLICT (campaign_id, contact_id) DO NOTHING;

END $$;

COMMIT;
