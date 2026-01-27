using LeadGenerator.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace LeadGenerator.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ReportsController : ControllerBase
{
    private readonly IReportService _reportService;
    private readonly ILogger<ReportsController> _logger;

    public ReportsController(IReportService reportService, ILogger<ReportsController> logger)
    {
        _reportService = reportService;
        _logger = logger;
    }

    [HttpGet("campaign/{campaignId}")]
    public async Task<IActionResult> GetCampaignStatistics(Guid campaignId)
    {
        try
        {
            var stats = await _reportService.GetCampaignStatisticsAsync(campaignId);
            return Ok(stats);
        }
        catch (InvalidOperationException ex)
        {
            return NotFound(new { message = ex.Message });
        }
    }

    [HttpGet("overall")]
    public async Task<IActionResult> GetOverallStatistics([FromQuery] bool onlyMine = false)
    {
        Guid? userId = null;
        if (onlyMine)
        {
            var userIdClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            if (userIdClaim != null && Guid.TryParse(userIdClaim, out var parsedUserId))
            {
                userId = parsedUserId;
            }
        }

        var stats = await _reportService.GetOverallStatisticsAsync(userId);
        return Ok(stats);
    }
}
