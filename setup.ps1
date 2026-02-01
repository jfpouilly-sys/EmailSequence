<#
.SYNOPSIS
    First-time setup script for Lead Generator - Unblocks PowerShell scripts

.DESCRIPTION
    This script unblocks all PowerShell scripts in the Lead Generator project
    so they can be executed without execution policy errors.

.NOTES
    Run this script FIRST if you get "cannot be loaded" or "not digitally signed" errors.
    You may need to run this with: powershell -ExecutionPolicy Bypass -File setup.ps1
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Lead Generator - First Time Setup Script        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will unblock all PowerShell files in this project." -ForegroundColor Yellow
Write-Host "This is necessary because Windows blocks downloaded scripts by default." -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARN] You are not running as Administrator." -ForegroundColor Yellow
    Write-Host "[WARN] Some scripts may still be blocked." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Setup cancelled. Please run PowerShell as Administrator and try again." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[INFO] Searching for PowerShell scripts..." -ForegroundColor Blue

try {
    # Get all PowerShell scripts in the project
    $scripts = Get-ChildItem -Path $PSScriptRoot -Recurse -Filter "*.ps1" -ErrorAction Stop

    Write-Host "[INFO] Found $($scripts.Count) PowerShell script(s)" -ForegroundColor Blue
    Write-Host ""

    if ($scripts.Count -eq 0) {
        Write-Host "[WARN] No PowerShell scripts found!" -ForegroundColor Yellow
        exit 0
    }

    # Unblock each script
    $unblocked = 0
    $skipped = 0
    $failed = 0

    foreach ($script in $scripts) {
        try {
            # Check if file is blocked
            $isBlocked = (Get-Item $script.FullName).Attributes -band [System.IO.FileAttributes]::Offline

            if ($isBlocked) {
                Unblock-File -Path $script.FullName -ErrorAction Stop
                Write-Host "[OK] Unblocked: $($script.Name)" -ForegroundColor Green
                $unblocked++
            } else {
                Write-Host "[SKIP] Already unblocked: $($script.Name)" -ForegroundColor Gray
                $skipped++
            }
        }
        catch {
            Write-Host "[ERROR] Failed to unblock: $($script.Name)" -ForegroundColor Red
            Write-Host "        Error: $($_.Exception.Message)" -ForegroundColor Red
            $failed++
        }
    }

    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " Summary:" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host " Total scripts found:  $($scripts.Count)" -ForegroundColor White
    Write-Host " Unblocked:            $unblocked" -ForegroundColor Green
    Write-Host " Already unblocked:    $skipped" -ForegroundColor Gray
    Write-Host " Failed:               $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "White" })
    Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    if ($failed -gt 0) {
        Write-Host "[WARN] Some scripts could not be unblocked." -ForegroundColor Yellow
        Write-Host "[WARN] Try running PowerShell as Administrator." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }

    Write-Host "[SUCCESS] Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run: .\build.ps1 -Target help" -ForegroundColor Yellow
    Write-Host "2. Run: .\build.ps1 -Target install-all" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Cyan
    Write-Host ""

    exit 0
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Run PowerShell as Administrator" -ForegroundColor White
    Write-Host "2. Run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass" -ForegroundColor White
    Write-Host "3. Then run this setup script again" -ForegroundColor White
    Write-Host ""
    Write-Host "See EXECUTION_POLICY.md for more information." -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
