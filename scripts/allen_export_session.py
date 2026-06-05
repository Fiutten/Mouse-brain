"""Export one Allen Visual Behavior Neuropixels session to `session.json`.

This script is intended for the future `.venv-allen` environment. It requires
AllenSDK and should be used after selecting a specific ecephys session from
metadata. It downloads/loads one NWB session, normalizes it, and writes the core
artifact consumed by `.venv`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from neurotwin_mvp.allen_normalization import AllenSessionNormalizer, TimeWindows
from neurotwin_mvp.datasets import AllenVisualBehaviorNeuropixelsLoader


ROOT = Path(__file__).resolve().parents[1]


def local_nwb_path(cache_dir: Path, ecephys_session_id: int) -> Path:
    """Return the expected local Allen Visual Behavior Neuropixels NWB path."""
    return (
        cache_dir
        / "visual-behavior-neuropixels-0.5.0"
        / "behavior_ecephys_sessions"
        / str(ecephys_session_id)
        / f"ecephys_session_{ecephys_session_id}.nwb"
    )


def load_allen_session(loader: AllenVisualBehaviorNeuropixelsLoader, ecephys_session_id: int):
    """Load an Allen session, preferring an already cached NWB for offline use."""
    nwb_path = local_nwb_path(loader.cache_dir, ecephys_session_id)
    if nwb_path.exists():
        from allensdk.brain_observatory.ecephys.behavior_ecephys_session import (
            BehaviorEcephysSession,
        )

        try:
            return BehaviorEcephysSession.from_nwb_path(str(nwb_path))
        except Exception as exc:
            raise RuntimeError(
                f"Local NWB exists but could not be opened as a valid Allen session: {nwb_path}. "
                "The file may be a partial download. Resume or replace it before exporting."
            ) from exc

    cache_class = loader._cache_class()
    cache = cache_class.from_s3_cache(cache_dir=loader.cache_dir)
    return cache.get_ecephys_session(ecephys_session_id=ecephys_session_id)


def main() -> None:
    """Load one Allen session through AllenSDK and export a normalized artifact."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ecephys-session-id", type=int, required=True)
    parser.add_argument("--behavior-session-id", type=int)
    parser.add_argument("--animal-id", default="unknown")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-trials", type=int)
    parser.add_argument("--baseline-start", type=float, default=-0.250)
    parser.add_argument("--baseline-end", type=float, default=0.0)
    parser.add_argument("--stimulus-start", type=float, default=0.0)
    parser.add_argument("--stimulus-end", type=float, default=0.250)
    parser.add_argument("--decision-start", type=float, default=0.250)
    parser.add_argument("--decision-end", type=float, default=0.750)
    parser.add_argument("--pre-response-start", type=float, default=0.250)
    parser.add_argument("--pre-response-end", type=float, default=0.750)
    parser.add_argument("--response-margin", type=float, default=0.050)
    args = parser.parse_args()

    loader = AllenVisualBehaviorNeuropixelsLoader(ROOT / "data" / "allen")
    allen_session = load_allen_session(loader, args.ecephys_session_id)
    normalizer = AllenSessionNormalizer(
        TimeWindows(
            baseline_start=args.baseline_start,
            baseline_end=args.baseline_end,
            stimulus_start=args.stimulus_start,
            stimulus_end=args.stimulus_end,
            decision_start=args.decision_start,
            decision_end=args.decision_end,
            pre_response_start=args.pre_response_start,
            pre_response_end=args.pre_response_end,
            response_margin=args.response_margin,
        )
    )
    artifact = normalizer.export(
        allen_session,
        output_dir=args.out,
        ecephys_session_id=args.ecephys_session_id,
        behavior_session_id=args.behavior_session_id,
        animal_id=args.animal_id,
        max_trials=args.max_trials,
    )
    print(f"session_artifact={artifact}")


if __name__ == "__main__":
    main()
