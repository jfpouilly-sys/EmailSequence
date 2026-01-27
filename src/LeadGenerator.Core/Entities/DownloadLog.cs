namespace LeadGenerator.Core.Entities;

public class DownloadLog
{
    public Guid DownloadId { get; set; }

    public Guid AttachmentId { get; set; }
    public Attachment Attachment { get; set; } = null!;

    public Guid? ContactId { get; set; }
    public Contact? Contact { get; set; }

    public Guid? CampaignId { get; set; }
    public Campaign? Campaign { get; set; }

    public DateTime DownloadedAt { get; set; } = DateTime.UtcNow;
    public string? IpAddress { get; set; }
    public string? UserAgent { get; set; }
}
