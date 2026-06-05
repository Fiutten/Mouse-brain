# Allen environment

## Purpose

The Allen environment is responsible for AllenSDK/NWB-specific work only.

Responsibilities:

- install AllenSDK;
- read Visual Behavior Neuropixels metadata;
- load selected NWB sessions;
- map units to coarse regions;
- compute region-level trial features;
- export normalized `session.json` artifacts.

## Recommended Python

Use Python 3.10 or 3.11.

Do not use the current Python 3.14 environment for AllenSDK. AllenSDK 2.16.2 depends on `numpy<1.24`, which is not a practical target for Python 3.14.

## Actual setup used in this workspace

```bash
tools/miniforge3/bin/conda create -y -p .venv-allen python=3.11 pip
.venv-allen/bin/pip install "allensdk==2.16.2"
.venv-allen/bin/pip install "hdmf<4"
.venv-allen/bin/pip install -e .
```

AllenSDK 2.16.2 installed `pynwb 2.8.3`. The initial resolver selected
`hdmf 6.0.2`, which is incompatible in this stack and produced an NWB
construction error. Pinning `hdmf<4` installed `hdmf 3.14.6` and fixed the
import/load path.

## Output contract

Allen scripts must write:

```text
artifacts/datasets/allen/<ecephys_session_id>/session.json
```

This file must match the `Session`/`Trial` contract in `neurotwin_mvp.data`.

## Export selected candidate

Once AllenSDK is available in `.venv-allen`, run:

```bash
.venv-allen/bin/python scripts/allen_export_session.py \
  --ecephys-session-id 1087992708 \
  --behavior-session-id 1088053452 \
  --animal-id 556014 \
  --out artifacts/datasets/allen/1087992708
```

This command downloads/loads one NWB session through AllenSDK and writes:

```text
artifacts/datasets/allen/1087992708/session.json
```

The default neural feature window is `0.0s` to `0.250s` after trial start. This is a first engineering default and must be reviewed scientifically once the real trial tables are inspected.

If the NWB file already exists under `data/allen`, the script loads it directly
with `BehaviorEcephysSession.from_nwb_path(...)` and does not require S3 access.

## Current status

- Direct S3 metadata smoke test succeeded in the core environment.
- AllenSDK full environment exists in `.venv-allen`.
- NWB-to-Session normalizer is implemented and tested with fake Allen session objects.
- Real NWB execution succeeded for session `1087992708` with `--max-trials 100`.
- Exported artifact: `artifacts/datasets/allen/1087992708/session.json`.
