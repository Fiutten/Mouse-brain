# Sensorium Official Trained Baseline Status

## What Was Integrated

We now have a bounded local training/evaluation path for the official
Sensorium ecosystem:

- official Sensorium mouse video loader;
- official `make_video_model` factory;
- official Factorized3dCore + factorized readout model family;
- MouseBrainBench comparator integration;
- audit artifact that separates "trained locally" from "Q1-qualified".

The executable artifact is:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache/xdg \
PYTHONPATH=external/neuralpredictors_43fa:external/sensorium_2023 \
.venv-sensorium-official/bin/python \
  scripts/train_sensorium_official_tiny_baseline.py
```

## Current Result

Output:

- `results/sensorium_official_baseline_audit/official_trained_baseline_summary.json`
- `results/dynamic_sensorium_model_comparator/summary.json`
- `results/sensorium_official_baseline_audit/summary.json`

Current run:

- usable mice: 5;
- training budget: 24 train batches, 16 oracle/eval batches per mouse;
- model: official architecture family, tiny local configuration;
- claim: reproducible integration and local control;
- blocked claim: official/SOTA Sensorium baseline.

The tiny official model loses against the tracked local MLP on all 5 paired
Dynamic Sensorium mice in the current comparator. This is useful negative
evidence: the official stack is integrated, but this bounded run is not the
differential Q1 piece.

## Scientific Interpretation

This artifact proves that MouseBrainBench can execute an official Sensorium
model family end to end. It does not prove that we have matched the official
competition baseline, because the run deliberately uses a small training budget
and a small model configuration.

For a Q1 claim, one of these is still required:

1. train the official baseline with the published/accepted budget and
   configuration, then evaluate it through MouseBrainBench; or
2. obtain an external official checkpoint/leaderboard-equivalent prediction set
   and evaluate it through MouseBrainBench.
