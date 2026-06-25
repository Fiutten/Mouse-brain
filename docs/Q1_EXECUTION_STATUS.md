# Q1 Execution Status

## Current Bottom Line

MouseBrainBench now has Q1-candidate evidence, but it is not submission-ready:
the positive MICRONS signal is stratified, local, and still needs replication.

The most important result is now the expanded MICrONS pilot plus its
stratified follow-up:

- 1000 co-registered digital-twin/EM units;
- 2267 CAVE synapses;
- 2095 unique directed connected pairs;
- Q1-scale pilot gate: passed;
- global positive structure-function result: failed;
- stratified structure-function result: positive after distance/degree/FDR
  controls, dominated by `readout_location`.

In the global aggregate test, connected pairs are more functionally similar than a random null, and more
similar than a degree-matched null, but the effect does not survive the
distance-matched null. Therefore, the aggregate result remains a stress test,
while the stratified result provides the current Q1-candidate signal.

The stratified result changes the Q1 situation from "blocked by evidence" to
"candidate evidence requiring replication". It is not yet submission-ready Q1
evidence because the strongest effect is local and correlational rather than
causal or interventional.

## Step Status

| Step | Status | Result |
|---|---|---|
| Expand MICrONS with CAVE | Done | `digital_twin_properties_bcm_coreg_v4`, v1507, 1000 units |
| Add structure-function model | Done | Synapse count/size, random, distance, degree controls |
| Add stronger nulls | Done | Distance and degree matched permutation tests |
| Scale Sensorium on Mac GPU | Done | MPS works; small official model improves over tiny but remains far below MLP |
| Publication decision table | Done | Q1 candidate requires MICRONS replication; methodological paper remains viable |

## Key Results

| Evidence block | Scale | Result | Q1 use |
|---|---:|---|---|
| MICrONS static micro-pilot | 172 units, 82 synapses | Negative/inconclusive | Stress test only |
| MICrONS expanded pilot | 1000 units, 2267 synapses | Positive vs random/degree, not distance | Not enough for positive Q1 claim |
| MICrONS stratified expanded pilot | 1000 units, 2267 synapses | 28 tests positive after FDR, mostly readout-location | Q1 candidate only after replication |
| Sensorium official tiny | 5 mice | Runs on MPS, weak correlation | Integration evidence |
| Sensorium official small | 5 mice | Improves over tiny, far below MLP | Still not official/SOTA |
| Dynamic Sensorium MLP | 5 mice | Stronger prediction | Predictive baseline, not mechanistic |

## Next Q1-Capable Moves

1. Replicate the MICrONS stratified readout-location signal on a larger or
   held-out CAVE subset.
2. Keep the global MICrONS result negative unless the all-pairs distance-matched
   effect turns positive.
3. Treat non-readout functional positives as exploratory unless they replicate.
4. Obtain or train a stronger official Sensorium baseline. The current local
   official models are integration controls, not competitive baselines.
5. Frame the paper around the central methodological claim: MouseBrainBench
   prevents predictive success from being over-interpreted as mechanistic
   identifiability.

## Critical Interpretation

The project is not failing; it is doing what a serious benchmark should do. It
has already rejected weak mechanistic claims that would be tempting to overstate.
For Q1, however, we still need:

- replication of the positive MICRONS stratified signal on held-out/larger data;
  or
- an official/SOTA Sensorium result whose predictive success is analyzed through
  MIS and robustness gates.
