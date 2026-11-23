"""
Tests for Carbon-Aware Integration, Regional Mappings, Fallbacks, and Calculation Formulas.
"""
import pytest
from carboniq.cli.carbon_aware import CarbonAwareClient, FALLBACK_REGIONAL_BASELINES
from carboniq.cli.carbon_aware_sdk import CarbonAwareSDKClient


def test_regional_grid_baselines_completeness():
    assert len(FALLBACK_REGIONAL_BASELINES) >= 4
    assert "us-east-1" in FALLBACK_REGIONAL_BASELINES
    assert "eu-west-1" in FALLBACK_REGIONAL_BASELINES
    # eu-west-1 (Ireland) has lower baseline carbon intensity than us-east-1
    assert FALLBACK_REGIONAL_BASELINES["eu-west-1"]["carbon_intensity"] < FALLBACK_REGIONAL_BASELINES["us-east-1"]["carbon_intensity"]


def test_carbon_aware_client_fallback_behavior():
    client = CarbonAwareClient()
    # Explicitly verify the fallback baseline mechanism
    client.enabled = False
    data = client.get_current_intensity("us-east-1")
    assert data["carbon_intensity"] == FALLBACK_REGIONAL_BASELINES["us-east-1"]["carbon_intensity"]
    assert "fallback" in data["source"] or "baseline" in data["source"]


def test_carbon_aware_sdk_unavailable_handling():
    sdk = CarbonAwareSDKClient()
    # When local carbon aware sdk service is not running
    assert sdk.is_available() is False
    res = sdk.get_current_emissions("us-east-1")
    assert res is None or res == {}


def test_optimal_windows_calculation():
    client = CarbonAwareClient()
    res = client.get_optimal_windows(
        duration_minutes=60,
        regions=["us-east-1", "eu-west-1"]
    )
    assert res is not None
    assert "optimal_region" in res
    assert "optimal_intensity" in res
    assert "potential_carbon_savings_pct" in res
