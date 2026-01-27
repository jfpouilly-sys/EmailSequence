using LeadGenerator.Core.Enums;

namespace LeadGenerator.Core.Entities;

public class Campaign
{
    public Guid CampaignId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string CampaignRef { get; set; } = string.Empty; // ISIT-25xxxx

    public Guid? OwnerUserId { get; set; }
    public User? OwnerUser { get; set; }

    public Guid? ContactListId { get; set; }
    public ContactList? ContactList { get; set; }

    public CampaignStatus Status { get; set; } = CampaignStatus.Draft;

    // Sending Configuration
    public int InterEmailDelayMinutes { get; set; } = 30;
    public int SequenceStepDelayDays { get; set; } = 3;
    public TimeSpan SendingWindowStart { get; set; } = new TimeSpan(9, 0, 0);
    public TimeSpan SendingWindowEnd { get; set; } = new TimeSpan(17, 0, 0);
    public string SendingDays { get; set; } = "Mon,Tue,Wed,Thu,Fri";
    public int RandomizationMinutes { get; set; } = 15;
    public int DailySendLimit { get; set; } = 50;

    // Dates
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<EmailStep> EmailSteps { get; set; } = new List<EmailStep>();
    public ICollection<CampaignMailAccount> CampaignMailAccounts { get; set; } = new List<CampaignMailAccount>();
    public ICollection<CampaignContact> CampaignContacts { get; set; } = new List<CampaignContact>();
    public ICollection<ABTest> ABTests { get; set; } = new List<ABTest>();
    public ICollection<SuppressionEntry> SuppressionEntries { get; set; } = new List<SuppressionEntry>();
}
