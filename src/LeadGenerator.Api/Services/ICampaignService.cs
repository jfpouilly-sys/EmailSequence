using LeadGenerator.Api.Models.DTOs;
using LeadGenerator.Api.Models.Requests;

namespace LeadGenerator.Api.Services;

public interface ICampaignService
{
    Task<IEnumerable<CampaignDto>> GetAllCampaignsAsync(Guid? userId = null);
    Task<CampaignDto?> GetCampaignByIdAsync(Guid campaignId);
    Task<CampaignDto> CreateCampaignAsync(CreateCampaignRequest request, Guid userId);
    Task<bool> UpdateCampaignAsync(Guid campaignId, CreateCampaignRequest request);
    Task<bool> DeleteCampaignAsync(Guid campaignId);
    Task<bool> ActivateCampaignAsync(Guid campaignId);
    Task<bool> PauseCampaignAsync(Guid campaignId);
}
