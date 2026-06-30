"""Build working and anonymous EAAI manuscripts from modular LaTeX sources."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def read(relative_path: str) -> str:
    return (PAPER / relative_path).read_text(encoding="utf-8").strip()


def inline_inputs(text: str) -> str:
    """Expand table and section inputs so each generated manuscript is portable."""

    pattern = re.compile(r"\\input\{([^}]+)\}")
    while match := pattern.search(text):
        included = read(f"{match.group(1)}.tex")
        text = text[: match.start()] + included + text[match.end() :]
    return text


def abstract_body() -> str:
    text = read("sections/abstract.tex")
    start, end = r"\begin{abstract}", r"\end{abstract}"
    if not text.startswith(start) or not text.endswith(end):
        raise ValueError("abstract source must use the abstract environment")
    return text[len(start) : -len(end)].strip()


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def frontmatter(*, anonymous: bool) -> str:
    if anonymous:
        short_author = "Anonymous"
        author = r"""
\author[1]{Anonymous Author}
\affiliation[1]{organization={Affiliation withheld for double-anonymized review},
                country={}}
"""
    else:
        short_author = r"Fern\'andez-Isabel"
        author = r"""
\author[1]{Alberto Fern\'andez-Isabel}
\cormark[1]
\ead{alberto.fernandez.isabel@urjc.es}
\credit{Conceptualization, Methodology, Software, Validation, Formal analysis,
Investigation, Data curation, Writing--original draft, Writing--review and
editing, Project administration}
\affiliation[1]{organization={Data Science Laboratory, Rey Juan Carlos University},
                addressline={C/ Tulip\'an, s/n},
                city={M\'ostoles},
                postcode={28933},
                state={Madrid},
                country={Spain}}
\cortext[1]{Corresponding author}
"""
    return rf"""
\shorttitle{{Claim-aware validation of mouse-brain digital models}}
\shortauthors{{{short_author}}}

\title[mode=title]{{MouseBrainBench: Claim-aware verification and validation of
artificial intelligence models for partial digital representations of the
mouse brain}}

{author}

\begin{{abstract}}
{abstract_body()}
\end{{abstract}}

\begin{{keywords}}
artificial intelligence validation \sep scientific machine learning \sep
digital twins \sep computational neuroscience \sep benchmarking \sep
mechanistic identifiability
\end{{keywords}}
"""


def manuscript_body(*, anonymous: bool) -> str:
    if anonymous:
        availability = (
            "Source code, configurations, acquisition scripts, and result artifacts "
            "are available in an anonymous review archive. The public repository "
            "and archival DOI will be disclosed after double-anonymized review."
        )
    else:
        availability = (
            r"Source code, configurations, acquisition scripts, and result artifacts "
            r"are maintained at \url{https://github.com/Fiutten/Mouse-brain}. "
            r"A versioned archival DOI will be created for the submission release."
        )

    sections = [
        read("sections/introduction.tex"),
        read("sections/contributions.tex"),
        read("sections/related_work.tex"),
        read("sections/framework.tex"),
        read("sections/experimental_methodology.tex"),
        read("sections/discussion_eaai.tex"),
        read("sections/conclusions.tex"),
    ]
    body = "\n\n".join(sections)
    return rf"""
{body}

\section{{Data and code availability}}
\label{{sec:data-code-availability}}
{availability} Raw public datasets are not redistributed. Data acquisition
commands preserve public source identifiers and application programming
interface queries where licenses permit. MICRONS CAVE access requires a
personal token and acceptance of the service terms.

\section{{Declaration of competing interest}}
\label{{sec:competing-interest}}
The author declares no known competing financial interests or personal
relationships that could have appeared to influence the work reported in this
paper.

\section{{Acknowledgements}}
\label{{sec:acknowledgements}}
The author acknowledges the Allen Institute, the Sensorium and Dynamic
Sensorium teams, the MICRONS Consortium, and the CAVE infrastructure for making
the resources used in this study accessible.

\printcredits
\bibliographystyle{{cas-model2-names}}
\bibliography{{references}}
"""


def build_manuscript(*, anonymous: bool, output: Path) -> None:
    source = rf"""\documentclass[a4paper,fleqn]{{cas-sc}}

\usepackage[authoryear]{{natbib}}
\usepackage{{amsmath,amssymb,booktabs,tabularx,graphicx,capt-of}}
\usepackage{{url}}

\journal{{Engineering Applications of Artificial Intelligence}}

\begin{{document}}
\let\WriteBookmarks\relax
\def\floatpagepagefraction{{1}}
\def\textpagefraction{{.001}}

{frontmatter(anonymous=anonymous)}

\maketitle

{manuscript_body(anonymous=anonymous)}

\end{{document}}
"""
    output.write_text(normalize(inline_inputs(source)), encoding="utf-8")


def build_title_page() -> None:
    source = r"""\documentclass[a4paper,fleqn]{cas-sc}
\usepackage[authoryear]{natbib}
\journal{Engineering Applications of Artificial Intelligence}
\begin{document}
\shorttitle{Claim-aware validation of mouse-brain digital models}
\shortauthors{Fern\'andez-Isabel}
\title[mode=title]{MouseBrainBench: Claim-aware verification and validation of
artificial intelligence models for partial digital representations of the
mouse brain}
\author[1]{Alberto Fern\'andez-Isabel}
\cormark[1]
\ead{alberto.fernandez.isabel@urjc.es}
\credit{Conceptualization, Methodology, Software, Validation, Formal analysis,
Investigation, Data curation, Writing--original draft, Writing--review and
editing, Project administration}
\affiliation[1]{organization={Data Science Laboratory, Rey Juan Carlos University},
                addressline={C/ Tulip\'an, s/n},
                city={M\'ostoles},
                postcode={28933},
                state={Madrid},
                country={Spain}}
\cortext[1]{Corresponding author}
\begin{abstract}
Title page for double-anonymized review. The abstract is provided in the
anonymous manuscript.
\end{abstract}
\begin{keywords}
artificial intelligence validation \sep scientific machine learning \sep
digital twins \sep computational neuroscience \sep benchmarking
\end{keywords}
\maketitle
\end{document}
"""
    (PAPER / "title-page.tex").write_text(normalize(source), encoding="utf-8")


def build_highlights() -> None:
    """Create the separate highlights file requested by Elsevier submissions."""
    source = r"""\documentclass[a4paper]{article}
\usepackage[margin=25mm]{geometry}
\pagestyle{empty}
\begin{document}
\section*{Highlights}
\begin{itemize}
\item A claim-aware benchmark separates prediction from mechanistic evidence.
\item Conjunctive evidence gates prevent compensation across validation criteria.
\item Allen and Sensorium expose reproducible or predictive non-mechanistic cases.
\item A MICRONS endpoint replicates across two non-overlapping hold-out cohorts.
\item Decisions remain linked to versioned artifacts and explicitly blocked claims.
\end{itemize}
\end{document}
"""
    (PAPER / "highlights.tex").write_text(normalize(source), encoding="utf-8")


def main() -> None:
    build_manuscript(anonymous=False, output=PAPER / "main.tex")
    build_manuscript(anonymous=True, output=PAPER / "main_anonymous.tex")
    build_title_page()
    build_highlights()
    print(PAPER / "main.tex")
    print(PAPER / "main_anonymous.tex")
    print(PAPER / "title-page.tex")
    print(PAPER / "highlights.tex")


if __name__ == "__main__":
    main()
