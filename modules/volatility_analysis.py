"""Historical volatility outlook and scenario-analysis helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd


def classify_volatility_level(value: float | None) -> str:
    """Classify annualized historical volatility using transparent bands."""
    if value is None:
        return "Unknown"
    if value < 0.20:
        return "Low"
    if value <= 0.40:
        return "Moderate"
    return "High"


def build_volatility_outlook(history: pd.DataFrame) -> dict[str, Any]:
    """Calculate historical volatility, range, trend, and position metrics."""
    prices = history["Close"].dropna()
    daily_returns = prices.pct_change().dropna()

    annualized_volatility = None
    if len(daily_returns) > 1:
        annualized_volatility = float(daily_returns.std() * (252**0.5))

    maximum_drawdown = None
    if not prices.empty:
        drawdowns = prices / prices.cummax() - 1
        maximum_drawdown = float(drawdowns.min())

    period_high = float(prices.max()) if not prices.empty else None
    period_low = float(prices.min()) if not prices.empty else None
    latest_price = float(prices.iloc[-1]) if not prices.empty else None
    starting_price = float(prices.iloc[0]) if not prices.empty else None

    period_return = None
    if starting_price not in (None, 0) and latest_price is not None:
        period_return = latest_price / starting_price - 1

    current_price_position = None
    if (
        latest_price is not None
        and period_high is not None
        and period_low is not None
        and period_high != period_low
    ):
        current_price_position = (latest_price - period_low) / (period_high - period_low)

    recent_trend = "Unknown"
    recent_return = None
    if len(prices) >= 22 and prices.iloc[-22] != 0:
        recent_return = float(prices.iloc[-1] / prices.iloc[-22] - 1)
        if recent_return > 0.02:
            recent_trend = "Upward"
        elif recent_return < -0.02:
            recent_trend = "Downward"
        else:
            recent_trend = "Sideways"

    return {
        "annualized_volatility": annualized_volatility,
        "maximum_drawdown": maximum_drawdown,
        "period_high": period_high,
        "period_low": period_low,
        "latest_price": latest_price,
        "starting_price": starting_price,
        "period_return": period_return,
        "current_price_position": current_price_position,
        "recent_return": recent_return,
        "recent_trend": recent_trend,
        "volatility_level": classify_volatility_level(annualized_volatility),
    }
