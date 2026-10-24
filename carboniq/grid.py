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
        from cli.carbon_aware import CarbonAwareClient
        client = CarbonAwareClient()
        if client.is_available():
            data = client.get_current_intensity(region)
            if data:
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
        "aws_region": region,
        "carbon_intensity": intensity,
        "source": "baseline_estimate"
    }


def defer_until_green(
    region: str = "us-east-1",
    max_intensity: float = 300.0,
    check_interval: int = 30,
    max_wait_seconds: int = 300
):
    """
    Decorator to pause function execution until local grid carbon intensity drops below max_intensity.

    Args:
        region: Cloud region (e.g. us-east-1, us-west-2, eu-west-1)
        max_intensity: Carbon intensity threshold in gCO2/kWh
        check_interval: Polling frequency in seconds
        max_wait_seconds: Maximum time to wait before proceeding anyway
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = 0
            while elapsed < max_wait_seconds:
                grid_info = get_grid_intensity(region)
                current_ci = grid_info.get("carbon_intensity", 400.0)

                if current_ci <= max_intensity:
                    print(f"[CarbonIQ] 🟢 Grid intensity is green ({current_ci:.1f} gCO2/kWh <= threshold {max_intensity}). Executing '{func.__name__}'...")
                    break
                else:
                    print(f"[CarbonIQ] 🟡 Grid intensity is high ({current_ci:.1f} gCO2/kWh > threshold {max_intensity}). Deferring '{func.__name__}'...")
                    time.sleep(check_interval)
                    elapsed += check_interval

            return func(*args, **kwargs)
        return wrapper
    return decorator
