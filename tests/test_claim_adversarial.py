import json

from mousebrainbench.benchmarks.claim_adversarial import run


def test_claim_adversarial_benchmark_exposes_overclaiming(tmp_path) -> None:
    output = run(output=tmp_path / "summary.json", markdown=tmp_path / "summary.md")
    payload = json.loads(output.read_text())

    aggregate = {row["evaluator"]: row for row in payload["aggregate_by_evaluator"]}
    assert payload["decision"] == "claim_gate_blocks_adversarial_overclaims"
    assert aggregate["claim_gate"]["fp"] == 0
    assert aggregate["correlation_only"]["fp"] > 0
    assert aggregate["compensatory_score"]["fp"] > 0
