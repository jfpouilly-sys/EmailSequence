using LeadGenerator.Core.Entities;
using LeadGenerator.Core.Enums;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.Text.RegularExpressions;

namespace LeadGenerator.MailService.Services;

public class EmailSenderService : IEmailSenderService
{
    private readonly LeadGenDbContext _context;
    private readonly IOutlookService _outlookService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<EmailSenderService> _logger;
    private readonly string _workstationId;

    public EmailSenderService(
        LeadGenDbContext context,
        IOutlookService outlookService,
        IConfiguration configuration,
        ILogger<EmailSenderService> logger)
    {
        _context = context;
        _outlookService = outlookService;
        _configuration = configuration;
        _logger = logger;
        _workstationId = configuration["WorkstationId"] ?? "UNKNOWN";
    }

    public async Task ProcessQueueAsync(CancellationToken cancellationToken)
    {
        try
        {
            // Get mail accounts assigned to this workstation
            var mailAccounts = await _context.MailAccounts
                .Where(ma => ma.WorkstationId == _workstationId && ma.IsActive)
                .ToListAsync(cancellationToken);

            if (!mailAccounts.Any())
            {
                _logger.LogDebug("No mail accounts assigned to workstation {WorkstationId}", _workstationId);
                return;
            }

            // Get pending campaign contacts that are due to be sent
            var now = DateTime.UtcNow;
            var pendingContacts = await _context.CampaignContacts
                .Include(cc => cc.Campaign)
                .Include(cc => cc.Contact)
                .Include(cc => cc.AssignedMailAccount)
                .Where(cc =>
                    cc.Status == ContactStatus.Pending &&
                    cc.NextEmailScheduledAt <= now &&
                    cc.Campaign.Status == CampaignStatus.Active &&
                    mailAccounts.Select(ma => ma.AccountId).Contains(cc.AssignedMailAccountId!.Value))
                .OrderBy(cc => cc.NextEmailScheduledAt)
                .Take(50) // Process in batches
                .ToListAsync(cancellationToken);

            _logger.LogInformation("Processing {Count} pending emails", pendingContacts.Count);

            foreach (var campaignContact in pendingContacts)
            {
                if (cancellationToken.IsCancellationRequested)
                    break;

                await ProcessCampaignContactAsync(campaignContact, cancellationToken);

                // Delay between emails
                var delay = campaignContact.Campaign.InterEmailDelayMinutes;
                var randomization = campaignContact.Campaign.RandomizationMinutes;
                var totalDelay = delay + Random.Shared.Next(-randomization, randomization + 1);
                await Task.Delay(TimeSpan.FromMinutes(totalDelay), cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing email queue");
        }
    }

    private async Task ProcessCampaignContactAsync(CampaignContact campaignContact, CancellationToken cancellationToken)
    {
        try
        {
            // Get the email step to send
            var step = await _context.EmailSteps
                .Include(es => es.Attachments)
                .FirstOrDefaultAsync(es =>
                    es.CampaignId == campaignContact.CampaignId &&
                    es.StepNumber == campaignContact.CurrentStep + 1,
                    cancellationToken);

            if (step == null)
            {
                _logger.LogWarning("No email step found for campaign {CampaignId}, step {Step}",
                    campaignContact.CampaignId, campaignContact.CurrentStep + 1);
                return;
            }

            // Apply merge tags
            var subject = ApplyMergeTags(step.SubjectTemplate, campaignContact.Contact);
            var body = ApplyMergeTags(step.BodyTemplate, campaignContact.Contact);

            // Add campaign reference to subject
            subject = $"{subject} [{campaignContact.Campaign.CampaignRef}]";

            // Handle attachments
            var attachmentPaths = step.Attachments
                .Where(a => a.DeliveryMode == DeliveryMode.Attachment)
                .Select(a => a.FilePath)
                .ToList();

            // Send email
            var success = await _outlookService.SendEmailAsync(
                campaignContact.Contact.Email,
                subject,
                body,
                attachmentPaths.Any() ? attachmentPaths : null);

            if (success)
            {
                // Update campaign contact
                campaignContact.CurrentStep++;
                campaignContact.LastEmailSentAt = DateTime.UtcNow;
                campaignContact.Status = ContactStatus.InProgress;

                // Schedule next email if there are more steps
                var nextStep = await _context.EmailSteps
                    .FirstOrDefaultAsync(es =>
                        es.CampaignId == campaignContact.CampaignId &&
                        es.StepNumber == campaignContact.CurrentStep + 1,
                        cancellationToken);

                if (nextStep != null)
                {
                    campaignContact.NextEmailScheduledAt = DateTime.UtcNow.AddDays(nextStep.DelayDays);
                }
                else
                {
                    campaignContact.Status = ContactStatus.Completed;
                }

                campaignContact.UpdatedAt = DateTime.UtcNow;

                // Log email
                _context.EmailLogs.Add(new EmailLog
                {
                    LogId = Guid.NewGuid(),
                    CampaignId = campaignContact.CampaignId,
                    ContactId = campaignContact.ContactId,
                    StepId = step.StepId,
                    MailAccountId = campaignContact.AssignedMailAccountId,
                    Subject = subject,
                    SentAt = DateTime.UtcNow,
                    Status = "Sent"
                });

                await _context.SaveChangesAsync(cancellationToken);

                _logger.LogInformation("Email sent to {Email} for campaign {CampaignRef}",
                    campaignContact.Contact.Email, campaignContact.Campaign.CampaignRef);
            }
            else
            {
                _logger.LogError("Failed to send email to {Email}", campaignContact.Contact.Email);

                // Log failed email
                _context.EmailLogs.Add(new EmailLog
                {
                    LogId = Guid.NewGuid(),
                    CampaignId = campaignContact.CampaignId,
                    ContactId = campaignContact.ContactId,
                    StepId = step.StepId,
                    MailAccountId = campaignContact.AssignedMailAccountId,
                    Subject = subject,
                    SentAt = DateTime.UtcNow,
                    Status = "Failed",
                    ErrorMessage = "Failed to send email via Outlook"
                });

                await _context.SaveChangesAsync(cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing campaign contact {ContactId}", campaignContact.ContactId);
        }
    }

    private string ApplyMergeTags(string template, Contact contact)
    {
        var result = template;

        var mergeData = new Dictionary<string, string?>
        {
            { "FirstName", contact.FirstName },
            { "LastName", contact.LastName },
            { "Email", contact.Email },
            { "Company", contact.Company },
            { "Position", contact.Position },
            { "Title", contact.Title },
            { "Phone", contact.Phone },
            { "Custom1", contact.Custom1 },
            { "Custom2", contact.Custom2 },
            { "Custom3", contact.Custom3 },
            { "Custom4", contact.Custom4 },
            { "Custom5", contact.Custom5 },
            { "Custom6", contact.Custom6 },
            { "Custom7", contact.Custom7 },
            { "Custom8", contact.Custom8 },
            { "Custom9", contact.Custom9 },
            { "Custom10", contact.Custom10 }
        };

        foreach (var kvp in mergeData)
        {
            var pattern = $@"{{{{{kvp.Key}}}}}";
            result = Regex.Replace(result, pattern, kvp.Value ?? string.Empty, RegexOptions.IgnoreCase);
        }

        return result;
    }
}
