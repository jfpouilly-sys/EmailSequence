using Microsoft.Extensions.Logging;
using Outlook = Microsoft.Office.Interop.Outlook;

namespace LeadGenerator.MailService.Services;

public class OutlookService : IOutlookService
{
    private readonly ILogger<OutlookService> _logger;
    private Outlook.Application? _outlookApp;
    private Outlook.NameSpace? _nameSpace;

    public OutlookService(ILogger<OutlookService> logger)
    {
        _logger = logger;
        InitializeOutlook();
    }

    private void InitializeOutlook()
    {
        try
        {
            _outlookApp = new Outlook.Application();
            _nameSpace = _outlookApp.GetNamespace("MAPI");
            _logger.LogInformation("Outlook COM Interop initialized successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to initialize Outlook COM Interop");
            throw;
        }
    }

    public async Task<bool> SendEmailAsync(string to, string subject, string body, List<string>? attachmentPaths = null)
    {
        return await Task.Run(() =>
        {
            try
            {
                if (_outlookApp == null)
                {
                    _logger.LogError("Outlook application not initialized");
                    return false;
                }

                Outlook.MailItem mailItem = (Outlook.MailItem)_outlookApp.CreateItem(Outlook.OlItemType.olMailItem);
                mailItem.To = to;
                mailItem.Subject = subject;
                mailItem.HTMLBody = body;

                // Add attachments
                if (attachmentPaths != null && attachmentPaths.Any())
                {
                    foreach (var path in attachmentPaths)
                    {
                        if (File.Exists(path))
                        {
                            mailItem.Attachments.Add(path);
                        }
                    }
                }

                mailItem.Send();
                _logger.LogInformation("Email sent successfully to {To}", to);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send email to {To}", to);
                return false;
            }
        });
    }

    public async Task<List<EmailMessage>> GetUnreadEmailsAsync(string folderName = "Inbox")
    {
        return await Task.Run(() =>
        {
            var messages = new List<EmailMessage>();

            try
            {
                if (_nameSpace == null)
                {
                    _logger.LogError("Outlook namespace not initialized");
                    return messages;
                }

                var folder = _nameSpace.GetDefaultFolder(Outlook.OlDefaultFolders.olFolderInbox);

                // Try to find the specified folder
                if (folderName != "Inbox")
                {
                    try
                    {
                        folder = folder.Folders[folderName];
                    }
                    catch
                    {
                        _logger.LogWarning("Folder {FolderName} not found, using Inbox", folderName);
                    }
                }

                var items = folder.Items.Restrict("[Unread]=true");

                foreach (Outlook.MailItem item in items)
                {
                    messages.Add(new EmailMessage
                    {
                        EntryId = item.EntryID,
                        SenderEmail = item.SenderEmailAddress ?? "",
                        Subject = item.Subject ?? "",
                        Body = item.Body ?? "",
                        ReceivedTime = item.ReceivedTime
                    });
                }

                _logger.LogDebug("Retrieved {Count} unread emails from {Folder}", messages.Count, folderName);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get unread emails from {Folder}", folderName);
            }

            return messages;
        });
    }

    public async Task MoveEmailToFolderAsync(EmailMessage email, string targetFolderName)
    {
        await Task.Run(() =>
        {
            try
            {
                if (_nameSpace == null) return;

                var mailItem = _nameSpace.GetItemFromID(email.EntryId) as Outlook.MailItem;
                if (mailItem != null)
                {
                    var inbox = _nameSpace.GetDefaultFolder(Outlook.OlDefaultFolders.olFolderInbox);
                    var targetFolder = inbox.Folders[targetFolderName];
                    mailItem.Move(targetFolder);
                    _logger.LogDebug("Moved email to {Folder}", targetFolderName);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to move email to {Folder}", targetFolderName);
            }
        });
    }

    public async Task MarkAsReadAsync(EmailMessage email)
    {
        await Task.Run(() =>
        {
            try
            {
                if (_nameSpace == null) return;

                var mailItem = _nameSpace.GetItemFromID(email.EntryId) as Outlook.MailItem;
                if (mailItem != null)
                {
                    mailItem.UnRead = false;
                    mailItem.Save();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to mark email as read");
            }
        });
    }
}
