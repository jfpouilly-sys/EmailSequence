namespace LeadGenerator.MailService.Services;

public interface IEmailSenderService
{
    Task ProcessQueueAsync(CancellationToken cancellationToken);
}
