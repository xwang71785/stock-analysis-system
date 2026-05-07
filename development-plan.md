# 中国A股智能交易研究代理 - 详细开发计划

## 计划概览

| 版本 | 目标 | 预计周期 |
|------|------|----------|
| V1 | 实用的波动交易工作站 | 8-10周 |
| V2 | 研究级系统 | V1稳定后6-8周 |
| V3 | 差异化智能代理 | V2稳定后8-10周 |

---

# V1 开发计划（8-10周）

## V1 目标

构建一个可每日使用的下周波动交易研究工作站，覆盖约25只主题龙头股票。

### V1 核心交付物

- ✅ 完整数据采集管道（新闻/公告/KOL/行情/盘口/宏观）
- ✅ LLM驱动的文档-股票影响分析
- ✅ 机会/风险/信心三维评分引擎
- ✅ 可解释的行动推荐系统
- ✅ Web仪表盘和详情页
- ✅ 实时告警引擎

---

## Phase 0: 环境准备与基础设施数据采集（Week 1-2）

### 0.1 开发环境搭建（Day 1-2）

**任务清单：**
- [ ] 初始化Python项目结构
- [ ] 配置uv/pyenv虚拟环境
- [ ] 安装核心依赖：FastAPI, SQLAlchemy, APScheduler, Pydantic, httpx
- [ ] 配置代码规范工具（ruff, black）
- [ ] 设置Git仓库和.gitignore
- [ ] 创建项目文档结构（docs/, src/, tests/）

**项目结构：**
```
quants-trading-agent/
├── src/
│   ├── api/              # FastAPI路由和中间件
│   ├── collectors/       # 数据采集模块
│   ├── analyzers/        # 分析模块
│   ├── engines/          # 评分和推荐引擎
│   ├── models/           # 数据模型（SQLAlchemy）
│   ├── services/         # 业务逻辑服务
│   ├── utils/           # 工具函数
│   └── config/          # 配置管理
├── frontend/            # 前端静态文件
├── scripts/            # 初始化和迁移脚本
├── tests/              # 测试文件
├── docs/               # 文档
└── docker/             # Docker配置（可选）
```

**验收标准：**
- ✅ 项目结构完整
- ✅ `uv run python -m pytest` 可运行
- ✅ 代码格式化工具正常工作

---

### 0.2 数据库初始化（Day 3-4）

**任务清单：**
- [ ] 设置PostgreSQL数据库（本地或云）
- [ ] 安装DuckDB用于分析存储
- [ ] 创建数据库迁移工具（Alembic）
- [ ] 编写所有表的DDL脚本
- [ ] 创建初始化脚本（股票池、配置）
- [ ] 设置数据库连接池配置

**表创建优先级：**

| 优先级 | 表名 | 用途 |
|--------|------|------|
| P0 | stocks | 股票基本信息 |
| P0 | documents | 统一文档存储 |
| P0 | document_stock_impacts | LLM影响分析结果 |
| P0 | daily_features | 日线特征 |
| P0 | intraday_features | 日内盘口特征 |
| P0 | scores | 评分输出 |
| P0 | recommendations | 推荐结果 |
| P0 | alerts | 告警记录 |
| P1 | crowd_features | KOL人群特征 |
| P1 | score_explanations | 评分解释 |
| P1 | settings | 系统设置 |

**验收标准：**
- ✅ 所有表创建成功
- ✅ 外键约束正确
- ✅ 索引创建完成
- ✅ 初始化脚本可运行

---

### 0.3 配置管理系统（Day 5）

**任务清单：**
- [ ] 设计配置schema（YAML/TOML）
- [ ] 实现配置加载服务
- [ ] 环境变量管理（API密钥、数据库URL）
- [ ] 敏感信息加密存储
- [ ] 配置热重载机制（可选）

**配置项清单：**
```yaml
# 数据库配置
database:
  postgres_url: ${POSTGRES_URL}
  duckdb_path: ./data/duckdb/

# API配置
market_data:
  provider: tushare
  api_key: ${TUSHARE_KEY}

llm:
  provider: openai
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o-mini

# 爬虫配置
crawlers:
  sina:
    enabled: true
    interval: 7200  # 2小时
  eastmoney:
    enabled: true
    interval: 7200
  cninfo:
    enabled: true
    interval: 3600  # 1小时
  weibo:
    enabled: false  # V1.2启用
    interval: 7200

# 调度配置
scheduler:
  data_collection_start: "08:30"
  data_collection_end: "16:30"
  scoring_schedule: "0 17 * * 1-5"  # 每个交易日下午5点

# 告警配置
alerts:
  opportunity_threshold: 70
  risk_threshold: 60
  confidence_threshold: 50
```

**验收标准：**
- ✅ 配置文件结构清晰
- ✅ 环境变量正确加载
- ✅ 敏感信息加密正常

---

### 0.4 基础API框架（Day 6-7）

**任务清单：**
- [ ] 设置FastAPI应用结构
- [ ] 实现健康检查端点
- [ ] 实现API认证中间件（可选）
- [ ] 设置CORS配置
- [ ] 实现统一的响应格式
- [ ] 设置API文档（Swagger）

**核心端点（P0）：**
```python
# 健康检查
GET /health

# 股票相关
GET /api/stocks                    # 获取股票列表
GET /api/stocks/{stock_id}          # 获取股票详情

# 评分相关
GET /api/scores/latest              # 获取最新评分
GET /api/scores/{stock_id}/history  # 获取评分历史

# 文档相关
GET /api/documents                 # 获取文档列表
GET /api/documents/{doc_id}         # 获取文档详情

# 告警相关
GET /api/alerts/unread            # 获取未读告警
PUT /api/alerts/{alert_id}/read   # 标记告警已读

# 设置相关
GET /api/settings                 # 获取设置
PUT /api/settings                 # 更新设置
```

**验收标准：**
- ✅ FastAPI应用正常启动
- ✅ Swagger文档可访问
- ✅ 健康检查端点返回正常

---

## Phase 1: 数据采集模块（Week 3-4）

### 1.1 行情数据采集（Week 3, Day 1-3）

**任务清单：**
- [ ] 设计行情采集基类接口
- [ ] 实现Tushare/东方财富API客户端
- [ ] 日线OHLCV数据采集
- [ ] 历史数据初始化（加载1年历史）
- [ ] 增量数据同步逻辑
- [ ] 数据质量检查（异常值检测）

**采集频率：**
- 日线数据：盘后（收盘后1小时内）
- 逐笔数据：盘后加载当日数据
- 五档盘口：实时（每5秒）

**数据模型：**
```python
@dataclass
class DailyQuote:
    stock_id: int
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    adj_factor: float | None = None
```

**存储策略：**
- PostgreSQL: 存储最新快照
- DuckDB/Parquet: 存储完整历史用于分析

**验收标准：**
- ✅ 能采集25只股票的日线数据
- ✅ 历史数据成功加载到DuckDB
- ✅ 增量同步正常工作
- ✅ 异常数据被过滤或标记

---

### 1.2 实时盘口采集（Week 3, Day 4-5）

**任务清单：**
- [ ] 实现五档盘口采集客户端
- [ ] 设置WebSocket/SSE连接
- [ ] 盘口数据解析和标准化
- [ ] 实时特征聚合（1分钟、5分钟窗口）
- [ ] 盘口特征计算委托
  - 委托不平衡
  - 大单压力
  - 撤单代理
  - VWAP距离
  - 收盘强度

**盘口数据模型：**
```python
@dataclass
class OrderBookSnapshot:
    stock_id: int
    snapshot_time: datetime
    # 买方
    buy1_price: float
    buy1_vol: float
    buy2_price: float
    buy2_vol: float
    buy3_price: float
    buy3_vol: float
    buy4_price: float
    buy4_vol: float
    buy5_price: float
    buy5_vol: float
    # 卖方
    sell1_price: float
    sell1_vol: float
    sell2_price: float
    sell2_vol: float
    sell3_price: float
    sell3_vol: float
    sell4_price: float
    sell4_vol: float
    sell5_price: float
    sell5_vol: float
```

**聚合特征模型：**
```python
@dataclass
class IntradayFeatures:
    stock_id: int
    feature_time: datetime
    order_imbalance: float           # (买量-卖量)/(买量+卖量)
    large_order_pressure: float      # 大单净流入比例
    cancel_ratio_proxy: float       # 估计的撤单比率
    vwap_distance: float          # 当前价格距离VWAP的百分比
    close_strength: float          # 相对日内高点的收盘强度
    liquidity_stress: float       # 流动性压力指标
    pressure_score: float          # 综合压力评分
```

**验收标准：**
- ✅ 盘口数据实时采集正常
- ✅ 特征聚合延迟<5秒
- ✅ 数据存储到DuckDB（保留30天）
- ✅ 特征存储到PostgreSQL（每5分钟聚合一次）

---

### 1.3 新闻采集（Week 3, Day 6-7）

**任务清单：**
- [ ] 新浪财经爬虫实现
- [ ] 东方财富爬虫实现
- [ ] 去重逻辑（基于URL和内容哈希）
- [ ] 时间戳标准化
- [ ] 内容清洗（去除广告、无关内容）
- [ ] 采集失败重试机制
- [ ] Parser健康监控

**爬虫基类设计：**
```python
class BaseCrawler(ABC):
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30)

    @abstractmethod
    async def fetch_news(self) -> List[RawDocument]:
        pass

    @abstractmethod
    async def fetch_content(self, url: str) -> str:
        pass

    async def deduplicate(self, docs: List[RawDocument]) -> List[RawDocument]:
        """基于URL和内容哈希去重"""
        pass
```

**新闻数据模型：**
```python
@dataclass
class Document:
    id: int | None
    source_type: str  # news, filing, macro, kol
    source_name: str  # sina, eastmoney, cninfo, weibo
    title: str
    url: str
    content: str
    author_name: str | None
    published_at: datetime | None
    collected_at: datetime
    content_hash: str  # SHA256
    raw_metadata: dict
```

**采集调度：**
- 开盘前：08:00
- 交易中：每2小时
- 收盘后：15:30

**验收标准：**
- ✅ 新浪和东方财富新闻可采集
- ✅ 去重有效（无重复URL或内容）
- ✅ 失败重试机制正常工作
- ✅ Parser健康状态可监控

---

### 1.4 公告采集（Week 4, Day 1-2）

**任务清单：**
- [ ] 巨潮资讯爬虫实现
- [ ] 解析公告列表和详情
- [ ] 识别公告类型（年报、中报、重大事项等）
- [ ] PDF/HTML内容提取
- [ ] 公告重要性分类

**公告类型识别：**
- 业绩预告/快报
- 年度/半年度/季度报告
- 重大合同/订单
- 股东增减持
- 重大投资/并购
- 分红/送转
- 停牌/复牌
- 其他重大事项

**验收标准：**
- ✅ 巨潮资讯公告可采集
- ✅ 公告类型正确识别
- ✅ PDF/HTML内容成功提取
- ✅ 采集频率符合配置（每小时）

---

### 1.5 宏观数据采集（Week 4, Day 3-4）

**任务清单：**
- [ ] 统计局官网爬虫
- [ ] CPI/PPI数据采集
- [ ] PMI数据采集
- [ ] M2/信贷数据采集
- [ ] 宏观数据标准化存储

**关键指标列表：**
- CPI（居民消费价格指数）
- PPI（生产者价格指数）
- PMI（采购经理指数）
- M2（货币供应量）
- 社融数据（社会融资规模）
- 利率数据（LPR等）

**数据模型：**
```python
@dataclass
class MacroData:
    indicator: str
    value: float
    period: str      # "2024-01"
    published_at: datetime
```

**验收标准：**
- ✅ 关键宏观数据可采集
- ✅ 数据按期次存储
- ✅ 发布时间正确记录

---

### 1.6 KOL采集（Week 4, Day 5-7） - V1.2 可选

**任务清单：**
- [ ] 微博爬虫实现（登录/模拟）
- [ ] 关注KOL列表管理
- [ ] 帖子采集和解析
- [ ] 提及股票识别
- [ ] KOL可信度标记（后续）

**采集策略：**
- 每2小时采集一次
- 关注5-10个高可信度KOL
- 提及股票通过@股票名或股票代码识别

**验收标准：**
- ✅ 微博帖子可采集
- ✅ 提及股票正确识别
- ✅ 数据存储到documents表

---

### 1.7 数据采集调度器（Week 4, Day 完整测试）

**任务清单：**
- [ ] 实现APScheduler配置
- [ ] 定义所有采集任务
- [ ] 任务间依赖管理
- [ ] 失败任务告警
- [ ] 任务执行日志

**调度配置：**
```python
# 开盘前任务
scheduler.add_job(news_crawler.run, 'cron', hour=8, minute=0)
scheduler.add_job(macro_crawler.check_new_releases, 'cron', hour=8, minute=30)

# 交易中任务
scheduler.add_job(news_crawler.run, 'interval', hours=2, start_date='09:30')
scheduler.add_job(filings_crawler.run, 'interval', hours=1, start_date='09:30')
scheduler.add_job(orderbook_collector.start, 'date', run_date=today_open)

# 盘后任务
scheduler.add_job(daily_quotes_collector.run, 'cron', hour=16, minute=0)
scheduler.add_job(scoring_engine.run, 'cron', hour=17, minute=0)
```

**验收标准：**
- ✅ 所有采集任务按计划执行
- ✅ 失败任务产生告警
- ✅ 任务日志完整可查

---

## Phase 2: 文档智能与LLM集成（Week 5）

### 2.1 LLM服务封装（Week 5, Day 1-2）

**任务清单：**
- [ ] LLM客户端抽象层（支持多供应商）
- [ ] OpenAI集成
- [ ] 国内LLM集成（智谱AI/通义千问等）
- [ ] 请求重试和速率限制
- [ ] 响应缓存（基于输入哈希）
- [ ] 成本追踪

**LLM服务接口：**
```python
class LLMService(ABC):
    @abstractmethod
    async def classify_document_impact(
        self,
        document: Document,
        stocks: List[Stock]
    ) -> List[DocumentStockImpact]:
        pass

    @abstractmethod
    async def generate_explanation(
        self,
        stock_id: int,
        scores: Dict[str, float],
        context: dict
    ) -> ScoreExplanation:
        pass
```

**提示词模板：**
```python
# 文档影响分析提示词模板
DOCUMENT_IMPACT_PROMPT = """
你是一位专业的中国A股分析师。请分析以下文档对股票池的影响。

股票池：
{stocks_info}

文档信息：
- 标题：{title}
- 来源：{source}
- 发布时间：{published_at}
- 内容：{content}

请输出JSON格式：
{{
  "impacts": [
    {{
      "stock_code": "股票代码",
      "relevance_score": 0.0-1.0,
      "relevance_type": "direct/indirect/sector/market",
      "impact_direction": "positive/negative/mixed/neutral",
      "impact_strength": "weak/medium/strong",
      "impact_horizon": "intraday/2_5d/1_2w",
      "event_type": "事件类型",
      "confidence": "low/medium/high",
      "explanation": "简短解释",
      "evidence_snippet": "关键证据句"
    }}
  ]
}}
"""
```

**验收标准：**
- ✅ LLM服务正常调用
- ✅ 响应解析正确
- ✅ 失败自动重试
- ✅ 成本追踪准确

---

### 2.2 文档-股票影响分析（Week 5, Day 3-4）

**任务清单：**
- [ ] 实现基于规则的预筛选（股票名称/代码匹配）
- [ ] LLM影响分析流程
- [ ] 结果后处理和验证
- [ ] 批量处理优化
- [ ] 结果存储到数据库

**分析流程：**
```
1. 文档采集 → 存入documents表
2. 规则预筛选 → 识别可能相关的股票
3. LLM深度分析 → 生成详细影响分析
4. 结果验证 → 置信度检查
5. 存储结果 → document_stock_impacts表
```

**性能优化：**
- 对非相关文档跳过LLM调用
- 批量处理提高效率
- 缓存相似文档的分析结果

**验收标准：**
- ✅ 相关文档能被正确识别
- ✅ LLM分析结果结构正确
- ✅ 影响分析存储到数据库
- ✅ 处理延迟<5分钟/文档

---

### 2.3 文档处理管道（Week 5, Day 5）

**任务清单：**
- [ ] 端到端文档处理流程
- [ ] 处理状态跟踪
- [ ] 失败文档重试队列
- [ ] 处理性能监控

**处理状态：**
```python
class DocumentStatus(Enum):
    PENDING = "pending"
    PRE_FILTERING = "pre_filtering"
    LLM_ANALYSIS = "llm_analysis"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

**验收标准：**
- ✅ 文档处理流程完整
- ✅ 失败文档可重试
- ✅ 处理状态可查询

---

## Phase 3: 特征工程模块（Week 6）

### 3.1 技术指标计算（Week 6, Day 1-2）

**任务清单：**
- [ ] 移动平均线计算（MA 5/10/20/60）
- [ ] 趋势斜率计算
- [ ] RSI计算
- [ ] ATR计算
- [ ] 相对强度计算（vs 行业指数）
- [ ] 突破检测
- [ ] 价格形态识别

**技术特征列表：**
```python
@dataclass
class TechnicalFeatures:
    stock_id: int
    trade_date: date

    # 趋势
    ma5: float
    ma10: float
    ma20: float
    ma60: float
    trend_slope: float

    # 相对强度
    rs_vs_sector: float
    rs_vs_index: float

    # 波动
    atr: float
    atr_pct: float
    volatility_score: float

    # 动量
    rsi: float

    # 突破
    breakout_20d: bool
    breakdown_20d: bool
    gap_up: bool
    gap_down: bool

    # 量能
    volume_surprise: float
    turnover_percentile: float
    price_volume_confirmed: bool
```

**验收标准：**
- ✅ 所有技术指标计算正确
- ✅ 与专业软件结果验证
- ✅ 存储到daily_features表

---

### 3.2 盘口特征聚合（Week 6, Day 3-4）

**任务清单：**
- [ ] 委托不平衡计算
- [ ] 大单压力计算
- [ ] 撤单代理估算
- [ ] VWAP计算
- [ ] 收盘强度计算
- [ ] 流动性压力计算
- [ ] 综合压力评分

**特征计算方法：**
```python
# 委托不平衡
def calc_order_imbalance(order_book: OrderBookSnapshot) -> float:
    bid_vol = sum([order_book.buy1_vol, order_book.buy2_vol, ...])
    ask_vol = sum([order_book.sell1_vol, order_book.sell2_vol, ...])
    return (bid_vol - ask_vol) / (bid_vol + ask_vol + 1e-6)

# 大单压力
def calc_large_order_pressure(
    snapshots: List[OrderBookSnapshot],
    large_threshold: float = 100_000
) -> float:
    pressure = 0
    for snap in snapshots:
        # 识别大单
        large_bid = sum(v for p, v in snap.bids if v > large_threshold)
        large_ask = sum(v for p, v in snap.asks if v > large_threshold)
        pressure += (large_bid - large_ask) / (large_bid + large_ask + 1e-6)
    return pressure / len(snapshots)

# 撤单代理（通过快照差异估算）
def calc_cancel_ratio_proxy(
    current: OrderBookSnapshot,
    previous: OrderBookSnapshot
) -> float:
    # 估算被撤单的比例
    return estimate_canceled_ratio(current, previous)
```

**验收标准：**
- ✅ 所有盘口特征正确计算
- ✅ 实时更新延迟<5秒
- ✅ 聚合结果存储到intraday_features表

---

### 3.3 KOL人群特征（Week 6, Day 5）- V1.2 可选

**任务清单：**
- [ ] KOL提及统计
- [ ] 关注度突增检测
- [ ] 人群情绪计算
- [ ] 情绪离散度计算
- [ ] 拥挤风险评分

**人群特征模型：**
```python
@dataclass
class CrowdFeatures:
    stock_id: int
    feature_date: date

    mention_count: int                  # 提及次数
    attention_spike_score: float        # 关注度突增
    crowd_sentiment_score: float        # 人群情绪
    sentiment_dispersion: float        # 情绪离散度
    crowding_risk_score: float        # 拥挤风险
```

**验收标准：**
- ✅ KOL提及正确统计
- ✅ 突增检测准确
- ✅ 特征存储到crowd_features表

---

### 3.4 特征工程服务集成（Week 6, Day 完整测试）

**任务清单：**
- [ ] 统一特征计算服务
- [ ] 特征缓存机制
- [ ] 特征质量检查
- [ ] 特征缺失值处理

**验收标准：**
- ✅ 所有特征按计划计算
- ✅ 特征可追溯（版本控制）
- ✅ 质量检查通过

---

## Phase 4: 评分与推荐引擎（Week 7）

### 4.1 评分框架实现（Week 7, Day 1-2）

**任务清单：**
- [ ] 机会分数计算引擎
- [ ] 风险分数计算引擎
- [ ] 信心分数计算引擎
- [ ] 分数组件归一化
- [ ] 权重配置管理

**评分权重配置：**
```python
SCORE_WEIGHTS = {
    # 机会分数权重
    "opportunity": {
        "event_impact": 0.30,
        "trend_structure": 0.25,
        "volume_participation": 0.15,
        "order_flow_pressure": 0.15,
        "sector_macro_regime": 0.10,
        "crowd_attention": 0.05,
    },
    # 风险分数权重
    "risk": {
        "crowding_spike": 0.20,
        "negative_events": 0.30,
        "failed_confirmation": 0.20,
        "volatility_liquidity": 0.15,
        "macro_uncertainty": 0.15,
    },
    # 信心分数权重
    "confidence": {
        "signal_agreement": 0.30,
        "data_freshness": 0.20,
        "llm_confidence": 0.20,
        "source_quality": 0.15,
        "price_narrative_alignment": 0.15,
    }
}
```

**评分计算示例：**
```python
def calculate_opportunity_score(
    event_impact: float,
    trend_structure: float,
    volume_participation: float,
    order_flow_pressure: float,
    sector_macro_regime: float,
    crowd_attention: float,
) -> float:
    weights = SCORE_WEIGHTS["opportunity"]
    score = (
        event_impact * weights["event_impact"] +
        trend_structure * weights["trend_structure"] +
        volume_participation * weights["volume_participation"] +
        order_flow_pressure * weights["order_flow_pressure"] +
        sector_macro_regime * weights["sector_macro_regime"] +
        crowd_attention * weights["crowd_attention"]
    )
    return min(max(score * 100, 0), 100)  # 归一化到0-100
```

**验收标准：**
- ✅ 三个分数正确计算
- ✅ 权重可配置
- ✅ 分数范围在0-100
- ✅ 分数存储到scores表

---

### 4.2 推荐引擎实现（Week 7, Day 3-4）

**任务清单：**
- [ ] 推荐规则引擎
- [ ] 推荐状态机
- [ ] 入场条件生成
- [ ] 失效逻辑生成
- [ ] 推荐历史跟踪

**推荐类型：**
```python
class RecommendationAction(Enum):
    STRONG_LONG = "strong_long"      # 强力做多
    WATCH_LONG = "watch_long"        # 观察做多
    NEUTRAL = "neutral"             # 中性
    AVOID = "avoid"                # 避免
    REDUCE_EXIT = "reduce_exit"     # 减仓/出场

class RecommendationStance(Enum):
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
```

**推荐规则：**
```python
def generate_recommendation(
    opportunity: float,
    risk: float,
    confidence: float,
    trend_structure: dict,
    event_impact: dict,
    order_flow: dict,
) -> Recommendation:
    # 强力做多
    if (opportunity >= 70 and
        risk <= 50 and
        confidence >= 60 and
        event_impact.get("direction") == "positive" and
        trend_structure.get("status") == "uptrend"):
        return Recommendation(
            stance=RecommendationStance.BULLISH,
            action=RecommendationAction.STRONG_LONG,
            entry_condition="当前价格已突破，可考虑入场",
            invalidation_level=trend_structure.get("support_level"),
            target_hint="目标价前高或+5%",
            confidence="medium_to_high"
        )

    # 观察做多
    elif (opportunity >= 60 and
          trend_structure.get("status") in ["uptrend", "consolidation"]):
        return Recommendation(
            stance=RecommendationStance.BULLISH,
            action=RecommendationAction.WATCH_LONG,
            entry_condition="等待放量突破或回踩支撑",
            invalidation_level=trend_structure.get("support_level"),
            target_hint="视突破情况决定",
            confidence="medium"
        )

    # 中性
    elif opportunity < 60 and opportunity > 40:
        return Recommendation(
            stance=RecommendationStance.NEUTRAL,
            action=RecommendationAction.NEUTRAL,
            entry_condition="等待更明确的信号",
            invalidation_level=None,
            target_hint=None,
            confidence="low"
        )

    # 避免
    elif (opportunity <= 40 or
          risk >= 70 or
          confidence < 40):
        return Recommendation(
            stance=RecommendationStance.BEARISH if risk > 60 else RecommendationStance.NEUTRAL,
            action=RecommendationAction.AVOID,
            entry_condition=None,
            invalidation_level=None,
            target_hint=None,
            confidence="low"
        )

    # 减仓/出场
    elif (event_impact.get("direction") == "negative" and
          confidence >= 50):
        return Recommendation(
            stance=RecommendationStance.BEARISH,
            action=RecommendationAction.REDUCE_EXIT,
            entry_condition=None,
            invalidation_level=None,
            target_hint="考虑止盈/止损",
            confidence="medium"
        )
```

**验收标准：**
- ✅ 推荐规则正确执行
- ✅ 推荐历史可追溯
- ✅ 推荐存储到recommendations表

---

### 4.3 可解释性引擎（Week 7, Day 5）

**任务清单：**
- [ ] 驱动因素提取
- [ ] 前3看涨/看跌因素识别
- [ ] 变化检测（vs 前日）
- [ ] LLM解释生成
- [ ] 解释存储

**解释模型：**
```python
@dataclass
class ScoreExplanation:
    stock_id: int
    explanation_time: datetime

    top_positive_factors: List[dict]  # [{"factor": "...", "value": 0.8}]
    top_negative_factors: List[dict]
    changes_from_prior: dict
    supporting_document_ids: List[int]
    contradiction_flags: List[str]
    narrative_summary: str
```

**驱动因素提取：**
```python
def extract_top_factors(
    components: Dict[str, float],
    weights: Dict[str, float]
) -> List[dict]:
    """提取贡献度最高的因素"""
    factors = []
    for name, value in components.items():
        contribution = value * weights.get(name, 0)
        factors.append({
            "factor": name,
            "value": value,
            "contribution": contribution
        })
    return sorted(factors, key=lambda x: abs(x["contribution"]), reverse=True)[:3]
```

**验收标准：**
- ✅ 前3因素正确提取
- ✅ 变化检测准确
- ✅ 解释存储到score_explanations表

---

## Phase 5: Web前端（Week 8）

### 5.1 前端框架搭建（Week 8, Day 1-2）

**任务清单：**
- [ ] HTML基础模板
- [ ] CSS样式框架（使用Tailwind CSS CDN）
- [ ] JavaScript模块化结构
- [ ] API客户端封装
- [ ] 状态管理
- [ ] 路由实现

**前端结构：**
```
frontend/
├── index.html          # 主入口
├── css/
│   └── styles.css      # 样式文件
├── js/
│   ├── api.js          # API客户端
│   ├── state.js       # 状态管理
│   ├── dashboard.js    # 仪表盘
│   ├── stock-detail.js # 股票详情
│   ├── documents.js    # 文档流
│   ├── alerts.js      # 告警
│   └── utils.js       # 工具函数
└── assets/            # 静态资源
```

**API客户端：**
```javascript
class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    async get(path, params = {}) {
        const url = new URL(path, this.baseUrl);
        Object.keys(params).forEach(key =>
            url.searchParams.append(key, params[key])
        );
        const response = await fetch(url);
        return response.json();
    }

    async post(path, data) {
        const response = await fetch(path, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        return response.json();
    }

    // 股票相关
    async getStocks() { return this.get('/stocks'); }
    async getStockDetail(stockId) { return this.get(`/stocks/${stockId}`); }

    // 评分相关
    async getLatestScores() { return this.get('/scores/latest'); }
    async getScoreHistory(stockId) { return this.get(`/scores/${stockId}/history`); }

    // 告警相关
    async getUnreadAlerts() { return this.get('/alerts/unread'); }
    async markAlertRead(alertId) { return this.put(`/alerts/${alertId}/read`); }
}
```

**验收标准：**
- ✅ 前端结构完整
- ✅ API客户端正常工作
- ✅ 路由切换正常

---

### 5.2 仪表盘页面（Week 8, Day 3-4）

**任务清单：**
- [ ] 股票评分列表展示
- [ ] 排序和筛选功能
- [ ] 机会/风险/信心分数可视化
- [ ] Top 5做多/做空排行榜
- [ ] 行业对比视图
- [ ] 实时数据更新（WebSocket）

**仪表盘布局：**
```
┌─────────────────────────────────────────────────────────┐
│  中国A股智能交易研究代理                    [设置]   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ Top 5 做多  │  │ Top 5 风险 │  │ 宏观快照  │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
├─────────────────────────────────────────────────────────┤
│  股票评分列表                                       │
│  ┌─────┬──────┬──────┬──────┬──────┬─────────┐ │
│  │代码 │ 名称 │机会分│风险分│信心分│ 推荐   │ │
│  ├─────┼──────┼──────┼──────┼──────┼─────────┤ │
│  │600000│ 浦发 │  78  │  35  │  72  │ 强力做多│ │
│  │...  │ ...  │ ...  │ ...  │ ...  │ ...     │ │
│  └─────┴──────┴──────┴──────┴──────┴─────────┘ │
└─────────────────────────────────────────────────────────┘
```

**评分可视化：**
- 机会分：绿色进度条
- 风险分：红色进度条
- 信心分：蓝色进度条

**验收标准：**
- ✅ 股票列表正确显示
- ✅ 排序/筛选功能正常
- ✅ 实时更新正常

---

### 5.3 股票详情页（Week 8, Day 5-6）

**任务清单：**
- [ ] 股票基本信息展示
- [ ] 评分详情和构成
- [ ] 价格走势图（使用ECharts）
- [ ] 技术指标图表
- [ ] 盘口压力分析
- [ ] 前3看涨/看跌驱动因素
- [ ] 相关文档列表

**详情页布局：**
```
┌─────────────────────────────────────────────────────────┐
│  600000 浦发银行                                 │
├─────────────┬───────────────────────────────────────┤
│  评分       │  价格走势图                         │
│  ┌───────┐ │  ┌───────────────────────────────┐    │
│  │机会:78│ │  │                           │    │
│  │风险:35│ │  │   [图表]                   │    │
│  │信心:72│ │  │                           │    │
│  └───────┘ │  └───────────────────────────────┘    │
│  推荐：强力做多                                    │
│  入场：当前价格已突破                              │
│  失效：8.50                                       │
├─────────────┼───────────────────────────────────────┤
│  看涨因素   │  相关文档                          │
│  1. 业绩超预期       │  • [公告] 2024Q3业绩预增... │
│  2. 大单持续流入     │  • [新闻] 获重大银行...      │
│  3. 突破关键阻力     │  • [KOL] 建议关注...         │
├─────────────┼───────────────────────────────────────┤
│  看跌因素   │  盘口压力                          │
│  1. 行业整体偏弱     │  买压：↑↑                 │
│  2. 宏观流动性紧张     │  大单：净流入              │
│  3. 换手率过高        │  撤单：正常               │
└─────────────┴───────────────────────────────────────┘
```

**验收标准：**
- ✅ 详情页信息完整
- ✅ 图表正常渲染
- ✅ 文档列表正确显示

---

### 5.4 其他页面（Week 8, Day 7）

**任务清单：**
- [ ] 文档流页面
- [ ] KOL动态页面
- [ ] 宏观指标页面
- [ ] 设置页面
- [ ] 告警通知弹窗

**验收标准：**
- ✅ 所有页面正常显示
- ✅ 页面间导航正常

---

## Phase 6: 告警引擎（Week 9）

### 6.1 告警规则引擎（Week 9, Day 1-2）

**任务清单：**
- [ ] 告警类型定义
- [ ] 告警规则配置
- [ ] 条件检查器
- [ ] 告警去重
- [ ] 告警优先级

**告警类型：**
```python
class AlertType(Enum):
    # 事件告警
    MATERIAL_FILING = "material_filing"
    HIGH_IMPACT_NEWS = "high_impact_news"
    POLICY_NEWS = "policy_news"

    # 评分告警
    OPPORTUNITY_CROSS = "opportunity_cross"
    RISK_SPIKE = "risk_spike"
    CONFIDENCE_DROP = "confidence_drop"
    RECOMMENDATION_CHANGE = "recommendation_change"

    # 价格/结构告警
    BREAKOUT_CONFIRMED = "breakout_confirmed"
    FAILED_BREAKOUT = "failed_breakout"
    WEAK_CLOSE = "weak_close"

    # 人群/风险告警
    ATTENTION_SPIKE = "attention_spike"
    CROWDING_RISK = "crowding_risk"
    THESIS_CONTRADICTION = "thesis_contradiction"

    # 运营告警
    STALE_DATA = "stale_data"
    PARSER_FAILURE = "parser_failure"
```

**告警规则示例：**
```python
@alert_rule("opportunity_cross", severity="info")
def check_opportunity_cross(stock_id: int) -> Optional[Alert]:
    """检查机会分数跨越阈值"""
    current = get_latest_score(stock_id)
    prior = get_prior_score(stock_id)

    if (current.opportunity >= 70 and prior.opportunity < 70):
        return Alert(
            stock_id=stock_id,
            alert_type=AlertType.OPPORTUNITY_CROSS,
            severity="info",
            title=f"{get_stock_name(stock_id)} 机会分突破70",
            message=f"机会分从 {prior.opportunity:.1f} 升至 {current.opportunity:.1f}",
        )
    return None
```

**验收标准：**
- ✅ 所有告警类型可触发
- ✅ 告警规则可配置
- ✅ 告警去重正常工作

---

### 6.2 告警通知（Week 9, Day 3-4）

**任务清单：**
- [ ] WebSocket实时推送
- [ ] 告警弹窗UI
- [ ] 告警列表页面
- [ ] 已读/未读状态管理
- [ ] 告警历史查询

**WebSocket消息格式：**
```json
{
  "type": "alert",
  "data": {
    "id": 123,
    "stock_id": 1,
    "alert_type": "opportunity_cross",
    "severity": "info",
    "title": "浦发银行 机会分突破70",
    "message": "机会分从 65.0 升至 78.0",
    "created_at": "2024-04-08T10:30:00Z"
  }
}
```

**验收标准：**
- ✅ 实时告警推送正常
- ✅ 告警UI正常显示
- ✅ 已读状态同步

---

### 6.3 告警管理（Week 9, Day 5）

**任务清单：**
- [ ] 告警统计仪表板
- [ ] 告警配置页面
- [ ] 告警静默功能
- [ ] 告警导出

**验收标准：**
- ✅ 告警统计正确
- ✅ 配置可保存

---

## Phase 7: 集成测试与优化（Week 10）

### 7.1 端到端测试（Week 10, Day 1-3）

**测试场景：**

1. **数据采集流程**
   - [ ] 新闻采集 → 去重 → 存储
   - [ ] 公告采集 → LLM分析 → 影响存储
   - [ ] 行情采集 → 特征计算 → 存储
   - [ ] 盘口采集 → 特征聚合 → 存储

2. **分析流程**
   - [ ] 新文档自动触发LLM分析
   - [ ] 特征按计划计算
   - [ ] 评分自动生成

3. **告警流程**
   - [ ] 评分变化触发告警
   - [ ] 实时推送到达前端
   - [ ] 前端正确显示

4. **推荐流程**
   - [ ] 推荐正确生成
   - [ ] 可解释性正确展示

**验收标准：**
- ✅ 所有测试场景通过
- ✅ 无阻塞bug

---

### 7.2 性能优化（Week 10, Day 4-5）

**任务清单：**
- [ ] 数据库查询优化
- [ ] API响应时间优化
- [ ] 前端加载优化
- [ ] LLM调用优化（批量、缓存）

**性能目标：**
| 指标 | 目标 |
|------|------|
| API响应时间 | <200ms (P50) |
| 数据库查询 | <100ms (P50) |
| 页面加载时间 | <2s |
| 盘口特征延迟 | <5s |

**验收标准：**
- ✅ 性能目标达成

---

### 7.3 用户体验优化（Week 10, Day 6）

**任务清单：**
- [ ] UI细节调整
- [ ] 错误提示优化
- [ ] 加载状态优化
- [ ] 响应式布局调整

**验收标准：**
- ✅ 用户体验流畅

---

### 7.4 文档与部署准备（Week 10, Day 7）

**任务清单：**
- [ ] 更新README.md
- [ ] 编写部署文档
- [ ] 编写用户手册
- [ ] 创建Docker Compose配置
- [ ] 准备配置模板

**验收标准：**
- ✅ 文档完整
- ✅ 可直接部署

---

# V2 开发计划（V1稳定后6-8周）

## V2 目标

使系统更可靠、可回测和差异化。

## V2 主要模块

### 2.1 回测与评估框架（Week 1-2）
- 历史信号快照
- 下周结果对比
- 命中率分析
- 评分桶回报分析
- MFE/MAE计算

### 2.2 动态权重系统（Week 3-4）
- 行业特定权重
- 环境相关权重
- 事件敏感权重
- 权重自适应算法

### 2.3 叙事状态跟踪（Week 5）
- 看涨/看跌叙事维护
- 证据追踪
- 叙事状态判断

### 2.4 公告Parser（Week 5-6）
- 年报解析
- 业绩公告解析
- 重大事项解析
- 结构化事件提取

### 2.5 高级告警（Week 6-7）
- 叙事破裂告警
- 拥挤过载告警
- 事件-价格背离告警
- 失败突破告警

### 2.6 更好的行动框架（Week 7）
- 激进入场
- 确认入场
- 回撤入场
- 部分止盈
- 保护收益

---

# V3 开发计划（V2稳定后8-10周）

## V3 目标

转变为真正的AI分析师副驾驶。

## V3 主要模块

### 3.1 RAG研究副驾驶（Week 1-3）
- 文档向量化
- 向量搜索
- 重排序
- 引用支持的答案生成

### 3.2 事件研究引擎（Week 3-5）
- 历史事件统计
- 环境分层回报
- 基数率计算

### 3.3 概率预测（Week 5-6）
- 正回报概率
- 预期回报范围
- 置信区间

### 3.4 投资组合感知（Week 6-7）
- 相关性分析
- 行业集中度
- 分批入场建议

### 3.5 人工反馈循环（Week 7-8）
- 用户标注收集
- 模型重新训练
- 参数自适应

---

# 附录

## A. 技术依赖清单

```toml
[project]
name = "quants-trading-agent"
version = "0.1.0"
requires-python = ">=3.11"

[dependencies]
# Web框架
fastapi = ">=0.100"
uvicorn = ">=0.23"
websockets = ">=12"

# 数据库
sqlalchemy = ">=2.0"
psycopg2-binary = ">=2.9"
duckdb = ">=0.9"
alembic = ">=1.12"

# 数据处理
pandas = ">=2.0"
polars = ">=0.19"
numpy = ">=1.24"

# HTTP客户端
httpx = ">=0.24"
aiohttp = ">=3.8"

# 调度
apscheduler = ">=3.10"

# LLM
openai = ">=1.3"

# 爬虫
beautifulsoup4 = ">=4.12"
lxml = ">=4.9"
selenium = ">=4.15"

# 数据验证
pydantic = ">=2.0"
pydantic-settings = ">=2.0"

# 工具
python-dotenv = ">=1.0"
loguru = ">=0.7"
click = ">=8.1"

[dev-dependencies]
pytest = ">=7.4"
pytest-asyncio = ">=0.21"
ruff = ">=0.1"
black = ">=23.7"
mypy = ">=1.5"
```

## B. 环境变量模板

```env
# 数据库
POSTGRES_URL=postgresql://user:password@localhost:5432/quants
DUCKDB_PATH=./data/duckdb/quants.duckdb

# 行情API
TUSHARE_TOKEN=your_token_here

# LLM
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# 或使用国内LLM
ZHIPUAI_API_KEY=your_key_here

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

## C. 数据库初始化SQL

详见 [database_setup.sql](database_setup.sql)

## D. 部署检查清单

- [ ] PostgreSQL已安装并运行
- [ ] 数据库已初始化
- [ ] 环境变量已配置
- [ ] LLM API密钥已设置
- [ ] 行情API已配置
- [ ] 股票池已录入
- [ ] KOL列表已配置
- [ ] 防火墙端口已开放（8000）
- [ ] SSL证书已配置（如需HTTPS）
- [ ] 定时任务已测试
- [ ] 告警通知已测试
