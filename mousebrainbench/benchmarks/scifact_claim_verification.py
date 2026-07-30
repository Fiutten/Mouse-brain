"""SciFact external claim-verification adapter.

This benchmark is not intended to compete with SciFact systems. Its role is to
test whether MouseBrainBench can consume a public scientific claim-verification
dataset and keep claim support separate from lexical similarity.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from mousebrainbench import __version__
from mousebrainbench.artifacts import code_revision


DEFAULT_ROOT = Path("data/external/scifact/data")
DEFAULT_OUTPUT = Path("results/scifact_claim_verification/summary.json")
DEFAULT_MARKDOWN = Path("results/scifact_claim_verification/summary.md")


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in {"the", "and", "with", "from", "that", "this"}
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _gold_label(claim: dict[str, Any]) -> str:
    labels = []
    for entries in claim.get("evidence", {}).values():
        labels.extend(str(entry.get("label", "NOT_ENOUGH_INFO")) for entry in entries)
    if not labels:
        return "NOT_ENOUGH_INFO"
    counts = Counter(labels)
    return str(counts.most_common(1)[0][0])


def _lexical_score(claim_text: str, cited_docs: list[int], corpus: dict[int, dict[str, Any]]) -> float:
    claim_tokens = _tokens(claim_text)
    if not claim_tokens:
        return 0.0
    doc_tokens: set[str] = set()
    for doc_id in cited_docs:
        doc = corpus.get(int(doc_id), {})
        doc_tokens.update(_tokens(str(doc.get("title", ""))))
        doc_tokens.update(_tokens(" ".join(str(item) for item in doc.get("abstract", []))))
    if not doc_tokens:
        return 0.0
    return len(claim_tokens & doc_tokens) / math.sqrt(len(claim_tokens) * len(doc_tokens))


def run(
    root: Path = DEFAULT_ROOT,
    output: Path = DEFAULT_OUTPUT,
    markdown: Path = DEFAULT_MARKDOWN,
    max_claims: int | None = None,
) -> Path:
    """Run a lightweight SciFact claim-auditing benchmark."""

    started = time.perf_counter()
    claims_path = root / "claims_dev.jsonl"
    corpus_path = root / "corpus.jsonl"
    if not claims_path.exists() or not corpus_path.exists():
        payload = {
            "version": __version__,
            "git_revision": code_revision(),
            "analysis": "scifact_claim_verification",
            "decision": "scifact_data_missing",
            "missing": [str(path) for path in (claims_path, corpus_path) if not path.exists()],
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2))
        write_markdown(payload, markdown)
        return output

    claims = _load_jsonl(claims_path)
    if max_claims is not None:
        claims = claims[:max_claims]
    corpus = {int(doc["doc_id"]): doc for doc in _load_jsonl(corpus_path)}

    rows: list[dict[str, Any]] = []
    threshold = 0.18
    abstain_threshold = 0.12
    for claim in claims:
        label = _gold_label(claim)
        score = _lexical_score(str(claim["claim"]), claim.get("cited_doc_ids", []), corpus)
        shortcut_supported = score >= threshold
        abstaining_supported = score >= threshold
        abstained = score < abstain_threshold
        gold_supported = label == "SUPPORT"
        rows.append(
            {
                "claim_id": claim["id"],
                "gold_label": label,
                "lexical_score": score,
                "shortcut_supported": shortcut_supported,
                "abstained": abstained,
                "abstaining_supported": False if abstained else abstaining_supported,
                "gold_supported": gold_supported,
                "shortcut_false_positive": shortcut_supported and not gold_supported,
                "shortcut_false_negative": (not shortcut_supported) and gold_supported,
                "abstaining_false_positive": (not abstained) and abstaining_supported and not gold_supported,
                "abstaining_false_negative": (not abstained) and (not abstaining_supported) and gold_supported,
            }
        )

    fp = sum(row["shortcut_false_positive"] for row in rows)
    fn = sum(row["shortcut_false_negative"] for row in rows)
    gold_positive = sum(row["gold_supported"] for row in rows)
    gold_negative = len(rows) - gold_positive
    label_counts = Counter(row["gold_label"] for row in rows)
    per_label = {}
    for label in sorted(label_counts):
        subset = [row for row in rows if row["gold_label"] == label]
        per_label[label] = {
            "n": len(subset),
            "mean_lexical_score": sum(float(row["lexical_score"]) for row in subset) / len(subset),
            "shortcut_supported_rate": sum(row["shortcut_supported"] for row in subset) / len(subset),
        }
    non_abstained = [row for row in rows if not row["abstained"]]
    abstaining_fp = sum(row["abstaining_false_positive"] for row in non_abstained)
    abstaining_fn = sum(row["abstaining_false_negative"] for row in non_abstained)
    abstaining_gold_positive = sum(row["gold_supported"] for row in non_abstained)
    abstaining_gold_negative = len(non_abstained) - abstaining_gold_positive
    payload = {
        "version": __version__,
        "git_revision": code_revision(),
        "analysis": "scifact_claim_verification",
        "dataset": "SciFact dev",
        "num_claims": len(rows),
        "label_counts": dict(label_counts),
        "lexical_threshold": threshold,
        "abstain_threshold": abstain_threshold,
        "shortcut_false_positives": fp,
        "shortcut_false_negatives": fn,
        "shortcut_overclaiming_risk": fp / gold_negative if gold_negative else 0.0,
        "shortcut_conservativeness": fn / gold_positive if gold_positive else 0.0,
        "abstention_rate": 1.0 - (len(non_abstained) / len(rows) if rows else 0.0),
        "abstaining_overclaiming_risk": (
            abstaining_fp / abstaining_gold_negative if abstaining_gold_negative else 0.0
        ),
        "abstaining_conservativeness": (
            abstaining_fn / abstaining_gold_positive if abstaining_gold_positive else 0.0
        ),
        "per_label": per_label,
        "runtime_seconds": time.perf_counter() - started,
        "rows": rows,
        "decision": (
            "scifact_external_claim_audit_ready"
            if len(rows) >= 100 and fp > 0
            else "scifact_external_claim_audit_insufficient"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    write_markdown(payload, markdown)
    return output


def write_markdown(payload: dict[str, Any], markdown: Path) -> None:
    """Write SciFact adapter report."""

    lines = [
        "# SciFact Claim Verification Adapter",
        "",
        f"- Decision: `{payload['decision']}`",
        f"- Claims: `{payload.get('num_claims', 0)}`",
        f"- Label counts: `{payload.get('label_counts', {})}`",
        f"- Shortcut ORI: `{payload.get('shortcut_overclaiming_risk', 0.0):.3f}`",
        f"- Shortcut CI: `{payload.get('shortcut_conservativeness', 0.0):.3f}`",
        f"- Abstention rate: `{payload.get('abstention_rate', 0.0):.3f}`",
        f"- Abstaining ORI: `{payload.get('abstaining_overclaiming_risk', 0.0):.3f}`",
        f"- Runtime seconds: `{payload.get('runtime_seconds', 0.0):.3f}`",
        "",
    ]
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--max-claims", type=int, default=None)
    args = parser.parse_args()
    print(json.dumps({"output": str(run(args.root, args.output, args.markdown, args.max_claims).resolve())}))


if __name__ == "__main__":
    main()
