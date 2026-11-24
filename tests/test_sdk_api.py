"""
Comprehensive test suite for CarbonIQ Python SDK APIs.
Tests:
- carboniq.audit_code()
- carboniq.optimize_code()
- carboniq.track()
- carboniq.defer_until_green()
- carboniq.get_grid_intensity()
"""
import pytest
import carboniq
from carboniq import audit_code, optimize_code, track, defer_until_green, get_grid_intensity


class TestAuditCodeAPI:
    def test_audit_code_clean(self):
        code = "def add(a, b):\n    return a + b\n"
        result = audit_code(code)
        assert result["valid_syntax"] is True
        assert result["carbon_score"] == 100
        assert "A" in result["carbon_grade"]
        assert len(result["issues"]) == 0

    def test_audit_code_anti_patterns(self):
        code = """
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

def build_data(n):
    res = []
    for i in range(n):
        res.append(i * 2)
    return res
"""
        result = audit_code(code)
        assert result["valid_syntax"] is True
        assert result["carbon_score"] < 100
        types = [i["type"] for i in result["issues"]]
        assert "UNCACHED_RECURSION" in types
        assert "UNVECTORIZED_ACCUMULATION" in types

    def test_audit_code_syntax_error(self):
        code = "def broken_code(:"
        result = audit_code(code)
        assert result["valid_syntax"] is False
        assert "error" in result
        assert result["carbon_grade"] == "N/A"


class TestOptimizeCodeAPI:
    def test_optimize_recursion(self):
        code = """
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
"""
        result = optimize_code(code)
        assert "optimized_code" in result
        assert "@lru_cache" in result["optimized_code"]
        assert "from functools import lru_cache" in result["optimized_code"]

    def test_optimize_loop_append(self):
        code = """
def squares(n):
    out = []
    for i in range(n):
        out.append(i * i)
    return out
"""
        result = optimize_code(code)
        assert "out = [i * i for i in range(n)]" in result["optimized_code"]

    def test_optimize_safe_list_preservation(self):
        code = """
def process():
    data = [x * 2 for x in range(50000)]
    return data[5] + len(data)
"""
        result = optimize_code(code)
        # data should not be turned into generator since it's indexed and sized
        assert "[x * 2 for x in range(50000)]" in result["optimized_code"]


class TestGridIntensityAPI:
    def test_get_grid_intensity_known_region(self):
        data = get_grid_intensity("us-east-1")
        assert "region" in data or "aws_region" in data
        assert "carbon_intensity" in data
        assert isinstance(data["carbon_intensity"], (int, float))
        assert data["carbon_intensity"] > 0
        assert "unit" in data

    def test_get_grid_intensity_fallback_region(self):
        data = get_grid_intensity("unknown-custom-region-1")
        assert "carbon_intensity" in data
        assert isinstance(data["carbon_intensity"], (int, float))


class TestDeferUntilGreenAPI:
    def test_defer_decorator_under_threshold(self):
        executed = []

        @defer_until_green(region="us-east-1", max_intensity=9999, check_interval=0.05, max_wait_seconds=0.2)
        def my_task():
            executed.append(True)
            return "done"

        res = my_task()
        assert res == "done"
        assert executed == [True]

    def test_defer_decorator_over_threshold_timeout(self):
        @defer_until_green(region="us-east-1", max_intensity=1, check_interval=0.05, max_wait_seconds=0.1)
        def heavy_task():
            return "ran"

        with pytest.raises(TimeoutError) as exc_info:
            heavy_task()
        assert "timed out" in str(exc_info.value).lower()


class TestTrackAPI:
    def test_track_context_manager(self):
        with track("test_block") as tracker:
            s = sum(i * i for i in range(5000))
        assert tracker.duration_seconds >= 0
        assert tracker.energy_kwh >= 0
        assert tracker.emissions_kg_co2 >= 0

    def test_track_decorator(self):
        @track("test_func")
        def work():
            return 42

        res = work()
        assert res == 42
