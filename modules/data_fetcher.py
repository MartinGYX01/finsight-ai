"""Functions for downloading company and financial data from Yahoo Finance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import yfinance as yf


class StockDataError(Exception):
    """A friendly error that can be shown directly in the Streamlit app."""


def _safe_info_value(info: dict[str, Any], key: str, fallback: Any = "N/A") -> Any:
    """Return a profile value while handling missing and empty fields."""
    value = info.get(key)
    return value if value not in (None, "") else fallback


def _normalized_dividend_yield(info: dict[str, Any]) -> float | None:
    """Calculate a decimal dividend yield despite Yahoo format differences."""
    dividend_rate = info.get("dividendRate")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    try:
        if dividend_rate is not None and current_price not in (None, 0):
            return float(dividend_rate) / float(current_price)
    except (TypeError, ValueError, ZeroDivisionError):
        pass

    # Older Yahoo responses used decimals (0.006), while some newer responses
    # use percentage points (0.6). This fallback handles both representations.
    raw_yield = info.get("dividendYield")
    try:
        parsed_yield = float(raw_yield)
    except (TypeError, ValueError):
        return None
    return parsed_yield / 100 if parsed_yield > 0.15 else parsed_yield


def fetch_company_profile(ticker_symbol: str) -> dict[str, Any]:
    """Fetch the descriptive company information for one ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
    except Exception as error:
        raise StockDataError(
            f"Could not retrieve company information for '{ticker_symbol}'. "
            "Please check the ticker and try again."
        ) from error

    # Yahoo sometimes returns an almost-empty dictionary for an invalid ticker.
    if not info or not (info.get("longName") or info.get("shortName")):
        raise StockDataError(
            f"'{ticker_symbol}' does not appear to be a valid stock ticker."
        )

    return {
        "company_name": _safe_info_value(
            info, "longName", _safe_info_value(info, "shortName", ticker_symbol)
        ),
        "sector": _safe_info_value(info, "sector"),
        "industry": _safe_info_value(info, "industry"),
        "country": _safe_info_value(info, "country"),
        # "currency" is the trading currency used for prices and market cap.
        # "financialCurrency" is the currency used in company statements.
        "currency": _safe_info_value(info, "currency", None),
        "financial_currency": _safe_info_value(info, "financialCurrency", None),
        "market_cap": _safe_info_value(info, "marketCap", None),
        "business_summary": _safe_info_value(
            info, "longBusinessSummary", "No business summary is available."
        ),
        "website": _safe_info_value(info, "website"),
        "exchange": _safe_info_value(info, "exchange"),
        "beta": _safe_info_value(info, "beta", None),
        "trailing_pe": _safe_info_value(info, "trailingPE", None),
        "forward_pe": _safe_info_value(info, "forwardPE", None),
        "dividend_yield": _normalized_dividend_yield(info),
    }


def fetch_stock_history(ticker_symbol: str, period: str = "5y") -> pd.DataFrame:
    """Fetch historical prices and ensure usable closing prices are present."""
    try:
        history = yf.Ticker(ticker_symbol).history(
            period=period, interval="1d", auto_adjust=True
        )
    except Exception as error:
        raise StockDataError(
            f"Could not download price history for '{ticker_symbol}'."
        ) from error

    if history.empty or "Close" not in history.columns:
        raise StockDataError(
            f"No stock-price history was found for '{ticker_symbol}'. "
            "Please check the ticker and try again."
        )

    history = history.copy()
    history["Close"] = pd.to_numeric(history["Close"], errors="coerce")
    history = history.dropna(subset=["Close"])
    if history.empty:
        raise StockDataError(f"No usable price data was found for '{ticker_symbol}'.")
    return history


def _find_statement_value(
    statement: pd.DataFrame, possible_rows: list[str], column_position: int = 0
) -> float | None:
    """Find a value despite small naming differences in financial statements."""
    if statement is None or statement.empty or len(statement.columns) <= column_position:
        return None

    for row_name in possible_rows:
        if row_name in statement.index:
            value = statement.loc[row_name].iloc[column_position]
            if pd.notna(value):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None
    return None


def fetch_financial_data(ticker_symbol: str) -> dict[str, float | None]:
    """Fetch the latest annual statements and extract the fields used by the app."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        income_statement = ticker.income_stmt
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow
    except Exception:
        # Prices may be available even when statements are not. In that case the
        # app remains useful and displays N/A for unavailable financial fields.
        income_statement = pd.DataFrame()
        balance_sheet = pd.DataFrame()
        cash_flow = pd.DataFrame()

    return {
        "revenue": _find_statement_value(
            income_statement, ["Total Revenue", "Operating Revenue"]
        ),
        "previous_revenue": _find_statement_value(
            income_statement, ["Total Revenue", "Operating Revenue"], 1
        ),
        "net_income": _find_statement_value(
            income_statement,
            ["Net Income", "Net Income Common Stockholders", "Net Income Continuous Operations"],
        ),
        "total_assets": _find_statement_value(balance_sheet, ["Total Assets"]),
        "stockholders_equity": _find_statement_value(
            balance_sheet,
            ["Stockholders Equity", "Total Equity Gross Minority Interest"],
        ),
        "current_assets": _find_statement_value(
            balance_sheet, ["Current Assets", "Total Current Assets"]
        ),
        "current_liabilities": _find_statement_value(
            balance_sheet, ["Current Liabilities", "Total Current Liabilities"]
        ),
        "total_debt": _find_statement_value(
            balance_sheet,
            ["Total Debt", "Total Liabilities Net Minority Interest"],
        ),
        "operating_cash_flow": _find_statement_value(
            cash_flow,
            ["Operating Cash Flow", "Total Cash From Operating Activities"],
        ),
    }


def _published_date(value: Any) -> str | None:
    """Convert the different Yahoo date formats into a readable date."""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%d %b %Y")
        parsed = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.strftime("%d %b %Y")
    except (TypeError, ValueError, OverflowError):
        return None


def fetch_company_news(ticker_symbol: str, limit: int = 8) -> list[dict[str, str | None]]:
    """Fetch and normalize recent Yahoo Finance headlines when available.

    Yahoo has used both flat and nested news formats, so this function supports
    both and returns only real fields supplied by Yahoo.
    """
    try:
        raw_news = yf.Ticker(ticker_symbol).news or []
    except Exception:
        return []

    articles: list[dict[str, str | None]] = []
    for item in raw_news:
        if not isinstance(item, dict):
            continue

        content = item.get("content") if isinstance(item.get("content"), dict) else item
        title = content.get("title")
        if not title:
            continue

        provider = content.get("provider")
        publisher = (
            provider.get("displayName")
            if isinstance(provider, dict)
            else content.get("publisher")
        )

        canonical_url = content.get("canonicalUrl")
        click_url = content.get("clickThroughUrl")
        link = (
            canonical_url.get("url")
            if isinstance(canonical_url, dict)
            else click_url.get("url")
            if isinstance(click_url, dict)
            else content.get("link")
        )

        articles.append(
            {
                "title": str(title),
                "publisher": str(publisher) if publisher else "Publisher unavailable",
                "published_date": _published_date(
                    content.get("pubDate") or content.get("providerPublishTime")
                ),
                "link": str(link) if link else None,
            }
        )
        if len(articles) >= limit:
            break

    return articles
