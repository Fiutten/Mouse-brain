from __future__ import annotations

import pytest

from mousebrainbench.artifacts import code_revision


def test_code_revision_accepts_valid_publication_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOUSEBRAINBENCH_GIT_REVISION", "ABCDEF123456")

    assert code_revision() == "abcdef123456"


def test_code_revision_rejects_non_git_publication_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MOUSEBRAINBENCH_GIT_REVISION", "main-dirty")

    with pytest.raises(ValueError, match="hexadecimal Git ID"):
        code_revision()
