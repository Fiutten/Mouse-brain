import json

from mousebrainbench.benchmarks.synthetic_identifiability import run


def test_synthetic_benchmark_separates_directed_and_common_drive(tmp_path) -> None:
    output = run(tmp_path / "synthetic.json")
    payload = json.loads(output.read_text())
    cases = {case["case"]: case for case in payload["cases"]}

    assert cases["directed_truth"]["mis"]["passed"]
    assert not cases["common_drive_nonidentifiable"]["mis"]["passed"]

