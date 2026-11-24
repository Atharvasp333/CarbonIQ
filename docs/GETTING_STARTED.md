# Getting Started with CarbonIQ

Welcome to CarbonIQ! This guide covers installing and using the CarbonIQ Python SDK and CLI, running your first code audit, profiling workload energy, and connecting to the cloud dashboard.

---

## 1. Installation

### Quick Public PyPI Install

CarbonIQ SDK is officially published on PyPI. Install the core SDK and CLI in any Python 3.9+ environment:

```bash
pip install carboniq-sdk
```

### Optional Hardware Telemetry Profiling

For physical CPU/RAM power tracking on supported bare-metal systems (via CodeCarbon and Intel RAPL):

```bash
pip install "carboniq-sdk[hardware]"
```

> [!NOTE]
> On cloud VMs, WSL, or systems without direct RAPL sensor access, CarbonIQ automatically falls back to a calibrated 65W TDP baseline CPU/RAM energy estimation model.

### Verify Installation

```bash
carboniq --help
```

You should see the CarbonIQ command suite:
* `audit`: Analyze Python scripts for carbon efficiency anti-patterns.
* `optimize`: Generate refactored, energy-efficient Python code.
* `measure`: Profile duration, energy (kWh), and carbon emissions (gCO2e).
* `compare`: Compare baseline vs optimized script metrics.
* `recommend-schedule`: Query regional carbon intensity rankings.
* `deploy-analysis`: Combine execution metrics with regional grid forecasting.
* `carbon-intensity`: Look up current electric grid carbon intensity.
* `monitor`: Stream continuous grid intensity telemetry.

---

## 2. Static Code Auditing & Green Refactoring

### A. Audit a Python Script
Run the static AST auditor to inspect code without running it:

```bash
carboniq audit my_workload.py
```

**Understanding the Audit Grade:**
* **Grades A through F:** Reflect an AST structural heuristic efficiency score based on detected computational anti-patterns (such as repeated `list.append` in loops, unvectorized math, uncached recursive calls, or unbounded generator materialization).
* **Important Distinction:** The static audit score is a structural code heuristic. It highlights algorithmic optimization opportunities but does not represent physical hardware measurements.

### B. Automatically Optimize Inefficient Code
To generate energy-efficient refactored code:

```bash
# Preview the suggested optimizations
carboniq optimize my_workload.py

# Or apply improvements in-place
carboniq optimize my_workload.py --in-place
```

---

## 3. Measuring Workload Energy & Carbon Emissions

Profile the actual execution of any Python command:

```bash
carboniq measure python my_workload.py
```

**Command Output:**
* **Duration:** Wall-clock runtime in seconds.
* **Energy (kWh):** Direct energy consumption measured via hardware telemetry or calculated via the calibrated 65W TDP baseline model.
* **Emissions (gCO2e):** Calculated from energy consumption multiplied by the regional grid carbon intensity factor.
* **Telemetry Tag:** Explicitly reports whether metrics represent physical hardware telemetry or calibrated baseline estimation.

---

## 4. Carbon-Aware Scheduling Guidance

Find the cleanest cloud regions and optimal time windows to schedule compute-intensive workloads:

```bash
# Compare carbon intensity across major AWS regions
carboniq recommend-schedule -d 60 -r us-east-1 -r us-west-2 -r eu-west-1 -r ap-south-1
```

*Output shows estimated carbon reduction when shifting flexible workloads from carbon-heavy regions (e.g., Mumbai `ap-south-1`) to clean-energy regions (e.g., Ireland `eu-west-1` or Oregon `us-west-2`).*

---

## 5. Connecting to the Cloud Dashboard

To synchronize your CLI measurements with the collaborative CarbonIQ web platform:

1. Create an account or sign in to the [CarbonIQ Dashboard](https://carboniq-capstone.vercel.app/home).
2. Navigate to **CLI Workloads** and generate a persistent API Key (`ciq_live_...`).
3. Store the API key in your local CLI configuration:
   ```bash
   carboniq config set-key ciq_live_your_key_here
   ```
4. Now, any workload measured with a name tag will automatically stream telemetry to your dashboard:
   ```bash
   carboniq measure -n "Data-Processing-Job" -t "production" -- python run_pipeline.py
   ```
