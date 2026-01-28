using LeadGenerator.Api.Models.DTOs;

namespace LeadGenerator.Api.Services;

public interface IAuthService
{
    Task<LoginResponse?> LoginAsync(string username, string password);
    Task<bool> ChangePasswordAsync(Guid userId, string currentPassword, string newPassword);
    Task<UserDto?> GetUserByIdAsync(Guid userId);
}
