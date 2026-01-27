using LeadGenerator.Api.Models.DTOs;
using LeadGenerator.Api.Models.Requests;
using LeadGenerator.Core.Entities;
using LeadGenerator.Core.Enums;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;

namespace LeadGenerator.Api.Services;

public class CampaignService : ICampaignService
{
    private readonly LeadGenDbContext _context;
    private readonly IConfiguration _configuration;
    private readonly ILogger<CampaignService> _logger;

    public CampaignService(LeadGenDbContext context, IConfiguration configuration, ILogger<CampaignService> logger)
    {
        _context = context;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<IEnumerable<CampaignDto>> GetAllCampaignsAsync(Guid? userId = null)
    {
        var query = _context.Campaigns.AsQueryable();

        if (userId.HasValue)
        {
            query = query.Where(c => c.OwnerUserId == userId.Value);
        }

        var campaigns = await query
            .OrderByDescending(c => c.CreatedAt)
            .ToListAsync();

        return campaigns.Select(MapToDto);
    }

    public async Task<CampaignDto?> GetCampaignByIdAsync(Guid campaignId)
    {
        var campaign = await _context.Campaigns.FindAsync(campaignId);
        return campaign == null ? null : MapToDto(campaign);
    }

    public async Task<CampaignDto> CreateCampaignAsync(CreateCampaignRequest request, Guid userId)
    {
        var campaignRef = await GenerateCampaignRefAsync();

        var campaign = new Campaign
        {
            CampaignId = Guid.NewGuid(),
            Name = request.Name,
            Description = request.Description,
            CampaignRef = campaignRef,
            OwnerUserId = userId,
            ContactListId = request.ContactListId,
            Status = CampaignStatus.Draft,
            InterEmailDelayMinutes = request.InterEmailDelayMinutes ?? _configuration.GetValue<int>("CampaignDefaults:InterEmailDelayMinutes", 30),
            SequenceStepDelayDays = request.SequenceStepDelayDays ?? _configuration.GetValue<int>("CampaignDefaults:SequenceStepDelayDays", 3),
            SendingWindowStart = TimeSpan.Parse(request.SendingWindowStart ?? _configuration["CampaignDefaults:SendingWindowStart"]!),
            SendingWindowEnd = TimeSpan.Parse(request.SendingWindowEnd ?? _configuration["CampaignDefaults:SendingWindowEnd"]!),
            SendingDays = request.SendingDays ?? _configuration["CampaignDefaults:SendingDays"]!,
            RandomizationMinutes = request.RandomizationMinutes ?? _configuration.GetValue<int>("CampaignDefaults:RandomizationMinutes", 15),
            DailySendLimit = request.DailySendLimit ?? _configuration.GetValue<int>("CampaignDefaults:DailySendLimit", 50),
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        _context.Campaigns.Add(campaign);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Campaign {CampaignId} created by user {UserId}", campaign.CampaignId, userId);

        return MapToDto(campaign);
    }

    public async Task<bool> UpdateCampaignAsync(Guid campaignId, CreateCampaignRequest request)
    {
        var campaign = await _context.Campaigns.FindAsync(campaignId);
        if (campaign == null) return false;

        campaign.Name = request.Name;
        campaign.Description = request.Description;
        campaign.ContactListId = request.ContactListId;

        if (request.InterEmailDelayMinutes.HasValue)
            campaign.InterEmailDelayMinutes = request.InterEmailDelayMinutes.Value;
        if (request.SequenceStepDelayDays.HasValue)
            campaign.SequenceStepDelayDays = request.SequenceStepDelayDays.Value;
        if (!string.IsNullOrEmpty(request.SendingWindowStart))
            campaign.SendingWindowStart = TimeSpan.Parse(request.SendingWindowStart);
        if (!string.IsNullOrEmpty(request.SendingWindowEnd))
            campaign.SendingWindowEnd = TimeSpan.Parse(request.SendingWindowEnd);
        if (!string.IsNullOrEmpty(request.SendingDays))
            campaign.SendingDays = request.SendingDays;
        if (request.RandomizationMinutes.HasValue)
            campaign.RandomizationMinutes = request.RandomizationMinutes.Value;
        if (request.DailySendLimit.HasValue)
            campaign.DailySendLimit = request.DailySendLimit.Value;

        campaign.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<bool> DeleteCampaignAsync(Guid campaignId)
    {
        var campaign = await _context.Campaigns.FindAsync(campaignId);
        if (campaign == null) return false;

        _context.Campaigns.Remove(campaign);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Campaign {CampaignId} deleted", campaignId);
        return true;
    }

    public async Task<bool> ActivateCampaignAsync(Guid campaignId)
    {
        var campaign = await _context.Campaigns.FindAsync(campaignId);
        if (campaign == null) return false;

        campaign.Status = CampaignStatus.Active;
        campaign.StartDate = DateTime.UtcNow;
        campaign.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        _logger.LogInformation("Campaign {CampaignId} activated", campaignId);
        return true;
    }

    public async Task<bool> PauseCampaignAsync(Guid campaignId)
    {
        var campaign = await _context.Campaigns.FindAsync(campaignId);
        if (campaign == null) return false;

        campaign.Status = CampaignStatus.Paused;
        campaign.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
        _logger.LogInformation("Campaign {CampaignId} paused", campaignId);
        return true;
    }

    private async Task<string> GenerateCampaignRefAsync()
    {
        var year = DateTime.UtcNow.Year.ToString().Substring(2);
        var lastRef = await _context.Campaigns
            .Where(c => c.CampaignRef.StartsWith($"ISIT-{year}"))
            .OrderByDescending(c => c.CampaignRef)
            .Select(c => c.CampaignRef)
            .FirstOrDefaultAsync();

        int nextNumber = 1;
        if (lastRef != null && int.TryParse(lastRef.Substring(8), out int currentNumber))
        {
            nextNumber = currentNumber + 1;
        }

        return $"ISIT-{year}{nextNumber:D4}";
    }

    private static CampaignDto MapToDto(Campaign campaign)
    {
        return new CampaignDto
        {
            CampaignId = campaign.CampaignId,
            Name = campaign.Name,
            Description = campaign.Description,
            CampaignRef = campaign.CampaignRef,
            OwnerUserId = campaign.OwnerUserId,
            ContactListId = campaign.ContactListId,
            Status = campaign.Status,
            InterEmailDelayMinutes = campaign.InterEmailDelayMinutes,
            SequenceStepDelayDays = campaign.SequenceStepDelayDays,
            SendingWindowStart = campaign.SendingWindowStart,
            SendingWindowEnd = campaign.SendingWindowEnd,
            SendingDays = campaign.SendingDays,
            RandomizationMinutes = campaign.RandomizationMinutes,
            DailySendLimit = campaign.DailySendLimit,
            StartDate = campaign.StartDate,
            EndDate = campaign.EndDate,
            CreatedAt = campaign.CreatedAt,
            UpdatedAt = campaign.UpdatedAt
        };
    }
}
