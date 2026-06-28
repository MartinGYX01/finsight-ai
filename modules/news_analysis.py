"""Simple, transparent headline sentiment for the free-data fallback."""

from __future__ import annotations

from typing import Mapping


POSITIVE_WORDS = {
    "beat",
    "beats",
    "growth",
    "grows",
    "gain",
    "gains",
    "profit",
    "profits",
    "record",
    "strong",
    "surge",
    "upgrade",
    "upgraded",
    "outperform",
    "expands",
    "partnership",
    "approval",
}

NEGATIVE_WORDS = {
    "decline",
    "declines",
    "fall",
    "falls",
    "loss",
    "losses",
    "miss",
    "missed",
    "misses",
    "risk",
    "cuts",
    "cut",
    "downgrade",
    "downgraded",
    "lawsuit",
    "probe",
    "warning",
    "weak",
    "weaker",
    "trails",
    "recall",
}


def label_headline_sentiment(title: str) -> str:
    """Label one headline using visible keyword rules."""
    words = {
        word.strip(".,:;!?()[]{}\"'").lower()
        for word in title.split()
    }
    positive_hits = len(words & POSITIVE_WORDS)
    negative_hits = len(words & NEGATIVE_WORDS)
    if positive_hits > negative_hits:
        return "Positive"
    if negative_hits > positive_hits:
        return "Negative"
    return "Neutral"


def analyze_news_sentiment(
    news: list[Mapping[str, str | None]],
) -> dict[str, int | str]:
    """Summarize headline labels without pretending to understand full articles."""
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for article in news:
        label = label_headline_sentiment(article.get("title") or "")
        counts[label] += 1

    if counts["Positive"] and counts["Negative"]:
        overall = "Mixed"
    elif counts["Positive"] > counts["Negative"] and counts["Positive"] > counts["Neutral"]:
        overall = "Positive"
    elif counts["Negative"] > counts["Positive"] and counts["Negative"] > counts["Neutral"]:
        overall = "Negative"
    else:
        overall = "Neutral"

    return {"label": overall, **counts}
