# Allen session normalization

## Purpose

Convert one Allen Visual Behavior Neuropixels NWB session into the core `Session` artifact:

```text
artifacts/datasets/allen/<ecephys_session_id>/session.json
```

## Implemented components

- `neurotwin_mvp/allen_normalization.py`
- `scripts/allen_export_session.py`
- tests with fake Allen session objects
- offline loading from the cached NWB file when present
- unit-to-region mapping through `peak_channel_id -> channel.structure_acronym`
- `searchsorted` spike counting for AllenSDK sorted spike-time arrays

## Current default windows

All windows are relative to trial start:

```text
baseline: -0.250s to 0.000s
stimulus:  0.000s to 0.250s
decision:  0.250s to 0.750s
pre_response: 0.250s to min(0.750s, response_time - 0.050s)
```

`Trial.region_rates` remains the stimulus-window rate for backward
compatibility with the existing benchmark stack. New exports also store all
three windows in:

```text
trial.metadata["region_rates_by_window"]
```

This nested field is required by the temporal-window benchmark. Older artifacts
without it must be re-exported before temporal claims are made.

The `pre_response` window is dynamic. Trials with no response use the default
0.250s to 0.750s window; trials with a response are truncated 50 ms before the
response. If the response occurs too early to form a positive-duration window,
the window is marked invalid in:

```text
trial.metadata["time_window_valid"]["pre_response"]
```

## Region mapping

Allen acronyms are mapped to coarse model regions using `COARSE_REGION_MAP`:

- visual cortex;
- visual thalamus;
- hippocampus;
- basal ganglia;
- arousal/midbrain.

For Visual Behavior Neuropixels, the real `get_units(...)` table does not
include anatomical acronyms directly. Units are mapped through:

```text
unit.peak_channel_id -> channel.id -> channel.structure_acronym
```

For session `1087992708`, this maps 2,735 of 3,043 sorted units into the current
coarse model regions after adding the aggregate `DG` hippocampal acronym. Units
in structures outside the current model scope remain intentionally unmapped.

## Scientific limitations

The normalizer aggregates recorded/sorted units into region-level rates.

It does not:

- estimate total biological neuron counts;
- infer unrecorded neurons;
- model cell types;
- produce a calibrated digital twin by itself.

It creates the first empirical artifact needed to calibrate and test the regional model.

The current stimulus encoding is a deterministic binary placeholder derived
from Allen image metadata. It is acceptable for pipeline validation, but it is
not a final task model and must be replaced with a scientifically justified
visual-behavior feature encoding before claims about behavior or cognition.

## Real execution

Requires `.venv-allen` with AllenSDK:

```bash
.venv-allen/bin/python scripts/allen_export_session.py \
  --ecephys-session-id 1087992708 \
  --behavior-session-id 1088053452 \
  --animal-id 556014 \
  --out artifacts/datasets/allen/1087992708 \
  --baseline-start -0.250 \
  --baseline-end 0.0 \
  --stimulus-start 0.0 \
  --stimulus-end 0.250 \
  --decision-start 0.250 \
  --decision-end 0.750 \
  --pre-response-start 0.250 \
  --pre-response-end 0.750 \
  --response-margin 0.050 \
  --max-trials 100
```

Verified output after default behavior-trial filtering:

```text
artifacts/datasets/allen/1087992708/session.json
n_trials = 162
regions = arousal_midbrain, basal_ganglia, hippocampus, visual_cortex, visual_thalamus
```

Default filtering excludes aborted and auto-rewarded trials, and keeps go/catch
trials. Trial metadata now preserves Allen task fields such as image names,
go/catch flags, hit/miss/false-alarm/correct-reject labels and reward volume.
