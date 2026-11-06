"""
Synthetic test fixtures for offline testing.

Generates deterministic, reproducible data that mimics daily bar structure.
No network or API keys required.

These fixtures are NOT real market data - they are synthetic patterns
designed to test factor calculations and backtest logic.
"""

import numpy as np
import pandas as pd


def generate_fixture_data(
    n_days: int = 60,
    n_symbols: int = 5,
    seed: int = 42,
    base_price: float = 100.0,
    daily_vol: float = 0.02,
) -> dict[str, pd.DataFrame]:
    """
    Generate synthetic daily bar data for testing.

    The data has deterministic patterns:
    - Symbol 0: Upward drift (positive momentum)
    - Symbol 1: Downward drift (negative momentum)
    - Symbol 2: Mean-reverting (high reversal signal)
    - Symbol 3: High volatility
    - Symbol 4: Low volatility / stable

    Args:
        n_days: Number of trading days
        n_symbols: Number of symbols
        seed: Random seed for reproducibility
        base_price: Starting price level
        daily_vol: Base daily volatility

    Returns:
        Dict mapping symbol names to DataFrames with OHLCV data
    """
    rng = np.random.default_rng(seed)

    dates = pd.bdate_range(start="2024-01-01", periods=n_days, freq="B")

    data = {}

    for i in range(n_symbols):
        symbol = f"SYM{i:03d}"

        if i == 0:
            drift = 0.001
            vol = daily_vol
        elif i == 1:
            drift = -0.001
            vol = daily_vol
        elif i == 2:
            drift = 0.0
            vol = daily_vol * 1.5
        elif i == 3:
            drift = 0.0
            vol = daily_vol * 2.5
        else:
            drift = 0.0
            vol = daily_vol * 0.5

        returns = rng.normal(drift, vol, n_days)

        if i == 2:
            for j in range(1, n_days):
                returns[j] -= 0.3 * returns[j - 1]

        prices = base_price * np.cumprod(1 + returns)

        high = prices * (1 + rng.uniform(0, 0.01, n_days))
        low = prices * (1 - rng.uniform(0, 0.01, n_days))
        open_price = low + rng.uniform(0.3, 0.7, n_days) * (high - low)
        volume = rng.integers(100000, 1000000, n_days)

        df = pd.DataFrame({
            "open": open_price,
            "high": high,
            "low": low,
            "close": prices,
            "volume": volume,
        }, index=dates)
        df.index.name = "date"

        data[symbol] = df

    return data


def load_fixture(fixture_name: str = "default") -> dict[str, pd.DataFrame]:
    """
    Load a predefined test fixture.

    Args:
        fixture_name: Name of fixture to load

    Returns:
        Dict mapping symbol names to DataFrames

    Available fixtures:
        - "default": 60 days, 5 symbols with varied characteristics
        - "minimal": 20 days, 3 symbols for quick tests
        - "single": 30 days, 1 symbol for unit tests
    """
    fixtures = {
        "default": lambda: generate_fixture_data(n_days=60, n_symbols=5, seed=42),
        "minimal": lambda: generate_fixture_data(n_days=20, n_symbols=3, seed=42),
        "single": lambda: generate_fixture_data(n_days=30, n_symbols=1, seed=42),
    }

    if fixture_name not in fixtures:
        raise ValueError(f"Unknown fixture: {fixture_name}. Available: {list(fixtures.keys())}")

    return fixtures[fixture_name]()


def fixture_to_panel(data: dict[str, pd.DataFrame], field: str = "close") -> pd.DataFrame:
    """
    Convert fixture dict to a panel DataFrame.

    Args:
        data: Dict from generate_fixture_data or load_fixture
        field: OHLCV field to extract ("open", "high", "low", "close", "volume")

    Returns:
        DataFrame with dates as index and symbols as columns
    """
    return pd.DataFrame({
        symbol: df[field] for symbol, df in data.items()
    })
