"""
CodeCarbon wrapper for CarbonIQ
Handles workload measurement using CodeCarbon library.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from codecarbon import EmissionsTracker, OfflineEmissionsTracker
from dotenv import load_dotenv

load_dotenv()


class CodeCarbonMeasurement:
    """Wrapper for CodeCarbon emission tracking."""
    
    def __init__(
        self,
        workload_name: str,
        workload_type: str = "general",
        output_dir: Path = Path("./measurements"),
        tracking_mode: Optional[str] = None
    ):
        """
        Initialize CodeCarbon measurement wrapper.
        
        Args:
            workload_name: Name of the workload being measured
            workload_type: Type of workload (e.g., ml-training, data-processing)
            output_dir: Directory to save measurement outputs
            tracking_mode: CodeCarbon tracking mode (machine, process)
        """
        self.workload_name = workload_name
        self.workload_type = workload_type
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get tracking mode from env or use default
        self.tracking_mode = tracking_mode or os.getenv("CODECARBON_TRACKING_MODE", "machine")
        
        # CodeCarbon configuration
        self.project_name = f"carboniq_{workload_name.replace(' ', '_')}"
        self.tracker = None
    
    def measure_command(self, command: List[str]) -> Optional[Dict]:
        """
        Measure emissions for an external command.
        
        Args:
            command: Command to execute as a list (e.g., ['python', 'script.py'])
        
        Returns:
            Dictionary containing measurement results, or None if failed
        """
        print(f"[CodeCarbon] Starting measurement for: {' '.join(command)}")
        print(f"[CodeCarbon] Tracking mode: {self.tracking_mode}")
        
        # Initialize tracker
        try:
            self.tracker = EmissionsTracker(
                project_name=self.project_name,
                measure_power_secs=1,  # Measure every second for more accuracy
                save_to_file=True,
                output_dir=str(self.output_dir),
                log_level='warning'  # Reduce noise
            )
        except Exception as e:
            print(f"[CodeCarbon] Error initializing tracker: {e}")
            return None
        
        # Start tracking
        self.tracker.start()
        start_time = time.time()
        exit_code = 0
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            exit_code = result.returncode
            
            # Print command output
            if result.stdout:
                print("\n[Command Output]:")
                print(result.stdout)
            
            if result.stderr:
                print("\n[Command Errors]:")
                print(result.stderr)
            
            if exit_code != 0:
                print(f"\n[Warning] Command exited with code {exit_code}")
        
        except Exception as e:
            print(f"[Error] Failed to execute command: {e}")
            exit_code = 1
        
        finally:
            # Stop tracking
            end_time = time.time()
            duration = end_time - start_time
            
            try:
                emissions_data = self.tracker.stop()
                print(f"[CodeCarbon] Measurement completed in {duration:.2f}s")
            except Exception as e:
                print(f"[CodeCarbon] Error stopping tracker: {e}")
                emissions_data = None
        
        if emissions_data is None:
            return None
        
        # Parse and return results
        return self._parse_results(emissions_data, duration, exit_code)
    
    def measure_function(self, func, *args, **kwargs) -> Tuple[Any, Optional[Dict]]:
        """
        Measure emissions for a Python function.
        
        Args:
            func: Function to measure
            *args, **kwargs: Arguments to pass to the function
        
        Returns:
            Tuple of (function_result, measurement_dict)
        """
        print(f"[CodeCarbon] Starting measurement for function: {func.__name__}")
        
        # Initialize tracker
        try:
            self.tracker = EmissionsTracker(
                project_name=self.project_name,
                measure_power_secs=1,
                save_to_file=True,
                output_dir=str(self.output_dir),
                log_level='warning'
            )
        except Exception as e:
            print(f"[CodeCarbon] Error initializing tracker: {e}")
            return None, None
        
        # Start tracking
        self.tracker.start()
        start_time = time.time()
        func_result = None
        error = None
        
        try:
            # Execute the function
            func_result = func(*args, **kwargs)
        except Exception as e:
            error = e
            print(f"[Error] Function raised exception: {e}")
        finally:
            # Stop tracking
            end_time = time.time()
            duration = end_time - start_time
            
            try:
                emissions_data = self.tracker.stop()
                print(f"[CodeCarbon] Measurement completed in {duration:.2f}s")
            except Exception as e:
                print(f"[CodeCarbon] Error stopping tracker: {e}")
                emissions_data = None
        
        if emissions_data is None:
            if error:
                raise error
            return func_result, None
        
        measurement = self._parse_results(emissions_data, duration, 0 if not error else 1)
        
        if error:
            raise error
        
        return func_result, measurement
    
    def _parse_results(self, emissions_data: float, duration: float, exit_code: int) -> Dict:
        """
        Parse CodeCarbon results into a standardized format.
        
        Args:
            emissions_data: Emissions in kgCO2e from CodeCarbon
            duration: Execution duration in seconds
            exit_code: Command exit code
        
        Returns:
            Dictionary with standardized measurement results
        """
        # CodeCarbon returns emissions in kgCO2e, convert to gCO2e
        emissions_gco2e = emissions_data * 1000 if emissions_data else 0
        
        # Try to get more detailed data from the last emissions.csv file
        detailed_data = self._read_latest_emissions_csv()
        
        results = {
            "workload_name": self.workload_name,
            "workload_type": self.workload_type,
            "duration_seconds": round(duration, 2),
            "emissions_gco2e": round(emissions_gco2e, 4),
            "emissions_kgco2e": round(emissions_data, 6) if emissions_data else 0,
            "exit_code": exit_code,
            "tracking_mode": self.tracking_mode,
            "project_name": self.project_name,
        }
        
        # Add detailed data if available
        if detailed_data:
            results.update({
                "energy_kwh": detailed_data.get("energy_consumed", 0),
                "cpu_energy": detailed_data.get("cpu_energy", 0),
                "ram_energy": detailed_data.get("ram_energy", 0),
                "gpu_energy": detailed_data.get("gpu_energy", 0),
                "country_name": detailed_data.get("country_name", "Unknown"),
                "country_iso_code": detailed_data.get("country_iso_code", ""),
                "region": detailed_data.get("region", ""),
                "carbon_intensity": detailed_data.get("carbon_intensity", 0),
                "cpu_power": detailed_data.get("cpu_power", 0),
                "ram_power": detailed_data.get("ram_power", 0),
                "gpu_power": detailed_data.get("gpu_power", 0),
            })
        
        return results
    
    def _read_latest_emissions_csv(self) -> Optional[Dict]:
        """
        Read the most recent emissions.csv file created by CodeCarbon.
        
        Returns:
            Dictionary with detailed emissions data, or None if not found
        """
        try:
            emissions_file = self.output_dir / "emissions.csv"
            
            if not emissions_file.exists():
                return None
            
            # Read the last line of the CSV (most recent measurement)
            import csv
            with open(emissions_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    return None
                
                last_row = rows[-1]
                
                # Convert to our format
                return {
                    "timestamp": last_row.get("timestamp", ""),
                    "project_name": last_row.get("project_name", ""),
                    "duration": float(last_row.get("duration", 0)),
                    "emissions": float(last_row.get("emissions", 0)),
                    "emissions_rate": float(last_row.get("emissions_rate", 0)),
                    "cpu_power": float(last_row.get("cpu_power", 0)),
                    "gpu_power": float(last_row.get("gpu_power", 0)),
                    "ram_power": float(last_row.get("ram_power", 0)),
                    "cpu_energy": float(last_row.get("cpu_energy", 0)),
                    "gpu_energy": float(last_row.get("gpu_energy", 0)),
                    "ram_energy": float(last_row.get("ram_energy", 0)),
                    "energy_consumed": float(last_row.get("energy_consumed", 0)),
                    "country_name": last_row.get("country_name", "Unknown"),
                    "country_iso_code": last_row.get("country_iso_code", ""),
                    "region": last_row.get("region", ""),
                    "cloud_provider": last_row.get("cloud_provider", ""),
                    "cloud_region": last_row.get("cloud_region", ""),
                    "carbon_intensity": float(last_row.get("carbon_intensity", 0)),
                }
        
        except Exception as e:
            print(f"[Warning] Could not read emissions CSV: {e}")
            return None
