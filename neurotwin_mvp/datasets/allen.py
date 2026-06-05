"""Allen Visual Behavior Neuropixels adapter.

This adapter is intentionally conservative. It defines the contract and the
official dependency path, but does not pretend to solve full NWB alignment yet.

Official access path:

- AllenSDK
- VisualBehaviorNeuropixelsProjectCache
- NWB files / S3 cache
"""

from __future__ import annotations

from dataclasses import dataclass
import csv
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from ..data import Session
from .errors import DatasetConfigurationError, DatasetDependencyError


ALLEN_VBN_S3_BASE_URL = "https://visual-behavior-neuropixels-data.s3.us-west-2.amazonaws.com"
ALLEN_VBN_ECEPHYS_SESSIONS_CSV = (
    f"{ALLEN_VBN_S3_BASE_URL}/visual-behavior-neuropixels/project_metadata/ecephys_sessions.csv"
)


@dataclass(frozen=True)
class AllenSessionSelection:
    ecephys_session_id: int | None = None
    max_units: int | None = None
    max_trials: int | None = None


@dataclass(frozen=True)
class AllenMetadataSmokeResult:
    """Result of a metadata-only AllenSDK smoke test.

    This intentionally records project-level metadata only. It must not trigger
    download of full per-session NWB files.
    """

    cache_dir: str
    manifest: str
    n_ecephys_sessions: int
    columns: list[str]
    source: str = "allensdk"


class AllenVisualBehaviorNeuropixelsLoader:
    """Loader skeleton for Allen Visual Behavior Neuropixels.

    The first production implementation should:

    1. instantiate `VisualBehaviorNeuropixelsProjectCache`;
    2. load session metadata;
    3. select one ecephys session;
    4. load trials/stimulus presentations/units/spike times;
    5. aggregate units by `structure_acronym`;
    6. map acronyms into our coarse regional model.
    """

    def __init__(
        self,
        cache_dir: str | Path,
        selection: AllenSessionSelection | None = None,
    ) -> None:
        """Create an Allen adapter.

        The adapter stores configuration only. It does not download data during
        initialization; downloads must be explicit in the future implementation.
        """
        self.cache_dir = Path(cache_dir)
        self.selection = selection or AllenSessionSelection()

    def _cache_class(self) -> Any:
        """Import AllenSDK lazily so the core package works without it."""
        try:
            from allensdk.brain_observatory.behavior.behavior_project_cache import (  # type: ignore
                VisualBehaviorNeuropixelsProjectCache,
            )
        except ModuleNotFoundError as exc:
            raise DatasetDependencyError(
                "AllenSDK is not installed. Install optional dependency `allensdk` "
                "before using AllenVisualBehaviorNeuropixelsLoader."
            ) from exc
        return VisualBehaviorNeuropixelsProjectCache

    def available(self) -> bool:
        """Return whether AllenSDK is importable in the current environment."""
        try:
            self._cache_class()
        except DatasetDependencyError:
            return False
        return True

    def load(self) -> Session:
        """Normalize one Allen session into the internal `Session` contract.

        Full implementation is intentionally pending. The current explicit error
        prevents accidental use of an incomplete real-data path.
        """
        raise DatasetConfigurationError(
            "Allen loader contract is defined, but full NWB-to-Session normalization "
            "is not implemented yet. Use SyntheticNeuropixelsLoader for local tests "
            "or implement `load` after selecting a concrete Allen session."
        )

    def metadata_smoke_test(self) -> AllenMetadataSmokeResult:
        """Load Allen Visual Behavior Neuropixels metadata only.

        Expected behavior:

        - instantiate `VisualBehaviorNeuropixelsProjectCache`;
        - download/read the project manifest if needed;
        - load the ecephys session metadata table;
        - return row count and columns.

        This method must not call `get_ecephys_session(...)`, because that would
        download a full NWB file, typically around gigabytes per session.
        """
        cache_class = self._cache_class()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache = cache_class.from_s3_cache(cache_dir=self.cache_dir)
        manifest = str(cache.current_manifest())
        ecephys_sessions = cache.get_ecephys_session_table()
        columns = [str(column) for column in getattr(ecephys_sessions, "columns", [])]
        return AllenMetadataSmokeResult(
            cache_dir=str(self.cache_dir),
            manifest=manifest,
            n_ecephys_sessions=len(ecephys_sessions),
            columns=columns,
        )

    def direct_s3_metadata_smoke_test(self) -> AllenMetadataSmokeResult:
        """Load Allen metadata directly from the public S3 CSV.

        This is a fallback for environments where AllenSDK cannot be installed
        cleanly. It uses only Python's standard library and downloads the small
        `ecephys_sessions.csv` metadata file, not NWB session data.

        The direct S3 route is suitable for session discovery and environment
        validation. Full data normalization should still use AllenSDK or a
        carefully implemented manifest-based S3 pipeline.
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        metadata_dir = self.cache_dir / "project_metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        local_csv = metadata_dir / "ecephys_sessions.csv"
        if not local_csv.exists() or local_csv.stat().st_size == 0:
            with urlopen(ALLEN_VBN_ECEPHYS_SESSIONS_CSV, timeout=30) as response:
                local_csv.write_bytes(response.read())
        with local_csv.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            columns = next(reader)
            n_rows = sum(1 for _ in reader)
        return AllenMetadataSmokeResult(
            cache_dir=str(self.cache_dir),
            manifest="direct_s3_metadata_csv",
            n_ecephys_sessions=n_rows,
            columns=[str(column) for column in columns],
            source="direct_s3",
        )

    def describe_plan(self) -> list[str]:
        """Return the concrete implementation plan for this adapter."""
        return [
            "Use AllenSDK VisualBehaviorNeuropixelsProjectCache.",
            "Fallback: direct S3 metadata CSV for environment smoke tests.",
            f"Cache directory: {self.cache_dir}",
            "Load project metadata: ecephys sessions, behavior sessions, units, probes, channels.",
            "Select ecephys session by configured ID or by quality/region coverage.",
            "Load trials, stimulus presentations, units and spike times.",
            "Aggregate spike rates by structure acronym and map to coarse regions.",
            "Return normalized neurotwin_mvp.data.Session.",
        ]
