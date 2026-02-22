# Auto Push to GitHub
# Usage: .\push.ps1
# Usage with message: .\push.ps1 "your commit message"

$BACKEND = "d:\html\digital lib sysytem env files\Digital Library SYSTEM\backend"
$MSG = if ($args[0]) { $args[0] } else { "Auto push: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }

Write-Host "📦 Staging all changes..." -ForegroundColor Cyan
git -C $BACKEND add -A

Write-Host "💾 Committing: $MSG" -ForegroundColor Cyan
git -C $BACKEND commit -m $MSG

if ($LASTEXITCODE -eq 0) {
    Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
    git -C $BACKEND push origin master
    Write-Host "✅ Done! Railway will auto-deploy now." -ForegroundColor Green
} else {
    Write-Host "ℹ️  Nothing to commit." -ForegroundColor Yellow
    Write-Host "🚀 Pushing existing commits..." -ForegroundColor Cyan
    git -C $BACKEND push origin master
    Write-Host "✅ Done!" -ForegroundColor Green
}
