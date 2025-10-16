# PowerShell script to permanently add make to Windows PATH
# Run this script as Administrator to permanently add GnuWin32 make to system PATH

param(
    [switch]$Force,
    [switch]$User
)

$MakePath = "C:\Program Files (x86)\GnuWin32\bin"

Write-Host "🔧 STM32 Build System - PATH Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Check if make is already in PATH
$currentPath = $env:PATH
if ($currentPath -like "*$MakePath*") {
    Write-Host "✅ Make is already in current session PATH" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Make is NOT in current session PATH" -ForegroundColor Red
}

# Check if GnuWin32 make exists
if (Test-Path "$MakePath\make.exe") {
    Write-Host "✅ Found make.exe at: $MakePath" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: make.exe not found at: $MakePath" -ForegroundColor Red
    Write-Host "Please install GnuWin32 make or update the path in this script" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Choose installation scope:" -ForegroundColor Cyan
Write-Host "1. System-wide (requires Administrator)" -ForegroundColor White
Write-Host "2. Current user only" -ForegroundColor White
Write-Host ""

$scope = "Machine"
if ($User) {
    $scope = "User"
    Write-Host "Installing for current user only..." -ForegroundColor Yellow
} elseif ($Force) {
    Write-Host "Installing system-wide (forced)..." -ForegroundColor Yellow
} else {
    $choice = Read-Host "Enter choice (1 for system-wide, 2 for user) [1]"
    if ($choice -eq "2") {
        $scope = "User"
        Write-Host "Installing for current user only..." -ForegroundColor Yellow
    } else {
        Write-Host "Installing system-wide..." -ForegroundColor Yellow
    }
}

try {
    # Get current PATH from registry
    if ($scope -eq "Machine") {
        $regPath = "HKLM:\System\CurrentControlSet\Control\Session Manager\Environment"
        $currentSystemPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    } else {
        $regPath = "HKCU:\Environment"
        $currentSystemPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    }
    
    Write-Host "Current $scope PATH length: $($currentSystemPath.Length) characters" -ForegroundColor Cyan
    
    # Check if path is already in system PATH
    if ($currentSystemPath -like "*$MakePath*") {
        Write-Host "✅ Make path is already in $scope PATH!" -ForegroundColor Green
        Write-Host "No changes needed." -ForegroundColor Green
    } else {
        Write-Host "Adding to $scope PATH..." -ForegroundColor Yellow
        
        # Add the new path
        $newPath = $currentSystemPath + ";$MakePath"
        
        # Set the new PATH
        [Environment]::SetEnvironmentVariable("PATH", $newPath, $scope)
        
        Write-Host "✅ Successfully added to $scope PATH!" -ForegroundColor Green
        Write-Host "New PATH length: $($newPath.Length) characters" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "🔄 Refreshing current session PATH..." -ForegroundColor Yellow
    
    # Refresh PATH for current session
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Host ""
    Write-Host "Testing make command..." -ForegroundColor Cyan
    
    # Test make command
    try {
        $makeVersion = & make --version 2>&1 | Select-Object -First 1
        Write-Host "✅ Make is working: $makeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Make command still not working. You may need to restart VS Code." -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "✅ PATH setup completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Note: If make still doesn't work:" -ForegroundColor Yellow
    Write-Host "   1. Restart VS Code completely" -ForegroundColor White
    Write-Host "   2. Or restart your computer" -ForegroundColor White
    Write-Host "   3. New terminals will automatically have the updated PATH" -ForegroundColor White
    
} catch {
    Write-Host "❌ ERROR: Failed to update PATH" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($scope -eq "Machine") {
        Write-Host ""
        Write-Host "💡 Try running PowerShell as Administrator, or use:" -ForegroundColor Yellow
        Write-Host "   .\scripts\setup_path.ps1 -User" -ForegroundColor White
    }
    
    exit 1
}
