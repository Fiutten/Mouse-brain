# MICRONS Stratified Structure-Function Analysis

- Scientific decision: `positive_stratified_structure_function_signal`
- Positive after FDR: `True`
- Units: `1000`
- Synapses loaded: `2267`
- Connected edge pairs: `2095`
- Candidate pairs: `999000`
- Tested strata: `29`
- Statistical tests: `174`
- Confirmed positives: `28`

## Top Distance-Matched Tests

| Stratum | Metric | Connected | Distance delta | Distance q | Degree delta | Degree q | Confirmed |
|---|---|---:|---:|---:|---:|---:|---:|
| `all_pairs` | `readout_location` | `2095` | `0.0215146` | `0.00755766` | `0.040264` | `0.00526746` | `True` |
| `same_coarse_cell_type` | `readout_location` | `1392` | `0.020265` | `0.00755766` | `0.040006` | `0.00526746` | `True` |
| `different_coarse_cell_type` | `readout_location` | `703` | `0.0243546` | `0.00755766` | `0.0400662` | `0.00526746` | `True` |
| `same_fine_cell_type` | `readout_location` | `972` | `0.0187883` | `0.00755766` | `0.0389421` | `0.00526746` | `True` |
| `same_readout_quadrant` | `readout_location` | `984` | `0.00762759` | `0.00755766` | `0.0132138` | `0.00526746` | `True` |
| `different_readout_quadrant` | `readout_location` | `1111` | `0.0221826` | `0.00755766` | `0.0348251` | `0.00526746` | `True` |
| `both_high_reliability` | `readout_location` | `548` | `0.0252707` | `0.00755766` | `0.0441253` | `0.00526746` | `True` |
| `distance_tercile:0` | `readout_location` | `1898` | `0.0186005` | `0.00755766` | `0.0170678` | `0.00526746` | `True` |
| `distance_tercile:1` | `readout_location` | `133` | `0.0221643` | `0.00755766` | `0.0186593` | `0.00526746` | `True` |
| `distance_tercile:2` | `readout_location` | `64` | `0.0354881` | `0.00755766` | `0.0214332` | `0.0332859` | `True` |

## Interpretation

A stratified MICrONS effect is accepted only if it has positive random, distance-matched, and degree-matched deltas and survives FDR correction on the matched controls. Otherwise the result remains negative or exploratory and must not be used as a Q1 mechanistic claim.
