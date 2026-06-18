import json
import pytest

from mousebrainbench.benchmarks.sensorium_model_comparator import (
    compare_sensorium_artifacts,
    mouse_key,
    write_comparison_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def test_mouse_key_aligns_artifact_name_variants() -> None:
    assert mouse_key("dynamic29228-2-10") == "dynamic29228"
    assert mouse_key("dynamic29228-2-10-Video-hash") == "dynamic29228"
    assert mouse_key("other") == "other"


def test_compare_sensorium_artifacts_reports_paired_svd_gain(tmp_path) -> None:
    temporal = tmp_path / "summary_dynamic_sensorium_legacy_ood_temporal_comparison.json"
    svd = tmp_path / "summary_dynamic_sensorium_legacy_ood_temporal_svd.json"
    _write_json(
        temporal,
        {
            "rows": [
                {
                    "mouse": "dynamic1-1-1",
                    "summary_correlation": 0.30,
                    "temporal_filterbank_correlation": 0.40,
                    "temporal_minus_mean": 0.05,
                    "summary_minus_mean": -0.05,
                    "summary_minus_scrambled": 0.01,
                    "temporal_minus_scrambled": 0.10,
                    "reliability_estimable": False,
                    "mis_passed": False,
                },
                {
                    "mouse": "dynamic2-1-1",
                    "summary_correlation": 0.20,
                    "temporal_filterbank_correlation": 0.25,
                    "temporal_minus_mean": -0.01,
                    "summary_minus_mean": -0.06,
                    "summary_minus_scrambled": 0.02,
                    "temporal_minus_scrambled": 0.03,
                    "reliability_estimable": False,
                    "mis_passed": False,
                },
            ]
        },
    )
    _write_json(
        svd,
        {
            "rows": [
                {
                    "mouse": "dynamic1-1-1-extra",
                    "temporal_svd_correlation": 0.45,
                    "temporal_svd_minus_mean": 0.10,
                    "temporal_svd_minus_scrambled": 0.14,
                    "reliability_estimable": False,
                    "mis_passed": False,
                },
                {
                    "mouse": "dynamic2-1-1-extra",
                    "temporal_svd_correlation": 0.30,
                    "temporal_svd_minus_mean": 0.04,
                    "temporal_svd_minus_scrambled": 0.08,
                    "reliability_estimable": False,
                    "mis_passed": False,
                },
            ]
        },
    )

    payload = compare_sensorium_artifacts(
        temporal_summary=temporal,
        svd_summary=svd,
        cohort_name="dynamic_sensorium_legacy_ood",
    )

    svd_vs_temporal = payload["pairwise"]["temporal_filterbank_vs_temporal_svd"]
    assert payload["n_mice"] == 2
    assert svd_vs_temporal["right_wins"] == 2
    assert svd_vs_temporal["median_delta"] == pytest.approx(0.05)
    assert payload["evidence_label"] == (
        "positive_ood_prediction_without_mechanistic_identifiability"
    )


def test_write_comparison_outputs_creates_json_and_markdown(tmp_path) -> None:
    payload = {
        "interpretation": "predictive only",
        "cohorts": [
            {
                "cohort": "toy",
                "n_mice": 1,
                "evidence_label": "mixed_evidence",
                "mis_passed_count": 0,
                "reliability_estimable_count": 0,
                "pairwise": {
                    "mean_response_vs_temporal_svd": {
                        "right_wins": 1,
                        "n_paired": 1,
                        "median_delta": 0.1,
                        "mean_delta": 0.1,
                    }
                },
                "model_rows": [
                    {
                        "mouse": "dynamic1",
                        "mean_response": 0.1,
                        "summary_adapter": 0.2,
                        "temporal_filterbank": 0.3,
                        "temporal_svd": 0.4,
                    }
                ],
                "best_models": [{"mouse": "dynamic1", "best_model": "temporal_svd"}],
            }
        ],
    }

    output_json = tmp_path / "summary.json"
    output_md = tmp_path / "summary.md"
    write_comparison_outputs(payload, output_json, output_md)

    assert json.loads(output_json.read_text())["interpretation"] == "predictive only"
    assert "Dynamic Sensorium Model Comparator" in output_md.read_text()
