"""Risk indicators and the transparent FinSight financial health score."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd


def analyze_risk(
    history: pd.DataFrame, beta: float | None = None
) -> dict[str, float | None]:
    """Calculate price volatility, drawdown, return, and beta."""
    prices = history["Close"].dropna()
    daily_returns = prices.pct_change().dropna()

    annualized_volatility = None
    if len(daily_returns) > 1:
        annualized_volatility = float(daily_returns.std() * (252**0.5))

    maximum_drawdown = None
    if not prices.empty:
        running_peak = prices.cummax()
        drawdowns = prices / running_peak - 1
        maximum_drawdown = float(drawdowns.min())

    period_return = None
    starting_price = None
    latest_price = None
    if len(prices) >= 2 and prices.iloc[0] != 0:
        starting_price = float(prices.iloc[0])
        latest_price = float(prices.iloc[-1])
        period_return = float(prices.iloc[-1] / prices.iloc[0] - 1)

    try:
        parsed_beta = float(beta) if beta is not None else None
    except (TypeError, ValueError):
        parsed_beta = None

    return {
        "annualized_volatility": annualized_volatility,
        "maximum_drawdown": maximum_drawdown,
        "period_return": period_return,
        "starting_price": starting_price,
        "latest_price": latest_price,
        "beta": parsed_beta,
    }


def classify_risk_level(health_score: int) -> dict[str, str]:
    """Map the health score to the simple risk bands used in the interface."""
    if health_score >= 75:
        return {"label": "Low Risk", "css_class": "low-risk"}
    if health_score >= 50:
        return {"label": "Moderate Risk", "css_class": "moderate-risk"}
    return {"label": "High Risk", "css_class": "high-risk"}


def build_risk_breakdown(
    ratios: Mapping[str, float | None],
    risk: Mapping[str, float | None],
    profile: Mapping[str, Any],
) -> list[dict[str, str]]:
    """Explain six major risk categories using only available information."""
    margin = ratios.get("net_profit_margin")
    if margin is None:
        profitability = ("Unknown", "Profitability data is unavailable.")
    elif margin < 0:
        profitability = ("High", "The latest annual net profit margin is negative.")
    elif margin < 0.08:
        profitability = ("Moderate", "The latest margin is positive but relatively thin.")
    else:
        profitability = ("Low", "The latest annual net profit margin is positive.")

    leverage = ratios.get("debt_to_assets")
    if leverage is None:
        leverage_risk = ("Unknown", "Debt-to-assets data is unavailable.")
    elif leverage > 0.60:
        leverage_risk = ("High", "Debt represents more than 60% of reported assets.")
    elif leverage >= 0.30:
        leverage_risk = ("Moderate", "Debt is meaningful relative to reported assets.")
    else:
        leverage_risk = ("Low", "Debt is below 30% of reported assets.")

    current_ratio = ratios.get("current_ratio")
    if current_ratio is None:
        liquidity = ("Unknown", "Current assets or current liabilities are unavailable.")
    elif current_ratio < 1:
        liquidity = ("High", "Current liabilities exceed reported current assets.")
    elif current_ratio < 1.5:
        liquidity = ("Moderate", "Short-term liquidity appears adequate but not strong.")
    else:
        liquidity = ("Low", "Reported current assets comfortably cover current liabilities.")

    volatility = risk.get("annualized_volatility")
    if volatility is None:
        market = ("Unknown", "There is not enough price data to estimate volatility.")
    elif volatility > 0.40:
        market = ("High", "Annualized historical volatility is above 40%.")
    elif volatility > 0.25:
        market = ("Moderate", "Annualized historical volatility is between 25% and 40%.")
    else:
        market = ("Low", "Annualized historical volatility is below 25%.")

    sector = str(profile.get("sector") or "the company's sector")
    sector_lower = sector.lower()
    if "financial" in sector_lower:
        sector_text = "Financial businesses can be sensitive to interest rates, credit quality, and regulation."
    elif "technology" in sector_lower:
        sector_text = "Technology businesses face rapid innovation cycles and intense competition."
    elif "energy" in sector_lower or "materials" in sector_lower:
        sector_text = "Results may be sensitive to commodity prices and economic cycles."
    elif "consumer cyclical" in sector_lower:
        sector_text = "Demand can weaken when consumers reduce discretionary spending."
    else:
        sector_text = f"Performance can be affected by competition and changing conditions in {sector}."

    currency = profile.get("currency")
    country = profile.get("country")
    if currency and currency != "USD":
        country_text = (
            f"The shares trade in {currency}; investors using another home currency "
            f"may experience exchange-rate effects. Country exposure is {country or 'unavailable'}."
        )
        country_level = "Moderate"
    else:
        country_text = (
            f"Country exposure is {country or 'unavailable'}. Political, regulatory, "
            "and economic conditions may still affect results."
        )
        country_level = "Context"

    items = [
        ("Profitability risk", *profitability),
        ("Leverage risk", *leverage_risk),
        ("Liquidity risk", *liquidity),
        ("Market volatility risk", *market),
        ("Sector & business model risk", "Context", sector_text),
        ("Currency & country risk", country_level, country_text),
    ]
    return [
        {"name": name, "level": level, "explanation": explanation}
        for name, level, explanation in items
    ]


def calculate_financial_health_score(
    ratios: Mapping[str, float | None],
    financials: Mapping[str, float | None],
    history: pd.DataFrame,
) -> dict[str, int | list[str]]:
    """Create a transparent 0-100 score from five simple signals.

    This is an educational screening score, not a valuation model.
    """
    score = 50
    explanations: list[str] = []

    margin = ratios.get("net_profit_margin")
    if margin is None:
        explanations.append("Profitability data unavailable: no score change.")
    elif margin >= 0.15:
        score += 15
        explanations.append("Strong net profit margin: +15.")
    elif margin > 0:
        score += 8
        explanations.append("Positive net profit margin: +8.")
    else:
        score -= 15
        explanations.append("Negative net profit margin: -15.")

    leverage = ratios.get("debt_to_assets")
    if leverage is None:
        explanations.append("Leverage data unavailable: no score change.")
    elif leverage < 0.30:
        score += 12
        explanations.append("Low debt relative to assets: +12.")
    elif leverage <= 0.60:
        score += 4
        explanations.append("Moderate debt relative to assets: +4.")
    else:
        score -= 12
        explanations.append("High debt relative to assets: -12.")

    growth = ratios.get("revenue_growth")
    if growth is None:
        explanations.append("Revenue growth data unavailable: no score change.")
    elif growth >= 0.10:
        score += 12
        explanations.append("Revenue growth of at least 10%: +12.")
    elif growth >= 0:
        score += 5
        explanations.append("Revenue is stable or growing: +5.")
    else:
        score -= 10
        explanations.append("Revenue declined year over year: -10.")

    operating_cash_flow = financials.get("operating_cash_flow")
    if operating_cash_flow is None:
        explanations.append("Operating cash-flow data unavailable: no score change.")
    elif operating_cash_flow > 0:
        score += 8
        explanations.append("Positive operating cash flow: +8.")
    else:
        score -= 8
        explanations.append("Negative operating cash flow: -8.")

    prices = history["Close"].dropna()
    if len(prices) >= 2 and prices.iloc[0] != 0:
        price_return = prices.iloc[-1] / prices.iloc[0] - 1
        if price_return > 0:
            score += 3
            explanations.append("Positive stock return over the selected period: +3.")
        else:
            score -= 3
            explanations.append("Negative stock return over the selected period: -3.")

    return {"score": int(max(0, min(100, score))), "explanations": explanations}
