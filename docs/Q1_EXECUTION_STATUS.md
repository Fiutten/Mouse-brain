# Q1 Execution Status

## Current Bottom Line

MouseBrainBench is now technically stronger than before, but the Q1 claim is
still blocked by evidence, not by infrastructure.

The most important result is the expanded MICrONS pilot:

- 1000 co-registered digital-twin/EM units;
- 2267 CAVE synapses;
- 2095 unique directed connected pairs;
- Q1-scale pilot gate: passed;
- positive structure-function result: failed.

Connected pairs are more functionally similar than a random null, and more
similar than a degree-matched null, but the effect does not survive the
distance-matched null. Therefore, the current result supports a methodological
paper and a strong negative/stress-test discussion, but it does not support a
Q1 claim that local synaptic structure explains function in this subset.

## Step Status

| Step | Status | Result |
|---|---|---|
| Expand MICrONS with CAVE | Done | `digital_twin_properties_bcm_coreg_v4`, v1507, 1000 units |
| Add structure-function model | Done | Synapse count/size, random, distance, degree controls |
| Add stronger nulls | Done | Distance and degree matched permutation tests |
| Scale Sensorium on Mac GPU | Done | MPS works; small official model improves over tiny but remains far below MLP |
| Publication decision table | Done | Q1 remains blocked; methodological paper remains viable |

## Key Results

| Evidence block | Scale | Result | Q1 use |
|---|---:|---|---|
| MICrONS static micro-pilot | 172 units, 82 synapses | Negative/inconclusive | Stress test only |
| MICrONS expanded pilot | 1000 units, 2267 synapses | Positive vs random/degree, not distance | Not enough for positive Q1 claim |
| Sensorium official tiny | 5 mice | Runs on MPS, weak correlation | Integration evidence |
| Sensorium official small | 5 mice | Improves over tiny, far below MLP | Still not official/SOTA |
| Dynamic Sensorium MLP | 5 mice | Stronger prediction | Predictive baseline, not mechanistic |

## Next Q1-Capable Moves

1. Expand MICrONS beyond the first 1000 units and repeat the distance-controlled
   test. The current effect may be local-distance dominated.
2. Stratify MICrONS by area, readout location, cell type, and reliability. A
   global all-pairs test may dilute a real effect that is specific to cell class
   or visual area.
3. Replace the single aggregate functional similarity with task-specific
   measures: orientation similarity, direction similarity, readout-location
   similarity, and response-performance similarity.
4. Obtain or train a stronger official Sensorium baseline. The current local
   official models are integration controls, not competitive baselines.
5. Frame the paper around the central methodological claim: MouseBrainBench
   prevents predictive success from being over-interpreted as mechanistic
   identifiability.

## Critical Interpretation

The project is not failing; it is doing what a serious benchmark should do. It
has already rejected weak mechanistic claims that would be tempting to overstate.
For Q1, however, we still need either:

- a positive MICrONS result that survives spatial/type/degree controls; or
- an official/SOTA Sensorium result whose predictive success is analyzed through
  MIS and robustness gates.
