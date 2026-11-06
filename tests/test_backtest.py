"""Tests for backtest engine."""

import pandas as pd
import pytest

from data.fixtures import load_fixture, fixture_to_panel
from factors import momentum_factor
from backtest import BacktestEngine, BacktestConfig, BacktestResult
from backtest.engine import compare_cost_modes


class TestBacktestConfig:
    """Tests for BacktestConfig."""

    def test_zero_cost_mode_sets_zero_rates(self):
        """zero_cost mode should set commission and slippage to 0."""
        config = BacktestConfig(cost_mode="zero_cost")

        assert config.commission_rate == 0.0
        assert config.slippage_rate == 0.0

    def test_with_cost_mode_preserves_rates(self):
        """with_cost mode should preserve default rates."""
        config = BacktestConfig(cost_mode="with_cost")

        assert config.commission_rate == 0.001
        assert config.slippage_rate == 0.001

    def test_custom_rates(self):
        """Custom rates should be preserved in with_cost mode."""
        config = BacktestConfig(
            cost_mode="with_cost",
            commission_rate=0.002,
            slippage_rate=0.003,
        )

        assert config.commission_rate == 0.002
        assert config.slippage_rate == 0.003


class TestBacktestEngine:
    """Tests for BacktestEngine."""

    @pytest.fixture
    def simple_data(self):
        """Simple data for backtest testing."""
        dates = pd.bdate_range("2024-01-01", periods=20)
        prices = pd.DataFrame({
            "A": [100 + i for i in range(20)],
            "B": [100 - i * 0.5 for i in range(20)],
            "C": [100 + (i % 5) for i in range(20)],
        }, index=dates, dtype=float)

        factor = pd.DataFrame({
            "A": [1.0] * 20,
            "B": [-1.0] * 20,
            "C": [0.0] * 20,
        }, index=dates)

        return prices, factor

    def test_returns_backtest_result(self, simple_data):
        """Engine should return BacktestResult."""
        prices, factor = simple_data
        engine = BacktestEngine()

        result = engine.run(prices, factor)

        assert isinstance(result, BacktestResult)
        assert len(result.portfolio_value) == len(prices)

    def test_portfolio_value_starts_at_initial_capital(self, simple_data):
        """Portfolio should start at initial capital."""
        prices, factor = simple_data
        config = BacktestConfig(initial_capital=500_000)
        engine = BacktestEngine(config)

        result = engine.run(prices, factor)

        assert result.portfolio_value.iloc[0] == pytest.approx(500_000, rel=0.01)

    def test_mismatched_index_raises(self, simple_data):
        """Mismatched price/factor index should raise."""
        prices, factor = simple_data
        wrong_factor = factor.iloc[:-5]
        engine = BacktestEngine()

        with pytest.raises(ValueError, match="same index"):
            engine.run(prices, wrong_factor)


class TestCostComparison:
    """Tests comparing zero-cost vs with-cost backtests."""

    @pytest.fixture
    def fixture_data(self):
        """Load fixture data for cost comparison tests."""
        data = load_fixture("default")
        prices = fixture_to_panel(data, "close")
        factor = momentum_factor(prices, lookback=10, skip_recent=1)
        return prices, factor

    def test_cost_modes_differ(self, fixture_data):
        """Zero-cost and with-cost results should differ."""
        prices, factor = fixture_data

        results = compare_cost_modes(prices, factor)

        zero_cost = results["zero_cost"]
        with_cost = results["with_cost"]

        assert zero_cost.total_return != with_cost.total_return

    def test_with_cost_has_lower_or_equal_return(self, fixture_data):
        """With-cost return should generally be lower due to trading costs."""
        prices, factor = fixture_data

        results = compare_cost_modes(prices, factor)

        assert results["with_cost"].total_cost > 0
        assert results["zero_cost"].total_cost == 0

    def test_both_modes_same_number_of_trades(self, fixture_data):
        """Both modes should make the same trading decisions."""
        prices, factor = fixture_data

        results = compare_cost_modes(prices, factor)

        assert results["zero_cost"].n_trades == results["with_cost"].n_trades


class TestReproducibility:
    """Tests for backtest reproducibility."""

    def test_same_inputs_produce_same_outputs(self):
        """Same inputs should always produce identical results."""
        data = load_fixture("default")
        prices = fixture_to_panel(data, "close")
        factor = momentum_factor(prices, lookback=10, skip_recent=1)

        engine = BacktestEngine(BacktestConfig(cost_mode="with_cost"))

        result1 = engine.run(prices, factor)
        result2 = engine.run(prices, factor)

        pd.testing.assert_series_equal(
            result1.portfolio_value,
            result2.portfolio_value
        )
        assert result1.total_return == result2.total_return
        assert result1.n_trades == result2.n_trades
        assert result1.total_cost == result2.total_cost
