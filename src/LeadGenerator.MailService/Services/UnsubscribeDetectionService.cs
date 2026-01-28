using LeadGenerator.Core.Entities;
using LeadGenerator.Core.Enums;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Text.RegularExpressions;

namespace LeadGenerator.MailService.Services;

public class UnsubscribeDetectionService : IUnsubscribeDetectionService
{
    private readonly LeadGenDbContext _context;
    private readonly IOutlookService _outlookService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<UnsubscribeDetectionService> _logger;
    private readonly List<string> _keywordsEN;
    private readonly List<string> _keywordsFR;

    public UnsubscribeDetectionService(
        LeadGenDbContext context,
        IOutlookService outlookService,
        IConfiguration configuration,
        ILogger<UnsubscribeDetectionService> logger)
    {
        _context = context;
        _outlookService = outlookService;
        _configuration = configuration;
        _logger = logger;

        _keywordsEN = configuration.GetSection("Unsubscribe:KeywordsEN").Get<List<string>>() ?? new List<string>();
        _keywordsFR = configuration.GetSection("Unsubscribe:KeywordsFR").Get<List<string>>() ?? new List<string>();
    }

    public async Task ScanForUnsubscribesAsync(CancellationToken cancellationToken)
    {
        try
        {
            var folders = _configuration.GetSection("Outlook:ScanFolders").Get<List<string>>() ?? new List<string> { "Inbox" };

            foreach (var folderName in folders)
            {
                if (cancellationToken.IsCancellationRequested)
                    break;

                var emails = await _outlookService.GetUnreadEmailsAsync(folderName);

                foreach (var email in emails)
                {
                    if (ContainsUnsubscribeKeyword(email.Subject) || ContainsUnsubscribeKeyword(email.Body))
                    {
                        await ProcessUnsubscribeAsync(email, cancellationToken);
                    }
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error scanning for unsubscribes");
        }
    }

    private bool ContainsUnsubscribeKeyword(string text)
    {
        if (string.IsNullOrEmpty(text)) return false;

        var upperText = text.ToUpperInvariant();
        var allKeywords = _keywordsEN.Concat(_keywordsFR);

        return allKeywords.Any(keyword => upperText.Contains(keyword.ToUpperInvariant()));
    }

    private async Task ProcessUnsubscribeAsync(EmailMessage email, CancellationToken cancellationToken)
    {
        try
        {
            // Find contact by sender email
            var contact = await _context.Contacts
                .FirstOrDefaultAsync(c => c.Email.ToLower() == email.SenderEmail.ToLower(), cancellationToken);

            if (contact == null)
            {
                _logger.LogDebug("Contact not found for email {Email}", email.SenderEmail);
                return;
            }

            // Extract campaign ID from subject if present (ISIT-25xxxx)
            var campaignRef = ExtractCampaignRef(email.Subject);
            Guid? campaignId = null;

            if (!string.IsNullOrEmpty(campaignRef))
            {
                var campaign = await _context.Campaigns
                    .FirstOrDefaultAsync(c => c.CampaignRef == campaignRef, cancellationToken);
                campaignId = campaign?.CampaignId;
            }

            // Determine scope
            var scope = campaignId.HasValue ? UnsubscribeScope.Campaign : UnsubscribeScope.Global;

            // Add to suppression list
            var suppression = new SuppressionEntry
            {
                Email = contact.Email.ToLower(),
                Scope = scope,
                Source = UnsubscribeSource.EmailReply,
                CampaignId = campaignId,
                Reason = "Unsubscribe keyword detected in email",
                CreatedAt = DateTime.UtcNow
            };

            // Check if already exists
            var exists = await _context.SuppressionList
                .AnyAsync(s => s.Email == suppression.Email, cancellationToken);

            if (!exists)
            {
                _context.SuppressionList.Add(suppression);
            }

            // Update campaign contact status
            var campaignContacts = await _context.CampaignContacts
                .Where(cc => cc.ContactId == contact.ContactId)
                .ToListAsync(cancellationToken);

            foreach (var cc in campaignContacts)
            {
                if (!campaignId.HasValue || cc.CampaignId == campaignId.Value)
                {
                    cc.Status = ContactStatus.Unsubscribed;
                    cc.UpdatedAt = DateTime.UtcNow;
                }
            }

            await _context.SaveChangesAsync(cancellationToken);

            _logger.LogInformation("Processed unsubscribe for {Email} (Scope: {Scope})",
                contact.Email, scope);

            // Mark email as read and move to processed folder
            await _outlookService.MarkAsReadAsync(email);
            await _outlookService.MoveEmailToFolderAsync(email, "Processed");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing unsubscribe from {Email}", email.SenderEmail);
        }
    }

    private string? ExtractCampaignRef(string subject)
    {
        var match = Regex.Match(subject, @"\[?(ISIT-\d{6})\]?", RegexOptions.IgnoreCase);
        return match.Success ? match.Groups[1].Value : null;
    }
}
