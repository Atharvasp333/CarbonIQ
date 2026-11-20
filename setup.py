# CarbonIQ SDK Setup Configuration
from setuptools import setup, find_packages

setup(
    name="carboniq-sdk",
    version="0.2.0",
    packages=find_packages(include=["carboniq*"]),
    entry_points={
        "console_scripts": [
            "carboniq=carboniq.cli.carboniq_cli:cli",
        ],
    },
)
