"""Detailed template-based research report generation for FinSight AI."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Mapping

import pandas as pd


DISCLAIMER = (
    "This report is generated for educational purposes only and does not "
    "constitute financial advice."
)


def _percent(value: float | None) -> str:
    """Format an optional decimal value for report sentences."""
    return f"{value:.1%}" if value is not None else "unavailable"


def _number(value: float | None) -> str:
    """Format an optional ratio that is not a percentage."""
    return f"{value:.2f}" if value is not None else "unavailable"


def _money(value: float | None, currency: str | None = None) -> str:
    """Format an optional monetary value with its known currency code."""
    if value is None:
        return "unavailable"
    prefix = f"{currency} " if currency else ""
    absolute_value = abs(value)
    if absolute_value >= 1_000_000_000_000:
        return f"{prefix}{value / 1_000_000_000_000:,.2f} trillion"
    if absolute_value >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:,.1f} billion"
    if absolute_value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:,.1f} million"
    return f"{prefix}{value:,.0f}"


def _price(value: float | None, currency: str | None = None) -> str:
    """Format a stock price without rounding away useful decimals."""
    if value is None:
        return "unavailable"
    prefix = f"{currency} " if currency else ""
    return f"{prefix}{value:,.2f}"


def _business_style(profile: Mapping[str, Any]) -> tuple[str, str]:
    """Describe a business model using broad, non-speculative sector traits."""
    sector = str(profile.get("sector") or "").lower()
    industry = str(profile.get("industry") or "").lower()
    if "financial" in sector or "bank" in industry or "insurance" in industry:
        return (
            "financial-services-driven",
            "Revenue is commonly influenced by lending, fees, investment activity, "
            "insurance, or the spread between funding costs and asset yields. "
            "Results can be sensitive to interest rates, credit quality, and regulation.",
        )
    if "technology" in sector:
        return (
            "technology-driven",
            "Revenue is likely tied to technology products, software, services, or "
            "digital ecosystems described in the company profile. Innovation, customer "
            "retention, and competition are important operating drivers.",
        )
    if "consumer defensive" in sector or "utilities" in sector or "healthcare" in sector:
        return (
            "relatively defensive",
            "Demand may be steadier than in highly discretionary industries, although "
            "pricing, regulation, input costs, and execution can still affect results.",
        )
    if "consumer cyclical" in sector or "industrials" in sector or "materials" in sector:
        return (
            "cyclical",
            "Revenue can move with consumer demand, capital spending, commodity costs, "
            "or the broader economic cycle.",
        )
    if "energy" in sector:
        return (
            "cyclical and asset-heavy",
            "Revenue and cash flow may be influenced by commodity prices, production "
            "levels, capital investment, and regulation.",
        )
    return (
        "sector-dependent",
        "The free company profile identifies the main activities, but a detailed "
        "revenue-segment breakdown is not available from the current data source.",
    )


def _performance_label(margin: float | None, growth: float | None, cash_flow: float | None) -> str:
    """Create a simple strength label from three reported financial signals."""
    signals: list[bool] = []
    if margin is not None:
        signals.append(margin > 0)
    if growth is not None:
        signals.append(growth > 0)
    if cash_flow is not None:
        signals.append(cash_flow > 0)
    if not signals:
        return "unclear because key data is unavailable"
    positives = sum(signals)
    if positives == len(signals):
        return "strong across the available indicators"
    if positives >= max(1, len(signals) // 2):
        return "moderate, with a mixture of positive and cautious signals"
    return "weak across several available indicators"


def _valuation_view(profile: Mapping[str, Any]) -> str:
    """Explain valuation only when Yahoo supplies a P/E ratio."""
    trailing_pe = profile.get("trailing_pe")
    forward_pe = profile.get("forward_pe")
    if trailing_pe is None and forward_pe is None:
        return (
            "A dependable price-to-earnings valuation measure is unavailable from "
            "the current free data source, so this report does not make a valuation claim."
        )
    values = []
    if trailing_pe is not None:
        values.append(f"trailing P/E is {trailing_pe:.1f}")
    if forward_pe is not None:
        values.append(f"forward P/E is {forward_pe:.1f}")
    joined = " and ".join(values)
    reference_pe = forward_pe if forward_pe is not None else trailing_pe
    if reference_pe is not None and reference_pe > 35:
        interpretation = (
            "This represents a premium earnings multiple and raises the importance "
            "of future growth and execution."
        )
    elif reference_pe is not None and reference_pe > 0:
        interpretation = (
            "The multiple should be compared with the company's history, peers, "
            "growth rate, and interest-rate environment before drawing conclusions."
        )
    else:
        interpretation = (
            "A non-positive P/E can reflect negative or unusual earnings and is not "
            "a reliable standalone valuation signal."
        )
    return f"Yahoo Finance reports that {joined}. {interpretation}"


def _bullish_factors(
    ratios: Mapping[str, float | None],
    financials: Mapping[str, float | None],
    risk: Mapping[str, float | None],
) -> list[str]:
    """Build evidence-based positive observations."""
    factors: list[str] = []
    margin = ratios.get("net_profit_margin")
    growth = ratios.get("revenue_growth")
    leverage = ratios.get("debt_to_assets")
    if margin is not None and margin > 0:
        factors.append(f"Positive annual profitability, with a {_percent(margin)} net margin.")
    if growth is not None and growth > 0:
        factors.append(f"Latest annual revenue grew {_percent(growth)} year over year.")
    if financials.get("operating_cash_flow") is not None and financials["operating_cash_flow"] > 0:
        factors.append("Latest reported operating cash flow is positive.")
    if leverage is not None and leverage < 0.30:
        factors.append("Reported debt is below 30% of total assets.")
    if risk.get("period_return") is not None and risk["period_return"] > 0:
        factors.append("The share price delivered a positive return over the selected period.")
    while len(factors) < 3:
        factors.append(
            "Additional positive confirmation requires data not available from the current free source."
        )
    return factors[:5]


def _bearish_factors(
    profile: Mapping[str, Any],
    ratios: Mapping[str, float | None],
    financials: Mapping[str, float | None],
    risk: Mapping[str, float | None],
) -> list[str]:
    """Build evidence-based caution points."""
    factors: list[str] = []
    margin = ratios.get("net_profit_margin")
    growth = ratios.get("revenue_growth")
    leverage = ratios.get("debt_to_assets")
    volatility = risk.get("annualized_volatility")
    if margin is not None and margin <= 0:
        factors.append("Latest annual net income is not positive relative to revenue.")
    if growth is not None and growth < 0:
        factors.append(f"Latest annual revenue declined {_percent(abs(growth))} year over year.")
    if financials.get("operating_cash_flow") is not None and financials["operating_cash_flow"] <= 0:
        factors.append("Latest reported operating cash flow is negative.")
    if leverage is not None and leverage > 0.60:
        factors.append("Reported debt exceeds 60% of total assets.")
    if volatility is not None and volatility > 0.30:
        factors.append(f"Historical volatility is elevated at {_percent(volatility)} annualized.")
    valuation = _valuation_view(profile)
    if "premium earnings multiple" in valuation:
        factors.append("The available P/E ratio indicates a premium valuation that may require strong execution.")
    if len(factors) < 3:
        factors.append("Competition, regulation, and changing market conditions remain general business risks.")
    if len(factors) < 3:
        factors.append("Free-source data is incomplete, limiting confidence in the risk assessment.")
    return factors[:5]


def build_investor_watchlist(
    profile: Mapping[str, Any],
    ratios: Mapping[str, float | None],
) -> list[str]:
    """Return five practical monitoring items tailored where possible."""
    sector = str(profile.get("sector") or "")
    watchlist = [
        "Track annual and quarterly revenue growth for evidence of accelerating or slowing demand.",
        "Monitor net profit margin for pricing power, cost pressure, and operating efficiency.",
        "Compare operating cash flow with net income to judge the quality of reported earnings.",
        "Watch debt-to-assets and short-term liquidity for changes in balance-sheet resilience.",
    ]
    if "Financial" in sector:
        watchlist.append(
            "Monitor interest rates, credit quality, loan growth, and regulatory capital conditions."
        )
    elif profile.get("currency") and profile.get("currency") != "USD":
        watchlist.append(
            f"Monitor {profile.get('currency')} exchange-rate exposure and economic conditions in "
            f"{profile.get('country') or 'the home market'}."
        )
    else:
        watchlist.append(
            "Monitor competitive pressure, product demand, regulation, and management guidance."
        )
    return watchlist


def generate_research_report(
    ticker: str,
    profile: Mapping[str, Any],
    history: pd.DataFrame,
    financials: Mapping[str, float | None],
    ratios: Mapping[str, float | None],
    risk: Mapping[str, float | None],
    health: Mapping[str, Any],
    risk_level: str,
    risk_breakdown: list[Mapping[str, str]],
    news: list[Mapping[str, str | None]],
    news_sentiment: Mapping[str, Any],
) -> OrderedDict[str, str]:
    """Create a detailed, data-grounded report when OpenAI is unavailable."""
    company_name = str(profile.get("company_name") or ticker)
    trading_currency = profile.get("currency")
    financial_currency = profile.get("financial_currency") or trading_currency
    margin = ratios.get("net_profit_margin")
    growth = ratios.get("revenue_growth")
    cash_flow = financials.get("operating_cash_flow")
    performance_strength = _performance_label(margin, growth, cash_flow)
    business_style, business_explanation = _business_style(profile)
    period_return = risk.get("period_return")
    starting_price = risk.get("starting_price")
    latest_price = risk.get("latest_price")

    if period_return is None:
        price_view = "Price performance is unavailable for the selected period."
    elif period_return > 0.10:
        price_view = "The selected period shows clear positive price growth."
    elif period_return < -0.10:
        price_view = "The selected period shows notable price weakness."
    else:
        price_view = "The selected period shows relatively limited directional movement."

    executive_sentences = [
        f"{company_name} is a {profile.get('industry', 'N/A')} company in the "
        f"{profile.get('sector', 'N/A')} sector.",
        f"Its business model appears {business_style} based on the available company profile.",
        f"Financial performance is {performance_strength}.",
        f"The stock returned {_percent(period_return)} over the selected period, while "
        f"annualized volatility was {_percent(risk.get('annualized_volatility'))}.",
        f"FinSight's transparent financial health score is {health['score']}/100, "
        f"which maps to the interface classification of {risk_level}.",
        "From an educational research perspective, the available data supports a balanced "
        "view that considers operating quality, valuation, market behavior, and missing information.",
    ]

    company_overview = (
        f"**Company:** {company_name}  \n"
        f"**Ticker:** {ticker}  \n"
        f"**Sector:** {profile.get('sector', 'N/A')}  \n"
        f"**Industry:** {profile.get('industry', 'N/A')}  \n"
        f"**Country:** {profile.get('country', 'N/A')}  \n"
        f"**Exchange:** {profile.get('exchange', 'N/A')}  \n"
        f"**Market capitalization:** {_money(profile.get('market_cap'), trading_currency)}\n\n"
        f"{profile.get('business_summary', 'Business summary unavailable from the current free data source.')}"
    )

    business_model = (
        f"The available profile suggests a **{business_style}** business model. "
        f"{business_explanation}\n\n"
        "The business summary above is the best free-source description of how the "
        "company makes money. FinSight does not have a verified segment revenue table, "
        "so it does not assign precise revenue contributions to products or divisions."
    )

    stock_performance = (
        f"The adjusted closing price moved from "
        f"**{_price(starting_price, trading_currency)}** to "
        f"**{_price(latest_price, trading_currency)}** over the selected period, "
        f"a return of **{_percent(period_return)}**. {price_view} "
        f"Annualized historical volatility was {_percent(risk.get('annualized_volatility'))}, "
        f"and the largest peak-to-trough decline in the period was "
        f"{_percent(risk.get('maximum_drawdown'))}. These are historical observations, "
        "not a forecast of the next price move."
    )

    financial_performance = (
        f"Latest available annual revenue is **{_money(financials.get('revenue'), financial_currency)}** "
        f"and net income is **{_money(financials.get('net_income'), financial_currency)}**. "
        f"The resulting net profit margin is {_percent(margin)}, while annual revenue "
        f"growth is {_percent(growth)}. Operating cash flow is "
        f"{_money(cash_flow, financial_currency)}.\n\n"
        f"Overall, the available financial picture is **{performance_strength}**. "
        "This classification is deliberately simple and should be checked against "
        "multiple years of statements, one-off items, and company guidance."
    )

    ratio_analysis = (
        f"- **Net profit margin — {_percent(margin)}:** the share of revenue left as net "
        "income after reported expenses. Higher and stable margins generally indicate "
        "stronger profitability, but useful comparisons are industry-specific.\n"
        f"- **Debt-to-assets — {_percent(ratios.get('debt_to_assets'))}:** the portion of "
        "reported assets financed by debt. A higher figure can increase sensitivity to "
        "interest rates and weaker operating conditions.\n"
        f"- **Return on equity — {_percent(ratios.get('return_on_equity'))}:** net income "
        "relative to shareholder equity. It can indicate capital efficiency, but high "
        "leverage may also lift this ratio.\n"
        f"- **Current ratio — {_number(ratios.get('current_ratio'))}:** current assets "
        "divided by current liabilities. It is a basic short-term liquidity measure and "
        "may be less informative for banks and some financial companies.\n"
        f"- **Revenue growth — {_percent(growth)}:** the latest annual change in sales. "
        "One year should be viewed as a snapshot rather than a durable trend."
    )

    risk_lines = [
        f"- **{item['name']} — {item['level']}:** {item['explanation']}"
        for item in risk_breakdown
    ]
    risk_analysis = (
        f"The overall interface classification is **{risk_level}**, based on the "
        f"{health['score']}/100 health score. This label is a screening aid, not a "
        "probability of loss.\n\n"
        + "\n".join(risk_lines)
        + "\n\n"
        + _valuation_view(profile)
    )

    if news:
        headline_lines = []
        for article in news[:6]:
            metadata = " · ".join(
                part
                for part in [article.get("publisher"), article.get("published_date")]
                if part
            )
            headline_lines.append(f"- **{article.get('title')}**" + (f" — {metadata}" if metadata else ""))
        news_text = (
            f"Rule-based headline sentiment is **{news_sentiment.get('label', 'Neutral')}**. "
            "This label uses simple positive and negative keywords and does not evaluate "
            "the full articles.\n\n" + "\n".join(headline_lines)
        )
    else:
        news_text = "Recent news data is not available from the current free data source."

    bullish = "\n".join(f"- {factor}" for factor in _bullish_factors(ratios, financials, risk))
    bearish = "\n".join(
        f"- {factor}" for factor in _bearish_factors(profile, ratios, financials, risk)
    )
    watchlist = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(build_investor_watchlist(profile, ratios), start=1)
    )

    dividend_yield = profile.get("dividend_yield")
    suitability_parts = [
        f"With a {risk_level.lower()} classification and {_percent(risk.get('annualized_volatility'))} "
        "historical volatility, the stock's risk profile is most relevant to investors "
        "who can tolerate that degree of price movement."
    ]
    if growth is not None and growth > 0.10:
        suitability_parts.append(
            "The available revenue growth may interest growth-oriented researchers, "
            "although valuation and growth durability still need review."
        )
    if dividend_yield is not None and dividend_yield > 0:
        suitability_parts.append(
            f"Yahoo Finance reports a dividend yield of {_percent(dividend_yield)}, "
            "which may be relevant to income-focused research; dividend sustainability "
            "has not been independently assessed."
        )
    else:
        suitability_parts.append(
            "Dividend suitability cannot be confirmed from the current available data."
        )
    suitability_parts.append(
        "Long-term, value, conservative, or higher-risk suitability depends on the "
        "investor's objectives and on deeper work beyond this educational screen."
    )

    return OrderedDict(
        [
            ("Executive Summary", " ".join(executive_sentences)),
            ("Company Overview", company_overview),
            ("Business Model Analysis", business_model),
            ("Stock Price Performance", stock_performance),
            ("Financial Performance", financial_performance),
            ("Key Financial Ratios", ratio_analysis),
            ("Risk Analysis", risk_analysis),
            ("News / Market Sentiment", news_text),
            ("Bullish Case", bullish),
            ("Bearish Case", bearish),
            ("Investor Watchlist", watchlist),
            ("Suitability Analysis", " ".join(suitability_parts)),
            (
                "Final Neutral View",
                f"From an educational research perspective, {company_name} appears to "
                f"have financial performance that is {performance_strength}, alongside "
                f"a {risk_level.lower()} "
                "screening classification. The company may have identifiable strengths, "
                "but those strengths should be weighed against the risk breakdown, "
                "valuation context, sector conditions, and gaps in free-source data. "
                "Investors may want to monitor the watchlist above and compare multiple "
                "years of filings before forming an independent view. FinSight does not "
                "provide a buy, sell, or hold recommendation.",
            ),
            ("Disclaimer", DISCLAIMER),
        ]
    )


def report_to_markdown(report: Mapping[str, str]) -> str:
    """Convert the ordered report into Markdown for display and download."""
    return "\n\n---\n\n".join(
        f"## {heading}\n\n{text}" for heading, text in report.items()
    )
