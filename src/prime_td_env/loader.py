"""Entrypoint dispatch for legacy and actual-game environment families."""

from __future__ import annotations

from typing import Any, Dict

ACTUAL_GAME_WRAPPERS = {
    "actual_game_command",
    "benchmark_commands",
}


def load_environment(
    config: Dict[str, Any] | None = None,
    num_examples: int = 64,
    seed_start: int = 0,
    **kwargs: Any,
):
    wrapper = ""
    if isinstance(config, dict):
        wrapper = str(config.get("wrapper", "") or "").lower()
    if wrapper in ACTUAL_GAME_WRAPPERS:
        from . import actual_game_env

        return actual_game_env.load_environment(
            config=config,
            num_examples=num_examples,
            seed_start=seed_start,
            **kwargs,
        )
    from . import environment as legacy_environment

    return legacy_environment.load_environment(
        config=config,
        num_examples=num_examples,
        seed_start=seed_start,
        **kwargs,
    )


__all__ = ["load_environment"]
