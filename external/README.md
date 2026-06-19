# External Official Sources

This directory is intentionally not used for vendored dependencies in Git.

The official Sensorium integration smoke test expects two downloaded source
trees:

- `external/sensorium_2023`
- `external/neuralpredictors_43fa`

Recreate them with:

```bash
scripts/setup_sensorium_official_env.sh
```

The downloaded source trees are excluded from Git to avoid vendoring third-party
code. The tracked artifact is the smoke-test output in:

```text
results/sensorium_official_baseline_audit/official_model_smoke.json
```
