"""
Tear sheet and analysis utilities.

Placeholder for alphalens-style factor analysis.
For full analysis, consider using alphalens-reloaded:
    https://github.com/stefan-jansen/alphalens-reloaded

IMPORTANT: Analysis results are for research purposes only.
They do NOT predict future performance.
"""

from typing import Optional

import numpy as np
import pandas as pd

from backtest.engine import BacktestResult


def generate_summary(result: BacktestResult) -> dict:
    """
    Generate a summary of backtest results.

    Args:
        result: BacktestResult from backtest engine

    Returns:
        Dict with summary statistics
    """
    pv = result.portfolio_value

    returns = pv.pct_change().dropna()

    summary = {
        "start_date": str(pv.index[0].date()),
        "end_date": str(pv.index[-1].date()),
        "initial_value": pv.iloc[0],
        "final_value": pv.iloc[-1],
        "total_return": result.total_return,
        "n_trades": result.n_trades,
        "total_cost": result.total_cost,
        "cost_mode": result.config.cost_mode,
    }

    if len(returns) > 1:
        summary["daily_vol"] = returns.std()
        summary["annualized_vol"] = returns.std() * np.sqrt(252)

        if returns.std() > 0:
            summary["sharpe_ratio"] = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        else:
            summary["sharpe_ratio"] = 0.0

        cummax = pv.cummax()
        drawdown = (pv - cummax) / cummax
        summary["max_drawdown"] = drawdown.min()

    return summary


def factor_stats(
    factor_values: pd.DataFrame,
    forward_returns: Optional[pd.DataFrame] = None,
) -> dict:
    """
    Calculate basic factor statistics.

    Args:
        factor_values: DataFrame with factor values
        forward_returns: Optional DataFrame with forward returns for IC calculation

    Returns:
        Dict with factor statistics
    """
    stats = {
        "n_dates": len(factor_values),
        "n_symbols": len(factor_values.columns),
        "coverage": factor_values.notna().mean().mean(),
        "mean": factor_values.mean().mean(),
        "std": factor_values.std().mean(),
    }

    if forward_returns is not None:
        aligned_factor = factor_values.reindex_like(forward_returns)
        aligned_returns = forward_returns.reindex_like(factor_values)

        ic_series = aligned_factor.corrwith(aligned_returns, axis=1)
        stats["mean_ic"] = ic_series.mean()
        stats["ic_std"] = ic_series.std()
        stats["ic_ir"] = stats["mean_ic"] / stats["ic_std"] if stats["ic_std"] > 0 else 0.0

    return stats


def print_summary(result: BacktestResult) -> None:
    """Print a formatted summary of backtest results."""
    summary = generate_summary(result)

    print("=" * 50)
    print("Backtest Summary")
    print("=" * 50)
    print(f"Period: {summary['start_date']} to {summary['end_date']}")
    print(f"Cost Mode: {summary['cost_mode']}")
    print("-" * 50)
    print(f"Initial Value: ${summary['initial_value']:,.2f}")
    print(f"Final Value: ${summary['final_value']:,.2f}")
    print(f"Total Return: {summary['total_return']:.2%}")
    print("-" * 50)
    print(f"Number of Trades: {summary['n_trades']}")
    print(f"Total Trading Cost: ${summary['total_cost']:,.2f}")

    if "sharpe_ratio" in summary:
        print("-" * 50)
        print(f"Annualized Volatility: {summary['annualized_vol']:.2%}")
        print(f"Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {summary['max_drawdown']:.2%}")

    print("=" * 50)
