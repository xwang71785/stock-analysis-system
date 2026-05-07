# 中国A股智能交易研究代理 - 产品需求文档 (PDR)

## 1. 产品定位与目标

### 1.1 产品愿景

构建一个本地Linux服务器托管的Web应用，用于**下周波动交易（Swing Trading）**的中国A股研究监控代理。

系统聚焦约25只主题龙头股票，持续监控：
- 日线/日内价格与量能数据
- 五档盘口压力
- 公告/财报/重大新闻
- KOL/人群关注度
- 宏观政策环境

核心能力：
- **事件相关性分析**：自动判断新闻/公告/KOL对目标股票的影响
- **下周机会/风险评估**：生成可解释的评分和行动建议
- **实时监控告警**：在叙事相关变化发生时提醒用户

### 1.2 主要使用场景

| 场景 | 描述 |
|------|------|
| **早盘准备** | 过夜发生了什么？我的25只股票中哪些最重要？ |
| **日内监控** | 异常盘口压力、叙事冲击、突破/破位 |
| **盘后复盘** | 评分变化、事件回顾、次日观察清单 |
| **研究深挖** | 为什么这只股票排名高/低？有哪些证据和矛盾？ |

### 1.3 产品目标

- 主要目标：**下周方向性机会和风险的预估**
- 次要目标：投资想法优先级排序供人工审阅
- 第三目标：事件监控和告警

---

## 2. 产品范围

### 2.1 市场与股票池

| 维度 | 范围 |
|------|------|
| 市场 | 中国A股 |
| 行业主题 | AI、机器人、国防、新能源、生物医药 |
| 股票数量 | ~25只（每行业5只龙头） |
| 用户 | 个人投资者 |
| 部署环境 | Linux服务器本地运行 |

### 2.2 预测/决策时间窗

- **主要时间窗**：1-2周（5-10个交易日）
- **辅助时间窗**：日内（入场时机确认）、2-5天（短期波动）

---

## 3. 产品功能模块

### 3.1 数据采集模块

| 数据源 | 采集内容 | 频率 | 方式 | 可靠性层级 |
|--------|----------|------|------|-----------|
| 巨潮资讯 | 年报/公告 | 每小时检查 | API/网页 | Tier 1 |
| 新浪财经 | 财经新闻 | 开盘前、每2小时、收盘后 | API/网页 | Tier 2 |
| 东方财富 | 财经新闻 | 开盘前、每2小时、收盘后 | API/网页 | Tier 2 |
| 行情API | 日线OHLCV | 盘后更新 | API | Tier 1 |
| 行情API | 五档盘口 | 每5秒 | API | Tier 1 |
| 行情API | 历史逐笔数据 | 盘后加载 | API | Tier 1 |
| 微博 | KOL帖子 | 每2小时 | 网页爬取 | Tier 3 |
| 宏观数据源 | CPI/PMI/M2等 | 按发布时间 | 网页/API | Tier 2 |

**数据质量保障：**
- 去重（基于内容哈希）
- 时间戳标准化
- 来源可靠性标记
- Parser健康监控

---

### 3.2 文档影响分析模块（替代简单情感分析）

#### 目标
超越通用情感分析，判断新闻、公告、宏观数据、KOL帖子对目标股票是否有**实质性影响**，影响方向为**下周波动交易时间窗**。

#### 支持的文档类型
- 财经新闻
- 交易所公告/公司公告
- 宏观政策发布
- KOL/人群帖子

#### 核心功能
对每个文档自动提取：

1. **目标相关性**
   - 该文档是否与跟踪股票池中的某只股票相关？
   - 相关性类型：直接/间接/行业层面/市场层面

2. **影响方向**
   - 正面 / 负面 / 混合 / 中性

3. **影响强度**
   - 弱 / 中 / 强

4. **影响时间窗**
   - 日内 / 2-5天 / 1-2周

5. **事件类型**
   示例：业绩/预增公告、指引变化、重大订单/合同、产品发布/获批、政策支持/限制、融资/定增/可转债、股东增减持、管理层变更、诉讼/监管、供应链/客户/竞争格局变化等

6. **置信度**
   - 低 / 中 / 高

7. **证据提取**
   - 支持分类的关键句
   - LLM生成的结构化解释

#### 处理方式
使用混合流水线：
- 基于规则预处理：去重、来源标准化、股票/实体关键词匹配
- 云端LLM分类：相关性、事件类型、方向、时间窗、置信度、解释

#### 输出
对每个文档-股票对，存储：
- 相关性分数
- 影响方向
- 影响强度
- 影响时间窗
- 事件类型
- 置信度
- 解释
- 证据片段

#### 注意事项
- 此模块替代简单正/负面情感作为主要文本分析机制
- 通用情感可保留为辅助特征，但不作为主要决策变量

---

### 3.3 价格/趋势结构模块（技术面）

#### 推荐特征

**趋势指标**
- MA(5, 10, 20, 60) - 移动平均线
- 趋势斜率
- 20日突破/破位状态
- 相对强度（vs 行业/指数）
- ATR（波动率标准化）
- 缺口行为
- 换手率百分位

**动量指标**
- RSI(14) - 超买超卖
- 趋势持续性

**成交量指标**
- 量能惊喜（vs 20日均值）
- 换手率突增
- 价格-量能确认度

#### 形态识别
- 突破形态：放量突破平台、突破阻力位
- 盘整形态：箱体震荡、收敛三角形
- 转折形态：金叉死叉、背离

#### 角色定位
- 确认市场是否验证了叙事/事件
- 提供技术面确认

---

### 3.4 盘口与日内压力分析模块（五档行情）

#### 目标
分析日内盘口和逐笔行为，评估**买卖压力**、**执行质量**和**入场/出场时机确认**，用于下周波动交易。

#### 定位
此模块应被视为：
- **微观结构压力代理**
- **时机确认层**
- **风险/确认信号**

**不应**描述为确定的"机构行为分析"，因为仅凭五档盘口数据不足以高置信度识别机构意图。

#### 输入
- 实时五档盘口
- 历史逐笔数据
- 日内交易/报价快照
- 日线OHLCV数据

#### 推荐特征

**1. 委托不平衡**
- 买量 vs 卖量总和
- 1分钟/5分钟/15分钟滚动不平衡

**2. 大单压力**
- 大买/大卖出现频率
- 净大单压力
- 大单随时间持续性

**3. 撤单代理**
- 通过对比时间轴上的盘口变化估算撤单强度
- 识别快速挂单/撤单行为
- 检测异常报价不稳定

**4. VWAP与日内强度**
- 当前价格 vs VWAP
- 日内收盘强度
- 下午强度 vs 上午弱势
- 日内恢复/回落形态

**5. 流动性与价格响应**
- 价差变化
- 深度变化
- 大报价/交易事件后的价格响应
- 异常流动性真空行为

#### 衍生信号
- 买压增强
- 卖压增强
- 突破确认
- 失败突破警告
- 出货风险
- 弱势收盘警告
- 日内吸纳/支撑行为

#### 输出
该模块应产生：
- 压力分数
- 确认分数
- 拥挤风险标志
- 主导日内行为的解释

---

### 3.5 波动交易评分与推荐系统

#### 目标
为跟踪股票池中的每只股票生成可解释的、下周导向的交易评估。

#### 输出结构
不仅仅输出单一原始分数，系统应生成**三个核心分数 + 一个推荐层**：

1. **机会分数 (0–100)**
   - 衡量下周上涨吸引力

2. **风险分数 (0–100)**
   - 衡量设置失败、反转、拥挤或事件风险的概率

3. **信心分数 (0–100)**
   - 衡量一致性、数据质量和当前信号的可靠性

4. **交易推荐**
   - 强力做多
   - 观察做多
   - 中性
   - 避免
   - 减仓/出场

#### 核心信号维度

**A. 事件/公告影响**
权重：**30%**

包括：交易所公告、业绩相关事件、政策影响、重大订单/合同、资本市场行动、重大公司特定发展

角色：下周波动机会的主要驱动

**B. 价格/趋势结构**
权重：**25%**

包括：MA趋势对齐、突破/破位状态、20日/60日价格结构、相对强度（vs 行业/指数）、ATR标准化趋势质量

角色：确认市场是否验证了叙事

**C. 量能/参与度**
权重：**15%**

包括：量能惊喜、换手率百分位、价格-量能确认、吸筹/出货代理

角色：衡量走势背后的参与质量

**D. 盘口/日内压力**
权重：**15%**

包括：委托不平衡、大单压力、撤单代理、VWAP强度、收盘强度

角色：确认入场时机并识别短期风险

**E. 行业/宏观环境**
权重：**10%**

包括：行业龙头/弱势、市场环境、政策和宏观背景、主题顺风/逆风

角色：根据外部环境调整股票评分

**F. 人群关注度/KOL代理**
权重：**5%**

包括：KOL提及突增、人群情绪、叙事加速、拥挤风险

角色：主要用作关注度/拥挤指标，非独立alpha源

---

#### 机会分数计算
机会分数应强调：
- 正面实质性事件
- 看涨价格确认
- 强相对强度
- 支撑性量能
- 正面日内压力
- 有利行业背景

#### 风险分数计算
风险分数应强调：
- 矛盾或负面事件
- 失败突破行为
- 弱势收盘结构
- 异常拥挤突增
- 高撤单/不稳定盘口行为
- 不利宏观/政策发展

#### 信心分数计算
信心分数应基于：
- 各信号模块间的一致性
- 来源可靠性
- LLM影响分类置信度
- 数据新鲜度和完整性
- 叙事与价格行为间的一致性

#### 推荐逻辑
推荐初始规则集：

- **强力做多**
  - 高机会
  - 低至中等风险
  - 中至高信心
  - 正面事件/叙事支持
  - 价格结构确认

- **观察做多**
  - 正面机会
  - 可接受风险
  - 需要确认
  - 例如：等待突破或回撤入场

- **中性**
  - 混合或弱信号
  - 无明确优势

- **避免**
  - 低机会
  - 升高风险
  - 弱或矛盾确认

- **减仓/出场**
  - 负面事件影响
  - 叙事恶化
  - 失败价格结构
  - 上升拥挤/反转风险

#### 可解释性要求
对每个生成的推荐，系统必须展示：
- 前3个看涨驱动因素
- 前3个看跌驱动因素
- 相比前日的变化
- 信心解释
- 支持文档/证据
- 建议入场条件
- 建议失效/止损逻辑
- 可选目标风格或出场条件

#### 建议UI展示
对每只股票：
- 机会分数
- 风险分数
- 信心分数
- 交易推荐
- 入场条件
- 失效价位
- 顶部正面驱动因素
- 顶部负面驱动因素
- 最新实质性事件

---

### 3.6 Web界面（Tab布局）

**Tab 1: 仪表盘 (Dashboard)**
- 所有股票评分列表（可排序/筛选）
- 机会分数Top 5 / 风险分数Top 5
- 行业评分对比
- 今日事件摘要

**Tab 2: 股票详情 (Stock Detail)**
- 当前评分和评分构成
- 机会/风险/信心分数拆解
- 价格走势图（日线）
- 技术指标图表
- 盘口压力分析
- 相关文档（带影响标注）
- 解释层（前3正面/负面驱动因素）

**Tab 3: 文档流 (Documents)**
- 按时间排序
- 按事件类型筛选
- 按相关股票筛选
- 显示影响方向和时间窗

**Tab 4: KOL动态**
- 关注的KOL列表
- 帖子列表及关注度/拥挤度标注
- 重要观点摘要

**Tab 5: 宏观指标**
- 关键宏观指标卡片
- 最新数据及变化趋势

**Tab 6: 系统设置 (Settings)**
- 股票列表管理
- KOL关注列表
- 权重调整（初始规则，V2可动态调整）
- 告警设置
- 数据刷新频率

---

### 3.7 告警系统

#### 告警分类

**A. 事件告警**
- 实质公告发布
- 检测到高影响新闻
- 影响跟踪主题的政策新闻
- LLM标记强正面或负面直接影响

**B. 评分告警**
- 机会分数跨越阈值
- 风险分数升至阈值以上
- 信心分数大幅下降
- 推荐状态变化

**C. 价格/结构告警**
- 突破确认
- 失败突破
- 强开盘后的弱势收盘
- 相对强度恶化

**D. 人群/风险告警**
- 关注度突增
- 拥挤风险增加
- 叙事与价格行为矛盾

**E. 运营告警**
- 数据源陈旧
- Parser失败
- LLM分类失败
- 缺失日内更新

---

## 4. 技术架构

### 4.1 技术栈

| 层级 | 技术 | 描述 |
|------|------|------|
| 后端 | Python 3.11+ | 核心开发语言 |
| Web框架 | FastAPI | 高性能API和服务层 |
| 任务调度 | APScheduler (v1) / Celery或Prefect (v2+) | 数据采集和处理工作流 |
| 关系存储 | PostgreSQL | 应用、元数据、文档、信号、告警的主要运营数据库 |
| 分析存储 | DuckDB + Parquet | 历史市场数据、逐笔衍生特征、回测、分析查询 |
| 前端 | HTML + CSS + JS (v1) | 轻量级本地Web界面 |
| 实时更新 | WebSocket / SSE | 推送评分和告警更新 |
| LLM集成 | 云端LLM API | 相关性、事件提取、影响评估、解释生成 |
| 数据处理 | Pandas / Polars | 特征工程和转换 |
| 日志/监控 | 结构化日志 + 健康检查 | 任务状态、Parser错误、陈旧数据检测 |

#### 架构原则
1. **运营和分析工作负载应分离**
   - PostgreSQL用于事务性应用状态
   - DuckDB/Parquet用于时间序列分析

2. **文本分析应以事件影响驱动**
   - 不仅限通用情感

3. **每个分数都应可解释**
   - 必须存储分数来源

4. **实时数据应聚合成有用特征**
   - 避免仅存储无衍生特征的原始快照

---

### 4.2 系统架构图

```
┌────────────────────────────────────────────────────────────────────┐
│                            Web前端                            │
│ 仪表盘 | 股票详情 | 文档 | KOL | 宏观 | 设置                  │
└───────────────────────────────┬────────────────────────────────────┘
                                │ REST API / WebSocket / SSE
┌───────────────────────────────▼────────────────────────────────────┐
│                           FastAPI后端                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────┐ │
│  │ API路由      │ │ 实时中心      │ │ 调度器        │ │ 认证(可选)│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └───────────┘ │
└───────────────────────────────┬────────────────────────────────────┘
                                │
       ┌────────────────────────┼─────────────────────────┐
       │                        │                         │
┌──────▼───────┐    ┌────────▼─────────┐    ┌──────────▼──────────┐
│ 数据采集      │    │ AI/LLM分析      │    │ 信号与决策         │
│               │    │                 │    │ 引擎               │
│ - 新闻        │    │ - 相关性        │    │ - 事件分数         │
│ - 公告       │    │ - 事件类型      │    │ - 技术分数         │
│ - KOL帖子    │    │ - 影响方向      │    │ - 量能分数         │
│ - 宏观       │    │ - 时间窗        │    │ - 盘口流分数       │
│ - 日线数据   │    │ - 置信度        │    │ - 环境分数         │
│ - 逐笔数据   │    │ - 解释          │    │ - 风险分数         │
│ - 五档盘口   │    │                 │    │ - 信心分数         │
└──────┬──────┘    └────────┬─────────┘    │ - 推荐             │
       │                       │              └──────────┬──────────┘
       │                       │                         │
       └───────────────────────┼─────────────────────────┘
                               │
          ┌────────────────────▼────────────────────┐
          │              存储层                      │
          │                                          │
          │ PostgreSQL                               │
          │ - stocks                                 │
          │ - documents                              │
          │ - document_stock_impacts                 │
          │ - daily_features                         │
          │ - recommendations                        │
          │ - alerts                                 │
          │ - settings                               │
          │ - score_explanations                     │
          │                                          │
          │ DuckDB / Parquet                         │
          │ - daily_quotes                           │
          │ - tick_data                              │
          │ - order_book_snapshots                   │
          │ - order_book_features                    │
          │ - backtest_snapshots                     │
          └──────────────────────────────────────────┘
```

---

### 4.3 处理层级

**A. 数据采集层**
职责：来源采集、时间戳标准化、去重、内容哈希、Parser健康监控、来源可靠性标记

**B. 文档智能层**
职责：股票相关性映射、事件提取、影响分类、时间窗标记、置信度生成、可解释摘要生成

**C. 特征工程层**
职责：技术指标、相对强度、量能/换手特征、日内压力特征、人群关注度特征、宏观/行业环境特征

**D. 评分与推荐层**
职责：计算机会/风险/信心分数、生成推荐类别、创建解释payload、触发告警

**E. 监控与验证层**
职责：陈旧数据检测、任务失败告警、模型版本跟踪、评分漂移监控、未来回测/重放支持

---

## 5. 数据库设计

### 5.1 设计原则
1. 分离**文档**、**特征**、**评分**和**推荐**
2. 显式存储**LLM输出**
3. 存储**解释和证据**
4. 使用**时间序列分析存储**处理高频数据
5. 确保股票级唯一性约束正确

---

### 5.2 核心关系表（PostgreSQL）

#### stocks
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    theme VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### documents
新闻、公告、宏观和KOL帖子的统一表。

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(20) NOT NULL,   -- news, filing, macro, kol
    source_name VARCHAR(50) NOT NULL,   -- sina, eastmoney, cninfo, weibo, etc.
    title TEXT,
    url TEXT UNIQUE,
    content TEXT,
    author_name VARCHAR(100),
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT NOW(),
    content_hash VARCHAR(64),
    language VARCHAR(10) DEFAULT 'zh',
    raw_metadata JSONB
);

CREATE INDEX idx_documents_source_type ON documents(source_type);
CREATE INDEX idx_documents_published_at ON documents(published_at);
CREATE INDEX idx_documents_content_hash ON documents(content_hash);
```

#### document_stock_impacts
存储LLM/规则的结构化输出。

```sql
CREATE TABLE document_stock_impacts (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    relevance_score REAL NOT NULL,              -- 0 to 1
    relevance_type VARCHAR(20),                 -- direct, indirect, sector, market
    impact_direction VARCHAR(20),               -- positive, negative, mixed, neutral
    impact_strength VARCHAR(20),                -- weak, medium, strong
    impact_horizon VARCHAR(20),                 -- intraday, 2_5d, 1_2w
    event_type VARCHAR(50),
    confidence VARCHAR(20),                     -- low, medium, high
    explanation TEXT,
    evidence_snippet TEXT,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_doc_impacts_stock_id ON document_stock_impacts(stock_id);
CREATE INDEX idx_doc_impacts_document_id ON document_stock_impacts(document_id);
CREATE INDEX idx_doc_impacts_event_type ON document_stock_impacts(event_type);
```

#### daily_features
存储用于排名/评分的日线级计算特征。

```sql
CREATE TABLE daily_features (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    close_price REAL,
    volume REAL,
    amount REAL,

    trend_score REAL,
    relative_strength_score REAL,
    breakout_score REAL,
    volatility_score REAL,
    volume_surprise REAL,
    turnover_percentile REAL,

    event_score REAL,
    crowd_attention_score REAL,
    sector_regime_score REAL,

    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_id, trade_date)
);

CREATE INDEX idx_daily_features_stock_date ON daily_features(stock_id, trade_date);
```

#### intraday_features
存储聚合日内压力特征，不仅限原始快照。

```sql
CREATE TABLE intraday_features (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    feature_time TIMESTAMP NOT NULL,

    order_imbalance REAL,
    large_order_pressure REAL,
    cancel_ratio_proxy REAL,
    vwap_distance REAL,
    close_strength REAL,
    liquidity_stress REAL,
    pressure_score REAL,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_intraday_features_stock_time ON intraday_features(stock_id, feature_time);
```

#### crowd_features
KOL为基础的人群/关注度指标。

```sql
CREATE TABLE crowd_features (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    feature_date DATE NOT NULL,

    mention_count INT,
    attention_spike_score REAL,
    crowd_sentiment_score REAL,
    sentiment_dispersion REAL,
    crowding_risk_score REAL,

    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stock_id, feature_date)
);

CREATE INDEX idx_crowd_features_stock_date ON crowd_features(stock_id, feature_date);
```

#### scores
每只股票和日期/时间的最终分数输出。

```sql
CREATE TABLE scores (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    score_time TIMESTAMP NOT NULL,

    opportunity_score REAL NOT NULL,   -- 0 to 100
    risk_score REAL NOT NULL,          -- 0 to 100
    confidence_score REAL NOT NULL,      -- 0 to 100

    event_component REAL,
    trend_component REAL,
    volume_component REAL,
    order_flow_component REAL,
    regime_component REAL,
    crowd_component REAL,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scores_stock_time ON scores(stock_id, score_time);
```

#### recommendations
存储最终行动建议。

```sql
CREATE TABLE recommendations (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    recommendation_time TIMESTAMP NOT NULL,

    stance VARCHAR(20),                -- bullish, neutral, bearish
    action VARCHAR(30),                -- strong_long, watch_long, neutral, avoid, reduce_exit
    entry_condition TEXT,
    invalidation_level REAL,
    target_hint TEXT,
    confidence_label VARCHAR(20),        -- low, medium, high

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recommendations_stock_time ON recommendations(stock_id, recommendation_time);
```

#### score_explanations
人类可读推理层。

```sql
CREATE TABLE score_explanations (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    explanation_time TIMESTAMP NOT NULL,

    top_positive_factors JSONB,
    top_negative_factors JSONB,
    changes_from_prior JSONB,
    supporting_document_ids JSONB,
    contradiction_flags JSONB,
    narrative_summary TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_score_explanations_stock_time ON score_explanations(stock_id, explanation_time);
```

#### alerts
```sql
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    stock_id INT REFERENCES stocks(id) ON DELETE CASCADE,
    alert_time TIMESTAMP NOT NULL DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20),              -- info, warning, critical
    title TEXT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    related_score_id BIGINT,
    related_document_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_stock_time ON alerts(stock_id, alert_time);
CREATE INDEX idx_alerts_is_read ON alerts(is_read);
```

#### settings
```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 5.3 分析存储（DuckDB / Parquet）

这些数据集应存储在运营关系数据库之外以提高性能和可维护性：

#### daily_quotes
字段：stock_id, trade_date, open, high, low, close, volume, amount, adj_factor（如需）

#### tick_data
字段：stock_id, trade_time, price, volume, amount, side（如可推导）、session标志

#### order_book_snapshots
字段：stock_id, snapshot_time, buy1~buy5价格/量, sell1~sell5价格/量

#### backtest_snapshots
字段：stock_id, snapshot_date/time, 所有特征, 评分, 推荐, 实现前瞻回报(1w), 实现MFE/MAE

这将支持未来的验证和模型迭代。

---

## 6. 实施计划（V1/V2/V3路线图）

### V1 - 实用MVP（6-10周）

**目标**：构建可每日用于下周波动交易设置的实用工作站。

#### V1核心能力

**A. 股票池与数据采集**
- 固定股票池（~25只）
- 历史日线OHLCV
- 历史逐笔数据
- 实时五档盘口
- 新闻采集
- 公告/公告采集
- 宏观日历/关键发布
- KOL帖子采集

**B. 股票-事件相关性（LLM驱动）**
使用LLM分类：
- 是否与股票池中的任何股票相关？
- 直接或间接相关性？
- 正面/负面/混合影响？
- 预计影响时间窗：日内/2-5天/1-2周
- 置信度
- 理由
- 文本引用证据

**C. 可解释评分引擎**
三个输出：机会分数 / 风险分数 / 信心分数

**D. V1核心信号桶**
1. 价格/趋势结构（25%）
2. 量能/参与度（15%）
3. 事件/新闻/公告影响（30%）
4. 盘口/日内压力代理（15%）
5. 人群关注度/KOL代理（5%）
6. 行业/宏观环境（10%）

**E. 行动推荐引擎**
推荐类型：强力做多 / 观察做多 / 中性 / 避免 / 减仓出场

**F. 可解释性层**
对每个评分/推荐显示：前3看涨驱动因素、前3看跌驱动因素、相比前日变化、关键支持文档、置信度

**G. 告警引擎**
事件告警、评分告警、价格/结构告警、人群/风险告警、运营告警

---

### V2 - 研究级系统（V1之后）

**目标**：使系统更可靠、可回测和差异化。

#### V2主要升级

**A. 回测与评估框架**
对每天和每只股票：快照所有信号、存储推荐、与下周结果对比

测量：命中率、评分桶回报、最大不利偏移、最大有利偏移、按行动类型的精确度、误报率、按行业/环境/事件类型

**B. 动态权重**
允许：行业特定权重、环境相关权重、事件敏感权重

**C. 行业相对与环境感知排名**
绝对机会 / 行业相对机会 / 人群调整机会 / 风险调整机会

**D. 更丰富的逐笔/盘口特征工程**
激进者交易流近似、撤单强度、日内压力环境、开盘竞价强度、下午延续行为、收盘竞价意义、大打价格影响、流动性真空形态

**E. 叙事状态跟踪**
每只股票维护实时叙事账本：当前看涨叙事、当前看跌叙事、最新确认证据、最新矛盾证据、叙事状态：增强/减弱/破裂

**F. 公告/财报Parser**
完全解析：年报、中报、关键公告、业绩预增、定增/可转债发行、股东增减持、回购、管理层变更

**G. 高级告警类型**
叙事破裂告警、拥挤过载告警、事件-价格背离告警、失败突破告警、评分-信心背离告警、陈旧数据/Parser失败告警

**H. 更好的行动框架**
激进入场 / 确认入场 / 回撤入场 / 部分止盈 / 保护收益 / 因事件不确定性避免 / 因叙事破裂出场

---

### V3 - 差异化智能代理（V2之后）

**目标**：将系统转变为真正的AI分析师副驾驶，不仅限评分工具。

#### V3.1 RAG研究副驾驶
用户可询问：为什么这只股票本周排名第一？过去3天有什么变化？总结看涨和看跌证据。设置的主要风险是什么？哪些文档支持推荐？将这只股票与其最接近的同行进行比较。

需要：向量搜索、重排序、文档引用、基于存储数据的接地答案生成

#### V3.2 事件研究引擎
对每个事件类型：计算历史下周回报、按行业、按市场环境、按股票流动性桶

系统可以说："历史上，这种类型的合同赢取在强行业环境的AI硬件名称中导致中位数+4.2%下周回报。"

#### V3.3 概率预测
从原始分数转向：正下周回报概率、预期回报范围、下行风险范围、置信区间

#### V3.4 投资组合感知推荐引擎
跨名称相关性、行业集中度、事件重叠、拥挤重叠、分批入场建议

#### V3.5 人工反馈学习循环
让用户对：告警有用性、推荐质量、文档相关性、叙事/解释是否正确进行评分

然后重新训练或重新校准：事件相关性、评分权重、告警阈值、KOL可信度、推荐模板

---

## 7. 数据保留策略

| 数据类型 | 保留期限 | 存储位置 |
|----------|----------|----------|
| 股票信息 | 永久 | PostgreSQL |
| 文档 | 1年 | PostgreSQL |
| 文档-股票影响 | 1年 | PostgreSQL |
| 日线报价 | 永久 | DuckDB/Parquet |
| 逐笔数据 | 1年 | DuckDB/Parquet |
| 盘口快照 | 30天（仅特征保留更久） | DuckDB/Parquet |
| 评分 | 1年 | PostgreSQL + DuckDB |
| 推荐 | 1年 | PostgreSQL |
| 回测快照 | 永久（用于模型迭代） | DuckDB/Parquet |
| 告警 | 90天 | PostgreSQL |

---

## 8. 风险管理

### 数据风险
- Scraper断开
- 不一致时间戳
- 重复故事
- 错误KOL信号
- 弱股票-新闻映射

### 模型风险
- LLM幻觉
- 不稳定影响分类
- 对嘈杂数据反应过度

### 交易风险
- 拥挤
- 缺口风险
- 事件隔夜风险
- 错误突破信号

### 运营风险
- 任务失败
- 数据陈旧
- 错过告警
- 解释能力差

---

## 9. 验收标准

### 9.1 端到端测试流程

1. **启动系统**
   - 运行后端服务
   - 打开Web界面

2. **数据采集测试**
   - 检查新闻是否正常采集
   - 检查五档盘口是否每5秒更新
   - 验证数据库有新数据

3. **分析引擎测试**
   - 查看事件影响分析结果
   - 验证技术指标计算
   - 检查盘口压力分析

4. **评分系统测试**
   - 查看机会/风险/信心分数是否生成
   - 检查各模块分数占比
   - 验证分数在合理范围

5. **可解释性测试**
   - 检查每个推荐是否有前3正面/负面驱动因素
   - 验证"相比前日变化"显示
   - 确认支持文档链接

6. **告警测试**
   - 触发评分突变
   - 检查告警是否出现

### 9.2 用户验收标准

- ✅ Web界面可正常访问
- ✅ 25只股票数据正常显示
- ✅ 机会/风险/信心分数在0-100范围内
- ✅ 文档和KOL有影响标注（非简单情感）
- ✅ 五档盘口实时更新
- ✅ 每个推荐有完整可解释性
- ✅ 告警及时触发
- ✅ 可以通过Web界面配置

---

## 10. 开放问题

1. **股票列表**：需要用户提供具体的25只股票代码和名称
2. **KOL列表**：需要提供关注的微博KOL账号
3. **API凭证**：需要提供行情API的接入信息
4. **LLM选择**：选择哪个云端LLM API（OpenAI/Anthropic/国内供应商）
5. **数据保留**：确认数据保留策略是否合适

---

## 11. 下一步行动

1. 用户确认PDR内容
2. 提供股票列表和KOL列表
3. 选择LLM供应商
4. 开始V1 Phase A开发（基础设施数据采集）
5. 开始V1 Phase B开发（核心智能LLM相关性 + 评分引擎）
