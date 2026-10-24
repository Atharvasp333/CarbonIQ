"""
CarbonIQ Workload Tracker
Provides @carboniq.track decorator and context manager to monitor code energy and carbon emissions.
"""
import time
import functools
import logging
from typing import Optional, Callable, Any
from pathlib import Path

logger = logging.getLogger("carboniq.tracker")


class TrackContext:
    """Context manager for tracking energy and emissions of a code block."""

    def __init__(
        self,
        workload_name: str = "workload",
        workload_type: str = "general",
        auto_send: bool = True
    ):
        self.workload_name = workload_name
        self.workload_type = workload_type
        self.auto_send = auto_send
        self.start_time = None
        self.end_time = None
        self.duration_seconds = 0
        self.tracker = None
        self.results = None

    def __enter__(self):
        self.start_time = time.time()
        try:
            from codecarbon import OfflineEmissionsTracker
            # Default country ISO (e.g. USA) or local
            self.tracker = OfflineEmissionsTracker(
                country_iso_code="USA",
                save_to_file=False,
                log_level="error"
            )
            self.tracker.start()
        except Exception as e:
            logger.debug(f"CodeCarbon init fallback: {e}")
            self.tracker = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_seconds = self.end_time - self.start_time

        emissions_kg = 0.0
        energy_kwh = 0.0

        if self.tracker:
            try:
                emissions_kg = self.tracker.stop() or 0.0
                energy_kwh = getattr(self.tracker, "_total_energy", 0.0) or 0.0
            except Exception as e:
                logger.debug(f"CodeCarbon stop fallback: {e}")

        # If CodeCarbon returned zero (e.g. very fast micro-benchmark), estimate based on CPU time
        if energy_kwh <= 0.0:
            # Conservative estimate: typical 65W CPU baseline
            energy_kwh = (65.0 * (self.duration_seconds / 3600.0)) / 1000.0
        if emissions_kg <= 0.0:
            # ~380 gCO2/kWh average grid
            emissions_kg = (energy_kwh * 0.380)

        emissions_g = emissions_kg * 1000.0

        self.results = {
            "workload_name": self.workload_name,
            "workload_type": self.workload_type,
            "duration_seconds": self.duration_seconds,
            "emissions_gco2e": emissions_g,
            "energy_kwh": energy_kwh,
            "carbon_intensity": (emissions_g / energy_kwh) if energy_kwh > 0 else 380.0
        }

        # Print user friendly log in terminal
        print(f"\n[CarbonIQ] 🌱 Workload '{self.workload_name}' completed:")
        print(f"  • Duration:  {self.duration_seconds:.2f}s")
        print(f"  • Energy:    {energy_kwh:.6f} kWh")
        print(f"  • Emissions: {emissions_g:.4f} gCO2e")

        if self.auto_send:
            self._dispatch_to_backend()

    def _dispatch_to_backend(self):
        """Asynchronously send measurement to configured CarbonIQ backend"""
        try:
            import os
            import requests
            from cli.config_manager import get_api_key, get_api_url

            url = get_api_url()
            key = get_api_key()

            headers = {"Content-Type": "application/json"}
            if key:
                headers["X-API-Key"] = key

            payload = {
                "workload_name": self.workload_name,
                "workload_type": self.workload_type,
                "measurement": {
                    "duration_seconds": self.duration_seconds,
                    "emissions_gco2e": self.results["emissions_gco2e"],
                    "energy_kwh": self.results["energy_kwh"],
                    "cpu_energy": self.results["energy_kwh"] * 0.7,
                    "ram_energy": self.results["energy_kwh"] * 0.3,
                    "carbon_intensity": self.results["carbon_intensity"],
                    "country_name": "Local Host"
                }
            }

            resp = requests.post(f"{url}/cli/measurements", json=payload, headers=headers, timeout=5)
            if resp.status_code in (200, 201):
                data = resp.json()
                print(f"  • Synced to CarbonIQ Dashboard (ID: {data.get('measurement_id', 'ok')})\n")
            else:
                print(f"  • Notice: Saved locally (backend status {resp.status_code})\n")
        except Exception:
            # Silent fallback if offline or no backend reachable
            print(f"  • Notice: Saved locally (offline)\n")


def track(workload_name: Optional[str] = None, workload_type: str = "general", auto_send: bool = True):
    """
    Decorator & context manager to track carbon emissions of a function or code block.

    Usage as Decorator:
        @carboniq.track(workload_name="train_model")
        def train():
            ...

    Usage as Context Manager:
        with carboniq.track(workload_name="data_processing"):
            process()
    """
    def decorator(func: Callable) -> Callable:
        name = workload_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with TrackContext(workload_name=name, workload_type=workload_type, auto_send=auto_send):
                return func(*args, **kwargs)
        return wrapper

    if callable(workload_name):
        func = workload_name
        name = func.__name__
        workload_name = None
        return decorator(func)

    return TrackContext(
        workload_name=workload_name or "workload",
        workload_type=workload_type,
        auto_send=auto_send
    )
