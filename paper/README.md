# MouseBrainBench manuscript

The manuscript targets **Engineering Applications of Artificial Intelligence
(EAAI)** as an original research article.

## Official template

The working manuscript uses Elsevier's official Complex Article Service
single-column template:

- document class: cas-sc;
- template bundle: els-cas-templates 2.4;
- bibliography style: cas-model2-names;
- author--year citations;
- single-column A4 layout, as required by EAAI.

The upstream template is retained at paper/template/cas-sc-template-v2.4.tex.
The class, common style, and bibliography files are included in paper/ so that
the Overleaf project does not depend on an implicit template version.

## Generated manuscripts

Generate all editorial artifacts with:

    .venv/bin/python scripts/build_eaai_manuscript.py

The command creates:

- paper/main.tex: complete working manuscript with author information;
- paper/main_anonymous.tex: manuscript for double-anonymized review;
- paper/title-page.tex: separate author and affiliation page.

All tables are expanded into the generated manuscripts. Scientific sections
remain modular under paper/sections/ to support review and maintenance.

## Compilation

In a functional TeX environment:

    cd paper
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

## Claim boundary

The AI contribution is a claim-aware verification and validation framework for
scientific models. MICRONS is an external-validity case compatible with
published structure--function findings. The paper does not claim biological
priority for that wiring rule, a complete mouse-brain digital twin, causal
mechanism, consciousness, behavioural equivalence, or a state-of-the-art
Sensorium predictor.
