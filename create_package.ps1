# Create deployment package (ZIP file)
# Run this script from the sterling_edi_app directory

$packageName = "sterling_edi_app.zip"
$excludePatterns = @("*.pyc", "__pycache__", "*.log", ".git", ".gitignore", "*.zip", "metrics", "dashboards", "logs")

Write-Host "Creating deployment package: $packageName" -ForegroundColor Green

# Remove existing package if it exists
if (Test-Path $packageName) {
    Remove-Item $packageName
    Write-Host "Removed existing package" -ForegroundColor Yellow
}

# Get current directory
$sourceDir = Get-Location

# Create temporary directory for packaging
$tempDir = Join-Path $env:TEMP "sterling_edi_package"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy files (excluding patterns)
Write-Host "Copying files..." -ForegroundColor Cyan
Get-ChildItem -Path $sourceDir -Recurse | Where-Object {
    $exclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($_.FullName -like "*$pattern*") {
            $exclude = $true
            break
        }
    }
    -not $exclude
} | Copy-Item -Destination {
    $_.FullName.Replace($sourceDir, $tempDir)
} -Recurse -Force

# Create ZIP file
Write-Host "Creating ZIP file..." -ForegroundColor Cyan
Compress-Archive -Path "$tempDir\*" -DestinationPath (Join-Path $sourceDir $packageName) -Force

# Cleanup
Remove-Item $tempDir -Recurse -Force

Write-Host "Package created: $packageName" -ForegroundColor Green
Write-Host "Size: $((Get-Item $packageName).Length / 1MB) MB" -ForegroundColor Green

