"""
API request and response models for the Stock Analysis System.

This module defines Pydantic models for API endpoints.
"""
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="System status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.now)


class StockSearchRequest(BaseModel):
    """Stock search request."""

    query: str = Field(..., min_length=1, description="Search query (stock code or company name)")


class StockInfoResponse(BaseModel):
    """Stock information response."""

    stock_code: str
    company_name: str
    industry: str
    market: str
    current_price: Optional[float] = None
    change_percent: Optional[float] = None


class AnalyzeRequest(BaseModel):
    """Stock analysis request."""

    stock_code: str = Field(..., pattern=r"^[0-9]{6}$", description="6-digit stock code")
    analysis_types: List[Literal["macro", "fundamental", "technical"]] = Field(
        default_factory=lambda: ["fundamental", "technical"],
        description="Types of analysis to perform",
    )
    include_peer_comparison: bool = Field(default=True, description="Include peer comparison")
    report_format: Literal["detailed", "summary"] = Field(default="detailed", description="Report format")


class AnalyzeResponse(BaseModel):
    """Stock analysis response."""

    stock_code: str
    company_name: str
    analysis_date: datetime
    macro_analysis: Optional[dict] = None
    fundamental_analysis: Optional[dict] = None
    technical_analysis: Optional[dict] = None
    summary: dict
    limitations: List[str]


class PriceHistoryRequest(BaseModel):
    """Price history request."""

    stock_code: str = Field(..., pattern=r"^[0-9]{6}$")
    period: Literal["1d", "1w", "1m", "3m", "6m", "1y", "3y"] = Field(default="3m")


class PriceHistoryResponse(BaseModel):
    """Price history response."""

    stock_code: str
    data: List[dict]
    period: str


class IndustriesResponse(BaseModel):
    """Available industries response."""

    industries: List[dict]
