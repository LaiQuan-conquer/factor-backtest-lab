"""Tests for data fixtures."""

import pandas as pd
import pytest

from data.fixtures import generate_fixture_data, load_fixture, fixture_to_panel


class TestGenerateFixtureData:
    """Tests for generate_fixture_data function."""

    def test_returns_dict_of_dataframes(self):
        """Generated data should be dict of DataFrames."""
        data = generate_fixture_data(n_days=10, n_symbols=3, seed=42)

        assert isinstance(data, dict)
        assert len(data) == 3

        for symbol, df in data.items():
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 10

    def test_dataframe_has_ohlcv_columns(self):
        """Each DataFrame should have OHLCV columns."""
        data = generate_fixture_data(n_days=10, n_symbols=1, seed=42)
        df = list(data.values())[0]

        expected_columns = ["open", "high", "low", "close", "volume"]
        assert list(df.columns) == expected_columns

    def test_deterministic_with_same_seed(self):
        """Same seed should produce identical data."""
        data1 = generate_fixture_data(n_days=20, n_symbols=3, seed=123)
        data2 = generate_fixture_data(n_days=20, n_symbols=3, seed=123)

        for symbol in data1:
            pd.testing.assert_frame_equal(data1[symbol], data2[symbol])

    def test_different_seeds_produce_different_data(self):
        """Different seeds should produce different data."""
        data1 = generate_fixture_data(n_days=20, n_symbols=1, seed=1)
        data2 = generate_fixture_data(n_days=20, n_symbols=1, seed=2)

        symbol = list(data1.keys())[0]
        assert not data1[symbol]["close"].equals(data2[symbol]["close"])

    def test_price_constraints(self):
        """Prices should follow OHLC constraints: low <= open,close <= high."""
        data = generate_fixture_data(n_days=50, n_symbols=5, seed=42)

        for symbol, df in data.items():
            assert (df["low"] <= df["open"]).all(), f"{symbol}: low > open"
            assert (df["low"] <= df["close"]).all(), f"{symbol}: low > close"
            assert (df["high"] >= df["open"]).all(), f"{symbol}: high < open"
            assert (df["high"] >= df["close"]).all(), f"{symbol}: high < close"


class TestLoadFixture:
    """Tests for load_fixture function."""

    def test_load_default_fixture(self):
        """Default fixture should load with 60 days, 5 symbols."""
        data = load_fixture("default")

        assert len(data) == 5
        for df in data.values():
            assert len(df) == 60

    def test_load_minimal_fixture(self):
        """Minimal fixture should load with 20 days, 3 symbols."""
        data = load_fixture("minimal")

        assert len(data) == 3
        for df in data.values():
            assert len(df) == 20

    def test_load_single_fixture(self):
        """Single fixture should load with 30 days, 1 symbol."""
        data = load_fixture("single")

        assert len(data) == 1
        for df in data.values():
            assert len(df) == 30

    def test_unknown_fixture_raises(self):
        """Unknown fixture name should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown fixture"):
            load_fixture("nonexistent")


class TestFixtureToPanel:
    """Tests for fixture_to_panel function."""

    def test_converts_to_panel(self):
        """Should convert dict to panel DataFrame."""
        data = load_fixture("minimal")
        panel = fixture_to_panel(data, "close")

        assert isinstance(panel, pd.DataFrame)
        assert len(panel.columns) == 3
        assert len(panel) == 20

    def test_extracts_correct_field(self):
        """Should extract the specified field."""
        data = load_fixture("single")
        symbol = list(data.keys())[0]

        close_panel = fixture_to_panel(data, "close")
        assert close_panel[symbol].equals(data[symbol]["close"])

        volume_panel = fixture_to_panel(data, "volume")
        assert volume_panel[symbol].equals(data[symbol]["volume"])
