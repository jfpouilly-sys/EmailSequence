using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LeadGenerator.Desktop.Services;
using System.Collections.ObjectModel;

namespace LeadGenerator.Desktop.ViewModels;

public partial class CampaignListViewModel : ObservableObject
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private ObservableCollection<CampaignItem> _campaigns = new();

    [ObservableProperty]
    private bool _isLoading = true;

    public CampaignListViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
        _ = LoadCampaignsAsync();
    }

    private async Task LoadCampaignsAsync()
    {
        try
        {
            var campaigns = await _apiClient.GetAsync<List<CampaignItem>>("api/campaigns?onlyMine=true");
            if (campaigns != null)
            {
                Campaigns = new ObservableCollection<CampaignItem>(campaigns);
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Failed to load campaigns: {ex.Message}");
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    private async Task Refresh()
    {
        IsLoading = true;
        await LoadCampaignsAsync();
    }
}

public class CampaignItem
{
    public Guid CampaignId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string CampaignRef { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}
