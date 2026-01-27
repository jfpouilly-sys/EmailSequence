using LeadGenerator.MailService.Services;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace LeadGenerator.MailService;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly IServiceProvider _serviceProvider;
    private readonly IConfiguration _configuration;

    public Worker(ILogger<Worker> logger, IServiceProvider serviceProvider, IConfiguration configuration)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
        _configuration = configuration;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Lead Generator Mail Service started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();

                // Process email queue
                var emailSender = scope.ServiceProvider.GetRequiredService<IEmailSenderService>();
                await emailSender.ProcessQueueAsync(stoppingToken);

                // Check for replies
                var replyDetector = scope.ServiceProvider.GetRequiredService<IReplyDetectionService>();
                await replyDetector.ScanForRepliesAsync(stoppingToken);

                // Check for unsubscribes
                var unsubDetector = scope.ServiceProvider.GetRequiredService<IUnsubscribeDetectionService>();
                await unsubDetector.ScanForUnsubscribesAsync(stoppingToken);

                _logger.LogDebug("Mail service cycle completed");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in mail service worker");
            }

            var interval = _configuration.GetValue<int>("ScanIntervalSeconds", 60);
            await Task.Delay(TimeSpan.FromSeconds(interval), stoppingToken);
        }

        _logger.LogInformation("Lead Generator Mail Service stopped");
    }
}
