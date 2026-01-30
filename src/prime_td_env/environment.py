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
        self.towers: Dict[int, Tower] = {}
        self.next_tower_id = 1
        self.next_bloon_id = 1

    def _normalize_upgrades(self, tower_type: TowerType, upgrades: Any) -> Dict[str, int]:
        if not isinstance(upgrades, dict):
            return {}
        normalized: Dict[str, int] = {}
        for path, tier in upgrades.items():
            if path not in tower_type.upgrade_paths:
                continue
            coerced = _coerce_int(tier)
            normalized[path] = max(0, coerced) if coerced is not None else 0
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
        map_obs = obs.get("map", {}) if isinstance(obs.get("map"), dict) else {}
        if map_obs.get("path"):
            self.path = self._normalize_points(map_obs["path"], "map.path", min_points=2)
        else:
            self.path = self._init_path()
        if map_obs.get("build_slots"):
            self.build_slots = self._normalize_points(map_obs["build_slots"], "map.build_slots")
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
        return self._observation()

    def step(self, action: Dict[str, Any] | None) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
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
        if self.state.phase != "build":
            invalid_action = True
            invalid_reason = "wrong_phase"
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
            reward, round_info = self._simulate_round()
            reward_breakdown.update(round_info.get("reward_breakdown", {}))
            info.update(round_info)
            completed_round = True
        elif action_type == "noop":
            pass
        else:
            invalid_action = True
            invalid_reason = "unknown_action"

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

        if not done and completed_round:
            self.state.round = current_round + 1
        if completed_round:
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
        cost = self.tower_types[tower_type].cost
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
        for path, tier in tower.upgrades.items():
            tier_value = self._get_upgrade_tier(tower, path)
            for i in range(tier_value):
                total_cost += self.tower_types[tower.type_name].upgrade_cost(path, i)
        return total_cost

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

    def _observation(self) -> Dict[str, Any]:
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

        return {
            "round": self.state.round,
            "phase": self.state.phase,
            "steps": self.state.steps,
            "lives": self.state.lives,
            "cash": self.state.cash,
            "seed": self.state.seed,
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
        return sorted([slot for slot in self.build_slots if slot not in occupied])

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
            if cash < tower_type.cost:
                continue
            for x, y in available_slots:
                build_actions.append(
                    {
                        "type": "build",
                        "tower_type": tower_name,
                        "x": x,
                        "y": y,
                        "cost": tower_type.cost,
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

        sell_actions = [
            {
                "type": "sell",
                "tower_id": tower_id,
                "refund": self._tower_refund(self.towers[tower_id]),
            }
            for tower_id in sorted(self.towers.keys())
        ]

        counts = {
            "build": len(build_actions),
            "upgrade": len(upgrade_actions),
            "sell": len(sell_actions),
        }
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

        return {
            "build": build_actions,
            "upgrade": upgrade_actions,
            "sell": sell_actions,
            "start_round": True,
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


ACTION_TYPES = {"build", "upgrade", "sell", "start_round", "noop"}
FORMAT_INVALID_REWARD = -5.0
MAX_ACTION_CHARS = 256

SYSTEM_PROMPT = (
    "You are playing a tower-defense game. Respond with ONLY a single JSON action "
    "object and no extra text. Examples: "
    "{\"type\": \"build\", \"tower_type\": \"dart\", \"x\": 0, \"y\": 0} "
    "{\"type\": \"upgrade\", \"tower_id\": 1, \"path\": \"a\"} "
    "{\"type\": \"sell\", \"tower_id\": 1} "
    "{\"type\": \"start_round\"} "
    "{\"type\": \"noop\"}."
)


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


_ACTIVE_CONFIG: Dict[str, Any] = DEFAULT_CONFIG


def _sample_action(obs: Dict[str, Any], rng: random.Random, policy: str) -> Dict[str, Any]:
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

    for i in range(num_examples):
        seed = seed_start + i
        obs = simulator.reset(seed=seed)
        rng = random.Random(seed + 101)
        for _ in range(max(0, rollout_steps)):
            action = _sample_action(obs, rng, policy)
            obs, _reward, done, _info = simulator.step(action)
            if done:
                break
        prompt = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Observation: {json.dumps(obs, sort_keys=True)}"},
        ]
        prompts.append(prompt)
        infos.append({"seed": seed, "obs": obs})
    return Dataset.from_dict({"prompt": prompts, "info": infos, "task": ["train"] * num_examples})


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
    _obs, reward, _done, _info = simulator.step(action)
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
        rubric = vf.Rubric(funcs=[_format_reward, _reward_from_action], weights=[format_weight, env_weight])
        super().__init__(dataset=dataset, rubric=rubric, **kwargs)


def load_environment(
    config: Dict[str, Any] | None = None,
    num_examples: int = 64,
    seed_start: int = 0,
    **_kwargs: Any,
) -> vf.Environment:
    """Prime Intellect verifiers entrypoint."""
    return TowerDefenseVerifiersEnv(config or DEFAULT_CONFIG, num_examples, seed_start)
