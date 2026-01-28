using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;

namespace LeadGenerator.Api.Services;

public class ReportService : IReportService
{
    private readonly LeadGenDbContext _context;

    public ReportService(LeadGenDbContext context)
    {
        _context = context;
    }

    public async Task<object> GetCampaignStatisticsAsync(Guid campaignId)
    {
        var campaign = await _context.Campaigns
            .Include(c => c.CampaignContacts)
            .FirstOrDefaultAsync(c => c.CampaignId == campaignId);

        if (campaign == null)
            throw new InvalidOperationException("Campaign not found");

        var totalContacts = campaign.CampaignContacts.Count;
        var sentCount = await _context.EmailLogs.CountAsync(el => el.CampaignId == campaignId && el.Status == "Sent");
        var respondedCount = campaign.CampaignContacts.Count(cc => cc.RespondedAt.HasValue);
        var unsubscribedCount = campaign.CampaignContacts.Count(cc => cc.Status == Core.Enums.ContactStatus.Unsubscribed);

        return new
        {
            CampaignId = campaignId,
            CampaignName = campaign.Name,
            TotalContacts = totalContacts,
            EmailsSent = sentCount,
            ResponseRate = totalContacts > 0 ? (double)respondedCount / totalContacts * 100 : 0,
            UnsubscribeRate = totalContacts > 0 ? (double)unsubscribedCount / totalContacts * 100 : 0,
            Responded = respondedCount,
            Unsubscribed = unsubscribedCount
        };
    }

    public async Task<object> GetOverallStatisticsAsync(Guid? userId = null)
    {
        var campaignsQuery = _context.Campaigns.AsQueryable();
        if (userId.HasValue)
        {
            campaignsQuery = campaignsQuery.Where(c => c.OwnerUserId == userId.Value);
        }

        var totalCampaigns = await campaignsQuery.CountAsync();
        var activeCampaigns = await campaignsQuery.CountAsync(c => c.Status == Core.Enums.CampaignStatus.Active);
        var totalEmailsSent = await _context.EmailLogs.CountAsync(el => el.Status == "Sent");
        var totalContacts = await _context.Contacts.CountAsync();

        return new
        {
            TotalCampaigns = totalCampaigns,
            ActiveCampaigns = activeCampaigns,
            TotalEmailsSent = totalEmailsSent,
            TotalContacts = totalContacts
        };
    }
}
