namespace LeadGenerator.MailService.Services;

public interface IOutlookService
{
    Task<bool> SendEmailAsync(string to, string subject, string body, List<string>? attachmentPaths = null);
    Task<List<EmailMessage>> GetUnreadEmailsAsync(string folderName = "Inbox");
    Task MoveEmailToFolderAsync(EmailMessage email, string targetFolderName);
    Task MarkAsReadAsync(EmailMessage email);
}

public class EmailMessage
{
    public string EntryId { get; set; } = string.Empty;
    public string SenderEmail { get; set; } = string.Empty;
    public string Subject { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public DateTime ReceivedTime { get; set; }
}
