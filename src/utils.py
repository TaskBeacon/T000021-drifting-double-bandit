from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any

from psychopy import logging


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


@dataclass
class Controller:
    """Controller for a drifting two-armed bandit task."""

    initial_left_prob: float = 0.65
    initial_right_prob: float = 0.35
    drift_sigma: float = 0.05
    min_prob: float = 0.10
    max_prob: float = 0.90
    anti_correlated: bool = True
    no_choice_policy: str = "random"
    randomize_within_block: bool = False
    enable_logging: bool = True

    _rng: random.Random = field(init=False, repr=False)
    completed_trials: int = field(init=False, default=0)
    cumulative_reward: int = field(init=False, default=0)
    history: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._rng = random.Random(0)
        self.no_choice_policy = str(self.no_choice_policy).strip().lower()
        self.drift_sigma = max(0.0, float(self.drift_sigma))
        self.min_prob = _clip(float(self.min_prob), 0.0, 1.0)
        self.max_prob = _clip(float(self.max_prob), self.min_prob, 1.0)
        self.initial_left_prob = _clip(float(self.initial_left_prob), self.min_prob, self.max_prob)
        self.initial_right_prob = _clip(float(self.initial_right_prob), self.min_prob, self.max_prob)
        if self.no_choice_policy not in {"random", "left", "right"}:
            raise ValueError("[DriftBanditController] no_choice_policy must be one of: random, left, right.")

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "Controller":
        allowed = {
            "initial_left_prob",
            "initial_right_prob",
            "drift_sigma",
            "min_prob",
            "max_prob",
            "anti_correlated",
            "no_choice_policy",
            "randomize_within_block",
            "enable_logging",
        }
        extra = set(config.keys()) - allowed
        if extra:
            raise ValueError(f"[DriftBanditController] Unsupported config keys: {sorted(extra)}")
        return cls(
            initial_left_prob=float(config.get("initial_left_prob", 0.65)),
            initial_right_prob=float(config.get("initial_right_prob", 0.35)),
            drift_sigma=float(config.get("drift_sigma", 0.05)),
            min_prob=float(config.get("min_prob", 0.10)),
            max_prob=float(config.get("max_prob", 0.90)),
            anti_correlated=bool(config.get("anti_correlated", True)),
            no_choice_policy=str(config.get("no_choice_policy", "random")),
            randomize_within_block=bool(config.get("randomize_within_block", False)),
            enable_logging=bool(config.get("enable_logging", True)),
        )

    def _drift_once(self, p_left: float, p_right: float) -> tuple[float, float]:
        if self.drift_sigma <= 0.0:
            return p_left, p_right

        if self.anti_correlated:
            delta = self._rng.gauss(0.0, self.drift_sigma)
            p_left = _clip(p_left + delta, self.min_prob, self.max_prob)
            p_right = 1.0 - p_left
            p_right = _clip(p_right, self.min_prob, self.max_prob)
            p_left = 1.0 - p_right
            p_left = _clip(p_left, self.min_prob, self.max_prob)
            return p_left, p_right

        p_left = _clip(p_left + self._rng.gauss(0.0, self.drift_sigma), self.min_prob, self.max_prob)
        p_right = _clip(p_right + self._rng.gauss(0.0, self.drift_sigma), self.min_prob, self.max_prob)
        return p_left, p_right

    def prepare_block(self, *, block_idx: int, n_trials: int, seed: int) -> list[tuple[Any, ...]]:
        if n_trials <= 0:
            return []
        self._rng = random.Random(int(seed) + int(block_idx) * 1009)

        p_left = float(self.initial_left_prob)
        p_right = float(self.initial_right_prob)

        trials: list[tuple[Any, ...]] = []
        for i in range(int(n_trials)):
            condition_id = f"L{int(round(p_left * 100)):02d}_R{int(round(p_right * 100)):02d}_t{i + 1:03d}"
            trials.append((round(p_left, 4), round(p_right, 4), condition_id, i + 1))
            p_left, p_right = self._drift_once(p_left, p_right)

        if self.randomize_within_block:
            self._rng.shuffle(trials)

        if self.enable_logging:
            avg_left = sum(float(t[0]) for t in trials) / max(1, len(trials))
            avg_right = sum(float(t[1]) for t in trials) / max(1, len(trials))
            logging.data(
                f"[DriftBanditController] block={block_idx} n_trials={n_trials} seed={seed} "
                f"avg_p_left={avg_left:.3f} avg_p_right={avg_right:.3f}"
            )
        return trials

    def fallback_choice(self, *, left_key: str, right_key: str) -> str:
        if self.no_choice_policy == "left":
            return left_key
        if self.no_choice_policy == "right":
            return right_key
        return left_key if self._rng.random() < 0.5 else right_key

    def draw_reward(self, *, choice_side: str, p_left: float, p_right: float) -> bool:
        p = float(p_left) if str(choice_side) == "left" else float(p_right)
        p = _clip(p, 0.0, 1.0)
        return bool(self._rng.random() < p)

    def update(self, trial_summary: dict[str, Any]) -> None:
        self.completed_trials += 1
        delta = int(trial_summary.get("reward_delta", 0) or 0)
        self.cumulative_reward += delta
        self.history.append(dict(trial_summary))
        if self.enable_logging:
            logging.data(
                f"[DriftBanditController] trial={self.completed_trials} "
                f"choice={trial_summary.get('choice_side')} "
                f"p_left={float(trial_summary.get('p_left', 0.0)):.2f} "
                f"p_right={float(trial_summary.get('p_right', 0.0)):.2f} "
                f"win={bool(trial_summary.get('reward_win', False))} "
                f"delta={delta} total={self.cumulative_reward}"
            )
