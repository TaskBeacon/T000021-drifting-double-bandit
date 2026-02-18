# Stimulus Mapping

Task: `Drifting Double-Bandit Task`

| Condition / Phase | Implemented Stimulus IDs | Source Paper ID | Evidence | Implementation Mode | Notes |
|---|---|---|---|---|---|
| Condition registry | `bandit` | `W2955737617` | Restless two-option bandit implemented as a single repeating condition with drifting latent reward rates. | `psychopy_builtin` | Condition token defined in `config/config.yaml`. |
| Choice screen | `machine_left`, `machine_right`, `machine_left_label`, `machine_right_label`, `choice_prompt` | `W2955737617` | Restless two-option repeated choice under uncertainty. | `psychopy_builtin` | Side-by-side option display without condition leakage. |
| Choice confirmation | `highlight_left`/`highlight_right`, `target_prompt` | `W3024348208` | Trial-wise choice commitment before reward feedback. | `psychopy_builtin` | Short confirmation stage for temporal separation of events. |
| Outcome feedback | `feedback_win`, `feedback_loss` | `W2027554764` | Reinforcement signal in unstable environments updates choice policy. | `psychopy_builtin` | Displays immediate outcome and running total score. |
| Inter-trial interval | `fixation` | `W2084489534` | Standard fixation-based ITI in sequential decision tasks. | `psychopy_builtin` | Stabilizes trial rhythm and trigger timing. |

Implementation mode legend:
- `psychopy_builtin`: rendered via PsychoPy text/shape primitives from YAML.
