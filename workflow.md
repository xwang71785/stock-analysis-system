# Stock Analysis System - Workflow & Function Map

## System Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                   │
│                   (web/templates/index.html)                               │
│         HTML + Tailwind CSS + Plotly.js Dashboard                          │
└────────────────────────┬───────────────────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI APP                                        │
│                      (app/main.py)                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          API ENDPOINTS                              │   │
│  │  • GET /health           - Health check                             │   │
│  │  • GET /                 - Serve dashboard                          │   │
│  │  • GET /api/v1/stock/{code}/info        - Stock info                │   │
│  │  • POST /api/v1/stock/{code}/price      - Price history             │   │
│  │  • POST /api/v1/analyze                 - Main analysis endpoint    │   │
│  │  • GET /api/v1/industries               - Supported industries      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
                         │
                         │  POST /api/v1/analyze
                         │  Request: {stock_code, analysis_types, ...}
                         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    STOCK ANALYSIS ORCHESTRATOR                             │
│                          (main.py:analyze_stock)                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  1. Get Stock Info (via TushareClient)                               │  │
│  │  2. Initialize Analyst Classes (based on analysis_types)             │  │
│  │  3. Run Parallel Analysis (macro, fundamental, technical)            │  │
│  │  4. Generate Summary (weighted scoring)                              │  │
│  │  5. Generate Limitations                                             │  │
│  │  6. Return AnalyzeResponse                                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Macro       │ │ Fundamental  │ │ Technical    │
│  Analyst     │ │ Analyst      │ │ Analyst      │
│  (30% weight)│ │ (40% weight) │ │ (30% weight) │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ SinaFinance  │ │ Eastmoney    │ │ Tushare      │
│ Client       │ │ Client       │ │ Client       │
└──────────────┘ └──────────────┘ └──────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ News Data    │ │ Financial    │ │ Price Data   │
│              │ │ Statements   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Detailed Function Map

### 1. Macro Analyst (`app/analysts/macro_analyst.py`)

**Main Function:** `analyze() → Dict[str, Any]`

**Key Sub-functions:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `_analyze_macro_trend(news_list)` | Analyze overall macro trend based on news sentiment | "bullish" \| "bearish" \| "neutral" |
| `_rank_industries(macro_news, industry_news)` | Rank industries based on potential | List[Dict] (industry scores) |
| `_calculate_industry_score(industry, news_list)` | Calculate a score for an industry based on news | (score, reason) |
| `_detect_risks(macro_news, industry_news)` | Detect high-risk areas based on news and policies | List[str] (risk areas) |
| `_identify_key_events(macro_news, industry_news)` | Identify key market events | List[Dict] (events) |

**Data Source:** `SinaFinanceClient` (`app/data/sources/sina_finance.py`)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_macro_news(days=7)` | Fetch macro economic news | List[NewsItem] |
| `get_industry_news(industry, days=7)` | Fetch industry-specific news | List[NewsItem] |
| `analyze_sentiment(content)` | Analyze sentiment of news content | float (-1.0 to 1.0) |

---

### 2. Fundamental Analyst (`app/analysts/fundamental_analyst.py`)

**Main Function:** `analyze() → Dict[str, Any]`

**Key Sub-functions:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `_calculate_profitability_rating(metrics)` | Calculate overall profitability rating | "A" \| "B" \| "C" \| "D" |
| `_estimate_percentile(value, mean, std)` | Estimate percentile rank for a metric value | float (0-100) |
| `_evaluate_valuation(metrics)` | Evaluate stock valuation | "undervalued" \| "fair" \| "overvalued" |
| `_calculate_fair_value(metrics)` | Calculate fair value range | (lower_bound, upper_bound) |
| `_identify_risks(metrics)` | Identify potential risks based on financial metrics | List[str] |
| `_detect_anomalies(financial_data)` | Detect potential financial anomalies or red flags | List[str] |

**Data Source:** `EastmoneyClient` (`app/data/sources/eastmoney_api.py`)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_financial_statements(stock_code)` | Fetch financial statements | Dict (raw financial data) |
| `parse_financial_metrics(financial_data)` | Parse and calculate key metrics | Dict (key metrics) |

**Key Metrics Calculated:**

| Metric | Description | Weight in Rating |
|--------|-------------|-----------------|
| Revenue Growth | Year-over-year revenue growth % | 20% |
| Net Margin | Net profit margin % | 25% |
| ROE | Return on equity % | 30% |
| Debt Ratio | Debt-to-asset ratio (lower is better) | 15% |
| Gross Margin | Gross profit margin % | 10% |

---

### 3. Technical Analyst (`app/analysts/technical_analyst.py`)

**Main Function:** `analyze() → Dict[str, Any]`

**Key Sub-functions:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `_calculate_indicators(closes, highs, lows)` | Calculate all technical indicators | TechnicalIndicator |
| `_detect_patterns(closes, highs, lows, volumes)` | Detect trading patterns in price data | TradingPattern \| None |
| `_identify_support_resistance(closes)` | Identify key support and resistance levels | Dict[str, float] |
| `_generate_signal(indicators, pattern)` | Generate trading signal based on indicators and patterns | (signal, confidence) |
| `_determine_failure_conditions(closes, key_levels)` | Determine conditions that would invalidate the trading signal | List[str] |

**Indicator Calculations:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `_calculate_ma(data, period)` | Calculate Simple Moving Average | np.ndarray |
| `_calculate_macd(prices)` | Calculate MACD indicator | (MACD, Signal, Histogram) |
| `_calculate_ema(data, period)` | Calculate Exponential Moving Average | np.ndarray |
| `_calculate_rsi(prices, period=14)` | Calculate RSI indicator | np.ndarray |
| `_calculate_kdj(highs, lows, closes, period=9)` | Calculate KDJ indicator | (K, D, J) |
| `_calculate_bollinger_bands(prices)` | Calculate Bollinger Bands | (Upper, Middle, Lower) |

**Pattern Detection:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `_is_double_bottom(prices)` | Check for double bottom pattern | bool |
| `_is_breakout(prices)` | Check for breakout pattern | bool |
| `_is_consolidation(prices)` | Check for consolidation pattern | bool |

**Data Source:** `TushareClient` (`app/data/sources/tushare_client.py`)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_daily_prices(stock_code, start_date, end_date)` | Fetch daily price data | List[Dict] |
| `get_stock_info(stock_code)` | Get basic stock information | Dict |
| `get_latest_price(stock_code)` | Get latest price data | Dict |

---

### 4. Summary Generation (`main.py`)

**Function:** `_generate_summary(macro, fundamental, technical, analysis_types) → Dict`

**Process:**

1. **Extract scores from each analysis type:**
   - Macro: bullish (5.0) / neutral (3.0) / bearish (1.0)
   - Fundamental: A (5.0) / B (4.0) / C (3.0) / D (2.0)
   - Technical: buy (5.0) / watch (3.0) / sell (1.0)

2. **Apply weights:**
   - Macro: 0.3 (30%)
   - Fundamental: 0.4 (40%)
   - Technical: 0.3 (30%)

3. **Calculate weighted average score**

4. **Determine overall rating and recommendation:**
   | Score Range | Rating | Recommendation |
   |-------------|--------|----------------|
   | 4.5+ | A | strong_buy |
   | 3.5-4.5 | B | buy |
   | 2.5-3.5 | C | hold |
   | 1.5-2.5 | D | sell |
   | <1.5 | F | strong_sell |

5. **Generate key takeaways**

6. **Determine confidence level:** high (3 analyses) / medium (2 analyses) / low (1 analysis)

---

## Data Models

### API Models (`app/api/models.py`)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `HealthResponse` | Health check response | status, version, timestamp |
| `AnalyzeRequest` | Analysis request parameters | stock_code, analysis_types, include_peer_comparison, report_format |
| `AnalyzeResponse` | Complete analysis response | stock_code, company_name, analysis_date, macro_analysis, fundamental_analysis, technical_analysis, summary, limitations |
| `StockInfoResponse` | Stock information | stock_code, company_name, industry, market, current_price, change_percent |
| `PriceHistoryRequest` | Price history request | stock_code, period |
| `PriceHistoryResponse` | Price history response | stock_code, data, period |
| `IndustriesResponse` | Available industries | industries |

### Data Models (`app/data/models.py`)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `StockInfo` | Basic stock information | stock_code, company_name, industry, market |
| `PriceData` | Stock price data | date, open, high, low, close, volume, turnover |
| `FinancialMetrics` | Calculated financial metrics | revenue_growth, net_margin, gross_margin, roe, roa, debt_ratio, pe_ratio, pb_ratio, etc. |
| `FinancialStatement` | Financial statement data | period, revenue, net_profit, total_assets, total_equity, cash_flow, etc. |
| `TechnicalIndicator` | Technical analysis indicators | ma_5, ma_10, ma_20, ma_60, macd, macd_signal, rsi, kdj_k, kdj_d, kdj_j, bb_upper, bb_middle, bb_lower |
| `TradingPattern` | Identified trading pattern | pattern_name, pattern_type (reversal/continuation/neutral), confidence, description |
| `NewsItem` | News article data | title, content, date, source, sentiment |
| `FundamentalAnalysis` | Fundamental analysis results | profitability_rating, key_metrics, peer_comparison, valuation, fair_value_range, core_risks, anomalies |
| `TechnicalAnalysis` | Technical analysis results | signal, confidence, key_levels, current_pattern, indicators, failure_conditions |
| `MacroAnalysis` | Macro analysis results | macro_trend, industry_rankings, risk_areas, key_events |
| `AnalysisSummary` | Overall analysis summary | overall_rating, recommendation, confidence, key_takeaways, weights_used |
| `StockAnalysis` | Complete stock analysis report | stock_code, company_name, analysis_date, macro_analysis, fundamental_analysis, technical_analysis, summary, limitations |

---

## Configuration (`app/config/settings.py`)

### Settings Structure

| Category | Setting | Default | Description |
|----------|---------|---------|-------------|
| **API Credentials** | `tushare_token` | "" | Tushare API token |
| | `eastmoney_api_key` | "" | Eastmoney API key |
| **Cache Configuration** | `cache_dir` | "./cache" | Cache directory path |
| | `cache_expiry_price` | 24 hours | Price data cache expiry |
| | `cache_expiry_financials` | 168 hours | Financial data cache expiry (7 days) |
| | `cache_expiry_news` | 4 hours | News data cache expiry |
| **Application** | `app_name` | "Stock Analysis System" | Application name |
| | `app_version` | "1.0.0" | Application version |
| | `debug` | False | Debug mode |
| **Focus Industries** | `focus_industries` | AI, Robotics, Military Industry, Electricity & New Energy, Biopharmaceutical | Supported industries |
| **Analysis Weights** | `weight_macro` | 0.3 | Macro analysis weight (30%) |
| | `weight_fundamental` | 0.4 | Fundamental analysis weight (40%) |
| | `weight_technical` | 0.3 | Technical analysis weight (30%) |

### Demo Stocks Mapping

| Industry | Stock Code | Company Name | Description |
|----------|------------|--------------|-------------|
| AI | 002230 | 科大讯飞 | Speech recognition AI leader |
| Robotics | 002747 | 埃斯顿 | Industrial robotics manufacturer |
| Military | 600760 | 中航沈飞 | Aviation and defense manufacturing |
| Energy | 300750 | 宁德时代 | Battery and new energy technology |
| Biopharma | 600276 | 恒瑞医药 | Pharmaceutical innovation leader |

---

## Key Workflows

### Analysis Request Flow

```
User Request
    ↓
Dashboard (web/templates/index.html)
    ↓
HTTP POST /api/v1/analyze
    ↓
┌───────────────────────────────────────────────────────────────┐
│  1. Validate stock code (6-digit numeric)                     │
│  2. Get stock info via TushareClient.get_stock_info()         │
│  3. Initialize analyst classes based on analysis_types        │
│     • MacroAnalyst(stock_code, industry)                      │
│     • FundamentalAnalyst(stock_code)                          │
│     • TechnicalAnalyst(stock_code)                            │
│  4. Perform parallel analysis                                 │
│     • Macro: Fetch news, analyze trends, rank industries      │
│     • Fundamental: Fetch statements, calculate metrics        │
│     • Technical: Fetch prices, calculate indicators           │
│  5. Generate summary with weighted scoring                    │
│  6. Generate limitations                                      │
│  7. Return AnalyzeResponse as JSON                            │
└───────────────────────────────────────────────────────────────┘
    ↓
JSON Response to Dashboard
    ↓
Visualization (Plotly.js charts)
```

### Data Fetching Flow with Caching

```
Data Request
    ↓
Check Cache (file-based)
    ↓
    ├─ Cache Hit → Return Cached Data
    │
    └─ Cache Miss → Fetch from API
         ↓
    Save to Cache
         ↓
    Return Data
```

### Technical Analysis Calculation Flow

```
Fetch Price Data (TushareClient)
    ↓
Convert to numpy arrays (closes, highs, lows, volumes)
    ↓
┌─────────────────────────────────────────────────────────┐
│ Calculate Indicators:                                   │
│ • Moving Averages: 5, 10, 20, 60 day                    │
│ • MACD: EMA(12) - EMA(26), Signal = EMA(9)              │
│ • RSI: Relative Strength Index (14 period)              │
│ • KDJ: Stochastic oscillator (9 period)                 │
│ • Bollinger Bands: ±2 standard deviations from MA(20)   │
└─────────────────────────────────────────────────────────┘
    ↓
Detect Patterns (double bottom, breakout, consolidation)
    ↓
Identify Support/Resistance Levels
    ↓
Generate Trading Signal (buy/sell/watch)
    ↓
Determine Failure Conditions
    ↓
Return Technical Analysis
```

### Fundamental Analysis Calculation Flow

```
Fetch Financial Statements (EastmoneyClient)
    ↓
Parse Financial Metrics:
    • Revenue Growth = (Current Revenue - Previous Revenue) / Previous Revenue
    • Net Margin = Net Profit / Revenue
    • Gross Margin = (Revenue - COGS) / Revenue
    • ROE = Net Income / Shareholder Equity
    • ROA = Net Income / Total Assets
    • Debt Ratio = Total Liabilities / Total Assets
    ↓
Calculate Profitability Rating (weighted score)
    ↓
Estimate Percentile Rankings vs Industry
    ↓
Evaluate Valuation (undervalued/fair/overvalued)
    ↓
Identify Risks (declining revenue, high debt, low margins)
    ↓
Detect Anomalies (unusual growth patterns)
    ↓
Return Fundamental Analysis
```

### Macro Analysis Calculation Flow

```
Fetch Macro News (SinaFinanceClient)
    ↓
Fetch Industry News (if specified)
    ↓
Analyze Macro Trend:
    • Calculate average sentiment of all news
    • Determine bullish/neutral/bearish
    ↓
Rank Industries:
    • Match news against industry keywords
    • Calculate sentiment-based scores
    • Sort by score descending
    ↓
Detect Risk Areas:
    • Search for risk keywords (regulation, investigation, ban, etc.)
    ↓
Identify Key Events:
    • Search for policy-related news
    • Assess impact (positive/negative) and intensity (1-5)
    ↓
Return Macro Analysis
```

---

## Caching Strategy

| Data Type | Cache Key Format | Expiry Time | Purpose |
|-----------|-----------------|--------------|---------|
| Stock Info | `tushare_stock_info_{stock_code}` | 24 hours | Basic company information |
| Price History | `tushare_prices_{stock_code}_{start_date}_{end_date}` | 24 hours | Historical price data |
| Latest Price | `tushare_latest_price_{stock_code}` | 1 hour | Real-time price data |
| Financial Statements | `eastmoney_financial_{stock_code}` | 168 hours (7 days) | Financial reports |
| News Data | `sina_news_{industry}_{days}` | 4 hours | News articles |

---

## Error Handling

### Common Error Scenarios

| Error Type | Location | Handling |
|------------|----------|----------|
| Invalid stock code | API layer | Return error response |
| Stock not found | Data layer | Return error response |
| Insufficient price data | Technical analyst | Return error with message |
| API rate limit | Data layer | Retry with exponential backoff |
| Cache write failure | Base analyst | Fail silently (continue) |
| Missing API credentials | Application startup | Raise ValueError |

---

## System Limitations

1. **Black Swan Events**: Cannot predict unforeseen market shocks
2. **Data Latency**: Some data sources may have delays
3. **Regulatory Changes**: Quick policy changes may not be captured immediately
4. **Technical Analysis Lag**: Indicators are based on historical data
5. **Sentiment Accuracy**: NLP sentiment analysis may have errors
6. **Peer Comparison**: Limited to available comparable companies
7. **Not Financial Advice**: System provides analysis, not personalized advice

---

## File Structure

```
stock-analysis-system/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── models.py           # Pydantic models for API requests/responses
│   │   └── routes.py           # API endpoint definitions (not implemented)
│   ├── analysts/
│   │   ├── base_analyst.py     # Abstract base class for all analysts
│   │   ├── macro_analyst.py    # Macro policy and news analysis
│   │   ├── fundamental_analyst.py  # Financial statement analysis
│   │   └── technical_analyst.py    # Technical indicator analysis
│   ├── data/
│   │   ├── models.py           # Pydantic data models
│   │   └── sources/
│   │       ├── tushare_client.py    # Tushare API integration
│   │       ├── eastmoney_api.py    # Eastmoney API integration
│   │       ├── sina_finance.py      # Sina Finance news scraper
│   │       └── caixin_scraper.py   # Caixin news scraper
│   ├── config/
│   │   └── settings.py         # Application configuration
│   ├── report/
│   │   ├── generator.py        # Report generation (not implemented)
│   │   └── templates.py        # Report templates (not implemented)
│   └── utils/
│       ├── indicators.py       # Technical indicator calculations (not implemented)
│       └── helpers.py          # Utility functions (not implemented)
├── web/
│   ├── static/                 # Static files (CSS, JS)
│   └── templates/
│       └── index.html          # Main dashboard
├── cache/                     # Local file cache
├── tests/
├── requirements.txt
├── .env.example
├── README.md
└── workflow.md                # This file
```

---

## API Endpoints Quick Reference

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/health` | Health check | None | HealthResponse |
| GET | `/` | Serve dashboard | None | HTML |
| GET | `/api/v1/stock/{code}/info` | Get stock info | None | StockInfoResponse |
| POST | `/api/v1/stock/{code}/price` | Get price history | PriceHistoryRequest | PriceHistoryResponse |
| POST | `/api/v1/analyze` | Analyze stock | AnalyzeRequest | AnalyzeResponse |
| GET | `/api/v1/industries` | Get supported industries | None | IndustriesResponse |

---

## Technical Analysis Indicators Reference

| Indicator | Formula | Trading Signal |
|-----------|---------|----------------|
| **Moving Average (MA)** | Simple average of last N periods | Price > MA: Bullish |
| **MACD** | EMA(12) - EMA(26) | MACD > Signal: Bullish |
| **RSI** | 100 - (100 / (1 + RS)) | RSI < 30: Oversold (Buy) |
| | | RSI > 70: Overbought (Sell) |
| **KDJ** | Stochastic oscillator | K < 20: Oversold |
| | | K > 80: Overbought |
| **Bollinger Bands** | MA ± 2×StdDev | Price < Lower: Oversold |
| | | Price > Upper: Overbought |

---

## Fundamental Analysis Metrics Reference

| Metric | Good Value | Interpretation |
|--------|------------|----------------|
| **Revenue Growth** | > 20% | Strong growth |
| | 10-20% | Moderate growth |
| **Net Margin** | > 20% | Excellent profitability |
| | 10-20% | Good profitability |
| **ROE** | > 20% | Excellent return |
| | 15-20% | Good return |
| **Debt Ratio** | < 0.3 | Low leverage (good) |
| | 0.3-0.5 | Moderate leverage |
| **Gross Margin** | > 50% | High margin business |

---

## Industry Keywords for News Matching

| Industry | Keywords (EN) | Keywords (CN) |
|----------|---------------|---------------|
| AI | AI, machine learning, chatgpt, 大模型 | 人工智能, 人工智能 |
| Robotics | robot, automation, manufacturing, 智能制造 | 机器人, 自动化 |
| Military | defense, military, 航空, 船舶, 导弹 | 军工, 国防 |
| Energy | energy, solar,光伏, wind, 风电, battery, 电池 | 能源, 新能源 |
| Biopharma | pharma, drug, biotech, biotechnology, 疫苗 | 医药, 生物制药 |

---

*Last Updated: 2026-03-17*
