namespace LeadGenerator.MailService.Services;

public interface IReplyDetectionService
{
    Task ScanForRepliesAsync(CancellationToken cancellationToken);
}
