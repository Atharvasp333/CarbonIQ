# CarbonIQ - Start All Services in One Command
# PowerShell script for Windows

Write-Host ">> Starting CarbonIQ Development Environment..." -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "[!] Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Found .env file" -ForegroundColor Green
Write-Host ""

$rootPath = $PSScriptRoot
if (-Not $rootPath) {
    $rootPath = (Get-Location).Path
}

$backendDir = Join-Path $rootPath "backend"
$frontendDir = Join-Path $rootPath "frontend"

# Start Backend in background
Write-Host "[*] Starting Backend (FastAPI)..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    python -m uvicorn main:app --reload --port 8000
} -ArgumentList $backendDir

Write-Host "    Backend starting on http://localhost:8000" -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start Frontend in background
Write-Host "[*] Starting Frontend (React + Vite)..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev
} -ArgumentList $frontendDir

Write-Host "    Frontend starting on http://localhost:5173" -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=================================================" -ForegroundColor Green
Write-Host "[+] CarbonIQ is running!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend  : http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Logs (Press Ctrl+C to stop all services):" -ForegroundColor Yellow
Write-Host ""

# Monitor jobs and show output
try {
    while ($true) {
        if ($backendJob) {
            $backendOutput = Receive-Job -Job $backendJob
            if ($backendOutput) {
                Write-Host "[BACKEND] $backendOutput" -ForegroundColor Blue
            }
            if ($backendJob.State -eq "Failed") {
                Write-Host "[!] Backend service failed!" -ForegroundColor Red
                break
            }
        }

        if ($frontendJob) {
            $frontendOutput = Receive-Job -Job $frontendJob
            if ($frontendOutput) {
                Write-Host "[FRONTEND] $frontendOutput" -ForegroundColor Magenta
            }
            if ($frontendJob.State -eq "Failed") {
                Write-Host "[!] Frontend service failed!" -ForegroundColor Red
                break
            }
        }

        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host ""
    Write-Host "[*] Stopping all services..." -ForegroundColor Yellow
    $jobs = @()
    if ($backendJob) { $jobs += $backendJob }
    if ($frontendJob) { $jobs += $frontendJob }

    if ($jobs.Count -gt 0) {
        Stop-Job -Job $jobs -ErrorAction SilentlyContinue
        Remove-Job -Job $jobs -ErrorAction SilentlyContinue
    }
    Write-Host "[+] All services stopped" -ForegroundColor Green
}
