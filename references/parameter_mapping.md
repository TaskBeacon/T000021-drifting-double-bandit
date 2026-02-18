# Parameter Mapping

| Parameter | Implemented Value | Source Paper ID | Confidence | Rationale |
|---|---|---|---|---|
| `task.key_list` | `["f","j","space"]` | `W2955737617` | inferred | Two-choice decision keys plus continue key for instruction/break pages. |
| `timing.choice_duration` | `2.0 s` | `W2955737617` | inferred | Short repeated response window in restless bandit decisions. |
| `controller.initial_left_prob` | `0.65` | `W2027554764` | inferred | Mild initial asymmetry to induce early learning pressure. |
| `controller.initial_right_prob` | `0.35` | `W2027554764` | inferred | Complementary value for two-arm competition. |
| `controller.drift_sigma` | `0.05` | `W2084489534` | inferred | Trial-wise Gaussian drift magnitude in restless environment. |
| `controller.anti_correlated` | `true` | `W3024348208` | inferred | Maintains competing values between two options over time. |
| `controller.min_prob/max_prob` | `0.10 / 0.90` | `W2084489534` | inferred | Prevents degenerate deterministic branches. |
| `task.reward_win/reward_loss` | `10 / 0` | `W2955737617` | inferred | Discrete reinforcement signal suitable for behavioral modeling. |
