# MouseBrainBench manuscript

This directory contains the working LaTeX manuscript for the MouseBrainBench
paper. It is intentionally journal-neutral so it can be synchronized to
Overleaf first and adapted later to PLOS Computational Biology, Nature
Computational Science, or another target journal.

## Build

```bash
cd paper
latexmk -pdf main.tex
```

## Current target strategy

Primary realistic target: PLOS Computational Biology.

Stretch target: Nature Computational Science, only if the framing is elevated
as a broad computational-science framework for auditing partial digital-twin
claims.

Specialized fallback: Neuroinformatics.

## Important claim boundary

The manuscript must not claim a complete mouse-brain digital twin. The current
defensible contribution is a reproducible claim-audit benchmark for partial
mouse-brain digital models, with MICRONS as the main replicated empirical
structure-function case.
