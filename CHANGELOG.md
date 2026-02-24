# CHANGELOG

All notable development changes for `T000021-drifting-double-bandit` are documented here.

## [Unreleased]

### Changed
- Replaced the generic task `Controller` object with PsyFlow-aligned custom condition generation (`condition_generation`) plus `RewardTracker`.
- Refactored `main.py` to use `BlockUnit.generate_conditions(func=...)` for deterministic drifting trial specs.
- Refactored `src/run_trial.py` to consume preplanned fallback choice/reward draw values and use task-phase `StimUnit` labels.
- Updated sampler responder phase routing to canonical `bandit_choice` only.
- Renamed top-level config section `controller` -> `condition_generation` in all profiles and updated audit/reference docs accordingly.

### Fixed
- Repaired `src/run_trial.py` timing/trigger wiring to use existing config keys (`pre_choice_fixation_duration`, `choice_confirmation_duration`, `outcome_feedback_duration`, etc.) instead of stale template keys (`cue_duration`, `target_duration`, `feedback_duration`).
- Standardized ITI runtime phase naming to `iti` (removed `inter_trial_interval` runtime metadata).

## [0.2.2-dev] - 2026-02-19

### Changed
- Replaced template-like unit labels in `src/run_trial.py` with paradigm-specific labels (`pre_choice_fixation`, `bandit_choice`, `choice_confirmation`, `outcome_feedback`, `iti`).
- Migrated timing keys to phase-specific names in all configs:
  - `cue_duration` -> `pre_choice_fixation_duration`
  - `target_duration` -> `choice_confirmation_duration`
  - `feedback_duration` -> `outcome_feedback_duration`
- Migrated trigger keys to phase-specific names in all configs:
  - `cue_onset` -> `pre_choice_fixation_onset`
  - `target_onset` -> `choice_confirmation_onset`
  - `feedback_win_onset` / `feedback_loss_onset` -> `outcome_feedback_win_onset` / `outcome_feedback_loss_onset`
- Updated references/docs (`references/task_logic_audit.md`, `references/parameter_mapping.md`, `README.md`) to keep audit-to-code traceability with the new phase naming.

### Fixed
- Added backward-compatible fallback lookup in `src/run_trial.py` so legacy timing/trigger keys continue to run while new phase-specific keys are canonical.
- Standardized ITI runtime phase/state naming to `iti` instead of `inter_trial_interval`.

## [0.2.1] - 2026-02-18

### Changed
- Reworked trial logic in `src/run_trial.py` to a clean drifting-bandit flow with `cue -> anticipation -> target -> feedback -> iti` and removed forced-trial branch logic.
- Updated condition-generation utilities in `src/utils.py` to generate per-trial drifting probabilities without placeholder forced condition scheduling.
- Updated `main.py` block/final summaries to report `no_response_rate` instead of forced-trial metrics.
- Refactored `responders/task_sampler.py` to respond on anticipation stage with probability-based softmax choice only.
- Rewrote all configs (`config.yaml`, `config_qa.yaml`, `config_scripted_sim.yaml`, `config_sampler_sim.yaml`) with consistent Chinese text, SimHei font, and strict human/qa/sim separation.
- Updated `README.md` to match the current task logic and parameters.

### Fixed
- Removed repeated trial-screen key reminder text; key mapping is now taught in instructions only.
- Removed legacy placeholder fields in outputs and config text related to forced-trial mode.

## [0.2.0] - 2026-02-18

### Added
- Added drifting bandit condition generator in `src/utils.py` with:
  - Gaussian probability drift,
  - anti-correlated mode,
  - forced trial scheduling,
  - per-trial condition IDs.
- Added task-specific bandit sampler in `responders/task_sampler.py` using softmax choice policy with lapse and perseveration terms.
- Added forced-trial compliance fields to trial output (`forced_side`, `forced_compliant`).

### Changed
- Replaced MID-template trial logic with true drifting double-bandit flow in `src/run_trial.py`.
- Updated `main.py` to generate per-block drifting conditions instead of static condition list.
- Reworked all configs (`config.yaml`, `config_qa.yaml`, `config_scripted_sim.yaml`, `config_sampler_sim.yaml`) to align with drifting bandit design and Chinese participant-facing text.
- Updated `README.md` to full contract structure with reproducible flow/config/methods sections.

### Fixed
- Removed placeholder condition labels (`option_a/option_b/forced`) used as pseudo-task logic.
- Fixed response model from single-key placeholder (`space`) to real left/right decision input (`F/J`).
- Fixed QA acceptance columns to match actual drifting bandit outputs.
