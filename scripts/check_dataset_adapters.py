"""Check optional real-data adapter availability.

This script is a smoke test for the future real-data path. It should be safe to
run before AllenSDK or ONE are installed; missing dependencies are reported as
`available=False`, not as workflow failures.
"""

from __future__ import annotations

from pathlib import Path

from neurotwin_mvp.datasets import AllenVisualBehaviorNeuropixelsLoader, IBLBrainwideMapLoader


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Print availability and implementation plan for each optional adapter."""
    loaders = [
        ("allen_visual_behavior_neuropixels", AllenVisualBehaviorNeuropixelsLoader(ROOT / "data" / "allen")),
        ("ibl_brainwide_map", IBLBrainwideMapLoader(ROOT / "data" / "ibl")),
    ]
    for name, loader in loaders:
        print(f"{name}: available={loader.available()}")
        for step in loader.describe_plan():
            print(f"  - {step}")


if __name__ == "__main__":
    main()
