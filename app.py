"""FinSight AI V3 - premium, beginner-friendly global stock research."""

from __future__ import annotations

import html
import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from modules.ai_report import AIReportError, generate_ai_report, has_openai_api_key
from modules.data_fetcher import (
    StockDataError,
    fetch_company_news,
    fetch_company_profile,
    fetch_financial_data,
    fetch_stock_history,
)
from modules.financial_ratios import calculate_financial_ratios
from modules.news_analysis import analyze_news_sentiment, label_headline_sentiment
from modules.report_generator import (
    build_investor_watchlist,
    generate_research_report,
    report_to_markdown,
)
from modules.risk_analysis import (
    analyze_risk,
    build_risk_breakdown,
    calculate_financial_health_score,
    classify_risk_level,
)


st.set_page_config(
    page_title="FinSight AI",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Local development can use .env. Streamlit Community Cloud can provide the
# same values through its encrypted Secrets settings. Existing environment
# variables take priority, and the app never displays either value.
load_dotenv()


def configure_optional_openai_settings() -> None:
    """Copy optional Streamlit secrets into the environment for ai_report.py."""
    for setting_name in ("OPENAI_API_KEY", "OPENAI_MODEL"):
        if os.getenv(setting_name):
            continue
        try:
            secret_value = st.secrets[setting_name]
        except (FileNotFoundError, KeyError):
            # No secrets file is normal: FinSight uses the template report.
            continue
        if secret_value:
            os.environ[setting_name] = str(secret_value)


configure_optional_openai_settings()


PREMIUM_CSS = """
<style>
:root {
    --ink: #111214;
    --muted: #686b73;
    --line: rgba(17, 18, 20, 0.09);
    --surface: rgba(255, 255, 255, 0.82);
    --soft: #f5f6f8;
}

html {
    scroll-behavior: smooth;
    max-width: 100%;
    overflow-x: hidden;
}

*, *::before, *::after { box-sizing: border-box; }

body, .stApp {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter",
        "Segoe UI", sans-serif;
    color: var(--ink);
    background:
        radial-gradient(circle at 50% -10%, rgba(185, 205, 255, 0.42), transparent 34rem),
        linear-gradient(180deg, #fbfcff 0%, #ffffff 30%, #f7f8fa 100%);
}

[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {
    display: none !important;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.6rem;
    padding-bottom: 3rem;
    animation: pageEntrance 0.65s ease-out both;
}

@keyframes pageEntrance {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero {
    text-align: center;
    padding: 3.2rem 1rem 2rem;
    animation: fadeInUp 0.75s ease-out both;
}

.student-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.48rem 0.9rem;
    border: 1px solid rgba(17, 18, 20, 0.10);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.72);
    box-shadow: 0 8px 30px rgba(18, 23, 38, 0.06);
    color: #464951;
    font-size: 0.78rem;
    font-weight: 650;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    backdrop-filter: blur(18px);
}

.student-badge::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #111214;
}

.hero h1 {
    margin: 1.15rem 0 0.7rem;
    font-size: clamp(3.6rem, 8vw, 6.8rem);
    line-height: 0.96;
    letter-spacing: -0.072em;
    font-weight: 760;
    background: linear-gradient(145deg, #090a0c 25%, #545965 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero .subtitle {
    margin: 0 auto;
    max-width: 760px;
    font-size: clamp(1.2rem, 2.4vw, 1.75rem);
    line-height: 1.35;
    font-weight: 560;
    letter-spacing: -0.025em;
    color: #2b2e34;
}

.hero .description {
    margin: 0.8rem auto 0;
    max-width: 660px;
    color: var(--muted);
    font-size: 1.02rem;
    line-height: 1.7;
}

[data-testid="stForm"] {
    padding: 1.25rem 1.35rem 1.35rem;
    border: 1px solid rgba(255, 255, 255, 0.82);
    border-radius: 26px;
    background: rgba(255, 255, 255, 0.64);
    box-shadow: 0 24px 70px rgba(32, 39, 59, 0.12);
    backdrop-filter: blur(24px);
    animation: fadeInUp 0.8s 0.08s ease-out both;
}

[data-testid="stForm"] label {
    color: #555961 !important;
    font-size: 0.78rem !important;
    font-weight: 650 !important;
    letter-spacing: 0.025em;
}

[data-testid="stFormSubmitButton"] { margin-top: 1.68rem; }

[data-baseweb="input"] > div,
[data-baseweb="select"] > div {
    min-height: 3.25rem;
    border: 1px solid rgba(17, 18, 20, 0.10) !important;
    border-radius: 15px !important;
    background: rgba(248, 249, 251, 0.9) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: rgba(17, 18, 20, 0.32) !important;
    box-shadow: 0 0 0 4px rgba(17, 18, 20, 0.045) !important;
}

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
    min-height: 3.25rem;
    border: 0 !important;
    border-radius: 999px !important;
    background: linear-gradient(135deg, #101114 0%, #2b2f37 100%) !important;
    color: white !important;
    font-weight: 650 !important;
    box-shadow: 0 10px 25px rgba(15, 16, 18, 0.18);
    transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease;
}

.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 34px rgba(15, 16, 18, 0.24);
    filter: brightness(1.08);
}

.result-header {
    margin-top: 3.4rem;
    padding: 0 0.2rem 1rem;
    animation: fadeInUp 0.6s ease-out both;
}

.eyebrow {
    color: #777b84;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
}

.result-header h2 {
    margin: 0.35rem 0 0.35rem;
    font-size: clamp(2rem, 4vw, 3.3rem);
    letter-spacing: -0.045em;
    line-height: 1.08;
}

.result-header p { color: var(--muted); margin: 0; }

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 0.8rem 0 1.8rem;
}

.premium-card {
    position: relative;
    overflow: hidden;
    min-height: 156px;
    padding: 1.35rem;
    border: 1px solid var(--line);
    border-radius: 24px;
    background: var(--surface);
    box-shadow: 0 14px 38px rgba(31, 38, 57, 0.07);
    backdrop-filter: blur(18px);
    transition: transform 0.26s ease, box-shadow 0.26s ease, border-color 0.26s ease;
    animation: fadeInUp 0.65s ease-out both;
}

.premium-card::after {
    content: "";
    position: absolute;
    right: -34px;
    bottom: -48px;
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(151, 176, 234, 0.14), transparent 70%);
}

.premium-card:hover {
    transform: translateY(-5px);
    border-color: rgba(17, 18, 20, 0.16);
    box-shadow: 0 22px 50px rgba(31, 38, 57, 0.11);
}

.metric-label {
    color: #737780;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.metric-value {
    margin-top: 0.65rem;
    color: #121316;
    font-size: clamp(1.5rem, 2.5vw, 2.15rem);
    font-weight: 720;
    letter-spacing: -0.04em;
    line-height: 1.12;
    max-width: 100%;
    overflow-wrap: anywhere;
    word-break: break-word;
    font-variant-numeric: tabular-nums;
}

.metric-note {
    margin-top: 0.55rem;
    color: #868a92;
    font-size: 0.78rem;
}

.health-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
}

.score-track {
    height: 7px;
    margin-top: 0.8rem;
    overflow: hidden;
    border-radius: 999px;
    background: #e7e9ed;
}

.score-fill {
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, #444a55, #111214);
}

.risk-pill, .sentiment-pill, .level-pill {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    padding: 0.34rem 0.64rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.025em;
}

.low-risk, .Positive, .Low {
    color: #245d48;
    background: #e8f3ee;
}

.moderate-risk, .Mixed, .Moderate, .Context {
    color: #765c22;
    background: #f5efdf;
}

.high-risk, .Negative, .High {
    color: #80413d;
    background: #f7e9e7;
}

.Neutral, .Unknown {
    color: #535861;
    background: #eceef1;
}

[data-testid="stPlotlyChart"] {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    padding: 0.8rem;
    border: 1px solid var(--line);
    border-radius: 26px;
    background: rgba(255, 255, 255, 0.84);
    box-shadow: 0 16px 44px rgba(31, 38, 57, 0.065);
    animation: fadeInUp 0.7s ease-out both;
}

.js-plotly-plot, .plot-container, .svg-container {
    width: 100% !important;
    max-width: 100% !important;
}

.stTabs [data-baseweb="tab-list"] {
    display: flex;
    max-width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    flex-wrap: nowrap;
    overscroll-behavior-x: contain;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
    gap: 0.35rem;
    padding: 0.35rem;
    border-radius: 16px;
    background: #f0f1f3;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }

.stTabs [data-baseweb="tab"] {
    flex: 0 0 auto;
    white-space: nowrap;
    height: 2.8rem;
    padding: 0 1rem;
    border-radius: 12px;
    color: #656971;
    font-weight: 620;
}

.stTabs [aria-selected="true"] {
    color: #151619 !important;
    background: white !important;
    box-shadow: 0 5px 16px rgba(24, 29, 43, 0.08);
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

.stTabs [data-baseweb="tab-panel"] {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    padding-top: 1.4rem;
    animation: fadeInUp 0.45s ease-out both;
}

[data-testid="stDataFrame"], [data-testid="stTable"] {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

[data-testid="stMetric"] {
    min-height: 132px;
    padding: 1.1rem 1.2rem;
    border: 1px solid var(--line);
    border-radius: 20px;
    background: rgba(255,255,255,0.82);
    box-shadow: 0 10px 28px rgba(31, 38, 57, 0.055);
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 34px rgba(31, 38, 57, 0.09);
}

.section-card, .risk-card, .news-card {
    padding: 1.25rem 1.35rem;
    border: 1px solid var(--line);
    border-radius: 20px;
    background: rgba(255,255,255,0.8);
    box-shadow: 0 10px 28px rgba(31, 38, 57, 0.05);
}

.risk-grid, .news-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 0.9rem 0 1.2rem;
}

.risk-card, .news-card {
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.risk-card:hover, .news-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 36px rgba(31, 38, 57, 0.09);
}

.risk-card h4, .news-card h4 {
    margin: 0.65rem 0 0.45rem;
    font-size: 1rem;
    letter-spacing: -0.015em;
}

.risk-card p, .news-card p {
    margin: 0;
    color: var(--muted);
    font-size: 0.88rem;
    line-height: 1.55;
}

.news-card a {
    color: #151619;
    text-decoration: none;
}

.news-card a:hover { text-decoration: underline; }

.st-key-report_article {
    max-width: 880px;
    margin: 0 auto;
    padding: clamp(1.3rem, 4vw, 3.25rem) !important;
    border: 1px solid var(--line) !important;
    border-radius: 26px !important;
    background: rgba(255,255,255,0.92) !important;
    box-shadow: 0 18px 55px rgba(31, 38, 57, 0.075);
}

.st-key-report_article h2 {
    margin-top: 2.4rem;
    padding-top: 0.8rem;
    border-top: 1px solid #eceef1;
    font-size: 1.65rem;
    letter-spacing: -0.035em;
}

.st-key-report_article h2:first-child {
    margin-top: 0;
    padding-top: 0;
    border-top: 0;
}

.st-key-report_article p, .st-key-report_article li {
    color: #383b42;
    font-size: 1rem;
    line-height: 1.78;
}

.footer-note {
    max-width: 100%;
    overflow-wrap: anywhere;
    margin-top: 4rem;
    padding-top: 1.7rem;
    border-top: 1px solid rgba(17,18,20,0.08);
    color: #9699a0;
    text-align: center;
    font-size: 0.8rem;
    letter-spacing: 0.025em;
}

@media (max-width: 1024px) {
    .block-container {
        max-width: 100%;
        padding: 1.2rem 1.5rem 2.5rem;
    }

    .hero { padding: 2.5rem 0.75rem 1.8rem; }
    .hero h1 { font-size: clamp(4.3rem, 9vw, 5.4rem); }
    .hero .subtitle { max-width: 680px; }

    .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

    .st-key-report_article {
        max-width: 820px;
        padding: 2.25rem !important;
    }
}

@media (max-width: 768px) {
    .block-container {
        width: 100%;
        padding: 0.75rem 1rem 2rem;
    }

    .hero {
        padding: 1.65rem 0.25rem 1.35rem;
    }

    .hero h1 {
        margin-top: 0.9rem;
        font-size: clamp(3.25rem, 15vw, 4.35rem);
        letter-spacing: -0.065em;
    }

    .hero .subtitle {
        max-width: 520px;
        font-size: 1.15rem;
        line-height: 1.4;
    }

    .hero .description {
        max-width: 500px;
        margin-top: 0.65rem;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    [data-testid="stForm"] {
        width: 100%;
        padding: 1rem;
        border-radius: 22px;
        box-shadow: 0 15px 40px rgba(32, 39, 59, 0.09);
    }

    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.8rem !important;
    }

    [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 0 !important;
        flex: 1 1 100% !important;
    }

    [data-testid="stFormSubmitButton"] { margin-top: 0.15rem; }

    .stButton > button, .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 3.5rem;
        touch-action: manipulation;
    }

    .result-header {
        margin-top: 2.25rem;
        padding-bottom: 0.7rem;
    }

    .result-header h2 {
        font-size: clamp(1.85rem, 8vw, 2.6rem);
        overflow-wrap: anywhere;
    }

    .metric-grid {
        grid-template-columns: 1fr;
        gap: 0.8rem;
        margin-bottom: 1.25rem;
    }

    .premium-card {
        width: 100%;
        min-height: 132px;
        padding: 1.15rem;
        border-radius: 20px;
        box-shadow: 0 9px 24px rgba(31, 38, 57, 0.055);
    }

    .metric-value { font-size: clamp(1.6rem, 8vw, 2rem); }

    [data-testid="stPlotlyChart"] {
        width: 100%;
        padding: 0.35rem;
        border-radius: 20px;
        box-shadow: 0 10px 28px rgba(31, 38, 57, 0.05);
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: flex-start;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 2.65rem;
        padding: 0 0.85rem;
        font-size: 0.84rem;
    }

    .stTabs [data-baseweb="tab-panel"] { padding-top: 1rem; }

    .risk-grid, .news-grid { grid-template-columns: 1fr; }

    [data-testid="stMetric"] {
        width: 100%;
        min-height: auto;
        padding: 1rem;
    }

    .section-card, .risk-card, .news-card {
        padding: 1.05rem;
        border-radius: 18px;
        box-shadow: 0 7px 20px rgba(31, 38, 57, 0.045);
    }

    .st-key-report_article {
        width: 100%;
        max-width: 100%;
        padding: 1.3rem !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(31, 38, 57, 0.05);
        overflow-wrap: anywhere;
    }

    .st-key-report_article h2 {
        margin-top: 1.8rem;
        font-size: 1.38rem;
        line-height: 1.25;
    }

    .st-key-report_article p, .st-key-report_article li {
        font-size: 0.97rem;
        line-height: 1.7;
    }

    .footer-note {
        margin-top: 2.6rem;
        padding: 1.25rem 0.5rem 0;
        font-size: 0.74rem;
        line-height: 1.55;
    }
}

@media (max-width: 480px) {
    .block-container { padding: 0.5rem 0.75rem 1.6rem; }

    .hero { padding: 1.25rem 0 1rem; }

    .student-badge {
        padding: 0.42rem 0.68rem;
        font-size: 0.66rem;
        letter-spacing: 0.035em;
    }

    .hero h1 {
        font-size: clamp(3rem, 16vw, 3.65rem);
        letter-spacing: -0.06em;
    }

    .hero .subtitle {
        font-size: 1.03rem;
        line-height: 1.42;
    }

    .hero .description {
        font-size: 0.89rem;
        line-height: 1.55;
    }

    [data-testid="stForm"] {
        padding: 0.82rem;
        border-radius: 19px;
    }

    .premium-card {
        min-height: 124px;
        padding: 1rem;
    }

    .health-row { align-items: flex-start; }

    .stTabs [data-baseweb="tab"] {
        padding: 0 0.72rem;
        font-size: 0.78rem;
    }

    .st-key-report_article {
        padding: 1.05rem !important;
        border-radius: 17px !important;
    }

    .st-key-report_article h2 {
        font-size: 1.22rem;
        letter-spacing: -0.025em;
    }

    .st-key-report_article p, .st-key-report_article li {
        font-size: 0.94rem;
        line-height: 1.64;
    }

    .footer-note {
        font-size: 0.69rem;
        letter-spacing: 0.01em;
    }
}

@media (hover: none), (pointer: coarse) {
    .premium-card:hover, [data-testid="stMetric"]:hover,
    .risk-card:hover, .news-card:hover {
        transform: none;
        box-shadow: 0 7px 20px rgba(31, 38, 57, 0.045);
    }

    .stButton > button:hover, .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        transform: none;
    }
}

@media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=900, show_spinner=False)
def load_stock_data(ticker: str, period: str):
    """Cache Yahoo data for 15 minutes to reduce repeated requests."""
    profile = fetch_company_profile(ticker)
    history = fetch_stock_history(ticker, period)
    financials = fetch_financial_data(ticker)
    news = fetch_company_news(ticker)
    return profile, history, financials, news


def format_money(
    value: float | None,
    currency: str | None = None,
    compact: bool = True,
) -> str:
    """Turn a number into a readable currency-aware value."""
    if value is None or pd.isna(value):
        return "N/A"
    prefix = f"{currency} " if currency else ""
    if not compact:
        return f"{prefix}{value:,.2f}"
    absolute_value = abs(value)
    if absolute_value >= 1_000_000_000_000:
        return f"{prefix}{value / 1_000_000_000_000:,.2f}T"
    if absolute_value >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:,.2f}B"
    if absolute_value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:,.2f}M"
    return f"{prefix}{value:,.0f}"


def format_percent(value: float | None) -> str:
    """Format a decimal ratio such as 0.15 as 15.00%."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.2%}"


def format_ratio(value: float | None) -> str:
    """Format a non-percentage financial ratio."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.2f}"


def create_price_chart(
    history: pd.DataFrame,
    company_name: str,
    currency: str | None,
) -> go.Figure:
    """Build an understated interactive Plotly closing-price chart."""
    y_axis_title = f"Price ({currency})" if currency else "Price"
    hover_prefix = f"{currency} " if currency else ""
    figure = go.Figure(
        go.Scatter(
            x=history.index,
            y=history["Close"],
            mode="lines",
            name="Closing price",
            fill="tozeroy",
            fillcolor="rgba(92, 112, 160, 0.07)",
            line={"color": "#252a33", "width": 2.4},
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>{hover_prefix}"
                "%{y:,.2f}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title={"text": f"{company_name} · price history", "font": {"size": 18}},
        xaxis_title="Date",
        yaxis_title=y_axis_title,
        hovermode="x unified",
        height=440,
        margin={"l": 28, "r": 20, "t": 62, "b": 26},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            "color": "#555a64",
        },
        xaxis={"gridcolor": "rgba(20,24,32,0.055)", "zeroline": False},
        yaxis={"gridcolor": "rgba(20,24,32,0.055)", "zeroline": False},
    )
    return figure


def render_metric_cards(
    profile: dict[str, Any],
    history: pd.DataFrame,
    risk: dict[str, float | None],
    health: dict[str, Any],
    risk_classification: dict[str, str],
) -> None:
    """Render four premium headline cards with a health progress bar."""
    currency = profile.get("currency")
    cards = [
        (
            "Market Cap",
            format_money(profile.get("market_cap"), currency),
            "Reported by Yahoo Finance",
        ),
        (
            "Latest Close",
            format_money(float(history["Close"].iloc[-1]), currency, compact=False),
            f"Trading currency · {currency or 'Unavailable'}",
        ),
        (
            "Period Return",
            format_percent(risk.get("period_return")),
            "Adjusted close · selected period",
        ),
    ]
    card_html = "".join(
        f'<div class="premium-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div>'
        f'</div>'
        for label, value, note in cards
    )
    score = int(health["score"])
    health_card = (
        f'<div class="premium-card">'
        f'<div class="health-row"><div class="metric-label">Health Score</div>'
        f'<span class="risk-pill {risk_classification["css_class"]}">'
        f'{html.escape(risk_classification["label"])}</span></div>'
        f'<div class="metric-value">{score}'
        f'<span style="font-size:.9rem;color:#8a8e96"> / 100</span></div>'
        f'<div class="score-track"><div class="score-fill" style="width:{score}%">'
        f'</div></div><div class="metric-note">Transparent screening score</div>'
        f'</div>'
    )
    st.markdown(
        f'<div class="metric-grid">{card_html}{health_card}</div>',
        unsafe_allow_html=True,
    )


def render_risk_cards(risk_breakdown: list[dict[str, str]]) -> None:
    """Display the transparent risk breakdown in compact cards."""
    cards = []
    for item in risk_breakdown:
        level = html.escape(item["level"])
        cards.append(
            f'<div class="risk-card">'
            f'<span class="level-pill {level}">{level}</span>'
            f'<h4>{html.escape(item["name"])}</h4>'
            f'<p>{html.escape(item["explanation"])}</p>'
            f'</div>'
        )
    st.markdown(
        f'<div class="risk-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_news(
    news: list[dict[str, str | None]],
    sentiment: dict[str, Any],
) -> None:
    """Show only real Yahoo headlines, with transparent keyword sentiment."""
    label = html.escape(str(sentiment.get("label", "Neutral")))
    st.markdown(
        f"""
        <div class="section-card">
            <div class="eyebrow">Headline pulse</div>
            <h3 style="margin:.45rem 0 .5rem">Market sentiment
                <span class="sentiment-pill {label}">{label}</span>
            </h3>
            <p style="color:#737780;margin:0;line-height:1.6">
                A simple keyword label based on available headlines—not full-article analysis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not news:
        st.info("Recent news data is not available from the current free data source.")
        return

    cards = []
    for article in news:
        title = html.escape(article.get("title") or "Untitled")
        publisher = html.escape(article.get("publisher") or "Publisher unavailable")
        date = html.escape(article.get("published_date") or "Date unavailable")
        item_label = label_headline_sentiment(article.get("title") or "")
        safe_url = article.get("link")
        linked_title = title
        if safe_url and safe_url.startswith(("https://", "http://")):
            linked_title = (
                f'<a href="{html.escape(safe_url, quote=True)}" target="_blank" '
                f'rel="noopener noreferrer">{title}</a>'
            )
        cards.append(
            f'<div class="news-card">'
            f'<span class="sentiment-pill {item_label}">{item_label}</span>'
            f'<h4>{linked_title}</h4>'
            f'<p>{publisher} · {date}</p>'
            f'</div>'
        )
    st.markdown(
        f'<div class="news-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )
    st.caption("Headlines, publishers, dates, and links are supplied by Yahoo Finance.")


def show_dashboard(ticker: str, period: str) -> None:
    """Load data, calculate research signals, and render the full dashboard."""
    profile, history, financials, news = load_stock_data(ticker, period)
    ratios = calculate_financial_ratios(financials)
    risk = analyze_risk(history, profile.get("beta"))
    health = calculate_financial_health_score(ratios, financials, history)
    risk_classification = classify_risk_level(int(health["score"]))
    risk_breakdown = build_risk_breakdown(ratios, risk, profile)
    sentiment = analyze_news_sentiment(news)

    template_report = generate_research_report(
        ticker=ticker,
        profile=profile,
        history=history,
        financials=financials,
        ratios=ratios,
        risk=risk,
        health=health,
        risk_level=risk_classification["label"],
        risk_breakdown=risk_breakdown,
        news=news,
        news_sentiment=sentiment,
    )
    report_markdown = report_to_markdown(template_report)
    report_source = "Detailed template report"
    ai_error = None

    if has_openai_api_key():
        try:
            report_markdown = generate_ai_report(
                ticker=ticker,
                profile=profile,
                history=history,
                financials=financials,
                ratios=ratios,
                risk=risk,
                health=health,
                risk_level=risk_classification["label"],
                risk_breakdown=risk_breakdown,
                news=news,
                news_sentiment=sentiment,
            )
            report_source = (
                f"AI-generated research · {os.getenv('OPENAI_MODEL', 'gpt-5.5')}"
            )
        except AIReportError:
            ai_error = (
                "The AI report was unavailable, so FinSight preserved the full "
                "analytical template report."
            )

    currency = profile.get("currency")
    financial_currency = profile.get("financial_currency") or currency
    company_name = profile["company_name"]

    st.markdown(
        f"""
        <section class="result-header">
            <div class="eyebrow">Research workspace · {html.escape(ticker)}</div>
            <h2>{html.escape(company_name)}</h2>
            <p>{html.escape(str(profile['sector']))} &nbsp;·&nbsp;
               {html.escape(str(profile['industry']))} &nbsp;·&nbsp;
               {html.escape(str(profile['country']))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(profile, history, risk, health, risk_classification)
    st.plotly_chart(
        create_price_chart(history, company_name, currency),
        width="stretch",
        config={"displaylogo": False, "responsive": True},
    )

    overview_tab, financial_tab, risk_tab, news_tab, report_tab = st.tabs(
        ["Overview", "Financials", "Risk Analysis", "News", "Research Report"]
    )

    with overview_tab:
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("### Company overview")
            st.markdown(
                f"""
                **Ticker:** {ticker}  
                **Exchange:** {profile['exchange']}  
                **Sector:** {profile['sector']}  
                **Industry:** {profile['industry']}  
                **Country:** {profile['country']}  
                **Trading currency:** {currency or 'Unavailable'}
                """
            )
            website = profile.get("website")
            if website and str(website).startswith(("http://", "https://")):
                st.link_button("Visit company website ↗", str(website))
        with right:
            st.markdown("### Business model")
            st.write(profile["business_summary"])
            st.caption(
                "The summary is supplied by Yahoo Finance. Segment-level revenue "
                "data may not be available from the free source."
            )

    with financial_tab:
        st.markdown("### Latest annual financial snapshot")
        metric_columns = st.columns(5)
        values = [
            ("Revenue", financials.get("revenue")),
            ("Net income", financials.get("net_income")),
            ("Total assets", financials.get("total_assets")),
            ("Total debt", financials.get("total_debt")),
            ("Operating cash flow", financials.get("operating_cash_flow")),
        ]
        for column, (label, value) in zip(metric_columns, values):
            column.metric(label, format_money(value, financial_currency))

        st.markdown("### Key financial ratios")
        ratio_columns = st.columns(5)
        ratio_values = [
            ("Net margin", format_percent(ratios.get("net_profit_margin"))),
            ("Debt / assets", format_percent(ratios.get("debt_to_assets"))),
            ("Return on equity", format_percent(ratios.get("return_on_equity"))),
            ("Current ratio", format_ratio(ratios.get("current_ratio"))),
            ("Revenue growth", format_percent(ratios.get("revenue_growth"))),
        ]
        for column, (label, value) in zip(ratio_columns, ratio_values):
            column.metric(label, value)

        with st.expander("How to read these ratios", expanded=True):
            st.markdown(
                """
                - **Net margin** shows how much revenue remains as net income.
                - **Debt-to-assets** shows how much of the asset base is financed by debt.
                - **Return on equity** measures net income relative to shareholder equity.
                - **Current ratio** compares short-term assets with short-term liabilities.
                - **Revenue growth** compares the latest annual revenue with the previous year.

                Ratios are most useful when compared with several years of history and
                similar companies. `N/A` means the free data source did not provide the inputs.
                """
            )

        st.markdown("### Health score explanation")
        st.progress(int(health["score"]) / 100)
        st.caption(
            f"{health['score']}/100 · {risk_classification['label']} screening classification"
        )
        for explanation in health["explanations"]:
            st.write(f"• {explanation}")

    with risk_tab:
        st.markdown(
            f"""
            <h3 style="margin-bottom:.35rem">Risk profile
                <span class="risk-pill {risk_classification['css_class']}">
                    {html.escape(risk_classification['label'])}
                </span>
            </h3>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "The label follows the requested score bands. It is not a prediction "
            "of loss or a substitute for personal risk assessment."
        )
        render_risk_cards(risk_breakdown)

        indicators = st.columns(4)
        indicators[0].metric(
            "Volatility", format_percent(risk.get("annualized_volatility"))
        )
        indicators[1].metric(
            "Maximum drawdown", format_percent(risk.get("maximum_drawdown"))
        )
        indicators[2].metric(
            "Beta", format_ratio(risk.get("beta"))
        )
        indicators[3].metric(
            "Period return", format_percent(risk.get("period_return"))
        )

        st.markdown("### Investor watchlist")
        for index, item in enumerate(build_investor_watchlist(profile, ratios), start=1):
            st.markdown(f"**{index}.** {item}")

    with news_tab:
        render_news(news, sentiment)

    with report_tab:
        st.caption(report_source)
        if ai_error:
            st.info(ai_error)
        with st.container(border=True, key="report_article"):
            st.markdown(report_markdown.replace("$", "&#36;"))
        st.download_button(
            "Download full research report",
            data=report_markdown,
            file_name=f"finsight_ai_report_{ticker}.md",
            mime="text/markdown",
            width="stretch",
            on_click="ignore",
        )


st.markdown(
    """
    <section class="hero">
        <div class="student-badge">Made by a FinTech Student</div>
        <h1>FinSight AI</h1>
        <p class="subtitle">AI-powered financial research assistant for global stocks.</p>
        <p class="description">
            Analyze stocks, financial performance, risks, and investor watchlists
            in one clean dashboard.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.form("ticker_form"):
    input_column, period_column, button_column = st.columns([2, 1, 1])
    ticker_input = input_column.text_input(
        "Stock ticker",
        value="AAPL",
        placeholder="Try AAPL, 1155.KL, or 0700.HK",
    )
    period_label = period_column.selectbox(
        "Price history",
        ["1 Year", "2 Years", "5 Years", "10 Years", "Maximum"],
        index=2,
    )
    submitted = button_column.form_submit_button(
        "Generate Research", width="stretch", type="primary"
    )

period_options = {
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "10 Years": "10y",
    "Maximum": "max",
}

if submitted:
    cleaned_ticker = ticker_input.strip().upper()
    if not cleaned_ticker:
        st.warning("Please enter a stock ticker.")
    elif len(cleaned_ticker) > 15:
        st.error("That ticker is too long. Please check it and try again.")
    else:
        try:
            with st.spinner("Analyzing market data and generating research report..."):
                show_dashboard(cleaned_ticker, period_options[period_label])
        except StockDataError as error:
            st.error(str(error))
        except Exception:
            st.error(
                "FinSight could not complete this request. The market-data service "
                "may be temporarily unavailable, so please try again shortly."
            )

st.markdown(
    '<div class="footer-note">FinSight AI | Made by a FinTech Student | Educational Use Only</div>',
    unsafe_allow_html=True,
)
