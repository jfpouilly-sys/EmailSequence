# Lead Generator - Complete Installation Script
# Run this script as Administrator

param(
    [string]$ServerName = "localhost",
    [string]$DatabasePassword = "ChangeThisPassword123!",
    [string]$ApiServerUrl = "http://localhost:5000"
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Lead Generator Installation Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    exit 1
}

# 1. Install PostgreSQL (if not already installed)
Write-Host "Step 1: Checking PostgreSQL installation..." -ForegroundColor Yellow
$pgInstalled = Test-Path "C:\Program Files\PostgreSQL"
if (-not $pgInstalled) {
    Write-Host "PostgreSQL not found. Please install PostgreSQL 15+ manually from https://www.postgresql.org/download/windows/" -ForegroundColor Red
    exit 1
}
Write-Host "PostgreSQL found" -ForegroundColor Green

# 2. Create database
Write-Host ""
Write-Host "Step 2: Creating database..." -ForegroundColor Yellow
$env:PGPASSWORD = "postgres"
psql -U postgres -f "..\database\001_create_database.sql"
psql -U leadgen_user -d leadgenerator -f "..\database\002_create_tables.sql"
psql -U leadgen_user -d leadgenerator -f "..\database\003_seed_admin_user.sql"
psql -U leadgen_user -d leadgenerator -f "..\database\004_create_indexes.sql"
Write-Host "Database created successfully" -ForegroundColor Green

# 3. Install API Server
Write-Host ""
Write-Host "Step 3: Installing API Server..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "C:\LeadGenerator\Api" -Force | Out-Null
New-Item -ItemType Directory -Path "C:\LeadGenerator\Files" -Force | Out-Null
New-Item -ItemType Directory -Path "C:\LeadGenerator\Logs" -Force | Out-Null

# Copy API files (assumes built binaries are in publish folder)
if (Test-Path "..\..\publish\Api") {
    Copy-Item -Path "..\..\publish\Api\*" -Destination "C:\LeadGenerator\Api" -Recurse -Force

    # Update connection string in appsettings.json
    $appsettings = Get-Content "C:\LeadGenerator\Api\appsettings.json" | ConvertFrom-Json
    $appsettings.ConnectionStrings.DefaultConnection = "Host=$ServerName;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=$DatabasePassword"
    $appsettings | ConvertTo-Json -Depth 10 | Set-Content "C:\LeadGenerator\Api\appsettings.json"

    Write-Host "API Server installed successfully" -ForegroundColor Green
} else {
    Write-Host "ERROR: API binaries not found in publish folder. Please build the solution first." -ForegroundColor Red
    exit 1
}

# 4. Create Windows Service for API
Write-Host ""
Write-Host "Step 4: Creating API Windows Service..." -ForegroundColor Yellow
sc.exe create "LeadGeneratorApi" binPath= "C:\LeadGenerator\Api\LeadGenerator.Api.exe" start= auto
sc.exe description "LeadGeneratorApi" "Lead Generator API Server"
sc.exe start "LeadGeneratorApi"
Write-Host "API Service created and started" -ForegroundColor Green

# 5. Test API health endpoint
Write-Host ""
Write-Host "Step 5: Testing API..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $response = Invoke-RestMethod -Uri "$ApiServerUrl/health" -Method Get
    Write-Host "API is running: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "WARNING: API health check failed. Check logs at C:\LeadGenerator\Logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install Mail Service on each workstation using install-mailservice.ps1"
Write-Host "2. Install Desktop Client on each workstation using install-desktop.ps1"
Write-Host "3. Login with default credentials: admin / Admin123!"
Write-Host "4. IMPORTANT: Change the admin password immediately!"
Write-Host ""
Write-Host "API URL: $ApiServerUrl" -ForegroundColor Cyan
Write-Host "Swagger UI: $ApiServerUrl/swagger" -ForegroundColor Cyan
