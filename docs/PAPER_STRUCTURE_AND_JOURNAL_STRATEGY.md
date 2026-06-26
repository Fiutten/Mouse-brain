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

### Primary Realistic Target: PLOS Computational Biology

Fit:

- computational methods applied to biological systems;
- explicit neuroscience section;
- accepts Research, Methods, and Software articles;
- emphasizes reproducibility, data, code, and software availability;
- welcomes methods/software that provide biological insight.

Why it fits this manuscript:

- MouseBrainBench is not just software; it provides a methodological framework
  and real-data validation across MICRONS, Allen, and Sensorium;
- the strongest biological insight is local MICRONS structure-function
  association under matched controls;
- the framework blocks overclaiming from prediction alone, which is a
  meaningful computational-biology contribution.

Risk:

- the biological novelty must be explicit. A pure engineering paper will be too
  weak. The manuscript must foreground the MICRONS replicated result and the
  claim-audit logic.

Recommended article type:

- Methods, if the journal allows this route for benchmark frameworks;
- otherwise Research, with MouseBrainBench as the method and MICRONS as the
  central biological case.

### Ambitious Stretch Target: Nature Computational Science

Fit:

- multidisciplinary computational science;
- computational neuroscience explicitly in scope;
- interested in algorithms, tools, frameworks, mathematical models, and
  computational methods that advance scientific research.

Why it could fit:

- MouseBrainBench can be framed as a general computational framework for
  auditing partial digital-twin claims in neuroscience;
- the paper addresses a broader problem: predictive models, digital-twin
  language, and mechanistic claims are often conflated;
- the MICRONS result gives a concrete real-data demonstration.

Risk:

- current novelty may be judged too domain-specific or insufficiently broad
  unless we sharpen the general framework, package usability, and claim-audit
  contribution;
- the Sensorium official baseline remains non-Q1-qualified, so the paper should
  not be framed as a predictive-model benchmark competition.

Use this target only if the final manuscript clearly reads as a computational
science framework paper, not as a local analysis package.

### Safe Specialized Target: Neuroinformatics

Fit:

- data structures, software tools, modeling, integration, sharing, and
  independent evaluations of neuroscience databases/software;
- extremely aligned with MouseBrainBench as a neuroinformatics benchmark.

Why it fits:

- MouseBrainBench integrates public resources and evaluates claims across
  datasets;
- reproducibility, software, data provenance, and tool evaluation are central.

Risk:

- likely less strategic if the goal is a high-impact Q1-style venue;
- use as fallback if PLOS Computational Biology rejects on significance rather
  than correctness.

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
2. Use a neutral journal template first; avoid overfitting to one journal until
   the first full draft exists.
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
