using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LeadGenerator.Desktop.Services;

namespace LeadGenerator.Desktop.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private string _currentView = "Dashboard";

    [ObservableProperty]
    private string _username = "User";

    public MainViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;

        if (App.Current.Properties["Username"] is string username)
        {
            Username = username;
        }
    }

    [RelayCommand]
    private void NavigateToDashboard()
    {
        CurrentView = "Dashboard";
    }

    [RelayCommand]
    private void NavigateToCampaigns()
    {
        CurrentView = "Campaigns";
    }

    [RelayCommand]
    private void NavigateToContacts()
    {
        CurrentView = "Contacts";
    }

    [RelayCommand]
    private void NavigateToReports()
    {
        CurrentView = "Reports";
    }

    [RelayCommand]
    private void Logout()
    {
        App.Current.Properties.Clear();
        App.Current.Shutdown();
    }
}
