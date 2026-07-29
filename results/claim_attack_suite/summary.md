# Claim Attack Suite

- Decision: `claim_attack_suite_passed_with_known_limits`
- Risks: `1`

## Risks

| Level | Item | Evidence | Action |
|---|---|---|---|
| `medium` | `sensorium_not_q1_qualified` | official Sensorium baseline is not Q1-qualified locally | Keep Sensorium as predictive/interoperability evidence, not SOTA. |

## Allowed Claims

- MouseBrainBench separates prediction, OOD, reliability, and mechanistic gates.
- Allen VBN is a real negative case: reproducible but not mechanistically identifiable.
- Sensorium/Dynamic Sensorium provide modern predictive cases with local NN control.
- Sensorium static provides partial positive reliability/topographic evidence.
- The official Sensorium stack can run local forward-pass and bounded training/evaluation artifacts.
- MICrONS now provides a real CAVE-backed micro-pilot, but current structure-function signal is negative/inconclusive.
- MICrONS expanded pilot reaches Q1-scale data volume, but current distance-controlled structure-function result is not positive.
- MICrONS stratified analysis finds a local structure-function signal after distance/degree/FDR controls, dominated by readout-location similarity.
- MICrONS hold-out analyses internally reproduce the readout-location signal in two non-overlapping windows from the same resource.
- MICRONS primary endpoint survives combined distance/degree matching and within-distance readout shuffling.

## Blocked Claims

- A complete digital twin of mouse brain.
- A SOTA Sensorium predictor.
- A Q1-qualified official Sensorium baseline until the published budget/configuration or official checkpoint is evaluated.
- Causal mechanistic identifiability in Dynamic Sensorium.
- MICrONS causal mechanism claims: the stratified signal is correlational and local, not interventional.
- Whole-brain or causal MICrONS claims: the internally reproduced signal remains local, observational, and confined to one resource.
