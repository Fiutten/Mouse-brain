"""Latent temporal baselines for neural population windows.

This module provides a transparent first latent model: principal components of
temporal region-rate features followed by the same deterministic logistic
classifier used elsewhere in the project. It is intentionally modest, but it
creates the right benchmark surface for later CEBRA/LFADS-style models:
held-out behavior prediction, reconstruction error and component stability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from .behavioral_targets import TargetName, materialize_target_session
from .benchmark import DictLogisticRegressionClassifier
from .data import Session, Trial, train_test_split


@dataclass(frozen=True)
class LatentTemporalReport:
    """Held-out report for one latent temporal baseline."""

    session_id: str
    target_name: str
    window_names: list[str]
    n_components: int
    n_train: int
    n_test: int
    baseline_balanced_accuracy: float
    latent_balanced_accuracy: float
    latent_gain: float
    reconstruction_mse: float
    explained_variance_fraction: float
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


def run_latent_temporal_baseline(
    session: Session,
    *,
    target_name: TargetName = "go_response",
    window_names: list[str] | None = None,
    n_components: int = 3,
    train_fraction: float = 0.7,
) -> LatentTemporalReport:
    """Evaluate PCA temporal latents against a non-neural behavioral baseline."""
    if n_components <= 0:
        raise ValueError("n_components must be positive")
    window_names = window_names or ["baseline", "stimulus", "pre_response"]
    target_session = materialize_target_session(session, target_name)
    _require_temporal_windows(target_session.trials, window_names)
    train, test = train_test_split(target_session, train_fraction)
    split = len(train)
    raw_rows = _temporal_matrix(target_session.trials, target_session.region_names, window_names)
    pca = _fit_pca(raw_rows[:split], n_components)
    latent_rows = [_latent_row(pca, row) for row in raw_rows]
    baseline_rows = _behavioral_rows(target_session.trials)
    baseline_model = DictLogisticRegressionClassifier("latent_baseline_behavior")
    baseline_model.fit(baseline_rows[:split], [trial.choice for trial in train])
    latent_model = DictLogisticRegressionClassifier("latent_temporal_pca")
    latent_model.fit(latent_rows[:split], [trial.choice for trial in train])
    baseline_predictions = [_predict_dict(baseline_model, row) for row in baseline_rows[split:]]
    latent_predictions = [_predict_dict(latent_model, row) for row in latent_rows[split:]]
    targets = [trial.choice for trial in test]
    baseline_balanced = _balanced_accuracy(targets, baseline_predictions)
    latent_balanced = _balanced_accuracy(targets, latent_predictions)
    reconstruction = _reconstruction_mse(pca, raw_rows[split:])
    warnings = []
    if latent_balanced <= baseline_balanced:
        warnings.append("Latent temporal model does not beat behavioral baseline")
    if len(train) < 100:
        warnings.append("Training split has fewer than 100 trials; latent estimate is unstable")
    return LatentTemporalReport(
        session_id=target_session.session_id,
        target_name=target_name,
        window_names=window_names,
        n_components=len(pca["components"]),
        n_train=len(train),
        n_test=len(test),
        baseline_balanced_accuracy=baseline_balanced,
        latent_balanced_accuracy=latent_balanced,
        latent_gain=latent_balanced - baseline_balanced,
        reconstruction_mse=reconstruction,
        explained_variance_fraction=pca["explained_variance_fraction"],
        warnings=warnings,
    )


def _require_temporal_windows(trials: list[Trial], window_names: list[str]) -> None:
    """Ensure all trials expose the requested temporal window feature maps."""
    for trial in trials:
        temporal = trial.metadata.get("region_rates_by_window")
        if not isinstance(temporal, dict) or any(not isinstance(temporal.get(window), dict) for window in window_names):
            raise ValueError("Session is missing required temporal region-rate windows")


def _temporal_matrix(trials: list[Trial], region_names: list[str], window_names: list[str]) -> list[list[float]]:
    """Flatten region x window features into a dense matrix."""
    matrix = []
    for trial in trials:
        temporal = trial.metadata["region_rates_by_window"]
        row = []
        for window in window_names:
            rates = temporal[window]
            row.extend(float(rates.get(region, 0.0)) for region in region_names)
        matrix.append(row)
    return matrix


def _behavioral_rows(trials: list[Trial]) -> list[dict[str, float]]:
    """Build compact non-neural rows for the latent baseline comparator."""
    rows = []
    previous: Trial | None = None
    for trial in trials:
        row = {
            "stimulus": float(trial.stimulus),
            "latency_ms": float(trial.latency_ms),
            "engagement": float(trial.engagement),
        }
        if previous is None:
            row["history:prev_choice"] = 0.5
            row["history:prev_reward"] = 0.5
        else:
            row["history:prev_choice"] = float(previous.choice)
            row["history:prev_reward"] = float(previous.reward)
        rows.append(row)
        previous = trial
    return rows


def _fit_pca(rows: list[list[float]], n_components: int) -> dict:
    """Fit PCA with power iteration and deflation, dependency-free."""
    if not rows:
        raise ValueError("Cannot fit PCA on empty rows")
    n_features = len(rows[0])
    means = [sum(row[j] for row in rows) / len(rows) for j in range(n_features)]
    centered = [[value - means[j] for j, value in enumerate(row)] for row in rows]
    total_variance = sum(sum(value * value for value in row) for row in centered) or 1.0
    residual = [list(row) for row in centered]
    components = []
    variances = []
    for _ in range(min(n_components, n_features)):
        vector = [1.0 / math.sqrt(n_features) for _ in range(n_features)]
        for _ in range(40):
            projected = _covariance_vector_product(residual, vector)
            norm = math.sqrt(sum(value * value for value in projected))
            if norm == 0.0:
                break
            vector = [value / norm for value in projected]
        scores = [sum(value * weight for value, weight in zip(row, vector, strict=True)) for row in residual]
        variance = sum(score * score for score in scores)
        if variance <= 1e-12:
            break
        components.append(vector)
        variances.append(variance)
        residual = [
            [value - score * weight for value, weight in zip(row, vector, strict=True)]
            for row, score in zip(residual, scores, strict=True)
        ]
    return {
        "means": means,
        "components": components,
        "explained_variance_fraction": sum(variances) / total_variance,
    }


def _covariance_vector_product(rows: list[list[float]], vector: list[float]) -> list[float]:
    """Return X^T X vector for centered rows."""
    out = [0.0 for _ in vector]
    for row in rows:
        score = sum(value * weight for value, weight in zip(row, vector, strict=True))
        for j, value in enumerate(row):
            out[j] += value * score
    return out


def _latent_row(pca: dict, row: list[float]) -> dict[str, float]:
    centered = [value - mean for value, mean in zip(row, pca["means"], strict=True)]
    return {
        f"latent:{index}": sum(value * weight for value, weight in zip(centered, component, strict=True))
        for index, component in enumerate(pca["components"])
    }


def _reconstruction_mse(pca: dict, rows: list[list[float]]) -> float:
    """Compute held-out reconstruction MSE from retained components."""
    if not rows:
        return 0.0
    errors = []
    for row in rows:
        centered = [value - mean for value, mean in zip(row, pca["means"], strict=True)]
        reconstruction = [0.0 for _ in centered]
        for component in pca["components"]:
            score = sum(value * weight for value, weight in zip(centered, component, strict=True))
            for j, weight in enumerate(component):
                reconstruction[j] += score * weight
        errors.extend((value - estimate) ** 2 for value, estimate in zip(centered, reconstruction, strict=True))
    return sum(errors) / len(errors)


def _predict_dict(model: DictLogisticRegressionClassifier, row: dict[str, float]) -> int:
    return int(model.predict_probability(row) >= 0.5)


def _balanced_accuracy(targets: list[int], predictions: list[int]) -> float:
    recalls = []
    for label in (0, 1):
        total = sum(1 for target in targets if target == label)
        if total:
            correct = sum(
                1
                for target, prediction in zip(targets, predictions, strict=True)
                if target == label and prediction == label
            )
            recalls.append(correct / total)
    if not recalls:
        raise ValueError("Cannot compute balanced accuracy without targets")
    return sum(recalls) / len(recalls)
