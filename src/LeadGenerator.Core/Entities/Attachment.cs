using LeadGenerator.Core.Enums;

namespace LeadGenerator.Core.Entities;

public class Attachment
{
    public Guid AttachmentId { get; set; }
    public Guid StepId { get; set; }
    public EmailStep EmailStep { get; set; } = null!;

    public string FileName { get; set; } = string.Empty;
    public string FilePath { get; set; } = string.Empty;
    public long FileSize { get; set; }
    public string? MimeType { get; set; }
    public DeliveryMode DeliveryMode { get; set; } = DeliveryMode.Attachment;
    public string? LinkText { get; set; }
    public int? ExpirationDays { get; set; }
    public string? DownloadToken { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<DownloadLog> DownloadLogs { get; set; } = new List<DownloadLog>();
}
