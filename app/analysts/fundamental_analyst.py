"""
Fundamental analyst for the Stock Analysis System.

This module performs fundamental analysis of stocks based on financial statements,
ratios, and valuation metrics.
"""
from typing import Any, Dict, List, Optional

from app.analysts.base_analyst import BaseAnalyst
from app.data.models import (
    FinancialAnalysis,
    FinancialMetrics,
    FundamentalAnalysis,
)
from app.data.sources.eastmoney_api import EastmoneyClient


class FundamentalAnalyst(BaseAnalyst):
    """Analyst for fundamental stock analysis."""

    def __init__(self, stock_code: str):
        """
        Initialize the fundamental analyst.

        Args:
            stock_code: The stock code to analyze
        """
        super().__init__(stock_code)
        self.eastmoney_client = EastmoneyClient()

    def analyze(self) -> Dict[str, Any]:
        """
        Perform fundamental analysis.

        Returns:
            Dictionary containing fundamental analysis results
        """
        try:
            # Fetch financial data
            financial_data = self.eastmoney_client.get_financial_statements(self.stock_code)

            if not financial_data:
                return {
                    "error": "Unable to fetch financial data",
                    "stock_code": self.stock_code,
                }

            # Parse financial metrics
            metrics = self.eastmoney_client.parse_financial_metrics(financial_data)

            if not metrics:
                return {
                    "error": "Unable to parse financial metrics",
                    "stock_code": self.stock_code,
                }

            # Create FinancialMetrics object
            financial_metrics = FinancialMetrics(
                revenue_growth=metrics.get("revenue_growth", 0),
                net_margin=metrics.get("net_margin", 0),
                gross_margin=metrics.get("gross_margin", 0),
                operating_margin=0,  # Will need calculation
                roe=metrics.get("roe", 0),
                roa=metrics.get("roa", 0),
                debt_ratio=metrics.get("debt_ratio", 0),
                current_ratio=0,  # Will need from balance sheet
                pe_ratio=None,  # Will need from price data
                pb_ratio=None,  # Will need from price data
                ps_ratio=None,
                peg_ratio=None,
            )

            # Calculate profitability rating
            profitability_rating = self._calculate_profitability_rating(metrics)

            # Perform peer comparison (placeholder - would need peer data)
            peer_comparison = {
                "revenue_growth_percentile": self._estimate_percentile(metrics.get("revenue_growth", 0)),
                "net_margin_percentile": self._estimate_percentile(metrics.get("net_margin", 0)),
                "roe_percentile": self._estimate_percentile(metrics.get("roe", 0)),
            }

            # Evaluate valuation
            valuation = self._evaluate_valuation(metrics)

            # Calculate fair value range (placeholder - would need DCF or other model)
            fair_value_range = self._calculate_fair_value(metrics)

            # Identify core risks
            core_risks = self._identify_risks(metrics)

            # Detect anomalies
            anomalies = self._detect_anomalies(financial_data)

            return {
                "profitability_rating": profitability_rating,
                "key_metrics": financial_metrics.model_dump(),
                "peer_comparison": peer_comparison,
                "valuation": valuation,
                "fair_value_range": fair_value_range,
                "core_risks": core_risks,
                "anomalies": anomalies,
            }

        except Exception as e:
            return {
                "error": f"Fundamental analysis failed: {str(e)}",
                "stock_code": self.stock_code,
            }

    def _calculate_profitability_rating(self, metrics: Dict[str, float]) -> str:
        """
        Calculate overall profitability rating.

        Args:
            metrics: Financial metrics dictionary

        Returns:
            Rating (A, B, C, or D)
        """
        score = 0

        # Revenue growth (weight: 20%)
        revenue_growth = metrics.get("revenue_growth", 0)
        if revenue_growth >= 20:
            score += 20
        elif revenue_growth >= 10:
            score += 15
        elif revenue_growth >= 5:
            score += 10
        elif revenue_growth >= 0:
            score += 5

        # Net margin (weight: 25%)
        net_margin = metrics.get("net_margin", 0)
        if net_margin >= 20:
            score += 25
        elif net_margin >= 15:
            score += 20
        elif net_margin >= 10:
            score += 15
        elif net_margin >= 5:
            score += 10
        elif net_margin >= 0:
            score += 5

        # ROE (weight: 30%)
        roe = metrics.get("roe", 0)
        if roe >= 20:
            score += 30
        elif roe >= 15:
            score += 25
        elif roe >= 10:
            score += 20
        elif roe >= 5:
            score += 15
        elif roe >= 0:
            score += 10

        # Debt ratio (weight: 15%, lower is better)
        debt_ratio = metrics.get("debt_ratio", 1)
        if debt_ratio <= 0.3:
            score += 15
        elif debt_ratio <= 0.5:
            score += 12
        elif debt_ratio <= 0.7:
            score += 8
        elif debt_ratio <= 0.9:
            score += 5

        # Gross margin (weight: 10%)
        gross_margin = metrics.get("gross_margin", 0)
        if gross_margin >= 50:
            score += 10
        elif gross_margin >= 40:
            score += 8
        elif gross_margin >= 30:
            score += 6
        elif gross_margin >= 20:
            score += 4

        # Convert score to rating
        if score >= 80:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 40:
            return "C"
        else:
            return "D"

    def _estimate_percentile(self, value: float, mean: float = 10.0, std: float = 5.0) -> float:
        """
        Estimate percentile rank for a metric value.

        Args:
            value: Metric value
            mean: Industry mean
            std: Industry standard deviation

        Returns:
            Percentile (0-100)
        """
        # Simple z-score based percentile
        if std == 0:
            return 50.0

        z_score = (value - mean) / std
        percentile = 50 + (z_score * 16)  # Approximate conversion
        return max(0, min(100, percentile))

    def _evaluate_valuation(self, metrics: Dict[str, float]) -> str:
        """
        Evaluate stock valuation.

        Args:
            metrics: Financial metrics

        Returns:
            Valuation assessment (undervalued, fair, overvalued)
        """
        # This is a simplified approach
        # In production, you'd use PE, PB, PEG, and compare to historical and peers

        roe = metrics.get("roe", 0)
        revenue_growth = metrics.get("revenue_growth", 0)
        debt_ratio = metrics.get("debt_ratio", 0)

        # Simple valuation model
        if roe >= 15 and revenue_growth >= 15 and debt_ratio <= 0.5:
            return "undervalued"  # High quality, growing, low debt
        elif roe >= 10 and revenue_growth >= 10:
            return "fair"
        else:
            return "overvalued"

    def _calculate_fair_value(self, metrics: Dict[str, float]) -> tuple[float, float]:
        """
        Calculate fair value range.

        Args:
            metrics: Financial metrics

        Returns:
            Tuple of (lower_bound, upper_bound) for fair value
        """
        # This is a placeholder - actual implementation would use DCF, PEG, or other models
        # For now, return a generic range
        return (0.0, 0.0)

    def _identify_risks(self, metrics: Dict[str, float]) -> List[str]:
        """
        Identify potential risks based on financial metrics.

        Args:
            metrics: Financial metrics

        Returns:
            List of identified risks
        """
        risks = []

        # Check revenue growth trend
        revenue_growth = metrics.get("revenue_growth", 0)
        if revenue_growth < 0:
            risks.append("Revenue declining YoY")
        elif revenue_growth < 5:
            risks.append("Revenue growth slowing")

        # Check debt levels
        debt_ratio = metrics.get("debt_ratio", 0)
        if debt_ratio > 0.7:
            risks.append("High debt ratio")
        elif debt_ratio > 0.5:
            risks.append("Moderate debt levels")

        # Check profitability
        net_margin = metrics.get("net_margin", 0)
        if net_margin < 5:
            risks.append("Low profit margin")

        roe = metrics.get("roe", 0)
        if roe < 10:
            risks.append("Low return on equity")

        return risks if risks else ["No significant financial risks identified"]

    def _detect_anomalies(self, financial_data: Dict[str, List[Dict]]) -> List[str]:
        """
        Detect potential financial anomalies or red flags.

        Args:
            financial_data: Raw financial statement data

        Returns:
            List of detected anomalies
        """
        anomalies = []

        try:
            income_data = financial_data.get("income", [])

            if len(income_data) >= 2:
                # Check for unusual revenue growth (could indicate accounting issues)
                current_revenue = income_data[0].get("TOTAL_OPERATE_INCOME", 0)
                previous_revenue = income_data[1].get("TOTAL_OPERATE_INCOME", 0)

                if previous_revenue > 0:
                    growth_rate = (current_revenue - previous_revenue) / previous_revenue

                    # Unusually high growth could be suspicious
                    if growth_rate > 1.0:  # >100% growth
                        anomalies.append("Unusually high revenue growth (>100%)")
                    elif growth_rate < -0.5:  # >50% decline
                        anomalies.append("Significant revenue decline (>50%)")

        except Exception as e:
            print(f"Error detecting anomalies: {e}")

        return anomalies if anomalies else ["No significant anomalies detected"]
