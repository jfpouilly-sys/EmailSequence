using LeadGenerator.Data;
using LeadGenerator.MailService;
using LeadGenerator.MailService.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File("logs/mailservice-.log", rollingInterval: RollingInterval.Day)
    .CreateLogger();

try
{
    Log.Information("Starting Lead Generator Mail Service");

    var builder = Host.CreateApplicationBuilder(args);

    builder.Services.AddWindowsService(options =>
    {
        options.ServiceName = "Lead Generator Mail Service";
    });

    // Database
    builder.Services.AddDbContext<LeadGenDbContext>(options =>
        options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

    // Services
    builder.Services.AddSingleton<IOutlookService, OutlookService>();
    builder.Services.AddScoped<IEmailSenderService, EmailSenderService>();
    builder.Services.AddScoped<IReplyDetectionService, ReplyDetectionService>();
    builder.Services.AddScoped<IUnsubscribeDetectionService, UnsubscribeDetectionService>();

    builder.Services.AddHostedService<Worker>();

    builder.Services.AddSerilog();

    var host = builder.Build();
    await host.RunAsync();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
