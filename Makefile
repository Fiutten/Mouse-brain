PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help venv install test run register export-synthetic allen-smoke allen-smoke-s3 allen-select allen-target-aware-select allen-export-candidate allen-export-batch-plan allen-export-batch allen-evidence allen-targets allen-go-evidence-until-10 allen-session-relations allen-regional-ablation allen-temporal-reexport allen-temporal-windows allen-temporal-permutation allen-temporal-permutation-confirm allen-temporal-regional-ablation allen-uncertainty allen-response-controls allen-functional-graph allen-generative-surrogate allen-scientific-agent allen-study-manifest allen-stability-matrix allen-latent-temporal allen-graph-evidence-registry allen-session-generator-v2 allen-advanced-scientific-agent allen-selected-microcircuit allen-microcircuit-validation allen-advanced-evidence allen-stabilize verify clean

help:
	@echo "Targets:"
	@echo "  make venv     Create local virtual environment"
	@echo "  make install  Install package in editable mode"
	@echo "  make test     Run unit tests"
	@echo "  make run      Run prototype workflow"
	@echo "  make register Run workflow and persist experiment artifact"
	@echo "  make export-synthetic Export synthetic session artifact"
	@echo "  make allen-smoke Run Allen metadata-only smoke test"
	@echo "  make allen-smoke-s3 Run Allen direct-S3 metadata smoke test"
	@echo "  make allen-select Select candidate Allen sessions from metadata"
	@echo "  make allen-target-aware-select Rank pending Allen sessions using target evidence"
	@echo "  make allen-export-candidate Export selected Allen session (requires .venv-allen)"
	@echo "  make allen-export-batch-plan Plan resumable Allen batch export"
	@echo "  make allen-export-batch Export next pending Allen session"
	@echo "  make allen-evidence Synthesize current Allen evidence"
	@echo "  make allen-targets Diagnose Allen behavioral targets"
	@echo "  make allen-go-evidence-until-10 Export until 10 usable go_response sessions"
	@echo "  make allen-session-relations Explain usable vs non-usable Allen sessions"
	@echo "  make allen-regional-ablation Run go_response regional feature ablation"
	@echo "  make allen-temporal-reexport Re-export usable go_response sessions with temporal windows"
	@echo "  make allen-temporal-windows Run go_response temporal-window benchmark"
	@echo "  make allen-temporal-permutation Run pre_response temporal permutation screen"
	@echo "  make allen-temporal-permutation-confirm Run 500-permutation pre_response confirmation"
	@echo "  make allen-temporal-regional-ablation Run significant pre_response region ablation"
	@echo "  make allen-uncertainty Estimate cross-session uncertainty"
	@echo "  make allen-response-controls Run response-window and latency controls"
	@echo "  make allen-functional-graph Build empirical functional graph"
	@echo "  make allen-generative-surrogate Run calibrated generative surrogate"
	@echo "  make allen-scientific-agent Run deterministic scientific audit agent"
	@echo "  make allen-study-manifest Register reproducibility manifest"
	@echo "  make allen-stability-matrix Build session x control stability matrix"
	@echo "  make allen-latent-temporal Run PCA latent temporal baseline"
	@echo "  make allen-graph-evidence-registry Register graph-edge evidence states"
	@echo "  make allen-session-generator-v2 Generate calibrated synthetic session artifact"
	@echo "  make allen-advanced-scientific-agent Run advanced deterministic audit"
	@echo "  make allen-selected-microcircuit Run selected controlled-edge microcircuit"
	@echo "  make allen-microcircuit-validation Validate microcircuit against session stability"
	@echo "  make allen-advanced-evidence Run full advanced evidence pipeline"
	@echo "  make allen-stabilize Run current Allen evidence stabilization pipeline"
	@echo "  make verify   Run install, tests and prototype"
	@echo "  make clean    Remove generated caches"

venv:
	python3 -m venv .venv

install:
	$(PIP) install -e .

test:
	$(PYTHON) -m unittest discover -s tests

run:
	$(PYTHON) run_prototype.py

register:
	$(PYTHON) scripts/run_registered_experiment.py

export-synthetic:
	$(PYTHON) scripts/export_synthetic_session_artifact.py

allen-smoke:
	$(PYTHON) scripts/allen_metadata_smoke_test.py

allen-smoke-s3:
	$(PYTHON) scripts/allen_metadata_smoke_test.py --backend direct-s3

allen-select:
	$(PYTHON) scripts/select_allen_candidate_sessions.py

allen-target-aware-select:
	$(PYTHON) scripts/select_allen_target_aware_sessions.py

allen-export-candidate:
	$(PYTHON) scripts/allen_export_session.py --ecephys-session-id 1087992708 --behavior-session-id 1088053452 --animal-id 556014 --out artifacts/datasets/allen/1087992708

allen-export-batch-plan:
	$(PYTHON) scripts/export_allen_sessions_batch.py --dry-run

allen-export-batch:
	$(PYTHON) scripts/export_allen_sessions_batch.py --max-new 1

allen-evidence:
	$(PYTHON) scripts/run_allen_evidence_report.py

allen-targets:
	$(PYTHON) scripts/run_allen_target_diagnostics.py

allen-go-evidence-until-10:
	$(PYTHON) scripts/export_until_target_evidence.py --target-name go_response --target-usable-sessions 10 --final-permutations 500

allen-session-relations:
	$(PYTHON) scripts/analyze_allen_session_relations.py

allen-regional-ablation:
	$(PYTHON) scripts/run_allen_regional_ablation.py --target-name go_response --require-usable-target

allen-temporal-reexport:
	$(PYTHON) scripts/reexport_allen_temporal_sessions.py --target-name go_response --require-usable-target --skip-existing-temporal

allen-temporal-windows:
	$(PYTHON) scripts/run_allen_temporal_window_benchmark.py --target-name go_response --require-usable-target

allen-temporal-permutation:
	$(PYTHON) scripts/run_allen_temporal_permutation.py --target-name go_response --window-name pre_response --require-usable-target --n-permutations 50

allen-temporal-permutation-confirm:
	$(PYTHON) scripts/run_allen_temporal_permutation.py --target-name go_response --window-name pre_response --require-usable-target --n-permutations 500 --out-json artifacts/reports/allen_targets/go_response_pre_response_permutation_500.json --out-csv artifacts/reports/allen_targets/go_response_pre_response_permutation_500.csv --out-md artifacts/reports/allen_targets/go_response_pre_response_permutation_500.md

allen-temporal-regional-ablation:
	$(PYTHON) scripts/run_allen_temporal_regional_ablation.py --target-name go_response --window-name pre_response --require-usable-target --significant-only

allen-uncertainty:
	$(PYTHON) scripts/analyze_allen_cross_session_uncertainty.py

allen-response-controls:
	$(PYTHON) scripts/analyze_allen_response_controls.py --require-usable-target

allen-functional-graph:
	$(PYTHON) scripts/build_allen_functional_graph.py

allen-generative-surrogate:
	$(PYTHON) scripts/run_allen_generative_surrogate.py

allen-scientific-agent:
	$(PYTHON) scripts/run_allen_scientific_agent.py

allen-study-manifest:
	$(PYTHON) scripts/register_allen_study_manifest.py

allen-stability-matrix:
	$(PYTHON) scripts/build_allen_stability_matrix.py

allen-latent-temporal:
	$(PYTHON) scripts/run_allen_latent_temporal_baseline.py --require-usable-target

allen-graph-evidence-registry:
	$(PYTHON) scripts/build_allen_graph_evidence_registry.py

allen-session-generator-v2:
	$(PYTHON) scripts/run_allen_session_generator_v2.py --require-usable-target

allen-advanced-scientific-agent:
	$(PYTHON) scripts/run_allen_advanced_scientific_agent.py

allen-selected-microcircuit:
	$(PYTHON) scripts/run_allen_selected_microcircuit.py

allen-microcircuit-validation:
	$(PYTHON) scripts/run_allen_microcircuit_validation.py

allen-advanced-evidence: allen-stabilize allen-stability-matrix allen-latent-temporal allen-graph-evidence-registry allen-session-generator-v2 allen-advanced-scientific-agent allen-selected-microcircuit allen-microcircuit-validation test

allen-stabilize: allen-uncertainty allen-response-controls allen-functional-graph allen-generative-surrogate allen-scientific-agent allen-study-manifest test

verify:
	$(PYTHON) -m unittest discover -s tests
	$(PYTHON) run_prototype.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
