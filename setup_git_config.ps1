# Git Configuration Setup Script
# This will configure git with your GitHub account information

Write-Host "=== Git Configuration Setup ===" -ForegroundColor Green
Write-Host ""
Write-Host "This will configure git with your GitHub account information." -ForegroundColor Cyan
Write-Host ""

# Get GitHub username
$username = Read-Host "Enter your GitHub username"
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Username cannot be empty. Exiting." -ForegroundColor Red
    exit 1
}

# Get GitHub email
$email = Read-Host "Enter your GitHub email address"
if ([string]::IsNullOrWhiteSpace($email)) {
    Write-Host "Email cannot be empty. Exiting." -ForegroundColor Red
    exit 1
}

# Confirm
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Username: $username" -ForegroundColor Cyan
Write-Host "  Email: $email" -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "Is this correct? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Set global config
Write-Host ""
Write-Host "Setting global git configuration..." -ForegroundColor Cyan
git config --global user.name $username
git config --global user.email $email

# Set local config for this repo
Write-Host "Setting local git configuration for this repository..." -ForegroundColor Cyan
git config --local user.name $username
git config --local user.email $email

# Verify
Write-Host ""
Write-Host "=== Configuration Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Global configuration:" -ForegroundColor Cyan
git config --global --list | Select-String "user\."
Write-Host ""
Write-Host "Local configuration:" -ForegroundColor Cyan
git config --local --list | Select-String "user\."
Write-Host ""

# Update the last commit with correct author
Write-Host "Updating last commit with correct author information..." -ForegroundColor Cyan
git commit --amend --reset-author --no-edit

Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Green
Write-Host "Your git is now configured with your GitHub account." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a repository on GitHub (if you haven't already)" -ForegroundColor Cyan
Write-Host "2. Run: git remote add origin https://github.com/$username/REPO_NAME.git" -ForegroundColor Cyan
Write-Host "3. Run: git push -u origin main" -ForegroundColor Cyan
Write-Host ""

