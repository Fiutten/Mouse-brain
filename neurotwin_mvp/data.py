"""Data interfaces and synthetic Neuropixels-like fixtures.

The key design goal is to make synthetic and real datasets share one internal
contract. Allen/IBL loaders should eventually return the same `Session` object
that the synthetic fixture returns here. That keeps downstream experiments and
baselines independent from dataset-specific APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol
import math
import random


REGIONS = [
    "visual_thalamus",
    "visual_cortex",
    "association_cortex",
    "basal_ganglia",
    "hippocampus",
    "arousal",
]


@dataclass(frozen=True)
class Trial:
    """One behavioral/neural trial in the normalized internal format.

    `region_rates` stores coarse region-level activity features. For real
    Neuropixels data these will be derived from spike counts/rates after mapping
    recorded units to our coarse regions.
    """

    trial_id: int
    stimulus: float
    choice: int
    reward: int
    latency_ms: float
    engagement: float
    region_rates: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Session:
    """Normalized session consumed by baselines, models and workflows."""

    session_id: str
    animal_id: str
    dataset: str
    trials: list[Trial]
    region_names: list[str]


class SessionLoader(Protocol):
    """Minimal loader protocol used by workflow orchestration."""

    def load(self) -> Session:
        """Load one session."""


def _sigmoid(x: float) -> float:
    """Numerically stable sigmoid used only by the synthetic fixture."""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


class SyntheticNeuropixelsLoader:
    """Generate a controlled session with region-level rates.

    The fixture intentionally encodes known causal structure:

    - visual thalamus and visual cortex track stimulus;
    - association cortex integrates stimulus and engagement;
    - basal ganglia contributes to choice;
    - hippocampus carries weak context;
    - arousal controls engagement and latency.

    This is not evidence. It is a testbed for pipeline mechanics.
    """

    def __init__(self, n_trials: int = 240, seed: int = 11) -> None:
        if n_trials <= 1:
            raise ValueError("n_trials must be greater than 1")
        self.n_trials = n_trials
        self.rng = random.Random(seed)

    def load(self) -> Session:
        """Generate a synthetic session following the normalized contract."""
        trials = []
        context = 0.0
        for trial_id in range(self.n_trials):
            stimulus = self.rng.choice([-1.0, 1.0])
            context = 0.92 * context + 0.08 * stimulus + self.rng.gauss(0.0, 0.03)
            arousal = max(0.0, min(1.0, 0.62 + self.rng.gauss(0.0, 0.12)))
            visual_thalamus = 4.0 + 1.2 * stimulus + 0.5 * arousal + self.rng.gauss(0.0, 0.35)
            visual_cortex = 5.0 + 1.4 * stimulus + 0.7 * arousal + self.rng.gauss(0.0, 0.45)
            association = 3.5 + 0.8 * stimulus + 0.6 * context + 0.5 * arousal + self.rng.gauss(0.0, 0.40)
            basal_ganglia = 3.2 + 0.9 * association / 5.0 + 0.7 * stimulus + self.rng.gauss(0.0, 0.40)
            hippocampus = 2.8 + 1.0 * context + self.rng.gauss(0.0, 0.30)
            choice_probability = _sigmoid(
                0.95 * stimulus + 0.35 * (basal_ganglia - 3.2) + 0.20 * (association - 3.5)
            )
            choice = 1 if self.rng.random() < choice_probability else 0
            correct = int((choice == 1 and stimulus > 0) or (choice == 0 and stimulus < 0))
            latency = max(80.0, 420.0 - 120.0 * arousal - 45.0 * abs(stimulus) + self.rng.gauss(0.0, 25.0))
            trials.append(
                Trial(
                    trial_id=trial_id,
                    stimulus=stimulus,
                    choice=choice,
                    reward=correct,
                    latency_ms=latency,
                    engagement=arousal,
                    region_rates={
                        "visual_thalamus": visual_thalamus,
                        "visual_cortex": visual_cortex,
                        "association_cortex": association,
                        "basal_ganglia": basal_ganglia,
                        "hippocampus": hippocampus,
                        "arousal": arousal,
                    },
                )
            )
        return Session(
            session_id="synthetic_neuropixels_001",
            animal_id="synthetic_mouse",
            dataset="synthetic-neuropixels",
            trials=trials,
            region_names=list(REGIONS),
        )


def train_test_split(session: Session, train_fraction: float = 0.7) -> tuple[list[Trial], list[Trial]]:
    """Create a deterministic chronological split.

    For real data this avoids trial shuffling by default. Shuffled or
    animal/session-level splits should be explicit because leakage is a serious
    risk in neural datasets.
    """
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1")
    split = int(len(session.trials) * train_fraction)
    if split == 0 or split == len(session.trials):
        raise ValueError("train_fraction produces an empty split")
    return session.trials[:split], session.trials[split:]


def mean_region_rates(trials: list[Trial]) -> dict[str, float]:
    """Compute mean activity per coarse region over a list of trials."""
    if not trials:
        raise ValueError("Cannot summarize empty trial list")
    names = trials[0].region_rates
    return {
        name: sum(trial.region_rates[name] for trial in trials) / len(trials)
        for name in names
    }
