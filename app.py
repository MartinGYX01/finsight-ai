"""FinSight AI V7 - premium, beginner-friendly global stock research."""

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
from modules.formatting import (
    format_currency,
    format_percent as shared_format_percent,
    format_price,
    format_ratio as shared_format_ratio,
)
from modules.i18n import (
    risk_label,
    sentiment_label,
    text,
    translate_risk_breakdown,
)
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
from modules.volatility_analysis import build_volatility_outlook


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
    --ink: #18181b;
    --text: #27272a;
    --muted: #52525b;
    --quiet: #71717a;
    --line: #e5e5e5;
    --surface: #ffffff;
    --soft: #f7f7f5;
    --accent: #18181b;
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
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
        "SF Pro Text", "Inter", "Segoe UI", "Roboto", "Helvetica Neue",
        Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
        "Noto Sans CJK SC", sans-serif;
    color: var(--ink);
    background: #f7f7f5;
}

[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {
    display: none !important;
}

.block-container {
    max-width: 1140px;
    padding-top: 1.2rem;
    padding-bottom: 3.25rem;
    animation: pageEntrance 0.35s ease-out both;
}

@keyframes pageEntrance {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero {
    position: relative;
    overflow: hidden;
    text-align: center;
    max-width: 920px;
    margin: 0 auto 1.45rem;
    padding: clamp(3.3rem, 7vw, 5.6rem) 1rem 1.6rem;
    animation: fadeInUp 0.42s ease-out both;
}

.student-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.44rem 0.78rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: #ffffff;
    color: var(--muted);
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.035em;
    text-transform: uppercase;
}

.student-badge::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #18181b;
}

.hero-title {
    margin: 1.15rem 0 0.85rem;
    color: var(--ink);
    font-size: clamp(56px, 7vw, 96px);
    line-height: 0.96;
    letter-spacing: -0.052em;
    font-weight: 730;
}

.hero-subtitle {
    margin: 0 auto;
    max-width: 820px;
    color: var(--ink);
    font-size: clamp(24px, 2.5vw, 34px);
    line-height: 1.2;
    font-weight: 600;
    letter-spacing: -0.025em;
}

[data-testid="stForm"] {
    max-width: 900px;
    margin: 0 auto;
    padding: 1rem;
    border: 1px solid var(--line);
    border-radius: 20px;
    background: #ffffff;
    box-shadow: 0 10px 28px rgba(24, 24, 27, 0.045);
    animation: fadeInUp 0.38s 0.04s ease-out both;
}

[data-testid="stForm"] label {
    min-height: 1.28rem;
    color: #3f3f46 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.015em;
}

[data-testid="stFormSubmitButton"] { margin-top: 2.54rem; }

[data-baseweb="input"],
[data-baseweb="input"] > div,
[data-baseweb="select"],
[data-baseweb="select"] > div {
    min-height: 3.5rem;
    height: 3.5rem;
    border: 1px solid #d8d8d8 !important;
    border-radius: 15px !important;
    background: #ffffff !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-baseweb="input"] input,
[data-baseweb="select"] *,
[data-baseweb="popover"] * {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    font-size: 0.95rem !important;
    opacity: 1 !important;
}

[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[role="listbox"],
[role="option"] {
    background: #ffffff !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    opacity: 1 !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #f4f4f5 !important;
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
}

[data-baseweb="input"] input::placeholder {
    color: #71717a !important;
    -webkit-text-fill-color: #71717a !important;
    opacity: 1 !important;
}

[data-baseweb="input"]:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: #18181b !important;
    box-shadow: 0 0 0 3px rgba(24, 24, 27, 0.08) !important;
}

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
    min-height: 3.5rem;
    height: 3.5rem;
    border: 0 !important;
    border-radius: 15px !important;
    background: #18181b !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.005em;
    box-shadow: none;
    transition: transform 0.18s ease, background-color 0.18s ease, box-shadow 0.18s ease;
}

.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    background: #27272a !important;
    box-shadow: 0 8px 18px rgba(24, 24, 27, 0.12);
    filter: none;
}

.result-header {
    margin-top: 3.2rem;
    padding: 0 0.2rem 1rem;
    animation: fadeInUp 0.6s ease-out both;
}

.eyebrow {
    color: var(--quiet);
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.result-header h2 {
    margin: 0.35rem 0 0.35rem;
    color: var(--ink);
    font-size: clamp(1.85rem, 3.4vw, 2.35rem);
    font-weight: 650;
    letter-spacing: -0.035em;
    line-height: 1.15;
}

.result-header p { color: var(--muted); margin: 0; }

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin: 0.8rem 0 1.8rem;
}

.metric-grid.cols-5 {
    grid-template-columns: repeat(5, minmax(0, 1fr));
}

.metric-grid.cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.value-card {
    min-height: 132px;
}

.premium-card {
    position: relative;
    overflow: visible;
    min-height: 150px;
    padding: 1.25rem;
    border: 1px solid var(--line);
    border-radius: 18px;
    background: var(--surface);
    box-shadow: 0 6px 16px rgba(24, 24, 27, 0.035);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    animation: fadeInUp 0.35s ease-out both;
}

.premium-card::after {
    display: none;
}

.premium-card:hover {
    transform: translateY(-2px);
    border-color: #d4d4d8;
    box-shadow: 0 10px 22px rgba(24, 24, 27, 0.055);
}

.metric-label {
    color: var(--quiet);
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.055em;
    text-transform: uppercase;
}

.metric-value {
    margin-top: 0.65rem;
    color: var(--ink);
    font-size: clamp(1.75rem, 2.45vw, 2.25rem);
    font-weight: 650;
    letter-spacing: -0.04em;
    line-height: 1.08;
    max-width: 100%;
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    overflow-wrap: normal;
    word-break: normal;
    font-variant-numeric: tabular-nums;
}

.metric-note {
    margin-top: 0.55rem;
    color: var(--quiet);
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
    background: #ececec;
}

.score-fill {
    height: 100%;
    border-radius: inherit;
    background: #18181b;
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
    border-radius: 20px;
    background: #ffffff;
    box-shadow: 0 6px 18px rgba(24, 24, 27, 0.035);
    animation: fadeInUp 0.35s ease-out both;
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
    background: #eeeeec;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }

.stTabs [data-baseweb="tab"] {
    flex: 0 0 auto;
    white-space: nowrap;
    height: 2.8rem;
    padding: 0 1rem;
    border-radius: 12px;
    color: var(--muted);
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: var(--ink) !important;
    background: white !important;
    box-shadow: 0 2px 8px rgba(24, 24, 27, 0.06);
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

.stTabs [data-baseweb="tab-panel"] {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    padding-top: 1.4rem;
    animation: fadeInUp 0.25s ease-out both;
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
    border-radius: 18px;
    background: #ffffff;
    box-shadow: 0 4px 14px rgba(24, 24, 27, 0.03);
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    overflow: visible !important;
}

[data-testid="stMetric"] * {
    opacity: 1 !important;
}

[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
.metric-label {
    color: #52525b !important;
    -webkit-text-fill-color: #52525b !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"] *,
.metric-value {
    color: #18181b !important;
    -webkit-text-fill-color: #18181b !important;
    opacity: 1 !important;
    font-weight: 650 !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(24, 24, 27, 0.055);
}

.section-card, .risk-card, .news-card {
    padding: 1.25rem 1.35rem;
    border: 1px solid var(--line);
    border-radius: 18px;
    background: #ffffff;
    box-shadow: 0 4px 14px rgba(24, 24, 27, 0.03);
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
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(24, 24, 27, 0.055);
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
    color: var(--ink);
    text-decoration: none;
}

.news-card a:hover { text-decoration: underline; }

.st-key-report_article {
    max-width: 880px;
    margin: 0 auto;
    padding: clamp(1.3rem, 4vw, 3.25rem) !important;
    border: 1px solid var(--line) !important;
    border-radius: 20px !important;
    background: #ffffff !important;
    box-shadow: 0 6px 18px rgba(24, 24, 27, 0.035);
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
    color: var(--text);
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

    .hero {
        padding: 3rem 1rem 1.45rem;
    }
    .hero-title { font-size: clamp(3.5rem, 9vw, 5.4rem); }
    .hero-subtitle { max-width: 680px; }

    .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .metric-grid.cols-5,
    .metric-grid.cols-3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }

    .st-key-report_article {
        max-width: 820px;
        padding: 2.25rem !important;
    }
}

@media (max-width: 768px) {
    body, .stApp {
        color: var(--ink);
        background: #f7f7f5;
    }

    .block-container {
        width: 100%;
        padding: 0.75rem 1rem 6rem;
    }

    .hero {
        padding: 2.25rem 0.25rem 1.2rem;
    }

    .hero-title {
        margin-top: 0.9rem;
        font-size: clamp(2.75rem, 13vw, 3.5rem);
        letter-spacing: -0.045em;
        line-height: 0.98;
    }

    .hero-subtitle {
        max-width: 520px;
        font-size: clamp(1.25rem, 5.4vw, 1.5rem);
        line-height: 1.25;
    }

    [data-testid="stForm"] {
        width: 100%;
        margin-top: 0;
        padding: 1rem;
        border-radius: 18px;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(24, 24, 27, 0.035);
    }

    [data-testid="stForm"] label,
    [data-testid="stWidgetLabel"] p {
        color: #3f3f46 !important;
        opacity: 1 !important;
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

    .metric-grid.cols-5,
    .metric-grid.cols-3 { grid-template-columns: 1fr; }

    .premium-card {
        width: 100%;
        min-height: 132px;
        padding: 1.15rem;
        border-radius: 20px;
        box-shadow: 0 3px 10px rgba(24, 24, 27, 0.03);
        background: #ffffff;
    }

    .metric-value { font-size: clamp(2rem, 9vw, 2.4rem); }
    .metric-label, .eyebrow { color: #52525b; opacity: 1; }
    .metric-note, .result-header p { color: #71717a; opacity: 1; }

    [data-testid="stPlotlyChart"] {
        width: 100%;
        padding: 0.35rem;
        border-radius: 18px;
        background: #ffffff;
        box-shadow: 0 3px 10px rgba(24, 24, 27, 0.03);
        animation: none;
    }

    [data-testid="stPlotlyChart"] .js-plotly-plot,
    [data-testid="stPlotlyChart"] .plot-container,
    [data-testid="stPlotlyChart"] .svg-container {
        height: 310px !important;
        min-height: 310px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: flex-start;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 2.65rem;
        padding: 0 0.85rem;
        font-size: 0.84rem;
        color: #3f3f46;
        opacity: 1;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .risk-grid, .news-grid { grid-template-columns: 1fr; }

    [data-testid="stMetric"] {
        width: 100%;
        min-height: auto;
        padding: 1rem;
    }

    .section-card, .risk-card, .news-card {
        padding: 1.05rem;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 2px 8px rgba(24, 24, 27, 0.025);
    }

    h1, h2, h3, h4, h5, h6,
    .risk-card h4, .news-card h4 {
        color: var(--ink) !important;
        opacity: 1 !important;
    }

    p, li, .stMarkdown, .stCaption, [data-testid="stCaptionContainer"] {
        opacity: 1 !important;
    }

    .risk-card p, .news-card p, [data-testid="stCaptionContainer"] p {
        color: #3f3f46 !important;
    }

    .st-key-report_article {
        width: 100%;
        max-width: 100%;
        padding: 1.3rem !important;
        border-radius: 20px !important;
        box-shadow: 0 3px 10px rgba(24, 24, 27, 0.03);
        overflow-wrap: anywhere;
        background: #ffffff !important;
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
        color: #6b7280;
    }

    .hero, .result-header, .premium-card,
    .stTabs [data-baseweb="tab-panel"] { animation: none; }

    @keyframes mobileFade {
        from { opacity: 0; }
        to { opacity: 1; }
    }
}

@media (max-width: 480px) {
    .block-container { padding: 0.5rem 0.75rem 6.5rem; }

    .hero { padding: 1.8rem 0 1rem; }

    .student-badge {
        padding: 0.42rem 0.68rem;
        font-size: 0.66rem;
        letter-spacing: 0.02em;
    }

    .hero-title {
        font-size: clamp(2.75rem, 14.5vw, 3.35rem);
        letter-spacing: -0.042em;
    }

    .hero-subtitle {
        font-size: 1.22rem;
        line-height: 1.25;
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
    language: str = "en",
) -> str:
    """Turn a number into a readable currency-aware value."""
    if not compact:
        return format_price(value, currency, language)
    return format_currency(value, currency, language)


def format_percent(value: float | None, language: str = "en") -> str:
    """Format a decimal ratio such as 0.15 as 15.00%."""
    return shared_format_percent(value, language)


def format_ratio(value: float | None, language: str = "en") -> str:
    """Format a non-percentage financial ratio."""
    return shared_format_ratio(value, language)


def render_value_cards(
    items: list[tuple[str, str, str | None]],
    columns: int = 4,
) -> None:
    """Render non-truncating metric cards for numbers and ratios."""
    cards = "".join(
        '<div class="premium-card value-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        + (
            f'<div class="metric-note">{html.escape(note)}</div>'
            if note
            else ""
        )
        + "</div>"
        for label, value, note in items
    )
    st.markdown(
        f'<div class="metric-grid value-grid cols-{columns}">{cards}</div>',
        unsafe_allow_html=True,
    )


def create_price_chart(
    history: pd.DataFrame,
    company_name: str,
    currency: str | None,
    period: str,
    language: str,
) -> go.Figure:
    """Build a lightweight, high-contrast Plotly closing-price chart."""
    chart_history = history[["Close"]].dropna()
    # Long daily histories are expensive to draw on phones. Weekly closes retain
    # the useful trend while greatly reducing the number of browser data points.
    if period in {"5y", "10y", "max"}:
        chart_history = chart_history.resample("W-FRI").last().dropna()

    y_axis_title = (
        f"{text(language, 'price')} ({currency})"
        if currency
        else text(language, "price")
    )
    hover_prefix = f"{currency} " if currency else ""
    figure = go.Figure(
        go.Scatter(
            x=chart_history.index,
            y=chart_history["Close"],
            mode="lines",
            name=text(language, "closing_price"),
            line={"color": "#18181b", "width": 2.2, "simplify": True},
            hovertemplate=(
                f"%{{x|%b %d, %Y}}<br>{hover_prefix}"
                "%{y:,.2f}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title={
            "text": f"{company_name} · {text(language, 'price_history_title')}",
            "font": {"size": 17, "color": "#18181b"},
        },
        xaxis_title=text(language, "date"),
        yaxis_title=y_axis_title,
        hovermode="closest",
        height=380,
        margin={"l": 18, "r": 12, "t": 54, "b": 18},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        transition={"duration": 0},
        showlegend=False,
        font={
            "family": (
                '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", '
                '"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif'
            ),
            "color": "#3f3f46",
        },
        xaxis={
            "gridcolor": "#eeeeee",
            "zeroline": False,
            "fixedrange": True,
            "tickfont": {"color": "#52525b"},
            "title_font": {"color": "#52525b"},
        },
        yaxis={
            "gridcolor": "#eeeeee",
            "zeroline": False,
            "fixedrange": True,
            "tickfont": {"color": "#52525b"},
            "title_font": {"color": "#52525b"},
        },
    )
    return figure


def render_metric_cards(
    profile: dict[str, Any],
    history: pd.DataFrame,
    risk: dict[str, float | None],
    health: dict[str, Any],
    risk_classification: dict[str, str],
    language: str,
) -> None:
    """Render four premium headline cards with a health progress bar."""
    currency = profile.get("currency")
    cards = [
        (
            text(language, "market_cap"),
            format_money(profile.get("market_cap"), currency, language=language),
            text(language, "reported_yahoo"),
        ),
        (
            text(language, "latest_close"),
            format_money(
                float(history["Close"].iloc[-1]),
                currency,
                compact=False,
                language=language,
            ),
            f"{text(language, 'trading_currency')} · "
            f"{currency or text(language, 'unavailable')}",
        ),
        (
            text(language, "period_return"),
            format_percent(risk.get("period_return"), language),
            text(language, "adjusted_close"),
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
        f'<div class="health-row"><div class="metric-label">'
        f'{html.escape(text(language, "health_score"))}</div>'
        f'<span class="risk-pill {risk_classification["css_class"]}">'
        f'{html.escape(risk_label(language, risk_classification["label"]))}</span></div>'
        f'<div class="metric-value">{score}'
        f'<span style="font-size:.9rem;color:#8a8e96"> / 100</span></div>'
        f'<div class="score-track"><div class="score-fill" style="width:{score}%">'
        f'</div></div><div class="metric-note">'
        f'{html.escape(text(language, "transparent_score"))}</div>'
        f'</div>'
    )
    st.markdown(
        f'<div class="metric-grid">{card_html}{health_card}</div>',
        unsafe_allow_html=True,
    )


def localize_trend(trend: str, language: str) -> str:
    """Translate the transparent recent-trend label."""
    trend_key = {
        "Upward": "upward",
        "Downward": "downward",
        "Sideways": "sideways",
    }.get(trend, "unknown")
    return text(language, trend_key)


def build_investor_action_plan(
    outlook: dict[str, Any],
    language: str,
) -> list[str]:
    """Build educational volatility guidance without trading recommendations."""
    volatility_level = outlook.get("volatility_level")
    drawdown = outlook.get("maximum_drawdown")
    position = outlook.get("current_price_position")
    trend = outlook.get("recent_trend")

    if language == "zh":
        items: list[str] = []
        if volatility_level == "High":
            items.append("如果波动性继续较高，投资者需要更强的风险承受能力，并关注回撤风险和新闻催化因素。")
            items.append("从教育研究角度看，仓位大小、资金期限和风险预算需要与历史波动特征相匹配。")
        elif volatility_level == "Moderate":
            items.append("当前波动性处于中等区间，投资者可以继续跟踪趋势、盈利、利润率、现金流和宏观因素。")
            items.append("价格波动仍可能快速变化，因此应把市场表现与基本面变化一起观察。")
        elif volatility_level == "Low":
            items.append("历史波动性相对较低，但投资者仍应关注估值、基本面、行业风险和突发消息。")
        else:
            items.append("当前价格数据不足，投资者可以先补充更长周期数据后再评估波动特征。")

        if drawdown is not None and drawdown <= -0.25:
            items.append("历史最大回撤较明显，说明该股票曾出现较大阶段性下行压力；过去回撤不保证未来重复，但能反映风险行为。")
        if position is not None and position >= 0.80:
            items.append("当前价格接近所选区间高位，投资者可以关注基本面是否支持这一价格区间及估值敏感性。")
        elif position is not None and position <= 0.20:
            items.append("当前价格接近所选区间低位，投资者可以观察盈利、现金流、行业情绪和修复信号。")
        if trend == "Upward":
            items.append("近期趋势偏上行，说明动能较强；这不代表趋势一定延续。")
        elif trend == "Downward":
            items.append("近期趋势偏下行，投资者可以重点观察风险信号和市场情绪变化。")
        elif trend == "Sideways":
            items.append("近期走势偏横盘，投资者可以关注财报、新闻或行业因素是否改变波动区间。")
        return items

    items = []
    if volatility_level == "High":
        items.append(
            "If volatility remains high, investors may need stronger risk tolerance and closer monitoring of drawdown risk and news catalysts."
        )
        items.append(
            "From an educational research perspective, position size, time horizon, and risk budget should be considered alongside historical volatility."
        )
    elif volatility_level == "Moderate":
        items.append(
            "With moderate historical volatility, investors may want to monitor trend, earnings, margins, cash flow, and macro factors together."
        )
        items.append(
            "Price behavior can still change quickly, so market movement should be compared with changes in fundamentals."
        )
    elif volatility_level == "Low":
        items.append(
            "Lower historical volatility suggests relative price stability, but fundamentals, valuation, sector risk, and news still require monitoring."
        )
    else:
        items.append(
            "Price data is limited, so investors may want a longer data window before relying on volatility behavior."
        )

    if drawdown is not None and drawdown <= -0.25:
        items.append(
            "The historical maximum drawdown was meaningful; past drawdown does not guarantee future drawdown, but it shows how the stock has behaved under pressure."
        )
    if position is not None and position >= 0.80:
        items.append(
            "The latest close is near the selected-period high, so investors may monitor whether fundamentals support the current price range and valuation sensitivity."
        )
    elif position is not None and position <= 0.20:
        items.append(
            "The latest close is near the selected-period low, so investors may monitor recovery signals, profitability, cash flow, and sector sentiment."
        )
    if trend == "Upward":
        items.append("Recent trend is upward, indicating positive momentum; this does not imply continuation.")
    elif trend == "Downward":
        items.append("Recent trend is downward, so investors may pay closer attention to risk signals and market sentiment.")
    elif trend == "Sideways":
        items.append("Recent trend is sideways, so investors may monitor earnings, news, or sector catalysts that could change the range.")
    return items


def build_scenarios(language: str) -> list[tuple[str, str]]:
    """Return educational forward-looking scenarios, not price forecasts."""
    if language == "zh":
        return [
            (
                text(language, "base_case"),
                "假设波动性维持在近期历史水平附近。投资者可以继续关注基本面、盈利表现、利润率、现金流和市场情绪。",
            ),
            (
                text(language, "bullish_scenario"),
                "如果盈利改善、利润率提升、积极新闻增加、行业情绪转好或宏观环境改善，可能有助于缓解下行压力。但这不代表股价一定上涨。",
            ),
            (
                text(language, "bearish_scenario"),
                "如果盈利走弱、利润率承压、利率上升、监管风险增加、需求疲弱或负面新闻出现，可能提高波动性和回撤风险。但这不代表股价一定下跌。",
            ),
        ]
    return [
        (
            text(language, "base_case"),
            "Assumes volatility remains near its recent historical level. Investors may monitor fundamentals, earnings, margins, cash flow, and market sentiment.",
        ),
        (
            text(language, "bullish_scenario"),
            "Stronger earnings, improved margins, positive news, better sector sentiment, or supportive macro conditions could reduce downside pressure. This should not be presented as a guaranteed price increase.",
        ),
        (
            text(language, "bearish_scenario"),
            "Weak earnings, margin pressure, higher interest rates, regulatory risks, weak demand, or negative news could increase volatility and drawdown risk. This should not be presented as a guaranteed decline.",
        ),
    ]


def render_volatility_outlook(
    outlook: dict[str, Any],
    currency: str | None,
    language: str,
) -> None:
    """Render volatility metrics, action guidance, and scenarios."""
    level = str(outlook.get("volatility_level") or "Unknown")
    volatility_items = [
        (
            text(language, "annualized_volatility"),
            format_percent(outlook.get("annualized_volatility"), language),
            text(language, "volatility_note"),
        ),
        (
            text(language, "maximum_drawdown"),
            format_percent(outlook.get("maximum_drawdown"), language),
            None,
        ),
        (
            text(language, "current_price_position"),
            format_percent(outlook.get("current_price_position"), language),
            None,
        ),
        (
            text(language, "recent_trend"),
            localize_trend(str(outlook.get("recent_trend")), language),
            None,
        ),
        (
            text(language, "volatility_level"),
            risk_label(language, level),
            None,
        ),
    ]
    render_value_cards(volatility_items, columns=5)
    st.caption(text(language, "volatility_note"))

    st.markdown(f"### {text(language, 'investor_action_plan')}")
    for item in build_investor_action_plan(outlook, language):
        st.markdown(f"- {item}")

    st.markdown(f"### {text(language, 'forward_looking_scenarios')}")
    for heading, body in build_scenarios(language):
        st.markdown(f"**{heading}**  \n{body}")


def render_risk_cards(risk_breakdown: list[dict[str, str]]) -> None:
    """Display the transparent risk breakdown in compact cards."""
    cards = []
    for item in risk_breakdown:
        css_level = html.escape(item.get("css_level", item["level"]))
        level = html.escape(item["level"])
        cards.append(
            f'<div class="risk-card">'
            f'<span class="level-pill {css_level}">{level}</span>'
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
    language: str,
) -> None:
    """Show only real Yahoo headlines, with transparent keyword sentiment."""
    english_label = str(sentiment.get("label", "Neutral"))
    label = html.escape(english_label)
    localized_label = html.escape(sentiment_label(language, english_label))
    st.markdown(
        f"""
        <div class="section-card">
            <div class="eyebrow">{html.escape(text(language, "headline_pulse"))}</div>
            <h3 style="margin:.45rem 0 .5rem">{html.escape(text(language, "market_sentiment"))}
                <span class="sentiment-pill {label}">{localized_label}</span>
            </h3>
            <p style="color:#737780;margin:0;line-height:1.6">
                {html.escape(text(language, "sentiment_note"))}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not news:
        st.info(text(language, "news_unavailable"))
        return

    cards = []
    for article in news:
        title = html.escape(article.get("title") or "Untitled")
        publisher = html.escape(
            article.get("publisher") or text(language, "publisher_unavailable")
        )
        date = html.escape(
            article.get("published_date") or text(language, "date_unavailable")
        )
        item_label = label_headline_sentiment(article.get("title") or "")
        item_label_display = sentiment_label(language, item_label)
        safe_url = article.get("link")
        linked_title = title
        if safe_url and safe_url.startswith(("https://", "http://")):
            linked_title = (
                f'<a href="{html.escape(safe_url, quote=True)}" target="_blank" '
                f'rel="noopener noreferrer">{title}</a>'
            )
        cards.append(
            f'<div class="news-card">'
            f'<span class="sentiment-pill {item_label}">'
            f'{html.escape(item_label_display)}</span>'
            f'<h4>{linked_title}</h4>'
            f'<p>{publisher} · {date}</p>'
            f'</div>'
        )
    st.markdown(
        f'<div class="news-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(text(language, "headlines_source"))


HEALTH_EXPLANATIONS_ZH = {
    "Profitability data unavailable: no score change.": "盈利能力数据缺失：评分不变。",
    "Strong net profit margin: +15.": "净利润率较强：+15。",
    "Positive net profit margin: +8.": "净利润率为正：+8。",
    "Negative net profit margin: -15.": "净利润率为负：-15。",
    "Leverage data unavailable: no score change.": "杠杆数据缺失：评分不变。",
    "Low debt relative to assets: +12.": "债务相对总资产较低：+12。",
    "Moderate debt relative to assets: +4.": "债务相对总资产处于中等水平：+4。",
    "High debt relative to assets: -12.": "债务相对总资产较高：-12。",
    "Revenue growth data unavailable: no score change.": "营收增长数据缺失：评分不变。",
    "Revenue growth of at least 10%: +12.": "营收增长至少 10%：+12。",
    "Revenue is stable or growing: +5.": "营业收入稳定或增长：+5。",
    "Revenue declined year over year: -10.": "营业收入同比下降：-10。",
    "Operating cash-flow data unavailable: no score change.": "经营现金流数据缺失：评分不变。",
    "Positive operating cash flow: +8.": "经营现金流为正：+8。",
    "Negative operating cash flow: -8.": "经营现金流为负：-8。",
    "Positive stock return over the selected period: +3.": "所选周期股票收益为正：+3。",
    "Negative stock return over the selected period: -3.": "所选周期股票收益为负：-3。",
}


def translate_health_explanation(explanation: str, language: str) -> str:
    """Translate deterministic score explanations for the Chinese interface."""
    if language == "zh":
        return HEALTH_EXPLANATIONS_ZH.get(explanation, explanation)
    return explanation


def show_dashboard(ticker: str, period: str, language: str) -> None:
    """Load data, calculate research signals, and render the full dashboard."""
    profile, history, financials, news = load_stock_data(ticker, period)
    ratios = calculate_financial_ratios(financials)
    risk = analyze_risk(history, profile.get("beta"))
    volatility_outlook = build_volatility_outlook(history)
    risk.update(volatility_outlook)
    health = calculate_financial_health_score(ratios, financials, history)
    risk_classification = classify_risk_level(int(health["score"]))
    risk_breakdown = translate_risk_breakdown(
        build_risk_breakdown(ratios, risk, profile), language
    )
    sentiment = analyze_news_sentiment(news)
    sentiment["localized_label"] = sentiment_label(
        language, str(sentiment.get("label", "Neutral"))
    )
    localized_risk_level = risk_label(language, risk_classification["label"])

    template_report = generate_research_report(
        ticker=ticker,
        profile=profile,
        history=history,
        financials=financials,
        ratios=ratios,
        risk=risk,
        health=health,
        risk_level=localized_risk_level,
        risk_breakdown=risk_breakdown,
        news=news,
        news_sentiment=sentiment,
        language=language,
    )
    report_markdown = report_to_markdown(template_report)
    report_source = text(language, "template_source")
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
                risk_level=localized_risk_level,
                risk_breakdown=risk_breakdown,
                news=news,
                news_sentiment=sentiment,
                language=language,
            )
            report_source = (
                f"{text(language, 'ai_source')} · "
                f"{os.getenv('OPENAI_MODEL', 'gpt-5.5')}"
            )
        except AIReportError:
            ai_error = text(language, "ai_fallback")

    currency = profile.get("currency")
    financial_currency = profile.get("financial_currency") or currency
    company_name = profile["company_name"]

    st.markdown(
        f"""
        <section class="result-header">
            <div class="eyebrow">{html.escape(text(language, "research_workspace"))}
                · {html.escape(ticker)}</div>
            <h2>{html.escape(company_name)}</h2>
            <p>{html.escape(str(profile['sector']))} &nbsp;·&nbsp;
               {html.escape(str(profile['industry']))} &nbsp;·&nbsp;
               {html.escape(str(profile['country']))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(
        profile, history, risk, health, risk_classification, language
    )
    st.plotly_chart(
        create_price_chart(history, company_name, currency, period, language),
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
            "scrollZoom": False,
            "staticPlot": False,
        },
    )
    chart_summary_items = [
        (
            text(language, "start_price"),
            format_price(volatility_outlook.get("starting_price"), currency, language),
            None,
        ),
        (
            text(language, "latest_close"),
            format_price(volatility_outlook.get("latest_price"), currency, language),
            None,
        ),
        (
            text(language, "period_return"),
            format_percent(volatility_outlook.get("period_return"), language),
            None,
        ),
        (
            text(language, "highest_price"),
            format_price(volatility_outlook.get("period_high"), currency, language),
            None,
        ),
        (
            text(language, "lowest_price"),
            format_price(volatility_outlook.get("period_low"), currency, language),
            None,
        ),
    ]
    render_value_cards(chart_summary_items, columns=5)

    overview_tab, financial_tab, risk_tab, volatility_tab, news_tab, report_tab = st.tabs(
        [
            text(language, "overview"),
            text(language, "financials"),
            text(language, "risk_analysis"),
            text(language, "volatility_outlook"),
            text(language, "news"),
            text(language, "research_report"),
        ]
    )

    with overview_tab:
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown(f"### {text(language, 'company_overview')}")
            st.markdown(
                f"""
                **{text(language, 'ticker')}:** {ticker}  
                **{text(language, 'exchange')}:** {profile['exchange']}  
                **{text(language, 'sector')}:** {profile['sector']}  
                **{text(language, 'industry')}:** {profile['industry']}  
                **{text(language, 'country')}:** {profile['country']}  
                **{text(language, 'trading_currency')}:** {currency or text(language, 'unavailable')}
                """
            )
            website = profile.get("website")
            if website and str(website).startswith(("http://", "https://")):
                st.link_button(text(language, "visit_website"), str(website))
        with right:
            st.markdown(f"### {text(language, 'business_model')}")
            st.write(profile["business_summary"])
            st.caption(text(language, "summary_source"))

    with financial_tab:
        st.markdown(f"### {text(language, 'annual_snapshot')}")
        values = [
            (
                text(language, "revenue"),
                format_money(
                    financials.get("revenue"),
                    financial_currency,
                    language=language,
                ),
            ),
            (
                text(language, "net_income"),
                format_money(
                    financials.get("net_income"),
                    financial_currency,
                    language=language,
                ),
            ),
            (
                text(language, "total_assets"),
                format_money(
                    financials.get("total_assets"),
                    financial_currency,
                    language=language,
                ),
            ),
            (
                text(language, "total_debt"),
                format_money(
                    financials.get("total_debt"),
                    financial_currency,
                    language=language,
                ),
            ),
            (
                text(language, "operating_cash_flow"),
                format_money(
                    financials.get("operating_cash_flow"),
                    financial_currency,
                    language=language,
                ),
            ),
        ]
        render_value_cards([(label, value, None) for label, value in values], columns=5)

        st.markdown(f"### {text(language, 'key_financial_ratios')}")
        ratio_values = [
            (
                text(language, "net_margin"),
                format_percent(ratios.get("net_profit_margin"), language),
            ),
            (
                text(language, "debt_assets"),
                format_percent(ratios.get("debt_to_assets"), language),
            ),
            (
                text(language, "roe"),
                format_percent(ratios.get("return_on_equity"), language),
            ),
            (
                text(language, "current_ratio"),
                format_ratio(ratios.get("current_ratio"), language),
            ),
            (
                text(language, "revenue_growth"),
                format_percent(ratios.get("revenue_growth"), language),
            ),
        ]
        render_value_cards([(label, value, None) for label, value in ratio_values], columns=5)

        with st.expander(text(language, "ratio_help"), expanded=True):
            st.markdown(text(language, "ratio_help_text"))

        st.markdown(f"### {text(language, 'score_explanation')}")
        st.progress(int(health["score"]) / 100)
        st.caption(
            f"{health['score']}/100 · {localized_risk_level} "
            f"{text(language, 'screening_classification')}"
        )
        for explanation in health["explanations"]:
            st.write(f"• {translate_health_explanation(explanation, language)}")

    with risk_tab:
        st.markdown(
            f"""
            <h3 style="margin-bottom:.35rem">{html.escape(text(language, "risk_profile"))}
                <span class="risk-pill {risk_classification['css_class']}">
                    {html.escape(localized_risk_level)}
                </span>
            </h3>
            """,
            unsafe_allow_html=True,
        )
        st.caption(text(language, "risk_note"))
        render_risk_cards(risk_breakdown)

        render_value_cards(
            [
                (
                    text(language, "volatility"),
                    format_percent(risk.get("annualized_volatility"), language),
                    None,
                ),
                (
                    text(language, "maximum_drawdown"),
                    format_percent(risk.get("maximum_drawdown"), language),
                    None,
                ),
                (
                    text(language, "beta"),
                    format_ratio(risk.get("beta"), language),
                    None,
                ),
                (
                    text(language, "period_return"),
                    format_percent(risk.get("period_return"), language),
                    None,
                ),
            ],
            columns=4,
        )

        st.markdown(f"### {text(language, 'investor_watchlist')}")
        for index, item in enumerate(
            build_investor_watchlist(profile, ratios, language=language), start=1
        ):
            st.markdown(f"**{index}.** {item}")

    with volatility_tab:
        st.markdown(f"### {text(language, 'volatility_outlook')}")
        render_volatility_outlook(volatility_outlook, currency, language)

    with news_tab:
        render_news(news, sentiment, language)

    with report_tab:
        st.caption(report_source)
        if ai_error:
            st.info(ai_error)
        with st.container(border=True, key="report_article"):
            st.markdown(report_markdown.replace("$", "&#36;"))
        st.download_button(
            text(language, "download_full_report"),
            data=report_markdown,
            file_name=f"finsight_ai_report_{ticker}_{language}.md",
            mime="text/markdown",
            width="stretch",
            on_click="ignore",
        )


if "language_choice" not in st.session_state:
    st.session_state.language_choice = "English"

language_column_left, language_column = st.columns([5, 1.35])
with language_column:
    selected_language = st.selectbox(
        "Language / 语言",
        ["English", "中文"],
        key="language_choice",
    )

language = "zh" if selected_language == "中文" else "en"

if language == "zh":
    st.markdown(
        """
        <style>
        .hero-zh .student-badge,
        .hero-zh .hero-subtitle,
        .metric-label,
        .eyebrow,
        [data-testid="stForm"] label {
            letter-spacing: 0 !important;
            text-transform: none !important;
        }

        .hero-zh .hero-title { letter-spacing: -0.035em; }
        .hero-zh .hero-subtitle { line-height: 1.25; font-weight: 600; }

        .st-key-report_article p,
        .st-key-report_article li {
            line-height: 1.75 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <section class="hero {'hero-zh' if language == 'zh' else 'hero-en'}">
        <div class="student-badge">{html.escape(text(language, "student_badge"))}</div>
        <h1 class="hero-title">FinSight AI</h1>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.form("ticker_form"):
    input_column, period_column, button_column = st.columns(
        [1, 1, 1], gap="medium", vertical_alignment="bottom"
    )
    with input_column:
        ticker_input = st.text_input(
            text(language, "stock_ticker"),
            value=st.session_state.get("last_ticker", "AAPL"),
            placeholder=text(language, "ticker_placeholder"),
        )
    with period_column:
        period = st.selectbox(
            text(language, "price_history"),
            ["1y", "2y", "5y", "10y", "max"],
            index=2,
            format_func=lambda value: {
                "1y": text(language, "one_year"),
                "2y": text(language, "two_years"),
                "5y": text(language, "five_years"),
                "10y": text(language, "ten_years"),
                "max": text(language, "maximum"),
            }[value],
        )
    with button_column:
        submitted = st.form_submit_button(
            text(language, "generate_research"), width="stretch", type="primary"
        )

if submitted:
    cleaned_ticker = ticker_input.strip().upper()
    if not cleaned_ticker:
        st.warning(text(language, "enter_ticker"))
    elif len(cleaned_ticker) > 15:
        st.error(text(language, "ticker_too_long"))
    else:
        st.session_state.last_ticker = cleaned_ticker
        st.session_state.last_period = period
        st.session_state.has_research = True

if st.session_state.get("has_research"):
    try:
        with st.spinner(text(language, "analyzing")):
            show_dashboard(
                st.session_state.last_ticker,
                st.session_state.last_period,
                language,
            )
    except StockDataError as error:
        if language == "zh":
            st.error(text(language, "request_error"))
        else:
            st.error(str(error))
    except Exception:
        st.error(text(language, "request_error"))

st.markdown(
    f'<div class="footer-note">FinSight AI | '
    f'{html.escape(text(language, "student_badge"))} | '
    f'{html.escape(text(language, "educational_use"))}</div>',
    unsafe_allow_html=True,
)
