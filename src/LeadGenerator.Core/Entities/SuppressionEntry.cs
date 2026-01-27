using LeadGenerator.Core.Enums;

namespace LeadGenerator.Core.Entities;

public class SuppressionEntry
{
    public string Email { get; set; } = string.Empty;
    public UnsubscribeScope Scope { get; set; } = UnsubscribeScope.Global;
    public UnsubscribeSource Source { get; set; }

    public Guid? CampaignId { get; set; }
    public Campaign? Campaign { get; set; }

    public string? Reason { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
