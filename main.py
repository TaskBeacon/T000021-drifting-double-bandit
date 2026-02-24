from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core

from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    count_down,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import RewardTracker, generate_drifting_bandit_conditions, run_trial

MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def run(options: TaskRunOptions):
    """Run Drifting Double-Bandit task in human/qa/sim mode with one auditable flow."""
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path), extra_keys=["condition_generation"])
    
    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        # 2. Collect subject info
        if options.mode == "qa":
            subject_data = {"subject_id": "qa"}
        elif options.mode == "sim":
            participant_id = "sim"
            if runtime_ctx is not None and runtime_ctx.session is not None:
                participant_id = str(runtime_ctx.session.participant_id or "sim")
            subject_data = {"subject_id": participant_id}
        else:
            subform = SubInfo(cfg["subform_config"])
            subject_data = subform.collect()

        # 3. Load task settings
        settings = TaskSettings.from_dict(cfg["task_config"])
        if options.mode in ("qa", "sim") and output_dir is not None:
            settings.save_path = str(output_dir)
        settings.add_subinfo(subject_data)

        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        # 4. Task-specific condition generation settings (no adaptive controller object)
        condition_generation = cfg.get("condition_generation_config", {})

        # 5. Setup triggers
        settings.triggers = cfg["trigger_config"]
        trigger_runtime = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(cfg)

        # 6. Set up window & input
        win, kb = initialize_exp(settings)

        # 7. Setup stimulus bank
        stim_bank = StimBank(win, cfg["stim_config"])
        if options.mode not in ("qa", "sim"):
            stim_bank = stim_bank.convert_to_voice("instruction_text")
        stim_bank = stim_bank.preload_all()

        # 8. Setup reward tracker
        reward_tracker = RewardTracker()

        trigger_runtime.send(settings.triggers.get("exp_onset"))

        # Instruction
        instr = StimUnit("instruction_text", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("instruction_text")
        )
        if options.mode not in ("qa", "sim"):
            instr.add_stim(stim_bank.get("instruction_text_voice"))
        instr.wait_and_continue()

        all_data = []
        for block_i in range(settings.total_blocks):
            if options.mode not in ("qa", "sim"):
                count_down(win, 3, color="white")

            block = (
                BlockUnit(
                    block_id=f"block_{block_i}",
                    block_idx=block_i,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                )
                .generate_conditions(
                    func=generate_drifting_bandit_conditions,
                    n_trials=int(settings.trials_per_block),
                    condition_labels=list(getattr(settings, "conditions", ["bandit"])),
                    seed=int(settings.block_seed[block_i]),
                    **condition_generation,
                )
                .on_start(lambda b: trigger_runtime.send(settings.triggers.get("block_onset")))
                .on_end(lambda b: trigger_runtime.send(settings.triggers.get("block_end")))
                .run_trial(
                    partial(
                        run_trial,
                        stim_bank=stim_bank,
                        reward_tracker=reward_tracker,
                        trigger_runtime=trigger_runtime,
                        block_id=f"block_{block_i}",
                        block_idx=block_i,
                    )
                )
                .to_dict(all_data)
            )

            block_trials = block.get_all_data()
            n_block = max(1, len(block_trials))
            left_rate = sum(1 for t in block_trials if t.get("choice_side") == "left") / n_block
            win_rate = sum(1 for t in block_trials if bool(t.get("reward_win", False))) / n_block
            no_response_rate = sum(1 for t in block_trials if bool(t.get("missed_choice", False))) / n_block
            block_score = sum(int(t.get("reward_delta", 0) or 0) for t in block_trials)

            StimUnit("block", win, kb, runtime=trigger_runtime).add_stim(
                stim_bank.get_and_format(
                    "block_break",
                    block_num=block_i + 1,
                    total_blocks=settings.total_blocks,
                    left_rate=left_rate,
                    win_rate=win_rate,
                    no_response_rate=no_response_rate,
                    total_score=block_score,
                )
            ).wait_and_continue()

        n_all = max(1, len(all_data))
        final_score = sum(int(t.get("reward_delta", 0) or 0) for t in all_data)
        final_left_rate = sum(1 for t in all_data if t.get("choice_side") == "left") / n_all
        final_win_rate = sum(1 for t in all_data if bool(t.get("reward_win", False))) / n_all
        final_no_response_rate = sum(1 for t in all_data if bool(t.get("missed_choice", False))) / n_all

        StimUnit("goodbye", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get_and_format(
                "good_bye",
                total_score=final_score,
                left_rate=f"{final_left_rate:.1%}",
                win_rate=f"{final_win_rate:.1%}",
                no_response_rate=f"{final_no_response_rate:.1%}",
            )
        ).wait_and_continue(terminate=True)

        trigger_runtime.send(settings.triggers.get("exp_end"))
        
        df = pd.DataFrame(all_data)
        df.to_csv(settings.res_file, index=False)

        trigger_runtime.close()
        core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = parse_task_run_options(
        task_root=task_root,
        description="Run Drifting Double-Bandit task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )
    run(options)


if __name__ == "__main__":
    main()
