# pyrefly: ignore[missing-import]
from setuptools import setup, find_packages

setup(
    name="carboniq",
    version="0.2.0",
    author="CarbonIQ Team",
    description="Carbon-aware computing SDK and sustainable code generator",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "codecarbon>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "carboniq=cli.carboniq_cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
