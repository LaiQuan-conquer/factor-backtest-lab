"""
Realized volatility factor implementation.

Measures the standard deviation of past returns, often used as a risk measure.

Reference:
    Ang et al. (2006), "The Cross-Section of Volatility and Expected Returns"

IMPORTANT: Uses lagged returns to avoid look-ahead bias.
"""

import numpy as np
import pandas as pd


def realized_volatility_factor(
    prices: pd.DataFrame,
    lookback: int = 20,
    skip_recent: int = 1,
    annualize: bool = False,
    trading_days: int = 252,
) -> pd.DataFrame:
    """
    Calculate realized volatility (standard deviation of past returns).

    Formula:
        Returns(t) = Price(t) / Price(t-1) - 1
        RealizedVol(t) = StdDev(Returns(t-skip_recent-lookback+1 : t-skip_recent))

    Args:
        prices: DataFrame with dates as index, symbols as columns (close prices)
        lookback: Number of days for volatility calculation
        skip_recent: Number of recent days to skip (default=1 to avoid look-ahead)
        annualize: If True, multiply by sqrt(trading_days)
        trading_days: Number of trading days per year (default=252)

    Returns:
        DataFrame with volatility values, same shape as input
        NaN for periods with insufficient history
    """
    if lookback < 2:
        raise ValueError("lookback must be >= 2 for meaningful volatility")
    if skip_recent < 1:
        raise ValueError("skip_recent must be >= 1 to avoid look-ahead bias")

    returns = prices.pct_change()

    lagged_returns = returns.shift(skip_recent)

    vol = lagged_returns.rolling(window=lookback, min_periods=lookback).std()

    if annualize:
        vol = vol * np.sqrt(trading_days)

    return vol


def realized_volatility_log_returns(
    prices: pd.DataFrame,
    lookback: int = 20,
    skip_recent: int = 1,
) -> pd.DataFrame:
    """
    Realized volatility using log returns.

    Log returns are often preferred for volatility calculations as they
    are symmetric and additive over time.

    Args:
        prices: DataFrame with close prices
        lookback: Number of days for calculation
        skip_recent: Days to skip (default=1)

    Returns:
        DataFrame with volatility values
    """
    if lookback < 2:
        raise ValueError("lookback must be >= 2")
    if skip_recent < 1:
        raise ValueError("skip_recent must be >= 1")

    log_returns = np.log(prices / prices.shift(1))

    lagged_log_returns = log_returns.shift(skip_recent)

    vol = lagged_log_returns.rolling(window=lookback, min_periods=lookback).std()

    return vol
