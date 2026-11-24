"""
CarbonIQ CLI Entry Point (Compatibility Shim forwarding to canonical carboniq.cli)
"""
import sys
from pathlib import Path
repo_root = str(Path(__file__).parent.parent.resolve())
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from carboniq.cli.carboniq_cli import *
from carboniq.cli.carboniq_cli import cli

if __name__ == "__main__":
    cli()
