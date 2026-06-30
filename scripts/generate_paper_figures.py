"""Generate deterministic vector figures used by the EAAI manuscript."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper" / "figures"


def _box(ax, x: float, y: float, width: float, height: float, title: str, body: str,
         *, facecolor: str = "#f4f6f8", edgecolor: str = "#334155") -> None:
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.15, edgecolor=edgecolor, facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height * 0.70, title, ha="center", va="center",
            fontsize=7.7, fontweight="bold", color="#111827")
    ax.text(x + width / 2, y + height * 0.35, body, ha="center", va="center",
            fontsize=6.6, color="#374151", linespacing=1.20)


def _arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                linewidth=1.1, color="#475569"))


def build_framework_workflow() -> None:
    """Render the claim-aware evaluation workflow and its decision boundary."""
    fig, ax = plt.subplots(figsize=(7.2, 5.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    _box(ax, 0.04, 0.72, 0.25, 0.17, "1. Define claim",
         "Class and target entity\nScale and permitted scope", facecolor="#e8f1f8")
    _box(ax, 0.375, 0.72, 0.25, 0.17, "2. Check observability",
         "Required quantities\nCoverage and provenance", facecolor="#eef2f7")
    _box(ax, 0.71, 0.72, 0.25, 0.17, "3. Configure evidence",
         "Blocks, thresholds and nulls\nHold-outs and cost metrics", facecolor="#eef2f7")
    _arrow(ax, (0.29, 0.805), (0.375, 0.805))
    _arrow(ax, (0.625, 0.805), (0.71, 0.805))

    _box(ax, 0.04, 0.39, 0.25, 0.18, "4. Execute adapters",
         "Synthetic and public data\nBaselines and external models", facecolor="#eef2f7")
    _box(ax, 0.375, 0.39, 0.25, 0.18, "5. Evaluate blocks",
         "Prediction and reliability\nTopology, direction, structure", facecolor="#e9f5ef")
    _box(ax, 0.71, 0.39, 0.25, 0.18, "6. Apply claim gate",
         "All required blocks must pass\nMissing data cannot compensate", facecolor="#e9f5ef")
    _arrow(ax, (0.835, 0.72), (0.835, 0.60))
    _arrow(ax, (0.71, 0.48), (0.625, 0.48))
    _arrow(ax, (0.375, 0.48), (0.29, 0.48))

    _box(ax, 0.12, 0.08, 0.31, 0.17, "Admitted interpretation",
         "Bounded claim supported by\na complete evidence contract",
         facecolor="#e4f3e9", edgecolor="#26734d")
    _box(ax, 0.57, 0.08, 0.31, 0.17, "Blocked interpretation",
         "Failed or unobserved blocks\nremain explicit limitations",
         facecolor="#faeceb", edgecolor="#a53b32")
    _arrow(ax, (0.50, 0.39), (0.275, 0.25))
    _arrow(ax, (0.50, 0.39), (0.725, 0.25))

    ax.text(0.5, 0.965, "MouseBrainBench claim-aware verification and validation workflow",
            ha="center", va="top", fontsize=9.5, fontweight="bold", color="#111827")
    ax.text(0.5, 0.925,
            "The claim is configured before evaluation; the final decision preserves failed evidence blocks.",
            ha="center", va="top", fontsize=7.2, color="#4b5563")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / "framework_workflow.pdf", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUTPUT / "framework_workflow.png", dpi=240, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    build_framework_workflow()
