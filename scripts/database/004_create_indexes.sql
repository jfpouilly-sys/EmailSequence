-- Create indexes for better query performance

CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_list_id ON contacts(list_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_owner ON campaigns(owner_user_id);
CREATE INDEX idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX idx_campaign_contacts_next_scheduled ON campaign_contacts(next_email_scheduled_at);
CREATE INDEX idx_email_logs_campaign ON email_logs(campaign_id);
CREATE INDEX idx_email_logs_contact ON email_logs(contact_id);
CREATE INDEX idx_email_logs_sent_at ON email_logs(sent_at);
CREATE INDEX idx_download_logs_attachment ON download_logs(attachment_id);
CREATE INDEX idx_suppression_email ON suppression_list(email);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
