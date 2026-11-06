"""
CLI entry point for factor-backtest-lab.

Usage:
    python -m factor_backtest_lab [command]

Commands:
    demo    Run a demo backtest on synthetic data
    help    Show this help message
"""

import argparse
import sys


def run_demo() -> None:
    """Run demo backtest on synthetic fixture data."""
    print("=" * 60)
    print("Factor Backtest Lab - Demo")
    print("=" * 60)
    print()
    print("DISCLAIMER: This is for educational purposes only.")
    print("Results do NOT indicate future performance.")
    print("NOT investment advice. NOT for live trading.")
    print()
    print("-" * 60)

    from data.fixtures import load_fixture, fixture_to_panel
    from factors import momentum_factor, reversal_factor, realized_volatility_factor
    from backtest import BacktestEngine, BacktestConfig
    from backtest.engine import compare_cost_modes
    from analysis.tearsheet import print_summary

    print("\n[1/4] Loading synthetic fixture data...")
    fixture = load_fixture("default")
    prices = fixture_to_panel(fixture, "close")
    print(f"     Loaded {len(prices)} days, {len(prices.columns)} symbols")

    print("\n[2/4] Calculating factors...")
    momentum = momentum_factor(prices, lookback=10, skip_recent=1)
    reversal = reversal_factor(prices, lookback=5, skip_recent=1)
    volatility = realized_volatility_factor(prices, lookback=20, skip_recent=1)

    print(f"     Momentum: {momentum.notna().sum().sum()} valid values")
    print(f"     Reversal: {reversal.notna().sum().sum()} valid values")
    print(f"     Volatility: {volatility.notna().sum().sum()} valid values")

    print("\n[3/4] Running backtest with momentum factor...")
    results = compare_cost_modes(prices, momentum)

    print("\n--- Zero Cost Backtest ---")
    print_summary(results["zero_cost"])

    print("\n--- With Cost Backtest ---")
    print_summary(results["with_cost"])

    print("\n[4/4] Cost Impact Analysis")
    print("-" * 60)
    zero_return = results["zero_cost"].total_return
    cost_return = results["with_cost"].total_return
    cost_drag = zero_return - cost_return

    print(f"Zero-cost return: {zero_return:.2%}")
    print(f"With-cost return: {cost_return:.2%}")
    print(f"Cost drag: {cost_drag:.2%}")
    print()
    print("Note: The difference shows the impact of transaction costs.")
    print("      This is a key insight for realistic strategy evaluation.")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="factor-lab",
        description="Factor Backtest Lab - Personal research tools for classic factor construction",
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="demo",
        choices=["demo", "help"],
        help="Command to run (default: demo)",
    )

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        return 0

    if args.command == "demo":
        run_demo()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
