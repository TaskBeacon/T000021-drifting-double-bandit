# Parameter Mapping

| Parameter | Implemented Value | Source Paper ID | Confidence | Rationale |
|---|---|---|---|---|
| `task.key_list` | `["f","j","space"]` | `W2955737617` | inferred | Two-choice decision keys plus continue key for instruction/break pages. |
| `timing.pre_choice_fixation_duration` | `0.5 s` | `W2955737617` | inferred | Brief pre-choice fixation to stabilize gaze before decision display. |
| `timing.choice_duration` | `2.0 s` | `W2955737617` | inferred | Short repeated response window in restless bandit decisions. |
| `timing.choice_confirmation_duration` | `0.35 s` | `W3024348208` | inferred | Short commitment/confirmation display separates response from feedback. |
| `timing.outcome_feedback_duration` | `0.8 s` | `W2084489534` | inferred | Feedback interval long enough for reinforcement signal registration. |
| `condition_generation.initial_left_prob` | `0.65` | `W2027554764` | inferred | Mild initial asymmetry to induce early learning pressure. |
| `condition_generation.initial_right_prob` | `0.35` | `W2027554764` | inferred | Complementary value for two-arm competition. |
| `condition_generation.drift_sigma` | `0.05` | `W2084489534` | inferred | Trial-wise Gaussian drift magnitude in restless environment. |
| `condition_generation.anti_correlated` | `true` | `W3024348208` | inferred | Maintains competing values between two options over time. |
| `condition_generation.min_prob/max_prob` | `0.10 / 0.90` | `W2084489534` | inferred | Prevents degenerate deterministic branches. |
| `task.reward_win/reward_loss` | `10 / 0` | `W2955737617` | inferred | Discrete reinforcement signal suitable for behavioral modeling. |
| `triggers.map.pre_choice_fixation_onset` | `20` | `W2955737617` | inferred | Event marker for pre-choice fixation onset. |
| `triggers.map.choice_onset` | `30` | `W2955737617` | inferred | Event marker for choice-screen onset. |
| `triggers.map.choice_confirmation_onset` | `40` | `W3024348208` | inferred | Event marker for post-response confirmation onset. |
| `triggers.map.outcome_feedback_win_onset` | `50` | `W2084489534` | inferred | Event marker for win feedback onset. |
| `triggers.map.outcome_feedback_loss_onset` | `51` | `W2084489534` | inferred | Event marker for no-win feedback onset. |
| `triggers.map.iti_onset` | `60` | `W2955737617` | inferred | Event marker for inter-trial interval onset. |
