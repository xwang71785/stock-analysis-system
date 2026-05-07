Great. Your answers materially improve the design direction.

Given your clarifications, this is no longer just a generic “stock analysis dashboard.” It is more specifically:

> A China A-share swing-trading research and monitoring agent for next-week horizon, combining daily/tick/order-book/news/filings/crowd signals, using LLMs for impact relevance and explainable action recommendations.

That is a much sharper product.

Below I’ll give you **Option C**: a **v1 / v2 / v3 roadmap** with:
- practical features vs advanced features separated,
- what to build now,
- what to defer,
- what to remove or downgrade,
- and what “cutting-edge” components to add over time.

I’ll also tailor the roadmap for:
- **next-week horizon**
- **swing trading**
- **Linux deployment**
- **cloud LLMs**
- **explainability**
- **action recommendations**
- **1-year history retention**
- **KOL as crowd proxy, not primary alpha**

---

# 1. Strategic reframing of the product

Before roadmap, I’d reframe the system objective as:

## Product Objective
Build a local Linux-hosted web application for **next-week swing trading in China A-shares**, focused on a curated universe of ~25 leading thematic stocks, that:
- continuously monitors price, order book, filings, news, macro, and crowd attention,
- detects events and maps them to affected stocks,
- estimates **next-week directional opportunity and risk**,
- provides **explainable score changes and suggested trade actions**,
- and alerts the user when thesis-relevant changes occur.

## Primary use case
- Rank swing opportunities for the coming week
- Explain what changed
- Suggest whether to:
  - enter long,
  - reduce,
  - avoid,
  - wait for confirmation,
  - or exit

## Secondary use case
- Monitor thesis breaks and narrative shifts intraday / daily

## Important implication
Because your horizon is **next week**, the system should emphasize:
- **event impact**
- **daily + intraday context**
- **swing entry timing**
- **sector-relative strength**
- **microstructure confirmation**
- **crowding risk**
- **stop / target logic**
- **not ultra-high-frequency prediction**

So some microstructure features matter, but not at HFT depth.

---

# 2. High-level build philosophy

For your use case, the right sequence is:

## v1 = useful trader workstation
Focus on:
- stable data ingestion
- explainable stock ranking
- event relevance
- action suggestion
- alerting

## v2 = research-grade assistant
Add:
- backtesting
- crowding logic
- dynamic weighting
- richer microstructure features
- thesis tracking

## v3 = differentiated intelligent agent
Add:
- adaptive models
- RAG copilot
- event study engine
- confidence calibration
- portfolio-aware suggestions

This is important because many systems fail by trying to do too much AI too early.

---

# 3. Recommended V1 / V2 / V3 roadmap

---

## V1 — Practical MVP for real swing-trading use
### Goal
Build something you can actually use every day for next-week swing setups.

### Time horizon
~6–10 weeks depending on engineering speed.

---

## V1.1 Core capabilities

### A. Universe and data ingestion
Must have:
- fixed stock universe (~25 names)
- historical daily OHLCV
- historical tick data
- real-time 5-level order book
- news ingestion
- filings/announcements ingestion
- macro calendar / key releases
- KOL posts ingestion

### Priority notes
- **Filings/announcements are more important than KOLs**
- KOL should be retained, but as attention/crowding layer only

---

### B. Stock-event relevance using LLM
This is one of the highest-value additions based on your answer.

For each news/announcement/post, classify:
- is this relevant to any stock in the universe?
- direct or indirect relevance?
- positive / negative / mixed impact?
- likely impact horizon: intraday / 2–5 days / 1–2 weeks
- confidence level
- rationale
- cited evidence from text

This is much better than generic sentiment.

#### Suggested output schema
For each document:
- `doc_id`
- `doc_type` = news / filing / KOL / macro
- `stock_id`
- `relevance_score` (0–1)
- `impact_direction` = positive / negative / mixed / neutral
- `impact_horizon` = intraday / weekly / medium-term
- `event_type`
- `confidence`
- `evidence_snippet`
- `llm_summary`

This should be in V1.

---

### C. Explainable scoring engine for next-week swing trading
Instead of a raw score only, use 3 outputs:

#### 1. Opportunity Score
“How attractive is this stock for next-week upside?”

#### 2. Risk Score
“What is the chance this setup fails / gets crowded / reverses?”

#### 3. Confidence Score
“How trustworthy is the signal based on data quality and signal alignment?”

Then derive:
- **Action recommendation**
- **Entry style**
- **Stop / invalidation suggestion**
- **Take-profit style**
- **Wait / confirm / avoid logic**

This structure is much better than just `-10 to +10`.

---

### D. Core signal buckets for V1
For your horizon, I recommend these six:

#### 1. Price/Trend Structure
Use:
- 5/10/20/60 MA
- trend slope
- 20-day breakout/breakdown
- relative strength vs sector/index
- ATR / volatility
- gap behavior
- turnover percentile

#### 2. Volume & Participation
Use:
- volume surprise vs 20-day average
- turnover spike
- OBV or accumulation proxy
- volume on up/down days
- price-volume confirmation

#### 3. Event/News/Filing Impact
Use LLM and rules to capture:
- announcement materiality
- policy changes
- order wins
- earnings/guidance
- product approval / launch
- financing / dilution
- litigation / regulation
- shareholder changes

#### 4. Order Book / Intraday Pressure Proxy
For next-week swing trading, don't overcomplicate this in v1.
Use:
- rolling order imbalance
- large order persistence
- cancel ratio proxy
- intraday net pressure
- close strength
- VWAP relative position

This is enough for v1.

#### 5. Crowd Attention / KOL Proxy
Use KOL as:
- attention spike detector
- crowding indicator
- narrative acceleration signal
- sentiment dispersion signal

Not primary alpha.

#### 6. Macro / Sector Regime
Use:
- market regime
- sector strength
- major macro release context
- policy sensitivity

---

### E. Action recommendation engine
Because you said you want suggested actions and entries/exits, this should exist in V1.

Example outputs:
- **Long now**
- **Watch for breakout above X**
- **Wait for pullback to Y**
- **Reduce / take profit**
- **Exit if below Z**
- **Avoid due to crowding / weak confirmation**
- **High-risk event setup only**

#### Recommendation format
For each stock:
- current stance: bullish / neutral / bearish
- recommended action
- preferred entry condition
- invalidation level
- target style
- confidence
- reasons

This should be rules-based in V1, not full ML.

---

### F. Explainability layer
Must-have for V1.

For every score/recommendation, show:
- top 3 bullish drivers
- top 3 bearish drivers
- what changed since yesterday
- key supporting documents
- confidence
- freshness of data
- contradictory signals

This is non-negotiable if you want trust.

---

### G. Alert engine
For V1, alerts should focus on high signal-to-noise events:

#### V1 alert types
- material filing / announcement
- high-impact news mapped to stock
- score jump / drop
- opportunity score crosses threshold
- risk score spikes
- breakout with volume confirmation
- order-book pressure anomaly
- crowd attention spike
- thesis contradiction

This is enough.

---

## V1.2 What to simplify / defer in V1

These are things in your original PDR that I would **de-emphasize or simplify**:

### Defer 1: sophisticated pattern recognition library
You don’t need too many chart patterns initially.
Focus on:
- breakout
- pullback
- trend continuation
- failed breakout
- reversal at key levels

That is enough for swing trading.

### Defer 2: too many classic indicators
You don't need all of:
- MACD
- DMI
- KDJ
- BIAS
- VR
- OBV
all at once.

Start with:
- MA/trend
- RSI
- ATR
- relative strength
- volume surprise
- breakout metrics

Too many indicators can create noisy overlap.

### Defer 3: deep “institutional behavior” claims
Rename this module.
Use:
- **Order Book Pressure Analysis**
instead of:
- **Institution Behavior Analysis**

That wording is more honest and defensible.

### Defer 4: macro breadth
Only ingest macro data that matters to your sectors and weekly horizon.
For V1:
- PMI
- CPI/PPI
- M2 / credit impulse if relevant
- policy headlines
- major rate/liquidity events

Don’t build a full macro terminal.

---

# 4. V1 recommended architecture

## Backend
- Python 3.11+
- FastAPI
- APScheduler or Celery if concurrency increases
- SQLAlchemy
- Pydantic
- async HTTP clients

## Storage
For your use case, I recommend changing from pure SQLite:

### Better design
- **PostgreSQL** for metadata / app data / signals / alerts / docs
- **DuckDB + Parquet** for analytical time series, ticks, order book aggregates, backtests
- optional Redis for caching

If you insist on simple setup:
- SQLite for metadata
- Parquet/DuckDB for market + document features

But Linux server makes PostgreSQL a strong choice.

## NLP / AI
- cloud LLM APIs for:
  - event relevance
  - impact classification
  - summarization
  - explanation generation
- local rules for:
  - dedupe
  - basic entity matching
  - fallback relevance detection

## Frontend
You can keep simple web UI, but I would suggest:
- lightweight frontend framework eventually
- but plain JS is okay for v1 if speed matters

---

# 5. V1 data model additions

Your schema needs extension for explainability and LLM outputs.

## Add these tables

### `documents`
Unified source table:
- id
- source_type (news, filing, kol, macro)
- source_name
- title
- url
- content
- published_at
- collected_at
- hash
- raw_metadata

### `document_stock_impacts`
Stores LLM/rule outputs:
- id
- document_id
- stock_id
- relevance_score
- impact_direction
- impact_strength
- impact_horizon
- event_type
- confidence
- explanation
- evidence_snippet
- model_name
- model_version
- created_at

### `technical_features`
- stock_id
- date
- trend_score
- rs_score
- atr_pct
- breakout_flag
- volume_surprise
- turnover_pctile
- etc.

### `order_book_features`
- stock_id
- timestamp/minute_bucket
- imbalance
- cancel_ratio_proxy
- large_order_net
- vwap_distance
- close_strength
- pressure_score

### `crowd_features`
- stock_id
- date
- kol_mentions
- attention_spike
- crowd_sentiment
- sentiment_dispersion
- crowding_risk

### `recommendations`
- stock_id
- date/time
- stance
- action
- entry_condition
- stop_level
- target_hint
- confidence
- explanation

### `score_explanations`
- stock_id
- date
- opportunity_score
- risk_score
- confidence_score
- top_positive_factors
- top_negative_factors
- changes_from_prior

This will make the system much more usable.

---

# 6. V2 — Research-grade system
### Goal
Make the system more reliable, backtested, and differentiated.

### Time horizon
After V1 proves useful.

---

## V2.1 Major upgrades

### A. Backtesting and evaluation framework
This is the biggest missing professional component.

For each day and stock:
- snapshot all signals
- store recommendation
- compare with next-week outcome

Measure:
- hit rate
- score bucket returns
- max adverse excursion
- max favorable excursion
- precision by action type
- false positive rate
- by sector/regime/event type

This must be V2 if not V1.

---

### B. Dynamic weighting
Instead of static weights, allow:
- sector-specific weights
- regime-based weights
- event-sensitive weights

Examples:
- in event-heavy periods, event score > technical score
- in trend regime, price/volume > crowding
- when crowd spike is extreme, risk score rises

This can start as a rule engine before ML.

---

### C. Sector-relative and regime-aware ranking
For your universe, ranking should become:
- absolute opportunity
- sector-relative opportunity
- crowd-adjusted opportunity
- risk-adjusted opportunity

This matters a lot for swing trading.

---

### D. Better tick/order-book feature engineering
Since you have historical tick and real-time 5-level, V2 should extract:
- aggressor-like trade flow approximations
- cancel intensity
- intraday pressure regime
- opening auction strength
- afternoon continuation behavior
- close auction significance
- price impact of large prints
- liquidity vacuum patterns

These features can materially improve entry timing.

---

### E. Thesis state tracking
For each stock, maintain a live thesis ledger:
- current bullish narrative
- current bearish narrative
- latest confirming evidence
- latest contradicting evidence
- thesis status: strengthening / weakening / broken

This is extremely useful for discretionary swing traders.

---

### F. Filing / earnings parser
V2 should fully parse:
- annual reports
- interim reports
- key announcements
- earnings pre-announcements
- private placements / CB issuance
- shareholder reductions/increases
- buybacks
- management changes

And map them into structured event signals.

---

## V2.2 Advanced alert types
Add:
- thesis break alert
- crowding overload alert
- event-price divergence alert
- failed breakout alert
- score-confidence divergence alert
- stale data / parser failure alert

---

## V2.3 Better action framework
V2 recommendations should distinguish:
- **Aggressive entry**
- **Confirmation entry**
- **Pullback entry**
- **Take partial profits**
- **Protect gains**
- **Avoid due to event uncertainty**
- **Exit due to thesis break**

This is much closer to actual swing-trading decisions.

---

# 7. V3 — Differentiated intelligent agent
### Goal
Turn the system into a real AI analyst copilot, not just a scoring tool.

---

## V3.1 RAG research copilot
User can ask:
- Why is this stock ranked #1 this week?
- What changed in the last 3 days?
- Summarize bullish and bearish evidence.
- What are the main risks to the setup?
- Which docs support the recommendation?
- Compare this stock with its closest peer.

This requires:
- vector search
- reranking
- document citation
- answer generation grounded in your stored data

This is one of the most valuable “cutting-edge” additions.

---

## V3.2 Event study engine
For every event type:
- compute historical next-week response
- by sector
- by market regime
- by stock liquidity bucket

Then the system can say:
- “Historically, this kind of contract win in AI hardware names during strong sector regimes led to median +4.2% next-week returns.”

That is very powerful.

---

## V3.3 Probabilistic forecasting
Move from raw score to:
- probability of positive next-week return
- expected return band
- downside risk band
- confidence interval

This is much more sophisticated.

---

## V3.4 Portfolio-aware recommendation engine
Since you may eventually act on these ideas, V3 can consider:
- correlation across names
- sector concentration
- event overlap
- crowding overlap
- staggered entry suggestions

This goes beyond single-stock recommendation.

---

## V3.5 Human feedback learning loop
Let you rate:
- alert usefulness
- recommendation quality
- relevance of a document
- whether the thesis/explanation was right

Then retrain or recalibrate:
- event relevance
- score weights
- alert thresholds
- KOL credibility
- recommendation templates

This becomes your personal edge over time.

---

# 8. What to cut, simplify, or rename

Here is my direct advice on what to trim from the original PDR.

## Cut or reduce
### 1. Overloaded classic indicators
Reduce indicator sprawl.
Keep only the most useful for swing trading.

### 2. Generic sentiment framing
Replace with impact/event relevance.

### 3. “Institution behavior analysis” wording
Change to:
- order-book pressure
- microstructure pressure
- intraday flow proxy

### 4. Broad macro collection
Narrow to macro/policy inputs relevant to weekly swings.

### 5. Equal treatment of all data sources
You need source hierarchy:
- filings / exchange announcements
- structured news
- macro releases
- KOL/social

KOL should not have similar influence to filings.

---

# 9. Recommended scoring framework for your use case

For next-week swing trading, I’d recommend:

## Final output
For each stock:
- Opportunity Score: 0–100
- Risk Score: 0–100
- Confidence Score: 0–100
- Net Trade Rating: Strong Long / Watch Long / Neutral / Avoid / Exit

This is more intuitive than -10 to +10.

## V1 score weights
Initial rule-based weights:

### Opportunity Score
- Event/Filing Impact: 30%
- Price/Trend Structure: 25%
- Volume/Participation: 15%
- Order-Book Pressure: 15%
- Sector/Macro Regime: 10%
- Crowd Attention: 5%

### Risk Score
- Crowding spike: 20%
- Negative/contradictory events: 30%
- Failed price confirmation: 20%
- Volatility/liquidity risk: 15%
- Macro/event uncertainty: 15%

### Confidence Score
- signal agreement across modules
- freshness of data
- relevance confidence from LLM
- source quality
- whether price confirms narrative

This is much better aligned to your use case.

---

# 10. Suggested action recommendation logic

For example:

## Strong Long
Conditions:
- high opportunity
- moderate/low risk
- medium/high confidence
- event impact positive
- price structure supportive
- no severe crowding

## Watch Long
Conditions:
- high opportunity
- but needs breakout confirmation or pullback entry

## Neutral
Mixed signals, weak confirmation

## Avoid
High crowding, low confidence, or weak structure

## Exit / Reduce
Negative event or thesis break, or failed price confirmation

This can all be rules-based initially.

---

# 11. Recommended build order

If I were managing this as a hedge fund-style product build, I would use this sequence:

## Phase A — Foundation
- Linux deployment
- source connectors
- unified documents table
- stock master
- daily data
- 1-minute/tick-derived aggregate features
- base UI

## Phase B — Core intelligence
- LLM relevance and impact classification
- stock-event mapping
- score engine
- explanation engine
- recommendation engine

## Phase C — Monitoring
- real-time order-book feature updates
- alerts
- dashboard rankings
- document drill-down

## Phase D — Validation
- historical replay
- next-week backtests
- threshold tuning
- signal ablation

## Phase E — Advanced
- RAG copilot
- event study engine
- adaptive weighting
- feedback loop

This order minimizes wasted effort.

---

# 12. Technology recommendations by version

## V1
- FastAPI
- PostgreSQL or SQLite + DuckDB
- APScheduler
- Pandas / Polars
- cloud LLM API
- basic frontend
- Plotly/ECharts for charts

## V2
- PostgreSQL + DuckDB strongly preferred
- Redis optional
- Celery / Dramatiq / Prefect if workflows expand
- MLflow or simple experiment logging
- vector DB or pgvector for document retrieval

## V3
- pgvector / Milvus / Weaviate
- reranker model
- RAG pipeline
- more formal model calibration and evaluation stack

---

# 13. Key risks to manage

## Data risk
- scraper breakage
- inconsistent timestamps
- duplicate stories
- false KOL signals
- weak stock-news mapping

## Model risk
- LLM hallucination
- unstable impact classification
- overreaction to noisy social data

## Trading risk
- crowding
- gap risk
- event overnight risk
- false breakout signals

## Operational risk
- failed jobs
- stale data
- missed alerts
- poor explainability

These should be explicitly listed in the PDR.

---

# 14. My recommended final roadmap summary

## V1: Useful swing-trading workstation
Build now:
- fixed universe
- daily/tick/order-book ingestion
- filings/news/KOL ingestion
- LLM relevance + impact classification
- opportunity/risk/confidence score
- explainable action recommendations
- dashboard and alerts

## V2: Research-grade validation and better signal quality
Add next:
- backtesting
- dynamic weighting
- thesis tracking
- richer microstructure features
- sector-relative ranking
- filing parser
- advanced alerts

## V3: Differentiated AI analyst agent
Add later:
- RAG copilot
- event study engine
- probabilistic forecasts
- portfolio-aware recommendations
- feedback-driven personalization

---

# 15. My strongest recommendations for your case

If you want the shortest path to something genuinely valuable, prioritize these 8 items:

1. **Use LLMs for stock-event impact classification, not just sentiment**
2. **Change scoring from one raw number to opportunity/risk/confidence**
3. **Add explicit action recommendations with entry/invalidation logic**
4. **Treat KOL as crowding/attention proxy only**
5. **Make explainability first-class**
6. **Use order-book analysis as confirmation/timing, not core thesis**
7. **Store one year of history and build replay/backtest capability**
8. **Plan V2 backtesting early, even if not fully implemented in V1**

---

If you want, next I can do either of these:

### Option C1
I can turn this into a **clean V1/V2/V3 roadmap document** in PDR style, ready to give to engineers.

### Option C2
I can produce a **“revised architecture + revised scoring framework + revised schema”** section to directly replace parts of your current PDR.

### Option C3
I can create a **feature prioritization table** with:
- Must Have
- Should Have
- Nice to Have
- Cut for now

If you want the most practical next step, I recommend **C1**.