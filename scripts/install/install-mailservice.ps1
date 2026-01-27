# Lead Generator - Mail Service Installation Script
# Run this script on each workstation that will send emails
# Run as Administrator

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiServerUrl,

    [Parameter(Mandatory=$true)]
    [string]$WorkstationId,

    [Parameter(Mandatory=$false)]
    [string]$ServiceUsername = $null,

    [Parameter(Mandatory=$false)]
    [string]$ServicePassword = $null
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Mail Service Installation" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    exit 1
}

# Check if Outlook is installed
Write-Host "Checking Outlook installation..." -ForegroundColor Yellow
$outlookInstalled = Test-Path "C:\Program Files\Microsoft Office\root\Office*\OUTLOOK.EXE"
if (-not $outlookInstalled) {
    Write-Host "ERROR: Microsoft Outlook not found. Please install Outlook first." -ForegroundColor Red
    exit 1
}
Write-Host "Outlook found" -ForegroundColor Green

# Create installation directory
Write-Host ""
Write-Host "Installing Mail Service..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "C:\LeadGenerator\MailService" -Force | Out-Null

# Copy Mail Service files
if (Test-Path "..\..\publish\MailService") {
    Copy-Item -Path "..\..\publish\MailService\*" -Destination "C:\LeadGenerator\MailService" -Recurse -Force

    # Update configuration
    $appsettings = Get-Content "C:\LeadGenerator\MailService\appsettings.json" | ConvertFrom-Json
    $appsettings.ApiBaseUrl = $ApiServerUrl
    $appsettings.WorkstationId = $WorkstationId
    $appsettings | ConvertTo-Json -Depth 10 | Set-Content "C:\LeadGenerator\MailService\appsettings.json"

    Write-Host "Mail Service files copied" -ForegroundColor Green
} else {
    Write-Host "ERROR: Mail Service binaries not found in publish folder" -ForegroundColor Red
    exit 1
}

# Create Windows Service
Write-Host ""
Write-Host "Creating Windows Service..." -ForegroundColor Yellow
sc.exe create "LeadGeneratorMailService" binPath= "C:\LeadGenerator\MailService\LeadGenerator.MailService.exe" start= auto
sc.exe description "LeadGeneratorMailService" "Lead Generator Mail Service - $WorkstationId"

# Configure service to run as specific user (required for Outlook COM Interop)
if ($ServiceUsername -and $ServicePassword) {
    Write-Host "Configuring service to run as $ServiceUsername..." -ForegroundColor Yellow
    sc.exe config "LeadGeneratorMailService" obj= "$ServiceUsername" password= "$ServicePassword"
} else {
    Write-Host ""
    Write-Host "WARNING: Service is configured to run as LocalSystem" -ForegroundColor Yellow
    Write-Host "For Outlook COM Interop to work, the service must run as a user with Outlook configured" -ForegroundColor Yellow
    Write-Host "Use: sc config LeadGeneratorMailService obj=DOMAIN\Username password=Password" -ForegroundColor Yellow
}

# Start service
Write-Host ""
Write-Host "Starting Mail Service..." -ForegroundColor Yellow
sc.exe start "LeadGeneratorMailService"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Mail Service Installation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Workstation ID: $WorkstationId" -ForegroundColor Cyan
Write-Host "Logs: C:\LeadGenerator\MailService\logs" -ForegroundColor Cyan
