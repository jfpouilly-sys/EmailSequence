namespace LeadGenerator.Core.Entities;

public class CampaignMailAccount
{
    public Guid CampaignId { get; set; }
    public Campaign Campaign { get; set; } = null!;

    public Guid AccountId { get; set; }
    public MailAccount MailAccount { get; set; } = null!;

    public decimal DistributionWeight { get; set; } = 1.0m;
}
