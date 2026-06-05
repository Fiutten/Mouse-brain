"""Dataset adapter errors."""

from __future__ import annotations


class DatasetDependencyError(RuntimeError):
    """Raised when an optional dataset dependency is missing."""


class DatasetConfigurationError(RuntimeError):
    """Raised when a dataset adapter is not sufficiently configured or complete."""
