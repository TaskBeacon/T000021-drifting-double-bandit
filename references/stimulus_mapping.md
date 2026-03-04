# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `bandit` | `pre_choice_fixation` | `fixation` | Central fixation before choice presentation | W2955737617 | Pre-choice pacing in repeated bandit decisions | psychopy_builtin | config text stimulus | Shared phase marker |
| `bandit` | `bandit_choice` | `machine_left`, `machine_right`, `machine_left_label`, `machine_right_label`, `choice_prompt` | Two side-by-side machines with prompt to choose left/right | W2955737617 | Restless two-option repeated choice under uncertainty | psychopy_builtin | config shape/text stimuli | No internal condition token shown |
| `bandit` | `choice_confirmation` | `highlight_left`, `highlight_right`, `target_prompt` | Brief confirmation of selected machine | W3024348208 | Post-choice commitment stage before reward signal | psychopy_builtin | config shape/text stimuli | Only chosen side highlighted |
| `bandit` | `outcome_feedback` | `feedback_win`, `feedback_loss` | Win/loss feedback with running score | W2027554764; W2084489534 | Reinforcement signal in unstable reward environment | psychopy_builtin | config text stimuli | Outcome valence-specific messaging |
| `bandit` | `iti` | `fixation` | Inter-trial fixation | W2084489534 | Trial separation in restless bandit flow | psychopy_builtin | config text stimulus | Shared phase marker |
| `all` | `instruction/block_break/goodbye` | `instruction_text`, `block_break`, `good_bye` | Instructions, block summary, and completion message | inferred | Operational session flow support | psychopy_builtin | config text stimuli | Localization-ready via config |
