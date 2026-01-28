namespace LeadGenerator.Api.Services;

public interface IReportService
{
    Task<object> GetCampaignStatisticsAsync(Guid campaignId);
    Task<object> GetOverallStatisticsAsync(Guid? userId = null);
}
