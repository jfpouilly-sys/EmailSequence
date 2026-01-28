using LeadGenerator.Api.Models.DTOs;
using LeadGenerator.Api.Models.Requests;
using LeadGenerator.Core.Entities;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

namespace LeadGenerator.Api.Services;

public class ContactService : IContactService
{
    private readonly LeadGenDbContext _context;
    private readonly ILogger<ContactService> _logger;

    public ContactService(LeadGenDbContext context, ILogger<ContactService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<IEnumerable<ContactDto>> GetContactsByListIdAsync(Guid listId)
    {
        var contacts = await _context.Contacts
            .Where(c => c.ListId == listId)
            .OrderBy(c => c.LastName)
            .ThenBy(c => c.FirstName)
            .ToListAsync();

        return contacts.Select(MapToDto);
    }

    public async Task<ContactDto?> GetContactByIdAsync(Guid contactId)
    {
        var contact = await _context.Contacts.FindAsync(contactId);
        return contact == null ? null : MapToDto(contact);
    }

    public async Task<ContactDto> CreateContactAsync(CreateContactRequest request)
    {
        var contact = new Contact
        {
            ContactId = Guid.NewGuid(),
            ListId = request.ListId,
            Title = request.Title,
            FirstName = request.FirstName,
            LastName = request.LastName,
            Email = request.Email.ToLower(),
            Company = request.Company,
            Position = request.Position,
            Phone = request.Phone,
            LinkedInUrl = request.LinkedInUrl,
            Source = request.Source,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        // Apply custom fields
        if (request.CustomFields.TryGetValue("Custom1", out var custom1)) contact.Custom1 = custom1;
        if (request.CustomFields.TryGetValue("Custom2", out var custom2)) contact.Custom2 = custom2;
        if (request.CustomFields.TryGetValue("Custom3", out var custom3)) contact.Custom3 = custom3;
        if (request.CustomFields.TryGetValue("Custom4", out var custom4)) contact.Custom4 = custom4;
        if (request.CustomFields.TryGetValue("Custom5", out var custom5)) contact.Custom5 = custom5;
        if (request.CustomFields.TryGetValue("Custom6", out var custom6)) contact.Custom6 = custom6;
        if (request.CustomFields.TryGetValue("Custom7", out var custom7)) contact.Custom7 = custom7;
        if (request.CustomFields.TryGetValue("Custom8", out var custom8)) contact.Custom8 = custom8;
        if (request.CustomFields.TryGetValue("Custom9", out var custom9)) contact.Custom9 = custom9;
        if (request.CustomFields.TryGetValue("Custom10", out var custom10)) contact.Custom10 = custom10;

        _context.Contacts.Add(contact);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Contact {ContactId} created in list {ListId}", contact.ContactId, request.ListId);

        return MapToDto(contact);
    }

    public async Task<bool> UpdateContactAsync(Guid contactId, CreateContactRequest request)
    {
        var contact = await _context.Contacts.FindAsync(contactId);
        if (contact == null) return false;

        contact.Title = request.Title;
        contact.FirstName = request.FirstName;
        contact.LastName = request.LastName;
        contact.Email = request.Email.ToLower();
        contact.Company = request.Company;
        contact.Position = request.Position;
        contact.Phone = request.Phone;
        contact.LinkedInUrl = request.LinkedInUrl;
        contact.Source = request.Source;
        contact.UpdatedAt = DateTime.UtcNow;

        // Apply custom fields
        if (request.CustomFields.TryGetValue("Custom1", out var custom1)) contact.Custom1 = custom1;
        if (request.CustomFields.TryGetValue("Custom2", out var custom2)) contact.Custom2 = custom2;
        if (request.CustomFields.TryGetValue("Custom3", out var custom3)) contact.Custom3 = custom3;
        if (request.CustomFields.TryGetValue("Custom4", out var custom4)) contact.Custom4 = custom4;
        if (request.CustomFields.TryGetValue("Custom5", out var custom5)) contact.Custom5 = custom5;
        if (request.CustomFields.TryGetValue("Custom6", out var custom6)) contact.Custom6 = custom6;
        if (request.CustomFields.TryGetValue("Custom7", out var custom7)) contact.Custom7 = custom7;
        if (request.CustomFields.TryGetValue("Custom8", out var custom8)) contact.Custom8 = custom8;
        if (request.CustomFields.TryGetValue("Custom9", out var custom9)) contact.Custom9 = custom9;
        if (request.CustomFields.TryGetValue("Custom10", out var custom10)) contact.Custom10 = custom10;

        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<bool> DeleteContactAsync(Guid contactId)
    {
        var contact = await _context.Contacts.FindAsync(contactId);
        if (contact == null) return false;

        _context.Contacts.Remove(contact);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Contact {ContactId} deleted", contactId);
        return true;
    }

    public async Task<int> ImportContactsFromCsvAsync(Guid listId, Stream csvStream)
    {
        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            HasHeaderRecord = true,
            MissingFieldFound = null
        };

        using var reader = new StreamReader(csvStream);
        using var csv = new CsvReader(reader, config);

        var records = csv.GetRecords<dynamic>().ToList();
        int importedCount = 0;

        foreach (var record in records)
        {
            var dict = (IDictionary<string, object>)record;

            var contact = new Contact
            {
                ContactId = Guid.NewGuid(),
                ListId = listId,
                Title = GetValue(dict, "Title"),
                FirstName = GetValue(dict, "FirstName") ?? "",
                LastName = GetValue(dict, "LastName") ?? "",
                Email = (GetValue(dict, "Email") ?? "").ToLower(),
                Company = GetValue(dict, "Company") ?? "",
                Position = GetValue(dict, "Position"),
                Phone = GetValue(dict, "Phone"),
                LinkedInUrl = GetValue(dict, "LinkedInUrl"),
                Source = GetValue(dict, "Source"),
                Custom1 = GetValue(dict, "Custom1"),
                Custom2 = GetValue(dict, "Custom2"),
                Custom3 = GetValue(dict, "Custom3"),
                Custom4 = GetValue(dict, "Custom4"),
                Custom5 = GetValue(dict, "Custom5"),
                Custom6 = GetValue(dict, "Custom6"),
                Custom7 = GetValue(dict, "Custom7"),
                Custom8 = GetValue(dict, "Custom8"),
                Custom9 = GetValue(dict, "Custom9"),
                Custom10 = GetValue(dict, "Custom10"),
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            if (!string.IsNullOrEmpty(contact.Email))
            {
                _context.Contacts.Add(contact);
                importedCount++;
            }
        }

        await _context.SaveChangesAsync();
        _logger.LogInformation("Imported {Count} contacts into list {ListId}", importedCount, listId);

        return importedCount;
    }

    private static string? GetValue(IDictionary<string, object> dict, string key)
    {
        return dict.TryGetValue(key, out var value) ? value?.ToString() : null;
    }

    private static ContactDto MapToDto(Contact contact)
    {
        return new ContactDto
        {
            ContactId = contact.ContactId,
            ListId = contact.ListId,
            Title = contact.Title,
            FirstName = contact.FirstName,
            LastName = contact.LastName,
            Email = contact.Email,
            Company = contact.Company,
            Position = contact.Position,
            Phone = contact.Phone,
            LinkedInUrl = contact.LinkedInUrl,
            Source = contact.Source,
            CustomFields = new Dictionary<string, string?>
            {
                { "Custom1", contact.Custom1 },
                { "Custom2", contact.Custom2 },
                { "Custom3", contact.Custom3 },
                { "Custom4", contact.Custom4 },
                { "Custom5", contact.Custom5 },
                { "Custom6", contact.Custom6 },
                { "Custom7", contact.Custom7 },
                { "Custom8", contact.Custom8 },
                { "Custom9", contact.Custom9 },
                { "Custom10", contact.Custom10 }
            },
            CreatedAt = contact.CreatedAt,
            UpdatedAt = contact.UpdatedAt
        };
    }
}
