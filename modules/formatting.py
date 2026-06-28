"""Shared formatting helpers for visible financial values."""

from __future__ import annotations

import math
from typing import Any


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(math.isnan(float(value)))
    except (TypeError, ValueError):
        return False


def unavailable(language: str = "en") -> str:
    """Return the localized missing-value label."""
    return "暂无数据" if language == "zh" else "N/A"


def format_large_number(
    value: float | None,
    currency: str | None = None,
    language: str = "en",
) -> str:
    """Format large values with compact but specific suffixes."""
    if _is_missing(value):
        return unavailable(language)
    number = float(value)
    prefix = f"{currency} " if currency else ""
    absolute_value = abs(number)
    if absolute_value >= 1_000_000_000_000:
        return f"{prefix}{number / 1_000_000_000_000:,.2f}T"
    if absolute_value >= 1_000_000_000:
        return f"{prefix}{number / 1_000_000_000:,.2f}B"
    if absolute_value >= 1_000_000:
        return f"{prefix}{number / 1_000_000:,.2f}M"
    if absolute_value >= 1_000:
        return f"{prefix}{number / 1_000:,.2f}K"
    return f"{prefix}{number:,.2f}"


def format_currency(
    value: float | None,
    currency: str | None = None,
    language: str = "en",
) -> str:
    """Format a monetary value with a compact suffix."""
    return format_large_number(value, currency, language)


def format_price(
    value: float | None,
    currency: str | None = None,
    language: str = "en",
) -> str:
    """Format a stock price without compacting it."""
    if _is_missing(value):
        return unavailable(language)
    prefix = f"{currency} " if currency else ""
    return f"{prefix}{float(value):,.2f}"


def format_percent(
    value: float | None,
    language: str = "en",
    already_percentage: bool | None = None,
) -> str:
    """Format decimal or already-percentage values without double multiplying."""
    if _is_missing(value):
        return unavailable(language)
    number = float(value)
    if already_percentage is None:
        percentage = number if abs(number) > 3 else number * 100
    else:
        percentage = number if already_percentage else number * 100
    return f"{percentage:,.2f}%"


def format_ratio(value: float | None, language: str = "en") -> str:
    """Format a non-percentage financial ratio."""
    if _is_missing(value):
        return unavailable(language)
    return f"{float(value):,.2f}"
