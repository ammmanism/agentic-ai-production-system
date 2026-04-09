# 🚀 Daily Push Automation Script for Windows
# This script stages changes, commits with a timestamp, and pushes to GitHub.

$repoPath = "C:\Users\amman\.gemini\antigravity\scratch\agentic-ai-production-system"
Set-Location $repoPath

# Check for changes
$status = git status --porcelain
if ($null -eq $status -or $status -eq "") {
    Write-Host "✅ No changes to sync today. (Green graph is safe!)"
    exit 0
}

# Stage changes
Write-Host "📝 Staging changes..."
git add .

# Create persistent daily commit message
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "chore: daily system sync - $timestamp"

Write-Host "💾 Committing changes: $commitMessage"
git commit -m $commitMessage

# Push to origin
Write-Host "🚀 Pushing to GitHub..."
git push origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host "✨ Daily sync complete!"
} else {
    Write-Error "❌ Push failed. Check your Git credentials (SSH/PAT)."
}
