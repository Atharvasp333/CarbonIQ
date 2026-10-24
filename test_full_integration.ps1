# CarbonIQ Full Integration Test Script
# Tests: CLI + CodeCarbon + Backend API + Database + AWS S3

Write-Host "🧪 CarbonIQ Full Integration Test" -ForegroundColor Green
Write-Host "="*70
Write-Host ""

$ErrorCount = 0
$SuccessCount = 0

# Test 1: Backend Health Check
Write-Host "Test 1: Backend Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing | ConvertFrom-Json
    if ($health.status -eq "ok") {
        Write-Host "   ✅ Backend is running" -ForegroundColor Green
        Write-Host "   Database: $($health.keys_loaded.database)" -ForegroundColor Cyan
        $SuccessCount++
    } else {
        Write-Host "   ❌ Backend returned unhealthy status" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ Backend not reachable - Is it running?" -ForegroundColor Red
    Write-Host "   Start with: cd backend && python -m uvicorn main:app --reload" -ForegroundColor Yellow
    $ErrorCount++
}

# Test 2: CLI to Backend Connection
Write-Host "`nTest 2: CLI to Backend Connection..." -ForegroundColor Yellow
cd cli
try {
    $output = python carboniq_cli.py test-backend 2>&1
    if ($output -match "Backend is healthy") {
        Write-Host "   ✅ CLI can connect to backend" -ForegroundColor Green
        $SuccessCount++
    } else {
        Write-Host "   ❌ CLI cannot connect to backend" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ CLI test failed: $_" -ForegroundColor Red
    $ErrorCount++
}

# Test 3: CodeCarbon Measurement
Write-Host "`nTest 3: CodeCarbon Measurement..." -ForegroundColor Yellow
try {
    $output = python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "Integration Test" --no-send-to-backend 2>&1
    if ($output -match "Measurement completed") {
        Write-Host "   ✅ CodeCarbon measurement working" -ForegroundColor Green
        $SuccessCount++
    } else {
        Write-Host "   ❌ Measurement failed" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ Measurement test failed: $_" -ForegroundColor Red
    $ErrorCount++
}

# Test 4: CLI to Backend Data Transfer
Write-Host "`nTest 4: CLI to Backend Data Transfer..." -ForegroundColor Yellow
try {
    $output = python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "Backend Test" --send-to-backend 2>&1
    if ($output -match "Results sent to backend successfully") {
        Write-Host "   ✅ Data sent to backend successfully" -ForegroundColor Green
        $SuccessCount++
        
        # Verify data was received
        Start-Sleep -Seconds 1
        $stats = Invoke-WebRequest -Uri "http://localhost:8000/api/cli/stats" -UseBasicParsing | ConvertFrom-Json
        Write-Host "   📊 Backend stats: $($stats.total_measurements) measurements, $($stats.total_emissions_gco2e) gCO2e total" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Failed to send data to backend" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ Data transfer test failed: $_" -ForegroundColor Red
    $ErrorCount++
}

# Test 5: Measurement History
Write-Host "`nTest 5: Measurement History..." -ForegroundColor Yellow
try {
    $output = python carboniq_cli.py history --limit 3 2>&1
    if ($output -match "Recent Measurements") {
        Write-Host "   ✅ History command working" -ForegroundColor Green
        $SuccessCount++
    } else {
        Write-Host "   ❌ History command failed" -ForegroundColor Red
        $ErrorCount++
    }
} catch {
    Write-Host "   ❌ History test failed: $_" -ForegroundColor Red
    $ErrorCount++
}

# Test 6: AWS S3 Route (list files)
Write-Host "`nTest 6: AWS S3 Integration (List Files Route)..." -ForegroundColor Yellow
Write-Host "   ⚠️  Skipping - requires AWS credentials" -ForegroundColor Yellow
Write-Host "   To test: Use /api/aws/list-files endpoint with your credentials" -ForegroundColor Cyan

# Test 7: Database Connection
Write-Host "`nTest 7: Database Connection..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing | ConvertFrom-Json
    if ($health.keys_loaded.database -eq $true) {
        Write-Host "   ✅ Database connected" -ForegroundColor Green
        $SuccessCount++
    } else {
        Write-Host "   ⚠️  Database not connected (using in-memory storage)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not check database status" -ForegroundColor Yellow
}

cd ..

# Summary
Write-Host "`n" -NoNewline
Write-Host "="*70 -ForegroundColor Green
Write-Host "Test Summary" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green
Write-Host "✅ Passed: $SuccessCount" -ForegroundColor Green
Write-Host "❌ Failed: $ErrorCount" -ForegroundColor Red
Write-Host "="*70 -ForegroundColor Green
Write-Host ""

if ($ErrorCount -eq 0) {
    Write-Host "🎉 All critical tests passed!" -ForegroundColor Green
    Write-Host "✅ Your CarbonIQ system is fully operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test AWS S3 integration with your credentials" -ForegroundColor Cyan
    Write-Host "2. Set up Electricity Maps API key for carbon intensity data" -ForegroundColor Cyan
    Write-Host "3. Run compute-intensive workloads for benchmarking" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "⚠️  Some tests failed - check the output above" -ForegroundColor Red
    exit 1
}
