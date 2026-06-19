# MICrONS Structure-Function Pilot Status

## Current State

The project now has a reproducible MICrONS small-pilot path, but the pilot is
not approved yet.

Downloaded small static files:

- functional EM co-registration:
  `func_unit_em_match_release.csv`;
- proofreading status:
  `proofreading_status_public_release.csv`;
- digital twin v2 functional/anatomical unit properties:
  `dt_anatomy_units.csv`, `dt_performance_units.csv`,
  `dt_ori_dir_tuning_units.csv`.

Generated artifacts:

- `results/microns_pilot_gate/static_pilot_diagnostic.json`;
- `results/microns_pilot_gate/summary.json`;
- local ignored cache under `data/microns/static_small/`.

Rebuild command:

```bash
scripts/download_microns_static_small.sh
.venv/bin/python scripts/build_microns_static_pilot_manifest.py
.venv/bin/python scripts/query_microns_cave_pilot_edges.py
.venv/bin/python -m mousebrainbench.benchmarks.microns_pilot_gate
```

## Result

The static subset provides:

- 200 co-registered EM/function rows;
- 172 rows with usable functional properties;
- spatial coordinates;
- functional metrics from the digital twin property export;
- root IDs for candidate EM objects.

It does not provide:

- true synaptic edges among the matched units.

The current gate therefore returns:

```text
defer_microns_pilot_manifest_insufficient
```

## Why It Is Blocked

A defensible structure-function pilot requires real structural edges. The small
static files do not include those edges. The full static minnie65 synapse graph
is approximately 47.5 GB, which violates the bounded-pilot rule. The correct
small route is CAVE:

```bash
.venv/bin/python scripts/query_microns_cave_pilot_edges.py
```

That script calls:

```python
client.materialize.synapse_query(pre_ids=roots, post_ids=roots)
```

Current environment result:

```text
AuthException: CAVE token missing for minnie65_public
```

## Approval Rule

The MICrONS pilot becomes approved only when the manifest has:

- at least 500 neurons;
- spatial coordinates;
- functional responses/properties;
- real structural edges;
- estimated download size no greater than 5 GB.

The current static subset fails on neuron count and structural edges. This is a
scientific block, not a software bug.
