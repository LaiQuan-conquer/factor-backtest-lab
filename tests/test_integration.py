"""Integration tests for the full pipeline."""

import pytest

from data.fixtures import load_fixture, fixture_to_panel
from factors import momentum_factor, reversal_factor, realized_volatility_factor
from backtest import BacktestEngine, BacktestConfig
from backtest.engine import compare_cost_modes
from analysis.tearsheet import generate_summary, factor_stats


class TestFullPipeline:
    """Tests for the complete data -> factor -> backtest -> analysis pipeline."""

    def test_complete_pipeline_runs(self):
        """Full pipeline should run without errors."""
        data = load_fixture("default")
        prices = fixture_to_panel(data, "close")

        momentum = momentum_factor(prices, lookback=10, skip_recent=1)
        reversal = reversal_factor(prices, lookback=5, skip_recent=1)
        volatility = realized_volatility_factor(prices, lookback=20, skip_recent=1)

        for factor_name, factor_values in [
            ("momentum", momentum),
            ("reversal", reversal),
            ("volatility", volatility),
        ]:
            results = compare_cost_modes(prices, factor_values)

            for mode, result in results.items():
                summary = generate_summary(result)

                assert "total_return" in summary
                assert "n_trades" in summary
                assert "cost_mode" in summary
                assert summary["cost_mode"] == mode

    def test_factor_stats_calculation(self):
        """Factor stats should be calculable for all factors."""
        data = load_fixture("default")
        prices = fixture_to_panel(data, "close")

        momentum = momentum_factor(prices, lookback=10, skip_recent=1)

        stats = factor_stats(momentum)

        assert stats["n_dates"] == len(momentum)
        assert stats["n_symbols"] == len(momentum.columns)
        assert 0 <= stats["coverage"] <= 1

    def test_different_factors_produce_different_results(self):
        """Different factors should lead to different backtest results."""
        data = load_fixture("default")
        prices = fixture_to_panel(data, "close")

        momentum = momentum_factor(prices, lookback=10, skip_recent=1)
        reversal = reversal_factor(prices, lookback=5, skip_recent=1)

        config = BacktestConfig(cost_mode="zero_cost")
        engine = BacktestEngine(config)

        mom_result = engine.run(prices, momentum)
        rev_result = engine.run(prices, reversal)

        assert mom_result.total_return != rev_result.total_return


class TestDemoRuns:
    """Tests that the demo module runs correctly."""

    def test_demo_module_imports(self):
        """Demo module should be importable."""
        from factor_backtest_lab.__main__ import run_demo, main

        assert callable(run_demo)
        assert callable(main)

    def test_demo_runs_without_error(self, capsys):
        """Demo should run and produce output."""
        from factor_backtest_lab.__main__ import run_demo

        run_demo()

        captured = capsys.readouterr()
        assert "Factor Backtest Lab - Demo" in captured.out
        assert "Demo completed successfully" in captured.out
        assert "Cost Impact Analysis" in captured.out
