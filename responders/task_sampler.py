from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Any
import random as _py_random

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    """Sampler responder for drifting double-bandit choice behavior."""

    left_key: str = "f"
    right_key: str = "j"
    temperature: float = 0.45
    perseveration: float = 0.15
    lapse_rate: float = 0.05
    rt_mean_s: float = 0.55
    rt_sd_s: float = 0.12
    rt_min_s: float = 0.18
    continue_key: str = "space"
    continue_rt_s: float = 0.25

    def __post_init__(self) -> None:
        self._rng: Any = None
        self._last_side: str | None = None
        self.temperature = max(1e-4, float(self.temperature))
        self.perseveration = float(self.perseveration)
        self.lapse_rate = max(0.0, min(1.0, float(self.lapse_rate)))
        self.rt_mean_s = float(self.rt_mean_s)
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))
        self.continue_rt_s = max(0.0, float(self.continue_rt_s))

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng
        self._last_side = None

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None
        self._last_side = None

    def _rand(self) -> float:
        rng = self._rng
        if hasattr(rng, "random"):
            return float(rng.random())
        return float(_py_random.random())

    def _normal(self, mean: float, sd: float) -> float:
        rng = self._rng
        if hasattr(rng, "normal"):
            return float(rng.normal(mean, sd))
        return float(rng.gauss(mean, sd))

    def _softmax_prob_left(self, p_left: float, p_right: float) -> float:
        utility_left = float(p_left) + (self.perseveration if self._last_side == "left" else 0.0)
        utility_right = float(p_right) + (self.perseveration if self._last_side == "right" else 0.0)
        z_left = exp(utility_left / self.temperature)
        z_right = exp(utility_right / self.temperature)
        denom = z_left + z_right
        if denom <= 0:
            return 0.5
        return z_left / denom

    def _read_choice_factors(self, obs: Observation) -> tuple[float, float]:
        factors = dict(obs.task_factors or {})
        p_left = float(factors.get("p_left", 0.5))
        p_right = float(factors.get("p_right", 0.5))
        return p_left, p_right

    def act(self, obs: Observation) -> Action:
        valid_keys = list(obs.valid_keys or [])
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})
        if self._rng is None:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "rng_missing"})

        phase = str(obs.phase or "")
        if phase != "anticipation":
            if self.continue_key in valid_keys:
                return Action(
                    key=self.continue_key,
                    rt_s=self.continue_rt_s,
                    meta={"source": "task_sampler", "phase": phase, "policy": "continue"},
                )
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "phase": phase})

        p_left, p_right = self._read_choice_factors(obs)
        rt = max(self.rt_min_s, self._normal(self.rt_mean_s, self.rt_sd_s))

        # lapse: random valid key
        if self._rand() < self.lapse_rate:
            picked = valid_keys[0] if self._rand() < 0.5 else valid_keys[-1]
            self._last_side = "left" if picked == self.left_key else "right"
            return Action(
                key=picked,
                rt_s=rt,
                meta={"source": "task_sampler", "policy": "lapse"},
            )

        p_choose_left = self._softmax_prob_left(p_left=p_left, p_right=p_right)
        choose_left = bool(self._rand() < p_choose_left)
        picked = self.left_key if choose_left else self.right_key
        if picked not in valid_keys:
            picked = valid_keys[0]
        self._last_side = "left" if picked == self.left_key else "right"
        return Action(
            key=picked,
            rt_s=rt,
            meta={
                "source": "task_sampler",
                "policy": "softmax",
                "p_left": p_left,
                "p_right": p_right,
                "p_choose_left": p_choose_left,
            },
        )
