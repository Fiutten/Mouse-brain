# Technical review

Date: 3 June 2026

## Scope

This review evaluates the current software architecture and implementation quality of the Neurotwin MVP.

The review does not validate scientific claims. It validates whether the current system is a sound software base for a future scientific prototype.

## Architecture verdict

The current architecture is acceptable for an early research MVP.

Strengths:

- Clear separation between model, data, experiments, knowledge graph, agents and workflow.
- Synthetic fixture is explicitly separated from scientific evidence.
- Real dataset adapters are isolated under `datasets/`.
- Optional dependencies are not imported by the core package.
- Tests cover core behavior and validation boundaries.
- The workflow is auditable: hypotheses, reviewer output, baselines and lesions are all visible.

Weaknesses:

- The regional model is not trainable yet.
- The synthetic fixture encodes the expected causal structure, so it cannot be used as evidence.
- The knowledge graph is a minimal in-memory structure, not a curated evidence system.
- The agent layer is deterministic and useful only as a workflow scaffold.
- Real Allen/IBL normalization is not implemented yet.

Conclusion:

The design is good enough to proceed to real-data integration, but not yet good enough to make scientific claims.

## System design validation

### Correct separation of responsibilities

The system distinguishes:

- `regional_model.py`: simulated regional dynamics.
- `data.py`: normalized session contract and synthetic fixture.
- `datasets/`: optional real-data adapters.
- `experiments.py`: lesion and decision experiments.
- `baselines.py`: baseline behavioral models.
- `knowledge.py`: evidence graph.
- `agents.py`: hypothesis and reviewer scaffolding.
- `workflow.py`: orchestration.

This is the right structure. It avoids mixing LLM/agent logic into the brain simulation, which would be conceptually weak.

### Simulation design

The Level-0 model is intentionally simple:

- continuous state nodes;
- directed weighted coupling;
- external input;
- lesion masking;
- decision readout.

This is appropriate as a falsifiable first level. It is not biologically detailed, but that is the correct choice at this stage. More detail before real data would create unidentifiable parameters.

Virtual lesions are used only as counterfactual probes. They test whether disabling a model region changes behavior in a pre-specified direction. They should be interpreted as architecture diagnostics until linked to empirical perturbation evidence.

### Data design

The `Session` and `Trial` contracts are sufficient for the first real-data milestone:

- stimulus;
- choice;
- reward;
- latency;
- engagement;
- region-level rates.

The contract will need expansion once real Allen/IBL data are loaded:

- trial start/end times;
- stimulus metadata;
- unit counts per region;
- spike-rate windows;
- session quality metadata;
- region acronym mapping;
- missing-data handling.

### Agent design

The deterministic agent MVP is appropriate. It prevents premature dependency on LLM APIs and gives us a testable workflow first.

Future LLM integration should be constrained to:

- evidence extraction;
- hypothesis generation;
- reviewer checks;
- experiment planning.

It should not be treated as part of the simulated brain.

## Issues found and fixed

### 1. `dt` existed but was unused

Risk:

- configuration parameter looked meaningful but had no effect.

Fix:

- `RegionalModel.step` now uses `effective_decay = region.decay * config.dt`, clipped to `[0, 1]`.

### 2. Unknown lesion/input regions were silently accepted

Risk:

- integration bugs could produce invalid experiments without failing.

Fix:

- `RegionalModel` now validates external input and lesion region names.

### 3. Invalid experiment parameters were not rejected

Risk:

- `repeats=0`, negative delay or zero decision steps could fail indirectly or produce invalid outputs.

Fix:

- explicit validation added in `run_trial` and `evaluate_visual_decision`.

### 4. Synthetic loader allowed invalid trial counts

Risk:

- empty or degenerate train/test splits.

Fix:

- `SyntheticNeuropixelsLoader` now requires `n_trials > 1`.

### 5. Baseline evaluation did not guard empty test sets

Risk:

- division by zero.

Fix:

- `evaluate_classifier` now rejects empty test trials.

### 6. Workflow was tightly coupled to synthetic data

Risk:

- future real-data loaders would require changing workflow internals.

Fix:

- `run_workflow` now accepts an optional `SessionLoader`.

## Current verification

Command:

```bash
.venv/bin/python scripts/verify.py
```

Result:

```text
Ran 19 tests
OK
```

Verified components:

- config loading;
- regional dynamics;
- lesion effects;
- data fixture;
- train/test split;
- baselines;
- workflow report;
- dataset adapter contracts;
- validation errors.

## Optimization assessment

The current code does not need performance optimization yet.

Reasons:

- model size is tiny;
- standard-library implementation is intentional;
- no real data arrays are loaded yet;
- bottlenecks will appear in spike aggregation and training, not in this MVP.

Premature optimization would be counterproductive.

The useful optimization work now is architectural:

- keep dependency boundaries clean;
- make real-data normalization explicit;
- add baselines before model complexity;
- preserve testability.

## Required next improvements

### P0 code transparency

- Keep public APIs documented with docstrings.
- Keep scientific limitations close to the code that implements the behavior.
- Avoid unexplained biological terms in code/config.
- Add comments when a modeling choice is a hypothesis rather than established fact.

### P0 before scientific claims

- Implement real Allen metadata loading.
- Define region acronym mapping.
- Define spike-rate extraction windows.
- Add real train/test split protocol.
- Add leakage checks.
- Add baseline reports on real data.

### P1 before architecture expansion

- Add trainable regional model.
- Add non-biological baseline with comparable parameter count.
- Add statistical confidence intervals.
- Add experiment registry.

### P2 before publication

- Curate literature graph.
- Validate lesion expectations against literature or perturbation data.
- Add reproducibility metadata: seeds, dataset versions, config hashes.
- Add result serialization.

## Blocking risks

1. Real data may not align cleanly with current coarse regions.
2. Behavioral variables may differ between Allen and IBL.
3. A simple baseline may outperform the regional model.
4. Lesion outputs may be plausible but empirically unvalidated.
5. The project can still drift into overclaiming if consciousness language returns.

## Final assessment

The codebase is now a reasonable professional research MVP.

It is not yet a scientific result. It is a controlled scaffold that can support the next decisive step: real-data integration.

The next technical milestone should be a metadata-only Allen loader smoke test, followed by one-session normalization into `Session`.
