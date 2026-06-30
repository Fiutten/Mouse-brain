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
    fig, ax = plt.subplots(figsize=(7.4, 3.35))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    columns = [0.025, 0.27, 0.515, 0.76]
    width = 0.205
    top = 0.47
    height = 0.36
    _box(ax, columns[0], top, width, height, "1. CLAIM CONTRACT",
         "Claim class\nTarget entity and scale\nPermitted interpretation",
         facecolor="#e8f1f8", edgecolor="#315f7d")
    _box(ax, columns[1], top, width, height, "2. EVIDENCE DESIGN",
         "Observable quantities\nBlocks and thresholds\nNulls and hold-outs",
         facecolor="#eef2f7")
    _box(ax, columns[2], top, width, height, "3. EXECUTION",
         "Dataset/model adapters\nMetrics and controls\nConjunctive block gates",
         facecolor="#e9f5ef", edgecolor="#39705a")
    _box(ax, columns[3], top, width, height, "4. DECISION ARTIFACT",
         "Admitted claims\nBlocked claims\nVersioned provenance",
         facecolor="#f3f0e8", edgecolor="#796b40")
    for left in columns[:-1]:
        _arrow(ax, (left + width, top + height / 2),
               (left + width + 0.04, top + height / 2))

    _box(ax, 0.085, 0.06, 0.34, 0.22, "ADMITTED",
         "Every required evidence block passes\nfor the declared scope",
         facecolor="#e4f3e9", edgecolor="#26734d")
    _box(ax, 0.575, 0.06, 0.34, 0.22, "BLOCKED OR PARTIAL",
         "Failed or unobserved blocks remain\nexplicit; scores cannot compensate",
         facecolor="#faeceb", edgecolor="#a53b32")
    _arrow(ax, (columns[3] + width / 2, top), (0.745, 0.28))
    _arrow(ax, (columns[3] + width / 2, top), (0.255, 0.28))

    ax.text(0.5, 0.985, "Claim-aware evaluation architecture",
            ha="center", va="top", fontsize=10.5, fontweight="bold", color="#111827")
    ax.text(0.5, 0.90,
            "Models and datasets enter through adapters; interpretation is controlled by the declared evidence contract.",
            ha="center", va="top", fontsize=7.3, color="#4b5563")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT / "framework_workflow.pdf", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(OUTPUT / "framework_workflow.png", dpi=240, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    build_framework_workflow()
