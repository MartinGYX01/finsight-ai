"""Detailed template-based research report generation for FinSight AI."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Mapping

import pandas as pd


DISCLAIMER = (
    "This report is generated for educational purposes only and does not "
    "constitute financial advice."
)
DISCLAIMER_ZH = "本报告仅用于教育和学习目的，不构成任何投资建议。"


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
    language: str = "en",
) -> list[str]:
    """Return five practical monitoring items tailored where possible."""
    sector = str(profile.get("sector") or "")
    if language == "zh":
        watchlist = [
            "跟踪年度和季度营收增长，观察需求是在加速还是放缓。",
            "关注净利润率，以评估定价能力、成本压力和经营效率。",
            "比较经营现金流与净利润，判断已报告盈利的质量。",
            "关注资产负债比率和短期流动性，观察资产负债表韧性的变化。",
        ]
        if "Financial" in sector:
            watchlist.append("关注利率、信贷质量、贷款增长及监管资本要求。")
        elif profile.get("currency") and profile.get("currency") != "USD":
            watchlist.append(
                f"关注 {profile.get('currency')} 汇率敞口及"
                f"{profile.get('country') or '公司本土市场'}的经济环境。"
            )
        else:
            watchlist.append("关注竞争压力、产品需求、监管变化及管理层指引。")
        return watchlist

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


def _percent_zh(value: float | None) -> str:
    """Format an optional percentage for the Chinese fallback report."""
    return f"{value:.1%}" if value is not None else "暂无数据"


def _number_zh(value: float | None) -> str:
    """Format an optional ratio for the Chinese fallback report."""
    return f"{value:.2f}" if value is not None else "暂无数据"


def _money_zh(value: float | None, currency: str | None = None) -> str:
    """Format money without changing the source currency or value."""
    if value is None:
        return "暂无数据"
    prefix = f"{currency} " if currency else ""
    absolute_value = abs(value)
    if absolute_value >= 1_000_000_000_000:
        return f"{prefix}{value / 1_000_000_000_000:,.2f} 万亿"
    if absolute_value >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:,.1f} 十亿"
    if absolute_value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:,.1f} 百万"
    return f"{prefix}{value:,.0f}"


def _price_zh(value: float | None, currency: str | None = None) -> str:
    """Format a stock price for the Chinese fallback report."""
    if value is None:
        return "暂无数据"
    prefix = f"{currency} " if currency else ""
    return f"{prefix}{value:,.2f}"


def _performance_label_zh(
    margin: float | None,
    growth: float | None,
    cash_flow: float | None,
) -> str:
    """Describe the available financial signals in simplified Chinese."""
    signals = [
        value
        for value in (
            margin > 0 if margin is not None else None,
            growth > 0 if growth is not None else None,
            cash_flow > 0 if cash_flow is not None else None,
        )
        if value is not None
    ]
    if not signals:
        return "由于关键数据缺失，暂不明确"
    positives = sum(signals)
    if positives == len(signals):
        return "在现有指标中整体较强"
    if positives >= max(1, len(signals) // 2):
        return "整体中等，积极与谨慎信号并存"
    return "在多项现有指标中偏弱"


def _business_model_zh(profile: Mapping[str, Any]) -> str:
    """Create a data-grounded Chinese business-model description."""
    sector = str(profile.get("sector") or "").lower()
    industry = str(profile.get("industry") or "").lower()
    if "financial" in sector or "bank" in industry or "insurance" in industry:
        return (
            "公司属于金融服务型商业模式。营业收入通常可能受到贷款、手续费、"
            "投资活动、保险业务或资金成本与资产收益率差异的影响；利率、信贷质量"
            "和监管环境是重要经营变量。"
        )
    if "technology" in sector:
        return (
            "公司属于科技驱动型商业模式，营业收入可能来自技术产品、软件、服务或"
            "数字生态。创新能力、客户留存和竞争格局是重要经营变量。"
        )
    if "consumer defensive" in sector or "utilities" in sector or "healthcare" in sector:
        return (
            "公司业务相对偏防御型，需求可能比高度可选消费行业更稳定，但定价、监管、"
            "投入成本和执行能力仍会影响经营表现。"
        )
    if "consumer cyclical" in sector or "industrials" in sector or "materials" in sector:
        return (
            "公司业务具有一定周期性，营业收入可能随消费需求、资本开支、原材料成本"
            "或整体经济周期变化。"
        )
    if "energy" in sector:
        return (
            "公司业务具有周期性和重资产特征，营业收入与现金流可能受到商品价格、"
            "产量、资本投入和监管变化影响。"
        )
    return (
        "公司的商业模式与所属行业密切相关。当前免费数据源未提供经过核实的分部"
        "营业收入表，因此本报告不对各产品或业务部门的收入贡献作精确判断。"
    )


def _valuation_view_zh(profile: Mapping[str, Any]) -> str:
    """Explain available P/E measures in simplified Chinese."""
    trailing_pe = profile.get("trailing_pe")
    forward_pe = profile.get("forward_pe")
    if trailing_pe is None and forward_pe is None:
        return "当前免费数据源未提供可靠的市盈率指标，因此本报告不作估值判断。"
    values = []
    if trailing_pe is not None:
        values.append(f"历史市盈率为 {trailing_pe:.1f}")
    if forward_pe is not None:
        values.append(f"预期市盈率为 {forward_pe:.1f}")
    reference_pe = forward_pe if forward_pe is not None else trailing_pe
    if reference_pe is not None and reference_pe > 35:
        interpretation = "该盈利倍数相对较高，未来增长和执行能力的重要性更为突出。"
    elif reference_pe is not None and reference_pe > 0:
        interpretation = "应结合公司历史、同业、增长率和利率环境进行比较。"
    else:
        interpretation = "非正数市盈率可能反映亏损或异常盈利，不宜单独作为估值信号。"
    return f"Yahoo Finance 显示，{'，'.join(values)}。{interpretation}"


def _generate_chinese_report(
    ticker: str,
    profile: Mapping[str, Any],
    financials: Mapping[str, float | None],
    ratios: Mapping[str, float | None],
    risk: Mapping[str, float | None],
    health: Mapping[str, Any],
    risk_level: str,
    risk_breakdown: list[Mapping[str, str]],
    news: list[Mapping[str, str | None]],
    news_sentiment: Mapping[str, Any],
) -> OrderedDict[str, str]:
    """Create a complete simplified-Chinese report without using OpenAI."""
    company_name = str(profile.get("company_name") or ticker)
    trading_currency = profile.get("currency")
    financial_currency = profile.get("financial_currency") or trading_currency
    margin = ratios.get("net_profit_margin")
    growth = ratios.get("revenue_growth")
    cash_flow = financials.get("operating_cash_flow")
    performance = _performance_label_zh(margin, growth, cash_flow)
    period_return = risk.get("period_return")

    if period_return is None:
        price_view = "所选周期的股价表现暂无数据。"
    elif period_return > 0.10:
        price_view = "所选周期内股价呈现较明显的正增长。"
    elif period_return < -0.10:
        price_view = "所选周期内股价表现明显偏弱。"
    else:
        price_view = "所选周期内股价方向性变化相对有限。"

    executive_summary = (
        f"{company_name}（{ticker}）属于 {profile.get('sector', 'N/A')} 板块的"
        f"{profile.get('industry', 'N/A')}公司。根据现有公司资料，其商业模式与所属行业"
        f"特征密切相关。现有财务指标显示，公司财务表现{performance}。所选周期收益率为"
        f"{_percent_zh(period_return)}，历史年化波动性为"
        f"{_percent_zh(risk.get('annualized_volatility'))}。FinSight 的透明财务健康评分为"
        f"{health['score']}/100，对应界面中的“{risk_level}”分类。从教育研究角度看，"
        "应综合考虑经营质量、估值、市场表现及免费数据的局限，形成平衡判断。"
    )

    company_overview = (
        f"**公司：** {company_name}  \n"
        f"**股票代码：** {ticker}  \n"
        f"**板块：** {profile.get('sector', 'N/A')}  \n"
        f"**行业：** {profile.get('industry', 'N/A')}  \n"
        f"**国家或地区：** {profile.get('country', 'N/A')}  \n"
        f"**交易所：** {profile.get('exchange', 'N/A')}  \n"
        f"**市值：** {_money_zh(profile.get('market_cap'), trading_currency)}\n\n"
        "以上公司资料来自当前免费数据源；公司名称、股票代码、货币和数值均按原始数据保留。"
    )

    stock_performance = (
        f"复权收盘价在所选周期内由 **{_price_zh(risk.get('starting_price'), trading_currency)}** "
        f"变为 **{_price_zh(risk.get('latest_price'), trading_currency)}**，区间收益率为 "
        f"**{_percent_zh(period_return)}**。{price_view}历史年化波动性为"
        f"{_percent_zh(risk.get('annualized_volatility'))}，周期内最大回撤为"
        f"{_percent_zh(risk.get('maximum_drawdown'))}。这些数据仅反映历史表现，不代表未来走势。"
    )

    financial_performance = (
        f"最新可用年度营业收入为 **{_money_zh(financials.get('revenue'), financial_currency)}**，"
        f"净利润为 **{_money_zh(financials.get('net_income'), financial_currency)}**。"
        f"净利润率为 {_percent_zh(margin)}，营收增长率为 {_percent_zh(growth)}，"
        f"经营现金流为 {_money_zh(cash_flow, financial_currency)}。\n\n"
        f"综合现有数据，财务表现{performance}。该判断采用简化规则，仍应结合多年财务报表、"
        "一次性项目和公司管理层指引进一步核实。"
    )

    ratio_analysis = (
        f"- **净利润率 — {_percent_zh(margin)}：**反映营业收入中最终转化为净利润的比例，"
        "但合理水平需结合行业比较。\n"
        f"- **资产负债比率 — {_percent_zh(ratios.get('debt_to_assets'))}：**反映总资产中"
        "由债务融资的比例，较高水平可能增加对利率和经营压力的敏感度。\n"
        f"- **股本回报率 / ROE — {_percent_zh(ratios.get('return_on_equity'))}：**衡量净利润"
        "相对于股东权益的水平，但较高杠杆也可能推高该比率。\n"
        f"- **流动比率 — {_number_zh(ratios.get('current_ratio'))}：**比较流动资产与流动负债，"
        "是基础的短期流动性指标，对银行等金融企业的解释力可能较弱。\n"
        f"- **营收增长率 — {_percent_zh(growth)}：**反映最新年度营业收入变化，单一年度"
        "仅是一个阶段性快照。"
    )

    risk_lines = [
        f"- **{item['name']} — {item['level']}：**{item['explanation']}"
        for item in risk_breakdown
    ]
    risk_analysis = (
        f"综合界面分类为 **{risk_level}**，对应 {health['score']}/100 的健康评分。"
        "该标签仅用于初步筛选，并不代表亏损概率。\n\n"
        + "\n".join(risk_lines)
        + "\n\n"
        + _valuation_view_zh(profile)
    )

    if news:
        headline_lines = []
        for article in news[:6]:
            metadata = " · ".join(
                part
                for part in [article.get("publisher"), article.get("published_date")]
                if part
            )
            headline_lines.append(
                f"- **{article.get('title')}**" + (f" — {metadata}" if metadata else "")
            )
        news_text = (
            f"基于规则的新闻标题情绪分类为 **{news_sentiment.get('localized_label', '中性')}**。"
            "该分类仅使用标题中的简单关键词，并未分析新闻全文。\n\n"
            + "\n".join(headline_lines)
        )
    else:
        news_text = "当前免费数据源暂未提供相关新闻数据。"

    bullish_factors = []
    if margin is not None and margin > 0:
        bullish_factors.append(f"年度盈利为正，净利润率为 {_percent_zh(margin)}。")
    if growth is not None and growth > 0:
        bullish_factors.append(f"最新年度营业收入同比增长 {_percent_zh(growth)}。")
    if cash_flow is not None and cash_flow > 0:
        bullish_factors.append("最新已报告经营现金流为正。")
    if ratios.get("debt_to_assets") is not None and ratios["debt_to_assets"] < 0.30:
        bullish_factors.append("已报告债务低于总资产的 30%。")
    if period_return is not None and period_return > 0:
        bullish_factors.append("所选周期内股价取得正收益。")
    while len(bullish_factors) < 3:
        bullish_factors.append("仍需更多当前免费数据源未提供的信息来确认积极因素。")

    bearish_factors = []
    if margin is not None and margin <= 0:
        bearish_factors.append("最新年度净利润相对于营业收入并非正数。")
    if growth is not None and growth < 0:
        bearish_factors.append(f"最新年度营业收入同比下降 {_percent_zh(abs(growth))}。")
    if cash_flow is not None and cash_flow <= 0:
        bearish_factors.append("最新已报告经营现金流为负。")
    if ratios.get("debt_to_assets") is not None and ratios["debt_to_assets"] > 0.60:
        bearish_factors.append("已报告债务超过总资产的 60%。")
    if risk.get("annualized_volatility") is not None and risk["annualized_volatility"] > 0.30:
        bearish_factors.append(
            f"历史年化波动性较高，达到 {_percent_zh(risk['annualized_volatility'])}。"
        )
    general_cautions = [
        "竞争、监管和市场环境变化仍是一般性经营风险。",
        "免费数据源并不完整，因此风险判断仍存在信息局限。",
        "单一周期的市场和财务数据不足以确认长期趋势。",
    ]
    for caution in general_cautions:
        if len(bearish_factors) >= 3:
            break
        bearish_factors.append(caution)

    watchlist = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(
            build_investor_watchlist(profile, ratios, language="zh"), start=1
        )
    )
    suitability = (
        f"基于“{risk_level}”分类及 {_percent_zh(risk.get('annualized_volatility'))} 的历史"
        "年化波动性，该股票的风险特征更适合能够承受相应价格波动的研究者进一步分析。"
        "成长型、收益型、价值型或保守型投资者是否适配，仍取决于个人目标、风险承受能力"
        "及对公司更深入的独立研究，本报告不作个性化建议。"
    )

    return OrderedDict(
        [
            ("执行摘要", executive_summary),
            ("公司概况", company_overview),
            ("商业模式", _business_model_zh(profile)),
            ("股价表现", stock_performance),
            ("财务表现", financial_performance),
            ("关键财务比率", ratio_analysis),
            ("风险分析", risk_analysis),
            ("新闻与市场情绪", news_text),
            ("积极因素", "\n".join(f"- {item}" for item in bullish_factors[:5])),
            ("谨慎因素", "\n".join(f"- {item}" for item in bearish_factors[:5])),
            ("投资者关注事项", watchlist),
            ("投资者适配分析", suitability),
            (
                "中立观点",
                f"从教育研究角度看，{company_name} 的现有财务表现{performance}，并对应"
                f"“{risk_level}”筛选分类。公司的潜在优势需要与风险构成、估值背景、行业环境"
                "及免费数据缺口一并权衡。研究者可持续关注上述事项，并比较多年公司文件后形成"
                "独立判断。FinSight 不提供买入、卖出或持有建议。",
            ),
            ("免责声明", DISCLAIMER_ZH),
        ]
    )


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
    language: str = "en",
) -> OrderedDict[str, str]:
    """Create a detailed, data-grounded report when OpenAI is unavailable."""
    if language == "zh":
        return _generate_chinese_report(
            ticker=ticker,
            profile=profile,
            financials=financials,
            ratios=ratios,
            risk=risk,
            health=health,
            risk_level=risk_level,
            risk_breakdown=risk_breakdown,
            news=news,
            news_sentiment=news_sentiment,
        )
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
