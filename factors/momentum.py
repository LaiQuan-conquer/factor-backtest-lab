"""
Momentum factor implementation.

Classic momentum factor based on past cumulative returns.

Reference:
    Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers:
    Implications for Stock Market Efficiency"

IMPORTANT: Uses t-1 close price (not current day t) to avoid look-ahead bias.
At time t, we only know prices up to t-1 close.
"""

import pandas as pd


def momentum_factor(
    prices: pd.DataFrame,
    lookback: int = 20,
    skip_recent: int = 1,
) -> pd.DataFrame:
    """
    Calculate momentum factor (past cumulative return).

    Formula:
        Momentum(t) = Price(t-skip_recent) / Price(t-lookback-skip_recent+1) - 1

    With default skip_recent=1:
        Momentum(t) = Price(t-1) / Price(t-lookback) - 1

    This ensures we only use information available at decision time.

    Args:
        prices: DataFrame with dates as index, symbols as columns (close prices)
        lookback: Number of days for momentum calculation
        skip_recent: Number of recent days to skip (default=1 to avoid look-ahead)

    Returns:
        DataFrame with momentum values, same shape as input
        NaN for periods with insufficient history
    """
    if lookback < 1:
        raise ValueError("lookback must be >= 1")
    if skip_recent < 1:
        raise ValueError("skip_recent must be >= 1 to avoid look-ahead bias")

    lagged_prices = prices.shift(skip_recent)

    past_prices = prices.shift(skip_recent + lookback - 1)

    momentum = (lagged_prices / past_prices) - 1

    return momentum


def momentum_factor_with_gap(
    prices: pd.DataFrame,
    formation_period: int = 12,
    holding_gap: int = 1,
) -> pd.DataFrame:
    """
    Alternative momentum with explicit formation and holding gap.

    Classic "12-1" momentum: 12-month formation, skip most recent month.

    Args:
        prices: DataFrame with dates as index, symbols as columns
        formation_period: Number of periods for formation window
        holding_gap: Gap between formation end and signal date

    Returns:
        DataFrame with momentum values
    """
    end_price = prices.shift(holding_gap)

    start_price = prices.shift(holding_gap + formation_period)

    return (end_price / start_price) - 1
