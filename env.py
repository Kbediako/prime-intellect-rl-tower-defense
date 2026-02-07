"""CLI-facing shim to satisfy Prime env packaging checks."""

from prime_td_env import load_environment

__all__ = ["load_environment"]
