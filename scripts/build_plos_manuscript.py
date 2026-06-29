"""Build the self-contained PLOS Computational Biology manuscript.

PLOS requires one LaTeX source file without input statements. The scientific
text remains modular during development, while this script expands all sections
and tables into paper/main.tex using the official PLOS v3.8 template preamble.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
TEMPLATE = PAPER / "template" / "plos_latex_template_v3.8.tex"
OUTPUT = PAPER / "main.tex"


def _read(relative_path: str) -> str:
    return (PAPER / relative_path).read_text(encoding="utf-8").strip()


def _inline_inputs(text: str) -> str:
    """Recursively replace LaTeX inputs with their file contents."""

    pattern = re.compile(r"\\input\{([^}]+)\}")
    while match := pattern.search(text):
        included = _read(f"{match.group(1)}.tex")
        text = text[: match.start()] + included + text[match.end() :]
    return text


def _star_headings(text: str) -> str:
    """Use the unnumbered heading convention shown by the PLOS template."""

    text = re.sub(r"\\section\{", r"\\section*{", text)
    text = re.sub(r"\\subsection\{", r"\\subsection*{", text)
    text = re.sub(r"\\subsubsection\{", r"\\subsubsection*{", text)
    return text.replace(r"\citep{", r"\cite{").replace(r"\citet{", r"\cite{")


def _without_leading_section(text: str, title: str) -> str:
    marker = rf"\section{{{title}}}"
    if not text.startswith(marker):
        raise ValueError(f"expected {marker!r} at start of section")
    return text[len(marker) :].lstrip()


def _without_leading_abstract(text: str) -> str:
    start = r"\begin{abstract}"
    end = r"\end{abstract}"
    if not text.startswith(start) or not text.endswith(end):
        raise ValueError("abstract section must use the abstract environment")
    return text[len(start) : -len(end)].strip()


def build() -> Path:
    template = TEMPLATE.read_text(encoding="utf-8")
    preamble, _ = template.split(r"\begin{document}", maxsplit=1)
    preamble = preamble.replace(
        r"\usepackage{array}",
        "\\usepackage{array}\n"
        "\\usepackage{booktabs,tabularx}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[utf8]{inputenc}",
    )
    preamble = preamble.replace(
        "%\\usepackage{setspace} \n%\\doublespacing",
        "\\usepackage{setspace}\n\\doublespacing",
    )
    preamble = preamble.replace(
        "\\newcommand{\\lorem}{\\textbf{LOREM}}\n"
        "\\newcommand{\\ipsum}{\\textbf{IPSUM}}\n",
        "",
    )

    introduction = _without_leading_section(_read("sections/introduction.tex"), "Introduction")
    related = _without_leading_section(_read("sections/related_work.tex"), "Related work")
    contributions = _without_leading_section(
        _read("sections/contributions.tex"), "Research contributions"
    )

    body = rf"""
\begin{{document}}
\vspace*{{0.2in}}

\begin{{flushleft}}
{{\Large
\textbf{{MouseBrainBench: A reproducible claim-audit framework for partial digital models of the mouse brain}}
}}
\newline
\\
Alberto Fern\'andez-Isabel\textsuperscript{{1*}}
\\
\bigskip
\textbf{{1}} Data Science Laboratory, Rey Juan Carlos University, M\'ostoles, Madrid, Spain
\\
\bigskip
* alberto.fernandez.isabel@urjc.es
\\
\textbf{{Short title:}} Auditing partial digital models of the mouse brain
\end{{flushleft}}

\section*{{Abstract}}
{_without_leading_abstract(_read("sections/abstract.tex"))}

\section*{{Author summary}}
{_read("sections/author_summary.tex")}

\clearpage
\newgeometry{{top=0.85in,left=1in,right=1in,footskip=0.75in}}
\linenumbers

\section*{{Introduction}}
{introduction}

\subsection*{{Relationship to existing resources and methods}}
{related}

\subsection*{{Scope and contributions}}
{contributions}

{_read("sections/results.tex")}

{_read("sections/discussion_plos.tex")}

{_read("sections/methods_plos.tex")}

\section*{{Data and code availability}}
The MouseBrainBench source code, fixed configurations, acquisition scripts, and
machine-readable result artifacts are maintained at
\url{{https://github.com/Fiutten/Mouse-brain}}. Raw public datasets are not
redistributed. Acquisition scripts record public sources and API queries where
licenses permit reproducible access. MICRONS CAVE queries require a personal
access token and acceptance of the corresponding terms of service. A permanent
software release and archival DOI will be created for the version associated
with submission.

\section*{{Acknowledgments}}
The author acknowledges the Allen Institute, the Sensorium and Dynamic
Sensorium teams, the MICRONS Consortium, and the CAVE infrastructure for making
the resources used in this study publicly accessible.

\section*{{Author contributions}}
Alberto Fern\'andez-Isabel: Conceptualization, Methodology, Software,
Validation, Formal analysis, Investigation, Data curation, Writing--original
draft, Writing--review and editing, and Project administration.

\section*{{Competing interests}}
The author declares no competing interests.

\nolinenumbers
\bibliography{{references}}

\end{{document}}
"""
    document = preamble + _star_headings(_inline_inputs(body))
    # The official archive uses CRLF and includes trailing spaces in comments.
    # Normalize generated output so repository checks remain deterministic.
    document = "\n".join(line.rstrip() for line in document.splitlines()) + "\n"
    OUTPUT.write_text(document, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(build())
