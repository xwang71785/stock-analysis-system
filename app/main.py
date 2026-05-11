"""
FastAPI application entry point for the Stock Analysis System.

This module initializes the FastAPI application and defines the main routes.
"""
from datetime import datetime
from typing import List, Literal

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    IndustriesResponse,
    PriceHistoryRequest,
    PriceHistoryResponse,
    StockInfoResponse,
)
from app.analysts.fundamental_analyst import FundamentalAnalyst
from app.analysts.macro_analyst import MacroAnalyst
from app.analysts.technical_analyst import TechnicalAnalyst
from app.config.settings import settings
from app.data.sources.tushare_client import TushareClient

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive stock analysis system for individual investors",
)

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="web/templates")

# Initialize clients (lazy loading)
_tushare_client = None


def get_tushare_client():
    """Get or create Tushare client instance."""
    global _tushare_client
    if _tushare_client is None:
        _tushare_client = TushareClient()
    return _tushare_client


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
    )


# Root endpoint (web dashboard)
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


# Stock info endpoint
@app.get("/api/v1/stock/{stock_code}/info", response_model=StockInfoResponse)
async def get_stock_info(stock_code: str):
    """Get basic stock information."""
    try:
        client = get_tushare_client()
        info = client.get_stock_info(stock_code)

        if not info:
            return {"error": "Stock not found"}

        # Get latest price
        latest_price = client.get_latest_price(stock_code)

        return StockInfoResponse(
            stock_code=stock_code,
            company_name=info.get("name", ""),
            industry=info.get("industry", ""),
            market=info.get("market", ""),
            current_price=latest_price.get("close", None) if latest_price else None,
            change_percent=None,  # Would need previous close to calculate
        )

    except Exception as e:
        return {"error": str(e)}


# Price history endpoint
@app.post("/api/v1/stock/{stock_code}/price", response_model=PriceHistoryResponse)
async def get_price_history(stock_code: str, request: PriceHistoryRequest):
    """Get price history for a stock."""
    try:
        client = get_tushare_client()
        prices = client.get_daily_prices(stock_code)

        return PriceHistoryResponse(
            stock_code=stock_code,
            data=prices,
            period=request.period,
        )

    except Exception as e:
        return {"error": str(e)}


# Analysis endpoint
@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_stock(request: AnalyzeRequest):
    """
    Analyze a stock using specified analyst modules.

    This endpoint performs comprehensive stock analysis using the requested analyst types.
    """
    try:
        # Get stock info
        client = get_tushare_client()
        stock_info = client.get_stock_info(request.stock_code)

        if not stock_info:
            return {"error": "Stock not found"}

        company_name = stock_info.get("name", "")
        industry = stock_info.get("industry", "general")

        # Initialize result containers
        macro_analysis = None
        fundamental_analysis = None
        technical_analysis = None

        # Perform requested analyses
        if "macro" in request.analysis_types:
            macro_analyst = MacroAnalyst(request.stock_code, industry=industry)
            macro_analysis = macro_analyst.analyze()

        if "fundamental" in request.analysis_types:
            fundamental_analyst = FundamentalAnalyst(request.stock_code)
            fundamental_analysis = fundamental_analyst.analyze()

        if "technical" in request.analysis_types:
            technical_analyst = TechnicalAnalyst(request.stock_code)
            technical_analysis = technical_analyst.analyze()

        # Generate summary
        summary = _generate_summary(
            macro_analysis, fundamental_analysis, technical_analysis, request.analysis_types
        )

        # Generate limitations
        limitations = _generate_limitations(request.analysis_types)

        return AnalyzeResponse(
            stock_code=request.stock_code,
            company_name=company_name,
            analysis_date=datetime.now(),
            macro_analysis=macro_analysis,
            fundamental_analysis=fundamental_analysis,
            technical_analysis=technical_analysis,
            summary=summary,
            limitations=limitations,
        )

    except Exception as e:
        return {
            "error": str(e),
            "stock_code": request.stock_code,
        }


# Industries endpoint
@app.get("/api/v1/industries", response_model=IndustriesResponse)
async def get_industries():
    """Get list of supported industries."""
    industries = [
        {"name": industry, "code": industry.lower().replace(" ", "_")}
        for industry in settings.focus_industries
    ]
    return IndustriesResponse(industries=industries)


# Helper functions
def _generate_summary(macro, fundamental, technical, analysis_types) -> dict:
    """Generate overall analysis summary."""
    scores = []

    # Extract scores from each analysis
    if macro and "macro_trend" in macro:
        trend_score = 5.0 if macro["macro_trend"] == "bullish" else 3.0 if macro["macro_trend"] == "neutral" else 1.0
        scores.append(("macro", trend_score))

    if fundamental and "profitability_rating" in fundamental:
        rating = fundamental["profitability_rating"]
        rating_score = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0}.get(rating, 3.0)
        scores.append(("fundamental", rating_score))

    if technical and "signal" in technical:
        signal = technical["signal"]
        signal_score = {"buy": 5.0, "watch": 3.0, "sell": 1.0}.get(signal, 3.0)
        scores.append(("technical", signal_score))

    # Calculate weighted average
    weights = {
        "macro": settings.weight_macro,
        "fundamental": settings.weight_fundamental,
        "technical": settings.weight_technical,
    }

    total_score = 0.0
    total_weight = 0.0

    for analysis_type, score in scores:
        total_score += score * weights[analysis_type]
        total_weight += weights[analysis_type]

    final_score = total_score / total_weight if total_weight > 0 else 3.0

    # Determine overall rating
    if final_score >= 4.5:
        overall_rating = "A"
        recommendation = "strong_buy"
    elif final_score >= 3.5:
        overall_rating = "B"
        recommendation = "buy"
    elif final_score >= 2.5:
        overall_rating = "C"
        recommendation = "hold"
    elif final_score >= 1.5:
        overall_rating = "D"
        recommendation = "sell"
    else:
        overall_rating = "F"
        recommendation = "strong_sell"

    # Determine confidence
    confidence = "high" if len(scores) >= 3 else "medium" if len(scores) >= 2 else "low"

    # Generate key takeaways
    key_takeaways = []
    if macro and "industry_rankings" in macro and macro["industry_rankings"]:
        top_industry = macro["industry_rankings"][0]
        key_takeaways.append(f"Top performing industry: {top_industry['industry']} (score: {top_industry['score']})")

    if fundamental and "profitability_rating" in fundamental:
        key_takeaways.append(f"Profitability rating: {fundamental['profitability_rating']}")

    if technical and "signal" in technical:
        key_takeaways.append(f"Technical signal: {technical['signal']} ({technical.get('confidence', 'N/A')} confidence)")

    return {
        "overall_rating": overall_rating,
        "recommendation": recommendation,
        "confidence": confidence,
        "key_takeaways": key_takeaways if key_takeaways else ["Analysis completed"],
        "weights_used": weights,
    }


def _generate_limitations(analysis_types: List[str]) -> List[str]:
    """Generate list of system limitations based on performed analyses."""
    limitations = [
        "Black Swan Events: Cannot predict unforeseen market shocks",
        "Data Latency: Some data sources may have delays",
    ]

    if "fundamental" in analysis_types:
        limitations.append("Financial analysis based on historical data, future performance may differ")

    if "technical" in analysis_types:
        limitations.append("Technical indicators have lag, past patterns may not repeat")

    if "macro" in analysis_types:
        limitations.append("Sentiment analysis may have errors and biases")

    limitations.append("This analysis is not financial advice, please conduct your own research")

    return limitations


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
