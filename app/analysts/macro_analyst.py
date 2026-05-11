"""
Macro analyst for the Stock Analysis System.

This module performs macro analysis based on news, policies, and economic indicators.
"""
from typing import Any, Dict, List, Optional

from app.analysts.base_analyst import BaseAnalyst
from app.data.sources.sina_finance import SinaFinanceClient


class MacroAnalyst(BaseAnalyst):
    """Analyst for macro and policy analysis."""

    def __init__(self, stock_code: str, industry: str = "general"):
        """
        Initialize the macro analyst.

        Args:
            stock_code: The stock code to analyze
            industry: Industry sector (for industry-specific analysis)
        """
        super().__init__(stock_code)
        self.industry = industry
        self.sina_client = SinaFinanceClient()

    def analyze(self) -> Dict[str, Any]:
        """
        Perform macro analysis.

        Returns:
            Dictionary containing macro analysis results
        """
        try:
            # Fetch macro news
            macro_news = self.sina_client.get_macro_news(days=7)

            # Fetch industry news if specified
            industry_news = []
            if self.industry != "general":
                industry_news = self.sina_client.get_industry_news(self.industry, days=7)

            # Analyze overall macro trend
            macro_trend = self._analyze_macro_trend(macro_news)

            # Rank industry potential
            industry_rankings = self._rank_industries(macro_news, industry_news)

            # Detect high risk areas
            risk_areas = self._detect_risks(macro_news, industry_news)

            # Identify key events
            key_events = self._identify_key_events(macro_news, industry_news)

            return {
                "macro_trend": macro_trend,
                "industry_rankings": industry_rankings,
                "risk_areas": risk_areas,
                "key_events": key_events,
            }

        except Exception as e:
            return {
                "error": f"Macro analysis failed: {str(e)}",
                "stock_code": self.stock_code,
            }

    def _analyze_macro_trend(self, news_list: List[Dict]) -> str:
        """
        Analyze overall macro trend based on news sentiment.

        Args:
            news_list: List of news articles

        Returns:
            Macro trend (bullish, bearish, or neutral)
        """
        if not news_list:
            return "neutral"

        # Calculate average sentiment
        sentiment_scores = []
        for news in news_list:
            content = news.get("content", "") + " " + news.get("title", "")
            sentiment = self.sina_client.analyze_sentiment(content)
            sentiment_scores.append(sentiment)

        if not sentiment_scores:
            return "neutral"

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        # With neutral sentiment (0.0), default to neutral trend
        # When sentiment analysis is implemented, this will work properly
        if avg_sentiment > 0.3:
            return "bullish"
        elif avg_sentiment < -0.3:
            return "bearish"
        else:
            return "neutral"

    def _rank_industries(self, macro_news: List[Dict], industry_news: List[Dict]) -> List[Dict[str, Any]]:
        """
        Rank industries based on potential.

        Args:
            macro_news: Macro news articles
            industry_news: Industry-specific news articles

        Returns:
            List of industry rankings with scores and reasons
        """
        # Combine news
        all_news = macro_news + industry_news

        # Focus industries
        focus_industries = self.settings.focus_industries

        rankings = []

        for industry in focus_industries:
            # Calculate industry score based on news sentiment and keywords
            score, reason = self._calculate_industry_score(industry, all_news)

            rankings.append({
                "industry": industry,
                "score": round(score, 2),
                "reason": reason,
            })

        # Sort by score descending
        rankings.sort(key=lambda x: x["score"], reverse=True)

        return rankings

    def _calculate_industry_score(self, industry: str, news_list: List[Dict]) -> tuple[float, str]:
        """
        Calculate a score for an industry based on news.

        Args:
            industry: Industry name
            news_list: List of news articles

        Returns:
            Tuple of (score, reason)
        """
        score = 3.0  # Base score
        reasons = []

        # Industry keywords for matching
        industry_keywords = {
            "AI": ["AI", "人工智能", "machine learning", "人工智能", "chatgpt", "大模型"],
            "Robotics": ["robot", "机器人", "automation", "自动化", "manufacturing", "智能制造"],
            "Military Industry": ["defense", "军工", "military", "航空", "船舶", "导弹"],
            "Electricity & New Energy": ["energy", "能源", "solar", "光伏", "wind", "风电", "battery", "电池"],
            "Biopharmaceutical": ["pharma", "医药", "drug", "药物", "biotech", "biotechnology", "疫苗"],
        }

        keywords = industry_keywords.get(industry, [])

        if not keywords:
            return 3.0, "No specific keywords defined"

        # Analyze news for this industry
        relevant_news = []
        for news in news_list:
            content = (news.get("content", "") + " " + news.get("title", "")).lower()

            # Check if any keyword matches
            if any(keyword.lower() in content for keyword in keywords):
                relevant_news.append(news)

        # Adjust score based on relevant news
        if relevant_news:
            # Calculate average sentiment of relevant news
            sentiments = []
            for news in relevant_news:
                content = news.get("content", "") + " " + news.get("title", "")
                sentiment = self.sina_client.analyze_sentiment(content)
                sentiments.append(sentiment)

            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)

                # Adjust score based on sentiment (when implemented)
                # For now, with neutral sentiment (0.0), score remains at base level
                if abs(avg_sentiment) > 0:
                    score += avg_sentiment * 1.5

                # Limit score to 0-5 range
                score = max(0.0, min(5.0, score))

                if abs(avg_sentiment) > 0.3:
                    if avg_sentiment > 0:
                        reasons.append(f"Positive news coverage in recent period")
                    else:
                        reasons.append(f"Negative news coverage in recent period")
                else:
                    reasons.append(f"Moderate news coverage in recent period")
        else:
            reasons.append("Limited recent news coverage")

        return score, "; ".join(reasons)

    def _detect_risks(self, macro_news: List[Dict], industry_news: List[Dict]) -> List[str]:
        """
        Detect high-risk areas based on news and policies.

        Args:
            macro_news: Macro news articles
            industry_news: Industry-specific news articles

        Returns:
            List of identified risks
        """
        risks = []

        # Risk keywords
        risk_keywords = [
            "regulation", "regulatory", "监管",
            "risk", "danger", "风险",
            "crackdown", "打击",
            "investigation", "调查",
            "ban", "禁止",
            "restriction", "限制",
            "sanction", "制裁",
        ]

        all_news = macro_news + industry_news

        for news in all_news:
            content = (news.get("content", "") + " " + news.get("title", "")).lower()

            # Check for risk keywords
            if any(keyword in content for keyword in risk_keywords):
                title = news.get("title", "")
                if title not in risks:
                    risks.append(f"Regulatory concern: {title[:50]}...")

        # Limit to top 5 risks
        return risks[:5] if risks else ["No significant risks identified in recent news"]

    def _identify_key_events(self, macro_news: List[Dict], industry_news: List[Dict]) -> List[Dict[str, Any]]:
        """
        Identify key market events.

        Args:
            macro_news: Macro news articles
            industry_news: Industry-specific news articles

        Returns:
            List of key events with impact assessment
        """
        events = []

        # Look for policy-related news
        policy_keywords = [
            "policy", "政策",
            "announcement", "宣布",
            "launch", "发布",
            "reform", "改革",
            "subsidy", "补贴",
            "tax", "税收",
            "interest rate", "利率",
        ]

        all_news = macro_news + industry_news

        for news in all_news:
            content = (news.get("content", "") + " " + news.get("title", "")).lower()

            # Check for policy keywords
            if any(keyword in content for keyword in policy_keywords):
                # Assess impact
                sentiment = self.caixin_scraper.analyze_sentiment(
                    news.get("content", "") + " " + news.get("title", "")
                )

                if abs(sentiment) > 0.3:
                    # Determine impact level (1-5)
                    impact_level = min(5, int(abs(sentiment) * 5))

                    events.append({
                        "title": news.get("title", ""),
                        "date": news.get("date", ""),
                        "impact": "positive" if sentiment > 0 else "negative",
                        "intensity": impact_level,
                        "source": news.get("source", "新浪财经"),
                    })

        # Limit to top 5 events
        return sorted(events, key=lambda x: x["intensity"], reverse=True)[:5]
