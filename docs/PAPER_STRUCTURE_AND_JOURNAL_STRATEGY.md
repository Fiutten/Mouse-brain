# MouseBrainBench Paper Structure and Journal Strategy

## Working Title

MouseBrainBench: a reproducible claim-audit benchmark for partial mouse-brain
digital models

## Core Position

The paper must not claim a complete mouse-brain digital twin. The defensible
claim is narrower and stronger:

MouseBrainBench is a reproducible benchmark framework that separates predictive
performance, reproducibility, anatomical plausibility, structure-function
association, and mechanistic identifiability in partial mouse-brain digital
models.

The main empirical result is the replicated MICRONS local structure-function
case. Allen VBN, Sensorium, Dynamic Sensorium, and synthetic experiments are
supporting audit layers, not competing main claims.

## Recommended Journal Strategy

### Primary Target: Engineering Applications of Artificial Intelligence

Fit:

- JCR category aligned with Computer Science, Artificial Intelligence;
- practical verification and validation of AI-based software is in scope;
- public datasets and reproducible benchmarking are explicitly valued;
- complex networks, neural models, and engineering case studies are supported.

Why it fits this manuscript:

- the AI contribution is a claim-aware validation architecture with
  non-interchangeable evidence blocks and executable claim gates;
- the engineering application is verification of partial neural digital models;
- validation spans synthetic truth, Allen, Sensorium, Dynamic Sensorium, and
  MICRONS;
- the software and result artifacts provide traceability and reproducibility.

Risk:

- the manuscript will be desk-rejected if MIS appears to be only an ad hoc set
  of thresholds or if the AI contribution is not explicit;
- computational neuroscience must be framed as the engineering application,
  while the reusable contribution is verification and validation of AI models;
- the abstract must state both contributions separately.

Recommended article type:

- Original Research Article using Elsevier CAS single-column format;
- double-anonymized manuscript plus a separate title page.

### Ambitious Alternative: Information Sciences

Fit:

- JCR categories aligned with Artificial Intelligence and Information Systems;
- intelligent systems, software tools, computational biology, and brain mapping
  are explicitly in scope;
- balanced theoretical and practical contributions are expected.

Why it could fit:

- the non-compensatory evidence model can be generalized beyond neuroscience;
- the formal claim contract and provenance architecture fit intelligent
  information systems;
- the multi-resource experiments provide a substantive validation case.

Risk:

- current validation remains domain-specific;
- a submission would require additional non-neuroscience evidence or stronger
  theory to justify general information-science significance.

Use this target only after demonstrating that the framework transfers beyond
mouse-brain datasets.

### Thematic Alternative: Neurocomputing

Fit:

- explicitly covers neural computation, biological neural network modelling,
  neurobiology, AI, and software environments;
- the domain fit is stronger than EAAI, while the professional category remains
  Computer Science, Artificial Intelligence.

Why it fits:

- the benchmark evaluates neural predictive and digital models;
- model comparison, software, and mechanistic interpretation fit the journal.

Risk:

- reviewers may expect a new neural model or learning algorithm rather than a
  validation framework;
- use as the second submission route if EAAI rejects the engineering framing.

## Proposed Manuscript Structure

### 1. Abstract

Four-message abstract:

1. Public mouse-brain resources are powerful but fragmented, and digital-twin
   claims are easy to overstate.
2. MouseBrainBench introduces a reproducible claim-audit framework separating
   prediction, reliability, anatomical controls, structure-function association,
   and mechanistic identifiability.
3. Across Allen VBN, Sensorium/Dynamic Sensorium, synthetic cases, and MICRONS,
   the framework blocks weak claims and identifies one robust positive result:
   replicated MICRONS local structure-function association.
4. The contribution is a benchmark for partial digital models, not a complete
   mouse-brain simulation.

### 2. Introduction

Key narrative:

- Digital-brain and digital-twin terminology is accelerating faster than
  validation standards.
- Public mouse-brain resources already cover complementary scales: functional
  activity, mesoscopic/behavioral recordings, predictive visual datasets, and
  local EM/function coregistration.
- Existing tools are powerful but fragmented; a lightweight benchmark is needed
  to decide what level of claim is justified.
- MouseBrainBench provides that benchmark.

Claims to avoid:

- no complete brain;
- no consciousness;
- no causal mechanism from observational MICRONS alone;
- no Sensorium SOTA.

### 3. Related Work

Subsections:

- Mouse-brain resources and digital-brain initiatives.
- MICRONS and local structure-function data.
- Allen Visual Behavior Neuropixels and reproducible neural signatures.
- Sensorium/Dynamic Sensorium and predictive visual neuroscience benchmarks.
- BMTK/SONATA/TVB and why MouseBrainBench does not reimplement simulators.
- Digital-twin validation and mechanistic identifiability.

Purpose:

This section must show we are not reinventing BMTK, TVB, Sensorium, Allen, or
MICRONS. The novelty is claim auditing across resources.

### 4. MouseBrainBench Framework

Subsections:

- Data adapters and provenance.
- Graph and region abstractions.
- Prediction/reliability layer.
- Anatomical and perturbation controls.
- Mechanistic Identifiability Score.
- Claim gates and blocked claims.
- Reproducibility package.

Central figure:

System diagram showing datasets entering independent evidence gates and ending
in allowed/blocked claims.

### 5. Datasets and Roles

Use a table:

| Dataset | Scale | Role | Claim status |
|---|---|---|---|
| Synthetic MIS | controlled truth | validates scoring logic | method sanity check |
| Allen VBN | 20-21 analyzed sessions | negative mechanistic control | reproducible but not identifiable |
| Sensorium static | 7 validation mice, 5 repeated-test mice | predictive/reliability auxiliary case | predictive, not causal |
| Dynamic Sensorium | 5 current + 5 OOD mice | temporal predictive stress test | predictive, underpowered for central claim |
| MICRONS CAVE | 2991 units, 6575 synapses, 5943 connected pairs | main empirical evidence | replicated local structure-function |

### 6. Results

Recommended order:

1. Synthetic MIS validates the gate logic.
2. Allen VBN demonstrates that reproducibility alone does not imply mechanism.
3. Sensorium static/dynamic show prediction can improve while MIS remains
   incomplete.
4. MICRONS global aggregate test fails distance matching, preventing an
   overclaim.
5. MICRONS stratified endpoint replicates across three cohorts.
6. Claim audit freezes allowed and blocked interpretations.

Main result to highlight:

`all_pairs/readout_location` in MICRONS:

- discovery: 1000 units, 2267 synapses, 2095 connected pairs;
- hold-out offset1000: 992 units, 2161 synapses, 1926 connected pairs;
- hold-out offset2000: 999 units, 2147 synapses, 1922 connected pairs;
- unit-cluster bootstrap lower bounds positive in all cohorts.

### 7. Discussion

Core discussion points:

- The framework is valuable because it says "no" to unsupported claims.
- MICRONS provides a positive local structure-function result, but not causal
  mechanism.
- Sensorium demonstrates predictive benchmarking, but official/SOTA claims
  remain blocked.
- Allen demonstrates why reproducibility without topology/directionality is
  insufficient.
- MouseBrainBench can support future larger digital-brain integrations without
  pretending to be one.

### 8. Limitations

Required limitations:

- observational MICRONS cannot establish causality;
- MICRONS volume is local, not whole brain;
- Sensorium official baseline is bounded local training, not leaderboard-level;
- Allen analysis is currently a negative-control subset, not exhaustive use of
  all available sessions;
- no behavioral digital-twin claim;
- no consciousness claim.

### 9. Methods

Subsections:

- Software environment and versioning.
- Dataset provenance.
- Synthetic MIS benchmark.
- Allen VBN analysis.
- Sensorium static analysis.
- Dynamic Sensorium baselines.
- Official bounded Sensorium baseline.
- MICRONS CAVE querying and cohort definition.
- Matched nulls: random, distance, degree.
- FDR correction.
- Unit-cluster bootstrap.
- Claim-freeze logic.

### 10. Code and Data Availability

State:

- source code hosted on GitHub;
- raw public datasets are not redistributed;
- scripts reproduce data acquisition where licenses/APIs allow;
- generated result artifacts are versioned;
- CAVE access may require token and accepted terms;
- all claims are linked to tracked benchmark artifacts.

## Figure Plan

1. Framework overview and claim gates.
2. Dataset-role map across evidence layers.
3. Allen negative mechanistic-identifiability result.
4. Sensorium predictive controls and bounded official baseline.
5. MICRONS cohort design and matched nulls.
6. MICRONS replicated primary endpoint with bootstrap intervals.
7. Claim audit: allowed vs blocked claims.

## Immediate Writing Plan

1. Create an Overleaf project named `MouseBrainBench`.
2. Use the official Elsevier CAS single-column template required for the EAAI
   submission route.
3. Draft in this order:
   - Methods;
   - Results;
   - Introduction;
   - Discussion;
   - Abstract last.
4. Keep a strict claim table in the manuscript from the first draft.

## Overleaf Setup

Recommended:

- create a blank Overleaf project;
- enable Git access if available;
- add me the Git URL or provide the exported project zip;
- I will create the LaTeX skeleton locally under `paper/` and synchronize it.

If Overleaf Git is not available, we can still write the manuscript in the
repository and upload a zip to Overleaf manually.
