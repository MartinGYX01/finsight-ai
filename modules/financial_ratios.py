"""Simple financial ratio calculations used by FinSight AI."""

from __future__ import annotations

from typing import Mapping


def _safe_divide(numerator: float | None, denominator: float | None) -> float | None:
    """Divide two values without crashing on missing data or zero."""
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def calculate_financial_ratios(
    financials: Mapping[str, float | None],
) -> dict[str, float | None]:
    """Calculate beginner-friendly ratios from annual statement data."""
    revenue = financials.get("revenue")
    previous_revenue = financials.get("previous_revenue")

    net_profit_margin = _safe_divide(financials.get("net_income"), revenue)
    debt_to_assets = _safe_divide(
        financials.get("total_debt"), financials.get("total_assets")
    )
    return_on_equity = _safe_divide(
        financials.get("net_income"), financials.get("stockholders_equity")
    )
    current_ratio = _safe_divide(
        financials.get("current_assets"), financials.get("current_liabilities")
    )

    revenue_growth = None
    if revenue is not None and previous_revenue not in (None, 0):
        revenue_growth = (revenue - previous_revenue) / abs(previous_revenue)

    return {
        "net_profit_margin": net_profit_margin,
        "debt_to_assets": debt_to_assets,
        "return_on_equity": return_on_equity,
        "current_ratio": current_ratio,
        "revenue_growth": revenue_growth,
    }
