# CarbonIQ CLI & Python SDK

Command-line interface and Python SDK for measuring carbon emissions of computing workloads, optimizing code sustainability, and syncing live with the CarbonIQ platform.

## 🚀 Key Capabilities

- 🌍 **Hardware Emission Tracking**: Uses CodeCarbon to measure physical CPU, RAM, and GPU energy consumption & CO2e emissions.
- 🔑 **Personalized Multi-Tenant Sync**: Connects securely to the CarbonIQ backend via API Keys (`ciq_live_...`) to isolate and log each developer's workload history on their dashboard.
- 🌿 **Sustainable Code Optimizer**: AST-based static analyzer (`audit`) and automated green code refactorer (`optimize`) to detect and eliminate energy anti-patterns.
- 🌱 **Electricity Maps & Grid Awareness**: Live grid carbon intensity queries and intelligent execution deferral to cleaner energy hours.
- 📦 **Python Library (`carboniq`)**: Import directly in your codebase with `@carboniq.track` and `@carboniq.defer_until_green`.
- 📊 **Real-Time Terminal Monitoring**: Live intensity tracking and side-by-side benchmark comparison.

---

## 📦 Installation & Setup

### 1. Installation

#### Standard Editable Installation (Development)
From the root of the CarbonIQ repository:
```bash
pip install -e .
```

#### Windows Environment Setup Note
When running Python on Windows without standard script directories in the system `PATH`, ensure the user Scripts directory is added:
```powershell
$scriptsPath = "$env:LOCALAPPDATA\Python\pythoncore-3.15-64\Scripts"
if ($env:PATH -notlike "*$scriptsPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$scriptsPath", [EnvironmentVariableTarget]::User)
    $env:PATH += ";$scriptsPath"
}
```
*Alternatively, the CLI can always be executed via module syntax: `python -m cli.carboniq_cli <command>`.*

### 2. Configure Developer Authentication
1. Authenticate to the CarbonIQ Web Dashboard (`https://carboniq-capstone.vercel.app`).
2. Navigate to the **CLI & Workloads** tab in the sidebar.
3. Click **Generate API Key** and copy your token (`ciq_live_...`).
4. Execute in your terminal:
   ```bash
   carboniq config set-key ciq_live_your_token_here
   ```
5. Confirm connection and telemetry identity:
   ```bash
   carboniq whoami
   ```

---

## 💻 Python Library (`carboniq`) Usage

You can import `carboniq` directly into your data pipelines, machine learning scripts, or backend services:

### 1. Function Tracking Decorator
```python
import carboniq

@carboniq.track(workload_name="train_classifier", workload_type="ml-training")
def train_model():
    # Automatically records CPU/RAM kWh and emissions gCO2e
    # and posts the benchmark to your CarbonIQ dashboard!
    ...
```

### 2. Context Manager
```python
import carboniq

with carboniq.track(workload_name="batch_data_etl", workload_type="data-processing"):
    process_large_dataset()
```

### 3. Grid-Aware Execution Deferral
```python
import carboniq

# Runs only when the electric grid carbon intensity is below 250 gCO2/kWh
@carboniq.defer_until_green(region="us-east-1", max_intensity=250)
def compute_heavy_simulation():
    ...
```

---

## 🛠️ CLI Commands Reference

### 1. Code Optimization & Auditing (Sustainable Code Engine)

#### Audit a Python Script for Carbon Inefficiencies
```bash
carboniq audit path/to/script.py
```
* Analyzes AST for $O(N^2)$ nested loops, memory bloating list comprehensions, un-memoized recursion, and inefficient allocations.
* Outputs efficiency score (0-100), carbon letter grade (**A to F**), and estimated % energy savings.

#### Refactor & Generate Sustainable Code
```bash
# Preview green optimized code in terminal
carboniq optimize path/to/script.py

# Write to a new optimized file
carboniq optimize path/to/script.py --output green_script.py

# Update the file in-place
carboniq optimize path/to/script.py --in-place
```

---

### 2. Workload Measurement & Benchmarking

#### Measure Any Terminal Command
```bash
carboniq measure python my_task.py --workload-name "Model Benchmark" --workload-type "ml"
```

#### Measure a Python Script Directly
```bash
carboniq measure-script path/to/workload.py --workload-name "ETL Run"
```

---

### 3. Real-Time Monitoring & Green Scheduling

#### Live Grid Carbon Intensity Monitor
```bash
carboniq monitor --region us-east-1 --interval 5 --duration 60
```

#### Green Region & Schedule Recommendation
```bash
carboniq recommend-schedule --duration 30 --regions us-east-1 --regions us-west-2 --regions eu-west-1
```

#### Compare Two Measurement Benchmarks
```bash
carboniq compare measurements/baseline.json measurements/optimized.json
```

#### View User Measurement History
```bash
# Fetch from cloud backend (personalized to your user)
carboniq history --source backend --limit 10

# Fetch local measurement files
carboniq history --source local
```

#### View Aggregated User Statistics
```bash
carboniq stats
```

---

### 4. Configuration & Health

```bash
# Show active configuration
carboniq config show

# Set API Key
carboniq config set-key ciq_live_...

# Set Backend API URL (defaults to production Render backend)
carboniq config set-url https://carboniq-backend-duel.onrender.com/api

# Test connection and view logged-in identity
carboniq whoami
carboniq test-backend
carboniq test-electricity-maps
```
