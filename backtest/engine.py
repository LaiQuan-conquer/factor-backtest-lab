"""
Simple rule-based backtest engine.

This is a minimal pandas-based implementation for research purposes.
For production research, consider vectorbt or similar frameworks.

IMPORTANT: This backtest is for demonstrating research workflow only.
Results do NOT indicate future performance and should NOT be used for
investment decisions.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional

import numpy as np
import pandas as pd


@dataclass
class BacktestConfig:
    """Configuration for backtest parameters."""

    cost_mode: Literal["zero_cost", "with_cost"] = "zero_cost"

    commission_rate: float = 0.001
    slippage_rate: float = 0.001

    initial_capital: float = 1_000_000.0

    rebalance_freq: str = "daily"

    top_n: int = 1
    bottom_n: int = 1

    def __post_init__(self):
        if self.cost_mode == "zero_cost":
            self.commission_rate = 0.0
            self.slippage_rate = 0.0


@dataclass
class BacktestResult:
    """Results from a backtest run."""

    portfolio_value: pd.Series
    positions: pd.DataFrame
    trades: pd.DataFrame
    config: BacktestConfig

    total_return: float = field(init=False)
    n_trades: int = field(init=False)
    total_cost: float = field(init=False)

    def __post_init__(self):
        if len(self.portfolio_value) > 1:
            self.total_return = (
                self.portfolio_value.iloc[-1] / self.portfolio_value.iloc[0] - 1
            )
        else:
            self.total_return = 0.0

        self.n_trades = len(self.trades) if len(self.trades) > 0 else 0

        if "cost" in self.trades.columns and len(self.trades) > 0:
            self.total_cost = self.trades["cost"].sum()
        else:
            self.total_cost = 0.0


class BacktestEngine:
    """
    Simple factor-based backtest engine.

    Strategy:
        - Long top_n stocks by factor value
        - Short bottom_n stocks by factor value
        - Equal weight within each leg
        - Rebalance at specified frequency
    """

    def __init__(self, config: Optional[BacktestConfig] = None):
        """
        Initialize backtest engine.

        Args:
            config: Backtest configuration. If None, uses zero_cost defaults.
        """
        self.config = config or BacktestConfig()

    def run(
        self,
        prices: pd.DataFrame,
        factor_values: pd.DataFrame,
    ) -> BacktestResult:
        """
        Run backtest with given prices and factor values.

        Args:
            prices: DataFrame with dates as index, symbols as columns (close prices)
            factor_values: DataFrame with factor values, same structure as prices

        Returns:
            BacktestResult with portfolio value, positions, and trades
        """
        if not prices.index.equals(factor_values.index):
            raise ValueError("prices and factor_values must have same index")
        if not prices.columns.equals(factor_values.columns):
            raise ValueError("prices and factor_values must have same columns")

        dates = prices.index
        symbols = prices.columns

        portfolio_values = []
        all_positions = []
        all_trades = []

        cash = self.config.initial_capital
        holdings = pd.Series(0.0, index=symbols)

        for i, date in enumerate(dates):
            day_factor = factor_values.loc[date]
            day_prices = prices.loc[date]

            valid_factor = day_factor.dropna()

            if len(valid_factor) < self.config.top_n + self.config.bottom_n:
                portfolio_value = cash + (holdings * day_prices).sum()
                portfolio_values.append(portfolio_value)
                all_positions.append(holdings.copy())
                continue

            sorted_symbols = valid_factor.sort_values(ascending=False)
            long_symbols = sorted_symbols.head(self.config.top_n).index.tolist()
            short_symbols = sorted_symbols.tail(self.config.bottom_n).index.tolist()

            target_holdings = pd.Series(0.0, index=symbols)

            total_value = cash + (holdings * day_prices).sum()
            long_value = total_value * 0.5 / self.config.top_n
            short_value = total_value * 0.5 / self.config.bottom_n

            for sym in long_symbols:
                if day_prices[sym] > 0:
                    target_holdings[sym] = long_value / day_prices[sym]

            for sym in short_symbols:
                if day_prices[sym] > 0:
                    target_holdings[sym] = -short_value / day_prices[sym]

            trades_today = target_holdings - holdings
            trade_value = (trades_today.abs() * day_prices).sum()

            cost = trade_value * (self.config.commission_rate + self.config.slippage_rate)

            cash = cash - (trades_today * day_prices).sum() - cost

            holdings = target_holdings.copy()

            portfolio_value = cash + (holdings * day_prices).sum()
            portfolio_values.append(portfolio_value)
            all_positions.append(holdings.copy())

            if trade_value > 0:
                all_trades.append({
                    "date": date,
                    "trade_value": trade_value,
                    "cost": cost,
                    "long_symbols": long_symbols,
                    "short_symbols": short_symbols,
                })

        portfolio_series = pd.Series(portfolio_values, index=dates, name="portfolio_value")

        positions_df = pd.DataFrame(all_positions, index=dates)

        trades_df = pd.DataFrame(all_trades) if all_trades else pd.DataFrame(
            columns=["date", "trade_value", "cost", "long_symbols", "short_symbols"]
        )

        return BacktestResult(
            portfolio_value=portfolio_series,
            positions=positions_df,
            trades=trades_df,
            config=self.config,
        )


def compare_cost_modes(
    prices: pd.DataFrame,
    factor_values: pd.DataFrame,
) -> dict[str, BacktestResult]:
    """
    Run backtest with both zero-cost and with-cost configurations.

    This comparison is essential for understanding the impact of
    transaction costs on strategy performance.

    Args:
        prices: DataFrame with close prices
        factor_values: DataFrame with factor values

    Returns:
        Dict with "zero_cost" and "with_cost" BacktestResult
    """
    results = {}

    zero_config = BacktestConfig(cost_mode="zero_cost")
    zero_engine = BacktestEngine(zero_config)
    results["zero_cost"] = zero_engine.run(prices, factor_values)

    cost_config = BacktestConfig(cost_mode="with_cost")
    cost_engine = BacktestEngine(cost_config)
    results["with_cost"] = cost_engine.run(prices, factor_values)

    return results
