using LeadGenerator.Core.Entities;
using LeadGenerator.Core.Enums;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;

namespace LeadGenerator.Api.Services;

public class SuppressionService : ISuppressionService
{
    private readonly LeadGenDbContext _context;
    private readonly ILogger<SuppressionService> _logger;

    public SuppressionService(LeadGenDbContext context, ILogger<SuppressionService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<bool> IsEmailSuppressedAsync(string email, Guid? campaignId = null)
    {
        var normalizedEmail = email.ToLower();

        // Check global suppression
        var globalSuppression = await _context.SuppressionList
            .AnyAsync(s => s.Email == normalizedEmail && s.Scope == UnsubscribeScope.Global);

        if (globalSuppression) return true;

        // Check campaign-specific suppression
        if (campaignId.HasValue)
        {
            var campaignSuppression = await _context.SuppressionList
                .AnyAsync(s => s.Email == normalizedEmail &&
                              s.Scope == UnsubscribeScope.Campaign &&
                              s.CampaignId == campaignId.Value);

            if (campaignSuppression) return true;
        }

        return false;
    }

    public async Task AddToSuppressionListAsync(string email, UnsubscribeScope scope, UnsubscribeSource source, Guid? campaignId = null, string? reason = null)
    {
        var normalizedEmail = email.ToLower();

        // Check if already in suppression list
        var exists = await _context.SuppressionList.AnyAsync(s => s.Email == normalizedEmail);
        if (exists)
        {
            _logger.LogInformation("Email {Email} already in suppression list", normalizedEmail);
            return;
        }

        var suppression = new SuppressionEntry
        {
            Email = normalizedEmail,
            Scope = scope,
            Source = source,
            CampaignId = campaignId,
            Reason = reason,
            CreatedAt = DateTime.UtcNow
        };

        _context.SuppressionList.Add(suppression);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Added {Email} to suppression list (Scope: {Scope}, Source: {Source})",
            normalizedEmail, scope, source);
    }

    public async Task<IEnumerable<object>> GetSuppressionListAsync()
    {
        var suppressions = await _context.SuppressionList
            .OrderByDescending(s => s.CreatedAt)
            .Select(s => new
            {
                s.Email,
                Scope = s.Scope.ToString(),
                Source = s.Source.ToString(),
                s.CampaignId,
                s.Reason,
                s.CreatedAt
            })
            .ToListAsync();

        return suppressions;
    }
}
