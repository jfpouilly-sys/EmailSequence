namespace LeadGenerator.Core.Entities;

public class MailAccount
{
    public Guid AccountId { get; set; }
    public string AccountName { get; set; } = string.Empty;
    public string EmailAddress { get; set; } = string.Empty;
    public string? WorkstationId { get; set; }
    public int DailyLimit { get; set; } = 50;
    public int HourlyLimit { get; set; } = 10;
    public int CurrentDailyCount { get; set; } = 0;
    public DateTime? LastCountReset { get; set; }
    public bool IsActive { get; set; } = true;
    public bool WarmupMode { get; set; } = false;
    public DateTime? WarmupStartDate { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<UserMailAccount> UserMailAccounts { get; set; } = new List<UserMailAccount>();
    public ICollection<CampaignMailAccount> CampaignMailAccounts { get; set; } = new List<CampaignMailAccount>();
    public ICollection<EmailLog> EmailLogs { get; set; } = new List<EmailLog>();
}
