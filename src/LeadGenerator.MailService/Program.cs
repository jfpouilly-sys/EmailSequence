using LeadGenerator.Data;
using LeadGenerator.MailService;
using LeadGenerator.MailService.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Serilog;

var configuration = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .Build();

Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(configuration)
    .Enrich.FromLogContext()
    .Enrich.WithProperty("Application", "LeadGenerator.MailService")
    .CreateLogger();

try
{
    Log.Information("=== Lead Generator Mail Service Starting ===");
    Log.Information("Workstation: {WorkstationId}", configuration["WorkstationId"]);
    Log.Information("Log files location: logs/mailservice/");

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
