# Drifting Double-Bandit Task

![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Drifting Double-Bandit Task |
| Version | v0.2.2-dev |
| URL / Repository | https://github.com/TaskBeacon/T000021-drifting-double-bandit |
| Short Description | Restless two-armed bandit task for exploration-exploitation behavior under non-stationary rewards. |
| Created By | TaskBeacon |
| Date Updated | 2026-02-19 |
| PsyFlow Version | 0.1.9 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural |

## 1. Task Overview

This task implements a restless (drifting) two-armed bandit paradigm. Participants repeatedly choose between left and right options while reward probabilities drift across trials. The task measures adaptive choice behavior, exploration-exploitation balance, and reward-based learning in non-stationary environments.

## 2. Task Flow

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Initialize runtime | Window, triggers, stimulus bank, and controller are initialized. |
| 2. Show instructions | Task instruction page is displayed before trials begin. |
| 3. Prepare block drift path | Controller generates per-trial drifting reward probabilities for the block. |
| 4. Execute block trials | Each trial records choice, RT, reward outcome, and cumulative score. |
| 5. Show block summary | Block statistics are displayed (choice ratio, hit rate, no-response ratio, block score). |
| 6. Show final summary | Final metrics are displayed and data are saved. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Pre-choice fixation | Central fixation before choice. |
| Bandit choice | Left/right options are shown and choice is captured (`F/J`). |
| Choice confirmation | Selected option is highlighted briefly. |
| Outcome feedback | Reward/no-reward feedback with cumulative score. |
| Inter-trial interval | Fixation interval before the next trial. |

### Controller Logic

| Component | Logic |
|---|---|
| Probability drift | Reward probabilities are updated each trial via Gaussian random walk (`drift_sigma`) and bounded to `[min_prob, max_prob]`. |
| Coupling | With `anti_correlated=true`, left and right probabilities drift in opposite directions. |
| Reward sampling | Bernoulli reward draw from current trial probabilities. |
| No-response policy | If no response occurs, fallback policy imputes a choice and flags `no_response=true`. |

### Runtime Context Phases

| Phase Label | Meaning |
|---|---|
| `pre_choice_fixation` | Fixation before choice. |
| `bandit_choice` | Choice response window. |
| `choice_confirmation` | Selected-option confirmation stage. |
| `outcome_feedback` | Outcome feedback stage. |
| `iti` | ITI stage. |

## 3. Configuration Summary

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | Participant identifier. |

### b. Window Settings

| Parameter | Value |
|---|---|
| `size` | `[1280, 720]` |
| `units` | `pix` |
| `screen` | `0` |
| `bg_color` | `black` |
| `fullscreen` | `false` |
| `monitor_width_cm` | `35.5` |
| `monitor_distance_cm` | `60` |

### c. Stimuli

| Name | Type | Description |
|---|---|---|
| `fixation` | text | Central fixation marker. |
| `machine_left/right` | rect | Left and right option panels. |
| `machine_left_label/right_label` | text | Option labels. |
| `highlight_left/right` | rect | Selection highlight frame. |
| `choice_prompt` | text | Choice prompt with deadline. |
| `target_prompt` | text | Choice confirmation text. |
| `feedback_win/loss` | text | Outcome feedback with score. |
| `block_break` / `good_bye` | text | Block/final summary pages. |

### d. Timing

| Phase | Duration |
|---|---|
| pre_choice_fixation_duration | 0.50 s |
| choice_duration | 2.00 s |
| choice_confirmation_duration | 0.35 s |
| outcome_feedback_duration | 0.80 s |
| iti_duration | 0.60 s |

## 4. Methods (for academic publication)

Participants completed repeated binary choices under non-stationary reward contingencies. Each trial contained fixation, choice, confirmation, and feedback stages, followed by an inter-trial interval. Reward probabilities changed continuously across trials via random walk dynamics.

The paradigm is designed to quantify adaptive learning under volatility. Trial logs include probabilities, responses, no-response imputations, reward outcomes, and cumulative score trajectories, enabling model-based analyses of exploration and exploitation strategies.

The implementation supports consistent `human`, `qa`, and `sim` execution pipelines with standardized responder context metadata.
