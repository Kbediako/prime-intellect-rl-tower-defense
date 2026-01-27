"""Verifiers-compatible environment stub.

The real implementation should follow Prime Intellect verifiers environment
contract and expose load_environment(config: dict) -> env.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class EnvState:
    """Placeholder state container."""

    round: int
    lives: int
    cash: int
    seed: int


class TowerDefenseEnv:
    """Minimal stub to define the interface expected by verifiers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state = None

    def reset(self, seed: int | None = None) -> Dict[str, Any]:
        seed_value = int(seed or 0)
        self.state = EnvState(round=1, lives=100, cash=650, seed=seed_value)
        return {
            "round": self.state.round,
            "lives": self.state.lives,
            "cash": self.state.cash,
            "seed": self.state.seed,
        }

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Stub step; returns no reward and immediate termination."""

        observation = {
            "round": self.state.round if self.state else 1,
            "lives": self.state.lives if self.state else 100,
            "cash": self.state.cash if self.state else 650,
        }
        reward = 0.0
        done = True
        info = {"reason": "stub"}
        return observation, reward, done, info


def load_environment(config: Dict[str, Any]) -> TowerDefenseEnv:
    """Prime Intellect verifiers entrypoint."""

    return TowerDefenseEnv(config)
