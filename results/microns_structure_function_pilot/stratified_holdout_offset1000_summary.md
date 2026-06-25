# MICRONS Stratified Structure-Function Analysis

- Scientific decision: `positive_stratified_structure_function_signal`
- Positive after FDR: `True`
- Units: `992`
- Synapses loaded: `2161`
- Connected edge pairs: `1926`
- Candidate pairs: `983072`
- Tested strata: `27`
- Statistical tests: `162`
- Confirmed positives: `30`

## Top Distance-Matched Tests

| Stratum | Metric | Connected | Distance delta | Distance q | Degree delta | Degree q | Confirmed |
|---|---|---:|---:|---:|---:|---:|---:|
| `all_pairs` | `readout_location` | `1926` | `0.0210337` | `0.00703644` | `0.0380016` | `0.00622454` | `True` |
| `same_coarse_cell_type` | `readout_location` | `1364` | `0.0206217` | `0.00703644` | `0.0374112` | `0.00622454` | `True` |
| `different_coarse_cell_type` | `readout_location` | `562` | `0.0234416` | `0.00703644` | `0.0398089` | `0.00622454` | `True` |
| `same_fine_cell_type` | `readout_location` | `656` | `0.0169436` | `0.00703644` | `0.0386118` | `0.00622454` | `True` |
| `same_readout_quadrant` | `aggregate_functional` | `948` | `0.154999` | `0.00703644` | `0.197485` | `0.00622454` | `True` |
| `same_readout_quadrant` | `readout_location` | `948` | `0.0072775` | `0.00703644` | `0.0106022` | `0.00622454` | `True` |
| `different_readout_quadrant` | `readout_location` | `978` | `0.0174226` | `0.00703644` | `0.0308354` | `0.00622454` | `True` |
| `both_high_reliability` | `readout_location` | `504` | `0.0265325` | `0.00703644` | `0.0441287` | `0.00622454` | `True` |
| `distance_tercile:0` | `readout_location` | `1610` | `0.0174175` | `0.00703644` | `0.0186018` | `0.00622454` | `True` |
| `distance_tercile:1` | `readout_location` | `277` | `0.0312268` | `0.00703644` | `0.0325415` | `0.00622454` | `True` |

## Interpretation

A stratified MICrONS effect is accepted only if it has positive random, distance-matched, and degree-matched deltas and survives FDR correction on the matched controls. Otherwise the result remains negative or exploratory and must not be used as a Q1 mechanistic claim.
