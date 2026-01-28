using LeadGenerator.Core.Enums;

namespace LeadGenerator.Api.Models.DTOs;

public class CampaignDto
{
    public Guid CampaignId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string CampaignRef { get; set; } = string.Empty;
    public Guid? OwnerUserId { get; set; }
    public Guid? ContactListId { get; set; }
    public CampaignStatus Status { get; set; }
    public int InterEmailDelayMinutes { get; set; }
    public int SequenceStepDelayDays { get; set; }
    public TimeSpan SendingWindowStart { get; set; }
    public TimeSpan SendingWindowEnd { get; set; }
    public string SendingDays { get; set; } = string.Empty;
    public int RandomizationMinutes { get; set; }
    public int DailySendLimit { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
