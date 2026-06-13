"""Validated regional activity extracted from an empirical recording."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class RegionalActivity:
    """Binned population firing rate aligned across named brain regions."""

    time: np.ndarray
    activity_hz: np.ndarray
    region_acronyms: tuple[str, ...]
    unit_counts: tuple[int, ...]
    session_id: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        expected = (len(self.time), len(self.region_acronyms))
        if self.activity_hz.shape != expected:
            raise ValueError(f"activity_hz must have shape {expected}")
        if len(self.unit_counts) != len(self.region_acronyms):
            raise ValueError("unit_counts must align with region_acronyms")
        if len(set(self.region_acronyms)) != len(self.region_acronyms):
            raise ValueError("region acronyms must be unique")
        if np.any(self.activity_hz < 0) or not np.all(np.isfinite(self.activity_hz)):
            raise ValueError("firing rates must be finite and non-negative")
