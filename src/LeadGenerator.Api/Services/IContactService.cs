using LeadGenerator.Api.Models.DTOs;
using LeadGenerator.Api.Models.Requests;

namespace LeadGenerator.Api.Services;

public interface IContactService
{
    Task<IEnumerable<ContactDto>> GetContactsByListIdAsync(Guid listId);
    Task<ContactDto?> GetContactByIdAsync(Guid contactId);
    Task<ContactDto> CreateContactAsync(CreateContactRequest request);
    Task<bool> UpdateContactAsync(Guid contactId, CreateContactRequest request);
    Task<bool> DeleteContactAsync(Guid contactId);
    Task<int> ImportContactsFromCsvAsync(Guid listId, Stream csvStream);
}
