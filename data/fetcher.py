"""
Data fetching interface for public market data.

Supports AkShare (A-share) and yfinance (global) as data sources.
All data is public and freely available.

Note: For testing, use fixtures.py instead to avoid network dependencies.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pandas as pd


class DataFetcher(ABC):
    """Abstract base class for data fetchers."""

    @abstractmethod
    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Fetch daily OHLCV bars for a symbol.

        Args:
            symbol: Stock symbol/ticker
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
            Index should be DatetimeIndex
        """
        pass


class YFinanceFetcher(DataFetcher):
    """
    Fetcher using yfinance for Yahoo Finance public data.

    Requires: pip install yfinance
    """

    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Fetch daily bars from Yahoo Finance."""
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError(
                "yfinance not installed. Install with: pip install yfinance"
            )

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)

        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })

        df.index.name = "date"
        return df[["open", "high", "low", "close", "volume"]]


class AkShareFetcher(DataFetcher):
    """
    Fetcher using AkShare for A-share public data.

    Requires: pip install akshare
    """

    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Fetch daily bars from AkShare."""
        try:
            import akshare as ak
        except ImportError:
            raise ImportError(
                "akshare not installed. Install with: pip install akshare"
            )

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
            adjust="qfq",  # 前复权
        )

        df = df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        })

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        return df[["open", "high", "low", "close", "volume"]]


class CachedFetcher(DataFetcher):
    """
    Wrapper that caches fetched data to disk.

    Reduces API calls and enables offline replay.
    """

    def __init__(
        self,
        base_fetcher: DataFetcher,
        cache_dir: Optional[Path] = None,
    ):
        self.base_fetcher = base_fetcher
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, symbol: str, start_date: str, end_date: str) -> Path:
        """Generate cache file path."""
        filename = f"{symbol}_{start_date}_{end_date}.parquet"
        return self.cache_dir / filename

    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Fetch from cache if available, otherwise fetch and cache."""
        cache_path = self._cache_path(symbol, start_date, end_date)

        if cache_path.exists():
            return pd.read_parquet(cache_path)

        df = self.base_fetcher.fetch_daily_bars(symbol, start_date, end_date)
        df.to_parquet(cache_path)
        return df
