using CommunityToolkit.Mvvm.ComponentModel;
using LeadGenerator.Desktop.Services;

namespace LeadGenerator.Desktop.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private int _totalCampaigns;

    [ObservableProperty]
    private int _activeCampaigns;

    [ObservableProperty]
    private int _totalEmailsSent;

    [ObservableProperty]
    private int _totalContacts;

    [ObservableProperty]
    private bool _isLoading = true;

    public DashboardViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
        _ = LoadStatisticsAsync();
    }

    private async Task LoadStatisticsAsync()
    {
        try
        {
            var stats = await _apiClient.GetAsync<OverallStatistics>("api/reports/overall?onlyMine=true");
            if (stats != null)
            {
                TotalCampaigns = stats.TotalCampaigns;
                ActiveCampaigns = stats.ActiveCampaigns;
                TotalEmailsSent = stats.TotalEmailsSent;
                TotalContacts = stats.TotalContacts;
            }
        }
        catch (Exception ex)
        {
            // Handle error
            System.Diagnostics.Debug.WriteLine($"Failed to load statistics: {ex.Message}");
        }
        finally
        {
            IsLoading = false;
        }
    }
}

public class OverallStatistics
{
    public int TotalCampaigns { get; set; }
    public int ActiveCampaigns { get; set; }
    public int TotalEmailsSent { get; set; }
    public int TotalContacts { get; set; }
}
