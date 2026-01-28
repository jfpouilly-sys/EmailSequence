using CommunityToolkit.Mvvm.ComponentModel;
using LeadGenerator.Core;
using System;

namespace LeadGenerator.Desktop.ViewModels;

public partial class AboutViewModel : ObservableObject
{
    [ObservableProperty]
    private string _productName = VersionInfo.ProductName;

    [ObservableProperty]
    private string _description = VersionInfo.Description;

    [ObservableProperty]
    private string _version = VersionInfo.Version;

    [ObservableProperty]
    private string _buildDate = VersionInfo.BuildDate.ToString("MMMM dd, yyyy");

    [ObservableProperty]
    private string _company = VersionInfo.Company;

    [ObservableProperty]
    private string _copyright = VersionInfo.Copyright;

    [ObservableProperty]
    private string _dotNetVersion = Environment.Version.ToString();

    [ObservableProperty]
    private string _machineName = Environment.MachineName;

    [ObservableProperty]
    private string _operatingSystem = Environment.OSVersion.ToString();

    [ObservableProperty]
    private string _userName = Environment.UserName;

    public AboutViewModel()
    {
        // Constructor can be used to initialize additional properties if needed
    }
}
