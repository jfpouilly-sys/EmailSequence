using LeadGenerator.Core.Enums;

namespace LeadGenerator.Core.Entities;

public class CampaignContact
{
    public Guid CampaignId { get; set; }
    public Campaign Campaign { get; set; } = null!;

    public Guid ContactId { get; set; }
    public Contact Contact { get; set; } = null!;

    public ContactStatus Status { get; set; } = ContactStatus.Pending;
    public Guid? AssignedMailAccountId { get; set; }
    public MailAccount? AssignedMailAccount { get; set; }

    public int CurrentStep { get; set; } = 0;
    public DateTime? LastEmailSentAt { get; set; }
    public DateTime? NextEmailScheduledAt { get; set; }
    public DateTime? RespondedAt { get; set; }
    public char? ABTestVariant { get; set; } // 'A' or 'B'
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
