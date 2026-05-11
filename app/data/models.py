"""
Data models for the Stock Analysis System.

This module defines Pydantic models for data validation and serialization.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class StockInfo(BaseModel):
    """Basic stock information."""

    stock_code: str = Field(..., description="Stock code (e.g., '600519')")
    company_name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry sector")
    market: Literal["SH", "SZ"] = Field(..., description="Stock exchange (SH/Shanghai, SZ/Shenzhen)")


class PriceData(BaseModel):
    """Stock price data for a specific date."""

    date: datetime
    open_price: float = Field(..., alias="open")
    high_price: float = Field(..., alias="high")
    low_price: float = Field(..., alias="low")
    close_price: float = Field(..., alias="close")
    volume: int
    turnover: float = Field(default=0.0)


class FinancialStatement(BaseModel):
    """Financial statement data."""

    period: str = Field(..., description="Reporting period (e.g., '2024Q3')")
    revenue: float
    net_profit: float
    gross_profit: float
    operating_profit: float
    total_assets: float
    total_liabilities: float
    total_equity: float
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float


class FinancialMetrics(BaseModel):
    """Calculated financial metrics and ratios."""

    revenue_growth: float = Field(..., description="Year-over-year revenue growth %")
    net_margin: float = Field(..., description="Net profit margin %")
    gross_margin: float = Field(..., description="Gross profit margin %")
    operating_margin: float = Field(..., description="Operating profit margin %")
    roe: float = Field(..., description="Return on equity %")
    roa: float = Field(..., description="Return on assets %")
    debt_ratio: float = Field(..., description="Debt-to-asset ratio")
    current_ratio: float = Field(..., description="Current ratio")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    pb_ratio: Optional[float] = Field(None, description="Price-to-book ratio")
    ps_ratio: Optional[float] = Field(None, description="Price-to-sales ratio")
    peg_ratio: Optional[float] = Field(None, description="PEG ratio")


class NewsItem(BaseModel):
    """News article data."""

    title: str
    content: str
    date: datetime
    source: str = Field(default="Caixin")
    url: Optional[str] = None
    sentiment: Optional[float] = Field(None, ge=-1.0, le=1.0)


class MacroIndicator(BaseModel):
    """Macroeconomic indicator data."""

    indicator_name: str
    value: float
    period: str
    change: Optional[float] = None
    impact: Literal["positive", "negative", "neutral"] = "neutral"


class TechnicalIndicator(BaseModel):
    """Technical analysis indicator values."""

    ma_5: float
    ma_10: float
    ma_20: float
    ma_60: float
    macd: float
    macd_signal: float
    macd_hist: float
    rsi: float
    kdj_k: float
    kdj_d: float
    kdj_j: float
    bb_upper: float
    bb_middle: float
    bb_lower: float


class TradingPattern(BaseModel):
    """Identified trading pattern."""

    pattern_name: str
    pattern_type: Literal["reversal", "continuation", "neutral"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str


class FundamentalAnalysis(BaseModel):
    """Fundamental analysis results."""

    profitability_rating: Literal["A", "B", "C", "D"]
    key_metrics: FinancialMetrics
    peer_comparison: Dict[str, float]
    valuation: Literal["undervalued", "fair", "overvalued"]
    fair_value_range: tuple[float, float]
    core_risks: List[str]
    anomalies: List[str]


class TechnicalAnalysis(BaseModel):
    """Technical analysis results."""

    signal: Literal["buy", "sell", "watch"]
    confidence: Literal["high", "medium", "low"]
    key_levels: Dict[str, float]
    current_pattern: Optional[TradingPattern]
    indicators: TechnicalIndicator
    failure_conditions: List[str]


class MacroAnalysis(BaseModel):
    """Macro analysis results."""

    macro_trend: Literal["bullish", "bearish", "neutral"]
    industry_rankings: List[Dict[str, Any]]
    risk_areas: List[str]
    key_events: List[Dict[str, Any]]


class AnalysisSummary(BaseModel):
    """Overall analysis summary."""

    overall_rating: Literal["A", "B", "C", "D", "F"]
    recommendation: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"]
    confidence: Literal["high", "medium", "low"]
    key_takeaways: List[str]
    weights_used: Dict[str, float]


class StockAnalysis(BaseModel):
    """Complete stock analysis report."""

    stock_code: str
    company_name: str
    analysis_date: datetime
    macro_analysis: Optional[MacroAnalysis] = None
    fundamental_analysis: Optional[FundamentalAnalysis] = None
    technical_analysis: Optional[TechnicalAnalysis] = None
    summary: AnalysisSummary
    limitations: List[str]
