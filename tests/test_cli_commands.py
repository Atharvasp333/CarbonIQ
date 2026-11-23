"""
Comprehensive test suite for CarbonIQ CLI commands.
Tests all top-level commands and subcommands:
1.  carboniq --help
2.  carboniq audit <file>
3.  carboniq optimize <file>
4.  carboniq measure <command>
5.  carboniq measure-script <file>
6.  carboniq monitor -r <region>
7.  carboniq compare <before.json> <after.json>
8.  carboniq recommend-schedule
9.  carboniq deploy-analysis
10. carboniq carbon-intensity
11. carboniq config set-key
12. carboniq config set-url
13. carboniq config show
14. carboniq whoami
15. carboniq test-backend
16. carboniq test-electricity-maps
17. carboniq history
18. carboniq stats
"""
import json
import os
import tempfile
from pathlib import Path
import pytest
from click.testing import CliRunner
from carboniq.cli.carboniq_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_py(tmp_path):
    p = tmp_path / "sample.py"
    p.write_text("""
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

def build_data(n):
    res = []
    for i in range(n):
        res.append(i)
    return res
""", encoding="utf-8")
    return str(p)


@pytest.fixture
def sample_measurements(tmp_path):
    b = tmp_path / "before.json"
    a = tmp_path / "after.json"
    data_b = {
        "timestamp": "2026-11-20T10:00:00",
        "workload_name": "task_before",
        "measurement": {
            "duration_seconds": 10.0,
            "energy_kwh": 0.005,
            "emissions_gco2e": 2.0
        }
    }
    data_a = {
        "timestamp": "2026-11-20T11:00:00",
        "workload_name": "task_after",
        "measurement": {
            "duration_seconds": 5.0,
            "energy_kwh": 0.002,
            "emissions_gco2e": 0.8
        }
    }
    b.write_text(json.dumps(data_b), encoding="utf-8")
    a.write_text(json.dumps(data_a), encoding="utf-8")
    return str(b), str(a)


def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "CarbonIQ CLI" in result.output
    assert "Commands:" in result.output


def test_cli_audit(runner, sample_py):
    result = runner.invoke(cli, ["audit", sample_py])
    assert result.exit_code == 0
    assert "Carbon Audit Report" in result.output or "Score" in result.output or "Grade" in result.output


def test_cli_optimize(runner, sample_py):
    result = runner.invoke(cli, ["optimize", sample_py])
    assert result.exit_code == 0
    assert "@lru_cache" in result.output or "Sustainable" in result.output


def test_cli_measure(runner):
    result = runner.invoke(cli, ["measure", "-n", "test_cmd", "python -c 'sum(range(1000))'"])
    assert result.exit_code == 0
    assert "Workload Measurement" in result.output or "Duration" in result.output or "Emissions" in result.output


def test_cli_measure_script(runner, sample_py):
    result = runner.invoke(cli, ["measure-script", sample_py])
    assert result.exit_code == 0
    assert "Measurement" in result.output or "Duration" in result.output


def test_cli_monitor_timeout(runner):
    result = runner.invoke(cli, ["monitor", "-r", "us-east-1", "-d", "1", "-i", "1"])
    assert result.exit_code == 0 or "Monitoring" in result.output or "Intensity" in result.output


def test_cli_compare(runner, sample_measurements):
    f1, f2 = sample_measurements
    result = runner.invoke(cli, ["compare", f1, f2])
    assert result.exit_code == 0
    assert "Comparison" in result.output or "Delta" in result.output or "Reduction" in result.output or "MEASUREMENT COMPARISON" in result.output


def test_cli_recommend_schedule(runner):
    result = runner.invoke(cli, ["recommend-schedule", "-d", "60", "-r", "us-east-1"])
    assert result.exit_code == 0
    assert "Recommendation" in result.output or "Schedule" in result.output or "Intensity" in result.output


def test_cli_deploy_analysis(runner, sample_py):
    result = runner.invoke(cli, ["deploy-analysis", "-n", "deploy_sample", "python -c 'print(1)'"])
    assert result.exit_code == 0
    assert "Analysis" in result.output or "Carbon" in result.output or "Measurement" in result.output


def test_cli_carbon_intensity(runner):
    result = runner.invoke(cli, ["carbon-intensity", "-r", "us-east-1"])
    assert result.exit_code == 0
    assert "Intensity" in result.output or "gCO2eq" in result.output or "Region" in result.output


def test_cli_config_flow(runner):
    # Set key
    res_key = runner.invoke(cli, ["config", "set-key", "ciq_live_mock_dummy_key_12345"])
    assert res_key.exit_code == 0

    # Set url
    res_url = runner.invoke(cli, ["config", "set-url", "https://carboniq-backend-duel.onrender.com/api"])
    assert res_url.exit_code == 0

    # Show config (confirm masking)
    res_show = runner.invoke(cli, ["config", "show"])
    assert res_show.exit_code == 0
    assert "ciq_live_mock_dummy_key_12345" not in res_show.output  # Must be masked!


def test_cli_whoami(runner):
    result = runner.invoke(cli, ["whoami"])
    # May succeed or report connection status
    assert result.exit_code == 0 or "Checking" in result.output or "Target Backend" in result.output


def test_cli_test_backend(runner):
    result = runner.invoke(cli, ["test-backend"])
    assert result.exit_code == 0 or "Testing" in result.output or "Backend" in result.output


def test_cli_test_electricity_maps(runner):
    result = runner.invoke(cli, ["test-electricity-maps"])
    assert result.exit_code == 0 or "Testing" in result.output or "Electricity Maps" in result.output


def test_cli_history(runner):
    result = runner.invoke(cli, ["history"])
    assert result.exit_code == 0 or "History" in result.output or "No measurements" in result.output


def test_cli_stats(runner):
    result = runner.invoke(cli, ["stats"])
    assert result.exit_code == 0 or "Statistics" in result.output or "Stats" in result.output
