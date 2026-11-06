"""Tests for factor calculations."""

import numpy as np
import pandas as pd
import pytest

from data.fixtures import load_fixture, fixture_to_panel
from factors import momentum_factor, reversal_factor, realized_volatility_factor


class TestMomentumFactor:
    """Tests for momentum factor."""

    @pytest.fixture
    def prices(self):
        """Simple price series for testing."""
        dates = pd.bdate_range("2024-01-01", periods=10)
        return pd.DataFrame({
            "A": [100, 102, 104, 103, 105, 107, 106, 108, 110, 112],
            "B": [50, 49, 48, 47, 46, 45, 44, 43, 42, 41],
        }, index=dates)

    def test_uses_lagged_prices(self, prices):
        """Momentum should use t-1 price, not t price (avoid look-ahead)."""
        mom = momentum_factor(prices, lookback=3, skip_recent=1)

        mom_at_day_5 = mom.iloc[4]
        price_t_minus_1 = prices.iloc[3]
        price_t_minus_lookback = prices.iloc[1]
        expected = (price_t_minus_1 / price_t_minus_lookback) - 1

        pd.testing.assert_series_equal(
            mom_at_day_5.dropna(),
            expected.dropna(),
            check_names=False
        )

    def test_positive_momentum_for_uptrend(self, prices):
        """Stock A (uptrend) should have positive momentum."""
        mom = momentum_factor(prices, lookback=5, skip_recent=1)

        valid_mom = mom["A"].dropna()
        assert (valid_mom > 0).any(), "Uptrending stock should have positive momentum"

    def test_negative_momentum_for_downtrend(self, prices):
        """Stock B (downtrend) should have negative momentum."""
        mom = momentum_factor(prices, lookback=5, skip_recent=1)

        valid_mom = mom["B"].dropna()
        assert (valid_mom < 0).all(), "Downtrending stock should have negative momentum"

    def test_requires_positive_skip_recent(self, prices):
        """skip_recent must be >= 1 to avoid look-ahead."""
        with pytest.raises(ValueError, match="skip_recent must be >= 1"):
            momentum_factor(prices, lookback=5, skip_recent=0)

    def test_nan_for_insufficient_history(self, prices):
        """First rows should be NaN due to insufficient history."""
        mom = momentum_factor(prices, lookback=5, skip_recent=1)

        assert mom.iloc[0].isna().all()
        assert mom.iloc[4].isna().all()
        assert mom.iloc[5].notna().all()


class TestReversalFactor:
    """Tests for reversal factor."""

    @pytest.fixture
    def prices(self):
        """Price series with known patterns."""
        dates = pd.bdate_range("2024-01-01", periods=10)
        return pd.DataFrame({
            "A": [100, 110, 105, 115, 110, 120, 115, 125, 120, 130],
        }, index=dates)

    def test_reversal_is_negative_momentum(self, prices):
        """Reversal should be negative of momentum."""
        mom = momentum_factor(prices, lookback=3, skip_recent=1)
        rev = reversal_factor(prices, lookback=3, skip_recent=1)

        pd.testing.assert_frame_equal(rev, -mom)

    def test_requires_positive_skip_recent(self, prices):
        """skip_recent must be >= 1."""
        with pytest.raises(ValueError, match="skip_recent must be >= 1"):
            reversal_factor(prices, lookback=3, skip_recent=0)


class TestRealizedVolatilityFactor:
    """Tests for realized volatility factor."""

    @pytest.fixture
    def prices(self):
        """Price series for volatility testing."""
        dates = pd.bdate_range("2024-01-01", periods=30)
        np.random.seed(42)

        high_vol = 100 * np.cumprod(1 + np.random.normal(0, 0.05, 30))
        low_vol = 100 * np.cumprod(1 + np.random.normal(0, 0.01, 30))

        return pd.DataFrame({
            "HIGH_VOL": high_vol,
            "LOW_VOL": low_vol,
        }, index=dates)

    def test_higher_vol_stock_has_higher_value(self, prices):
        """High volatility stock should have higher realized vol."""
        vol = realized_volatility_factor(prices, lookback=10, skip_recent=1)

        valid_vol = vol.dropna()
        assert (valid_vol["HIGH_VOL"] > valid_vol["LOW_VOL"]).all()

    def test_volatility_is_positive(self, prices):
        """Volatility should always be non-negative."""
        vol = realized_volatility_factor(prices, lookback=10, skip_recent=1)

        assert (vol.dropna() >= 0).all().all()

    def test_requires_minimum_lookback(self, prices):
        """lookback must be >= 2 for meaningful volatility."""
        with pytest.raises(ValueError, match="lookback must be >= 2"):
            realized_volatility_factor(prices, lookback=1, skip_recent=1)

    def test_requires_positive_skip_recent(self, prices):
        """skip_recent must be >= 1."""
        with pytest.raises(ValueError, match="skip_recent must be >= 1"):
            realized_volatility_factor(prices, lookback=10, skip_recent=0)


class TestFactorsOnFixture:
    """Integration tests with fixture data."""

    def test_all_factors_run_on_fixture(self):
        """All factors should run without error on fixture data."""
        data = load_fixture("default")
        prices = fixture_to_panel(data, "close")

        mom = momentum_factor(prices, lookback=10, skip_recent=1)
        rev = reversal_factor(prices, lookback=5, skip_recent=1)
        vol = realized_volatility_factor(prices, lookback=20, skip_recent=1)

        assert mom.shape == prices.shape
        assert rev.shape == prices.shape
        assert vol.shape == prices.shape

        assert mom.notna().sum().sum() > 0
        assert rev.notna().sum().sum() > 0
        assert vol.notna().sum().sum() > 0
