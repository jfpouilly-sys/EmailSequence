namespace LeadGenerator.Api.Models.Requests;

public class CreateContactRequest
{
    public Guid ListId { get; set; }
    public string? Title { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Company { get; set; } = string.Empty;
    public string? Position { get; set; }
    public string? Phone { get; set; }
    public string? LinkedInUrl { get; set; }
    public string? Source { get; set; }
    public Dictionary<string, string?> CustomFields { get; set; } = new();
}
