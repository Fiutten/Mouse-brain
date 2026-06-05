# Allen metadata smoke test

Date: 3 June 2026

## Objective

Validate access to Allen Visual Behavior Neuropixels metadata without downloading full NWB session files.

## Official access paths

Allen documents two relevant access paths:

- AllenSDK `VisualBehaviorNeuropixelsProjectCache`;
- direct public S3 access to metadata and data files.

The project currently supports both at the contract level:

- `make allen-smoke`: AllenSDK backend;
- `make allen-smoke-s3`: direct S3 metadata backend.

## Result

The direct S3 metadata backend succeeded.

Command:

```bash
.venv/bin/python scripts/allen_metadata_smoke_test.py --backend direct-s3
```

Output summary:

```text
source: direct_s3
n_ecephys_sessions: 153
metadata: data/allen/project_metadata/ecephys_sessions.csv
```

Detected columns:

- `ecephys_session_id`
- `behavior_session_id`
- `date_of_acquisition`
- `equipment_name`
- `session_type`
- `mouse_id`
- `genotype`
- `sex`
- `project_code`
- `age_in_days`
- `unit_count`
- `probe_count`
- `channel_count`
- `structure_acronyms`
- `image_set`
- `prior_exposures_to_image_set`
- `session_number`
- `experience_level`
- `prior_exposures_to_omissions`
- `file_id`
- `abnormal_histology`
- `abnormal_activity`

## AllenSDK issue

Attempting to install AllenSDK in the current Python 3.14 virtual environment failed.

Observed cause:

- AllenSDK 2.16.2 depends on `numpy<1.24`;
- on Python 3.14 this resolves to a source build path rather than a compatible wheel;
- installation fails before AllenSDK can be used.

Interpretation:

The current Python 3.14 environment is suitable for the standard-library MVP, but not suitable as the main AllenSDK environment.

## Decision

For metadata discovery, use the direct S3 backend.

For full NWB/session normalization, create a separate scientific environment with a compatible Python version, ideally Python 3.10 or 3.11, then install AllenSDK there.

## Next technical step

Use the downloaded `ecephys_sessions.csv` to select candidate sessions by:

- `unit_count`;
- `probe_count`;
- `structure_acronyms`;
- `abnormal_histology`;
- `abnormal_activity`;
- `session_type`;
- visual-region coverage.

Then implement a candidate selection script before downloading any full session NWB files.
