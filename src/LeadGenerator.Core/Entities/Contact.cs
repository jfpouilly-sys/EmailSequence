namespace LeadGenerator.Core.Entities;

public class Contact
{
    public Guid ContactId { get; set; }
    public Guid ListId { get; set; }
    public ContactList ContactList { get; set; } = null!;

    public string? Title { get; set; }
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Company { get; set; } = string.Empty;
    public string? Position { get; set; }
    public string? Phone { get; set; }
    public string? LinkedInUrl { get; set; }
    public string? Source { get; set; }

    // Custom fields with labels
    public string? Custom1 { get; set; }
    public string? Custom2 { get; set; }
    public string? Custom3 { get; set; }
    public string? Custom4 { get; set; }
    public string? Custom5 { get; set; }
    public string? Custom6 { get; set; }
    public string? Custom7 { get; set; }
    public string? Custom8 { get; set; }
    public string? Custom9 { get; set; }
    public string? Custom10 { get; set; }

    public string? Custom1Label { get; set; }
    public string? Custom2Label { get; set; }
    public string? Custom3Label { get; set; }
    public string? Custom4Label { get; set; }
    public string? Custom5Label { get; set; }
    public string? Custom6Label { get; set; }
    public string? Custom7Label { get; set; }
    public string? Custom8Label { get; set; }
    public string? Custom9Label { get; set; }
    public string? Custom10Label { get; set; }

    public string? CrmLeadId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public ICollection<CampaignContact> CampaignContacts { get; set; } = new List<CampaignContact>();
    public ICollection<EmailLog> EmailLogs { get; set; } = new List<EmailLog>();
}
