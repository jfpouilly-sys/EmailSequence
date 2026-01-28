using LeadGenerator.Core;
using Microsoft.AspNetCore.Mvc;

namespace LeadGenerator.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class VersionController : ControllerBase
{
    private readonly ILogger<VersionController> _logger;

    public VersionController(ILogger<VersionController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Get version information
    /// </summary>
    /// <returns>Version details</returns>
    [HttpGet]
    public IActionResult GetVersion()
    {
        var (year, month, day, build) = VersionInfo.GetVersionComponents();

        var versionInfo = new
        {
            version = VersionInfo.Version,
            productName = VersionInfo.ProductName,
            description = VersionInfo.Description,
            company = VersionInfo.Company,
            copyright = VersionInfo.Copyright,
            buildDate = VersionInfo.BuildDate,
            formattedVersion = VersionInfo.GetFormattedVersion(),
            components = new
            {
                year,
                month,
                day,
                build
            },
            environment = new
            {
                dotnetVersion = Environment.Version.ToString(),
                osVersion = Environment.OSVersion.ToString(),
                machineName = Environment.MachineName,
                processorCount = Environment.ProcessorCount,
                is64BitOperatingSystem = Environment.Is64BitOperatingSystem,
                is64BitProcess = Environment.Is64BitProcess
            }
        };

        return Ok(versionInfo);
    }

    /// <summary>
    /// Get health status
    /// </summary>
    /// <returns>API health status</returns>
    [HttpGet("health")]
    public IActionResult GetHealth()
    {
        return Ok(new
        {
            status = "healthy",
            version = VersionInfo.Version,
            timestamp = DateTime.UtcNow
        });
    }
}
