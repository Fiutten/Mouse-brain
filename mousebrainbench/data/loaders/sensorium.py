"""Load lightweight Sensorium/Sensorium-style trial directories.

The official Sensorium releases store each trial as NumPy arrays under
``data/images`` or ``data/videos`` and ``data/responses``, with split labels in
``meta/trials/tiers.npy``. This loader intentionally covers that documented
structure without depending on the heavier official PyTorch stack.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np


Modality = Literal["static", "dynamic"]


@dataclass(frozen=True)
class SensoriumTrialTable:
    """In-memory tabular representation of a small Sensorium cohort."""

    root: Path
    modality: Modality
    stimulus_features: np.ndarray
    responses: np.ndarray
    tiers: np.ndarray
    trial_ids: np.ndarray
    stimulus_ids: np.ndarray
    neuron_ids: np.ndarray

    @property
    def n_trials(self) -> int:
        return int(self.responses.shape[0])

    @property
    def n_neurons(self) -> int:
        return int(self.responses.shape[1])


def _numeric_key(path: Path) -> tuple[int, str]:
    try:
        return int(path.stem), path.name
    except ValueError:
        return 10**12, path.name


def _load_trial_arrays(directory: Path, *, max_trials: int | None = None) -> list[np.ndarray]:
    files = sorted(directory.glob("*.npy"), key=_numeric_key)
    if max_trials is not None:
        files = files[:max_trials]
    if not files:
        raise FileNotFoundError(f"no .npy trial files found in {directory}")
    return [np.load(file) for file in files]


def _feature_vector(stimulus: np.ndarray, modality: Modality) -> np.ndarray:
    """Extract cheap stimulus descriptors for transparent baselines.

    These features are not intended to be state of the art. They provide a
    deterministic baseline that can be tested before adding deep visual models.
    """

    values = np.asarray(stimulus, dtype=float)
    flat = values.reshape(-1)
    features = [
        float(np.mean(flat)),
        float(np.std(flat)),
        float(np.percentile(flat, 25)),
        float(np.percentile(flat, 75)),
    ]
    if modality == "dynamic" and values.ndim >= 3:
        frame_axis = 0
        frame_means = values.mean(axis=tuple(range(1, values.ndim)))
        features.extend(
            [
                float(np.std(frame_means)),
                float(np.mean(np.abs(np.diff(frame_means)))) if len(frame_means) > 1 else 0.0,
                float(values.shape[frame_axis]),
            ]
        )
    else:
        features.extend([0.0, 0.0, 1.0])
    return np.asarray(features, dtype=float)


def _response_vector(response: np.ndarray) -> np.ndarray:
    """Collapse official static/dynamic response arrays to trial x neuron."""

    values = np.asarray(response, dtype=float)
    if values.ndim == 1:
        return values
    if values.ndim == 2:
        # Dynamic Sensorium responses are neuron x frame; static responses are
        # usually already one value per neuron. Averaging preserves a simple
        # trial-level target for first-pass benchmarking.
        return values.mean(axis=1)
    return values.reshape(values.shape[0], -1).mean(axis=1)


def _load_meta_array(path: Path, *, fallback: np.ndarray) -> np.ndarray:
    return np.load(path) if path.exists() else fallback


def load_sensorium_directory(
    root: str | Path,
    *,
    modality: Modality | None = None,
    max_trials: int | None = None,
) -> SensoriumTrialTable:
    """Load a documented Sensorium 2022/2023 directory into compact arrays."""

    base = Path(root)
    data_dir = base / "data"
    if modality is None:
        if (data_dir / "videos").exists():
            modality = "dynamic"
        elif (data_dir / "images").exists():
            modality = "static"
        else:
            raise FileNotFoundError("expected data/images or data/videos under Sensorium root")
    stimulus_dir = data_dir / ("videos" if modality == "dynamic" else "images")
    response_dir = data_dir / "responses"
    stimuli = _load_trial_arrays(stimulus_dir, max_trials=max_trials)
    responses = _load_trial_arrays(response_dir, max_trials=max_trials)
    if len(stimuli) != len(responses):
        raise ValueError("stimulus and response trial counts do not match")

    n_trials = len(responses)
    fallback_trial_ids = np.arange(n_trials)
    tiers = _load_meta_array(
        base / "meta" / "trials" / "tiers.npy",
        fallback=np.full(n_trials, "train", dtype=object),
    )[:n_trials].astype(str)
    trial_ids = _load_meta_array(
        base / "meta" / "trials" / "trial_idx.npy", fallback=fallback_trial_ids
    )[:n_trials]
    stimulus_ids = _load_meta_array(
        base / "meta" / "trials" / "frame_image_id.npy", fallback=fallback_trial_ids
    )[:n_trials]
    response_matrix = np.stack([_response_vector(response) for response in responses])
    neuron_ids = _load_meta_array(
        base / "meta" / "neurons" / "unit_ids.npy",
        fallback=np.arange(response_matrix.shape[1]),
    )[: response_matrix.shape[1]]
    return SensoriumTrialTable(
        root=base,
        modality=modality,
        stimulus_features=np.stack([_feature_vector(stimulus, modality) for stimulus in stimuli]),
        responses=response_matrix,
        tiers=tiers,
        trial_ids=trial_ids,
        stimulus_ids=stimulus_ids,
        neuron_ids=neuron_ids,
    )

