# Core environment

## Purpose

The core environment runs the research MVP without heavy external neuroscience dependencies.

Responsibilities:

- simulation;
- synthetic fixtures;
- normalized artifact consumption;
- baselines;
- hypothesis/reviewer scaffolding;
- experiment registry;
- tests.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Commands

```bash
make test
make run
make register
make verify
```

## Contract with data environments

The core environment reads normalized session artifacts:

```text
artifacts/datasets/<source>/<session_id>/session.json
```

It should not import AllenSDK or ONE directly.
