# Lead Generator - Desktop Client Installation Script
# Run this script on each workstation

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiServerUrl
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Desktop Client Installation" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Create installation directory
Write-Host "Installing Desktop Client..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "C:\Program Files\LeadGenerator" -Force | Out-Null

# Copy Desktop files
if (Test-Path "..\..\publish\Desktop") {
    Copy-Item -Path "..\..\publish\Desktop\*" -Destination "C:\Program Files\LeadGenerator" -Recurse -Force

    # Update configuration
    $appsettings = @{
        ApiBaseUrl = $ApiServerUrl
        SessionTimeoutMinutes = 480
        AutoRefreshTokenMinutes = 60
    }
    $appsettings | ConvertTo-Json | Set-Content "C:\Program Files\LeadGenerator\appsettings.json"

    Write-Host "Desktop Client installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Desktop binaries not found in publish folder" -ForegroundColor Red
    exit 1
}

# Create desktop shortcut
Write-Host ""
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\Lead Generator.lnk")
$Shortcut.TargetPath = "C:\Program Files\LeadGenerator\LeadGenerator.Desktop.exe"
$Shortcut.WorkingDirectory = "C:\Program Files\LeadGenerator"
$Shortcut.Save()

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Desktop Client Installation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launch Lead Generator from the desktop shortcut" -ForegroundColor Cyan
Write-Host "Default login: admin / Admin123!" -ForegroundColor Cyan
