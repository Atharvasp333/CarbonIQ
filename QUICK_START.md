# CarbonIQ CLI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install CLI Dependencies
```powershell
cd cli
pip install -r requirements.txt
```

### Step 2: Configure Environment
```powershell
copy .env.example .env
# Edit .env if needed (defaults work fine for local testing)
```

### Step 3: Start the Backend (in a separate terminal)
```powershell
cd backend
python -m uvicorn main:app --reload
```

### Step 4: Test the Setup
```powershell
cd cli
python carboniq_cli.py test-backend
```

### Step 5: Run Your First Measurement
```powershell
python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "My First Test"
```

## ✅ What You Should See

1. **CodeCarbon tracking starts**: Shows measurement progress
2. **Workload executes**: Your script runs normally
3. **Results displayed**: Energy, emissions, duration shown
4. **Data sent to backend**: Confirmation message
5. **Local file saved**: JSON file in `measurements/` directory

## 📊 View Your Results

### Check CLI History
```powershell
python carboniq_cli.py history
```

### Query Backend API
```powershell
curl http://localhost:8000/api/cli/stats
```

### View All Measurements
```powershell
curl http://localhost:8000/api/cli/measurements
```

## 🎯 Available Commands

| Command | Description |
|---------|-------------|
| `measure` | Measure any command's emissions |
| `measure-script` | Measure a Python script |
| `history` | View measurement history |
| `test-backend` | Test API connection |
| `test-carbon-aware` | Test Carbon Aware SDK |

## 💡 Common Use Cases

### Measure a Python Script
```powershell
python carboniq_cli.py measure-script my_script.py --workload-name "Data Processing"
```

### Measure Any Command
```powershell
python carboniq_cli.py measure node app.js --workload-name "Node App" --workload-type "web-server"
```

### Measure with Deadline
```powershell
python carboniq_cli.py measure python train.py --workload-name "ML Training" --deadline "2026-10-25T12:00:00Z"
```

### Skip Backend (Local Only)
```powershell
python carboniq_cli.py measure-script script.py --workload-name "Test" --no-send-to-backend
```

## 🔧 Troubleshooting

### Backend Not Reachable
**Solution**: Make sure backend is running on port 8000
```powershell
cd backend
python -m uvicorn main:app --reload
```

### CodeCarbon Not Working
**Solution**: Reinstall dependencies
```powershell
pip install --upgrade codecarbon
```

### Import Errors
**Solution**: Check you're in the correct directory
```powershell
cd cli  # Make sure you're in the CLI directory
python carboniq_cli.py --help
```

## 📚 Next Steps

1. **Try the compute-intensive workload**:
   ```powershell
   python carboniq_cli.py measure-script sample_workloads/compute_intensive.py --workload-name "Compute Test"
   ```

2. **Measure your own workloads**: Replace `sample_workloads/simple_task.py` with your script

3. **View the full documentation**: Check `cli/README.md` for advanced features

4. **Integrate with AWS**: See `CLI_INTEGRATION_SUMMARY.md` for AWS integration plans

## 🎓 For Your Capstone

### Demo Script (2 minutes)
```powershell
# 1. Show CLI help
python carboniq_cli.py --help

# 2. Test backend connection
python carboniq_cli.py test-backend

# 3. Measure sample workload
python carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "Demo"

# 4. Show results
python carboniq_cli.py history
```

### Key Points to Highlight
- ✅ Automated carbon measurement using CodeCarbon
- ✅ CLI tool for easy workload measurement
- ✅ Backend API for centralized data collection
- ✅ Foundation for AWS region recommendation system
- ✅ Extensible architecture for future enhancements

---

**Need Help?** Check `CLI_INTEGRATION_SUMMARY.md` for detailed information or ask me!
