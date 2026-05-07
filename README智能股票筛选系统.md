# Quants - 智能股票筛选系统

基于基本面分析和宏观经济因素的智能化沪深股市股票筛选系统，为投资者提供数据驱动的投资决策支持。

## 🚀 项目特性

### 核心功能
- **📊 多源数据采集**: 支持Tushare、AKShare等多个数据源
- **💹 实时行情数据**: 股票价格、成交量、技术指标等
- **📈 财务报表分析**: 资产负债表、利润表、现金流量表
- **🌍 宏观经济分析**: 经济指标、政策影响评估
- **🎯 智能筛选策略**: 价值投资、成长投资、量化多因子模型
- **⚠️ 风险管理**: 个股风险评估、组合风险分析
- **📱 RESTful API**: 完整的API接口支持
- **📊 数据可视化**: 图表展示和交互式界面

### 技术亮点
- **现代化架构**: 基于FastAPI + SQLAlchemy + PostgreSQL
- **高性能处理**: 异步数据处理，支持大规模数据集
- **灵活配置**: 支持多种配置方式和环境
- **完整测试**: 单元测试和集成测试覆盖
- **容器化部署**: 支持Docker部署
- **数据质量**: 完整的数据清洗和验证流程

## 📋 系统架构

```
Quants System Architecture
├── 数据采集层 (Data Collection)
│   ├── Tushare数据源
│   ├── AKShare数据源
│   └── 其他数据源扩展
├── 数据存储层 (Data Storage)
│   ├── PostgreSQL数据库
│   ├── Redis缓存
│   └── 文件存储
├── 分析计算层 (Analysis Engine)
│   ├── 基本面分析
│   ├── 技术分析
│   ├── 宏观分析
│   └── 风险评估
├── 策略执行层 (Strategy Engine)
│   ├── 筛选策略
│   ├── 组合管理
│   └── 回测系统
└── 用户接口层 (User Interface)
    ├── REST API
    ├── Web界面
    └── 命令行工具
```

## 🛠️ 技术栈

### 后端技术
- **Python 3.12+**: 核心开发语言
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM框架
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和会话存储
- **Celery**: 异步任务队列
- **Pandas**: 数据处理
- **NumPy**: 数值计算

### 数据处理
- **Scikit-learn**: 机器学习
- **XGBoost**: 梯度提升算法
- **Plotly**: 交互式图表
- **Matplotlib**: 数据可视化
- **Seaborn**: 统计图表

### 开发工具
- **UV**: 现代Python包管理器
- **pytest**: 测试框架
- **Black**: 代码格式化
- **Ruff**: 代码检查
- **MyPy**: 类型检查

## 📦 安装和配置

### 环境要求
- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- 4GB+ RAM

### 快速安装

1. **克隆项目**
```bash
git clone https://github.com/your-username/quants.git
cd quants
```

2. **创建虚拟环境**
```bash
# 使用uv (推荐)
uv venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 或使用venv
python -m venv .venv
source .venv/bin/activate
```

3. **安装依赖**
```bash
# 生产环境
uv sync

# 开发环境
uv sync --dev
```

4. **配置环境变量**
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# 配置数据库连接、API密钥等
```

5. **初始化数据库**
```bash
# 创建数据库表
python -m src.quants.models.init_db init

# 检查数据库连接
python -m src.quants.models.init_db check
```

### 配置说明

主要配置项：

```env
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/quants_db
REDIS_URL=redis://localhost:6379/0

# API密钥
TUSHARE_TOKEN=your_tushare_token_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# 系统配置
LOG_LEVEL=INFO
API_DEBUG=false
MAX_PORTOLIO_SIZE=50
```

## 🚀 快速开始

### 1. 数据采集

```python
from src.quants.data import DataCollector

# 初始化数据收集器
collector = DataCollector()

# 获取股票列表
stocks = collector.get_stock_list()
print(f"获取到 {len(stocks)} 只股票")

# 获取价格数据
prices = collector.get_price_data(
    stock_codes=['000001.SZ', '600000.SH'],
    start_date='2024-01-01',
    end_date='2024-11-18'
)
```

### 2. 数据存储

```python
from src.quants.data import DataStorage

# 初始化存储
storage = DataStorage()

# 保存股票列表
storage.save_stock_list(stocks)

# 保存价格数据
for stock_code, price_df in prices.items():
    storage.save_price_data(stock_code, price_df)
```

### 3. 基本面分析

```python
from src.quants.analysis import FundamentalAnalyzer

# 初始化分析器
analyzer = FundamentalAnalyzer()

# 计算财务指标
ratios = analyzer.calculate_ratios('000001.SZ')

# 评估投资价值
score = analyzer.evaluate_investment('000001.SZ')
```

### 4. 股票筛选

```python
from src.quants.strategy import StockScreener

# 初始化筛选器
screener = StockScreener()

# 价值投资策略
value_stocks = screener.screen_value_stocks(
    pe_ratio_max=20,
    pb_ratio_max=2,
    roe_min=0.1
)

# 成长投资策略
growth_stocks = screener.screen_growth_stocks(
    revenue_growth_min=0.15,
    profit_growth_min=0.15
)
```

### 5. 启动API服务

```bash
# 启动开发服务器
uvicorn src.quants.api.main:app --reload

# 启动生产服务器
uvicorn src.quants.api.main:app --host 0.0.0.0 --port 8000
```

API文档访问: http://localhost:8000/docs

## 📊 使用示例

### 获取股票基本信息

```python
from src.quants.data.storage import DataStorage

storage = DataStorage()
stock = storage.get_stock_by_code('000001.SZ')
print(f"股票名称: {stock.name}")
print(f"所属行业: {stock.industry}")
print(f"上市日期: {stock.listing_date}")
```

### 技术指标分析

```python
from src.quants.data.processor import DataProcessor

processor = DataProcessor()
price_df = storage.get_price_data('000001.SZ', days=60)
technical_df = processor.calculate_technical_indicators(price_df)

# 查看最新技术指标
latest = technical_df.iloc[-1]
print(f"RSI: {latest['rsi']:.2f}")
print(f"MACD: {latest['macd']:.4f}")
print(f"20日均线: {latest['ma_20']:.2f}")
```

### 组合回测

```python
from src.quants.strategy import BacktestEngine

engine = BacktestEngine()
results = engine.run_backtest(
    strategy='value_investing',
    start_date='2023-01-01',
    end_date='2024-11-18',
    initial_capital=1000000
)

print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/unit/test_data.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 📝 API文档

### 主要端点

- `GET /api/v1/stocks` - 获取股票列表
- `GET /api/v1/stocks/{code}` - 获取股票详情
- `GET /api/v1/stocks/{code}/prices` - 获取价格数据
- `GET /api/v1/stocks/{code}/financial` - 获取财务数据
- `POST /api/v1/screen` - 股票筛选
- `GET /api/v1/analysis/{code}` - 股票分析

### 示例请求

```bash
# 获取股票列表
curl http://localhost:8000/api/v1/stocks?exchange=SH&limit=10

# 获取平安银行价格数据
curl http://localhost:8000/api/v1/stocks/000001.SZ/prices?start_date=2024-01-01&end_date=2024-11-18

# 股票筛选
curl -X POST http://localhost:8000/api/v1/screen \
  -H "Content-Type: application/json" \
  -d '{"strategy": "value", "pe_max": 20, "pb_max": 2}'
```

## 🔧 开发指南

### 添加新数据源

1. 继承 `BaseDataSource` 类
2. 实现必需的方法
3. 在 `DataCollector` 中注册

```python
from src.quants.data.collector import BaseDataSource

class MyDataSource(BaseDataSource):
    def get_stock_list(self):
        # 实现获取股票列表
        pass

    def get_price_data(self, stock_code, start_date, end_date):
        # 实现获取价格数据
        pass
```

### 添加筛选策略

1. 在 `strategy` 模块中创建策略类
2. 实现筛选逻辑
3. 在 `StockScreener` 中注册

### 数据库模型扩展

1. 在 `models` 目录下定义新模型
2. 继承 `BaseModel` 类
3. 运行数据库迁移

## 🚀 部署

### Docker部署

```bash
# 构建镜像
docker build -t quants .

# 运行容器
docker run -d --name quants \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  quants
```

### 生产环境部署

1. 使用Nginx作为反向代理
2. 配置Gunicorn作为应用服务器
3. 设置PostgreSQL主从复制
4. 配置Redis集群
5. 设置监控和日志收集

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Ruff 进行代码检查
- 使用 MyPy 进行类型检查
- 编写单元测试
- 添加类型注解

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

- 📧 邮箱: support@quants.com
- 💬 微信群: 扫描二维码加入
- 📖 文档: https://docs.quants.com
- 🐛 问题反馈: https://github.com/your-username/quants/issues

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [Pandas](https://pandas.pydata.org/) - 强大的数据分析工具
- [Tushare](https://tushare.pro/) - 专业的财经数据接口
- [AKShare](https://www.akshare.xyz/) - 开源的金融数据库

## 🗺️ 路线图

### v0.2.0 (计划中)
- [ ] 机器学习预测模型
- [ ] 实时推送通知
- [ ] 移动端应用
- [ ] 更多技术指标

### v0.3.0 (计划中)
- [ ] 期权数据支持
- [ ] 期货数据集成
- [ ] 港股、美股数据
- [ ] 量化交易接口

### v1.0.0 (长期目标)
- [ ] 完整的资产管理平台
- [ ] 智能投顾系统
- [ ] 社区功能
- [ ] 商业化版本

---

**免责声明**: 本系统仅用于教育和研究目的，不构成投资建议。投资有风险，决策需谨慎。