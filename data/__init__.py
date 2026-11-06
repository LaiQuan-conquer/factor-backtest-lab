"""
Data module for factor-backtest-lab.

Provides data fetching interfaces and test fixtures.
All data sources are public (AkShare, yfinance).
"""

from data.fetcher import DataFetcher
from data.fixtures import generate_fixture_data, load_fixture

__all__ = ["DataFetcher", "generate_fixture_data", "load_fixture"]
