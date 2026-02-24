from __future__ import annotations

import random
from typing import Any

from psychopy import logging


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


class RewardTracker:
    """Track cumulative reward across trials."""

    def __init__(self, initial_reward: int = 0) -> None:
        self.cumulative_reward = int(initial_reward)

    def update(self, delta: int) -> int:
        self.cumulative_reward += int(delta)
        return self.cumulative_reward


def _drift_once(
    *,
    rng: random.Random,
    p_left: float,
    p_right: float,
    drift_sigma: float,
    min_prob: float,
    max_prob: float,
    anti_correlated: bool,
) -> tuple[float, float]:
    if drift_sigma <= 0.0:
        return p_left, p_right

    if anti_correlated:
        delta = rng.gauss(0.0, drift_sigma)
        p_left = _clip(p_left + delta, min_prob, max_prob)
        p_right = _clip(1.0 - p_left, min_prob, max_prob)
        p_left = _clip(1.0 - p_right, min_prob, max_prob)
        return p_left, p_right

    p_left = _clip(p_left + rng.gauss(0.0, drift_sigma), min_prob, max_prob)
    p_right = _clip(p_right + rng.gauss(0.0, drift_sigma), min_prob, max_prob)
    return p_left, p_right


def generate_drifting_bandit_conditions(
    n_trials: int,
    condition_labels: list[Any] | None,
    *,
    seed: int,
    initial_left_prob: float = 0.65,
    initial_right_prob: float = 0.35,
    drift_sigma: float = 0.05,
    min_prob: float = 0.10,
    max_prob: float = 0.90,
    anti_correlated: bool = True,
    no_choice_policy: str = "random",
    randomize_within_block: bool = False,
    enable_logging: bool = True,
) -> list[tuple[float, float, str, int, str, float]]:
    """
    Generate per-trial drifting probability conditions plus deterministic draws.

    Returns tuples:
    (p_left, p_right, condition_id, trial_index, fallback_side, reward_draw_u)
    """
    del condition_labels  # not used; required by BlockUnit custom-func signature

    n = int(n_trials)
    if n <= 0:
        return []

    rng = random.Random(int(seed))
    policy = str(no_choice_policy).strip().lower()
    if policy not in {"random", "left", "right"}:
        raise ValueError("no_choice_policy must be one of: random, left, right")

    min_prob = _clip(min_prob, 0.0, 1.0)
    max_prob = _clip(max_prob, min_prob, 1.0)
    drift_sigma = max(0.0, float(drift_sigma))
    p_left = _clip(initial_left_prob, min_prob, max_prob)
    p_right = _clip(initial_right_prob, min_prob, max_prob)

    trials: list[tuple[float, float, str, int, str, float]] = []
    for trial_index in range(1, n + 1):
        cond_id = f"L{int(round(p_left * 100)):02d}_R{int(round(p_right * 100)):02d}_t{trial_index:03d}"
        if policy == "random":
            fallback_side = "left" if rng.random() < 0.5 else "right"
        else:
            fallback_side = policy
        reward_draw_u = float(rng.random())
        trials.append(
            (
                round(float(p_left), 4),
                round(float(p_right), 4),
                cond_id,
                trial_index,
                fallback_side,
                reward_draw_u,
            )
        )
        p_left, p_right = _drift_once(
            rng=rng,
            p_left=float(p_left),
            p_right=float(p_right),
            drift_sigma=drift_sigma,
            min_prob=min_prob,
            max_prob=max_prob,
            anti_correlated=bool(anti_correlated),
        )

    if bool(randomize_within_block):
        rng.shuffle(trials)

    if bool(enable_logging):
        avg_left = sum(float(t[0]) for t in trials) / max(1, len(trials))
        avg_right = sum(float(t[1]) for t in trials) / max(1, len(trials))
        logging.data(
            f"[DriftingBandit] n_trials={n} seed={seed} avg_p_left={avg_left:.3f} avg_p_right={avg_right:.3f}"
        )
    return trials


def reward_from_draw(*, choice_side: str, p_left: float, p_right: float, draw_u: float) -> bool:
    p = float(p_left) if str(choice_side) == "left" else float(p_right)
    p = _clip(p, 0.0, 1.0)
    return float(draw_u) < p
