"""
Backtest module for factor-backtest-lab.

Provides a simple rule-based backtest engine with configurable costs.

Supports:
    - Zero-cost mode (theoretical baseline)
    - With-cost mode (commission + slippage)
"""

from backtest.engine import BacktestEngine, BacktestConfig, BacktestResult

__all__ = ["BacktestEngine", "BacktestConfig", "BacktestResult"]
