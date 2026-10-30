"""
src/utils/formatting.py
Display formatters that render missing values as "N/A" instead of inventing a number or crashing.
"""
from typing import Any

import pandas as pd

NA_TEXT = "N/A"


def is_missing(value: Any) -> bool:
    """True for None, NaN, NaT and pd.NA."""
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def fmt_money(value: Any, decimals: int = 2) -> str:
    if is_missing(value):
        return NA_TEXT
    return f"${float(value):,.{decimals}f}"


def fmt_num(value: Any, decimals: int = 0) -> str:
    if is_missing(value):
        return NA_TEXT
    return f"{float(value):,.{decimals}f}"


def fmt_pct(value: Any, decimals: int = 1) -> str:
    if is_missing(value):
        return NA_TEXT
    return f"{float(value):.{decimals}f}%"


def fmt_signed(value: Any, decimals: int = 2) -> str:
    if is_missing(value):
        return NA_TEXT
    return f"{float(value):+.{decimals}f}"


def fmt_rating(value: Any, decimals: int = 2) -> str:
    if is_missing(value):
        return NA_TEXT
    return f"{float(value):.{decimals}f}★"
