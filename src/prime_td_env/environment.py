"""Tower-defense environment with a minimal deterministic simulation core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
import copy
import json
import random
import re

import verifiers as vf
from datasets import Dataset

@dataclass
class EnvState:
    round: int
    lives: int
    cash: int
    seed: int
    steps: int = 0
    phase: str = "build"
    last_round: Dict[str, Any] = field(default_factory=dict)
    prep_actions_remaining: int = 1
    prep_actions_max: int = 1


@dataclass
class UpgradeTier:
    cost: int
    damage_add: float = 0.0
    range_add: float = 0.0
    pierce_add: int = 0
    fire_rate_add: float = 0.0


@dataclass
class TowerType:
    name: str
    cost: int
    range: float
    damage: float
    pierce: int
    fire_rate: float
    upgrade_paths: Dict[str, List[UpgradeTier]] = field(default_factory=dict)

    def stats_with_upgrades(self, upgrades: Dict[str, int]) -> Dict[str, float]:
        damage = self.damage
        range_value = self.range
        pierce = self.pierce
        fire_rate = self.fire_rate
        for path, tiers in self.upgrade_paths.items():
            applied = upgrades.get(path, 0)
            for tier in range(applied):
                effect = tiers[tier]
                damage += effect.damage_add
                range_value += effect.range_add
                pierce += effect.pierce_add
                fire_rate += effect.fire_rate_add
        return {
            "damage": max(0.0, damage),
            "range": max(0.1, range_value),
            "pierce": max(1, pierce),
            "fire_rate": max(0.1, fire_rate),
        }

    def upgrade_cost(self, path: str, tier: int) -> int:
        return self.upgrade_paths[path][tier].cost


@dataclass
class Tower:
    id: int
    type_name: str
    x: int
    y: int
    upgrades: Dict[str, int] = field(default_factory=dict)
    targeting: str = "first"
    cooldown: int = 0


@dataclass
class BloonType:
    name: str
    hp: float
    speed: float
    reward: int
    tier: int
    children: List[str] = field(default_factory=list)
    traits: List[str] = field(default_factory=list)


@dataclass
class Bloon:
    id: int
    type_name: str
    hp: float
    speed: float
    reward: int
    position: float
    children: List[str]


@dataclass
class SpawnEvent:
    tick: int
    type_name: str


DEFAULT_CONFIG: Dict[str, Any] = {
    "wrapper": None,
    "map": {
        "width": 10,
        "height": 8,
        "seed": 0,
        "path": None,
        "path_turn_chance": 0.25,
        "build_slots": None,
    },
    "economy": {
        "starting_cash": 650,
        "starting_lives": 100,
        "sell_refund_ratio": 0.7,
        "end_round_income": 100,
    },
    "episode": {
        "max_steps": None,
    },
    "difficulty": {
        "max_rounds": None,
        "health_scale_per_round": 0.02,
        "speed_scale_per_round": 0.005,
    },
    "simulation": {
        "max_ticks_per_round": 500,
        "spawn_interval_ticks": 2,
    },
    "rewards": {
        "pop_reward_multiplier": 1.0,
        "life_loss_penalty": 10.0,
        "invalid_action_penalty": 1.0,
        "step_penalty": 0.1,
        "macro_round_invariant_penalty": 50.0,
    },
    "reward_shaping": {
        "enable_lookahead": False,
        "lookahead_rounds": 1,
        "lookahead_weight": 0.5,
        "delta_reward": False,
        "regret_metric": False,
    },
    "rules": {
        "require_tower_before_start": False,
        "auto_advance_round": False,
        "prep_actions_per_round": 1,
        "prep_actions_round_scale": 0.0,
        "prep_actions_max": None,
        "start_round_max_prep_remaining": None,
        "mask_sell": False,
        "require_choose": False,
    },
    "reward_weights": {
        "format": 0.5,
        "env": 1.0,
    },
    "observation": {
        "max_action_candidates": 200,
        "max_build_slots": 200,
        "max_towers": 50,
        "max_threats": 5,
        "max_path_points": None,
    },
    "dataset": {
        "rollout_steps": 0,
        "policy": "random",
        "num_seeds": None,
        "snapshots": {},
        "snapshots_per_seed": 0,
        "safe_explore_upgrade_prob": 0.5,
        "diagnostics": {},
        "margin_min": 0.0,
        "require_best_types": None,
    },
    "towers": {
        "dart": {
            "cost": 200,
            "range": 3.5,
            "damage": 1.0,
            "pierce": 1,
            "fire_rate": 1.0,
            "upgrade_paths": {
                "a": [
                    {"cost": 100, "damage_add": 1.0},
                    {"cost": 200, "damage_add": 2.0},
                    {"cost": 400, "damage_add": 3.0},
                ],
                "b": [
                    {"cost": 80, "range_add": 0.5},
                    {"cost": 160, "range_add": 1.0},
                    {"cost": 320, "range_add": 1.5},
                ],
                "c": [
                    {"cost": 90, "fire_rate_add": 0.2},
                    {"cost": 180, "fire_rate_add": 0.4},
                    {"cost": 360, "fire_rate_add": 0.6},
                ],
            },
        }
    },
    "bloons": {
        "red": {"hp": 1.0, "speed": 1.0, "reward": 1, "tier": 0},
        "blue": {"hp": 2.0, "speed": 1.1, "reward": 2, "tier": 1, "children": ["red"]},
        "green": {"hp": 3.0, "speed": 1.2, "reward": 3, "tier": 2, "children": ["blue"]},
        "yellow": {"hp": 4.0, "speed": 1.5, "reward": 4, "tier": 3, "children": ["green"]},
        "lead": {"hp": 6.0, "speed": 0.8, "reward": 6, "tier": 4, "traits": ["fortified"]},
        "moab": {
            "hp": 40.0,
            "speed": 0.6,
            "reward": 40,
            "tier": 5,
            "children": ["yellow", "yellow", "yellow", "yellow"],
            "traits": ["moab"],
        },
    },
}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class TowerDefenseEnv:
    """Deterministic tower-defense environment with between-round actions."""

    def __init__(self, config: Dict[str, Any]):
        self.config = deep_merge(DEFAULT_CONFIG, config or {})
        self.env_id: str | None = None
        self.env_args: Dict[str, Any] | None = None
        self.rng = random.Random(0)
        self.state: EnvState | None = None
        self.tower_types = self._load_tower_types()
        self.bloon_types = self._load_bloon_types()
        self.path = self._init_path()
        self.build_slots = self._init_build_slots()
        self._cached_action_candidates: List[Dict[str, Any]] | None = None
        self.towers: Dict[int, Tower] = {}
        self.next_tower_id = 1
        self.next_bloon_id = 1

    def _prep_actions_for_round(self, round_number: int) -> int:
        rules = self.config.get("rules", {}) if isinstance(self.config.get("rules"), dict) else {}
        auto_advance = bool(rules.get("auto_advance_round", False))
        if not auto_advance:
            return 1
        base = _coerce_int(rules.get("prep_actions_per_round"))
        base = 1 if base is None else max(1, base)
        scale = float(rules.get("prep_actions_round_scale", 0.0) or 0.0)
        if scale < 0:
            scale = 0.0
        extra = int((max(1, round_number) - 1) * scale)
        total = max(1, base + extra)
        max_cap = _coerce_int(rules.get("prep_actions_max"))
        if max_cap is not None:
            total = min(total, max(1, max_cap))
        return total

    def _reset_prep_actions(self) -> None:
        if self.state is None:
            return
        total = self._prep_actions_for_round(self.state.round)
        self.state.prep_actions_max = total
        self.state.prep_actions_remaining = total

    def _normalize_upgrades(self, tower_type: TowerType, upgrades: Any) -> Dict[str, int]:
        if not isinstance(upgrades, dict):
            return {}
        normalized: Dict[str, int] = {}
        for path, tier in upgrades.items():
            if path not in tower_type.upgrade_paths:
                continue
            coerced = _coerce_int(tier)
            max_tier = len(tower_type.upgrade_paths[path])
            if coerced is None:
                normalized[path] = 0
            else:
                normalized[path] = max(0, min(coerced, max_tier))
        return normalized

    def _get_upgrade_tier(self, tower: Tower, path: str) -> int:
        tier = _coerce_int(tower.upgrades.get(path, 0))
        return max(0, tier) if tier is not None else 0

    def reset(self, seed: int | None = None) -> Dict[str, Any]:
        seed_value = int(seed if seed is not None else self.config["map"]["seed"])
        self.rng = random.Random(seed_value)
        self.state = EnvState(
            round=1,
            lives=self.config["economy"]["starting_lives"],
            cash=self.config["economy"]["starting_cash"],
            seed=seed_value,
            steps=0,
            phase="build",
            last_round={},
        )
        self._reset_prep_actions()
        self.towers = {}
        self.next_tower_id = 1
        self.next_bloon_id = 1
        self.path = self._init_path()
        self.build_slots = self._init_build_slots()
        return self._observation()

    def load_from_observation(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        seed_value = int(obs.get("seed", self.config["map"]["seed"]))
        self.rng = random.Random(seed_value)
        self.state = EnvState(
            round=int(obs.get("round", 1)),
            lives=int(obs.get("lives", self.config["economy"]["starting_lives"])),
            cash=int(obs.get("cash", self.config["economy"]["starting_cash"])),
            seed=seed_value,
            steps=int(obs.get("steps", 0)),
            phase=str(obs.get("phase", "build")),
            last_round=dict(obs.get("last_round", {}) or {}),
        )
        round_number = self.state.round
        prep_max = _coerce_int(obs.get("prep_actions_max"))
        if prep_max is None:
            prep_max = self._prep_actions_for_round(round_number)
        prep_remaining = _coerce_int(obs.get("prep_actions_remaining"))
        if prep_remaining is None:
            prep_remaining = prep_max
        self.state.prep_actions_max = max(1, int(prep_max))
        self.state.prep_actions_remaining = max(
            0,
            min(int(prep_remaining), self.state.prep_actions_max),
        )
        map_obs = obs.get("map", {}) if isinstance(obs.get("map"), dict) else {}
        if map_obs.get("path"):
            self.path = self._normalize_points(map_obs["path"], "map.path", min_points=2)
        else:
            self.path = self._init_path()

        candidate_slots: List[Tuple[int, int]] = []
        candidates = obs.get("action_candidates")
        if isinstance(candidates, list):
            for cand in candidates:
                if not isinstance(cand, dict) or cand.get("type") != "build":
                    continue
                x = cand.get("x")
                y = cand.get("y")
                if isinstance(x, int) and isinstance(y, int):
                    candidate_slots.append((x, y))

        map_slots: List[Tuple[int, int]] = []
        if map_obs.get("build_slots"):
            map_slots = self._normalize_points(map_obs["build_slots"], "map.build_slots")

        combined_slots = set(map_slots)
        if candidate_slots:
            combined_slots.update(candidate_slots)

        if combined_slots:
            self.build_slots = sorted(combined_slots)
        else:
            self.build_slots = self._init_build_slots()

        self.towers = {}
        self.next_tower_id = 1
        for tower in sorted(obs.get("towers", []), key=lambda t: int(t.get("id", 0))):
            tower_id = int(tower.get("id", self.next_tower_id))
            tower_type = self.tower_types.get(str(tower.get("type", "dart")))
            self.towers[tower_id] = Tower(
                id=tower_id,
                type_name=str(tower.get("type", "dart")),
                x=int(tower.get("x", 0)),
                y=int(tower.get("y", 0)),
                upgrades=self._normalize_upgrades(tower_type, tower.get("upgrades", {}))
                if tower_type
                else {},
                targeting=str(tower.get("targeting", "first")),
            )
            self.next_tower_id = max(self.next_tower_id, tower_id + 1)
        self.next_bloon_id = 1
        obs_out = self._observation(cache_action_candidates=False)
        if isinstance(candidates, list):
            self._cached_action_candidates = [c for c in candidates if isinstance(c, dict)]
        else:
            self._cached_action_candidates = None
        return obs_out

    def step(
        self,
        action: Dict[str, Any] | None,
        internal: bool = False,
    ) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if self.state is None:
            raise RuntimeError("reset must be called before step")

        self.state.steps += 1
        invalid_action = False
        invalid_reason = ""
        completed_round = False
        round_info: Dict[str, Any] = {}
        info: Dict[str, Any] = {}
        reward_breakdown = {
            "pop_reward": 0.0,
            "end_round_income": 0.0,
            "life_loss_penalty": 0.0,
            "invalid_action_penalty": 0.0,
            "step_penalty": 0.0,
        }

        if action is None:
            action = {"type": "noop"}

        action_type = action.get("type", "noop")
        original_action_type = action_type
        rules_cfg = self.config.get("rules", {}) if isinstance(self.config.get("rules"), dict) else {}
        auto_advance = bool(rules_cfg.get("auto_advance_round", False))
        mask_sell = bool(rules_cfg.get("mask_sell", False))
        require_tower = bool(rules_cfg.get("require_tower_before_start", False))
        require_choose = bool(rules_cfg.get("require_choose", False))
        max_prep_remaining = _coerce_int(rules_cfg.get("start_round_max_prep_remaining"))
        advance_round = False
        prep_budget_exhausted = auto_advance and self.state.prep_actions_remaining <= 0

        if action_type == "choose":
            index = _coerce_int(action.get("index"))
            flat_candidates = self._cached_action_candidates
            if not isinstance(flat_candidates, list) or not flat_candidates:
                invalid_action = True
                invalid_reason = "missing_action_candidates"
                action_type = "noop"
                action = {"type": "noop"}
            elif index is None or index < 0 or index >= len(flat_candidates):
                invalid_action = True
                invalid_reason = "invalid_index"
                action_type = "noop"
                action = {"type": "noop"}
            else:
                action = flat_candidates[index]
                action_type = action.get("type", "noop")

        if not invalid_action and require_choose and not internal and original_action_type != "choose":
            invalid_action = True
            invalid_reason = "choose_required"

        if not invalid_action:
            if self.state.phase != "build":
                invalid_action = True
                invalid_reason = "wrong_phase"
            elif prep_budget_exhausted and action_type in {"build", "upgrade", "sell"}:
                invalid_action = True
                invalid_reason = "prep_budget_exhausted"
            elif action_type == "sell" and mask_sell:
                invalid_action = True
                invalid_reason = "sell_masked"
            elif action_type == "build":
                ok, reason = self._apply_build(action)
                invalid_action = not ok
                invalid_reason = reason
            elif action_type == "upgrade":
                ok, reason = self._apply_upgrade(action)
                invalid_action = not ok
                invalid_reason = reason
            elif action_type == "sell":
                ok, reason = self._apply_sell(action)
                invalid_action = not ok
                invalid_reason = reason
            elif action_type == "start_round":
                if (
                    auto_advance
                    and max_prep_remaining is not None
                    and self.state.prep_actions_remaining > max_prep_remaining
                ):
                    invalid_action = True
                    invalid_reason = "start_round_not_allowed"
                else:
                    advance_round = True
                    if require_tower and not self.towers:
                        invalid_action = True
                        invalid_reason = "no_towers"
            elif action_type == "noop":
                pass
            else:
                invalid_action = True
                invalid_reason = "unknown_action"

        if auto_advance:
            if self.state.prep_actions_remaining > 0:
                self.state.prep_actions_remaining -= 1
            if advance_round:
                self.state.prep_actions_remaining = 0
            if advance_round or self.state.prep_actions_remaining <= 0:
                reward, round_info = self._simulate_round()
                reward_breakdown.update(round_info.get("reward_breakdown", {}))
                info.update(round_info)
                completed_round = True
        elif advance_round and not invalid_action:
            reward, round_info = self._simulate_round()
            reward_breakdown.update(round_info.get("reward_breakdown", {}))
            info.update(round_info)
            completed_round = True

        reward = reward_breakdown["pop_reward"] + reward_breakdown["end_round_income"] + reward_breakdown["life_loss_penalty"]

        step_penalty = float(self.config["rewards"].get("step_penalty", 0.0))
        reward -= step_penalty
        reward_breakdown["step_penalty"] = -step_penalty

        if invalid_action:
            penalty = float(self.config["rewards"]["invalid_action_penalty"])
            reward -= penalty
            reward_breakdown["invalid_action_penalty"] = -penalty
            info["invalid_action"] = True
            info["invalid_reason"] = invalid_reason
        else:
            info["invalid_action"] = False

        current_round = int(info.get("round", self.state.round))
        terminated = self.state.lives <= 0
        truncated = False
        max_steps = self.config.get("episode", {}).get("max_steps")
        if max_steps is not None and self.state.steps >= int(max_steps):
            truncated = True
        max_rounds = self.config["difficulty"].get("max_rounds")
        if completed_round and max_rounds is not None and current_round >= int(max_rounds):
            truncated = True

        done = terminated or truncated
        if terminated:
            info["termination"] = "loss"
        elif truncated:
            info["termination"] = "truncation"

        info["terminated"] = terminated
        info["truncated"] = truncated
        info["phase"] = self.state.phase
        info["step"] = self.state.steps
        info["reward_breakdown"] = reward_breakdown

        if completed_round:
            if not done:
                self.state.round = current_round + 1
                self._reset_prep_actions()
            self.state.last_round = dict(round_info)

        return self._observation(), reward, done, info

    def _apply_build(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        tower_type = action.get("tower_type")
        x = action.get("x")
        y = action.get("y")
        if tower_type not in self.tower_types:
            return False, "unknown_tower"
        if x is None or y is None:
            return False, "missing_position"
        if (x, y) not in self.build_slots:
            return False, "invalid_position"
        if any(tower.x == x and tower.y == y for tower in self.towers.values()):
            return False, "occupied"
        cost = self._build_cost(self.tower_types[tower_type])
        if self.state.cash < cost:
            return False, "insufficient_cash"
        self.state.cash -= cost
        tower = Tower(id=self.next_tower_id, type_name=tower_type, x=x, y=y)
        self.towers[self.next_tower_id] = tower
        self.next_tower_id += 1
        return True, ""

    def _apply_upgrade(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        tower_id = action.get("tower_id")
        path = action.get("path")
        if tower_id not in self.towers:
            return False, "unknown_tower"
        tower = self.towers[tower_id]
        tower_type = self.tower_types[tower.type_name]
        if path not in tower_type.upgrade_paths:
            return False, "unknown_path"
        current = self._get_upgrade_tier(tower, path)
        if current >= len(tower_type.upgrade_paths[path]):
            return False, "max_tier"
        if not self._can_upgrade(tower, path):
            return False, "crosspath_locked"
        cost = tower_type.upgrade_cost(path, current)
        if self.state.cash < cost:
            return False, "insufficient_cash"
        self.state.cash -= cost
        tower.upgrades[path] = current + 1
        return True, ""

    def _apply_sell(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        tower_id = action.get("tower_id")
        if tower_id not in self.towers:
            return False, "unknown_tower"
        tower = self.towers.pop(tower_id)
        self.state.cash += self._tower_refund(tower)
        return True, ""

    def _can_upgrade(self, tower: Tower, path: str) -> bool:
        upgrades = {key: self._get_upgrade_tier(tower, key) for key in tower.upgrades.keys()}
        upgrades[path] = upgrades.get(path, 0) + 1
        active_paths = [p for p, tier in upgrades.items() if tier > 0]
        if len(active_paths) > 2:
            return False
        main_paths = [p for p, tier in upgrades.items() if tier > 2]
        if len(main_paths) > 1:
            return False
        return True

    def _tower_total_cost(self, tower: Tower) -> int:
        total_cost = self.tower_types[tower.type_name].cost
        for path in tower.upgrades.keys():
            tier_value = self._get_upgrade_tier(tower, path)
            for i in range(tier_value):
                total_cost += self.tower_types[tower.type_name].upgrade_cost(path, i)
        return total_cost

    def _build_cost(self, tower_type: TowerType) -> int:
        base_cost = tower_type.cost
        rules_cfg = self.config.get("rules", {}) if isinstance(self.config.get("rules"), dict) else {}
        soft_cap = rules_cfg.get("soft_tower_cap")
        if not isinstance(soft_cap, dict):
            return base_cost
        per_type = soft_cap.get("per_type")
        if not isinstance(per_type, dict):
            return base_cost
        threshold = _coerce_int(per_type.get("threshold"))
        multiplier = float(per_type.get("multiplier", 0.0) or 0.0)
        if threshold is None or multiplier <= 0:
            return base_cost
        count = sum(1 for tower in self.towers.values() if tower.type_name == tower_type.name)
        extra = max(0, count - threshold + 1)
        if extra <= 0:
            return base_cost
        scaled = base_cost * (1.0 + multiplier * extra)
        return max(base_cost, int(round(scaled)))

    def _tower_refund(self, tower: Tower) -> int:
        refund_ratio = self.config["economy"]["sell_refund_ratio"]
        return int(self._tower_total_cost(tower) * refund_ratio)

    def _simulate_round(self) -> Tuple[float, Dict[str, Any]]:
        if self.state is None:
            raise RuntimeError("state unavailable")
        current_round = self.state.round
        wave = self._generate_wave(current_round)
        spawn_events = self._build_spawn_events(wave)
        bloons: List[Bloon] = []
        total_cash = 0
        total_pops = 0
        lives_lost = 0
        health_scale = 1.0 + (current_round - 1) * self.config["difficulty"]["health_scale_per_round"]
        speed_scale = 1.0 + (current_round - 1) * self.config["difficulty"]["speed_scale_per_round"]

        max_ticks = self.config["simulation"]["max_ticks_per_round"]
        tick = 0
        event_index = 0

        for tower in self.towers.values():
            tower.cooldown = 0

        while tick < max_ticks and (event_index < len(spawn_events) or bloons):
            while event_index < len(spawn_events) and spawn_events[event_index].tick <= tick:
                bloon_type = self.bloon_types[spawn_events[event_index].type_name]
                bloons.append(self._spawn_bloon(bloon_type, health_scale, speed_scale))
                event_index += 1

            pops, cash = self._tower_attacks(bloons, health_scale, speed_scale)
            total_pops += pops
            total_cash += cash

            bloons = [b for b in bloons if b.hp > 0]

            remaining_bloons: List[Bloon] = []
            for bloon in bloons:
                bloon.position += bloon.speed
                if bloon.position >= len(self.path) - 1:
                    lives_lost += 1
                else:
                    remaining_bloons.append(bloon)
            bloons = remaining_bloons

            tick += 1

        if tick >= max_ticks and (event_index < len(spawn_events) or bloons):
            lives_lost += len(bloons)

        end_income = self.config["economy"]["end_round_income"]
        self.state.cash += total_cash + end_income
        self.state.lives -= lives_lost

        pop_reward = total_cash * self.config["rewards"]["pop_reward_multiplier"]
        life_loss_penalty = -lives_lost * self.config["rewards"]["life_loss_penalty"]
        reward = pop_reward + end_income + life_loss_penalty
        info = {
            "round": current_round,
            "pops": total_pops,
            "cash_earned": total_cash,
            "end_round_income": end_income,
            "lives_lost": lives_lost,
            "reward_breakdown": {
                "pop_reward": pop_reward,
                "end_round_income": float(end_income),
                "life_loss_penalty": life_loss_penalty,
            },
        }
        return reward, info

    def _tower_attacks(self, bloons: List[Bloon], health_scale: float, speed_scale: float) -> Tuple[int, int]:
        popped = 0
        cash = 0
        if not bloons:
            return 0, 0
        for tower in self.towers.values():
            tower.cooldown = max(0, tower.cooldown - 1)
            if tower.cooldown > 0:
                continue
            tower_type = self.tower_types[tower.type_name]
            stats = tower_type.stats_with_upgrades(tower.upgrades)
            in_range = [
                bloon
                for bloon in bloons
                if bloon.hp > 0
                and self._distance((tower.x, tower.y), self._bloon_position(bloon.position)) <= stats["range"]
            ]
            if not in_range:
                continue
            targets = self._select_targets(in_range, tower.targeting, stats["pierce"], origin=(tower.x, tower.y))
            for target in targets:
                target.hp -= stats["damage"]
                if target.hp <= 0:
                    popped += 1
                    cash += target.reward
                    for child_name in target.children:
                        child_type = self.bloon_types[child_name]
                        child = self._spawn_bloon(child_type, health_scale, speed_scale)
                        child.position = target.position
                        bloons.append(child)
            tower.cooldown = max(1, int(round(1.0 / stats["fire_rate"])))
        return popped, cash

    def _select_targets(
        self,
        bloons: List[Bloon],
        targeting: str,
        pierce: int,
        origin: Tuple[float, float] | None = None,
    ) -> List[Bloon]:
        if targeting == "strong":
            sorted_bloons = sorted(bloons, key=lambda b: b.hp, reverse=True)
        elif targeting == "last":
            sorted_bloons = sorted(bloons, key=lambda b: b.position)
        elif targeting == "close":
            if origin is None:
                sorted_bloons = sorted(bloons, key=lambda b: b.position, reverse=True)
            else:
                sorted_bloons = sorted(
                    bloons,
                    key=lambda b: self._distance(origin, self._bloon_position(b.position)),
                )
        else:
            sorted_bloons = sorted(bloons, key=lambda b: b.position, reverse=True)
        return sorted_bloons[:pierce]

    def _spawn_bloon(self, bloon_type: BloonType, health_scale: float = 1.0, speed_scale: float = 1.0) -> Bloon:
        bloon_id = self.next_bloon_id
        self.next_bloon_id += 1
        return Bloon(
            id=bloon_id,
            type_name=bloon_type.name,
            hp=bloon_type.hp * health_scale,
            speed=bloon_type.speed * speed_scale,
            reward=bloon_type.reward,
            position=0.0,
            children=list(bloon_type.children),
        )

    def _generate_wave(self, round_number: int) -> List[str]:
        round_rng = random.Random(self.state.seed + round_number * 10007) if self.state else random.Random(round_number)
        max_tier = max(bt.tier for bt in self.bloon_types.values())
        allowed_tier = min(round_number // 5, max_tier)
        available = [bt for bt in self.bloon_types.values() if bt.tier <= allowed_tier and "moab" not in bt.traits]
        count = 8 + round_number * 2
        wave = [round_rng.choice(available).name for _ in range(count)]
        if round_number >= 20 and round_number % 10 == 0:
            wave.append("moab")
        return wave

    def _build_spawn_events(self, wave: List[str]) -> List[SpawnEvent]:
        interval = self.config["simulation"]["spawn_interval_ticks"]
        return [SpawnEvent(tick=i * interval, type_name=name) for i, name in enumerate(wave)]

    def _observation(self, *, cache_action_candidates: bool = True) -> Dict[str, Any]:
        if self.state is None:
            raise RuntimeError("state unavailable")
        obs_config = self.config.get("observation", {})
        max_build_slots = obs_config.get("max_build_slots")
        max_towers = obs_config.get("max_towers")
        max_path_points = obs_config.get("max_path_points")

        path_points = [list(point) for point in self.path]
        path_truncated = False
        if max_path_points is not None and len(path_points) > int(max_path_points):
            path_points = path_points[: int(max_path_points)]
            path_truncated = True

        build_slots = [list(slot) for slot in sorted(self.build_slots)]
        build_slots_truncated = False
        build_slots_omitted = 0
        if max_build_slots is not None and len(build_slots) > int(max_build_slots):
            build_slots_omitted = len(build_slots) - int(max_build_slots)
            build_slots = build_slots[: int(max_build_slots)]
            build_slots_truncated = True

        towers_sorted = sorted(self.towers.values(), key=lambda t: t.id)
        towers = [self._tower_summary(tower) for tower in towers_sorted]
        towers_truncated = False
        towers_omitted = 0
        if max_towers is not None and len(towers) > int(max_towers):
            towers_omitted = len(towers) - int(max_towers)
            towers = towers[: int(max_towers)]
            towers_truncated = True

        next_wave = self._summarize_wave(self._generate_wave(self.state.round))
        valid_actions, action_meta = self._valid_actions()
        action_candidates = self._action_candidates(valid_actions)
        if cache_action_candidates:
            self._cached_action_candidates = action_candidates

        return {
            "round": self.state.round,
            "phase": self.state.phase,
            "steps": self.state.steps,
            "lives": self.state.lives,
            "cash": self.state.cash,
            "seed": self.state.seed,
            "prep_actions_remaining": self.state.prep_actions_remaining,
            "prep_actions_max": self.state.prep_actions_max,
            "map": {
                "width": self.config["map"]["width"],
                "height": self.config["map"]["height"],
                "path": path_points,
                "build_slots": build_slots,
            },
            "towers": towers,
            "next_wave": next_wave,
            "last_round": dict(self.state.last_round) if self.state.last_round else {},
            "valid_actions": valid_actions,
            "action_candidates": action_candidates,
            "action_candidates_count": len(action_candidates),
            "action_counts": action_meta["counts"],
            "action_truncated": action_meta["truncated"],
            "obs_truncated": {
                "path": path_truncated,
                "build_slots": build_slots_truncated,
                "towers": towers_truncated,
                "valid_actions": action_meta["truncated"].get("any", False),
                "threats": next_wave.get("truncated", False),
            },
            "omitted_counts": {
                "build_slots": build_slots_omitted,
                "towers": towers_omitted,
                "valid_actions": action_meta["omitted"],
            },
        }

    def _tower_summary(self, tower: Tower) -> Dict[str, Any]:
        return {
            "id": tower.id,
            "type": tower.type_name,
            "x": tower.x,
            "y": tower.y,
            "upgrades": {
                key: self._get_upgrade_tier(tower, key) for key in sorted(tower.upgrades.keys())
            },
            "targeting": tower.targeting,
        }

    def _summarize_wave(self, wave: List[str]) -> Dict[str, Any]:
        summary: Dict[str, int] = {}
        for name in wave:
            summary[name] = summary.get(name, 0) + 1
        threats = []
        for name, count in summary.items():
            bloon_type = self.bloon_types[name]
            threats.append(
                {
                    "type": name,
                    "count": count,
                    "tier": bloon_type.tier,
                    "hp": bloon_type.hp,
                    "speed": bloon_type.speed,
                }
            )
        threats.sort(key=lambda t: (-t["tier"], -t["count"], t["type"]))
        max_threats = self.config.get("observation", {}).get("max_threats")
        truncated = False
        if max_threats is not None and len(threats) > int(max_threats):
            threats = threats[: int(max_threats)]
            truncated = True
        return {
            "counts": summary,
            "total": len(wave),
            "top_threats": threats,
            "truncated": truncated,
        }

    def _available_build_slots(self) -> List[Tuple[int, int]]:
        occupied = {(tower.x, tower.y) for tower in self.towers.values()}
        slots = [slot for slot in self.build_slots if slot not in occupied]
        return sorted(slots, key=lambda slot: (self._distance_sq_to_path(slot), slot[0], slot[1]))

    def _distance_sq_to_path(self, slot: Tuple[int, int]) -> float:
        x, y = slot
        return min((x - px) ** 2 + (y - py) ** 2 for px, py in self.path)

    def _action_candidates(self, valid_actions: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []
        for key in ("build", "upgrade", "sell"):
            actions.extend(valid_actions.get(key, []))
        if valid_actions.get("start_round"):
            actions.append({"type": "start_round"})
        if valid_actions.get("noop"):
            actions.append({"type": "noop"})
        return actions

    def _normalize_points(
        self,
        points: Any,
        name: str,
        min_points: int | None = None,
    ) -> List[Tuple[int, int]]:
        if not isinstance(points, (list, tuple)):
            raise ValueError(f"{name} must be a list of [x, y] pairs")
        if min_points is not None and len(points) < min_points:
            raise ValueError(f"{name} must contain at least {min_points} points")
        normalized: List[Tuple[int, int]] = []
        for idx, point in enumerate(points):
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError(f"{name}[{idx}] must be a pair of integers")
            x, y = point
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError(f"{name}[{idx}] must be integers")
            normalized.append((x, y))
        return normalized

    def _round_phase(self, round_number: int | None, cfg: Dict[str, Any]) -> str:
        if round_number is None:
            return "late"
        early_max = _coerce_int(cfg.get("early_max_round")) or 11
        mid_max = _coerce_int(cfg.get("mid_max_round")) or 13
        if round_number <= early_max:
            return "early"
        if round_number <= mid_max:
            return "mid"
        return "late"

    def _apply_candidate_balance(
        self,
        build_actions: List[Dict[str, Any]],
        upgrade_actions: List[Dict[str, Any]],
        sell_actions: List[Dict[str, Any]],
        truncated: Dict[str, Any],
        omitted: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        obs_cfg = self.config.get("observation", {}) if isinstance(self.config.get("observation"), dict) else {}
        balance_cfg = obs_cfg.get("candidate_balance")
        if not isinstance(balance_cfg, dict):
            return build_actions, upgrade_actions, sell_actions
        phase = self._round_phase(self.state.round if self.state else None, balance_cfg)
        phase_cfg = balance_cfg.get("by_phase", {}) if isinstance(balance_cfg.get("by_phase"), dict) else {}
        phase_entry = phase_cfg.get(phase, {}) if isinstance(phase_cfg.get(phase), dict) else {}

        min_build_frac = phase_entry.get("min_build_frac", balance_cfg.get("min_build_frac"))
        max_upgrade = phase_entry.get("max_upgrade_candidates", balance_cfg.get("max_upgrade_candidates"))

        if max_upgrade is not None:
            max_upgrade = max(0, int(max_upgrade))
            if len(upgrade_actions) > max_upgrade:
                omitted["upgrade"] += len(upgrade_actions) - max_upgrade
                upgrade_actions = upgrade_actions[:max_upgrade]
                truncated["upgrade"] = True

        if (
            min_build_frac is not None
            and build_actions
            and upgrade_actions
            and isinstance(min_build_frac, (int, float))
        ):
            frac = max(0.0, min(1.0, float(min_build_frac)))
            if frac > 0:
                max_upgrades = int((len(build_actions) * (1.0 - frac)) / frac)
                max_upgrades = max(0, max_upgrades)
                if len(upgrade_actions) > max_upgrades:
                    omitted["upgrade"] += len(upgrade_actions) - max_upgrades
                    upgrade_actions = upgrade_actions[:max_upgrades]
                    truncated["upgrade"] = True

        return build_actions, upgrade_actions, sell_actions

    def _valid_actions(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if self.state is None:
            return {
                "build": [],
                "upgrade": [],
                "sell": [],
                "start_round": False,
                "noop": True,
            }, {
                "counts": {"build": 0, "upgrade": 0, "sell": 0},
                "truncated": {"build": False, "upgrade": False, "sell": False, "any": False},
                "omitted": {"build": 0, "upgrade": 0, "sell": 0},
            }

        if self.state.phase != "build":
            return {
                "build": [],
                "upgrade": [],
                "sell": [],
                "start_round": False,
                "noop": True,
            }, {
                "counts": {"build": 0, "upgrade": 0, "sell": 0},
                "truncated": {"build": False, "upgrade": False, "sell": False, "any": False},
                "omitted": {"build": 0, "upgrade": 0, "sell": 0},
            }

        rules_cfg = self.config.get("rules", {}) if isinstance(self.config.get("rules"), dict) else {}
        auto_advance = bool(rules_cfg.get("auto_advance_round", False))
        mask_sell = bool(rules_cfg.get("mask_sell", False))
        if auto_advance and self.state.prep_actions_remaining <= 0:
            require_tower = bool(rules_cfg.get("require_tower_before_start", False))
            start_round_allowed = not require_tower or bool(self.towers)
            return {
                "build": [],
                "upgrade": [],
                "sell": [],
                "start_round": start_round_allowed,
                "noop": True,
            }, {
                "counts": {"build": 0, "upgrade": 0, "sell": 0},
                "truncated": {"build": False, "upgrade": False, "sell": False, "any": False},
                "omitted": {"build": 0, "upgrade": 0, "sell": 0},
            }

        cash = self.state.cash
        obs_cfg = self.config.get("observation", {})
        max_candidates = obs_cfg.get("max_action_candidates")
        max_build_slots = obs_cfg.get("max_build_slots")
        build_actions: List[Dict[str, Any]] = []
        available_slots = self._available_build_slots()
        if max_build_slots is not None and len(available_slots) > int(max_build_slots):
            available_slots = available_slots[: int(max_build_slots)]
        for tower_name in sorted(self.tower_types.keys()):
            tower_type = self.tower_types[tower_name]
            build_cost = self._build_cost(tower_type)
            if cash < build_cost:
                continue
            for x, y in available_slots:
                build_actions.append(
                    {
                        "type": "build",
                        "tower_type": tower_name,
                        "x": x,
                        "y": y,
                        "cost": build_cost,
                    }
                )

        upgrade_actions: List[Dict[str, Any]] = []
        for tower_id in sorted(self.towers.keys()):
            tower = self.towers[tower_id]
            tower_type = self.tower_types[tower.type_name]
            for path in sorted(tower_type.upgrade_paths.keys()):
                current = self._get_upgrade_tier(tower, path)
                if current >= len(tower_type.upgrade_paths[path]):
                    continue
                if not self._can_upgrade(tower, path):
                    continue
                cost = tower_type.upgrade_cost(path, current)
                if cash < cost:
                    continue
                upgrade_actions.append(
                    {
                        "type": "upgrade",
                        "tower_id": tower_id,
                        "path": path,
                        "cost": cost,
                    }
                )

        sell_actions = []
        if not mask_sell:
            sell_actions = [
                {
                    "type": "sell",
                    "tower_id": tower_id,
                    "refund": self._tower_refund(self.towers[tower_id]),
                }
                for tower_id in sorted(self.towers.keys())
            ]

        truncated = {"build": False, "upgrade": False, "sell": False, "any": False}
        omitted = {"build": 0, "upgrade": 0, "sell": 0}

        if max_candidates is not None:
            max_candidates = max(0, int(max_candidates))
            if len(build_actions) > max_candidates:
                omitted["build"] = len(build_actions) - max_candidates
                build_actions = build_actions[:max_candidates]
                truncated["build"] = True
            if len(upgrade_actions) > max_candidates:
                omitted["upgrade"] = len(upgrade_actions) - max_candidates
                upgrade_actions = upgrade_actions[:max_candidates]
                truncated["upgrade"] = True
            if len(sell_actions) > max_candidates:
                omitted["sell"] = len(sell_actions) - max_candidates
                sell_actions = sell_actions[:max_candidates]
                truncated["sell"] = True
            truncated["any"] = truncated["build"] or truncated["upgrade"] or truncated["sell"]

        build_actions, upgrade_actions, sell_actions = self._apply_candidate_balance(
            build_actions, upgrade_actions, sell_actions, truncated, omitted
        )
        truncated["any"] = truncated["build"] or truncated["upgrade"] or truncated["sell"]

        counts = {
            "build": len(build_actions),
            "upgrade": len(upgrade_actions),
            "sell": len(sell_actions),
        }

        require_tower = bool(rules_cfg.get("require_tower_before_start", False))
        start_round_allowed = not require_tower or bool(self.towers)
        if auto_advance:
            max_prep_remaining = _coerce_int(rules_cfg.get("start_round_max_prep_remaining"))
            if (
                max_prep_remaining is not None
                and self.state.prep_actions_remaining > max_prep_remaining
            ):
                start_round_allowed = False
        return {
            "build": build_actions,
            "upgrade": upgrade_actions,
            "sell": sell_actions,
            "start_round": start_round_allowed,
            "noop": True,
        }, {"counts": counts, "truncated": truncated, "omitted": omitted}

    def _init_path(self) -> List[Tuple[int, int]]:
        config_path = self.config["map"].get("path")
        if config_path is not None:
            return self._normalize_points(config_path, "map.path", min_points=2)
        width = self.config["map"]["width"]
        height = self.config["map"]["height"]
        turn_chance = float(self.config["map"].get("path_turn_chance", 0.25))
        turn_chance = max(0.0, min(1.0, turn_chance))
        start_y = self.rng.randint(1, height - 2)
        path = [(0, start_y)]
        x = 0
        y = start_y
        while x < width - 1:
            if self.rng.random() < turn_chance:
                y += self.rng.choice([-1, 1])
                y = max(1, min(height - 2, y))
            x += 1
            path.append((x, y))
        return path

    def _init_build_slots(self) -> List[Tuple[int, int]]:
        config_slots = self.config["map"].get("build_slots")
        if config_slots is not None:
            return self._normalize_points(config_slots, "map.build_slots")
        width = self.config["map"]["width"]
        height = self.config["map"]["height"]
        path_set = set(self.path)
        return [
            (x, y)
            for y in range(height)
            for x in range(width)
            if (x, y) not in path_set
        ]

    def _load_tower_types(self) -> Dict[str, TowerType]:
        tower_types: Dict[str, TowerType] = {}
        for name, data in self.config["towers"].items():
            upgrade_paths: Dict[str, List[UpgradeTier]] = {}
            for path, tiers in data.get("upgrade_paths", {}).items():
                upgrade_paths[path] = [UpgradeTier(**tier) for tier in tiers]
            tower_types[name] = TowerType(
                name=name,
                cost=data["cost"],
                range=data["range"],
                damage=data["damage"],
                pierce=data["pierce"],
                fire_rate=data["fire_rate"],
                upgrade_paths=upgrade_paths,
            )
        return tower_types

    def _load_bloon_types(self) -> Dict[str, BloonType]:
        bloon_types: Dict[str, BloonType] = {}
        for name, data in self.config["bloons"].items():
            bloon_types[name] = BloonType(
                name=name,
                hp=data["hp"],
                speed=data["speed"],
                reward=data["reward"],
                tier=data["tier"],
                children=list(data.get("children", [])),
                traits=list(data.get("traits", [])),
            )
        return bloon_types

    def _bloon_position(self, progress: float) -> Tuple[float, float]:
        if progress <= 0:
            return self.path[0]
        idx = int(progress)
        if idx >= len(self.path) - 1:
            return self.path[-1]
        frac = progress - idx
        x0, y0 = self.path[idx]
        x1, y1 = self.path[idx + 1]
        return (x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac)

    @staticmethod
    def _distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


ACTION_TYPES = {"build", "upgrade", "sell", "start_round", "noop", "choose"}
FORMAT_INVALID_REWARD = -5.0
MAX_ACTION_CHARS = 256

SYSTEM_PROMPT = (
    "You are playing a tower-defense game. Respond with ONLY a single JSON action "
    "object and no extra text. Examples: "
    "{\"type\": \"build\", \"tower_type\": \"dart\", \"x\": 0, \"y\": 0} "
    "{\"type\": \"upgrade\", \"tower_id\": 1, \"path\": \"a\"} "
    "{\"type\": \"sell\", \"tower_id\": 1} "
    "{\"type\": \"start_round\"} "
    "{\"type\": \"noop\"} "
    "{\"type\": \"choose\", \"index\": 0}"
)

CHOOSE_SYSTEM_PROMPT = (
    "You are playing a tower-defense game. Respond with ONLY a single JSON action "
    "object using choose-index and no extra text. Example: "
    "{\"type\": \"choose\", \"index\": 0}"
)

MACRO_SYSTEM_PROMPT = (
    "You are playing a tower-defense game. Respond with ONLY a single JSON plan "
    "object and no extra text. The plan contains 0-2 prep actions, each selecting "
    "a candidate by index (valid indices: 0..action_candidates_count-1). Example: "
    "{\"type\": \"plan\", \"actions\": [{\"type\": \"choose\", \"index\": 0}, "
    "{\"type\": \"choose\", \"index\": 1}]}"
)


def _filter_macro_round_candidates(obs: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(obs, dict):
        return []
    raw_candidates = obs.get("action_candidates")
    if not isinstance(raw_candidates, list):
        raw_candidates = []
    filtered = [
        cand
        for cand in raw_candidates
        if not (isinstance(cand, dict) and cand.get("type") == "start_round")
    ]
    obs["action_candidates"] = filtered
    obs["action_candidates_count"] = len(filtered)
    valid_actions = obs.get("valid_actions")
    if isinstance(valid_actions, dict):
        valid_actions["start_round"] = False
    return filtered


def _completion_to_text(completion: vf.Messages) -> str:
    if isinstance(completion, list) and completion:
        return str(completion[-1].get("content", ""))
    return str(completion or "")


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
    return stripped.strip()


def _extract_json_object(text: str) -> Tuple[Dict[str, Any] | None, bool]:
    """Return (action, strict_match) where strict_match means no extra text."""
    raw = _strip_code_fences(text)
    if not raw:
        return None, False
    if len(raw) > MAX_ACTION_CHARS:
        return None, False
    try:
        parsed = json.loads(raw)
        return parsed, True
    except Exception:
        pass
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return None, False
    candidate = match.group(0)
    if len(candidate) > MAX_ACTION_CHARS:
        return None, False
    try:
        parsed = json.loads(candidate)
        strict = candidate.strip() == raw.strip()
        return parsed, strict
    except Exception:
        return None, False


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _normalize_action(action: Dict[str, Any]) -> Dict[str, Any] | None:
    if not isinstance(action, dict):
        return None
    action_type = action.get("type")
    if action_type not in ACTION_TYPES:
        return None
    if action_type == "build":
        x = _coerce_int(action.get("x"))
        y = _coerce_int(action.get("y"))
        tower_type = action.get("tower_type")
        if x is None or y is None or not isinstance(tower_type, str):
            return None
        return {"type": "build", "tower_type": tower_type, "x": x, "y": y}
    if action_type == "upgrade":
        tower_id = _coerce_int(action.get("tower_id"))
        path = action.get("path")
        if tower_id is None or path not in {"a", "b", "c"}:
            return None
        return {"type": "upgrade", "tower_id": tower_id, "path": path}
    if action_type == "sell":
        tower_id = _coerce_int(action.get("tower_id"))
        if tower_id is None:
            return None
        return {"type": "sell", "tower_id": tower_id}
    if action_type == "choose":
        index = _coerce_int(action.get("index"))
        if index is None:
            return None
        return {"type": "choose", "index": index}
    if action_type == "start_round":
        return {"type": "start_round"}
    return {"type": "noop"}


def _parse_action_text(text: str) -> Tuple[Dict[str, Any] | None, bool]:
    action, strict = _extract_json_object(text)
    if action is None:
        return None, False
    normalized = _normalize_action(action)
    if normalized is None:
        return None, False
    return normalized, strict


def _parse_plan_text(text: str) -> Tuple[List[Dict[str, Any]] | None, bool]:
    action, strict = _extract_json_object(text)
    if action is None or not isinstance(action, dict):
        return None, False
    if action.get("type") != "plan":
        return None, False
    actions = action.get("actions", [])
    if actions is None:
        actions = []
    if not isinstance(actions, list):
        return None, False
    normalized_actions: List[Dict[str, Any]] = []
    for item in actions:
        normalized = _normalize_action(item)
        if normalized is None:
            return None, False
        if normalized.get("type") != "choose":
            return None, False
        normalized_actions.append(normalized)
    return normalized_actions, strict


def _select_baseline_action(obs: Dict[str, Any]) -> Dict[str, Any]:
    valid_actions = obs.get("valid_actions", {}) if isinstance(obs.get("valid_actions"), dict) else {}
    if valid_actions.get("start_round"):
        return {"type": "start_round"}
    if valid_actions.get("noop"):
        return {"type": "noop"}
    candidates = obs.get("action_candidates")
    if isinstance(candidates, list):
        for cand in candidates:
            if isinstance(cand, dict):
                return cand
    return {"type": "noop"}


def _compute_singleturn_reward(
    obs: Dict[str, Any],
    action: Dict[str, Any],
    config: Dict[str, Any],
) -> Tuple[float, Dict[str, Any]]:
    simulator = TowerDefenseEnv(config)
    simulator.load_from_observation(obs)
    _obs, reward, done, info = simulator.step(action, internal=True)

    merged_cfg = simulator.config
    rules_cfg = merged_cfg.get("rules", {}) if isinstance(merged_cfg.get("rules"), dict) else {}
    auto_advance = bool(rules_cfg.get("auto_advance_round", False))
    if auto_advance and "pops" not in info and not info.get("invalid_action"):
        round_reward, _round_info = simulator._simulate_round()
        reward = float(round_reward)
        step_penalty = float(merged_cfg.get("rewards", {}).get("step_penalty", 0.0))
        reward -= step_penalty

    shaping_cfg = merged_cfg.get("reward_shaping", {}) if isinstance(merged_cfg.get("reward_shaping"), dict) else {}
    if (
        action.get("type") != "start_round"
        and shaping_cfg.get("enable_lookahead")
        and not auto_advance
    ):
        lookahead_rounds = max(0, int(shaping_cfg.get("lookahead_rounds", 1)))
        lookahead_weight = float(shaping_cfg.get("lookahead_weight", 0.5))
        if lookahead_rounds > 0 and lookahead_weight > 0:
            baseline = TowerDefenseEnv(config)
            baseline.load_from_observation(obs)

            def _simulate_rounds(env: TowerDefenseEnv, count: int) -> float:
                total = 0.0
                for _ in range(count):
                    _o, r, done_inner, _i = env.step({"type": "start_round"}, internal=True)
                    total += float(r)
                    if done_inner:
                        break
                return total

            baseline_future = _simulate_rounds(baseline, lookahead_rounds)
            after_future = 0.0 if done else _simulate_rounds(simulator, lookahead_rounds)
            reward += lookahead_weight * (after_future - baseline_future)

    return float(reward), info


def _candidate_rewards(
    obs: Dict[str, Any],
    config: Dict[str, Any],
) -> List[Tuple[Dict[str, Any], float]]:
    candidates = obs.get("action_candidates")
    rewards: List[Tuple[Dict[str, Any], float]] = []
    if not isinstance(candidates, list):
        return rewards
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        reward, _info = _compute_singleturn_reward(obs, cand, config)
        rewards.append((cand, reward))
    return rewards


_ACTIVE_CONFIG: Dict[str, Any] = DEFAULT_CONFIG


def _sample_action(
    obs: Dict[str, Any],
    rng: random.Random,
    policy: str,
    dataset_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    valid_actions = obs.get("valid_actions", {})
    actions: List[Dict[str, Any]] = []
    for key in ("build", "upgrade", "sell"):
        actions.extend(valid_actions.get(key, []))
    if valid_actions.get("start_round"):
        actions.append({"type": "start_round"})
    if valid_actions.get("noop"):
        actions.append({"type": "noop"})

    if policy == "noop" or not actions:
        return {"type": "noop"}
    if policy == "advance":
        return {"type": "start_round"}
    if policy == "bootstrap":
        towers = obs.get("towers", [])
        build_actions = valid_actions.get("build", [])
        if not towers and build_actions:
            return build_actions[0]
        if valid_actions.get("start_round"):
            return {"type": "start_round"}
        if build_actions:
            return build_actions[0]
        return {"type": "noop"}
    if policy == "noop_then_start":
        towers = obs.get("towers", [])
        build_actions = valid_actions.get("build", [])
        upgrade_actions = valid_actions.get("upgrade", [])
        sell_actions = valid_actions.get("sell", [])
        prep_remaining = _coerce_int(obs.get("prep_actions_remaining"))
        if not towers and build_actions:
            return build_actions[0]
        if (
            prep_remaining is not None
            and prep_remaining > 1
            and valid_actions.get("noop")
        ):
            return {"type": "noop"}
        if valid_actions.get("start_round"):
            return {"type": "start_round"}
        if build_actions:
            return build_actions[0]
        if upgrade_actions:
            return upgrade_actions[0]
        if sell_actions:
            return sell_actions[0]
        return {"type": "noop"}
    if policy == "safe_explore":
        build_actions = valid_actions.get("build", [])
        upgrade_actions = valid_actions.get("upgrade", [])
        prep_remaining = _coerce_int(obs.get("prep_actions_remaining"))
        round_number = _coerce_int(obs.get("round"))
        towers = obs.get("towers", [])
        build_until_round = _coerce_int(dataset_cfg.get("safe_explore_build_until_round"))
        build_until_towers = _coerce_int(dataset_cfg.get("safe_explore_build_until_towers"))
        upgrade_prob = float(dataset_cfg.get("safe_explore_upgrade_prob", 0.5) or 0.0)
        upgrade_prob = min(1.0, max(0.0, upgrade_prob))
        if build_actions:
            if build_until_round is not None and round_number is not None and round_number <= build_until_round:
                return build_actions[int(rng.random() * len(build_actions))]
            if build_until_towers is not None and isinstance(towers, list) and len(towers) < build_until_towers:
                return build_actions[int(rng.random() * len(build_actions))]
        if upgrade_actions and rng.random() < upgrade_prob:
            return upgrade_actions[int(rng.random() * len(upgrade_actions))]
        if build_actions:
            return build_actions[int(rng.random() * len(build_actions))]
        if (
            prep_remaining is not None
            and prep_remaining > 1
            and valid_actions.get("noop")
        ):
            return {"type": "noop"}
        if valid_actions.get("start_round"):
            return {"type": "start_round"}
        if upgrade_actions:
            return upgrade_actions[int(rng.random() * len(upgrade_actions))]
        return {"type": "noop"}
    return actions[int(rng.random() * len(actions))]


def _build_dataset(
    config: Dict[str, Any],
    num_examples: int,
    seed_start: int,
) -> Dataset:
    prompts: List[List[Dict[str, str]]] = []
    infos: List[Dict[str, Any]] = []
    simulator = TowerDefenseEnv(config)
    dataset_cfg = config.get("dataset", {}) if isinstance(config.get("dataset"), dict) else {}
    rollout_steps = int(dataset_cfg.get("rollout_steps", 0))
    policy = str(dataset_cfg.get("policy", "random"))
    wrapper_mode = str(config.get("wrapper", "") or "").lower()
    rules_cfg = config.get("rules", {}) if isinstance(config.get("rules"), dict) else {}
    require_choose = bool(rules_cfg.get("require_choose", False))
    if wrapper_mode == "macro_round":
        system_prompt = MACRO_SYSTEM_PROMPT
    elif require_choose:
        system_prompt = CHOOSE_SYSTEM_PROMPT
    else:
        system_prompt = SYSTEM_PROMPT
    num_seeds = _coerce_int(dataset_cfg.get("num_seeds"))
    if num_seeds is None:
        num_seeds = num_examples

    snapshots_cfg = dataset_cfg.get("snapshots", {}) if isinstance(dataset_cfg.get("snapshots"), dict) else {}
    snapshot_mode = str(snapshots_cfg.get("mode", "")).lower()
    snapshot_rounds: List[int] = []
    if isinstance(snapshots_cfg.get("rounds"), list):
        for value in snapshots_cfg.get("rounds", []):
            coerced = _coerce_int(value)
            if coerced is not None:
                snapshot_rounds.append(coerced)
    snapshot_rounds_set = set(snapshot_rounds)
    snapshot_prep_remaining = _coerce_int(snapshots_cfg.get("prep_remaining"))
    snapshots_per_seed = _coerce_int(dataset_cfg.get("snapshots_per_seed")) or 0

    diagnostics_cfg = dataset_cfg.get("diagnostics", {}) if isinstance(dataset_cfg.get("diagnostics"), dict) else {}
    dominance_enabled = bool(diagnostics_cfg.get("dominance", False))
    dominance_counts: Dict[str, int] = {}
    dominance_total = 0
    dominance_margin_sum = 0.0
    dominance_build_upgrade = {"total": 0, "build": 0, "upgrade": 0, "other": 0}

    margin_min = float(dataset_cfg.get("margin_min", 0.0) or 0.0)
    require_best_types_raw = dataset_cfg.get("require_best_types")
    require_best_types: List[str] = []
    if isinstance(require_best_types_raw, str):
        require_best_types = [require_best_types_raw]
    elif isinstance(require_best_types_raw, list):
        require_best_types = [str(value) for value in require_best_types_raw]
    filter_enabled = margin_min > 0 or bool(require_best_types)
    filter_counts = {"kept": 0, "filtered": 0, "no_candidates": 0}
    filter_margin_sum = 0.0

    def _evaluate_obs(obs: Dict[str, Any]) -> Dict[str, Any] | None:
        scored = _candidate_rewards(obs, config)
        if not scored:
            return None
        scored.sort(key=lambda item: item[1], reverse=True)
        best_action, best_reward = scored[0]
        runner_up = scored[1][1] if len(scored) > 1 else best_reward
        types_present = {str(cand.get("type", "unknown")) for cand, _reward in scored if isinstance(cand, dict)}
        baseline_reward = None
        margin_vs_baseline = None
        if filter_enabled:
            baseline_action = _select_baseline_action(obs)
            baseline_reward, _baseline_info = _compute_singleturn_reward(obs, baseline_action, config)
            margin_vs_baseline = best_reward - baseline_reward
        return {
            "best_action": best_action,
            "best_reward": best_reward,
            "runner_up": runner_up,
            "margin": best_reward - runner_up,
            "types_present": types_present,
            "baseline_reward": baseline_reward,
            "margin_vs_baseline": margin_vs_baseline,
        }

    def _record_prompt(obs: Dict[str, Any], seed: int, meta: Dict[str, Any]) -> None:
        nonlocal filter_margin_sum
        obs_for_prompt = obs
        if wrapper_mode == "macro_round":
            obs_for_prompt = copy.deepcopy(obs)
            _filter_macro_round_candidates(obs_for_prompt)
        eval_summary = _evaluate_obs(obs_for_prompt) if (filter_enabled or dominance_enabled) else None
        if filter_enabled:
            if eval_summary is None:
                filter_counts["filtered"] += 1
                filter_counts["no_candidates"] += 1
                return
            best_type = str(eval_summary["best_action"].get("type", "unknown"))
            margin_vs_baseline = float(eval_summary.get("margin_vs_baseline", 0.0) or 0.0)
            if margin_vs_baseline < margin_min:
                filter_counts["filtered"] += 1
                return
            if require_best_types and best_type not in require_best_types:
                filter_counts["filtered"] += 1
                return
            filter_counts["kept"] += 1
            filter_margin_sum += margin_vs_baseline
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Observation: {json.dumps(obs_for_prompt, sort_keys=True)}"},
        ]
        prompts.append(prompt)
        info = {"seed": seed, "obs": obs_for_prompt}
        if meta:
            info["snapshot"] = meta
        if filter_enabled and eval_summary is not None:
            info["decision_filter"] = {
                "best_type": str(eval_summary["best_action"].get("type", "unknown")),
                "best_reward": float(eval_summary["best_reward"]),
                "baseline_reward": float(eval_summary.get("baseline_reward") or 0.0),
                "margin_vs_baseline": float(eval_summary.get("margin_vs_baseline") or 0.0),
                "require_best_types": require_best_types,
                "margin_min": margin_min,
            }
        infos.append(info)

        nonlocal dominance_total, dominance_margin_sum
        if dominance_enabled:
            dominance = eval_summary
            if dominance:
                dominance_total += 1
                dominance_margin_sum += float(dominance["margin"])
                best_type = str(dominance["best_action"].get("type", "unknown"))
                dominance_counts[best_type] = dominance_counts.get(best_type, 0) + 1
                types_present = dominance["types_present"]
                if "build" in types_present and "upgrade" in types_present:
                    dominance_build_upgrade["total"] += 1
                    if best_type in {"build", "upgrade"}:
                        dominance_build_upgrade[best_type] += 1
                    else:
                        dominance_build_upgrade["other"] += 1

    for i in range(num_seeds):
        seed = seed_start + i
        obs = simulator.reset(seed=seed)
        rng = random.Random(seed + 101)
        captured_rounds: set[int] = set()
        snapshots_collected = 0
        obs_history: List[Dict[str, Any]] = []

        def _maybe_capture(current_obs: Dict[str, Any]) -> None:
            nonlocal snapshots_collected
            if snapshot_mode != "rounds":
                return
            round_value = _coerce_int(current_obs.get("round"))
            if round_value is None or (snapshot_rounds_set and round_value not in snapshot_rounds_set):
                return
            if snapshot_prep_remaining is not None:
                current_prep = _coerce_int(current_obs.get("prep_actions_remaining"))
                if current_prep != snapshot_prep_remaining:
                    return
            if round_value in captured_rounds:
                return
            if snapshots_per_seed and snapshots_collected >= snapshots_per_seed:
                return
            captured_rounds.add(round_value)
            snapshots_collected += 1
            _record_prompt(current_obs, seed, {"mode": "rounds", "round": round_value})

        _maybe_capture(obs)
        if snapshots_per_seed > 0 and snapshot_mode != "rounds":
            obs_history.append({"obs": obs, "step": 0, "round": _coerce_int(obs.get("round"))})

        for step_index in range(max(0, rollout_steps)):
            action = _sample_action(obs, rng, policy, dataset_cfg)
            obs, _reward, done, _info = simulator.step(action, internal=True)
            if snapshots_per_seed > 0 and snapshot_mode != "rounds":
                obs_history.append(
                    {"obs": obs, "step": step_index + 1, "round": _coerce_int(obs.get("round"))}
                )
            _maybe_capture(obs)
            if done:
                break
            if snapshot_mode == "rounds" and snapshot_rounds_set and snapshot_rounds_set.issubset(captured_rounds):
                if not snapshots_per_seed or snapshots_collected >= snapshots_per_seed:
                    break

        if snapshot_mode == "rounds":
            if snapshots_collected == 0:
                _record_prompt(obs, seed, {"mode": "fallback", "reason": "no_snapshots"})
        elif snapshots_per_seed > 0:
            if obs_history:
                count = min(snapshots_per_seed, len(obs_history))
                indices = rng.sample(range(len(obs_history)), count) if len(obs_history) >= count else list(range(len(obs_history)))
                for idx in indices:
                    entry = obs_history[idx]
                    _record_prompt(
                        entry["obs"],
                        seed,
                        {"mode": "sampled", "step": entry.get("step"), "round": entry.get("round")},
                    )
            else:
                _record_prompt(obs, seed, {"mode": "fallback", "reason": "empty_history"})
        else:
            _record_prompt(obs, seed, {})

    if dominance_enabled and dominance_total > 0:
        avg_margin = dominance_margin_sum / dominance_total
        print("Dominance diagnostic:")
        print(f"  samples: {dominance_total}")
        print(f"  best_by_type: {dominance_counts}")
        if dominance_build_upgrade["total"] > 0:
            print(f"  build_vs_upgrade: {dominance_build_upgrade}")
        print(f"  avg_margin: {avg_margin:.4f}")
    if filter_enabled:
        total = filter_counts["kept"] + filter_counts["filtered"]
        avg_filter_margin = (filter_margin_sum / filter_counts["kept"]) if filter_counts["kept"] else 0.0
        print("Decision filter:")
        print(f"  total: {total}")
        print(f"  kept: {filter_counts['kept']}")
        print(f"  filtered: {filter_counts['filtered']}")
        if filter_counts["no_candidates"]:
            print(f"  no_candidates: {filter_counts['no_candidates']}")
        if filter_counts["kept"]:
            print(f"  avg_margin_vs_baseline: {avg_filter_margin:.4f}")

    return Dataset.from_dict({"prompt": prompts, "info": infos, "task": ["train"] * len(prompts)})


def _reward_from_action(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    info = info or {}
    content = _completion_to_text(completion)
    action, _strict = _parse_action_text(content)
    if action is None:
        return FORMAT_INVALID_REWARD
    simulator = TowerDefenseEnv(_ACTIVE_CONFIG)
    obs = info.get("obs")
    if isinstance(obs, dict):
        simulator.load_from_observation(obs)
    else:
        seed = int(info.get("seed", 0))
        simulator.reset(seed=seed)
    resolved_action_type = action.get("type")
    if resolved_action_type == "choose" and isinstance(obs, dict):
        index = _coerce_int(action.get("index"))
        candidates = obs.get("action_candidates")
        if (
            index is not None
            and isinstance(candidates, list)
            and 0 <= index < len(candidates)
        ):
            candidate = candidates[index]
            if isinstance(candidate, dict):
                resolved_action_type = candidate.get("type", resolved_action_type)
    _obs, reward, _done, _info = simulator.step(action)
    shaping_cfg = _ACTIVE_CONFIG.get("reward_shaping", {}) if isinstance(_ACTIVE_CONFIG.get("reward_shaping"), dict) else {}
    merged_cfg = simulator.config
    rules_cfg = merged_cfg.get("rules", {}) if isinstance(merged_cfg.get("rules"), dict) else {}
    auto_advance = bool(rules_cfg.get("auto_advance_round", False))
    if auto_advance and "pops" not in _info and not _info.get("invalid_action"):
        round_reward, _round_info = simulator._simulate_round()
        reward = float(round_reward)
        step_penalty = float(merged_cfg.get("rewards", {}).get("step_penalty", 0.0))
        reward -= step_penalty
    if (
        resolved_action_type != "start_round"
        and shaping_cfg.get("enable_lookahead")
        and isinstance(obs, dict)
        and not auto_advance
    ):
        lookahead_rounds = max(0, int(shaping_cfg.get("lookahead_rounds", 1)))
        lookahead_weight = float(shaping_cfg.get("lookahead_weight", 0.5))
        if lookahead_rounds > 0 and lookahead_weight > 0:
            baseline = TowerDefenseEnv(_ACTIVE_CONFIG)
            baseline.load_from_observation(obs)

            def _simulate_rounds(env: TowerDefenseEnv, count: int) -> float:
                total = 0.0
                for _ in range(count):
                    _o, r, done, _i = env.step({"type": "start_round"}, internal=True)
                    total += float(r)
                    if done:
                        break
                return total

            baseline_future = _simulate_rounds(baseline, lookahead_rounds)
            after_future = 0.0 if _done else _simulate_rounds(simulator, lookahead_rounds)
            reward += lookahead_weight * (after_future - baseline_future)
    if shaping_cfg.get("delta_reward") and isinstance(obs, dict):
        baseline_action = _select_baseline_action(obs)
        baseline_reward, _baseline_info = _compute_singleturn_reward(obs, baseline_action, _ACTIVE_CONFIG)
        reward -= baseline_reward
    return float(reward)


def _format_reward(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    content = _completion_to_text(completion)
    _action, strict = _parse_action_text(content)
    if _action is None:
        return -1.0
    return 1.0 if strict else 0.0


def _regret_metric(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    shaping_cfg = _ACTIVE_CONFIG.get("reward_shaping", {}) if isinstance(_ACTIVE_CONFIG.get("reward_shaping"), dict) else {}
    if not shaping_cfg.get("regret_metric"):
        return 0.0
    info = info or {}
    obs = info.get("obs")
    if not isinstance(obs, dict):
        return 0.0
    content = _completion_to_text(completion)
    action, _strict = _parse_action_text(content)
    if action is None:
        return 0.0

    resolved_action = action
    if action.get("type") == "choose":
        index = _coerce_int(action.get("index"))
        candidates = obs.get("action_candidates")
        if (
            index is not None
            and isinstance(candidates, list)
            and 0 <= index < len(candidates)
            and isinstance(candidates[index], dict)
        ):
            resolved_action = candidates[index]

    chosen_reward, _info = _compute_singleturn_reward(obs, resolved_action, _ACTIVE_CONFIG)
    candidate_rewards = _candidate_rewards(obs, _ACTIVE_CONFIG)
    if not candidate_rewards:
        return 0.0
    best_reward = max(reward for _cand, reward in candidate_rewards)
    return float(max(0.0, best_reward - chosen_reward))


def _macro_round_env_reward(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    rewards = state.get("turn_rewards", [])
    if not rewards:
        return 0.0
    return float(sum(float(r) for r in rewards))


def _macro_round_format_reward(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    formats = state.get("format_rewards", [])
    if not formats:
        return -1.0
    return float(sum(float(r) for r in formats)) / float(len(formats))


class TowerDefenseVerifiersEnv(vf.SingleTurnEnv):
    """Verifiers-compatible wrapper for hosted training."""

    def __init__(
        self,
        config: Dict[str, Any],
        num_examples: int = 64,
        seed_start: int = 0,
        **kwargs: Any,
    ):
        self.env_id: str | None = None
        self.env_args: Dict[str, Any] | None = None
        global _ACTIVE_CONFIG
        _ACTIVE_CONFIG = config
        dataset = _build_dataset(config, num_examples, seed_start)
        weight_cfg = config.get("reward_weights", {}) if isinstance(config.get("reward_weights"), dict) else {}
        format_weight = float(weight_cfg.get("format", 0.5))
        env_weight = float(weight_cfg.get("env", 1.0))
        rubric = vf.Rubric(
            funcs=[_format_reward, _reward_from_action, _regret_metric],
            weights=[format_weight, env_weight, 0.0],
        )
        super().__init__(dataset=dataset, rubric=rubric, **kwargs)


class TowerDefenseMacroRoundEnv(vf.MultiTurnEnv):
    """Multi-turn macro-round wrapper: one model plan per round."""

    def __init__(
        self,
        config: Dict[str, Any],
        num_examples: int = 64,
        seed_start: int = 0,
        **kwargs: Any,
    ):
        self.config = config
        self.env_id: str | None = None
        self.env_args: Dict[str, Any] | None = None
        global _ACTIVE_CONFIG
        _ACTIVE_CONFIG = config
        dataset = _build_dataset(config, num_examples, seed_start)
        weight_cfg = config.get("reward_weights", {}) if isinstance(config.get("reward_weights"), dict) else {}
        format_weight = float(weight_cfg.get("format", 0.5))
        env_weight = float(weight_cfg.get("env", 1.0))
        rubric = vf.Rubric(funcs=[_macro_round_format_reward, _macro_round_env_reward], weights=[format_weight, env_weight])
        difficulty_cfg = config.get("difficulty", {}) if isinstance(config.get("difficulty"), dict) else {}
        max_rounds = _coerce_int(difficulty_cfg.get("max_rounds"))
        if max_rounds is not None:
            kwargs["max_turns"] = max_rounds + 1
        kwargs.setdefault("interleaved_rollouts", False)
        super().__init__(dataset=dataset, rubric=rubric, **kwargs)
        if hasattr(self, "set_interleaved_rollouts"):
            self.set_interleaved_rollouts(False)

    async def setup_state(self, state: vf.State) -> vf.State:
        info_raw = state.get("info")
        if isinstance(info_raw, dict):
            info = info_raw
        elif isinstance(info_raw, str):
            try:
                info = json.loads(info_raw)
            except Exception:
                info = {}
        else:
            info = {}
        simulator = TowerDefenseEnv(self.config)
        obs = info.get("obs")
        if isinstance(obs, dict):
            simulator.load_from_observation(obs)
        else:
            seed = _coerce_int(info.get("seed"))
            simulator.reset(seed=seed if seed is not None else None)
        state["simulator"] = simulator
        state["turn_rewards"] = []
        state["format_rewards"] = []
        state["episode_done"] = False
        return await super().setup_state(state)

    async def env_response(self, messages: vf.Messages, state: vf.State) -> vf.Messages:
        simulator: TowerDefenseEnv = state["simulator"]
        obs_for_plan = simulator._observation()
        candidates = _filter_macro_round_candidates(obs_for_plan)
        content = _completion_to_text(messages)
        actions, strict = _parse_plan_text(content)
        format_reward = 1.0 if strict else 0.0
        invalid_action = False
        invalid_reason = ""
        external_invalid = False
        if actions is None:
            actions = []
            format_reward = -1.0
            invalid_action = True
            invalid_reason = "invalid_plan"
            external_invalid = True

        total_reward = 0.0
        done = False
        last_obs: Dict[str, Any] | None = None
        sim_steps = 0

        prep_before = simulator.state.prep_actions_remaining if simulator.state is not None else 0
        budget = prep_before if prep_before is not None else 0
        if budget is None:
            budget = 0
        plan_limit = min(2, int(budget))
        if len(actions) > plan_limit:
            invalid_action = True
            invalid_reason = "plan_exceeds_budget"
            external_invalid = True
        actions_to_run = actions[: max(0, plan_limit)]
        resolved_actions: List[Dict[str, Any]] = []
        planning = TowerDefenseEnv(simulator.config)
        planning.load_from_observation(obs_for_plan)

        for action in actions_to_run:
            index = _coerce_int(action.get("index"))
            if index is None or index < 0 or index >= len(candidates):
                invalid_action = True
                external_invalid = True
                if not invalid_reason:
                    invalid_reason = "choose_out_of_range"
                continue
            candidate = candidates[index]
            if not isinstance(candidate, dict):
                invalid_action = True
                external_invalid = True
                if not invalid_reason:
                    invalid_reason = "choose_invalid_candidate"
                continue
            if candidate.get("type") == "start_round":
                # Skip without penalty; start_round is filtered from macro-round candidates.
                continue
            cand_type = candidate.get("type")
            ok = True
            reason = ""
            if cand_type == "build":
                ok, reason = planning._apply_build(candidate)
            elif cand_type == "upgrade":
                ok, reason = planning._apply_upgrade(candidate)
            elif cand_type == "sell":
                ok, reason = planning._apply_sell(candidate)
            if not ok:
                invalid_action = True
                external_invalid = True
                if not invalid_reason:
                    invalid_reason = (
                        "plan_insufficient_cash" if reason == "insufficient_cash" else reason
                    )
                continue
            resolved_actions.append(candidate)

        start_round_value = simulator.state.round if simulator.state is not None else 1
        for action in resolved_actions:
            last_obs, reward, done, info = simulator.step(action, internal=True)
            sim_steps += 1
            total_reward += float(reward)
            if info.get("invalid_action") and not invalid_reason:
                invalid_action = True
                invalid_reason = str(info.get("invalid_reason", "invalid_action"))
            if done:
                break

        if not done:
            rules_cfg = simulator.config.get("rules", {}) if isinstance(simulator.config.get("rules"), dict) else {}
            auto_advance = bool(rules_cfg.get("auto_advance_round", False))
            if auto_advance:
                target_round = start_round_value + 1
                remaining = 0
                if simulator.state is not None:
                    remaining = max(0, int(simulator.state.prep_actions_remaining))
                max_noops = remaining + 2
                noops = 0
                while (
                    simulator.state is not None
                    and simulator.state.round < target_round
                    and noops < max_noops
                    and not done
                ):
                    last_obs, reward, done, info = simulator.step({"type": "noop"}, internal=True)
                    sim_steps += 1
                    # Keep one-round progression even for external-invalid plans, but
                    # prevent pure-invalid plans from farming positive round rewards.
                    if external_invalid and not resolved_actions:
                        total_reward += min(0.0, float(reward))
                    else:
                        total_reward += float(reward)
                    if info.get("invalid_action") and not invalid_reason:
                        invalid_action = True
                        invalid_reason = str(info.get("invalid_reason", "invalid_action"))
                    noops += 1
                    if done:
                        break
            else:
                last_obs, reward, done, info = simulator.step({"type": "start_round"}, internal=True)
                sim_steps += 1
                total_reward += float(reward)
                if info.get("invalid_action") and not invalid_reason:
                    invalid_action = True
                    invalid_reason = str(info.get("invalid_reason", "invalid_action"))

        if last_obs is None:
            last_obs = simulator._observation()
        _filter_macro_round_candidates(last_obs)

        end_round_value = simulator.state.round if simulator.state is not None else start_round_value
        prep_after = simulator.state.prep_actions_remaining if simulator.state is not None else 0
        round_delta = end_round_value - start_round_value
        last_obs["macro_round_meta"] = {
            "start_round": start_round_value,
            "end_round": end_round_value,
            "delta_round": round_delta,
            "prep_before": prep_before,
            "prep_after": prep_after,
        }
        state["macro_round_last_meta"] = {
            "start_round": start_round_value,
            "end_round": end_round_value,
            "delta_round": round_delta,
            "sim_steps": sim_steps,
            "prep_before": prep_before,
            "prep_after": prep_after,
        }

        if not done and round_delta != 1:
            invalid_action = True
            if not invalid_reason:
                invalid_reason = "macro_round_round_jump"
            penalty = float(simulator.config.get("rewards", {}).get("macro_round_invariant_penalty", 0.0))
            total_reward -= penalty
            done = True
            state["episode_done"] = True

        if external_invalid:
            penalty = float(simulator.config.get("rewards", {}).get("invalid_action_penalty", 0.0))
            total_reward -= penalty

        state["turn_rewards"].append(total_reward)
        state["format_rewards"].append(format_reward)
        state["episode_done"] = bool(done)
        state["last_obs"] = last_obs
        if invalid_action:
            state.setdefault("invalid_actions", []).append(invalid_reason or "invalid_action")

        response = [{"role": "user", "content": f"Observation: {json.dumps(last_obs, sort_keys=True)}"}]
        if done:
            state["final_env_response"] = response
        return response

    def add_trajectory_step(self, state: vf.State, step: Dict[str, Any]) -> Dict[str, Any]:
        meta = state.get("macro_round_last_meta")
        if meta is not None:
            step.setdefault("extras", {})["macro_round"] = meta
        return super().add_trajectory_step(state, step)

    @vf.stop
    async def _episode_done(self, state: vf.State) -> bool:
        return bool(state.get("episode_done", False))


def load_environment(
    config: Dict[str, Any] | None = None,
    num_examples: int = 64,
    seed_start: int = 0,
    **_kwargs: Any,
) -> vf.Environment:
    """Prime Intellect verifiers entrypoint."""
    resolved = config or DEFAULT_CONFIG
    wrapper = str(resolved.get("wrapper", "") or "").lower()
    if wrapper == "macro_round":
        return TowerDefenseMacroRoundEnv(resolved, num_examples, seed_start)
    return TowerDefenseVerifiersEnv(resolved, num_examples, seed_start)
