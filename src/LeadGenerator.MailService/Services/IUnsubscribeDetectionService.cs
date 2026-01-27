namespace LeadGenerator.MailService.Services;

public interface IUnsubscribeDetectionService
{
    Task ScanForUnsubscribesAsync(CancellationToken cancellationToken);
}
