# Architecture

## Objective

Build a falsifiable, modular prototype for a knowledge-guided regional functional digital twin of mouse visual decision-making.

The system is separated into three graphs:

1. Neuroanatomical graph: regions, connections and dynamics.
2. Knowledge graph: claims, evidence, papers, functions and datasets.
3. Workflow graph: agents, experiment execution, review and reporting.

This separation is mandatory. The LLM/agent layer must not be treated as a biological component of the simulated brain.

## Current MVP

The current implementation is Level 0:

- continuous regional state model;
- synthetic visual decision trial;
- synthetic Neuropixels-like session fixture;
- optional real-data adapter contracts;
- behavioral baselines;
- local experiment registry;
- normalized artifact exchange between Python environments;
- virtual lesions;
- deterministic hypothesis and reviewer agents;
- minimal evidence graph;
- no external dependencies.

## Modules

### `config.py`

Loads and validates JSON model configuration.

### `artifacts.py`

Defines the normalized `Session` artifact contract used to integrate multiple Python environments.

The core environment consumes `session.json` artifacts. Allen/IBL-specific environments should produce them after extracting and normalizing external data.

### `regional_model.py`

Implements continuous state dynamics:

- directed regional coupling;
- external sensory input;
- lesions;
- decision readout.

This is a scaffold, not a biological claim.

### `experiments.py`

Runs visual decision probes and lesion sweeps.

Primary metric:

- sensitivity = action probability under positive stimulus minus action probability under negative stimulus.

Virtual lesions are counterfactual architecture probes. They clamp a region to zero and ignore its outgoing influence during a trial. Their purpose is to test whether the model's regional structure matters. They are not clinical lesion models and are not biological evidence until validated against empirical perturbation results.

### `knowledge.py`

Stores evidence and graph relations. This will later become a richer knowledge graph backed by curated papers and datasets.

### `agents.py`

Deterministic MVP agents:

- `HypothesisAgent`;
- `ReviewerAgent`.

External LLM calls should be added only after the deterministic workflow is testable.

### `workflow.py`

Orchestrates:

1. seed knowledge graph;
2. propose hypotheses;
3. review hypotheses;
4. load synthetic data fixture;
5. run behavioral baselines;
6. run lesion sweep;
7. return auditable report.

### `registry.py`

Persists workflow outputs under `artifacts/experiments/`.

The registry stores run metadata, a configuration snapshot, a configuration hash and the JSON workflow report. It is a lightweight reproducibility layer, not a full experiment tracking platform.

### `data.py`

Defines the session interface and a synthetic Neuropixels-like fixture.

The fixture is used only to test pipeline mechanics. It is not evidence and must be replaced by Allen/IBL data for scientific claims.

### `datasets/`

Contains optional adapters for real datasets:

- Allen Visual Behavior Neuropixels through AllenSDK.
- IBL brain-wide map through ONE/OpenAlyx.

These adapters currently define dependency checks and normalization plans. Full NWB/ONE conversion to the internal `Session` contract is the next implementation step.

### `baselines.py`

Defines minimal behavioral baselines. These are deliberately simple and will be expanded before any publication-oriented experiment.

## Directory layout

- `configs/`: versioned model and dataset configuration.
- `data/`: local dataset caches. Large data are not versioned.
- `artifacts/experiments/`: registered runs with manifest, report and config snapshot.
- `artifacts/datasets/`: normalized dataset/session artifacts exchanged between environments.
- `artifacts/reports/`: generated reports and paper-facing artifacts.

## Near-term design constraints

- Every new biological detail must improve a metric or explain a phenomenon.
- Every hypothesis must define an intervention, expected effect and metric.
- Every claim about a brain region must eventually be linked to evidence.
- Consciousness claims are out of scope.
- Baselines must be added before increasing model complexity.

## Code transparency policy

The codebase should remain understandable to an external reviewer.

Required conventions:

- each module explains its role and scientific limits;
- public dataclasses/classes/functions have docstrings;
- comments clarify design intent, not obvious Python syntax;
- synthetic fixtures are marked as engineering scaffolds, not evidence;
- real-data adapters must fail explicitly while incomplete;
- virtual lesions must be documented as counterfactual probes, not clinical simulations.
