using LeadGenerator.Api.Services;
using LeadGenerator.Core.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace LeadGenerator.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class SuppressionController : ControllerBase
{
    private readonly ISuppressionService _suppressionService;
    private readonly ILogger<SuppressionController> _logger;

    public SuppressionController(ISuppressionService suppressionService, ILogger<SuppressionController> logger)
    {
        _suppressionService = suppressionService;
        _logger = logger;
    }

    [HttpGet]
    public async Task<IActionResult> GetSuppressionList()
    {
        var suppressions = await _suppressionService.GetSuppressionListAsync();
        return Ok(suppressions);
    }

    [HttpGet("check/{email}")]
    public async Task<IActionResult> CheckSuppression(string email, [FromQuery] Guid? campaignId = null)
    {
        var isSuppressed = await _suppressionService.IsEmailSuppressedAsync(email, campaignId);
        return Ok(new { email, isSuppressed });
    }

    [HttpPost]
    [Authorize(Policy = "ManagerOrAdmin")]
    public async Task<IActionResult> AddToSuppressionList([FromBody] AddSuppressionRequest request)
    {
        await _suppressionService.AddToSuppressionListAsync(
            request.Email,
            request.Scope,
            UnsubscribeSource.Manual,
            request.CampaignId,
            request.Reason
        );

        return Ok(new { message = "Email added to suppression list" });
    }
}

public class AddSuppressionRequest
{
    public string Email { get; set; } = string.Empty;
    public UnsubscribeScope Scope { get; set; } = UnsubscribeScope.Global;
    public Guid? CampaignId { get; set; }
    public string? Reason { get; set; }
}
