# MouseBrainBench manuscript

This directory contains the manuscript targeting **PLOS Computational
Biology** as a Research Article.

## Journal template

The submission source uses the official PLOS LaTeX template:

- template version 3.8, April 2026;
- bibliography style plos2025.bst;
- continuous line numbering;
- double-spaced, single-column manuscript;
- Vancouver citation order;
- one self-contained LaTeX manuscript, as required by PLOS.

The unmodified upstream template is retained at
paper/template/plos_latex_template_v3.8.tex for provenance. It was downloaded
from the official PLOS LaTeX distribution linked by the journal guidelines.

## Building the manuscript source

Scientific sections remain modular during development. Generate the
self-contained PLOS source with:

    .venv/bin/python scripts/build_plos_manuscript.py

The command expands every section and table into paper/main.tex. The generated
file contains no LaTeX input statements and is the file compiled by Overleaf and
submitted to PLOS.

To compile in an operational TeX environment:

    cd paper
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

## Claim boundary

The manuscript reports MouseBrainBench as a reproducible claim-audit framework
for partial mouse-brain models. MICRONS is an external-validity case compatible
with previously published structure--function findings. The manuscript does not
claim biological priority for the MICRONS wiring rule, a complete mouse-brain
digital twin, causal mechanism, consciousness, behavioural equivalence, or a
state-of-the-art Sensorium predictor.
