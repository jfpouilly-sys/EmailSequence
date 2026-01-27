using LeadGenerator.Core.Enums;

namespace LeadGenerator.Core.Entities;

public class ABTest
{
    public Guid TestId { get; set; }

    public Guid CampaignId { get; set; }
    public Campaign Campaign { get; set; } = null!;

    public Guid StepId { get; set; }
    public EmailStep EmailStep { get; set; } = null!;

    public ABTestElement TestElement { get; set; }
    public string VariantAContent { get; set; } = string.Empty;
    public string VariantBContent { get; set; } = string.Empty;
    public decimal SplitRatio { get; set; } = 0.50m;
    public string SuccessMetric { get; set; } = "ResponseRate";
    public int MinSampleSize { get; set; } = 100;
    public int MaxDurationDays { get; set; } = 14;
    public ABTestStatus Status { get; set; } = ABTestStatus.Running;
    public char? WinnerVariant { get; set; } // 'A', 'B', or null
    public decimal? ConfidenceLevel { get; set; }
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
}
