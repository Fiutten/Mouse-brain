# ClaimBench v2 Unified Report

- Decision: `claimbench_v2_methodological_package_ready`
- Criteria: `9/9` passed

## Criteria

| Criterion | Passed | Evidence | Interpretation |
|---|---:|---|---|
| `synthetic_known_truth_gate` | `True` | cases=144; claim_gate_fp=0 | The internal gate blocks unsupported known-truth overclaims. |
| `threshold_limits_reported` | `True` | safe=108; dangerous=135 | Thresholds have safe regions, but dangerous regions must be reported. |
| `uncertainty_blocks_unsupported_support` | `True` | unsupported_supported=0; supported_uncertain=25 | Uncertainty is conservative and does not turn unsupported claims into support. |
| `scifact_external_claim_control` | `True` | claims=300; bm25_recall_at_5=0.898936170212766; shortcut_ORI=0.19886363636363635 | SciFact supports an external claim-auditing case, not SOTA verification. |
| `tuebingen_causal_overclaim_control` | `True` | pairs=108; direction_accuracy=0.4854368932038835; corr_overclaims=79 | Tuebingen supports causal overclaim auditing, not causal-discovery performance. |
| `manuscript_claim_audit` | `True` | inputs=3; active_hits=0 | The current manuscript wording passes executable claim-boundary checks. |
| `component_ablation_nonredundancy` | `True` | components=8; high_or_critical=7 | Core components are non-redundant because ablations reintroduce risks. |
| `reviewer_attack_suite` | `True` | risks=1 | Reviewer attacks pass with explicit reportable limits. |
| `clean_release` | `True` | missing=[]; dirty=[]; failing=[] | The tracked artifact package is internally reproducible. |

## Publishable Claim Boundary

ClaimBench v2 is a claim-aware auditing framework that separates prediction, evidence retrieval, causal direction, uncertainty, manuscript wording, and release reproducibility. It is not a SciFact SOTA system and not a causal-discovery performance method.
