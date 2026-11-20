"""
CarbonIQ CLI Package (Compatibility Shim)
"""
import sys
from pathlib import Path
repo_root = str(Path(__file__).parent.parent.resolve())
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from carboniq.cli import *
from carboniq.cli import __version__, __author__, cli

__all__ = ["cli", "__version__", "__author__"]
