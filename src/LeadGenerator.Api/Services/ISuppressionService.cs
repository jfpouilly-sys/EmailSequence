using LeadGenerator.Core.Enums;

namespace LeadGenerator.Api.Services;

public interface ISuppressionService
{
    Task<bool> IsEmailSuppressedAsync(string email, Guid? campaignId = null);
    Task AddToSuppressionListAsync(string email, UnsubscribeScope scope, UnsubscribeSource source, Guid? campaignId = null, string? reason = null);
    Task<IEnumerable<object>> GetSuppressionListAsync();
}
