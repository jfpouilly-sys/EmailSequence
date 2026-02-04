using LeadGenerator.MailService.Services;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace LeadGenerator.MailService;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly IServiceProvider _serviceProvider;
    private readonly IConfiguration _configuration;
    private bool _outlookAvailable = false;

    public Worker(ILogger<Worker> logger, IServiceProvider serviceProvider, IConfiguration configuration)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
        _configuration = configuration;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Lead Generator Mail Service started");

        // Check if Outlook is available
        _outlookAvailable = CheckOutlookAvailability();

        if (!_outlookAvailable)
        {
            _logger.LogError("==============================================");
            _logger.LogError("OUTLOOK NOT AVAILABLE");
            _logger.LogError("==============================================");
            _logger.LogError("Microsoft Outlook is not installed or not accessible.");
            _logger.LogError("The Mail Service requires Outlook to send emails.");
            _logger.LogError("");
            _logger.LogError("To fix this:");
            _logger.LogError("1. Install Microsoft Outlook on this machine");
            _logger.LogError("2. Configure an email account in Outlook");
            _logger.LogError("3. Restart the Mail Service");
            _logger.LogError("==============================================");
            _logger.LogWarning("Mail Service will continue running but cannot send emails.");
        }

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                if (_outlookAvailable)
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
                else
                {
                    _logger.LogDebug("Skipping cycle - Outlook not available");
                }
            }
            catch (System.IO.FileNotFoundException ex) when (ex.Message.Contains("office") || ex.Message.Contains("Outlook"))
            {
                _logger.LogError("Outlook COM interop failed. Is Outlook installed?");
                _outlookAvailable = false;
            }
            catch (System.Runtime.InteropServices.COMException ex)
            {
                _logger.LogError(ex, "Outlook COM error - Outlook may not be running or accessible");
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

    private bool CheckOutlookAvailability()
    {
        try
        {
            // Try to get Outlook type - this will fail if Office interop is not available
            var outlookType = Type.GetTypeFromProgID("Outlook.Application");
            if (outlookType == null)
            {
                _logger.LogWarning("Outlook.Application COM type not found");
                return false;
            }

            _logger.LogInformation("Outlook COM interop available");
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to check Outlook availability");
            return false;
        }
    }
}
