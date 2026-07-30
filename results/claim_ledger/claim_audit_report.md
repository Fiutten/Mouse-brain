# Claim Audit Report

- Decision: `claim_ledger_supported`
- Supported claims: `6/6`

## Ledger

| Claim ID | Status | Evidence | Permitted wording |
|---|---|---|---|
| `allen-negative-identifiability` | `supported` | `results/allen_vbn_mechanistic_identifiability_score.json` | Allen VBN is a real negative mechanistic-identifiability case. |
| `sensorium-predictive-interoperability` | `supported` | `results/sensorium_official_baseline_audit/summary.json` | Sensorium/Dynamic Sensorium are predictive and interoperability cases. |
| `dynamic-sensorium-predictive-only` | `supported` | `results/dynamic_sensorium_model_comparator/summary.json` | Dynamic Sensorium is used as a temporal predictive case. |
| `microns-local-structure-function` | `supported` | `results/microns_primary_robustness/summary.json` | MICRONS supports a local observational structure-function case at the fixed endpoint. |
| `claim-gate-blocks-overclaiming` | `supported` | `results/claim_adversarial_benchmark/summary.json` | The non-compensatory gate blocks broad adversarial overclaims. |
| `attack-suite-known-limits` | `supported` | `results/claim_attack_suite/summary.json` | The current release passes known attack checks with declared limits. |

## Blocked Wording

### `allen-negative-identifiability`
- Allen VBN validates a mechanistic brain model.
- Reproducibility alone establishes mechanism.

### `sensorium-predictive-interoperability`
- Sensorium proves mechanistic identifiability.
- MouseBrainBench is a Sensorium SOTA model.

### `dynamic-sensorium-predictive-only`
- Dynamic Sensorium validates causal mechanism.
- Temporal prediction establishes a digital twin.

### `microns-local-structure-function`
- MICRONS proves causality in this study.
- MICRONS validates a whole-brain mouse digital twin.

### `claim-gate-blocks-overclaiming`
- The gate is universally optimal.
- The adversarial suite proves biological truth.

### `attack-suite-known-limits`
- All external Q1 pieces are fully solved.
- There are no remaining methodological limitations.
