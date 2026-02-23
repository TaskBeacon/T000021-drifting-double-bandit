from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, set_trial_context, next_trial_id
from psyflow.sim import get_context

# run_trial uses task-specific phase labels via set_trial_context(...).


def _qa_scale_duration(duration_s: float, win) -> float:
    base = max(0.0, float(duration_s))
    ctx = get_context()
    if ctx is None or not ctx.config.enable_scaling:
        return base
    frame = float(getattr(win, "monitorFramePeriod", 1.0 / 60.0) or (1.0 / 60.0))
    min_frames = int(max(1, ctx.config.min_frames))
    scaled = base * float(ctx.config.timing_scale)
    return max(scaled, frame * min_frames)


def _parse_condition(condition: Any) -> tuple[float, float, str, int | None]:
    if isinstance(condition, dict):
        p_left = float(condition.get("p_left", 0.5))
        p_right = float(condition.get("p_right", 0.5))
        condition_id = str(
            condition.get(
                "condition_id",
                f"L{int(round(p_left * 100)):02d}_R{int(round(p_right * 100)):02d}",
            )
        )
        trial_index = condition.get("trial_index", None)
        return p_left, p_right, condition_id, (int(trial_index) if trial_index is not None else None)

    if isinstance(condition, (tuple, list)) and len(condition) >= 2:
        p_left = float(condition[0])
        p_right = float(condition[1])
        condition_id = (
            str(condition[2])
            if len(condition) >= 3 and condition[2] is not None
            else f"L{int(round(p_left * 100)):02d}_R{int(round(p_right * 100)):02d}"
        )
        trial_index = int(condition[3]) if len(condition) >= 4 and condition[3] is not None else None
        return p_left, p_right, condition_id, trial_index

    raise ValueError(f"Unsupported drifting-bandit condition format: {condition!r}")


def _fmt_pct(value: float) -> str:
    return f"{int(round(max(0.0, min(1.0, float(value))) * 100))}%"


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    controller,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    trial_id = next_trial_id()
    p_left, p_right, condition_id, trial_index = _parse_condition(condition)

    left_key = str(getattr(settings, "left_key", "f"))
    right_key = str(getattr(settings, "right_key", "j"))
    reward_win_value = int(getattr(settings, "reward_win", 10))
    reward_loss_value = int(getattr(settings, "reward_loss", 0))

    trial_data = {
        "trial_id": trial_id,
        "trial_index": trial_index,
        "condition_id": condition_id,
        "p_left": p_left,
        "p_right": p_right,
        "left_reward_prob_pct": _fmt_pct(p_left),
        "right_reward_prob_pct": _fmt_pct(p_right),
    }
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    cue = make_unit(unit_label="cue").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        cue,
        trial_id=trial_id,
        phase="pre_choice_fixation",
        deadline_s=settings.cue_duration,
        valid_keys=[],
        block_id=block_id,
        condition_id=condition_id,
        task_factors={"stage": "pre_choice_fixation", "p_left": p_left, "p_right": p_right, "block_idx": block_idx},
        stim_id="fixation",
    )
    cue.show(
        duration=float(settings.cue_duration),
        onset_trigger=settings.triggers.get("cue_onset"),
    ).to_dict(trial_data)

    choice = (
        make_unit(unit_label="anticipation")
        .add_stim(stim_bank.get("machine_left"))
        .add_stim(stim_bank.get("machine_right"))
        .add_stim(stim_bank.get("machine_left_label"))
        .add_stim(stim_bank.get("machine_right_label"))
        .add_stim(stim_bank.get_and_format("choice_prompt", deadline_s=f"{float(settings.choice_duration):.1f}"))
    )
    set_trial_context(
        choice,
        trial_id=trial_id,
        phase="bandit_choice",
        deadline_s=settings.choice_duration,
        valid_keys=[left_key, right_key],
        block_id=block_id,
        condition_id=condition_id,
        task_factors={
            "stage": "bandit_choice",
            "p_left": p_left,
            "p_right": p_right,
            "left_key": left_key,
            "right_key": right_key,
            "block_idx": block_idx,
        },
        stim_id="bandit_choice",
    )
    choice.capture_response(
        keys=[left_key, right_key],
        correct_keys=[left_key, right_key],
        duration=float(settings.choice_duration),
        onset_trigger=settings.triggers.get("choice_onset"),
        response_trigger={
            left_key: settings.triggers.get("choice_left_press"),
            right_key: settings.triggers.get("choice_right_press"),
        },
        timeout_trigger=settings.triggers.get("choice_no_response"),
        terminate_on_response=False,
        highlight_stim={
            left_key: stim_bank.get("highlight_left"),
            right_key: stim_bank.get("highlight_right"),
        },
        dynamic_highlight=False,
    )

    raw_key = choice.get_state("response", None)
    no_response = raw_key not in (left_key, right_key)
    choice_key = raw_key
    if no_response:
        choice_key = controller.fallback_choice(left_key=left_key, right_key=right_key)
        trigger_runtime.send(settings.triggers.get("choice_imputed"))

    choice_side = "left" if choice_key == left_key else "right"
    choice_prob = float(p_left if choice_side == "left" else p_right)
    choice_rt = choice.get_state("response_time", None)

    choice.set_state(
        choice_key=choice_key,
        choice_side=choice_side,
        choice_prob=choice_prob,
        missed_choice=no_response,
    ).to_dict(trial_data)

    choice_label = "左侧机器" if choice_side == "left" else "右侧机器"
    highlight_id = "highlight_left" if choice_side == "left" else "highlight_right"
    target = (
        make_unit(unit_label="target")
        .add_stim(stim_bank.get("machine_left"))
        .add_stim(stim_bank.get("machine_right"))
        .add_stim(stim_bank.get("machine_left_label"))
        .add_stim(stim_bank.get("machine_right_label"))
        .add_stim(stim_bank.get(highlight_id))
        .add_stim(stim_bank.get_and_format("target_prompt", choice_label=choice_label))
    )
    set_trial_context(
        target,
        trial_id=trial_id,
        phase="choice_confirmation",
        deadline_s=settings.target_duration,
        valid_keys=[],
        block_id=block_id,
        condition_id=condition_id,
        task_factors={
            "stage": "choice_confirmation",
            "choice_side": choice_side,
            "choice_prob": choice_prob,
            "p_left": p_left,
            "p_right": p_right,
            "block_idx": block_idx,
        },
        stim_id="selection_confirmation",
    )
    target.show(
        duration=float(settings.target_duration),
        onset_trigger=settings.triggers.get("target_onset"),
    ).to_dict(trial_data)

    reward_win = controller.draw_reward(choice_side=choice_side, p_left=p_left, p_right=p_right)
    reward_delta = reward_win_value if reward_win else reward_loss_value
    projected_total = int(getattr(controller, "cumulative_reward", 0)) + reward_delta
    feedback_stim = (
        stim_bank.get_and_format("feedback_win", reward_delta=reward_delta, total_score=projected_total)
        if reward_win
        else stim_bank.get_and_format("feedback_loss", reward_delta=reward_delta, total_score=projected_total)
    )
    feedback_trigger = (
        settings.triggers.get("feedback_win_onset")
        if reward_win
        else settings.triggers.get("feedback_loss_onset")
    )
    feedback = make_unit(unit_label="feedback").add_stim(feedback_stim)
    set_trial_context(
        feedback,
        trial_id=trial_id,
        phase="outcome_feedback",
        deadline_s=settings.feedback_duration,
        valid_keys=[],
        block_id=block_id,
        condition_id=condition_id,
        task_factors={
            "stage": "outcome_feedback",
            "choice_side": choice_side,
            "reward_win": reward_win,
            "reward_delta": reward_delta,
            "block_idx": block_idx,
        },
        stim_id="feedback_win" if reward_win else "feedback_loss",
    )
    feedback.show(
        duration=float(settings.feedback_duration),
        onset_trigger=feedback_trigger,
    ).set_state(
        reward_win=reward_win,
        reward_delta=reward_delta,
    ).to_dict(trial_data)

    iti = make_unit(unit_label="iti").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="inter_trial_interval",
        deadline_s=settings.iti_duration,
        valid_keys=[],
        block_id=block_id,
        condition_id=condition_id,
        task_factors={"stage": "inter_trial_interval", "block_idx": block_idx},
        stim_id="fixation",
    )
    iti.show(
        duration=float(settings.iti_duration),
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    controller.update(
        {
            "choice_side": choice_side,
            "choice_key": choice_key,
            "choice_prob": choice_prob,
            "reward_win": reward_win,
            "reward_delta": reward_delta,
            "p_left": p_left,
            "p_right": p_right,
            "no_response": no_response,
        }
    )

    trial_data.update(
        {
            "choice_key": choice_key,
            "choice_side": choice_side,
            "choice_rt": choice_rt,
            "choice_prob": choice_prob,
            "missed_choice": no_response,
            "reward_win": reward_win,
            "reward_delta": reward_delta,
            "total_score": int(getattr(controller, "cumulative_reward", 0)),
        }
    )
    for key in [k for k in trial_data if k.endswith("_no_response")]:
        trial_data.pop(key, None)
    return trial_data
