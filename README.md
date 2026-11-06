# Factor Backtest Lab / 因子回测实验室

[![pytest](https://github.com/LaiQuan-conquer/factor-backtest-lab/actions/workflows/test.yml/badge.svg)](https://github.com/LaiQuan-conquer/factor-backtest-lab/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## ⚠️ 重要声明 / Important Disclaimer

**中文：**
- 本项目仅用于**个人研究与教学目的**，不构成任何投资建议
- 仅使用**公开数据**（AkShare / yfinance 等公开接口）
- 因子构造均来自**经典教材/公开文献**（动量、反转、已实现波动率等），**非专有或盈利性因子**
- **不涉及模拟盘/实盘交易**，不提供任何收益率承诺
- 回测结果仅供研究流程演示，**不代表未来表现**

**English:**
- This project is for **personal research and educational purposes only**, NOT investment advice
- Uses **public data only** (AkShare / yfinance public APIs)
- Factor constructions are **classic textbook definitions** (momentum, reversal, realized volatility), NOT proprietary or profitable alpha
- **NO simulated or live trading** involved, NO return claims
- Backtest results are for demonstrating research workflow only, **NOT indicative of future performance**

---

## 项目简介 / Overview

这是一个经典因子研究的个人实验室，旨在走通「取数 → 清洗 → 因子构建 → 回测验证」的完整流程。

This is a personal research lab for classic factor construction, designed to demonstrate the complete workflow: data fetching → cleaning → factor construction → backtesting.

### 项目结构 / Structure

```
factor-backtest-lab/
├── data/                 # 公开数据拉取与缓存 / Data fetching and caching
│   ├── __init__.py
│   ├── fetcher.py        # 数据获取接口 / Data fetch interface
│   └── fixtures.py       # 测试用合成数据 / Synthetic test fixtures
├── factors/              # 经典因子定义 / Classic factor definitions
│   ├── __init__.py
│   ├── momentum.py       # 动量因子 / Momentum factor
│   ├── reversal.py       # 短期反转 / Short-term reversal
│   └── volatility.py     # 已实现波动率 / Realized volatility
├── backtest/             # 回测引擎 / Backtest engine
│   ├── __init__.py
│   └── engine.py         # 简单规则回测 / Simple rule-based backtest
├── analysis/             # 分析报告 / Analysis reports
│   ├── __init__.py
│   └── tearsheet.py      # 报告生成占位 / Report generation placeholder
├── tests/                # 测试套件 / Test suite
├── notebooks/            # 研究笔记 / Research notebooks
└── README.md
```

---

## 因子定义 / Factor Definitions

所有因子均采用经典教材中的公开构造，避免前视偏差（look-ahead bias）。

All factors use classic textbook constructions, with careful handling to avoid look-ahead bias.

### 1. 动量因子 / Momentum Factor

**定义：** 过去 N 日的累计收益率（不含当日）

**Definition:** Cumulative return over past N days (excluding current day)

```
Momentum(t) = Close(t-1) / Close(t-N) - 1
```

**注意：** 使用 t-1 日收盘价而非 t 日，避免使用当日尚未可得的信息（前视偏差）。

**Note:** Uses t-1 close price instead of t to avoid using information not yet available (look-ahead bias).

**参考 / Reference:** Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers"

### 2. 短期反转因子 / Short-term Reversal Factor

**定义：** 过去 N 日收益率的负值（预期均值回归）

**Definition:** Negative of past N-day return (expecting mean reversion)

```
Reversal(t) = -(Close(t-1) / Close(t-N) - 1)
```

**参考 / Reference:** Jegadeesh (1990), "Evidence of Predictable Behavior of Security Returns"

### 3. 已实现波动率 / Realized Volatility

**定义：** 过去 N 日日收益率的标准差

**Definition:** Standard deviation of daily returns over past N days

```
RealizedVol(t) = StdDev(Return(t-N:t-1))
```

**参考 / Reference:** Ang et al. (2006), "The Cross-Section of Volatility and Expected Returns"

---

## 安装 / Installation

```bash
# 克隆仓库 / Clone repository
git clone https://github.com/LaiQuan-conquer/factor-backtest-lab.git
cd factor-backtest-lab

# 创建虚拟环境（推荐）/ Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖 / Install dependencies
pip install -e ".[dev]"

# 安装数据获取依赖（可选）/ Install data fetching dependencies (optional)
pip install -e ".[fetch]"
```

---

## 使用方法 / Usage

### 运行演示 / Run Demo

```bash
# 使用内置合成数据运行完整演示
# Run full demo with built-in synthetic data
python -m factor_backtest_lab

# 或使用命令行入口 / Or use CLI entry
factor-lab --help
factor-lab demo
```

### 运行测试 / Run Tests

```bash
# 运行所有测试（离线，无需网络）
# Run all tests (offline, no network required)
pytest

# 带覆盖率 / With coverage
pytest --cov=. --cov-report=term-missing
```

---

## 回测说明 / Backtest Notes

回测引擎支持两种成本模式：

The backtest engine supports two cost modes:

| 模式 / Mode | 佣金 / Commission | 滑点 / Slippage | 用途 / Purpose |
|-------------|-------------------|-----------------|----------------|
| `zero_cost` | 0 | 0 | 理论基准 / Theoretical baseline |
| `with_cost` | 0.1% (单边) | 0.1% | 现实假设 / Realistic assumption |

**重要：** 两种模式的对比是研究的核心——展示交易成本对策略的影响，而非声称任何收益。

**Important:** Comparing both modes is central to research — demonstrating cost impact, NOT claiming any returns.

---

## 数据来源 / Data Sources

- **AkShare** (https://github.com/akfamily/akshare) - A 股公开数据
- **yfinance** (https://github.com/ranaroussi/yfinance) - Yahoo Finance 公开行情

测试使用合成数据，无需网络连接或 API 密钥。

Tests use synthetic data fixtures, requiring no network or API keys.

---

## 下一步计划 / Next Steps

- [ ] Alphalens 风格的因子分层分析
- [ ] Walk-forward 滚动窗口验证
- [ ] 更多经典因子（价值、规模等）
- [ ] 研究笔记与案例

---

## 贡献 / Contributing

欢迎提交 Issue 和 PR。请确保：

1. 所有代码通过 `pytest`
2. 新因子附带定义来源（教材/文献）
3. 不引入专有数据或收益承诺

---

## 许可证 / License

MIT License - 详见 [LICENSE](LICENSE)

---

## 致谢 / Acknowledgments

- [vectorbt](https://github.com/polakowo/vectorbt) - 向量化回测框架
- [alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded) - 因子分析工具
- [AkShare](https://github.com/akfamily/akshare) - 开源金融数据接口
