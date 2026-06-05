# Dataset decision

## Current recommendation

Start with Allen Visual Behavior Neuropixels.

Rationale:

- It is directly aligned with visual behavior.
- AllenSDK provides a documented project cache.
- The dataset is packaged in NWB files with metadata tables for sessions, units, probes and channels.
- It is closer to the current synthetic fixture.

Use IBL as the second dataset if the Allen route works.

Rationale:

- IBL is stronger for brain-wide decision-making.
- It is more appropriate for claims about distributed choice, action and engagement.
- It likely adds more complexity in task/session handling, so it should not be the first integration unless Allen blocks us.

## Decision criteria

Choose Allen first if:

- we need a controlled visual behavior pipeline;
- visual thalamus/cortex/ganglia lesions are the first target;
- we want NWB/AllenSDK tooling.

Choose IBL first if:

- the primary claim is brain-wide decision-making;
- we need richer coverage across regions;
- we accept additional complexity in ONE/OpenAlyx integration.

## Next implementation target

Allen minimal real-data milestone:

1. Use direct S3 metadata backend for session discovery in the current Python 3.14 environment.
2. Select one ecephys session with adequate visual cortex/thalamus coverage.
3. Create a separate Python 3.10/3.11 scientific environment for AllenSDK if full NWB access is needed.
4. Instantiate `VisualBehaviorNeuropixelsProjectCache` in that compatible environment.
5. Implement one-session `Session` normalization:
   - trials;
   - stimulus sign or category;
   - choice/reward if available;
   - unit structure acronyms;
   - region-level spike-rate features.

## Current smoke-test status

The direct S3 metadata smoke test succeeded.

Result:

- `ecephys_sessions.csv` loaded;
- 153 ecephys sessions detected;
- metadata cached under `data/allen/project_metadata/ecephys_sessions.csv`.

AllenSDK installation is blocked in the current Python 3.14 environment because AllenSDK 2.16.2 depends on `numpy<1.24`, which is not a practical target for this interpreter.

## Candidate selection status

Implemented:

- `neurotwin_mvp/allen_selection.py`;
- `scripts/select_allen_candidate_sessions.py`;
- `make allen-select`.

The selector uses metadata only. It ranks sessions by:

- recorded/sorted unit count;
- probe count;
- coarse model-region coverage;
- quality flags.

It does not download NWB files.

## Go/no-go criteria

Proceed if:

- one session loads reproducibly;
- trial table and unit table can be joined or aligned;
- at least three coarse regions are represented;
- baseline behavior prediction runs.

Pivot if:

- dependency installation is unstable;
- data volume is too large for local iteration;
- session alignment consumes disproportionate time;
- IBL offers a cleaner first session for the exact target task.
