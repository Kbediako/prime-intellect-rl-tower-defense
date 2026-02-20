"""Compatibility alias for the Tower Defence environment.

The canonical implementation lives in `prime_td_env`. This module exists so the
hub environment name can be a valid Python import (`tower_defence`) while
sharing the same implementation.
"""

from prime_td_env.environment import load_environment

__all__ = ["load_environment"]

