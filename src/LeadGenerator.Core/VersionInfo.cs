namespace LeadGenerator.Core;

/// <summary>
/// Centralized version information for the Lead Generator application.
/// Version format: YYMMDD-x where YY=year, MM=month, DD=day, x=daily version number
/// </summary>
public static class VersionInfo
{
    /// <summary>
    /// Current version in YYMMDD-x format
    /// </summary>
    public const string Version = "260128-2";

    /// <summary>
    /// Full product name
    /// </summary>
    public const string ProductName = "Lead Generator";

    /// <summary>
    /// Product description
    /// </summary>
    public const string Description = "Email Campaign Management System";

    /// <summary>
    /// Company/Organization name
    /// </summary>
    public const string Company = "ISIT";

    /// <summary>
    /// Copyright information
    /// </summary>
    public const string Copyright = "Copyright © 2026 ISIT. All rights reserved.";

    /// <summary>
    /// Build date (automatically set during compilation)
    /// </summary>
    public static readonly DateTime BuildDate = new DateTime(2026, 1, 28);

    /// <summary>
    /// Gets the version number components
    /// </summary>
    public static (int Year, int Month, int Day, int Build) GetVersionComponents()
    {
        var parts = Version.Split('-');
        if (parts.Length != 2) return (0, 0, 0, 0);

        var datePart = parts[0];
        if (datePart.Length != 6) return (0, 0, 0, 0);

        var year = int.Parse("20" + datePart.Substring(0, 2));
        var month = int.Parse(datePart.Substring(2, 2));
        var day = int.Parse(datePart.Substring(4, 2));
        var build = int.Parse(parts[1]);

        return (year, month, day, build);
    }

    /// <summary>
    /// Gets a formatted version string
    /// </summary>
    public static string GetFormattedVersion()
    {
        var (year, month, day, build) = GetVersionComponents();
        return $"Version {Version} ({year:0000}-{month:00}-{day:00} Build {build})";
    }

    /// <summary>
    /// Gets full product information
    /// </summary>
    public static string GetFullProductInfo()
    {
        return $"{ProductName} {GetFormattedVersion()}\n{Copyright}";
    }
}
