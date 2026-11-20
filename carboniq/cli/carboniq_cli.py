"""
CarbonIQ CLI - Carbon-aware workload measurement tool
Main entry point for measuring workload carbon emissions and communicating with the backend.
"""

import os
import sys
import json
import click
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

try:
    from .codecarbon_wrapper import CodeCarbonMeasurement
    from .backend_client import BackendClient
    from .carbon_aware import CarbonAwareClient
    from .carbon_aware_sdk import CarbonAwareSDKClient, DEFAULT_COMPARISON_REGIONS
    from .config_manager import get_api_key, get_api_url, save_config_value, get_config
except (ImportError, ValueError):
    try:
        from carboniq.cli.codecarbon_wrapper import CodeCarbonMeasurement
        from carboniq.cli.backend_client import BackendClient
        from carboniq.cli.carbon_aware import CarbonAwareClient
        from carboniq.cli.carbon_aware_sdk import CarbonAwareSDKClient, DEFAULT_COMPARISON_REGIONS
        from carboniq.cli.config_manager import get_api_key, get_api_url, save_config_value, get_config
    except ImportError:
        try:
            from cli.codecarbon_wrapper import CodeCarbonMeasurement
            from cli.backend_client import BackendClient
            from cli.carbon_aware import CarbonAwareClient
            from cli.carbon_aware_sdk import CarbonAwareSDKClient, DEFAULT_COMPARISON_REGIONS
            from cli.config_manager import get_api_key, get_api_url, save_config_value, get_config
        except ImportError:
            from codecarbon_wrapper import CodeCarbonMeasurement
            from backend_client import BackendClient
            from carbon_aware import CarbonAwareClient
            from carbon_aware_sdk import CarbonAwareSDKClient, DEFAULT_COMPARISON_REGIONS
            from config_manager import get_api_key, get_api_url, save_config_value, get_config

# Load environment variables
load_dotenv()

# Import AST optimizer functions
try:
    from carboniq.optimizer import audit_code, optimize_code
except ImportError:
    try:
        from ..optimizer import audit_code, optimize_code
    except (ImportError, ValueError):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
        from carboniq.optimizer import audit_code, optimize_code

# Configuration
API_URL = get_api_url()
OUTPUT_DIR = Path(os.getenv("CODECARBON_OUTPUT_DIR", "./measurements"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """CarbonIQ CLI - Measure and analyze carbon emissions of computing workloads."""
    pass


@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.option('--workload-name', '-n', required=True, help='Name for this workload')
@click.option('--workload-type', '-t', default='general', help='Type of workload (e.g., ml-training, data-processing, batch-job)')
@click.option('--deadline', '-d', help='Deadline for workload completion (ISO 8601 format)')
@click.option('--send-to-backend/--no-send-to-backend', default=True, help='Send results to CarbonIQ backend')
@click.option('--check-carbon-intensity/--no-carbon-intensity', default=False, help='Check Electricity Maps for current carbon intensity')
def measure(command, workload_name, workload_type, deadline, send_to_backend, check_carbon_intensity):
    """
    Measure carbon emissions of a workload.
    
    Example:
        carboniq measure python train_model.py --workload-name "ML Training" --workload-type ml-training
    """
    click.echo(f"\n🌍 CarbonIQ - Measuring workload: {workload_name}")
    click.echo(f"📊 Type: {workload_type}")
    click.echo(f"⚡ Command: {' '.join(command)}\n")
    
    # Step 1: Measure with CodeCarbon
    click.echo("Starting CodeCarbon measurement...")
    
    measurement = CodeCarbonMeasurement(
        workload_name=workload_name,
        workload_type=workload_type,
        output_dir=OUTPUT_DIR
    )
    
    try:
        results = measurement.measure_command(list(command))
        
        if not results:
            click.echo("❌ Measurement failed - no results returned", err=True)
            sys.exit(1)
        
        click.echo("\n✅ Measurement completed!")
        _display_results(results)
        
        # Step 2: Check Carbon Intensity (optional)
        carbon_aware_data = None
        if check_carbon_intensity:
            click.echo("\n🌱 Querying Electricity Maps for carbon intensity...")
            carbon_client = CarbonAwareClient()
            if carbon_client.is_available():
                carbon_aware_data = carbon_client.get_optimal_windows(
                    duration_minutes=int(results.get('duration_seconds', 0) / 60),
                    regions=["us-east-1", "us-west-2", "eu-west-1"],
                    deadline=deadline
                )
                if carbon_aware_data:
                    click.echo(f"✅ Optimal AWS region: {carbon_aware_data.get('optimal_region')} " + 
                              f"({carbon_aware_data.get('optimal_intensity')} gCO2/kWh)")
                else:
                    click.echo("⚠️  No carbon intensity data available")
            else:
                click.echo("⚠️  Electricity Maps API not available")
        
        # Step 3: Send to backend
        if send_to_backend:
            click.echo("\n📤 Sending results to CarbonIQ backend...")
            backend_client = BackendClient(API_URL)
            
            payload = {
                "workload_name": workload_name,
                "workload_type": workload_type,
                "measurement": results,
                "carbon_aware_data": carbon_aware_data,
                "deadline": deadline,
                "measured_at": datetime.utcnow().isoformat()
            }
            
            success = backend_client.send_measurement(payload)
            if success:
                click.echo("✅ Results sent to backend successfully")
            else:
                click.echo("⚠️  Failed to send results to backend", err=True)
        
        # Save local copy
        output_file = OUTPUT_DIR / f"{workload_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "workload_name": workload_name,
                "workload_type": workload_type,
                "measurement": results,
                "carbon_aware_data": carbon_aware_data,
                "deadline": deadline,
                "measured_at": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        click.echo(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Error during measurement: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.option('--workload-name', '-n', help='Name for this workload (defaults to script filename)')
@click.option('--workload-type', '-t', default='script', help='Type of workload')
@click.option('--send-to-backend/--no-send-to-backend', default=True, help='Send results to CarbonIQ backend')
def measure_script(script_path, workload_name, workload_type, send_to_backend):
    """
    Measure carbon emissions of a Python script.
    
    Example:
        carboniq measure-script my_script.py --workload-name "Data Processing"
    """
    if not workload_name:
        workload_name = Path(script_path).stem
    
    command = [sys.executable, script_path]
    
    # Call the measure command with constructed parameters
    ctx = click.get_current_context()
    ctx.invoke(measure, 
               command=command, 
               workload_name=workload_name,
               workload_type=workload_type,
               deadline=None,
               send_to_backend=send_to_backend,
               check_carbon_intensity=False)


@cli.command()
@click.option('--limit', '-l', default=10, help='Number of recent measurements to show')
@click.option('--source', '-s', type=click.Choice(['local', 'backend']), default='backend', help='Source: local files or backend API')
def history(limit, source):
    """Show recent measurement history."""
    
    if source == 'backend':
        # Fetch from backend
        click.echo(f"\n📊 Recent Measurements from Backend (last {limit}):\n")
        backend_client = BackendClient(API_URL)
        
        try:
            import requests
            response = requests.get(f"{API_URL}/cli/measurements/history?limit={limit}")
            if response.status_code == 200:
                data = response.json()
                measurements = data.get('measurements', [])
                
                if not measurements:
                    click.echo("No measurements found in backend.")
                    return
                
                for i, m in enumerate(measurements, 1):
                    click.echo(f"{i}. {m['workload_name']}")
                    click.echo(f"   Type: {m['workload_type']}")
                    click.echo(f"   Emissions: {m['emissions_gco2e']:.2f} gCO2e")
                    click.echo(f"   Duration: {m['duration_seconds']:.2f}s")
                    click.echo(f"   Energy: {m['energy_kwh']:.6f} kWh")
                    click.echo(f"   Measured: {m['measured_at']}")
                    click.echo()
            else:
                click.echo(f"❌ Failed to fetch from backend: {response.status_code}")
                click.echo("Falling back to local history...")
                source = 'local'
        except Exception as e:
            click.echo(f"❌ Error fetching from backend: {e}")
            click.echo("Falling back to local history...")
            source = 'local'
    
    if source == 'local':
        # Fetch from local files
        click.echo(f"\n📊 Recent Measurements from Local Files (last {limit}):\n")
        
        measurements = sorted(OUTPUT_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)[:limit]
        
        if not measurements:
            click.echo("No measurements found.")
            return
        
        for i, measurement_file in enumerate(measurements, 1):
            try:
                with open(measurement_file, 'r') as f:
                    data = json.load(f)
                
                click.echo(f"{i}. {data.get('workload_name', 'Unknown')}")
                click.echo(f"   Type: {data.get('workload_type', 'N/A')}")
                click.echo(f"   Emissions: {data.get('measurement', {}).get('emissions_gco2e', 'N/A')} gCO2e")
                click.echo(f"   Duration: {data.get('measurement', {}).get('duration_seconds', 'N/A')}s")
                click.echo(f"   Measured: {data.get('measured_at', 'N/A')}")
                click.echo()
            except Exception as e:
                click.echo(f"   Error reading file: {e}\n")


@cli.command()
def stats():
    """Show aggregate statistics from backend."""
    click.echo("\n📊 Workload Measurement Statistics\n")
    
    try:
        import requests
        response = requests.get(f"{API_URL}/cli/measurements/stats")
        
        if response.status_code == 200:
            data = response.json()
            
            click.echo("="*60)
            click.echo("OVERALL STATISTICS")
            click.echo("="*60)
            click.echo(f"Total Measurements:  {data['total_measurements']}")
            click.echo(f"Total Emissions:     {data['total_emissions_gco2e']:.2f} gCO2e")
            click.echo(f"Total Energy:        {data['total_energy_kwh']:.6f} kWh")
            click.echo(f"Avg Emissions:       {data['avg_emissions_gco2e']:.2f} gCO2e")
            click.echo(f"Avg Duration:        {data['avg_duration_seconds']:.2f}s")
            
            if data['workload_types']:
                click.echo("\n" + "="*60)
                click.echo("BREAKDOWN BY WORKLOAD TYPE")
                click.echo("="*60)
                for wt in data['workload_types']:
                    click.echo(f"\n{wt['workload_type']}:")
                    click.echo(f"  Count: {wt['count']}")
                    click.echo(f"  Total Emissions: {wt['total_emissions']:.2f} gCO2e")
            
            click.echo("\n" + "="*60 + "\n")
        else:
            click.echo(f"❌ Failed to fetch stats: {response.status_code}")
    except Exception as e:
        click.echo(f"❌ Error fetching stats: {e}")


@cli.command()
def test_backend():
    """Test connection to CarbonIQ backend."""
    click.echo(f"\n🔌 Testing connection to: {API_URL}\n")
    
    backend_client = BackendClient(API_URL)
    is_healthy = backend_client.health_check()
    
    if is_healthy:
        click.echo("✅ Backend is healthy and reachable")
    else:
        click.echo("❌ Backend is not reachable or unhealthy")
        sys.exit(1)


@cli.command()
@click.option('--region', '-r', default='us-east-1', help='AWS region to monitor')
@click.option('--interval', '-i', default=10, help='Update interval in seconds')
@click.option('--duration', '-d', default=60, help='Total monitoring duration in seconds')
def monitor(region, interval, duration):
    """
    Monitor real-time carbon intensity for a region.
    
    Example:
        carboniq monitor --region us-east-1 --interval 10 --duration 60
    """
    import time
    
    click.echo(f"\n🌍 Monitoring Carbon Intensity for {region}")
    click.echo(f"⏱️  Interval: {interval}s | Duration: {duration}s\n")
    
    carbon_client = CarbonAwareClient()
    if not carbon_client.is_available():
        click.echo("❌ Electricity Maps API not available", err=True)
        sys.exit(1)
    
    start_time = time.time()
    readings = []
    lowest = None
    highest = None
    
    try:
        while (time.time() - start_time) < duration:
            data = carbon_client.get_current_intensity(region)
            
            if data and data.get('carbon_intensity') is not None:
                intensity = float(data['carbon_intensity'])
                renewable = float(data.get('renewable_percentage') or 0.0)
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Track min/max
                if lowest is None or intensity < float(lowest['intensity']):
                    lowest = {'intensity': intensity, 'time': timestamp}
                if highest is None or intensity > float(highest['intensity']):
                    highest = {'intensity': intensity, 'time': timestamp}
                
                readings.append(intensity)
                
                # Color code based on intensity
                if intensity < 300:
                    status = "🟢 LOW"
                elif intensity < 500:
                    status = "🟡 MEDIUM"
                else:
                    status = "🔴 HIGH"
                
                click.echo(f"[{timestamp}] {status} | {intensity:.1f} gCO2/kWh | Renewable: {renewable:.1f}%")
            else:
                click.echo(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  No data available")
            
            time.sleep(interval)
        
        # Summary
        if readings and lowest and highest:
            avg_intensity = sum(readings) / len(readings)
            click.echo("\n" + "="*60)
            click.echo("MONITORING SUMMARY")
            click.echo("="*60)
            click.echo(f"Average Intensity: {avg_intensity:.1f} gCO2/kWh")
            click.echo(f"Lowest:  {lowest['intensity']:.1f} gCO2/kWh at {lowest['time']}")
            click.echo(f"Highest: {highest['intensity']:.1f} gCO2/kWh at {highest['time']}")
            click.echo(f"Total Readings: {len(readings)}")
            click.echo("="*60)
            
    except KeyboardInterrupt:
        click.echo("\n\n⏸️  Monitoring stopped by user")


@cli.command()
@click.option('--duration', '-d', required=True, type=int, help='Expected workload duration in minutes')
@click.option('--deadline', help='Deadline (ISO 8601 format, e.g., 2026-10-25T12:00:00)')
@click.option('--regions', '-r', multiple=True, default=['us-east-1', 'us-west-2', 'eu-west-1'], help='AWS regions to consider')
def recommend_schedule(duration, deadline, regions):
    """
    Get carbon-optimal execution schedule recommendation.
    
    Example:
        carboniq recommend-schedule --duration 30 --regions us-east-1 --regions us-west-2
    """
    click.echo(f"\n🧠 Finding optimal execution window...")
    click.echo(f"📊 Duration: {duration} minutes")
    click.echo(f"🌍 Regions: {', '.join(regions)}\n")
    
    carbon_client = CarbonAwareClient()
    if not carbon_client.is_available():
        click.echo("❌ Electricity Maps API not available", err=True)
        sys.exit(1)
    
    # Get optimal windows for each region
    results = carbon_client.get_optimal_windows(
        duration_minutes=duration,
        regions=list(regions),
        deadline=deadline
    )
    
    if not results:
        click.echo("❌ Could not get carbon intensity data", err=True)
        sys.exit(1)
    
    # Display recommendation
    click.echo("="*60)
    click.echo("CARBON-AWARE DECISION SUPPORT (RECOMMENDATION ONLY)")
    click.echo("="*60)
    click.echo("Notice: Advisory guidance only; does not perform automatic workload migration or execution.")
    click.echo(f"\n🏆 RECOMMENDED REGION: {results['optimal_region']}")
    click.echo(f"⚡ Carbon Intensity: {results['optimal_intensity']:.1f} gCO2/kWh")
    click.echo(f"🌱 Renewable %: {results.get('renewable_percentage', 'N/A')}")
    
    if results.get('recommendation'):
        click.echo(f"\n💡 RECOMMENDATION:")
        click.echo(f"   {results['recommendation']}")
    
    # Show comparison with other regions
    if len(regions) > 1:
        click.echo(f"\n📊 COMPARISON:")
        for r_info in results.get('all_regions', []):
            r_reg = r_info.get('aws_region')
            if r_reg != results['optimal_region']:
                r_int = r_info.get('carbon_intensity', 'N/A')
                r_ren = r_info.get('renewable_percentage', 'N/A')
                click.echo(f"   • {r_reg} ({r_info.get('zone', 'N/A')}): {r_int} gCO2/kWh (Renewable: {r_ren}%)")
    
    if results.get('source'):
        mode_label = "Live Electricity Maps API" if "live" in results['source'] else "Empirical Regional Baseline"
        click.echo(f"\n📡 Data Source: {mode_label}")
    
    click.echo("\n" + "="*60)


@cli.command()
@click.argument('baseline_file', type=click.Path(exists=True))
@click.argument('comparison_file', type=click.Path(exists=True))
def compare(baseline_file, comparison_file):
    """
    Compare two measurement files.
    
    Example:
        carboniq compare measurements/baseline.json measurements/optimized.json
    """
    try:
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
        with open(comparison_file, 'r') as f:
            comparison = json.load(f)
        
        baseline_m = baseline.get('measurement', {})
        comparison_m = comparison.get('measurement', {})
        
        # Calculate differences
        emissions_diff = comparison_m.get('emissions_gco2e', 0) - baseline_m.get('emissions_gco2e', 0)
        emissions_pct = (emissions_diff / baseline_m.get('emissions_gco2e', 1)) * 100
        
        duration_diff = comparison_m.get('duration_seconds', 0) - baseline_m.get('duration_seconds', 0)
        duration_pct = (duration_diff / baseline_m.get('duration_seconds', 1)) * 100
        
        energy_diff = comparison_m.get('energy_kwh', 0) - baseline_m.get('energy_kwh', 0)
        energy_pct = (energy_diff / baseline_m.get('energy_kwh', 0.0001)) * 100
        
        # Display comparison
        click.echo("\n" + "="*60)
        click.echo("MEASUREMENT COMPARISON")
        click.echo("="*60)
        
        click.echo(f"\n📊 BASELINE: {baseline.get('workload_name')}")
        click.echo(f"   Emissions: {baseline_m.get('emissions_gco2e'):.2f} gCO2e")
        click.echo(f"   Duration:  {baseline_m.get('duration_seconds'):.2f}s")
        click.echo(f"   Energy:    {baseline_m.get('energy_kwh'):.6f} kWh")
        
        click.echo(f"\n📊 COMPARISON: {comparison.get('workload_name')}")
        click.echo(f"   Emissions: {comparison_m.get('emissions_gco2e'):.2f} gCO2e")
        click.echo(f"   Duration:  {comparison_m.get('duration_seconds'):.2f}s")
        click.echo(f"   Energy:    {comparison_m.get('energy_kwh'):.6f} kWh")
        
        click.echo(f"\n📈 DIFFERENCE:")
        
        # Emissions
        emoji = "✅" if emissions_diff < 0 else "❌"
        click.echo(f"   {emoji} Emissions: {emissions_diff:+.2f} gCO2e ({emissions_pct:+.1f}%)")
        
        # Duration
        emoji = "✅" if duration_diff < 0 else "⚠️"
        click.echo(f"   {emoji} Duration:  {duration_diff:+.2f}s ({duration_pct:+.1f}%)")
        
        # Energy
        emoji = "✅" if energy_diff < 0 else "❌"
        click.echo(f"   {emoji} Energy:    {energy_diff:+.6f} kWh ({energy_pct:+.1f}%)")
        
        # Summary
        if emissions_diff < 0:
            click.echo(f"\n🎉 IMPROVEMENT: {abs(emissions_diff):.2f} gCO2e saved ({abs(emissions_pct):.1f}% reduction)")
        else:
            click.echo(f"\n⚠️  REGRESSION: {emissions_diff:.2f} gCO2e more emissions ({emissions_pct:.1f}% increase)")
        
        click.echo("="*60 + "\n")
        
    except Exception as e:
        click.echo(f"❌ Error comparing files: {e}", err=True)
        sys.exit(1)


@cli.command()
def test_electricity_maps():
    """Test Electricity Maps API connection."""
    click.echo("\n🌱 Testing Electricity Maps API connection...\n")
    
    carbon_client = CarbonAwareClient()
    if carbon_client.is_available():
        click.echo("✅ Electricity Maps API is available")
        
        # Try to get current data for a region
        click.echo("\nTesting US-East-1 carbon intensity...")
        data = carbon_client.get_current_intensity("us-east-1")
        if data:
            click.echo(f"📊 Current carbon intensity:")
            click.echo(f"   AWS Region: {data.get('aws_region')}")
            click.echo(f"   Zone: {data.get('zone')}")
            click.echo(f"   Carbon Intensity: {data.get('carbon_intensity')} gCO2/kWh")
            click.echo(f"   Renewable %: {data.get('renewable_percentage')}%")
        else:
            click.echo("⚠️  Could not retrieve current intensity data")
    else:
        click.echo("❌ Electricity Maps API is not available or not configured")
        click.echo("   Check your ELECTRICITY_MAPS_API_KEY in .env")


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def audit(filepath):
    """Analyze Python code for carbon/energy anti-patterns (AST static audit)."""
    click.echo(f"\n🔍 CarbonIQ Code Audit: {filepath}")
    click.echo("=" * 60)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    result = audit_code(content)
    if not result.get("valid_syntax"):
        click.echo(f"❌ Syntax Error: {result.get('error')}")
        return
        
    click.echo(f"🌿 Carbon Efficiency Rating: {result.get('carbon_grade')}")
    click.echo(f"📊 Efficiency Score:         {result.get('carbon_score')}/100")
    click.echo(f"⚡ Est. Energy Reduction:    {result.get('potential_energy_reduction_pct')}%")
    click.echo(f"⚠️  Anti-Patterns Detected:   {result.get('total_issues')}\n")
    
    issues = result.get("issues", [])
    if issues:
        click.echo("Detailed Findings:")
        for idx, issue in enumerate(issues, 1):
            sev_icon = "🔴" if issue['severity'] == 'HIGH' else "🟡"
            click.echo(f"  {idx}. {sev_icon} [Line {issue['line']}] {issue['description']}")
            click.echo(f"     💡 Fix: {issue['recommendation']}")
            click.echo(f"     ⚡ Potential Savings: ~{issue['estimated_savings_pct']}%\n")
    else:
        click.echo("🎉 Excellent! No major carbon anti-patterns detected.")
    click.echo("=" * 60 + "\n")


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output path for green optimized code (defaults to stdout or preview)")
@click.option("--in-place", is_flag=True, help="Overwrite existing file with optimized code")
def optimize(filepath, output, in_place):
    """Refactor code to generate sustainable, energy-efficient Python code."""
    click.echo(f"\n🌱 CarbonIQ Sustainable Code Generator: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    result = optimize_code(content)
    opt_code = result.get("optimized_code", content)
    improvements = result.get("improvements_applied", [])
    
    click.echo(f"Original Grade: {result.get('original_grade')}")
    click.echo(f"Est. Energy Reduction: {result.get('estimated_energy_reduction_pct')}%\n")
    
    if improvements:
        click.echo("Applied Sustainable Improvements:")
        for imp in improvements:
            click.echo(f"  ✓ {imp}")
    else:
        click.echo("Code is already well optimized!")
        
    if in_place:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(opt_code)
        click.echo(f"\n✅ Updated {filepath} in-place with green optimizations.")
    elif output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(opt_code)
        click.echo(f"\n✅ Wrote optimized code to {output}")
    else:
        click.echo("\n--- Optimized Code Preview ---")
        click.echo(opt_code)
        click.echo("------------------------------\n")


@cli.group()
def config():
    """Manage CarbonIQ CLI configuration (API keys, backend URL)."""
    pass


@config.command("show")
def config_show():
    """Display current CLI configuration."""
    cfg = get_config()
    key = get_api_key()
    url = get_api_url()
    
    click.echo("\n⚙️  CarbonIQ Configuration")
    click.echo("=" * 50)
    click.echo(f"Backend URL: {url}")
    if key:
        masked_key = f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"
        click.echo(f"API Key:     {masked_key} (active)")
    else:
        click.echo("API Key:     Not set (running as default user)")
    click.echo("=" * 50 + "\n")


@config.command("set-key")
@click.argument("api_key")
def config_set_key(api_key: str):
    """Set the API key to authenticate CLI runs with your user account."""
    api_key = api_key.strip()
    if not api_key.startswith("ciq_live_"):
        click.echo("⚠️  Warning: API keys usually start with 'ciq_live_'")
    save_config_value("api_key", api_key)
    click.echo(f"✅ API Key configured successfully!")
    click.echo("Run 'carboniq whoami' to verify your connection.")


@config.command("set-url")
@click.argument("api_url")
def config_set_url(api_url: str):
    """Set the backend API URL (e.g., https://carboniq-backend-duel.onrender.com/api)."""
    api_url = api_url.strip().rstrip('/')
    save_config_value("api_url", api_url)
    click.echo(f"✅ Backend URL set to: {api_url}")


@cli.command()
def whoami():
    """Check CLI authentication and connection status with CarbonIQ backend."""
    url = get_api_url()
    key = get_api_key()
    
    click.echo(f"\n🔍 Checking CarbonIQ connection...")
    click.echo(f"Target Backend: {url}")
    
    client = BackendClient(url, api_key=key)
    
    if not client.health_check():
        click.echo("❌ Could not connect to backend server. Make sure it is online.")
        return
        
    try:
        import requests
        headers = {"X-API-Key": key} if key else {}
        resp = requests.get(f"{url}/cli/measurements/stats", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            user_id = data.get("user_id")
            click.echo("\n✅ Authenticated successfully!")
            click.echo(f"👤 Connected User ID: {user_id}")
            click.echo(f"📊 Total Measurements Logged: {data.get('total_measurements', 0)}")
            click.echo(f"⚡ Total Energy: {data.get('total_energy_kwh', 0):.6f} kWh")
            click.echo(f"🌱 Total Emissions: {data.get('total_emissions_gco2e', 0):.2f} gCO2e")
        else:
            click.echo(f"⚠️  Backend responded with status {resp.status_code}: {resp.text}")
    except Exception as e:
        click.echo(f"❌ Error communicating with backend: {e}")


def _display_results(results: dict):
    """Display measurement results in a formatted way."""
    source_label = results.get("measurement_source") or ("CodeCarbon hardware telemetry" if CODECARBON_AVAILABLE else "CPU/RAM baseline estimate (65W TDP)")
    click.echo("\n" + "="*60)
    click.echo("MEASUREMENT RESULTS")
    click.echo("="*60)
    click.echo(f"Telemetry Source: {source_label}")
    click.echo(f"Duration:         {results.get('duration_seconds', 'N/A'):.2f} seconds")
    click.echo(f"Energy:          {results.get('energy_kwh', 'N/A'):.6f} kWh")
    click.echo(f"Emissions:       {results.get('emissions_gco2e', 'N/A'):.2f} gCO2e")
    click.echo(f"CPU Energy:      {results.get('cpu_energy', 'N/A'):.6f} kWh")
    click.echo(f"RAM Energy:      {results.get('ram_energy', 'N/A'):.6f} kWh")
    click.echo(f"Country:         {results.get('country_name', 'N/A')}")
    click.echo(f"Carbon Intensity: {results.get('carbon_intensity', 'N/A')} gCO2e/kWh")
    click.echo("="*60 + "\n")




# =============================================================================
# deploy-analysis: Measure + Carbon Aware SDK + Gemini Agent
# =============================================================================

@cli.command(name='deploy-analysis')
@click.argument('command', nargs=-1, required=True)
@click.option('--workload-name', '-n', required=True, help='Name for this workload')
@click.option('--workload-type', '-t', default='general', help='Type of workload (ml-training, batch-job, etc.)')
@click.option('--regions', '-r', multiple=True,
              default=['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-1'],
              help='AWS regions to compare (can specify multiple times)')
@click.option('--deadline', '-d', default=None, help='Deployment deadline (ISO 8601)')
@click.option('--forecast-region', '-f', default=None,
              help='AWS region to get a time-based forecast for (defaults to best region found)')
@click.option('--forecast-window', default=60, type=int,
              help='Workload duration in minutes for forecast window sizing')
@click.option('--send-to-backend/--no-send-to-backend', default=True,
              help='Send results to CarbonIQ backend')
def deploy_analysis(command, workload_name, workload_type, regions, deadline,
                    forecast_region, forecast_window, send_to_backend):
    """
    Measure a workload AND get an AI-powered deployment recommendation.

    Runs THREE steps in sequence:
      1. Measures your workload with CodeCarbon (energy + emissions)
      2. Queries the Carbon Aware SDK for real-time grid intensity across regions
      3. Sends combined data to the CarbonIQ backend agent (Gemini) which
         recommends the optimal REGION and TIME to deploy

    Example:
        carboniq deploy-analysis python train.py \\
            --workload-name "ML Training" --workload-type ml-training \\
            --regions us-east-1 --regions eu-west-1 --regions ap-southeast-1
    """
    click.echo("\n" + "=" * 70)
    click.echo("   CarbonIQ Deploy Analysis")
    click.echo("   CodeCarbon  +  Carbon Aware SDK  +  AI Agent")
    click.echo("=" * 70)
    click.echo(f"Workload : {workload_name} ({workload_type})")
    click.echo(f"Command  : {' '.join(command)}")
    click.echo(f"Regions  : {', '.join(regions)}")
    if deadline:
        click.echo(f"Deadline : {deadline}")
    click.echo()

    # ------------------------------------------------------------------ #
    # STEP 1: CodeCarbon measurement
    # ------------------------------------------------------------------ #
    click.echo("STEP 1/3  CodeCarbon Measurement")
    click.echo("-" * 40)

    measurement_obj = CodeCarbonMeasurement(
        workload_name=workload_name,
        workload_type=workload_type,
        output_dir=OUTPUT_DIR
    )

    try:
        codecarbon_results = measurement_obj.measure_command(list(command))
    except Exception as e:
        click.echo(f"ERROR during measurement: {e}", err=True)
        import sys; sys.exit(1)

    if not codecarbon_results:
        click.echo("ERROR: Measurement returned no results.", err=True)
        import sys; sys.exit(1)

    _display_results(codecarbon_results)

    # ------------------------------------------------------------------ #
    # STEP 2: Carbon Aware SDK query
    # ------------------------------------------------------------------ #
    click.echo("\nSTEP 2/3  Carbon Aware SDK — Region Comparison")
    click.echo("-" * 40)

    sdk_client = CarbonAwareSDKClient()
    sdk_available = sdk_client.is_available()

    if sdk_available:
        click.echo(f"Carbon Aware SDK reachable at: {sdk_client.base_url}")
    else:
        click.echo(
            f"Carbon Aware SDK NOT reachable at {sdk_client.base_url}\n"
            "  To run it locally:\n"
            "    docker run -p 5073:80 ghcr.io/green-software-foundation/carbon-aware-sdk:latest\n"
            "  Set CARBON_AWARE_SDK_URL env var to point to a hosted instance.\n"
            "  Continuing without real-time grid data..."
        )

    sdk_data = sdk_client.compare_regions(list(regions))

    # Also try to get a time-based forecast
    forecast_data = None
    if sdk_available:
        target_forecast_region = forecast_region
        if not target_forecast_region and sdk_data.get("best_region"):
            target_forecast_region = sdk_data["best_region"]["aws_region"]

        if target_forecast_region:
            click.echo(f"\nFetching time forecast for {target_forecast_region}...")
            forecast_data = sdk_client.get_forecast(
                aws_region=target_forecast_region,
                window_duration_minutes=forecast_window
            )

    # Display SDK results
    if sdk_data.get("available") and sdk_data.get("regions"):
        click.echo("\n  Region Carbon Intensity Ranking (lowest = greenest):")
        for i, r in enumerate(sdk_data["regions"], 1):
            tag = "  <-- BEST" if i == 1 else ("  <-- WORST" if i == len(sdk_data["regions"]) else "")
            click.echo(
                f"    {i:2d}. {r['aws_region']:<18} {r['carbon_intensity']:>7.1f} gCO2eq/kWh{tag}"
            )
        click.echo()

        if forecast_data and forecast_data.get("optimal_window_start"):
            click.echo(
                f"  Optimal time window ({forecast_data['aws_region']}): "
                f"{forecast_data['optimal_window_start']}  "
                f"({forecast_data['optimal_carbon_intensity']:.1f} gCO2eq/kWh)"
            )
    else:
        click.echo("  No real-time region data available from Carbon Aware SDK.")

    # ------------------------------------------------------------------ #
    # STEP 3: Backend agent analysis (Gemini)
    # ------------------------------------------------------------------ #
    click.echo("\nSTEP 3/3  AI Agent Analysis (Gemini)")
    click.echo("-" * 40)
    click.echo("Sending combined data to CarbonIQ backend for analysis...")

    # Build the payload
    sdk_regions_payload = []
    if sdk_data.get("regions"):
        for r in sdk_data["regions"]:
            sdk_regions_payload.append({
                "aws_region": r["aws_region"],
                "sdk_location": r.get("sdk_location"),
                "carbon_intensity": r["carbon_intensity"],
                "time": r.get("time"),
                "source": r.get("source"),
            })

    forecast_payload = None
    if forecast_data:
        forecast_payload = {
            "aws_region": forecast_data.get("aws_region"),
            "optimal_window_start": forecast_data.get("optimal_window_start"),
            "optimal_carbon_intensity": forecast_data.get("optimal_carbon_intensity"),
            "window_duration_minutes": forecast_data.get("window_duration_minutes"),
            "forecast_generated_at": forecast_data.get("forecast_generated_at"),
            "source": forecast_data.get("source"),
        }

    best_region = None
    if sdk_data.get("best_region"):
        br = sdk_data["best_region"]
        best_region = {
            "aws_region": br["aws_region"],
            "sdk_location": br.get("sdk_location"),
            "carbon_intensity": br["carbon_intensity"],
            "time": br.get("time"),
            "source": br.get("source"),
        }

    worst_region = None
    if sdk_data.get("worst_region"):
        wr = sdk_data["worst_region"]
        worst_region = {
            "aws_region": wr["aws_region"],
            "sdk_location": wr.get("sdk_location"),
            "carbon_intensity": wr["carbon_intensity"],
            "time": wr.get("time"),
            "source": wr.get("source"),
        }

    analysis_payload = {
        "codecarbon": {
            "workload_name": codecarbon_results.get("workload_name", workload_name),
            "workload_type": codecarbon_results.get("workload_type", workload_type),
            "duration_seconds": codecarbon_results.get("duration_seconds", 0),
            "emissions_gco2e": codecarbon_results.get("emissions_gco2e", 0),
            "energy_kwh": codecarbon_results.get("energy_kwh", 0),
            "carbon_intensity": codecarbon_results.get("carbon_intensity"),
            "country_name": codecarbon_results.get("country_name"),
            "cpu_energy": codecarbon_results.get("cpu_energy"),
            "ram_energy": codecarbon_results.get("ram_energy"),
            "gpu_energy": codecarbon_results.get("gpu_energy"),
        },
        "carbon_aware_sdk": {
            "available": sdk_data.get("available", False),
            "queried_at": sdk_data.get("queried_at"),
            "regions": sdk_regions_payload,
            "best_region": best_region,
            "worst_region": worst_region,
            "average_intensity": sdk_data.get("average_intensity"),
            "total_regions_compared": sdk_data.get("total_regions_compared"),
            "forecast": forecast_payload,
            "error": sdk_data.get("error"),
            "source": sdk_data.get("source"),
        },
        "deadline": deadline,
        "preferred_regions": list(regions) if regions else None,
        "measured_at": datetime.utcnow().isoformat(),
    }

    try:
        import requests as _requests
        resp = _requests.post(
            f"{API_URL}/cli/deployment-analysis",
            json=analysis_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if resp.status_code == 200:
            analysis = resp.json()
            _display_deployment_analysis(analysis)
        else:
            click.echo(f"Backend returned HTTP {resp.status_code}: {resp.text[:300]}", err=True)
            click.echo("\nShowing local summary instead...")
            _display_local_summary(codecarbon_results, sdk_data, forecast_data)

    except Exception as e:
        click.echo(f"Could not reach backend agent: {e}", err=True)
        click.echo("\nShowing local summary instead...")
        _display_local_summary(codecarbon_results, sdk_data, forecast_data)

    # Also send raw measurement to backend
    if send_to_backend:
        try:
            backend_client = BackendClient(API_URL)
            payload = {
                "workload_name": workload_name,
                "workload_type": workload_type,
                "measurement": codecarbon_results,
                "carbon_aware_data": sdk_data if sdk_available else None,
                "deadline": deadline,
                "measured_at": datetime.utcnow().isoformat(),
            }
            backend_client.send_measurement(payload)
        except Exception:
            pass  # Storage is secondary


@cli.command(name='carbon-intensity')
@click.option('--regions', '-r', multiple=True,
              default=['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
                       'ap-southeast-1', 'ap-southeast-2'],
              help='AWS regions to compare (repeatable)')
@click.option('--forecast', '-f', is_flag=True, default=False,
              help='Also show time-based forecast for the best region')
@click.option('--forecast-window', default=60, type=int,
              help='Workload duration in minutes for forecast sizing')
def carbon_intensity_check(regions, forecast, forecast_window):
    """
    Check real-time carbon intensity via Carbon Aware SDK across regions.

    Shows which AWS region is greenest RIGHT NOW and optionally the optimal
    deployment time window using forecasted grid data.

    Example:
        carboniq carbon-intensity --regions us-east-1 --regions eu-west-1 --forecast
    """
    click.echo("\n" + "=" * 60)
    click.echo("   Carbon Aware SDK  —  Real-time Grid Intensity")
    click.echo("=" * 60)

    sdk_client = CarbonAwareSDKClient()

    if not sdk_client.is_available():
        click.echo(
            f"Carbon Aware SDK not reachable at {sdk_client.base_url}\n"
            "  Start it with:\n"
            "    docker run -p 5073:80 ghcr.io/green-software-foundation/carbon-aware-sdk:latest\n"
            "  Or set CARBON_AWARE_SDK_URL to your hosted instance."
        )
        return

    click.echo(f"SDK endpoint : {sdk_client.base_url}")
    sdk_data = sdk_client.compare_regions(list(regions))

    if not sdk_data.get("available") or not sdk_data.get("regions"):
        click.echo("No data returned from Carbon Aware SDK.")
        return

    click.echo(f"\nQueried {sdk_data['total_regions_compared']} regions at {sdk_data['queried_at'][:19]}Z")
    click.echo(f"Average intensity : {sdk_data['average_intensity']:.1f} gCO2eq/kWh\n")
    click.echo(f"  {'Rank':<5} {'AWS Region':<20} {'Intensity':>13}  Notes")
    click.echo("  " + "-" * 55)

    for i, r in enumerate(sdk_data["regions"], 1):
        note = ""
        if i == 1:
            note = "BEST  🟢"
        elif i == len(sdk_data["regions"]):
            note = "WORST 🔴"
        elif r["carbon_intensity"] < sdk_data["average_intensity"]:
            note = "below avg 🟡"
        click.echo(f"  {i:<5} {r['aws_region']:<20} {r['carbon_intensity']:>8.1f} g/kWh  {note}")

    # Savings summary
    if len(sdk_data["regions"]) > 1:
        best = sdk_data["regions"][0]
        worst = sdk_data["regions"][-1]
        savings = (worst["carbon_intensity"] - best["carbon_intensity"]) / worst["carbon_intensity"] * 100
        click.echo(f"\nDeploying to {best['aws_region']} instead of {worst['aws_region']}")
        click.echo(f"saves approximately {savings:.1f}% carbon emissions.")

    # Optional forecast
    if forecast and sdk_data.get("best_region"):
        best_region = sdk_data["best_region"]["aws_region"]
        click.echo(f"\nFetching time forecast for {best_region} ({forecast_window}-min window)...")
        fc = sdk_client.get_forecast(best_region, window_duration_minutes=forecast_window)
        if fc and fc.get("optimal_window_start"):
            click.echo(f"  Optimal window starts : {fc['optimal_window_start']}")
            click.echo(f"  Forecast intensity    : {fc['optimal_carbon_intensity']:.1f} gCO2eq/kWh")
        else:
            click.echo("  No forecast data available for this region.")

    click.echo("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Display helpers for deploy-analysis
# ---------------------------------------------------------------------------

def _display_deployment_analysis(analysis: dict):
    """Pretty-print the backend agent's deployment analysis."""
    click.echo("\n" + "=" * 70)
    click.echo("   AI DEPLOYMENT RECOMMENDATION")
    click.echo("=" * 70)

    click.echo(f"\nSUMMARY:\n  {analysis.get('summary', 'N/A')}")

    primary = analysis.get("primary_recommendation", {})
    if primary:
        click.echo("\n" + "-" * 70)
        click.echo("PRIMARY RECOMMENDATION")
        click.echo("-" * 70)
        click.echo(f"  Deploy to     : {primary.get('optimal_region', 'N/A')}")
        if primary.get("optimal_time_window"):
            click.echo(f"  When          : {primary['optimal_time_window']}")
        if primary.get("estimated_carbon_intensity"):
            click.echo(f"  Intensity     : {primary['estimated_carbon_intensity']:.1f} gCO2eq/kWh")
        if primary.get("estimated_emissions_gco2e"):
            click.echo(f"  Est. emissions: {primary['estimated_emissions_gco2e']:.4f} gCO2e")
        if primary.get("carbon_savings_vs_current_pct") is not None:
            savings = primary["carbon_savings_vs_current_pct"]
            emoji = "✅" if savings > 0 else "⚠️ "
            click.echo(f"  Carbon savings: {emoji} {savings:+.1f}% vs. current location")
        click.echo(f"\n  Rationale:\n    {primary.get('rationale', 'N/A')}")

    alternatives = analysis.get("alternative_recommendations", [])
    if alternatives:
        click.echo("\n" + "-" * 70)
        click.echo("ALTERNATIVE OPTIONS")
        click.echo("-" * 70)
        for i, alt in enumerate(alternatives, 1):
            click.echo(f"\n  {i}. {alt.get('optimal_region', 'N/A')}")
            if alt.get("estimated_carbon_intensity"):
                click.echo(f"     Intensity : {alt['estimated_carbon_intensity']:.1f} gCO2eq/kWh")
            if alt.get("carbon_savings_vs_current_pct") is not None:
                click.echo(f"     Savings   : {alt['carbon_savings_vs_current_pct']:+.1f}%")
            if alt.get("optimal_time_window"):
                click.echo(f"     When      : {alt['optimal_time_window']}")
            click.echo(f"     {alt.get('rationale', '')}")

    insights = analysis.get("key_insights", [])
    if insights:
        click.echo("\n" + "-" * 70)
        click.echo("KEY INSIGHTS")
        click.echo("-" * 70)
        for ins in insights:
            click.echo(f"  * {ins}")

    if analysis.get("carbon_reduction_potential_pct") is not None:
        pct = analysis["carbon_reduction_potential_pct"]
        click.echo(f"\n  Max carbon reduction potential: {pct:.1f}%")

    click.echo(f"\n  Analysis by : {', '.join(analysis.get('data_sources', []))}")
    click.echo(f"  Timestamp   : {analysis.get('analysis_timestamp', 'N/A')}")
    click.echo("=" * 70 + "\n")


def _display_local_summary(codecarbon_results: dict, sdk_data: dict, forecast_data):
    """Fallback local summary when backend is not reachable."""
    click.echo("\n" + "=" * 60)
    click.echo("LOCAL DEPLOYMENT SUMMARY (backend unavailable)")
    click.echo("=" * 60)
    click.echo(f"Measured emissions : {codecarbon_results.get('emissions_gco2e', 'N/A'):.4f} gCO2e")
    click.echo(f"Energy consumed    : {codecarbon_results.get('energy_kwh', 'N/A'):.6f} kWh")
    click.echo(f"Duration           : {codecarbon_results.get('duration_seconds', 'N/A'):.2f}s")

    if sdk_data.get("available") and sdk_data.get("best_region"):
        best = sdk_data["best_region"]
        click.echo(f"\nGreenest region now: {best['aws_region']} ({best['carbon_intensity']:.1f} gCO2eq/kWh)")
        cur_i = codecarbon_results.get("carbon_intensity")
        if cur_i and cur_i > 0:
            savings = (cur_i - best["carbon_intensity"]) / cur_i * 100
            click.echo(f"Potential savings  : {savings:.1f}% by deploying to {best['aws_region']}")
    else:
        click.echo("\nCarbon Aware SDK data not available.")
        click.echo("  Run: docker run -p 5073:80 ghcr.io/green-software-foundation/carbon-aware-sdk:latest")

    if forecast_data and forecast_data.get("optimal_window_start"):
        click.echo(f"\nBest time window   : {forecast_data['optimal_window_start']}")
        click.echo(f"Forecast intensity : {forecast_data['optimal_carbon_intensity']:.1f} gCO2eq/kWh")

    click.echo("=" * 60 + "\n")



if __name__ == '__main__':
    cli()
