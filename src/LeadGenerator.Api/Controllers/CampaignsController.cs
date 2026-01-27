using LeadGenerator.Api.Models.Requests;
using LeadGenerator.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace LeadGenerator.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class CampaignsController : ControllerBase
{
    private readonly ICampaignService _campaignService;
    private readonly ILogger<CampaignsController> _logger;

    public CampaignsController(ICampaignService campaignService, ILogger<CampaignsController> logger)
    {
        _campaignService = campaignService;
        _logger = logger;
    }

    [HttpGet]
    public async Task<IActionResult> GetAllCampaigns([FromQuery] bool onlyMine = false)
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

        var campaigns = await _campaignService.GetAllCampaignsAsync(userId);
        return Ok(campaigns);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetCampaignById(Guid id)
    {
        var campaign = await _campaignService.GetCampaignByIdAsync(id);
        if (campaign == null)
        {
            return NotFound();
        }

        return Ok(campaign);
    }

    [HttpPost]
    public async Task<IActionResult> CreateCampaign([FromBody] CreateCampaignRequest request)
    {
        var userIdClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Unauthorized();
        }

        var campaign = await _campaignService.CreateCampaignAsync(request, userId);
        return CreatedAtAction(nameof(GetCampaignById), new { id = campaign.CampaignId }, campaign);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateCampaign(Guid id, [FromBody] CreateCampaignRequest request)
    {
        var success = await _campaignService.UpdateCampaignAsync(id, request);
        if (!success)
        {
            return NotFound();
        }

        return NoContent();
    }

    [HttpDelete("{id}")]
    [Authorize(Policy = "AdminOnly")]
    public async Task<IActionResult> DeleteCampaign(Guid id)
    {
        var success = await _campaignService.DeleteCampaignAsync(id);
        if (!success)
        {
            return NotFound();
        }

        return NoContent();
    }

    [HttpPost("{id}/activate")]
    public async Task<IActionResult> ActivateCampaign(Guid id)
    {
        var success = await _campaignService.ActivateCampaignAsync(id);
        if (!success)
        {
            return NotFound();
        }

        return Ok(new { message = "Campaign activated successfully" });
    }

    [HttpPost("{id}/pause")]
    public async Task<IActionResult> PauseCampaign(Guid id)
    {
        var success = await _campaignService.PauseCampaignAsync(id);
        if (!success)
        {
            return NotFound();
        }

        return Ok(new { message = "Campaign paused successfully" });
    }
}
