"""Configuration loading and validation.

The regional model is configured from JSON instead of hard-coded Python so that
experiments can be audited and reproduced. This module is deliberately small:
it parses the JSON file into typed dataclasses and rejects invalid model
definitions early.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class RegionConfig:
    """Parameters for one coarse brain region in the Level-0 model."""

    name: str
    role: str
    decay: float
    bias: float
    readout: float


@dataclass(frozen=True)
class ConnectionConfig:
    """Directed weighted connection between two configured regions."""

    source: str
    target: str
    weight: float


@dataclass(frozen=True)
class ModelConfig:
    """Full Level-0 model configuration."""

    regions: list[RegionConfig]
    connections: list[ConnectionConfig]
    dt: float
    noise: float


def load_config(path: str | Path) -> ModelConfig:
    """Load a model configuration from JSON and validate it."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    regions = [
        RegionConfig(
            name=item["name"],
            role=item["role"],
            decay=float(item["decay"]),
            bias=float(item.get("bias", 0.0)),
            readout=float(item.get("readout", 0.0)),
        )
        for item in data["regions"]
    ]
    connections = [
        ConnectionConfig(
            source=item["source"],
            target=item["target"],
            weight=float(item["weight"]),
        )
        for item in data["connections"]
    ]
    config = ModelConfig(
        regions=regions,
        connections=connections,
        dt=float(data.get("dt", 1.0)),
        noise=float(data.get("noise", 0.0)),
    )
    validate_config(config)
    return config


def validate_config(config: ModelConfig) -> None:
    """Reject malformed configurations before a model is instantiated."""
    if not config.regions:
        raise ValueError("At least one region is required")
    if config.dt <= 0.0:
        raise ValueError(f"dt must be positive: {config.dt}")
    if config.noise < 0.0:
        raise ValueError(f"noise must be non-negative: {config.noise}")
    names = [region.name for region in config.regions]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate regions: {duplicates}")
    known = set(names)
    for region in config.regions:
        if not 0.0 < region.decay <= 1.0:
            raise ValueError(f"Invalid decay for {region.name}: {region.decay}")
    for connection in config.connections:
        if connection.source not in known:
            raise ValueError(f"Unknown source region: {connection.source}")
        if connection.target not in known:
            raise ValueError(f"Unknown target region: {connection.target}")
