namespace LeadGenerator.Api.Services;

public interface ITemplateService
{
    string ApplyMergeTags(string template, Dictionary<string, string?> mergeData);
    Task<string> RenderEmailTemplateAsync(Guid stepId, Guid contactId);
}
