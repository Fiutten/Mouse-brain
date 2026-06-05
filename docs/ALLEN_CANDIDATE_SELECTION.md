# Allen candidate session selection

Date: 3 June 2026

## Purpose

Select a realistic first Allen Visual Behavior Neuropixels session for Layer 1 real-data normalization.

This selection uses metadata only. It does not download NWB session files.

## Scientific constraint

We do not pretend to simulate the full mouse brain at cellular scale.

The first empirical digital-twin layer uses recorded Neuropixels units as anchors:

- recorded/sorted units;
- probes;
- channels;
- structure acronym coverage;
- behavioral session metadata.

This is scientifically more defensible than inventing artificial neuron counts.

## Selection method

Implemented in:

- `neurotwin_mvp/allen_selection.py`
- `scripts/select_allen_candidate_sessions.py`

Command:

```bash
make allen-select
```

Filters:

- `unit_count >= 1500`;
- `probe_count >= 4`;
- exclude abnormal histology/activity;
- require coverage of:
  - visual cortex;
  - visual thalamus;
  - hippocampus.

Ranking score:

```text
unit_count + 150 * probe_count + 400 * number_of_covered_model_regions
```

## Primary candidate

Top-ranked session:

```text
ecephys_session_id: 1087992708
behavior_session_id: 1088053452
mouse_id: 556014
session_type: EPHYS_1_images_H_3uL_reward
experience_level: Novel
image_set: H
unit_count: 3043
probe_count: 6
channel_count: 2304
```

Covered model regions:

- visual cortex;
- visual thalamus;
- hippocampus;
- basal ganglia;
- arousal/midbrain.

Relevant Allen structures include:

- visual cortex: `VISp`, `VISal`, `VISam`, `VISl`, `VISpm`, `VISrl`;
- visual thalamus: `APN`, `LP`, `TH`;
- hippocampus: `CA1`, `CA3`, `DG-mo`, `DG-po`, `DG-sg`, `HPF`, `POST`, `PRE`;
- basal ganglia: `SNr`;
- arousal/midbrain: `MRN`, `MB`, `NB`.

## Interpretation

This session is a strong candidate for the first real-data layer because it has:

- high unit count;
- full 6-probe recording;
- broad visual/thalamic/hippocampal/subcortical coverage;
- no abnormal histology/activity flags in metadata.

## Next step

Create a compatible AllenSDK environment with Python 3.10/3.11 and implement one-session normalization for `ecephys_session_id=1087992708`.

Target output:

```text
artifacts/datasets/allen/1087992708/session.json
```

Implementation status:

- exporter CLI implemented in `scripts/allen_export_session.py`;
- normalizer implemented in `neurotwin_mvp/allen_normalization.py`;
- tests use fake Allen session objects, so core verification does not require AllenSDK;
- real execution requires `.venv-allen`.
