namespace LeadGenerator.Core.Entities;

public class EmailStep
{
    public Guid StepId { get; set; }
    public Guid CampaignId { get; set; }
    public Campaign Campaign { get; set; } = null!;

    public int StepNumber { get; set; }
    public string SubjectTemplate { get; set; } = string.Empty;
    public string BodyTemplate { get; set; } = string.Empty;
    public int DelayDays { get; set; } = 0; // Days after previous step
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<Attachment> Attachments { get; set; } = new List<Attachment>();
    public ICollection<EmailLog> EmailLogs { get; set; } = new List<EmailLog>();
    public ICollection<ABTest> ABTests { get; set; } = new List<ABTest>();
}
