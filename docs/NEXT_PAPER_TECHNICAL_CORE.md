# Next paper technical core

Date: 2026-07-30

## Working title

Executable Claim Auditing for Neurocomputational Digital Model Validation

## Strongest contribution

The strongest contribution is not another mouse-brain benchmark. The defensible
contribution is an executable claim-auditing layer that binds manuscript wording,
model evidence, uncertainty, cost, and claim scope.

## What is already solid

- ClaimBench v2 provides a broad adversarial known-truth suite.
- Shortcut evaluators over-authorize unsupported claims.
- The non-compensatory claim gate blocks overclaiming in the current v2 suite.
- Sensitivity analysis exposes a non-trivial safe region and dangerous threshold
  regions. This is stronger than pretending the thresholds are universally
  robust.
- External causal controls show that the gate is not only a MICRONS/Sensorium
  artifact.
- The claim DSL and manuscript auditor convert claims into executable contracts.

## What is not yet strong enough

- SciFact, Tuebingen cause-effect pairs, and Sachs are registered but not fully
  integrated as executable local benchmarks.
- The uncertainty-aware gate currently uses deterministic local perturbations.
  It is useful as a conservative first layer, but it is not a full Bayesian or
  bootstrap uncertainty model.
- The cost-fidelity frontier uses transparent proxy costs. A Q1 paper should add
  measured wall-clock, memory, data volume, and possibly energy estimates.
- The manuscript auditor currently matches declared wording. A stronger version
  should extract claims from LaTeX/PDF and classify paraphrases.

## Novelty position

The novelty should be stated narrowly:

MouseBrainBench-ClaimAudit introduces an executable evidence-to-claim contract
for neurocomputational digital model studies. It separates prediction,
reproducibility, topology, direction, local structure-function association,
causality, digital-twin wording, uncertainty, and computational cost. The
framework audits whether a manuscript-level claim is supported, blocked, or
uncertain under the available artifacts.

## What not to claim

- Do not claim a complete mouse-brain digital twin.
- Do not claim causal evidence from MICRONS observational results.
- Do not claim Sensorium SOTA unless an official, comparable baseline is fully
  reproduced.
- Do not claim universal validity of thresholds.
- Do not claim automatic peer review.

## Required next additions for a stronger Q1 submission

1. Integrate one public external benchmark fully, preferably SciFact for
   scientific claim verification or Tuebingen for causal direction.
2. Replace proxy cost with measured runtime/memory/data-volume metrics.
3. Add paraphrase-level claim extraction from LaTeX/PDF.
4. Add bootstrap or Bayesian uncertainty for real MICRONS/Sensorium evidence.
5. Produce a paper-level claim audit table automatically from the final LaTeX.

## Decision

Proceed as a second-paper line only if at least one public external benchmark is
fully integrated and the manuscript auditor is used on the actual paper sources.
Without that, the work is a strong engineering extension but still vulnerable as
a standalone Q1 contribution.
