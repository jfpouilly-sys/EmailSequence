<#
.SYNOPSIS
    Build and installation script for Lead Generator (Makefile-style for Windows)

.DESCRIPTION
    This script provides Makefile-like targets for building, publishing, and installing
    the Lead Generator application on Windows.

.PARAMETER Target
    The build target to execute: clean, restore, build, publish, database-setup, install-all, help

.PARAMETER Configuration
    Build configuration: Debug or Release (default: Release)

.EXAMPLE
    .\build.ps1 -Target build
    .\build.ps1 -Target publish
    .\build.ps1 -Target install-all

.NOTES
    Version: 260128-2
    Requires: .NET 8 SDK, PostgreSQL 15+
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("clean", "restore", "build", "publish", "database-setup", "install-all", "help", "test")]
    [string]$Target = "help",

    [Parameter(Mandatory=$false)]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = ".\publish",

    [Parameter(Mandatory=$false)]
    [string]$DatabaseServer = "localhost",

    [Parameter(Mandatory=$false)]
    [string]$DatabasePassword = "",

    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = "http://localhost:5000"
)

# Script configuration
$ErrorActionPreference = "Stop"
$SolutionFile = "LeadGenerator.sln"
$ScriptVersion = "260128-2"

# ANSI Colors for output
$script:ColorReset = "`e[0m"
$script:ColorGreen = "`e[32m"
$script:ColorYellow = "`e[33m"
$script:ColorRed = "`e[31m"
$script:ColorBlue = "`e[34m"
$script:ColorCyan = "`e[36m"

# Helper Functions
function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-DotNetInstalled {
    try {
        $dotnetVersion = dotnet --version
        Write-Success ".NET SDK $dotnetVersion is installed"
        return $true
    }
    catch {
        Write-Error-Message ".NET 8 SDK is not installed!"
        Write-Info "Download from: https://dotnet.microsoft.com/download/dotnet/8.0"
        return $false
    }
}

function Test-PostgreSQLInstalled {
    try {
        $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
        if ($pgService) {
            Write-Success "PostgreSQL service found: $($pgService.Name)"
            return $true
        }
        Write-Warning "PostgreSQL service not found"
        return $false
    }
    catch {
        Write-Warning "PostgreSQL may not be installed"
        return $false
    }
}

# Build Targets

function Target-Clean {
    Write-Header "Cleaning Build Artifacts"

    Write-Info "Removing bin and obj folders..."
    Get-ChildItem -Path . -Include bin,obj -Recurse -Directory | Remove-Item -Recurse -Force

    if (Test-Path $OutputDir) {
        Write-Info "Removing publish folder..."
        Remove-Item -Path $OutputDir -Recurse -Force
    }

    Write-Success "Clean completed"
}

function Target-Restore {
    Write-Header "Restoring NuGet Packages"

    if (-not (Test-DotNetInstalled)) { exit 1 }

    Write-Info "Restoring packages for $SolutionFile..."
    dotnet restore $SolutionFile

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Restore completed"
    } else {
        Write-Error-Message "Restore failed"
        exit 1
    }
}

function Target-Build {
    Write-Header "Building Solution"

    if (-not (Test-DotNetInstalled)) { exit 1 }

    Write-Info "Building $SolutionFile in $Configuration mode..."
    dotnet build $SolutionFile -c $Configuration --no-restore

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Build completed successfully"
    } else {
        Write-Error-Message "Build failed"
        exit 1
    }
}

function Target-Publish {
    Write-Header "Publishing Applications"

    if (-not (Test-DotNetInstalled)) { exit 1 }

    # Create output directory
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

    # Publish API
    Write-Info "Publishing API..."
    dotnet publish src/LeadGenerator.Api/LeadGenerator.Api.csproj `
        -c $Configuration `
        -o "$OutputDir/Api" `
        --no-restore

    # Publish Desktop
    Write-Info "Publishing Desktop..."
    dotnet publish src/LeadGenerator.Desktop/LeadGenerator.Desktop.csproj `
        -c $Configuration `
        -o "$OutputDir/Desktop" `
        --no-restore

    # Publish Mail Service
    Write-Info "Publishing Mail Service..."
    dotnet publish src/LeadGenerator.MailService/LeadGenerator.MailService.csproj `
        -c $Configuration `
        -o "$OutputDir/MailService" `
        --no-restore

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Publish completed"
        Write-Info "Output directory: $OutputDir"
    } else {
        Write-Error-Message "Publish failed"
        exit 1
    }
}

function Target-Database-Setup {
    Write-Header "Database Setup"

    if ([string]::IsNullOrEmpty($DatabasePassword)) {
        $DatabasePassword = Read-Host "Enter PostgreSQL password for user 'postgres'" -AsSecureString
        $DatabasePassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DatabasePassword))
    }

    $env:PGPASSWORD = $DatabasePassword

    try {
        Write-Info "Creating database and user..."
        psql -U postgres -h $DatabaseServer -f scripts/database/001_create_database.sql

        Write-Info "Creating tables..."
        psql -U leadgen_user -h $DatabaseServer -d leadgenerator -f scripts/database/002_create_tables.sql

        Write-Info "Seeding admin user..."
        psql -U leadgen_user -h $DatabaseServer -d leadgenerator -f scripts/database/003_seed_admin_user.sql

        Write-Info "Creating indexes..."
        psql -U leadgen_user -h $DatabaseServer -d leadgenerator -f scripts/database/004_create_indexes.sql

        Write-Success "Database setup completed"
        Write-Info "Default credentials: admin / Admin123!"
    }
    catch {
        Write-Error-Message "Database setup failed: $_"
        exit 1
    }
    finally {
        $env:PGPASSWORD = $null
    }
}

function Target-Install-All {
    Write-Header "Complete Installation"

    Write-Info "This will perform a complete build and installation"
    Write-Info "Server: $DatabaseServer"
    Write-Info "API URL: $ApiUrl"
    Write-Host ""

    $confirm = Read-Host "Continue? (y/n)"
    if ($confirm -ne "y") {
        Write-Warning "Installation cancelled"
        exit 0
    }

    # Run all build steps
    Target-Clean
    Target-Restore
    Target-Build
    Target-Publish

    # Setup database
    Write-Host ""
    $setupDb = Read-Host "Setup database? (y/n)"
    if ($setupDb -eq "y") {
        Target-Database-Setup
    }

    # Install services
    Write-Host ""
    Write-Info "Running installation scripts..."

    $installServer = Read-Host "Install API Server? (y/n)"
    if ($installServer -eq "y") {
        & ".\scripts\install\install-all.ps1" -ServerName $DatabaseServer -DatabasePassword $DatabasePassword -ApiServerUrl $ApiUrl
    }

    Write-Success "Installation completed!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start the API service: net start LeadGeneratorApi" -ForegroundColor Yellow
    Write-Host "2. Access Swagger: $ApiUrl/swagger" -ForegroundColor Yellow
    Write-Host "3. Install Desktop client on workstations" -ForegroundColor Yellow
    Write-Host "4. Install Mail Service on workstations with Outlook" -ForegroundColor Yellow
}

function Target-Test {
    Write-Header "Running Tests"

    Write-Info "Looking for test projects..."
    $testProjects = Get-ChildItem -Path . -Filter "*.Tests.csproj" -Recurse

    if ($testProjects.Count -eq 0) {
        Write-Warning "No test projects found"
        return
    }

    foreach ($testProject in $testProjects) {
        Write-Info "Running tests in $($testProject.Name)..."
        dotnet test $testProject.FullName -c $Configuration --no-restore
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Success "All tests passed"
    } else {
        Write-Error-Message "Some tests failed"
        exit 1
    }
}

function Target-Help {
    Write-Host ""
    Write-Host "Lead Generator Build Script (v$ScriptVersion)" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\build.ps1 -Target <target> [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Targets:" -ForegroundColor Green
    Write-Host "  clean           - Remove all build artifacts (bin, obj, publish)" -ForegroundColor White
    Write-Host "  restore         - Restore NuGet packages" -ForegroundColor White
    Write-Host "  build           - Build the solution" -ForegroundColor White
    Write-Host "  publish         - Publish all projects to .\publish\" -ForegroundColor White
    Write-Host "  database-setup  - Initialize PostgreSQL database" -ForegroundColor White
    Write-Host "  install-all     - Complete build and installation" -ForegroundColor White
    Write-Host "  test            - Run all tests" -ForegroundColor White
    Write-Host "  help            - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -Configuration <Debug|Release>  - Build configuration (default: Release)" -ForegroundColor White
    Write-Host "  -OutputDir <path>               - Publish output directory (default: .\publish)" -ForegroundColor White
    Write-Host "  -DatabaseServer <server>        - PostgreSQL server (default: localhost)" -ForegroundColor White
    Write-Host "  -DatabasePassword <password>    - PostgreSQL password" -ForegroundColor White
    Write-Host "  -ApiUrl <url>                   - API server URL (default: http://localhost:5000)" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\build.ps1 -Target build" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 -Target publish -Configuration Debug" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 -Target database-setup -DatabasePassword 'MyPassword123'" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 -Target install-all" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Prerequisites:" -ForegroundColor Green
    Write-Host "  - .NET 8 SDK: https://dotnet.microsoft.com/download/dotnet/8.0" -ForegroundColor White
    Write-Host "  - PostgreSQL 15+: https://www.postgresql.org/download/" -ForegroundColor White
    Write-Host "  - Microsoft Outlook (for Mail Service workstations)" -ForegroundColor White
    Write-Host ""

    # Check prerequisites
    Write-Host "Checking prerequisites..." -ForegroundColor Cyan
    Test-DotNetInstalled
    Test-PostgreSQLInstalled
    Write-Host ""
}

# Main Execution
try {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         Lead Generator Build System v$ScriptVersion        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    switch ($Target) {
        "clean"          { Target-Clean }
        "restore"        { Target-Restore }
        "build"          { Target-Restore; Target-Build }
        "publish"        { Target-Restore; Target-Build; Target-Publish }
        "database-setup" { Target-Database-Setup }
        "install-all"    { Target-Install-All }
        "test"           { Target-Test }
        "help"           { Target-Help }
        default          { Target-Help }
    }

    Write-Host ""
    Write-Success "Target '$Target' completed successfully!"
    exit 0
}
catch {
    Write-Host ""
    Write-Error-Message "Build failed: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
