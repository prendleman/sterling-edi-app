# Create Private Repository and Push - Quick Steps

## Step 1: Create Private Repository on GitHub

1. Go to: https://github.com/new
2. Repository name: `sterling-edi-app`
3. Description: `IBM Sterling EDI Application - Portfolio demonstration for Federated Group IT Director position`
4. **Select: Private** (important!)
5. **DO NOT** check "Initialize with README" (we already have files)
6. Click **Create repository**

## Step 2: Push Your Code

After creating the repository, run these commands:

```powershell
cd "G:\My Drive\Federated_Group\sterling_edi_app"

# Add remote
git remote add origin https://github.com/BlackLake420/sterling-edi-app.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

You'll be prompted for your GitHub credentials. Use:
- Username: `BlackLake420`
- Password: Your GitHub Personal Access Token (not your password - see below)

## Step 3: Add Bill as Collaborator

1. Go to: https://github.com/BlackLake420/sterling-edi-app
2. Click **Settings** (top right)
3. Click **Collaborators and teams** (left sidebar)
4. Click **Add people**
5. Enter Bill's GitHub username or email
6. Click **Add [username] to this repository**
7. Bill will receive an email invitation

## Step 4: Email Bill

Send Bill this email with the repository link. He'll need to accept the collaboration invitation first.

**Repository Link:** https://github.com/BlackLake420/sterling-edi-app

---

## Important: GitHub Authentication

GitHub no longer accepts passwords for git operations. You need a **Personal Access Token**:

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Name: `sterling-edi-app`
4. Select scopes: **repo** (full control of private repositories)
5. Click **Generate token**
6. **Copy the token immediately** (you won't see it again)
7. Use this token as your password when pushing

Or use GitHub Desktop for easier authentication.

