"""
Short-term reversal factor implementation.

Captures the tendency of recent losers to outperform and recent winners
to underperform in the short term (mean reversion).

Reference:
    Jegadeesh (1990), "Evidence of Predictable Behavior of Security Returns"

IMPORTANT: Uses lagged prices to avoid look-ahead bias.
"""

import pandas as pd


def reversal_factor(
    prices: pd.DataFrame,
    lookback: int = 5,
    skip_recent: int = 1,
) -> pd.DataFrame:
    """
    Calculate short-term reversal factor.

    Formula:
        Reversal(t) = -(Price(t-skip_recent) / Price(t-lookback-skip_recent+1) - 1)

    The negative sign means:
    - Recent losers (negative return) get positive reversal score
    - Recent winners (positive return) get negative reversal score

    Args:
        prices: DataFrame with dates as index, symbols as columns (close prices)
        lookback: Number of days for reversal calculation (typically 1-5 days)
        skip_recent: Number of recent days to skip (default=1 to avoid look-ahead)

    Returns:
        DataFrame with reversal values, same shape as input
        NaN for periods with insufficient history
    """
    if lookback < 1:
        raise ValueError("lookback must be >= 1")
    if skip_recent < 1:
        raise ValueError("skip_recent must be >= 1 to avoid look-ahead bias")

    lagged_prices = prices.shift(skip_recent)

    past_prices = prices.shift(skip_recent + lookback - 1)

    past_return = (lagged_prices / past_prices) - 1

    reversal = -past_return

    return reversal


def reversal_factor_simple(
    prices: pd.DataFrame,
    skip_recent: int = 1,
) -> pd.DataFrame:
    """
    Simple 1-day reversal (yesterday's return, negated).

    Args:
        prices: DataFrame with close prices
        skip_recent: Days to skip (default=1)

    Returns:
        DataFrame with reversal values
    """
    return reversal_factor(prices, lookback=1, skip_recent=skip_recent)
