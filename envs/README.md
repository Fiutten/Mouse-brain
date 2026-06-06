# Environment strategy

The project is designed to use multiple Python environments when scientific dependencies are incompatible.

This is intentional. Integration is achieved through normalized artifacts, not by forcing every dependency into one Python runtime.

## Environments

### Core environment: `.venv`

Purpose:

- regional simulation;
- baselines;
- workflow orchestration;
- experiment registry;
- tests;
- artifact reading/writing.

Current Python:

- Python 3.14.

Status:

- working;
- 113 tests passing;
- no heavy scientific dependencies required.

### Allen environment: `.venv-allen`

Purpose:

- AllenSDK;
- NWB access;
- session extraction;
- unit/spike/trial normalization;
- export to normalized artifacts.

Recommended Python:

- Python 3.10 or 3.11.

Current status:

- isolated environment creation attempted on 2026-06-06;
- blocked by corrupt cached Conda Python/setuptools packages;
- ONE is not installed and no IBL data have been downloaded.

Reason:

- AllenSDK 2.16.2 depends on older scientific packages, including `numpy<1.24`;
- this is not compatible with the current Python 3.14 environment.

### IBL environment: `.venv-ibl`

Purpose:

- ONE/OpenAlyx data access;
- IBL session extraction;
- export to normalized artifacts.

Recommended Python:

- Python 3.10 or 3.11.

## Integration principle

Environments do not import each other.

They communicate through normalized artifacts:

```text
artifacts/datasets/<source>/<session_id>/
  session.json
```

The external data environment produces `session.json`.

The core environment consumes `session.json`.

## Example flow

Allen environment:

```bash
source .venv-allen/bin/activate
python scripts/allen_export_session.py --session-id <id> --out artifacts/datasets/allen/<id>
```

Core environment:

```bash
source .venv/bin/activate
python scripts/run_registered_experiment.py --session artifacts/datasets/allen/<id>
```

The Allen exporter and NWB-derived state/anatomy sidecar exporter are
implemented. The IBL exporter remains a guarded adapter contract only.
