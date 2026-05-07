Below is a senior-analyst style review of your PDR based on the attached content.

## Executive view

This is a **strong v1 product design** for a **personal A-share idea-monitoring and scoring workstation**, especially for a local/self-hosted retail-to-pro user. It is clear, implementable, and has sensible modularization: data collection, sentiment, technical analysis, order book analysis, scoring, alerts, and a lightweight UI.

That said, if I review it through a **hedge fund / professional research** lens, the current design is still more of a **signal dashboard** than a true **investment research agent**. It is useful for monitoring and triage, but not yet strong enough for robust decision support unless you tighten:
- data quality and source reliability,
- methodology for scoring,
- event/entity mapping,
- backtesting and calibration,
- explainability,
- regime awareness,
- risk controls,
- and market microstructure realism.

Also, some “cutting-edge” elements are missing that would make this system much more differentiated:
- retrieval-augmented research workflows,
- event extraction and knowledge graph,
- factor-aware scoring,
- probabilistic forecasting instead of simple point scores,
- multimodal/LLM-based summarization with evidence citations,
- online learning / model recalibration,
- and proper evaluation pipelines.

---

# 1. What is already good

## 1.1 Clear product scope
You constrained the universe:
- China A-shares
- ~25 leading names
- selected thematic sectors

That is good. Small universe = feasible, controllable, and easier to validate.

## 1.2 Good modular decomposition
The separation into:
- collector,
- analyzer,
- scoring engine,
- UI,
- alerts

is correct and practical.

## 1.3 Reasonable first-pass dimensions
Your chosen signal buckets are intuitive:
- technicals
- news sentiment
- KOL sentiment
- order-book behavior
- macro

For a v1 discretionary assistant, this is sensible.

## 1.4 Local deployment choice is practical
Using:
- FastAPI
- SQLite
- APScheduler
- plain HTML/CSS/JS

is fine for a prototype or single-user local workstation.

## 1.5 Alerting focus is useful
The alert logic around:
- score jumps,
- threshold crossings,
- major announcements,
- unusual order flow,
- technical breakouts

is directly actionable.

---

# 2. Main weaknesses / gaps

## 2.1 The objective is not sharply defined
The PDR says the output is a score from -10 to +10 and trading signals. But **what exactly is the system optimizing for?**

A hedge fund would ask:
- Predict next-day return?
- Predict 3-day excess return?
- Predict probability of breakout?
- Predict odds of event-driven continuation?
- Improve analyst productivity rather than forecast returns?
- Generate ideas, not execution signals?

Right now, the score is a blend of intuition, but not tied to a specific target.

### Why this matters
If the target is unclear, then:
- you cannot calibrate weights,
- you cannot backtest correctly,
- you cannot know whether a score of +6 is meaningful,
- and alerts may become noisy.

### Suggestion
Define the target explicitly, for example:
- **Primary target:** next 1–3 trading day directional edge
- **Secondary target:** idea prioritization for discretionary review
- **Tertiary target:** event monitoring and alerting

Then define how each module supports that target.

---

## 2.2 Scoring weights are arbitrary
The weights:
- tech 30%
- news 20%
- KOL 15%
- order book 25%
- macro 10%

are plausible, but they are **hand-set**. That is acceptable for a v0, but a professional setup should not stop there.

### Suggestion
Convert the scoring framework into:
- **rule-based initialization** for v1
- then **backtest-driven calibration**
- then potentially **regime-dependent dynamic weighting**

For example:
- in high-dispersion event weeks, news/event scores matter more
- in low-news environments, technicals/order flow may dominate
- in policy-sensitive sectors, macro should carry more weight

Use:
- rolling IC / hit-rate
- precision by alert type
- score bucket return analysis
- sector/regime conditional performance

---

## 2.3 Sentiment analysis is too shallow as written
The PDR frames sentiment as:
- positive / negative / neutral
- score from -5 to +5

This is too simplistic for China equities research.

### Why
Market-relevant text is not just “sentiment.” It includes:
- policy direction
- order/booking growth
- margin pressure
- regulation risk
- export controls
- subsidy changes
- product launch success
- capex and financing risk
- management credibility
- industry demand inflection
- channel checks
- inventory destocking/restocking
- military procurement cycle
- reimbursement policy in biotech/healthcare

A title can sound positive but be poor for equity value, and vice versa.

### Suggestion
Upgrade this from basic sentiment to **financial event and thesis classification**.

Instead of only outputting sentiment, extract:
- entity: stock / sector / supplier / customer / regulator
- event type: earnings, guidance, order win, policy support, regulation, product launch, M&A, financing, litigation, executive change
- impact direction: positive / negative / mixed
- impact horizon: intraday / short-term / medium-term
- confidence
- evidence spans / citations

This is much more useful than generic sentiment.

---

## 2.4 KOL data is dangerous unless credibility-weighted
Using Weibo KOL data is interesting, but raw KOL sentiment can introduce significant noise and manipulation risk.

### Risks
- pump-and-dump behavior
- herd reinforcement
- low-information reposts
- anonymous rumors
- fake expertise
- delayed reactions already in price

### Suggestion
Create a **KOL credibility model**:
- historical hit rate
- sector specialization
- timeliness
- originality
- engagement quality, not just volume
- rumor frequency
- consistency over time

Then KOL input should be:
- credibility-weighted,
- capped,
- and possibly used as a **sentiment dispersion / crowding** signal rather than direct alpha.

In many cases, KOL activity is more useful as:
- retail crowding proxy,
- narrative acceleration indicator,
- or “attention shock” metric.

---

## 2.5 Order book / five-level quote analysis is under-specified
Your order book section mentions:
- large order identification,
- buy/sell force ratio,
- net inflow,
- accumulation/distribution/testing patterns

This is directionally good, but five-level data alone is limited.

### Missing realities
In A-shares, microstructure analysis can be distorted by:
- spoofing / fake orders
- rapid cancels
- auction effects
- midday liquidity shifts
- small-cap behavior
- board-specific rules
- price limit dynamics
- opening/closing call auction behavior

### Suggestion
Upgrade microstructure analysis with:
- order imbalance over rolling windows
- cancel ratio
- quote revision rate
- spread and depth dynamics
- intraday VWAP distance
- abnormal turnover vs historical intraday profile
- auction-specific features
- large-trade persistence
- price response after large prints
- limit-up/limit-down proximity logic

If only five-level data is available, be realistic and present this module as **order-book pressure proxy**, not “institutional behavior” certainty.

That wording matters. You cannot infer institution behavior reliably from top-of-book snapshots alone.

---

## 2.6 Technical analysis is fine for retail workflow, but weak for institutional robustness
The indicators listed are classic retail indicators:
- MA
- MACD
- DMI
- RSI
- KDJ
- BIAS
- VOL
- OBV
- VR

Useful for a dashboard, yes. But from a hedge-fund perspective, these are not enough and some are redundant.

### Suggestion
Add more robust market features:
- relative strength vs sector/index
- gap behavior
- realized volatility
- ATR
- trend persistence
- cross-sectional momentum
- volume surprise
- turnover percentile
- breakout strength normalized by volatility
- drawdown recovery velocity
- support/resistance from volume profile
- overnight vs intraday return decomposition

Also, do not rely on indicators alone. Focus on:
- features
- predictive usefulness
- and explainable mapping to outcomes

---

## 2.7 No fundamentals / valuation / earnings model
For a “stock analyst agent,” the absence of structured fundamental analysis is a major limitation.

You have:
- annual reports / announcements
- macro
- technicals
- news

But no explicit module for:
- earnings revisions
- valuation multiples
- guidance changes
- analyst consensus drift
- margin trends
- cash flow quality
- balance sheet stress
- shareholder dilution
- inventory/receivables trends
- capex cycle
- ROIC or profitability quality

### Suggestion
Add a **fundamental/event research module**, even if basic:
- parse earnings reports and announcements
- extract revenue/profit growth
- margins
- guidance change
- unusual items
- pledge ratio / shareholder reductions
- buyback / private placement / convertible bond issuance
- sector-specific KPIs

This will materially improve research quality.

---

## 2.8 No backtesting or evaluation framework
This is the biggest professional gap.

You have verification for whether the system runs, but not whether it is useful.

### Need to add
A proper evaluation section:
- score bucket forward returns
- hit rate by score threshold
- precision/recall of alerts
- confusion matrix on directional calls
- stability of sentiment labels
- false positive rate around major events
- latency from event publication to alert
- contribution analysis by module

### Suggestion
Add an explicit **Research Evaluation & Model Validation** section:
- in-sample vs out-of-sample periods
- walk-forward testing
- sector-level performance
- high-volatility vs low-volatility regimes
- turnover/noise sensitivity
- ablation tests for each module

Without this, the system is a UI product, not an investment-grade research tool.

---

## 2.9 Database schema has some structural issues
A few items need refinement.

### Examples
#### daily_quotes
```sql
date DATE UNIQUE
```
This is wrong if multiple stocks share the same table. It should be unique on `(stock_id, date)`.

#### scores
```sql
date DATE UNIQUE
```
Also should be unique on `(stock_id, date)`.

#### Missing foreign keys / indexes
You should add:
- foreign keys
- indexes on timestamps
- indexes on stock_id + time
- source/url unique constraints where relevant

#### order_book storage
Storing every 5 seconds in SQLite can get large quickly. For local use with 25 stocks, it may still become unwieldy.

### Suggestion
For high-frequency-like data:
- either aggregate features into 1-minute bars,
- or retain raw snapshots for short retention only,
- or use DuckDB / Parquet for analytical storage.

SQLite is okay for metadata and low-frequency tables, but not ideal for sustained frequent snapshots.

---

## 2.10 Some data acquisition assumptions may be fragile
Web scraping:
- Sina
- Eastmoney
- CNINFO
- Weibo

can break often and may have anti-bot protections, HTML changes, and legal/compliance concerns.

### Suggestion
In the PDR, distinguish data sources by reliability tier:
- **Tier 1:** exchange/API/direct structured sources
- **Tier 2:** semi-structured trusted media
- **Tier 3:** social and scraped sources

Then define fallbacks, retries, parser versioning, and monitoring.

Also specify:
- deduplication
- source priority
- timestamp normalization
- content hashing
- entity matching rules

---

# 3. Questions I would ask before finalizing the PDR

These are the key unclear points.

## 3.1 What exactly is the prediction horizon?
Choose one or more:
- intraday
- next day
- next 3 days
- next week

This changes the entire feature set and weighting.

## 3.2 Is this meant for:
- idea generation,
- monitoring,
- swing trading,
- event trading,
- or quasi-systematic signal ranking?

Right now it blends several use cases.

## 3.3 What market data access do you actually have?
Specifically:
- Which quote API?
- Does it provide tick/trade prints or only five-level snapshots?
- Does it include historical intraday data?
- Does it provide order cancellation info?
- Are there rate limits?

## 3.4 How will stock-news mapping work?
If a news item mentions:
- a sector,
- a supplier,
- a customer,
- a government policy,
- or a product category,

how do you map that to impacted stocks?

This is one of the most important parts and currently underdefined.

## 3.5 What is the exact role of KOLs?
Are KOLs:
- alpha source,
- sentiment confirmation,
- crowd proxy,
- or rumor detection source?

I would not treat them equally with news unless validated.

## 3.6 How much history do you plan to retain?
Especially for:
- order book snapshots,
- news,
- score history,
- features

This affects storage design.

## 3.7 What level of automation do you want for trading decisions?
Will the system:
- only show scores,
- suggest actions,
- generate a watchlist,
- or recommend entries/exits?

If it suggests trades, risk controls need to be far more explicit.

## 3.8 Do you want explainability?
For each score, should the system answer:
- why is this stock +6.5?
- what changed today?
- what evidence supports the score?
- what could invalidate the thesis?

This is very important in practice.

## 3.9 Which deployment OS?
The document asks this as an open question, but architecture may differ:
- Windows local retail box
- Mac laptop
- Linux mini-server

For scraping, scheduling, and browser automation, this matters.

## 3.10 How much LLM usage is allowed?
You mention local NLP model, but not whether:
- local Chinese LLMs,
- cloud APIs,
- embeddings,
- rerankers,
- or OCR for PDF filings

are allowed.

This matters a lot for the best architecture.

---

# 4. Suggested improvements to the PDR

## 4.1 Reframe the product goal
I would rewrite the objective like this:

> Build a local research copilot for a focused China A-share universe that continuously ingests market, news, filings, and social narrative data; transforms them into explainable event/factor signals; ranks stocks by short-horizon opportunity/risk; and alerts the user to material thesis changes.

This is stronger than “score from -10 to +10.”

---

## 4.2 Add a “Decision Use Cases” section
Split the product into use cases:
1. **Morning prep**
   - what happened overnight?
   - what matters to my 25 names?
2. **Intraday monitoring**
   - unusual order-book pressure
   - narrative shock
   - breakout / breakdown
3. **Post-close review**
   - score changes
   - event recap
   - next-day watchlist
4. **Research drill-down**
   - why is a stock ranked high/low?
   - what evidence and contradictions exist?

This makes the product much more concrete.

---

## 4.3 Replace “sentiment” with “event + stance + impact”
A better output schema for textual data:

- entity
- document type
- topic
- event type
- stance / impact direction
- confidence
- novelty
- expected horizon
- cited evidence
- linked stocks
- linked sector

This is much more powerful than positive/neutral/negative alone.

---

## 4.4 Add an “evidence-based explanation layer”
For every stock score, show:
- top 3 positive drivers
- top 3 negative drivers
- what changed vs yesterday
- confidence level
- supporting documents/posts
- contradictory evidence

This is critical for trust.

---

## 4.5 Introduce confidence and uncertainty
Instead of only a score:
- total score: +6.2
- confidence: medium
- uncertainty: elevated
- data freshness: good / stale

This is more realistic and professional.

---

## 4.6 Add regime detection
The same signals do not work in all regimes.

Add a module that classifies:
- trend regime
- volatility regime
- policy-sensitive regime
- risk-on / risk-off environment
- sector leadership regime

Then adapt weights or interpretation.

---

## 4.7 Add sector-relative scoring
Absolute stock scoring is less informative than:
- stock vs sector peers
- sector vs market
- stock’s change in rank over time

For a 25-stock universe across themes, relative ranking is extremely useful.

---

## 4.8 Expand alert taxonomy
Current alerts are okay, but I would add:
- **novel event alert**: first mention of critical topic
- **contradiction alert**: strong positive price action despite negative news, or vice versa
- **crowding alert**: unusual KOL/news attention spike
- **data quality alert**: stale feed, parser failure, missing API
- **thesis break alert**: a negative event invalidates prior bullish narrative

These are more analyst-grade.

---

# 5. Cutting-edge skills / technologies to add

Here are the highest-value modern upgrades.

## 5.1 Retrieval-Augmented Generation for research copilot
Use a RAG architecture so the agent can answer:
- Why did this stock score rise today?
- Summarize all relevant evidence from filings/news/KOLs.
- What are the bullish vs bearish arguments?
- What changed over the last 7 days?

### Recommended stack
- document chunking for news/filings/posts
- embeddings
- vector search
- reranking
- citation-backed answer generation

This greatly improves usability.

---

## 5.2 Knowledge graph / entity-event graph
Build a lightweight graph of:
- stocks
- sectors
- companies
- products
- regulators
- suppliers/customers
- policies
- people/KOLs
- events

Why this matters:
A news item about a supplier, ministry policy, or competitor can still affect your stock universe indirectly. A graph helps map second-order relevance.

Even a simple graph database or graph-like relational layer would help.

---

## 5.3 LLM-based financial information extraction
For Chinese financial text, use an LLM or small domain-tuned model to extract:
- event type
- impact direction
- impacted entities
- time horizon
- confidence
- supporting quote

This is much more useful than keyword matching alone.

You can still keep keyword rules as fallback.

---

## 5.4 Multistage NLP pipeline
A strong modern pipeline:
1. dedupe and clean
2. classify relevance
3. detect entities
4. extract event
5. estimate impact
6. summarize with citations
7. store structured output

This is much better than just one-shot sentiment scoring.

---

## 5.5 Dynamic weighting / online calibration
Rather than fixed manual weights forever, use:
- rolling performance attribution
- Bayesian updating
- online learning
- contextual bandit style weight tuning

Even a simple adaptive scheme would be a major improvement.

---

## 5.6 Probabilistic outputs
Instead of only:
- score = +7

consider:
- probability of positive 3-day return: 68%
- expected move range: +1.5% to +4.0%
- downside tail risk elevated

Professional users often benefit more from probability and uncertainty than raw scores.

---

## 5.7 Feature store + backtest harness
If you want this to become serious, build:
- a feature store
- reproducible signal snapshots
- walk-forward backtesting
- experiment tracking

Suggested tools:
- DuckDB / Parquet for analytics
- MLflow or simple experiment logging
- Prefect or Dagster if workflow grows beyond APScheduler

---

## 5.8 Better local Chinese NLP / LLM stack
Depending on hardware and budget:
- local Chinese embedding models
- reranker model
- local LLM for extraction/summarization
- OCR pipeline for filings/PDFs if needed

If using cloud is allowed, hybrid architecture may be best:
- local storage and orchestration
- cloud LLM for complex extraction and summarization
- local fallback model for privacy/cost control

---

## 5.9 Event study engine
This is very useful and underused.

For each detected event type:
- measure historical forward returns
- by stock / sector / regime
- estimate base rates and dispersion

Then the agent can say:
- “Historically, this event type in this sector led to positive 3-day performance 61% of the time.”

That is much more valuable than generic sentiment.

---

## 5.10 Human-in-the-loop learning
Allow the user to label:
- useful / not useful alert
- right / wrong sentiment/event classification
- important / irrelevant article
- trustworthy / untrustworthy KOL

Then continuously improve relevance and weighting.

This is a very practical edge for a personal system.

---

# 6. Specific comments on technical architecture

## 6.1 SQLite is okay for v1, but consider DuckDB + SQLite split
Recommended:
- **SQLite** for app metadata, settings, alerts, entities
- **DuckDB/Parquet** for time series, analytical features, news corpora, and order-book aggregates

This will scale much better for analysis.

## 6.2 Add a message queue or task abstraction if complexity grows
For v1, APScheduler is fine.
For v2+, consider:
- Redis task queue / Celery / Dramatiq
- or workflow tools like Prefect/Dagster

Especially if scraping, NLP, and scoring become asynchronous and failure-prone.

## 6.3 Add observability
Missing from the PDR:
- structured logging
- task success/failure monitoring
- source freshness checks
- parser failure alerts
- latency metrics

For a live monitoring tool, this is essential.

## 6.4 WebSocket is good, but consider SSE if simpler
For a local app, SSE may be enough for many live updates unless you need full duplex interaction.

---

# 7. Specific database/schema improvements

## Fix uniqueness constraints
Use:
- `UNIQUE(stock_id, date)` for daily_quotes
- `UNIQUE(stock_id, date)` or `UNIQUE(stock_id, timestamp_bucket)` for scores depending on granularity

## Add feature tables
You likely need:
- `document_entities`
- `document_events`
- `technical_features`
- `order_book_features`
- `score_explanations`
- `signal_snapshots`
- `backtest_results`
- `data_source_status`

## Add provenance fields
For extracted insights:
- model version
- prompt/template version
- extraction timestamp
- confidence
- source document IDs

This is important for debugging and trust.

---

# 8. What I would change in the implementation plan

## Current plan issue
The roadmap prioritizes building everything broadly before validating utility.

## Better sequence
### Phase 1
- universe management
- clean schema
- daily quotes + news ingestion
- basic dashboard
- manual score prototype

### Phase 2
- robust entity/event extraction
- explainable score decomposition
- alert engine
- stock-news mapping

### Phase 3
- order-book pressure features
- KOL module with credibility weighting
- macro module
- relative ranking

### Phase 4
- backtesting/evaluation framework
- adaptive weighting
- RAG research assistant
- confidence scoring

### Phase 5
- optimization
- human feedback loop
- regime model
- portfolio/watchlist layer

This ordering reduces wasted build effort.

---

# 9. Recommended rewritten scoring framework

Instead of only five broad components, I’d suggest:

## Core score dimensions
1. **Price/Volume Technical State**
2. **Microstructure Pressure**
3. **News/Event Impact**
4. **Filing/Announcement Impact**
5. **Narrative / Attention / KOL Crowd Signal**
6. **Sector & Macro Regime**
7. **Fundamental Drift / Quality Signal**

Each should produce:
- score contribution
- confidence
- freshness
- top reasons

Then aggregate into:
- total opportunity score
- risk score
- confidence score

That is much more nuanced and useful.

---

# 10. My high-priority recommendations

If you only implement a few improvements, do these first:

## Top 10 priorities
1. **Define the prediction/decision horizon clearly**
2. **Fix the database schema and retention strategy**
3. **Replace simple sentiment with event-impact extraction**
4. **Add explainability for every score**
5. **Add backtesting and evaluation framework**
6. **Treat KOL as credibility-weighted crowd signal, not raw alpha**
7. **Reframe order-book module as pressure proxy unless richer data exists**
8. **Add sector-relative and regime-aware scoring**
9. **Add fundamentals/filings parsing**
10. **Build a lightweight RAG-based research Q&A layer**

---

# 11. Questions for you

Please answer these, and I can give you a sharper revised PDR:

1. What is the main goal:
   - idea generation,
   - swing trading,
   - event monitoring,
   - or ranked signal output?

2. What is the intended holding period:
   - intraday,
   - 1–3 days,
   - 1–2 weeks?

3. Which market data API do you have access to?
   - daily only?
   - tick/trade?
   - five-level snapshots?
   - historical intraday?

4. Are you open to using LLMs locally or via API?

5. Do you want the system to be:
   - fully deterministic/rule-based,
   - hybrid AI + rules,
   - or ML/LLM-first?

6. Are filings/announcements more important to you than KOL/social data, or vice versa?

7. What machine are you running this on?
   - Windows/Mac/Linux
   - CPU only or GPU available?

8. Do you want this system to eventually suggest:
   - watchlist only,
   - entry timing,
   - or full trade opinions?

9. Are you willing to maintain scraped sources, or do you prefer more stable paid APIs?

10. Do you want me to rewrite your PDR into a **more professional v2 version** with:
   - clarified goals,
   - improved architecture,
   - better schema,
   - and added cutting-edge AI components?

If you want, my next step can be one of these:
- **Option A:** rewrite the entire PDR into a stronger hedge-fund-style version
- **Option B:** provide a redlined section-by-section improvement draft
- **Option C:** propose a **v1/v2/v3 roadmap** with practical vs advanced features separated