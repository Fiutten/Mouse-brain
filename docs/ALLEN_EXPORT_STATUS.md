# Allen export status

## Goal

Increase the number of normalized Allen Visual Behavior Neuropixels sessions so
multi-session validation becomes scientifically meaningful.

## Current checkpoint

Checkpoint date: 2026-06-06.

The latest controlled expansion reached 40 normalized Allen sessions. The
previous partial NWB download (`1048196054`) was resumed successfully and added
one usable `go_response` session. The empirical usable-session rate still makes
clear that "50 downloads" and "50 usable target sessions" are not equivalent.

| metric | value |
| --- | ---: |
| normalized/exported sessions | 40 |
| usable `go_response` sessions | 25 |
| non-usable `go_response` sessions | 15 |
| total labeled trials | 11096 |
| labeled `go_response` trials | 9705 |
| raw Allen cache size | 121 GB |
| normalized Allen artifacts size | 24 MB |
| free disk after checkpoint | 632 GiB |
| partially downloaded next session | none |
| partial bytes for next session | 0 |

The previous next-session partial download is now complete. Future interrupted
downloads remain recoverable because the batch exporter uses `curl -C -`, so a
later run resumes instead of restarting the NWB transfer.

Latest broad evidence status over all 40 normalized sessions:

| statistic | value |
| --- | ---: |
| total valid trials | 11096 |
| mean multi-split neural gain | 0.023 |
| mean permutation observed gain | 0.031 |
| positive multi-split fraction | 0.564 |
| significant permutation fraction | 0.462 |
| formal decision | `inconclusive_mixed_evidence` |

This remains exploratory. It is useful evidence for system behavior and target
selection, but it is not a publication-grade positive claim.

Latest behavioral-target diagnostics:

| target | usable sessions | labeled trials | interpretation |
| --- | ---: | ---: | --- |
| `choice` | 34/40 | 11096 | high-coverage continuity baseline |
| `go_response` | 25/40 | 9705 | strict primary task-native target candidate |
| `catch_response` | 0/40 | 1391 | systematically underpowered/imbalanced |
| `rewarded` | 35/40 | 11096 | useful but outcome-derived control |
| `response_made` | 34/40 | 11096 | broad action/no-action control |
| `task_success` | 26/40 | 11096 | correctness target; outcome-confounded |

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
make allen-export-batch
make allen-evidence
make allen-targets
make allen-go-evidence-until-10
make allen-target-aware-select
```

## Scientific status

Multi-session analysis infrastructure now runs on 40 fully normalized sessions,
with 25 usable sessions for the strict `go_response` target. This is a stronger
engineering and scientific base than the initial 15-session checkpoint, but the
formal result remains `inconclusive_mixed_evidence`. The immediate next step is
not to claim success; it is to build a target-aware session selector, stratify
usable/non-usable sessions, and run heavier evidence only on cohorts with
defensible behavioral balance.

The first target-aware selector is implemented in
`scripts/select_allen_target_aware_sessions.py`. At the 40-session checkpoint it
ranks 20 pending candidates from the top 80 metadata candidates; the top-ranked
candidate is `1122903357`. This ranking should be used to prioritize the next
downloads, then regenerated after each batch.
