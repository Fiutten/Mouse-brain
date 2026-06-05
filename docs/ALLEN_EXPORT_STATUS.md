# Allen export status

## Goal

Increase the number of normalized Allen Visual Behavior Neuropixels sessions so
multi-session validation becomes scientifically meaningful.

## Current normalized sessions

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

## Current evidence status

The broad all-valid-trials evidence synthesis uses 15 normalized sessions and
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

## Behavioral-target status

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
make allen-export-batch
make allen-evidence
make allen-targets
make allen-go-evidence-until-10
```

## Scientific status

Multi-session analysis infrastructure now runs on 15 fully normalized sessions,
with 10 usable sessions for the strict `go_response` target. This is a real
evidence base for iteration, but the formal result remains
`inconclusive_mixed_evidence`, so the next step is target/feature redesign and
stability analysis rather than a positive publication claim.
