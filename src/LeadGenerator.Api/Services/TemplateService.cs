using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;
using System.Text.RegularExpressions;

namespace LeadGenerator.Api.Services;

public class TemplateService : ITemplateService
{
    private readonly LeadGenDbContext _context;

    public TemplateService(LeadGenDbContext context)
    {
        _context = context;
    }

    public string ApplyMergeTags(string template, Dictionary<string, string?> mergeData)
    {
        if (string.IsNullOrEmpty(template)) return template;

        var result = template;
        foreach (var kvp in mergeData)
        {
            var pattern = $@"{{{{{kvp.Key}}}}}";
            result = Regex.Replace(result, pattern, kvp.Value ?? string.Empty, RegexOptions.IgnoreCase);
        }

        return result;
    }

    public async Task<string> RenderEmailTemplateAsync(Guid stepId, Guid contactId)
    {
        var step = await _context.EmailSteps.FindAsync(stepId);
        var contact = await _context.Contacts.FindAsync(contactId);

        if (step == null || contact == null)
            throw new InvalidOperationException("Step or contact not found");

        var mergeData = new Dictionary<string, string?>
        {
            { "FirstName", contact.FirstName },
            { "LastName", contact.LastName },
            { "Email", contact.Email },
            { "Company", contact.Company },
            { "Position", contact.Position },
            { "Title", contact.Title },
            { "Phone", contact.Phone },
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
        };

        return ApplyMergeTags(step.BodyTemplate, mergeData);
    }
}
