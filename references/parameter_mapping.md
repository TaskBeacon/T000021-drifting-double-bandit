# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| response_keys | `task.key_list` | `['f','j','space']` | W2955737617 | Repeated binary choice actions with continue key for non-trial pages | inferred | `f/j` for choice, `space` for continue |
| pre_choice_fixation_duration | `timing.pre_choice_fixation_duration` | `0.5` | W2955737617 | Pre-choice fixation before decision display | inferred | Gaze stabilization |
| choice_duration | `timing.choice_duration` | `2.0` | W2955737617 | Short repeated decision window in restless bandit | inferred | RT capture window |
| choice_confirmation_duration | `timing.choice_confirmation_duration` | `0.35` | W3024348208 | Brief post-choice commitment stage | inferred | Separates response from feedback |
| outcome_feedback_duration | `timing.outcome_feedback_duration` | `0.8` | W2084489534 | Feedback interval for reinforcement processing | inferred | Outcome display |
| initial_left_prob | `condition_generation.initial_left_prob` | `0.65` | W2027554764 | Asymmetric starting probabilities in unstable setting | inferred | Initial drift state |
| initial_right_prob | `condition_generation.initial_right_prob` | `0.35` | W2027554764 | Complement of initial left probability | inferred | Initial drift state |
| drift_sigma | `condition_generation.drift_sigma` | `0.05` | W2084489534 | Trial-wise random walk magnitude for restless contingency | inferred | Latent probability drift |
| anti_correlated | `condition_generation.anti_correlated` | `true` | W3024348208 | Competing option-value dynamics | inferred | Keeps two arms in opposition |
| prob_bounds | `condition_generation.min_prob`, `condition_generation.max_prob` | `0.10`, `0.90` | W2084489534 | Bound probabilities away from deterministic endpoints | inferred | Numerical stability |
| reward_values | `task.reward_win`, `task.reward_loss` | `10`, `0` | W2955737617 | Binary reinforcement mapping for behavior scoring | inferred | Displayed as points |
| trigger_fixation | `triggers.map.pre_choice_fixation_onset` | `20` | W2955737617 | Phase onset marker | inferred | EEG/event alignment |
| trigger_choice | `triggers.map.choice_onset` | `30` | W2955737617 | Choice display onset marker | inferred | Phase coding |
| trigger_confirm | `triggers.map.choice_confirmation_onset` | `40` | W3024348208 | Confirmation onset marker | inferred | Phase coding |
| trigger_feedback_win | `triggers.map.outcome_feedback_win_onset` | `50` | W2084489534 | Win-feedback onset marker | inferred | Outcome valence coding |
| trigger_feedback_loss | `triggers.map.outcome_feedback_loss_onset` | `51` | W2084489534 | Loss-feedback onset marker | inferred | Outcome valence coding |
| trigger_iti | `triggers.map.iti_onset` | `60` | W2955737617 | ITI onset marker | inferred | Phase boundary |
