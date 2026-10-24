# CarbonIQ - Start All Services in One Command
# PowerShell script for Windows

Write-Host "🚀 Starting CarbonIQ Development Environment..." -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found .env file" -ForegroundColor Green
Write-Host ""

# Start Backend in background
Write-Host "📦 Starting Backend (FastAPI)..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd backend
    python -m uvicorn main:app --reload --port 8000
}
Write-Host "   Backend starting on http://localhost:8000" -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start Frontend in background
Write-Host "🎨 Starting Frontend (React + Vite)..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd frontend
    npm run dev
}
Write-Host "   Frontend starting on http://localhost:5173" -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ CarbonIQ is running!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend:  http://localhost:5173" -ForegroundColor Cyan
Write-Host "⚡ Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Logs:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop all services" -ForegroundColor Gray
Write-Host ""

# Monitor jobs and show output
try {
    while ($true) {
        # Show backend output
        $backendOutput = Receive-Job -Job $backendJob
        if ($backendOutput) {
            Write-Host "[BACKEND] $backendOutput" -ForegroundColor Blue
        }
        
        # Show frontend output
        $frontendOutput = Receive-Job -Job $frontendJob
        if ($frontendOutput) {
            Write-Host "[FRONTEND] $frontendOutput" -ForegroundColor Magenta
        }
        
        # Check if jobs are still running
        if ($backendJob.State -eq "Failed" -or $frontendJob.State -eq "Failed") {
            Write-Host "❌ One or more services failed to start!" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host ""
    Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
    Write-Host "✅ All services stopped" -ForegroundColor Green
}
