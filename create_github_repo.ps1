# PowerShell script to create GitHub repository and push code
# Requires GitHub Personal Access Token

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "sterling-edi-app",
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "Sterling-style EDI operating model POC (independent portfolio project)",
    
    [Parameter(Mandatory=$false)]
    [switch]$Private = $false
)

$username = "BlackLake420"
$visibility = if ($Private) { "private" } else { "public" }

Write-Host "=== Creating GitHub Repository ===" -ForegroundColor Green
Write-Host "Repository: $RepoName" -ForegroundColor Cyan
Write-Host "Visibility: $visibility" -ForegroundColor Cyan
Write-Host ""

# Create repository via GitHub API
$body = @{
    name = $RepoName
    description = $Description
    private = $Private
} | ConvertTo-Json

$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
}

Write-Host "Creating repository on GitHub..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
} catch {
    Write-Host "Error creating repository: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Authentication failed. Please check your GitHub token." -ForegroundColor Red
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "Repository may already exist or name is invalid." -ForegroundColor Yellow
        Write-Host "Trying to continue with existing repository..." -ForegroundColor Yellow
    } else {
        exit 1
    }
}

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host ""
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
$remoteUrl = "https://github.com/$username/$RepoName.git"
Write-Host ""
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
Write-Host "Using token for authentication..." -ForegroundColor Yellow
Write-Host ""

# Configure git to use token
$remoteUrlWithToken = "https://$GitHubToken@github.com/$username/$RepoName.git"
git remote set-url origin $remoteUrlWithToken

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Success! ===" -ForegroundColor Green
    Write-Host "Your repository is now available at:" -ForegroundColor Green
    Write-Host "https://github.com/$username/$RepoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can share this link via email!" -ForegroundColor Green
    
    # Reset remote URL to remove token (for security)
    git remote set-url origin "https://github.com/$username/$RepoName.git"
    Write-Host ""
    Write-Host "Remote URL updated (token removed for security)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "=== Error ===" -ForegroundColor Red
    Write-Host "Failed to push to GitHub. Please check your token and try again." -ForegroundColor Red
}

