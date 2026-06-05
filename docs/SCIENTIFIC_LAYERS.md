# Scientific layers

## Current principle

The project should become more biologically detailed only when the data support that detail.

We should not invent full-brain neuron counts to make the model look realistic. A credible digital twin must be anchored to measured data, known anatomy and explicit assumptions.

## Implemented / designed layers

### Layer 0: regional functional scaffold

Status: implemented.

What it represents:

- coarse brain regions as dynamical nodes;
- directed coupling;
- sensory input;
- decision readout;
- virtual lesion probes.

Scientific level:

- engineering scaffold;
- not a calibrated biological model.

### Layer 1: empirical Neuropixels session selection

Status: implemented.

What it represents:

- real Allen Visual Behavior Neuropixels sessions;
- recorded/sorted unit counts;
- probe counts;
- structure acronym coverage;
- quality flags.

Current result:

- 153 ecephys sessions in metadata;
- candidate selection implemented;
- selected real session `1087992708`;
- 3,043 sorted units, 6 probes and 2,304 channels in the selected session.

Scientific level:

- real data selection;
- not yet neural activity normalization.

### Layer 2: normalized real session artifact

Status: implemented for the first Allen session.

What it will represent:

- one real Allen session converted to `Session`;
- trials;
- behavior;
- region-level neural features;
- region mapping from Allen acronyms to model regions.

Current result:

- `artifacts/datasets/allen/1087992708/session.json`;
- 100 normalized trials in the first exported artifact;
- five coarse regions represented: arousal/midbrain, basal ganglia,
  hippocampus, visual cortex and visual thalamus;
- unit anatomy inferred through `peak_channel_id -> structure_acronym`.

Scientific caveat:

- the current stimulus encoding is a deterministic pipeline placeholder, not a
  final visual-task representation.

### Layer 3: controlled temporal-regional evidence

Status: implemented as an empirical predictive layer.

What it should represent:

- target-specific temporal neural features;
- task/image/history baselines;
- permutation tests;
- cross-session uncertainty;
- negative window controls;
- latency-stratified fragility checks.

Current result:

- strict Allen `go_response` cohort has 10 usable sessions;
- `pre_response` temporal gain mean is 0.143 with CI95 [0.047, 0.243];
- negative window controls pass against baseline and stimulus windows;
- latency strata remain heterogeneous, especially in the fast stratum;
- advanced stability matrix: 4 robust, 3 mixed and 3 fragile sessions.

Scientific caveat:

- this is controlled predictive evidence, not causal mechanism.

### Layer 4: empirical functional graph and scientific-agent audit

Status: implemented as an initial graph/agent layer.

What it represents:

- coarse regions, temporal windows and behavioral targets as graph nodes;
- predictive region-window-target relations as weighted edges;
- deterministic audit rules that prevent unsupported claims;
- reproducible reports under `make allen-stabilize`.

Current result:

- `window:pre_response -> target:go_response` weight 0.143;
- `region:visual_cortex -> window:pre_response` weight 0.059;
- `region:basal_ganglia -> window:pre_response` weight 0.037;
- graph evidence registry marks all three edges as `controlled`;
- advanced scientific-agent decision: `advance_to_microcircuit_design`.

Scientific caveat:

- the graph is not an anatomical connectome;
- the agent is deterministic scaffolding for future LLM/LangGraph workflows,
  not autonomous scientific reasoning.

### Layer 5: calibrated generative surrogate

Status: implemented as a session-level surrogate.

What it represents:

- synthetic session-level evidence sampled from empirical temporal-gain and
  regional-drop summaries;
- a stress-test target for graph, audit and orchestration layers;
- a stepping stone toward richer generative models.

Current result:

- empirical temporal gain mean 0.143;
- generated temporal gain mean 0.152 over 10 generated sessions;
- regional generated means preserve the empirical ordering;
- generator v2 produces normalized trial-level sessions with 500 trials,
  temporal region-window metadata and calibrated latency/target summaries.

Scientific caveat:

- this is not a spike-train simulator, microcircuit model or whole-brain
  digital twin;
- empirical reports remain the only source of biological evidence.

### Layer 5b: latent temporal representation baseline

Status: implemented as a negative/diagnostic baseline.

What it represents:

- PCA temporal latents over region-window features;
- held-out behavior prediction against a compact behavioral baseline;
- held-out reconstruction error and explained variance.

Current result:

- mean latent gain -0.107;
- positive latent-gain fraction 0.200;
- mean explained variance fraction 0.857.

Scientific caveat:

- the current PCA baseline reconstructs variance but does not usually improve
  behavior prediction;
- this blocks strong claims about latent representation learning until failure
  modes are understood.

### Layer 6: selected microcircuits

Status: implemented as a first selected microcircuit scaffold.

What it should represent:

- thalamocortical visual pathway;
- basal-ganglia action selection;
- hippocampal/context module if required by task.

Initial scope:

- design only around controlled graph edges;
- prioritize robust sessions `1091039902`, `1093864136`, `1096620314` and
  `1119946360`;
- keep latent representation claims separate until PCA/stronger latent
  baselines become positive under controls.

Current result:

- selected visual-cortex / basal-ganglia pre-response scaffold calibrated from
  the four robust sessions;
- intact mean action probability 0.590;
- visual-excitation perturbation drop 0.020;
- basal-gate perturbation drop 0.009;
- visual-inhibition suppression changes probability by -0.003.

Scientific caveat:

- perturbation effects are directionally useful but modest;
- this remains a hypothesis-prioritization scaffold, not causal biological
  perturbation evidence.

## Note on neuron counts

A mouse brain has tens of millions of neurons. Simulating that number directly is not the current goal and would not automatically make the model a better digital twin.

The first empirical layer should use recorded Neuropixels units as anchors. The model may later introduce latent populations or scaling factors, but those must be explicitly justified and tested.

For the current Allen Visual Behavior Neuropixels route, the realistic first quantity is:

- number of recorded units in a selected session;
- number of probes/channels;
- number of represented structures;
- trial count and behavior coverage once NWB is normalized.

The next scientific step is therefore not "add more artificial neurons". It is:

> select the best real session, normalize its trials and recorded-unit activity, and calibrate the regional model against those empirical features.
