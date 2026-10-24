# CarbonIQ CLI Test Script
# This script runs a complete test of the CLI functionality

Write-Host "🧪 CarbonIQ CLI Test Suite" -ForegroundColor Green
Write-Host "="*60
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Test 1: CLI Help
Write-Host "Test 1: CLI Help Command" -ForegroundColor Yellow
python carboniq_cli.py --help | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   ❌ FAILED" -ForegroundColor Red
    $testsFailed++
}

# Test 2: Backend Connection
Write-Host "`nTest 2: Backend Connection" -ForegroundColor Yellow
Write-Host "   Note: This requires the backend to be running" -ForegroundColor Cyan
python carboniq_cli.py test-backend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   ⚠️  SKIPPED (backend not running)" -ForegroundColor Yellow
    Write-Host "   Start backend with: cd backend && python -m uvicorn main:app --reload" -ForegroundColor Cyan
}

# Test 3: Measure Simple Workload
Write-Host "`nTest 3: Measure Simple Workload" -ForegroundColor Yellow
python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "CLI Test Simple" --no-send-to-backend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   ❌ FAILED" -ForegroundColor Red
    $testsFailed++
}

# Test 4: History Command
Write-Host "`nTest 4: View History" -ForegroundColor Yellow
python carboniq_cli.py history --limit 5
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   ❌ FAILED" -ForegroundColor Red
    $testsFailed++
}

# Test 5: Measure with Backend (if running)
Write-Host "`nTest 5: Measure and Send to Backend" -ForegroundColor Yellow
Write-Host "   Note: This requires the backend to be running" -ForegroundColor Cyan
python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "CLI Test Backend" --send-to-backend
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ PASSED" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   ⚠️  SKIPPED (backend not running or measurement failed)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "="*60 -ForegroundColor Green
Write-Host "Test Summary" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -gt 0) { "Red" } else { "Green" })
Write-Host "="*60 -ForegroundColor Green
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Some tests failed. Please check the output above." -ForegroundColor Red
    exit 1
}
