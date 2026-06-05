"""International Brain Laboratory adapter.

Official access path:

- ONE API
- OpenAlyx public data endpoint
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..data import Session
from .errors import DatasetConfigurationError, DatasetDependencyError


@dataclass(frozen=True)
class IBLSessionSelection:
    eid: str | None = None
    subject: str | None = None
    max_trials: int | None = None


class IBLBrainwideMapLoader:
    """Loader skeleton for IBL brain-wide decision-making data."""

    def __init__(
        self,
        cache_dir: str | Path,
        selection: IBLSessionSelection | None = None,
        base_url: str = "https://openalyx.internationalbrainlab.org",
    ) -> None:
        """Create an IBL adapter without downloading data."""
        self.cache_dir = Path(cache_dir)
        self.selection = selection or IBLSessionSelection()
        self.base_url = base_url

    def _one_class(self) -> Any:
        """Import ONE lazily so the core package works without IBL dependencies."""
        try:
            from one.api import ONE  # type: ignore
        except ModuleNotFoundError as exc:
            raise DatasetDependencyError(
                "IBL ONE API is not installed. Install optional dependency `ONE-api` "
                "before using IBLBrainwideMapLoader."
            ) from exc
        return ONE

    def available(self) -> bool:
        """Return whether the ONE API is importable in the current environment."""
        try:
            self._one_class()
        except DatasetDependencyError:
            return False
        return True

    def load(self) -> Session:
        """Normalize one IBL session into the internal `Session` contract.

        Full implementation is intentionally pending. The explicit error is a
        guardrail against treating this adapter as production-ready.
        """
        raise DatasetConfigurationError(
            "IBL loader contract is defined, but full ONE-to-Session normalization "
            "is not implemented yet. Use SyntheticNeuropixelsLoader for local tests "
            "or implement `load` after selecting a concrete IBL session."
        )

    def describe_plan(self) -> list[str]:
        """Return the concrete implementation plan for this adapter."""
        return [
            "Use ONE API with OpenAlyx public endpoint.",
            f"Base URL: {self.base_url}",
            f"Cache directory: {self.cache_dir}",
            "Search or select session/eid.",
            "Load trials, choices, feedback, intervals and spike sorting outputs.",
            "Map Allen acronyms or IBL atlas regions into coarse neurotwin regions.",
            "Return normalized neurotwin_mvp.data.Session.",
        ]
