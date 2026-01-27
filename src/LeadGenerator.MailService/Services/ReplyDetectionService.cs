using LeadGenerator.Core.Enums;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using System.Text.RegularExpressions;

namespace LeadGenerator.MailService.Services;

public class ReplyDetectionService : IReplyDetectionService
{
    private readonly LeadGenDbContext _context;
    private readonly IOutlookService _outlookService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<ReplyDetectionService> _logger;

    public ReplyDetectionService(
        LeadGenDbContext context,
        IOutlookService outlookService,
        IConfiguration configuration,
        ILogger<ReplyDetectionService> logger)
    {
        _context = context;
        _outlookService = outlookService;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task ScanForRepliesAsync(CancellationToken cancellationToken)
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
                    await ProcessReplyAsync(email, cancellationToken);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error scanning for replies");
        }
    }

    private async Task ProcessReplyAsync(EmailMessage email, CancellationToken cancellationToken)
    {
        try
        {
            // Extract campaign reference from subject (ISIT-25xxxx)
            var campaignRef = ExtractCampaignRef(email.Subject);
            if (string.IsNullOrEmpty(campaignRef))
            {
                _logger.LogDebug("No campaign reference found in email subject");
                return;
            }

            // Find campaign by reference
            var campaign = await _context.Campaigns
                .FirstOrDefaultAsync(c => c.CampaignRef == campaignRef, cancellationToken);

            if (campaign == null)
            {
                _logger.LogWarning("Campaign not found for reference {CampaignRef}", campaignRef);
                return;
            }

            // Find contact by email
            var contact = await _context.Contacts
                .FirstOrDefaultAsync(c => c.Email.ToLower() == email.SenderEmail.ToLower(), cancellationToken);

            if (contact == null)
            {
                _logger.LogDebug("Contact not found for email {Email}", email.SenderEmail);
                return;
            }

            // Update campaign contact status
            var campaignContact = await _context.CampaignContacts
                .FirstOrDefaultAsync(cc =>
                    cc.CampaignId == campaign.CampaignId &&
                    cc.ContactId == contact.ContactId,
                    cancellationToken);

            if (campaignContact != null)
            {
                campaignContact.Status = ContactStatus.Responded;
                campaignContact.RespondedAt = DateTime.UtcNow;
                campaignContact.UpdatedAt = DateTime.UtcNow;

                await _context.SaveChangesAsync(cancellationToken);

                _logger.LogInformation("Reply detected from {Email} for campaign {CampaignRef}",
                    email.SenderEmail, campaignRef);

                // Mark email as read and move to processed folder
                await _outlookService.MarkAsReadAsync(email);
                await _outlookService.MoveEmailToFolderAsync(email, "Processed");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing reply from {Email}", email.SenderEmail);
        }
    }

    private string? ExtractCampaignRef(string subject)
    {
        var match = Regex.Match(subject, @"\[?(ISIT-\d{6})\]?", RegexOptions.IgnoreCase);
        return match.Success ? match.Groups[1].Value : null;
    }
}
