"""Run a bounded MICrONS structure-function pilot when real edges exist.

The analysis asks a narrow, falsifiable question: are functionally similar
co-registered MICrONS units more likely to be connected by real synaptic edges
than expected from spatially matched or random pairs? It deliberately avoids
claiming a full connectome/function model from the small pilot.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_MATCHED = Path("data/microns/static_small/matched_function_em_units.csv")
DEFAULT_EDGES = Path("data/microns/static_small/cave_synaptic_edges.csv")
DEFAULT_OUTPUT = Path("results/microns_structure_function_pilot/summary.json")
DEFAULT_MARKDOWN = Path("results/microns_structure_function_pilot/summary.md")


FUNCTION_COLUMNS = ("cc_abs", "cc_max", "cc_norm", "OSI", "DSI", "gOSI", "gDSI", "pref_ori", "pref_dir")
SPATIAL_COLUMNS = ("pt_position_x", "pt_position_y", "pt_position_z")


@dataclass(frozen=True)
class PairRecord:
    """One candidate ordered pair for structure-function testing."""

    pre_root: int
    post_root: int
    connected: bool
    distance: float
    functional_similarity: float


def _zscore(values: np.ndarray) -> np.ndarray:
    """Column-wise z-score with zero-variance protection."""

    mean = np.nanmean(values, axis=0)
    std = np.nanstd(values, axis=0)
    std[std == 0] = 1.0
    return (values - mean) / std


def _circular_distance_degrees(a: np.ndarray, b: np.ndarray, period: float) -> np.ndarray:
    """Return normalized circular similarity for angle-valued features."""

    raw = np.abs(a - b) % period
    dist = np.minimum(raw, period - raw)
    return 1.0 - (dist / (period / 2.0))


def _prepare_units(matched_units: Path) -> pd.DataFrame:
    """Load matched MICrONS units with usable spatial and functional fields."""

    units = pd.read_csv(matched_units)
    required = ["pt_root_id", *SPATIAL_COLUMNS, *FUNCTION_COLUMNS]
    usable = units.dropna(subset=required).copy()
    usable["pt_root_id"] = usable["pt_root_id"].astype("int64")
    usable = usable.drop_duplicates(subset=["pt_root_id"], keep="first")
    return usable


def _prepare_edges(edges_path: Path, valid_roots: set[int]) -> set[tuple[int, int]]:
    """Load directed synaptic root-id edges restricted to candidate roots."""

    edges = pd.read_csv(edges_path)
    required = {"pre_pt_root_id", "post_pt_root_id"}
    if not required.issubset(edges.columns):
        raise ValueError(f"Edges file lacks required columns: {sorted(required)}")
    edge_pairs: set[tuple[int, int]] = set()
    for row in edges[["pre_pt_root_id", "post_pt_root_id"]].dropna().itertuples(index=False):
        pre = int(row.pre_pt_root_id)
        post = int(row.post_pt_root_id)
        if pre != post and pre in valid_roots and post in valid_roots:
            edge_pairs.add((pre, post))
    return edge_pairs


def _functional_similarity_matrix(units: pd.DataFrame) -> np.ndarray:
    """Compute conservative functional similarity from static response properties."""

    continuous = _zscore(units[["cc_abs", "cc_max", "cc_norm", "OSI", "DSI", "gOSI", "gDSI"]].to_numpy(float))
    diff = continuous[:, None, :] - continuous[None, :, :]
    continuous_similarity = -np.linalg.norm(diff, axis=2)
    ori_similarity = _circular_distance_degrees(
        units["pref_ori"].to_numpy(float)[:, None],
        units["pref_ori"].to_numpy(float)[None, :],
        period=180.0,
    )
    dir_similarity = _circular_distance_degrees(
        units["pref_dir"].to_numpy(float)[:, None],
        units["pref_dir"].to_numpy(float)[None, :],
        period=360.0,
    )
    return continuous_similarity + ori_similarity + dir_similarity


def _pair_records(units: pd.DataFrame, edge_pairs: set[tuple[int, int]]) -> list[PairRecord]:
    """Build all ordered non-self candidate pairs with structure/function fields."""

    roots = units["pt_root_id"].astype("int64").to_numpy()
    xyz = units[list(SPATIAL_COLUMNS)].to_numpy(float)
    similarity = _functional_similarity_matrix(units)
    records: list[PairRecord] = []
    for i, pre in enumerate(roots):
        distances = np.linalg.norm(xyz[i] - xyz, axis=1)
        for j, post in enumerate(roots):
            if i == j:
                continue
            records.append(
                PairRecord(
                    pre_root=int(pre),
                    post_root=int(post),
                    connected=(int(pre), int(post)) in edge_pairs,
                    distance=float(distances[j]),
                    functional_similarity=float(similarity[i, j]),
                )
            )
    return records


def _permutation_p_value(observed: float, null: np.ndarray) -> float:
    """One-sided permutation p-value for connected-pair functional similarity."""

    return float((np.sum(null >= observed) + 1) / (len(null) + 1))


def _analyze(records: list[PairRecord], *, n_permutations: int, seed: int) -> dict[str, Any]:
    """Compare real connected pairs against random and distance-matched nulls."""

    rng = np.random.default_rng(seed)
    frame = pd.DataFrame([record.__dict__ for record in records])
    connected = frame[frame["connected"]]
    unconnected = frame[~frame["connected"]]
    if connected.empty:
        return {
            "approved_analysis": False,
            "reason": "No real synaptic edges among candidate roots.",
            "n_pairs": int(len(frame)),
            "n_connected_pairs": 0,
        }

    observed = float(connected["functional_similarity"].mean())
    random_null = np.array(
        [
            unconnected["functional_similarity"]
            .sample(n=len(connected), replace=len(unconnected) < len(connected), random_state=int(rng.integers(0, 2**31 - 1)))
            .mean()
            for _ in range(n_permutations)
        ],
        dtype=float,
    )

    distance_sorted = unconnected.assign(
        distance_bin=pd.qcut(unconnected["distance"], q=min(10, len(unconnected)), duplicates="drop")
    )
    connected_binned = connected.assign(
        distance_bin=pd.cut(
            connected["distance"],
            bins=pd.IntervalIndex(distance_sorted["distance_bin"].cat.categories),
        )
    )
    matched_samples: list[float] = []
    for _ in range(n_permutations):
        sampled = []
        for _, row in connected_binned.iterrows():
            candidates = distance_sorted[distance_sorted["distance_bin"] == row["distance_bin"]]
            if candidates.empty:
                candidates = unconnected
            sampled.append(float(candidates.sample(n=1, random_state=int(rng.integers(0, 2**31 - 1)))["functional_similarity"].iloc[0]))
        matched_samples.append(float(np.mean(sampled)))
    distance_null = np.array(matched_samples, dtype=float)

    random_delta = float(observed - random_null.mean())
    random_p = _permutation_p_value(observed, random_null)
    distance_delta = float(observed - distance_null.mean())
    distance_p = _permutation_p_value(observed, distance_null)
    positive_result = random_delta > 0.0 and distance_delta > 0.0 and distance_p <= 0.05
    return {
        "approved_analysis": True,
        "positive_structure_function_result": positive_result,
        "scientific_decision": (
            "positive_structure_function_micro_pilot"
            if positive_result
            else "negative_or_inconclusive_structure_function_micro_pilot"
        ),
        "n_pairs": int(len(frame)),
        "n_connected_pairs": int(len(connected)),
        "n_unconnected_pairs": int(len(unconnected)),
        "observed_connected_mean_functional_similarity": observed,
        "random_null_mean": float(random_null.mean()),
        "random_null_delta": random_delta,
        "random_null_p_one_sided": random_p,
        "distance_matched_null_mean": float(distance_null.mean()),
        "distance_matched_delta": distance_delta,
        "distance_matched_p_one_sided": distance_p,
        "n_permutations": n_permutations,
        "seed": seed,
    }


def run(
    *,
    matched_units: Path = DEFAULT_MATCHED,
    edges: Path = DEFAULT_EDGES,
    output: Path = DEFAULT_OUTPUT,
    markdown: Path = DEFAULT_MARKDOWN,
    n_permutations: int = 1000,
    seed: int = 17,
) -> dict[str, Any]:
    """Execute the MICrONS structure-function pilot analysis."""

    if not edges.exists():
        payload = {
            "analysis": "microns_structure_function_pilot",
            "approved_analysis": False,
            "reason": f"Missing real edge file: {edges}",
            "matched_units": str(matched_units),
            "edges": str(edges),
        }
    else:
        units = _prepare_units(matched_units)
        edge_pairs = _prepare_edges(edges, set(units["pt_root_id"].astype("int64")))
        records = _pair_records(units, edge_pairs)
        payload = {
            "analysis": "microns_structure_function_pilot",
            "matched_units": str(matched_units),
            "edges": str(edges),
            "n_units": int(len(units)),
            "n_edge_pairs_loaded": int(len(edge_pairs)),
            **_analyze(records, n_permutations=n_permutations, seed=seed),
            "interpretation": (
                "A positive result requires connected pairs to exceed both random "
                "and distance-matched nulls. This pilot tests local structure-function "
                "coupling only; it is not a whole-MICrONS model."
            ),
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2))
    lines = [
        "# MICrONS Structure-Function Pilot",
        "",
        f"- Approved analysis: `{payload['approved_analysis']}`",
        f"- Reason: {payload.get('reason', 'real edge file available')}",
    ]
    if payload.get("approved_analysis"):
        lines.extend(
            [
                f"- Units: `{payload['n_units']}`",
                f"- Connected pairs: `{payload['n_connected_pairs']}`",
                f"- Scientific decision: `{payload['scientific_decision']}`",
                f"- Random-null delta: `{payload['random_null_delta']}`",
                f"- Distance-matched delta: `{payload['distance_matched_delta']}`",
                f"- Distance-matched p: `{payload['distance_matched_p_one_sided']}`",
            ]
        )
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines) + "\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matched-units", type=Path, default=DEFAULT_MATCHED)
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--n-permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    payload = run(
        matched_units=args.matched_units,
        edges=args.edges,
        output=args.output,
        markdown=args.markdown,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )
    print(json.dumps({"output": str(args.output), "approved_analysis": payload["approved_analysis"]}))


if __name__ == "__main__":
    main()
