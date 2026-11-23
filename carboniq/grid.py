"""
CarbonIQ Grid & Carbon-Aware Execution
Provides real-time grid carbon intensity queries and execution deferral until green energy windows.
"""
import time
import functools
import logging
from typing import Optional, Callable, Any, Dict

logger = logging.getLogger("carboniq.grid")


def get_grid_intensity(region: str = "us-east-1") -> Dict[str, Any]:
    """
    Query real-time carbon intensity (gCO2/kWh) for a given cloud or electric region.
    """
    try:
        try:
            from carboniq.cli.carbon_aware import CarbonAwareClient
        except ImportError:
            try:
                from .cli.carbon_aware import CarbonAwareClient
            except (ImportError, ValueError):
                from cli.carbon_aware import CarbonAwareClient
        client = CarbonAwareClient()
        if client.is_available():
            data = client.get_current_intensity(region)
            if data:
                data.setdefault("region", region)
                data.setdefault("unit", "gCO2eq/kWh")
                return data
    except Exception as e:
        logger.debug(f"Grid query error: {e}")

    # Fallback typical baselines
    regional_baselines = {
        "us-east-1": 395.0,
        "us-west-2": 240.0,
        "eu-west-1": 210.0,
        "eu-north-1": 45.0,
    }
    intensity = regional_baselines.get(region, 350.0)
    return {
        "region": region,
        "aws_region": region,
        "zone": region,
        "carbon_intensity": intensity,
        "unit": "gCO2eq/kWh",
        "source": "baseline_estimate"
    }


def defer_until_green(
    region: str = "us-east-1",
    max_intensity: float = 300.0,
    check_interval: float = 30.0,
    max_wait_seconds: float = 300.0,
    poll_interval_sec: Optional[float] = None,
    timeout_sec: Optional[float] = None
):
    """
    Decorator to pause function execution until local grid carbon intensity drops below max_intensity.

    Args:
        region: Cloud region (e.g. us-east-1, us-west-2, eu-west-1)
        max_intensity: Carbon intensity threshold in gCO2/kWh
        check_interval: Polling frequency in seconds (alias: poll_interval_sec)
        max_wait_seconds: Maximum time to wait before proceeding/timing out (alias: timeout_sec)
    """
    if poll_interval_sec is not None:
        check_interval = poll_interval_sec
    if timeout_sec is not None:
        max_wait_seconds = timeout_sec

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = 0.0
            while elapsed < max_wait_seconds:
                grid_info = get_grid_intensity(region)
                current_ci = grid_info.get("carbon_intensity", 400.0)

                if current_ci <= max_intensity:
                    print(f"[CarbonIQ] 🟢 Grid intensity is green ({current_ci:.1f} gCO2/kWh <= threshold {max_intensity}). Executing '{func.__name__}'...")
                    return func(*args, **kwargs)
                else:
                    print(f"[CarbonIQ] 🟡 Grid intensity is high ({current_ci:.1f} gCO2/kWh > threshold {max_intensity}). Deferring '{func.__name__}'...")
                    time.sleep(check_interval)
                    elapsed += check_interval

            raise TimeoutError(
                f"Execution of '{func.__name__}' timed out after waiting {elapsed:.1f}s for grid intensity to drop below {max_intensity} gCO2/kWh."
            )
        return wrapper
    return decorator
