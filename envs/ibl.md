# IBL environment

## Purpose

The IBL environment is reserved for ONE/OpenAlyx access and conversion of
selected IBL sessions into the shared normalized artifact contract.

It must remain isolated from `.venv-allen`; installing ONE into the Allen
environment would make the working Allen dependency stack harder to reproduce.

## Intended setup

```bash
tools/miniforge3/bin/conda create -y -p .venv-ibl python=3.11 pip
.venv-ibl/bin/pip install "ONE-api"
.venv-ibl/bin/pip install -e .
```

## Current status

Environment creation was attempted on 2026-06-06. Conda failed during package
verification because cached Python 3.11 and setuptools packages were corrupt.
No ONE package was installed, no IBL data were downloaded and `.venv-allen`
was not modified.

The next attempt must repair or replace the local Conda package cache before
installing ONE.

## Scientific guardrail

The frozen external-replication design is documented in
`docs/EXTERNAL_REPLICATION_PROTOCOL.md`. Metadata access or adapter
availability must not be described as replication.
