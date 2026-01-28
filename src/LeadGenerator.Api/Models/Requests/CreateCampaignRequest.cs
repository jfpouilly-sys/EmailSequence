namespace LeadGenerator.Api.Models.Requests;

public class CreateCampaignRequest
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public Guid? ContactListId { get; set; }
    public int? InterEmailDelayMinutes { get; set; }
    public int? SequenceStepDelayDays { get; set; }
    public string? SendingWindowStart { get; set; }
    public string? SendingWindowEnd { get; set; }
    public string? SendingDays { get; set; }
    public int? RandomizationMinutes { get; set; }
    public int? DailySendLimit { get; set; }
}
