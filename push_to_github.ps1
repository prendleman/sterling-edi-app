# PowerShell script to push to GitHub
# Run this after creating a GitHub repository

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "sterling-edi-app"
)

Write-Host "=== Pushing to GitHub ===" -ForegroundColor Green
Write-Host ""

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists: $remoteExists" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to update it? (y/n)"
    if ($overwrite -eq "y") {
        git remote remove origin
    } else {
        Write-Host "Exiting. Please remove the remote manually if needed." -ForegroundColor Red
        exit 1
    }
}

# Add remote
$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"
Write-Host "Adding remote: $remoteUrl" -ForegroundColor Cyan
git remote add origin $remoteUrl

# Rename branch to main if needed
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Renaming branch from '$currentBranch' to 'main'" -ForegroundColor Cyan
    git branch -M main
}

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "You may be prompted for your GitHub credentials." -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Success! ===" -ForegroundColor Green
    Write-Host "Your repository is now available at:" -ForegroundColor Green
    Write-Host "https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can share this link via email!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== Error ===" -ForegroundColor Red
    Write-Host "Failed to push to GitHub. Please check:" -ForegroundColor Red
    Write-Host "1. Repository exists at: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Yellow
    Write-Host "2. You have push access to the repository" -ForegroundColor Yellow
    Write-Host "3. Your GitHub credentials are correct" -ForegroundColor Yellow
}

