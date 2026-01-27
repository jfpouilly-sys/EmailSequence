using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LeadGenerator.Desktop.Services;
using LeadGenerator.Desktop.Views;
using Microsoft.Extensions.DependencyInjection;
using System.Windows;

namespace LeadGenerator.Desktop.ViewModels;

public partial class LoginViewModel : ObservableObject
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private string _username = string.Empty;

    [ObservableProperty]
    private string _password = string.Empty;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private bool _isLoading;

    public LoginViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
    }

    [RelayCommand]
    private async Task Login()
    {
        ErrorMessage = string.Empty;

        if (string.IsNullOrWhiteSpace(Username) || string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "Please enter username and password";
            return;
        }

        IsLoading = true;

        try
        {
            var response = await _apiClient.PostAsync<LoginResponse>("api/auth/login", new
            {
                Username,
                Password
            });

            if (response != null && !string.IsNullOrEmpty(response.Token))
            {
                _apiClient.SetToken(response.Token);

                // Store user info
                App.Current.Properties["Username"] = response.Username;
                App.Current.Properties["Role"] = response.Role;
                App.Current.Properties["Token"] = response.Token;

                // Open main window
                var mainWindow = App.ServiceProvider.GetRequiredService<MainWindow>();
                mainWindow.Show();

                // Close login window
                Application.Current.Windows.OfType<Window>().FirstOrDefault(w => w.IsActive)?.Close();
            }
            else
            {
                ErrorMessage = "Invalid username or password";
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Login failed: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
}

public class LoginResponse
{
    public string Token { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public DateTime ExpiresAt { get; set; }
}
