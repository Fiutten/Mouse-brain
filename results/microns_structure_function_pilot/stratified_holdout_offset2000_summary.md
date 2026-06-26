# MICRONS Stratified Structure-Function Analysis

- Scientific decision: `positive_stratified_structure_function_signal`
- Positive after FDR: `True`
- Units: `999`
- Synapses loaded: `2147`
- Connected edge pairs: `1922`
- Candidate pairs: `997002`
- Tested strata: `29`
- Statistical tests: `174`
- Confirmed positives: `25`

## Top Distance-Matched Tests

| Stratum | Metric | Connected | Distance delta | Distance q | Degree delta | Degree q | Confirmed |
|---|---|---:|---:|---:|---:|---:|---:|
| `all_pairs` | `direction` | `1922` | `0.0214406` | `0.00869131` | `0.0225489` | `0.00827744` | `True` |
| `all_pairs` | `readout_location` | `1922` | `0.0178845` | `0.00869131` | `0.0286419` | `0.00827744` | `True` |
| `same_coarse_cell_type` | `readout_location` | `1320` | `0.0172891` | `0.00869131` | `0.0285796` | `0.00827744` | `True` |
| `different_coarse_cell_type` | `readout_location` | `602` | `0.018984` | `0.00869131` | `0.0296365` | `0.00827744` | `True` |
| `same_fine_cell_type` | `readout_location` | `614` | `0.0168963` | `0.00869131` | `0.0314208` | `0.00827744` | `True` |
| `same_readout_quadrant` | `readout_location` | `836` | `0.00540431` | `0.00869131` | `0.00823112` | `0.00827744` | `True` |
| `different_readout_quadrant` | `readout_location` | `1086` | `0.015542` | `0.00869131` | `0.0218709` | `0.00827744` | `True` |
| `both_high_reliability` | `readout_location` | `539` | `0.0246669` | `0.00869131` | `0.0358108` | `0.00827744` | `True` |
| `distance_tercile:0` | `readout_location` | `1554` | `0.0158971` | `0.00869131` | `0.0173871` | `0.00827744` | `True` |
| `distance_tercile:1` | `readout_location` | `290` | `0.0228197` | `0.00869131` | `0.0185021` | `0.00827744` | `True` |

## Interpretation

A stratified MICrONS effect is accepted only if it has positive random, distance-matched, and degree-matched deltas and survives FDR correction on the matched controls. Otherwise the result remains negative or exploratory and must not be used as a Q1 mechanistic claim.
