using LeadGenerator.Api.Models.Requests;
using LeadGenerator.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace LeadGenerator.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ContactsController : ControllerBase
{
    private readonly IContactService _contactService;
    private readonly ILogger<ContactsController> _logger;

    public ContactsController(IContactService contactService, ILogger<ContactsController> logger)
    {
        _contactService = contactService;
        _logger = logger;
    }

    [HttpGet("list/{listId}")]
    public async Task<IActionResult> GetContactsByList(Guid listId)
    {
        var contacts = await _contactService.GetContactsByListIdAsync(listId);
        return Ok(contacts);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetContactById(Guid id)
    {
        var contact = await _contactService.GetContactByIdAsync(id);
        if (contact == null)
        {
            return NotFound();
        }

        return Ok(contact);
    }

    [HttpPost]
    public async Task<IActionResult> CreateContact([FromBody] CreateContactRequest request)
    {
        var contact = await _contactService.CreateContactAsync(request);
        return CreatedAtAction(nameof(GetContactById), new { id = contact.ContactId }, contact);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateContact(Guid id, [FromBody] CreateContactRequest request)
    {
        var success = await _contactService.UpdateContactAsync(id, request);
        if (!success)
        {
            return NotFound();
        }

        return NoContent();
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteContact(Guid id)
    {
        var success = await _contactService.DeleteContactAsync(id);
        if (!success)
        {
            return NotFound();
        }

        return NoContent();
    }

    [HttpPost("import/{listId}")]
    public async Task<IActionResult> ImportContactsFromCsv(Guid listId, IFormFile file)
    {
        if (file == null || file.Length == 0)
        {
            return BadRequest(new { message = "No file uploaded" });
        }

        if (!file.FileName.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
        {
            return BadRequest(new { message = "Only CSV files are allowed" });
        }

        using var stream = file.OpenReadStream();
        var importedCount = await _contactService.ImportContactsFromCsvAsync(listId, stream);

        return Ok(new { message = $"Successfully imported {importedCount} contacts", count = importedCount });
    }
}
