# Q1 MICRONS Volume Adequacy and Stopping Rule

## Purpose

This document fixes the current MICRONS evidence volume before manuscript
drafting. Its role is to prevent open-ended exploratory cohort mining after the
primary endpoint has been selected.

## Included Cohorts

All cohorts use CAVE `minnie65_public`,
`digital_twin_properties_bcm_coreg_v4`, materialization version `1507`.

| Cohort | Unit offset | Units | Synapses | Connected edge pairs | Candidate directed pairs |
|---|---:|---:|---:|---:|---:|
| Discovery | 0 | 1000 | 2267 | 2095 | 999000 |
| Hold-out offset1000 | 1000 | 992 | 2161 | 1926 | 983072 |
| Hold-out offset2000 | 2000 | 999 | 2147 | 1922 | 997002 |
| Total | - | 2991 | 6575 | 5943 | 2979074 |

## Primary Endpoint

The primary endpoint is fixed as:

```text
all_pairs / readout_location
```

The endpoint is accepted only if it is positive after distance matching, degree
matching, FDR correction, and unit-cluster bootstrap stability in all three
cohorts.

## Current Decision

The current evidence is sufficient for a Q1-candidate local structure-function
benchmark claim:

- the primary endpoint is positive in discovery and both hold-outs;
- distance-matched and degree-matched deltas remain positive in all cohorts;
- 300-sample unit-cluster bootstrap intervals have positive lower bounds in all
  cohorts and both matched-control families.

## Stopping Rule

No additional MICRONS CAVE cohorts should be used to redefine the primary
endpoint, metric family, stratification, or acceptance rule. Additional MICRONS
downloads are allowed only as explicitly labelled confirmatory robustness
checks, reviewer-requested extensions, or independent replication material.

The manuscript claim must remain local and observational. These data do not
support causal mechanism, whole-brain mouse digital-twin, behavioral digital
twin, or Sensorium-SOTA claims.

## Citation Note

The CAVE table owner notice requests citation of Wang et al. 2025,
Ding/Fahey/Papadopoulos et al. 2025, and MICRONS Consortium et al. 2025.
