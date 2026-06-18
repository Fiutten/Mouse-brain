"""Transparent Sensorium prediction adapters.

The adapters in this module are deliberately lightweight. They are not intended
to replace official Sensorium models; they provide reproducible baselines that
can be audited inside the MouseBrainBench/MIS framework.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SensoriumAdapterResult:
    """Predictions and diagnostics emitted by a Sensorium adapter."""

    name: str
    prediction: np.ndarray
    scrambled_prediction: np.ndarray
    diagnostics: dict[str, float]


def _safe_correlation(left: np.ndarray, right: np.ndarray) -> float:
    left_flat = np.asarray(left, dtype=float).ravel()
    right_flat = np.asarray(right, dtype=float).ravel()
    if left_flat.size != right_flat.size:
        raise ValueError("correlation inputs must have equal size")
    if np.std(left_flat) == 0 or np.std(right_flat) == 0:
        return 0.0
    return float(np.corrcoef(left_flat, right_flat)[0, 1])


def _standardize_train_test(
    train: np.ndarray, test: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = train.mean(axis=0, keepdims=True)
    std = train.std(axis=0, keepdims=True)
    std[std == 0] = 1.0
    return (train - mean) / std, (test - mean) / std, mean, std


def ridge_fit_predict(
    train_x: np.ndarray,
    train_y: np.ndarray,
    test_x: np.ndarray,
    *,
    alpha: float,
) -> np.ndarray:
    """Fit closed-form ridge regression and predict on held-out features."""

    train_x_std, test_x_std, _, _ = _standardize_train_test(train_x, test_x)
    design = np.column_stack([np.ones(len(train_x_std)), train_x_std])
    test_design = np.column_stack([np.ones(len(test_x_std)), test_x_std])
    penalty = np.eye(design.shape[1]) * alpha
    penalty[0, 0] = 0.0
    weights = np.linalg.solve(design.T @ design + penalty, design.T @ train_y)
    return test_design @ weights


def calibrated_residual_ridge_adapter(
    train_x: np.ndarray,
    train_y: np.ndarray,
    eval_x: np.ndarray,
    *,
    alpha: float = 10.0,
    seed: int = 17,
    folds: int = 5,
    beta_grid: np.ndarray | None = None,
) -> SensoriumAdapterResult:
    """Predict ``mean response + beta * stimulus residual`` with train-only calibration.

    Dynamic Sensorium has a strong population mean component. A plain ridge
    residual can overfit and degrade held-out correlation even when it contains
    stimulus information. This adapter estimates the residual shrinkage
    coefficient ``beta`` by cross-validation within the training split, then
    applies the calibrated residual to the held-out tier.
    """

    if folds < 2:
        raise ValueError("folds must be at least 2")
    if len(train_x) != len(train_y):
        raise ValueError("train_x and train_y must have the same number of trials")
    if beta_grid is None:
        beta_grid = np.linspace(0.0, 1.5, 61)

    indices = np.arange(len(train_x))
    rng = np.random.default_rng(seed)
    rng.shuffle(indices)
    fold_indices = [fold for fold in np.array_split(indices, min(folds, len(indices))) if len(fold)]
    cv_predictions: dict[float, np.ndarray] = {
        float(beta): np.zeros_like(train_y, dtype=float) for beta in beta_grid
    }

    for fold in fold_indices:
        fit_indices = np.setdiff1d(indices, fold, assume_unique=False)
        train_mean = train_y[fit_indices].mean(axis=0, keepdims=True)
        residual = train_y[fit_indices] - train_mean
        residual_prediction = ridge_fit_predict(
            train_x[fit_indices], residual, train_x[fold], alpha=alpha
        )
        for beta in beta_grid:
            cv_predictions[float(beta)][fold] = train_mean + float(beta) * residual_prediction

    cv_scores = {
        beta: _safe_correlation(prediction, train_y)
        for beta, prediction in cv_predictions.items()
    }
    best_beta = max(cv_scores, key=cv_scores.get)

    full_mean = train_y.mean(axis=0, keepdims=True)
    full_residual = train_y - full_mean
    residual_prediction = ridge_fit_predict(train_x, full_residual, eval_x, alpha=alpha)
    prediction = np.repeat(full_mean, len(eval_x), axis=0) + best_beta * residual_prediction

    scrambled_train_x = rng.permutation(train_x)
    scrambled_residual = ridge_fit_predict(scrambled_train_x, full_residual, eval_x, alpha=alpha)
    scrambled_prediction = (
        np.repeat(full_mean, len(eval_x), axis=0) + best_beta * scrambled_residual
    )
    return SensoriumAdapterResult(
        name="calibrated_residual_ridge",
        prediction=prediction,
        scrambled_prediction=scrambled_prediction,
        diagnostics={
            "adapter_alpha": float(alpha),
            "adapter_beta": float(best_beta),
            "adapter_cv_correlation": float(cv_scores[best_beta]),
            "adapter_cv_folds": float(len(fold_indices)),
        },
    )
