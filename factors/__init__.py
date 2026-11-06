"""
Factor definitions module.

Classic textbook factor constructions for research purposes.
All factors use lagged data to avoid look-ahead bias.

Available factors:
    - Momentum: Past N-day cumulative return
    - Reversal: Short-term mean reversion signal
    - RealizedVolatility: Standard deviation of past returns
"""

from factors.momentum import momentum_factor
from factors.reversal import reversal_factor
from factors.volatility import realized_volatility_factor

__all__ = [
    "momentum_factor",
    "reversal_factor",
    "realized_volatility_factor",
]
