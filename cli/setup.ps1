# CarbonIQ CLI Setup Script for Windows PowerShell

Write-Host "🌍 CarbonIQ CLI Setup" -ForegroundColor Green
Write-Host "="*60

# Check Python installation
Write-Host "`n1. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment (optional but recommended)
Write-Host "`n2. Would you like to create a virtual environment? (Recommended)" -ForegroundColor Yellow
$createVenv = Read-Host "   Create venv? (y/n)"

if ($createVenv -eq 'y' -or $createVenv -eq 'Y') {
    Write-Host "   Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    
    Write-Host "   Activating virtual environment..." -ForegroundColor Cyan
    .\venv\Scripts\Activate.ps1
    
    Write-Host "   ✅ Virtual environment created and activated" -ForegroundColor Green
}

# Install requirements
Write-Host "`n3. Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup .env file
Write-Host "`n4. Setting up configuration..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "   .env file already exists" -ForegroundColor Cyan
} else {
    Copy-Item .env.example .env
    Write-Host "   ✅ Created .env file from template" -ForegroundColor Green
    Write-Host "   ⚠️  Please edit .env with your configuration" -ForegroundColor Yellow
}

# Create output directory
Write-Host "`n5. Creating output directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "measurements" -Force | Out-Null
Write-Host "   ✅ Created measurements directory" -ForegroundColor Green

# Test CLI
Write-Host "`n6. Testing CLI installation..." -ForegroundColor Yellow
python carboniq_cli.py --version

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ CLI is working" -ForegroundColor Green
} else {
    Write-Host "   ❌ CLI test failed" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "="*60 -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Make sure the backend is running:" -ForegroundColor Cyan
Write-Host "   cd backend && python -m uvicorn main:app --reload" -ForegroundColor White
Write-Host "`n2. Test the CLI:" -ForegroundColor Cyan
Write-Host "   python carboniq_cli.py test-backend" -ForegroundColor White
Write-Host "`n3. Run a sample measurement:" -ForegroundColor Cyan
Write-Host "   python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name 'Test'" -ForegroundColor White
Write-Host "`n4. View help:" -ForegroundColor Cyan
Write-Host "   python carboniq_cli.py --help" -ForegroundColor White
Write-Host ""
