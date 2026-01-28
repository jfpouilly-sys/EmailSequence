namespace LeadGenerator.Core.Entities;

public class EmailLog
{
    public Guid LogId { get; set; }

    public Guid? CampaignId { get; set; }
    public Campaign? Campaign { get; set; }

    public Guid? ContactId { get; set; }
    public Contact? Contact { get; set; }

    public Guid? StepId { get; set; }
    public EmailStep? EmailStep { get; set; }

    public Guid? MailAccountId { get; set; }
    public MailAccount? MailAccount { get; set; }

    public string? Subject { get; set; }
    public DateTime SentAt { get; set; } = DateTime.UtcNow;
    public string Status { get; set; } = string.Empty; // 'Sent', 'Failed', 'Bounced'
    public string? ErrorMessage { get; set; }
    public string? OutlookEntryId { get; set; }
}
