# CarbonIQ CLI

Command-line interface for measuring carbon emissions of computing workloads and integrating with the CarbonIQ backend.

## Features

- 🌍 **Carbon Emission Measurement**: Uses CodeCarbon to track energy consumption and emissions
- 🔄 **Backend Integration**: Sends measurements to CarbonIQ API for analysis and storage
- 🌱 **Electricity Maps Integration**: Real-time carbon intensity data for AWS regions
- 📊 **Measurement History**: Track and compare measurements over time (local + backend)
- 🎯 **Intelligent Scheduling**: Recommends optimal execution times based on carbon forecasts
- 📈 **Real-Time Monitoring**: Monitor live carbon intensity for regions
- 🔬 **Comparison Tool**: Compare measurements to track improvements
- 📉 **Statistics**: Aggregate stats across all your workloads
- 🧪 **Sample Workloads**: Test workloads included for quick testing

## Installation

1. **Install Python dependencies**:
   ```powershell
   cd cli
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```powershell
   copy .env.example .env
   # Edit .env with your configuration
   ```

3. **Verify installation**:
   ```powershell
   python carboniq_cli.py --help
   ```

## Configuration

Edit `cli/.env` with your settings:

```env
# Backend API URL (make sure backend is running)
CARBONIQ_API_URL=http://localhost:8000/api

# CodeCarbon settings
CODECARBON_TRACKING_MODE=machine
CODECARBON_OUTPUT_DIR=./measurements

# Carbon Aware SDK (optional)
CARBON_AWARE_SDK_URL=http://localhost:5073/emissions/forecasts/current
CARBON_AWARE_SDK_ENABLED=false
```

## Usage

### 1. Test Backend Connection

```powershell
python carboniq_cli.py test-backend
```

### 2. Test Electricity Maps API

```powershell
python carboniq_cli.py test-electricity-maps
```

### 3. Measure a Command

```powershell
python carboniq_cli.py measure python sample_workloads/simple_task.py --workload-name "Simple Task" --workload-type "test"
```

### 4. Measure a Python Script Directly

```powershell
python carboniq_cli.py measure-script sample_workloads/compute_intensive.py --workload-name "Compute Test"
```

### 5. View Measurement History

```powershell
# From backend (recommended)
python carboniq_cli.py history --source backend

# From local files
python carboniq_cli.py history --source local
```

### 6. View Statistics

```powershell
python carboniq_cli.py stats
```

### 7. Monitor Real-Time Carbon Intensity

```powershell
python carboniq_cli.py monitor --region us-east-1 --interval 10 --duration 60
```

### 8. Get Schedule Recommendations

```powershell
python carboniq_cli.py recommend-schedule --duration 30 --regions us-east-1 --regions us-west-2
```

### 9. Compare Two Measurements

```powershell
python carboniq_cli.py compare measurements/baseline.json measurements/optimized.json
```

## Command Reference

### `measure`
Measure carbon emissions of any command.

**Arguments:**
- `COMMAND`: Command to execute (e.g., `python script.py`)

**Options:**
- `--workload-name, -n`: Name for this workload (required)
- `--workload-type, -t`: Type of workload (default: "general")
- `--deadline, -d`: Deadline for workload (ISO 8601 format)
- `--send-to-backend/--no-send-to-backend`: Send to backend (default: true)
- `--check-carbon-aware/--no-carbon-aware`: Query Carbon Aware SDK (default: false)

### `measure-script`
Convenience command for measuring Python scripts.

**Arguments:**
- `SCRIPT_PATH`: Path to Python script

**Options:**
- `--workload-name, -n`: Name for this workload (defaults to script name)
- `--workload-type, -t`: Type of workload (default: "script")
- `--send-to-backend/--no-send-to-backend`: Send to backend (default: true)

### `history`
Show recent measurement history from backend or local files.

**Options:**
- `--limit, -l`: Number of measurements to show (default: 10)
- `--source, -s`: Source: 'backend' or 'local' (default: backend)

### `stats`
Show aggregate statistics from backend (total emissions, energy, averages, etc.)

### `monitor`
Monitor real-time carbon intensity for a region.

**Options:**
- `--region, -r`: AWS region to monitor (default: us-east-1)
- `--interval, -i`: Update interval in seconds (default: 10)
- `--duration, -d`: Total monitoring duration in seconds (default: 60)

### `recommend-schedule`
Get carbon-optimal execution schedule recommendation.

**Arguments:**
- `--duration, -d`: Expected workload duration in minutes (required)
- `--deadline`: Deadline in ISO 8601 format (optional)
- `--regions, -r`: AWS regions to consider (can specify multiple)

### `compare`
Compare two measurement files side-by-side.

**Arguments:**
- `BASELINE_FILE`: Path to baseline measurement
- `COMPARISON_FILE`: Path to comparison measurement

### `test-electricity-maps`
Test Electricity Maps API connection and get current carbon intensity.

## Output

Measurements are saved in two locations:

1. **Local JSON files**: `./measurements/<workload_name>_<timestamp>.json`
2. **Backend database**: Sent to CarbonIQ API (if enabled)

### Measurement Data Structure

```json
{
  "workload_name": "My Workload",
  "workload_type": "ml-training",
  "measurement": {
    "duration_seconds": 45.23,
    "emissions_gco2e": 12.45,
    "energy_kwh": 0.0234,
    "cpu_energy": 0.0200,
    "ram_energy": 0.0034,
    "country_name": "United States",
    "carbon_intensity": 532.0
  },
  "carbon_aware_data": null,
  "deadline": null,
  "measured_at": "2026-10-24T14:30:00Z"
}
```

## Example Workflow

### Complete Test Flow

```powershell
# 1. Start the backend (in another terminal)
cd backend
python -m uvicorn main:app --reload

# 2. Test backend connection
python carboniq_cli.py test-backend

# 3. Run a simple measurement
python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "Simple Test"

# 4. Run a compute-intensive workload
python carboniq_cli.py measure-script sample_workloads/compute_intensive.py --workload-name "Compute Intensive Test" --workload-type "compute"

# 5. View history
python carboniq_cli.py history
```

## Troubleshooting

### Backend not reachable
- Ensure the backend is running: `cd backend && python -m uvicorn main:app --reload`
- Check `CARBONIQ_API_URL` in `.env`
- Test with: `python carboniq_cli.py test-backend`

### CodeCarbon not tracking
- Check Python version (3.8+ required)
- Ensure CodeCarbon is installed: `pip install codecarbon`
- Check `CODECARBON_OUTPUT_DIR` permissions

### Carbon Aware SDK not available
- Carbon Aware SDK is optional
- Set `CARBON_AWARE_SDK_ENABLED=true` in `.env` if you have it running
- Download from: https://github.com/Green-Software-Foundation/carbon-aware-sdk

## Next Steps

1. **Integrate with AWS**: Add AWS workload measurement
2. **Recommendation Engine**: Implement full constraint-based recommendation system
3. **Database Persistence**: Replace in-memory storage with PostgreSQL
4. **Scheduling**: Add automated workload scheduling based on carbon intensity
5. **Multi-region Support**: Expand to support more cloud providers

## Support

For issues or questions:
- Check the main project README
- Review backend logs
- Check CodeCarbon documentation: https://mlco2.github.io/codecarbon/
