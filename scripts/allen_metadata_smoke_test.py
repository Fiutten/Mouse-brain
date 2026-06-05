"""Run a metadata-only Allen Visual Behavior Neuropixels smoke test.

This script must not download full NWB session files. It only instantiates the
AllenSDK project cache and reads metadata tables needed to choose a candidate
session.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurotwin_mvp.datasets import AllenVisualBehaviorNeuropixelsLoader


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Run the metadata smoke test and print JSON output."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=["allensdk", "direct-s3"],
        default="allensdk",
        help="Metadata backend. `direct-s3` avoids AllenSDK and downloads only metadata CSV.",
    )
    args = parser.parse_args()
    loader = AllenVisualBehaviorNeuropixelsLoader(ROOT / "data" / "allen")
    if args.backend == "direct-s3":
        result = loader.direct_s3_metadata_smoke_test()
    else:
        result = loader.metadata_smoke_test()
    print(
        json.dumps(
            {
                "cache_dir": result.cache_dir,
                "manifest": result.manifest,
                "n_ecephys_sessions": result.n_ecephys_sessions,
                "columns": result.columns,
                "source": result.source,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
