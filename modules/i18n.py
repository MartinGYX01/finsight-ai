"""Small bilingual text helpers for the FinSight AI interface."""

from __future__ import annotations

from typing import Mapping


TRANSLATIONS = {
    "en": {
        "language": "Language / 语言",
        "student_badge": "Designed by a UCSI FinTech Student",
        "subtitle": "AI-powered financial research assistant for global stocks.",
        "description": (
            "Analyze stocks, financial performance, risks, and investor watchlists "
            "in one clean dashboard."
        ),
        "stock_ticker": "Stock ticker",
        "ticker_placeholder": "Try AAPL, 1155.KL, or 0700.HK",
        "price_history": "Price history",
        "generate_research": "Generate Research",
        "research_workspace": "Research Workspace",
        "market_cap": "Market Cap",
        "latest_close": "Latest Close",
        "period_return": "Period Return",
        "health_score": "Health Score",
        "financial_health_score": "Financial Health Score",
        "low_risk": "Low Risk",
        "moderate_risk": "Moderate Risk",
        "high_risk": "High Risk",
        "overview": "Overview",
        "financials": "Financials",
        "risk_analysis": "Risk Analysis",
        "volatility_outlook": "Volatility Outlook",
        "news": "News",
        "research_report": "Research Report",
        "company_overview": "Company Overview",
        "business_model": "Business Model",
        "financial_performance": "Financial Performance",
        "stock_performance": "Stock Performance",
        "key_financial_ratios": "Key Financial Ratios",
        "bullish_case": "Bullish Case",
        "bearish_case": "Bearish Case",
        "investor_watchlist": "Investor Watchlist",
        "suitability_analysis": "Suitability Analysis",
        "final_neutral_view": "Final Neutral View",
        "download_report": "Download Report",
        "news_unavailable": (
            "Recent news data is not available from the current free data source."
        ),
        "disclaimer": (
            "This report is generated for educational purposes only and does not "
            "constitute financial advice. Historical volatility and past performance "
            "do not guarantee future results."
        ),
        "educational_use": "Educational Use Only",
        "analyzing": "Analyzing market data and generating research report...",
        "reported_yahoo": "Reported by Yahoo Finance",
        "trading_currency": "Trading currency",
        "unavailable": "Unavailable",
        "adjusted_close": "Adjusted close · selected period",
        "transparent_score": "Transparent screening score",
        "price": "Price",
        "date": "Date",
        "closing_price": "Closing price",
        "price_history_title": "price history",
        "ticker": "Ticker",
        "exchange": "Exchange",
        "sector": "Sector",
        "industry": "Industry",
        "country": "Country",
        "visit_website": "Visit company website ↗",
        "summary_source": (
            "The summary is supplied by Yahoo Finance. Segment-level revenue data "
            "may not be available from the free source."
        ),
        "annual_snapshot": "Latest annual financial snapshot",
        "revenue": "Revenue",
        "net_income": "Net income",
        "total_assets": "Total assets",
        "total_debt": "Total debt",
        "operating_cash_flow": "Operating cash flow",
        "net_margin": "Net profit margin",
        "debt_assets": "Debt-to-assets ratio",
        "roe": "Return on equity / ROE",
        "current_ratio": "Current ratio",
        "revenue_growth": "Revenue growth",
        "ratio_help": "How to read these ratios",
        "ratio_help_text": (
            "- **Net profit margin** shows how much revenue remains as net income.\n"
            "- **Debt-to-assets ratio** shows how much of the asset base is financed by debt.\n"
            "- **Return on equity / ROE** measures net income relative to shareholder equity.\n"
            "- **Current ratio** compares short-term assets with short-term liabilities.\n"
            "- **Revenue growth** compares the latest annual revenue with the previous year.\n\n"
            "Ratios are most useful when compared with several years of history and "
            "similar companies. `N/A` means the free data source did not provide the inputs."
        ),
        "score_explanation": "Health score explanation",
        "screening_classification": "screening classification",
        "risk_profile": "Risk profile",
        "risk_note": (
            "The label follows the score bands. It is not a prediction of loss or a "
            "substitute for personal risk assessment."
        ),
        "volatility": "Volatility",
        "annualized_volatility": "Annualized Volatility",
        "maximum_drawdown": "Maximum drawdown",
        "current_price_position": "Current Price Position",
        "recent_trend": "Recent Trend",
        "volatility_level": "Volatility Level",
        "start_price": "Start Price",
        "highest_price": "Highest Price",
        "lowest_price": "Lowest Price",
        "investor_action_plan": "Investor Action Plan",
        "forward_looking_scenarios": "Forward-Looking Scenarios",
        "base_case": "Base Case",
        "bullish_scenario": "Bullish Scenario",
        "bearish_scenario": "Bearish Scenario",
        "volatility_note": (
            "Volatility analysis is based on historical price data. It should be "
            "interpreted as scenario-based risk analysis, not a guaranteed forecast."
        ),
        "upward": "Upward",
        "downward": "Downward",
        "sideways": "Sideways",
        "beta": "Beta",
        "headline_pulse": "Headline pulse",
        "market_sentiment": "Market sentiment",
        "sentiment_note": (
            "A simple keyword label based on available headlines—not full-article analysis."
        ),
        "publisher_unavailable": "Publisher unavailable",
        "date_unavailable": "Date unavailable",
        "headlines_source": (
            "Headlines, publishers, dates, and links are supplied by Yahoo Finance."
        ),
        "template_source": "Detailed template report",
        "ai_source": "AI-generated research",
        "ai_fallback": (
            "The AI report was unavailable, so FinSight preserved the full analytical "
            "template report."
        ),
        "download_full_report": "Download full research report",
        "enter_ticker": "Please enter a stock ticker.",
        "ticker_too_long": "That ticker is too long. Please check it and try again.",
        "request_error": (
            "FinSight could not complete this request. The market-data service may be "
            "temporarily unavailable, so please try again shortly."
        ),
        "one_year": "1 Year",
        "two_years": "2 Years",
        "five_years": "5 Years",
        "ten_years": "10 Years",
        "maximum": "Maximum",
        "positive": "Positive",
        "negative": "Negative",
        "mixed": "Mixed",
        "neutral": "Neutral",
        "unknown": "Unknown",
        "low": "Low",
        "moderate": "Moderate",
        "high": "High",
        "context": "Context",
    },
    "zh": {
        "language": "Language / 语言",
        "student_badge": "来自 UCSI 金融科技学生的设计",
        "subtitle": "面向全球股票的 AI 金融研究助手。",
        "description": "在一个简洁的仪表板中分析股票、财务表现、风险和投资者关注事项。",
        "stock_ticker": "股票代码",
        "ticker_placeholder": "例如 AAPL、1155.KL 或 0700.HK",
        "price_history": "股价周期",
        "generate_research": "生成研究报告",
        "research_workspace": "研究工作区",
        "market_cap": "市值",
        "latest_close": "最新收盘价",
        "period_return": "区间收益率",
        "health_score": "健康评分",
        "financial_health_score": "财务健康评分",
        "low_risk": "低风险",
        "moderate_risk": "中等风险",
        "high_risk": "高风险",
        "overview": "公司概览",
        "financials": "财务数据",
        "risk_analysis": "风险分析",
        "volatility_outlook": "波动展望",
        "news": "新闻",
        "research_report": "研究报告",
        "company_overview": "公司概况",
        "business_model": "商业模式",
        "financial_performance": "财务表现",
        "stock_performance": "股价表现",
        "key_financial_ratios": "关键财务比率",
        "bullish_case": "积极因素",
        "bearish_case": "谨慎因素",
        "investor_watchlist": "投资者关注事项",
        "suitability_analysis": "投资者适配分析",
        "final_neutral_view": "中立观点",
        "download_report": "下载报告",
        "news_unavailable": "当前免费数据源暂未提供相关新闻数据。",
        "disclaimer": "本报告仅用于教育和学习目的，不构成任何投资建议。历史波动和过去表现并不保证未来结果。",
        "educational_use": "仅供教育用途",
        "analyzing": "正在分析市场数据并生成研究报告...",
        "reported_yahoo": "数据来自 Yahoo Finance",
        "trading_currency": "交易货币",
        "unavailable": "暂无数据",
        "adjusted_close": "复权收盘价 · 所选周期",
        "transparent_score": "透明的筛选评分",
        "price": "价格",
        "date": "日期",
        "closing_price": "收盘价",
        "price_history_title": "股价走势",
        "ticker": "股票代码",
        "exchange": "交易所",
        "sector": "板块",
        "industry": "行业",
        "country": "国家或地区",
        "visit_website": "访问公司网站 ↗",
        "summary_source": "公司摘要来自 Yahoo Finance。免费数据源可能不提供分部营业收入数据。",
        "annual_snapshot": "最新年度财务概览",
        "revenue": "营业收入",
        "net_income": "净利润",
        "total_assets": "总资产",
        "total_debt": "总债务",
        "operating_cash_flow": "经营现金流",
        "net_margin": "净利润率",
        "debt_assets": "资产负债比率",
        "roe": "股本回报率 / ROE",
        "current_ratio": "流动比率",
        "revenue_growth": "营收增长率",
        "ratio_help": "如何理解这些比率",
        "ratio_help_text": (
            "- **净利润率**表示营业收入中最终转化为净利润的比例。\n"
            "- **资产负债比率**表示总资产中由债务融资的比例。\n"
            "- **股本回报率 / ROE**衡量净利润相对于股东权益的水平。\n"
            "- **流动比率**比较短期资产与短期负债。\n"
            "- **营收增长率**比较最新年度与上一年度的营业收入。\n\n"
            "财务比率应结合多年数据和同业公司进行比较。`N/A` 表示免费数据源未提供所需数据。"
        ),
        "score_explanation": "健康评分说明",
        "screening_classification": "筛选分类",
        "risk_profile": "风险概况",
        "risk_note": "该标签依据评分区间得出，并非亏损预测，也不能替代个人风险评估。",
        "volatility": "波动性",
        "annualized_volatility": "年化波动率",
        "maximum_drawdown": "最大回撤",
        "current_price_position": "当前价格位置",
        "recent_trend": "近期趋势",
        "volatility_level": "波动等级",
        "start_price": "起始价格",
        "highest_price": "区间最高价",
        "lowest_price": "区间最低价",
        "investor_action_plan": "投资者应对建议",
        "forward_looking_scenarios": "未来波动情景",
        "base_case": "基准情景",
        "bullish_scenario": "积极情景",
        "bearish_scenario": "谨慎情景",
        "volatility_note": "波动分析基于历史价格数据，应理解为情景化风险分析，而不是确定性的未来预测。",
        "upward": "上行",
        "downward": "下行",
        "sideways": "横盘",
        "beta": "贝塔系数",
        "headline_pulse": "新闻动态",
        "market_sentiment": "市场情绪",
        "sentiment_note": "根据现有新闻标题关键词作出的简单分类，并非对全文的分析。",
        "publisher_unavailable": "发布方暂无数据",
        "date_unavailable": "日期暂无数据",
        "headlines_source": "新闻标题、发布方、日期和链接由 Yahoo Finance 提供。",
        "template_source": "详细模板研究报告",
        "ai_source": "AI 生成的研究报告",
        "ai_fallback": "AI 报告暂时不可用，FinSight 已保留完整的模板分析报告。",
        "download_full_report": "下载完整研究报告",
        "enter_ticker": "请输入股票代码。",
        "ticker_too_long": "股票代码过长，请检查后重试。",
        "request_error": "FinSight 暂时无法完成此请求。市场数据服务可能暂时不可用，请稍后重试。",
        "one_year": "1 年",
        "two_years": "2 年",
        "five_years": "5 年",
        "ten_years": "10 年",
        "maximum": "最长周期",
        "positive": "积极",
        "negative": "消极",
        "mixed": "分化",
        "neutral": "中性",
        "unknown": "未知",
        "low": "低",
        "moderate": "中等",
        "high": "高",
        "context": "背景因素",
    },
}


def text(language: str, key: str) -> str:
    """Return translated UI text, falling back to English for unknown keys."""
    selected = language if language in TRANSLATIONS else "en"
    return TRANSLATIONS[selected].get(key, TRANSLATIONS["en"].get(key, key))


def risk_label(language: str, english_label: str) -> str:
    """Translate a risk classification while preserving its CSS class elsewhere."""
    key = english_label.lower().replace(" ", "_")
    return text(language, key)


def sentiment_label(language: str, english_label: str) -> str:
    """Translate the small news-sentiment label."""
    return text(language, english_label.lower())


RISK_NAMES_ZH = {
    "Profitability risk": "盈利能力风险",
    "Leverage risk": "杠杆风险",
    "Liquidity risk": "流动性风险",
    "Market volatility risk": "市场波动风险",
    "Sector & business model risk": "行业与商业模式风险",
    "Currency & country risk": "货币与国家风险",
}


RISK_EXPLANATIONS_ZH = {
    "Profitability data is unavailable.": "暂无盈利能力数据。",
    "The latest annual net profit margin is negative.": "最新年度净利润率为负。",
    "The latest margin is positive but relatively thin.": "最新利润率为正，但相对偏低。",
    "The latest annual net profit margin is positive.": "最新年度净利润率为正。",
    "Debt-to-assets data is unavailable.": "暂无资产负债比率数据。",
    "Debt represents more than 60% of reported assets.": "债务超过已报告总资产的 60%。",
    "Debt is meaningful relative to reported assets.": "债务相对于已报告总资产处于较明显水平。",
    "Debt is below 30% of reported assets.": "债务低于已报告总资产的 30%。",
    "Current assets or current liabilities are unavailable.": "暂无流动资产或流动负债数据。",
    "Current liabilities exceed reported current assets.": "已报告流动负债超过流动资产。",
    "Short-term liquidity appears adequate but not strong.": "短期流动性看似尚可，但并不充裕。",
    "Reported current assets comfortably cover current liabilities.": "已报告流动资产能够较充分地覆盖流动负债。",
    "There is not enough price data to estimate volatility.": "股价数据不足，无法估算波动性。",
    "Annualized historical volatility is above 40%.": "历史年化波动性高于 40%。",
    "Annualized historical volatility is between 25% and 40%.": "历史年化波动性介于 25% 至 40%。",
    "Annualized historical volatility is below 25%.": "历史年化波动性低于 25%。",
    "Financial businesses can be sensitive to interest rates, credit quality, and regulation.": (
        "金融企业可能对利率、信贷质量和监管变化较为敏感。"
    ),
    "Technology businesses face rapid innovation cycles and intense competition.": (
        "科技企业面临快速的创新周期和激烈竞争。"
    ),
    "Results may be sensitive to commodity prices and economic cycles.": (
        "经营表现可能对大宗商品价格和经济周期较为敏感。"
    ),
    "Demand can weaken when consumers reduce discretionary spending.": (
        "当消费者减少可选消费支出时，需求可能走弱。"
    ),
}


def translate_risk_breakdown(
    items: list[Mapping[str, str]], language: str
) -> list[dict[str, str]]:
    """Translate the deterministic risk cards without changing their meaning."""
    if language != "zh":
        return [dict(item) for item in items]

    translated = []
    for item in items:
        explanation = item["explanation"]
        if explanation.startswith("Performance can be affected by competition"):
            explanation = "公司表现可能受到所在行业竞争和环境变化的影响。"
        elif explanation.startswith("The shares trade in"):
            explanation = (
                explanation.replace("The shares trade in ", "股票以 ")
                .replace(
                    "; investors using another home currency may experience exchange-rate effects. "
                    "Country exposure is ",
                    " 交易；使用其他本位币的投资者可能面临汇率影响。国家或地区敞口为 ",
                )
                .replace(".", "。")
            )
        elif explanation.startswith("Country exposure is"):
            explanation = "公司所在国家或地区的政治、监管和经济环境仍可能影响经营表现。"
        else:
            explanation = RISK_EXPLANATIONS_ZH.get(explanation, explanation)
        translated.append(
            {
                "name": RISK_NAMES_ZH.get(item["name"], item["name"]),
                "level": text("zh", item["level"].lower()),
                "css_level": item["level"],
                "explanation": explanation,
            }
        )
    return translated
