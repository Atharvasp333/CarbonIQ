"""
Numeric Utilities for Intelligence Engine

Handles conversion between PostgreSQL Decimal and Python float/int types
to prevent TypeError in arithmetic operations.

RULES:
- PostgreSQL NUMERIC columns return as Decimal
- Electricity Maps API returns float/int
- All intelligence calculations use float for consistency
- None values remain None
- Invalid values raise clear errors
"""
from decimal import Decimal
from typing import Union, Optional


def to_float(value: Union[Decimal, float, int, None]) -> Optional[float]:
    """
    Convert numeric value to float for calculations.
    
    Args:
        value: Decimal, float, int, or None
    
    Returns:
        float or None
    
    Raises:
        ValueError: If value cannot be converted to float
    """
    if value is None:
        return None
    
    if isinstance(value, (float, int)):
        return float(value)
    
    if isinstance(value, Decimal):
        return float(value)
    
    # Try to convert string or other types
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot convert {type(value).__name__} value '{value}' to float: {e}")


def safe_divide(numerator: Union[Decimal, float, int, None],
                denominator: Union[Decimal, float, int, None],
                default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling None and zero division.
    
    Args:
        numerator: The dividend
        denominator: The divisor
        default: Value to return if division is not possible
    
    Returns:
        Result of division or default value
    """
    if numerator is None or denominator is None:
        return default
    
    num = to_float(numerator)
    denom = to_float(denominator)
    
    if denom == 0:
        return default
    
    return num / denom


def safe_multiply(a: Union[Decimal, float, int, None],
                  b: Union[Decimal, float, int, None],
                  default: float = 0.0) -> float:
    """
    Safely multiply two numbers, handling None.
    
    Args:
        a: First operand
        b: Second operand
        default: Value to return if multiplication is not possible
    
    Returns:
        Result of multiplication or default value
    """
    if a is None or b is None:
        return default
    
    return to_float(a) * to_float(b)


def calculate_percentage_change(current: Union[Decimal, float, int, None],
                                target: Union[Decimal, float, int, None]) -> Optional[float]:
    """
    Calculate percentage change from current to target.
    
    Args:
        current: Current value
        target: Target value
    
    Returns:
        Percentage change or None if calculation not possible
    """
    if current is None or target is None:
        return None
    
    curr = to_float(current)
    targ = to_float(target)
    
    if curr == 0:
        return None
    
    return ((curr - targ) / curr) * 100


# Configuration constants
REGION_INTENSITY_THRESHOLD = 0.7  # 30% cleaner for region migration
TIME_INTENSITY_THRESHOLD = 1.15  # 15% higher for time shifting
MINIMUM_REDUCTION_KG = 5.0  # Minimum kg CO2 reduction to recommend
MINIMUM_REDUCTION_PCT = 10.0  # Minimum percentage reduction to recommend
