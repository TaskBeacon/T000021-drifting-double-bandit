# CHANGELOG

All notable development changes for `T000021-drifting-double-bandit` are documented here.

## [0.2.1] - 2026-02-18

### Changed
- Reworked trial logic in `src/run_trial.py` to a clean drifting-bandit flow with `cue -> anticipation -> target -> feedback -> iti` and removed forced-trial branch logic.
- Updated controller in `src/utils.py` to generate per-trial drifting probabilities without placeholder forced condition scheduling.
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
- Updated `main.py` to generate per-block drifting conditions via controller instead of static condition list.
- Reworked all configs (`config.yaml`, `config_qa.yaml`, `config_scripted_sim.yaml`, `config_sampler_sim.yaml`) to align with drifting bandit design and Chinese participant-facing text.
- Updated `README.md` to full contract structure with reproducible flow/config/methods sections.

### Fixed
- Removed placeholder condition labels (`option_a/option_b/forced`) used as pseudo-task logic.
- Fixed response model from single-key placeholder (`space`) to real left/right decision input (`F/J`).
- Fixed QA acceptance columns to match actual drifting bandit outputs.
