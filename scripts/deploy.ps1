# IBM Sterling EDI Application - Windows Deployment Script
# Run this script as Administrator

param(
    [string]$InstallPath = "C:\EDI\sterling_edi_app",
    [string]$PythonPath = "python",
    [switch]$SkipDependencies = $false
)

Write-Host "IBM Sterling EDI Application - Windows Deployment" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
}

# Step 1: Verify Python installation
Write-Host "Step 1: Verifying Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Step 2: Create installation directory
Write-Host "Step 2: Creating installation directory..." -ForegroundColor Cyan
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "  Created: $InstallPath" -ForegroundColor Green
} else {
    Write-Host "  Directory exists: $InstallPath" -ForegroundColor Yellow
}

# Step 3: Copy application files
Write-Host "Step 3: Copying application files..." -ForegroundColor Cyan
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$appPath = Split-Path -Parent $scriptPath

if (Test-Path $appPath) {
    Copy-Item -Path "$appPath\*" -Destination $InstallPath -Recurse -Force -Exclude "*.pyc","__pycache__"
    Write-Host "  Files copied to: $InstallPath" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Could not find application files. Manual copy may be required." -ForegroundColor Yellow
}

# Step 4: Install dependencies
if (-not $SkipDependencies) {
    Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Cyan
    Set-Location $InstallPath
    & $PythonPath -m pip install --upgrade pip | Out-Null
    & $PythonPath -m pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Some dependencies may have failed to install." -ForegroundColor Yellow
    }
} else {
    Write-Host "Step 4: Skipping dependency installation (--SkipDependencies)" -ForegroundColor Yellow
}

# Step 5: Create required directories
Write-Host "Step 5: Creating required directories..." -ForegroundColor Cyan
$directories = @(
    "$InstallPath\logs",
    "$InstallPath\processed",
    "$InstallPath\error"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Step 6: Verify configuration files
Write-Host "Step 6: Verifying configuration files..." -ForegroundColor Cyan
$configFiles = @(
    "$InstallPath\config\config.yaml",
    "$InstallPath\config\sterling_config.yaml"
)

foreach ($configFile in $configFiles) {
    if (Test-Path $configFile) {
        Write-Host "  Found: $configFile" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Missing: $configFile" -ForegroundColor Yellow
    }
}

# Step 7: Test installation
Write-Host "Step 7: Testing installation..." -ForegroundColor Cyan
Set-Location $InstallPath
try {
    $testResult = & $PythonPath -c "import yaml; import requests; print('OK')" 2>&1
    if ($testResult -match "OK") {
        Write-Host "  Installation test passed" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Installation test may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ERROR: Installation test failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit configuration files in: $InstallPath\config\" -ForegroundColor White
Write-Host "2. Configure Sterling directories in: $InstallPath\config\sterling_config.yaml" -ForegroundColor White
Write-Host "3. Test with: python $InstallPath\main.py process --file tests\sample_data\sample_850.x12" -ForegroundColor White
Write-Host "4. See DEPLOYMENT.md for detailed setup instructions" -ForegroundColor White
Write-Host ""

