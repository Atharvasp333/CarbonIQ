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

from codecarbon_wrapper import CodeCarbonMeasurement
from backend_client import BackendClient
from carbon_aware import CarbonAwareClient

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("CARBONIQ_API_URL", "http://localhost:8000/api")
OUTPUT_DIR = Path(os.getenv("CODECARBON_OUTPUT_DIR", "./measurements"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@click.group()
@click.version_option(version="0.1.0")
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
def history(limit):
    """Show recent measurement history."""
    click.echo(f"\n📊 Recent Measurements (last {limit}):\n")
    
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


def _display_results(results: dict):
    """Display measurement results in a formatted way."""
    click.echo("\n" + "="*60)
    click.echo("MEASUREMENT RESULTS")
    click.echo("="*60)
    click.echo(f"Duration:        {results.get('duration_seconds', 'N/A'):.2f} seconds")
    click.echo(f"Energy:          {results.get('energy_kwh', 'N/A'):.6f} kWh")
    click.echo(f"Emissions:       {results.get('emissions_gco2e', 'N/A'):.2f} gCO2e")
    click.echo(f"CPU Energy:      {results.get('cpu_energy', 'N/A'):.6f} kWh")
    click.echo(f"RAM Energy:      {results.get('ram_energy', 'N/A'):.6f} kWh")
    click.echo(f"Country:         {results.get('country_name', 'N/A')}")
    click.echo(f"Carbon Intensity: {results.get('carbon_intensity', 'N/A')} gCO2e/kWh")
    click.echo("="*60 + "\n")


if __name__ == '__main__':
    cli()
