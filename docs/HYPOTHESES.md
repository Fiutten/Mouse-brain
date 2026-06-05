# Hypothesis Registry

This file tracks hypotheses before implementation. Each hypothesis must include an intervention, expected effect, metric and evidence status.

## Note on virtual lesions

Virtual lesions are in-silico counterfactual probes. They are used to test whether the model architecture behaves coherently when a region or connection is disabled.

They are not clinical lesion simulations and do not prove biological causality by themselves. A lesion hypothesis becomes scientifically defensible only when it is linked to literature, perturbation data or real dataset evidence.

## H1: Visual thalamus lesion reduces stimulus sensitivity

Intervention:

- Set `visual_thalamus` state to zero during trial.

Expected effect:

- Lower difference between action probability for positive and negative visual stimulus.

Metric:

- `sensitivity = p(action | positive stimulus) - p(action | negative stimulus)`.

Evidence status:

- Plausible; must be linked to Allen/visual decision literature in the curated graph.

## H2: Basal ganglia lesion compresses action selection

Intervention:

- Set `basal_ganglia` state to zero during trial.

Expected effect:

- Reduced ability of integrated sensory state to drive action probability away from indifference.

Metric:

- sensitivity;
- action entropy;
- decision latency once implemented.

Evidence status:

- Plausible; must be linked to action-selection literature.

## H3: Arousal perturbation changes variability more than visual sensitivity

Intervention:

- Modify or lesion `arousal` gain.

Expected effect:

- Increased variability and altered engagement/latency rather than pure visual deficit.

Metric:

- trial-to-trial probability variance;
- latency;
- engagement proxy once real data is integrated.

Evidence status:

- Plausible; not yet tested in MVP.
