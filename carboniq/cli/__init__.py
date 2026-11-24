"""
CarbonIQ CLI Package
====================
Autonomous carbon-aware workload measurement, AST code auditing,
green refactoring, and grid telemetry tool.
"""

__version__ = "0.2.0"
__author__ = "CarbonIQ Team"

from .carboniq_cli import cli

__all__ = ["cli", "__version__", "__author__"]
