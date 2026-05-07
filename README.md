# Stock Analysis System for Individual Investors

A comprehensive stock analysis platform that combines three analytical perspectives (macro, fundamental, technical) into actionable insights for individual investors.

## Features

### Three Independent Analyst Modules

1. **Macro Policy & News Analyst** (30% weight)
   - Analyzes news from caixin.com
   - Tracks national policies and regulations
   - Monitors macroeconomic indicators
   - Evaluates impact on market sectors

2. **Financial Report & Fundamental Analyst** (40% weight)
   - Fetches financial statements from http://www.cninfo.com.cn/
   - Calculates key ratios and metrics
   - Compares with industry benchmarks
   - Generates valuation judgments

3. **Technical Indicator & Price-Volume Analyst** (30% weight)
   - Fetches price data from tushare
   - Calculates technical indicators (MA, MACD, KDJ, RSI, Bollinger Bands)
   - Identifies chart patterns
   - Generates trading signals

### Target Sectors

- AI (Artificial Intelligence)
- Robotics
- Military Industry
- Electricity & New Energy
- Biopharmaceutical

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Tailwind CSS + Plotly.js
- **Data Sources**:
  - Tushare (stock prices)
  - Eastmoney (financial statements)
  - Caixin (news)

## Installation

1. Clone the repository:
```bash
cd stock-analysis-system
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install TA-Lib (technical analysis library):

**Linux:**
```bash
sudo apt-get install ta-lib
```

**macOS:**
```bash
brew install ta-lib
```

**Windows:**
Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
TUSHARE_TOKEN=your_tushare_token_here
EASTMONEY_API_KEY=your_eastmoney_api_key_here
```

## Usage

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The dashboard will be available at: `http://localhost:8000`

### API Endpoints

#### Analyze a Stock
```bash
POST /api/v1/analyze

{
  "stock_code": "600519",
  "analysis_types": ["macro", "fundamental", "technical"],
  "include_peer_comparison": true,
  "report_format": "detailed"
}
```

#### Get Stock Info
```bash
GET /api/v1/stock/{stock_code}/info
```

#### Get Price History
```bash
POST /api/v1/stock/{stock_code}/price

{
  "stock_code": "600519",
  "period": "3m"
}
```

#### Health Check
```bash
GET /health
```

### Demo Stocks

Quick analysis buttons are available for:
- **AI**: 科大讯飞 (002230)
- **Robotics**: 埃斯顿 (002747)
- **Military**: 中航沈飞 (600760)
- **Energy**: 宁德时代 (300750)
- **Biopharma**: 恒瑞医药 (600276)

## Project Structure

```
stock-analysis-system/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── models.py           # Pydantic models for API
│   │   └── routes.py           # API endpoints
│   ├── analysts/
│   │   ├── base_analyst.py     # Abstract base class
│   │   ├── macro_analyst.py    # Macro analysis implementation
│   │   ├── fundamental_analyst.py  # Fundamental analysis
│   │   └── technical_analyst.py    # Technical analysis
│   ├── data/
│   │   ├── models.py           # Data models
│   │   └── sources/
│   │       ├── tushare_client.py
│   │       ├── eastmoney_api.py
│   │       └── caixin_scraper.py
│   ├── config/
│   │   └── settings.py         # Configuration
│   ├── report/
│   │   ├── generator.py        # Report generation
│   │   └── templates.py        # Report templates
│   └── utils/
│       ├── indicators.py       # Technical indicator calculations
│       └── helpers.py          # Utility functions
├── web/
│   ├── static/                 # Static files (CSS, JS)
│   └── templates/
│       └── index.html          # Main dashboard
├── tests/
├── cache/                     # Local file cache
├── requirements.txt
├── .env.example
└── README.md
```

## System Limitations

This system has the following limitations that users should be aware of:

1. **Black Swan Events**: Cannot predict unforeseen market shocks
2. **Data Latency**: Some data sources may have delays
3. **Regulatory Changes**: Quick policy changes may not be captured immediately
4. **Technical Analysis Lag**: Indicators are based on historical data
5. **Sentiment Accuracy**: NLP sentiment analysis may have errors
6. **Peer Comparison**: Limited to available comparable companies
7. **Not Financial Advice**: System provides analysis, not personalized advice

**Important**: This tool is for educational and informational purposes only. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

## Configuration

Edit `app/config/settings.py` to customize:

- Analysis weights (macro, fundamental, technical)
- Cache expiration times
- Focus industries
- Demo stocks

## Testing

Run unit tests:
```bash
pytest tests/
```

Run integration tests:
```bash
pytest tests/test_integration.py -v

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes.

## Acknowledgments

- Tushare for stock data API
- Eastmoney for financial statement data
- Caixin for financial news
- Plotly for data visualization
- Tailwind CSS for UI styling
