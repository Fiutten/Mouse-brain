# Allen export status

## Goal

Increase the number of normalized Allen Visual Behavior Neuropixels sessions so
multi-session validation becomes scientifically meaningful.

## Current checkpoint

Checkpoint date: 2026-06-06.

The latest controlled expansion reached 45 normalized Allen sessions after a
5-session target-aware selector trial. The previous 40-session checkpoint had
25 usable `go_response` sessions; the selector-prioritized batch added 5
normalized sessions, 4 of which are usable for the strict `go_response` cohort.
This is operationally encouraging, but it is not yet statistical proof that the
selector generalizes. The empirical usable-session rate still makes clear that
"50 downloads" and "50 usable target sessions" are not equivalent.

| metric | value |
| --- | ---: |
| normalized/exported sessions | 45 |
| usable `go_response` sessions | 29 |
| non-usable `go_response` sessions | 16 |
| total labeled trials | 12311 |
| labeled `go_response` trials | 10767 |
| raw Allen cache size after selector trial | 88 GB |
| normalized Allen artifacts size | 27 MB |
| free disk after selector trial | 665 GiB |
| pruned raw NWB files | 15 |
| storage freed by pruning | 46.34 GiB |
| partially downloaded next session | none |
| partial bytes for next session | 0 |

The previous next-session partial download is now complete. Future interrupted
downloads remain recoverable because the batch exporter uses `curl -C -`, so a
later run resumes instead of restarting the NWB transfer.

Latest broad evidence status over all 45 normalized sessions:

| statistic | value |
| --- | ---: |
| total valid trials | 12311 |
| mean multi-split neural gain | 0.021 |
| mean permutation observed gain | 0.030 |
| positive multi-split fraction | 0.578 |
| significant permutation fraction | 0.467 |
| formal decision | `inconclusive_mixed_evidence` |

This remains exploratory. It is useful evidence for system behavior and target
selection, but it is not a publication-grade positive claim.

Latest behavioral-target diagnostics:

| target | usable sessions | labeled trials | interpretation |
| --- | ---: | ---: | --- |
| `choice` | 39/45 | 12311 | high-coverage continuity baseline |
| `go_response` | 29/45 | 10767 | strict primary task-native target candidate |
| `catch_response` | 0/45 | 1544 | systematically underpowered/imbalanced |
| `rewarded` | 40/45 | 12311 | useful but outcome-derived control |
| `response_made` | 39/45 | 12311 | broad action/no-action control |
| `task_success` | 30/45 | 12311 | correctness target; outcome-confounded |

## Initial 15-session checkpoint

| ecephys session | status |
| --- | --- |
| 1053709239 | exported, benchmarked and diagnosed |
| 1064415305 | exported, benchmarked and diagnosed |
| 1065449881 | exported, benchmarked and diagnosed |
| 1087720624 | exported, benchmarked and diagnosed |
| 1087992708 | exported, benchmarked and diagnosed |
| 1090800639 | exported, benchmarked and diagnosed |
| 1090803859 | exported, benchmarked and diagnosed |
| 1091039902 | exported, benchmarked and diagnosed |
| 1092283837 | exported, benchmarked and diagnosed |
| 1093638203 | exported, benchmarked and diagnosed |
| 1093864136 | exported, benchmarked and diagnosed |
| 1096620314 | exported, benchmarked and diagnosed |
| 1098119201 | exported, benchmarked and diagnosed |
| 1111013640 | exported, benchmarked and diagnosed |
| 1119946360 | exported, benchmarked and diagnosed |

## Initial evidence status

The initial broad all-valid-trials evidence synthesis used 15 normalized sessions and
4005 valid behavior trials.

| statistic | value |
| --- | ---: |
| sessions | 15 |
| total valid trials | 4005 |
| mean multi-split neural gain | 0.008 |
| mean permutation observed gain | 0.031 |
| formal decision | negative_or_null_trend |

This is not positive evidence. The broad cohort remains a diagnostic control,
not the publication target.

## Initial behavioral-target status

The behavioral-target diagnostics run over all normalized Allen sessions. This
is required because the Allen task is not a simple balanced binary-choice
dataset.

| target | usable sessions | labeled trials | interpretation |
| --- | ---: | ---: | --- |
| `choice` | 12/15 | 4005 | useful continuity baseline |
| `go_response` | 10/15 | 3507 | primary task-native target candidate |
| `catch_response` | 0/15 | 498 | scientifically interesting but underpowered |
| `rewarded` | 12/15 | 4005 | useful control, partly outcome-derived |
| `response_made` | 12/15 | 4005 | broader action/no-action control; weaker evidence screen |
| `task_success` | 10/15 | 4005 | correctness target; outcome-confounded control |

The strict usable-session `go_response` cohort is now large enough to run the
predefined 10-session evidence check:

| statistic | value |
| --- | ---: |
| usable sessions | 10 |
| target-labeled trials across normalized sessions | 3507 |
| strict evidence trials | 2332 |
| final permutations | 500 |
| mean multi-split gain | 0.034 |
| mean permutation observed gain | 0.056 |
| positive multi-split fraction | 0.700 |
| significant permutation fraction | 0.300 |
| formal decision | inconclusive_mixed_evidence |

This is the strongest current signal, but it is still not sufficient for a
positive claim because the effect is not consistent across sessions.

`response_made` was screened because it reaches 12/15 usable sessions. Its
exploratory 50-permutation report returns `negative_or_null_trend`, so higher
coverage alone does not make it a better primary target.

## Target-driven export automation

`scripts/export_until_target_evidence.py` coordinates the target-specific export
workflow:

1. refresh behavioral-target diagnostics;
2. count usable sessions for the requested target;
3. export one pending Allen session at a time;
4. refresh diagnostics after each export;
5. stop when the target reaches the requested usable-session threshold or the
   maximum new-session budget is exhausted;
6. rebuild strict target-specific reports with the requested permutation count;
7. write `artifacts/reports/allen_targets/target_evidence_status.json`.

The latest run used:

```bash
.venv/bin/python scripts/export_until_target_evidence.py \
  --target-name go_response \
  --target-usable-sessions 10 \
  --max-new-sessions 12 \
  --candidate-limit 25 \
  --screening-permutations 50 \
  --final-permutations 500
```

It exported 9 additional sessions after the initial state and reached the target
at 10 usable `go_response` sessions.

The latest 50-session expansion checkpoint used:

```bash
.venv/bin/python scripts/export_until_target_evidence.py \
  --target-name go_response \
  --target-usable-sessions 50 \
  --max-new-sessions 63 \
  --candidate-limit 80 \
  --screening-permutations 20 \
  --final-permutations 200 \
  --min-free-gb 120
```

It was first stopped manually after reaching 39 normalized sessions and 24
usable `go_response` sessions. The next pending NWB (`1048196054`) was then
resumed in a controlled single-session batch and completed, giving the current
40-session checkpoint with 25 usable `go_response` sessions. This remains a
methodological checkpoint, not a data failure: the observed `go_response`
usable rate implies that reaching 50 usable sessions likely requires
substantially more than 50 downloads unless candidate selection becomes
target-aware.

## Batch export automation

`scripts/export_allen_sessions_batch.py` provides a controlled multi-session
export workflow:

1. rank candidate sessions from metadata;
2. skip sessions that already have `session.json`;
3. download or resume each NWB through `curl -C -`;
4. export through the Allen-specific Python environment;
5. refresh audit, benchmark, multi-split and permutation reports;
6. refresh `artifacts/reports/allen/evidence_report.json`;
7. refresh `artifacts/reports/allen/target_diagnostics.json`;
8. write `artifacts/reports/allen/export_batch_status.json`.

The downloader handles retries outside `curl` and invokes a fresh `curl -C -`
process for each attempt. This avoids an observed failure mode where internal
`curl --retry` restarted the partial NWB transfer instead of preserving
progress.

Useful commands:

```bash
make allen-export-batch-plan
make allen-export-selector-batch-plan
make allen-export-batch
make allen-evidence
make allen-targets
make allen-go-evidence-until-10
make allen-target-aware-select
make allen-prune-cache-plan
```

## Scientific status

Multi-session analysis infrastructure now runs on 45 fully normalized sessions,
with 29 usable sessions for the strict `go_response` target. This is a stronger
engineering and scientific base than the initial 15-session checkpoint, but the
formal result remains `inconclusive_mixed_evidence`. The immediate next step is
not to claim success; it is to build a target-aware session selector, stratify
usable/non-usable sessions, and run heavier evidence only on cohorts with
defensible behavioral balance.

The first target-aware selector is implemented in
`scripts/select_allen_target_aware_sessions.py`. At the 40-session checkpoint it
ranked 20 pending candidates from the top 80 metadata candidates; the top-ranked
candidate was `1122903357`. The first 5-session selector trial exported all 5
selected sessions and yielded 4/5 usable `go_response` sessions. After
regeneration at the 45-session checkpoint, the top-ranked pending candidate is
`1065905010`. This ranking should be regenerated after each batch.

The current best scientific signal is not the broad all-trials evidence report;
it is the expanded strict `go_response` temporal analysis. Over 29 usable
sessions, the `pre_response` window has mean gain 0.149, positive-gain fraction
0.655, confirmed 500-permutation significant fraction 0.552 and a bootstrap CI95 of 0.089
to 0.211. It passes baseline/stimulus window controls, but deterministic audit
agents still block strong mechanistic claims because regional effects are
heterogeneous, the latent baseline remains negative on average and the
microcircuit validation is only partially aligned.

The current fragility audit identifies 9 fragile sessions among the 29 usable
`go_response` sessions: 6 global temporal-null cases and 3 weak or
non-significant temporal-effect cases. This is now the main scientific obstacle
to stronger claims.

Expanded heterogeneity analysis shows that 21/29 usable sessions have
state-dependent support. Three of the 9 fragile sessions recover support in
specific chronological blocks, while six remain persistent null/weak cases.
Alternative windows rescue five fragile sessions, but three are decision-window
rescues with possible motor contamination. The completed 500-permutation
confirmation preserves the original mean gain 0.149 and significant fraction
0.552. Leave-one-animal-out mean gain remains positive in every case
(minimum 0.128).

Raw cache pruning is implemented in `scripts/prune_allen_nwb_cache.py`. The
2026-06-06 cleanup deleted only raw NWB files for the 15 sessions documented as
non-usable for `go_response`; all normalized artifacts remain available for
audit and reanalysis. The cleanup reduced `data/allen` from 121 GB to 75 GB and
increased free disk from 632 GiB to 679 GiB. The later selector trial increased
the raw cache to 88 GB and left 665 GiB free.
