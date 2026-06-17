import json

from mousebrainbench.benchmarks.allen_vbn_mis import build_allen_vbn_mis, run


def _phase2c() -> dict:
    return {
        "target_result": {
            "median_cross_mouse_correlation": 0.89,
            "median_split_half_correlation": 0.99,
            "fraction_above_own_null_95th": 0.75,
        }
    }


def _phase3() -> dict:
    return {
        "allen_minus_median_permutation": -0.005,
        "fraction_permutations_outperformed": 0.21,
        "paired_advantage_bootstrap_95_interval": [-0.007, -0.001],
        "allen_minus_disconnected": 0.003,
    }


def _phase4() -> dict:
    return {
        "latency": {
            "median_cross_mouse_tau": 0.0,
            "median_split_half_tau": 0.0,
            "fraction_above_own_null_95th": 0.0,
            "median_resolvable_pair_fraction": 0.0,
        },
        "lead_lag": {
            "fraction_above_own_null_95th": 0.0,
            "median_nonzero_pair_fraction": 0.0,
        },
    }


def test_allen_mis_marks_reproducible_target_as_non_mechanistic() -> None:
    mis = build_allen_vbn_mis(phase2c=_phase2c(), phase3=_phase3(), phase4=_phase4())
    blocks = {block["name"]: block for block in mis.as_dict()["blocks"]}

    assert blocks["reproducibility"]["passed"]
    assert not blocks["topology_specificity"]["passed"]
    assert not blocks["directed_identifiability"]["passed"]
    assert not mis.passed


def test_allen_mis_run_persists_decision(tmp_path) -> None:
    phase2c = tmp_path / "phase2c.json"
    phase3 = tmp_path / "phase3.json"
    phase4 = tmp_path / "phase4.json"
    output = tmp_path / "mis.json"
    phase2c.write_text(json.dumps(_phase2c()))
    phase3.write_text(json.dumps(_phase3()))
    phase4.write_text(json.dumps(_phase4()))

    run(phase2c_path=phase2c, phase3_path=phase3, phase4_path=phase4, output=output)
    payload = json.loads(output.read_text())

    assert payload["decision"] == "reproducible_target_without_mechanistic_identifiability"
