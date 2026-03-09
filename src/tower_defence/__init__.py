"""Compatibility alias for the Tower Defence environment package.

The hosted env slug resolves to ``tower_defence`` during installation, so this
module must delegate through the same loader entrypoint as ``env.py`` and
``prime_td_env``. Importing the legacy environment directly bypasses wrapper
dispatch and silently routes hosted evals back onto the old macro-round env.
"""

from prime_td_env.loader import load_environment

__all__ = ["load_environment"]
