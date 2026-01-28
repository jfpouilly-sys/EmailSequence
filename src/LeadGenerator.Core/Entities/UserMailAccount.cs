namespace LeadGenerator.Core.Entities;

public class UserMailAccount
{
    public Guid UserId { get; set; }
    public User User { get; set; } = null!;

    public Guid AccountId { get; set; }
    public MailAccount MailAccount { get; set; } = null!;
}
