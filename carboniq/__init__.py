"""
CarbonIQ Python Library & Sustainable Code Generation SDK
=========================================================
Empowering developers to measure energy, run carbon-aware workloads,
and generate green, low-carbon software.

Usage:
    import carboniq

    # Track energy & emissions
    @carboniq.track(workload_name="train_model")
    def my_pipeline():
        ...

    # Run only during clean grid hours
    @carboniq.defer_until_green(region="us-east-1", max_intensity=250)
    def heavy_batch():
        ...

    # Audit & optimize code
    audit = carboniq.audit_code("my_script.py")
    green_code = carboniq.optimize_code("my_script.py")
"""
__version__ = "0.2.0"

from .tracker import track, TrackContext
from .grid import get_grid_intensity, defer_until_green
from .optimizer import audit_code, optimize_code

__all__ = [
    "track",
    "TrackContext",
    "get_grid_intensity",
    "defer_until_green",
    "audit_code",
    "optimize_code",
    "__version__"
]
