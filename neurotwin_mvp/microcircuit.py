"""Selected microcircuit layer for controlled graph edges.

This layer is deliberately narrow. It models a visual-cortex / basal-ganglia
pre-response circuit because those are the currently controlled functional
graph edges. The model uses small latent populations, calibrated from robust
Allen sessions, to test whether a minimal mechanistic scaffold can reproduce
observed directionality. It is not a cellular simulation or causal claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from collections.abc import Callable, Iterable

from .data import Session, Trial


@dataclass(frozen=True)
class MicrocircuitCalibration:
    """Empirical parameters for the selected microcircuit."""

    target_name: str
    window_name: str
    robust_session_ids: list[str]
    region_means: dict[str, float]
    visual_cortex_drop: float
    basal_ganglia_drop: float
    temporal_gain: float
    seed: int

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class MicrocircuitTrial:
    """One simulated trial of the selected microcircuit."""

    trial_index: int
    visual_drive: float
    visual_excitation: float
    visual_inhibition: float
    basal_gate: float
    action_logit: float
    action_probability: float
    action: int


@dataclass(frozen=True)
class MicrocircuitSessionValidation:
    """Microcircuit projection for one real Allen session.

    The validation layer does not refit parameters per session. It applies the
    robust-session calibration to held-out real-session trial rates and asks
    whether the resulting circuit state tracks the independent stability label.
    """

    session_id: str
    status: str
    stability_score: float
    n_trials: int
    mean_visual_excitation: float
    mean_visual_inhibition: float
    mean_basal_gate: float
    mean_action_logit: float
    mean_action_probability: float


@dataclass(frozen=True)
class MicrocircuitPerturbationResult:
    """Effect of one in-silico subpopulation perturbation."""

    perturbation: str
    mean_action_probability: float
    drop_from_intact: float


@dataclass(frozen=True)
class MicrocircuitReport:
    """Full selected-microcircuit simulation report."""

    calibration: MicrocircuitCalibration
    intact_mean_action_probability: float
    perturbations: list[MicrocircuitPerturbationResult]
    trials: list[MicrocircuitTrial]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "calibration": self.calibration.to_dict(),
            "intact_mean_action_probability": self.intact_mean_action_probability,
            "perturbations": [asdict(item) for item in self.perturbations],
            "trials": [asdict(item) for item in self.trials],
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class MicrocircuitValidationReport:
    """External validation of the selected microcircuit against session stability."""

    calibration: MicrocircuitCalibration
    sessions: list[MicrocircuitSessionValidation]
    group_mean_action_probability: dict[str, float]
    group_mean_stability_score: dict[str, float]
    robust_minus_fragile_probability: float | None
    robust_minus_mixed_probability: float | None
    probability_stability_correlation: float | None
    decision: str
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "calibration": self.calibration.to_dict(),
            "sessions": [asdict(item) for item in self.sessions],
            "group_mean_action_probability": dict(self.group_mean_action_probability),
            "group_mean_stability_score": dict(self.group_mean_stability_score),
            "robust_minus_fragile_probability": self.robust_minus_fragile_probability,
            "robust_minus_mixed_probability": self.robust_minus_mixed_probability,
            "probability_stability_correlation": self.probability_stability_correlation,
            "decision": self.decision,
            "warnings": list(self.warnings),
        }


def calibrate_microcircuit_from_sessions(
    sessions: list[Session],
    *,
    robust_session_ids: list[str],
    target_name: str = "go_response",
    window_name: str = "pre_response",
    visual_cortex_drop: float,
    basal_ganglia_drop: float,
    temporal_gain: float,
    seed: int = 101,
) -> MicrocircuitCalibration:
    """Calibrate region means from robust normalized sessions.

    Only robust sessions are used because the microcircuit layer should be
    anchored to the most stable empirical subset. This avoids fitting a
    mechanistic story to sessions the controls already marked as fragile.
    """
    selected = [session for session in sessions if session.session_id in set(robust_session_ids)]
    if not selected:
        raise ValueError("No robust sessions available for microcircuit calibration")
    values = {"visual_cortex": [], "basal_ganglia": []}
    for session in selected:
        for trial in session.trials:
            temporal = trial.metadata.get("region_rates_by_window", {})
            if not isinstance(temporal, dict):
                continue
            rates = temporal.get(window_name, {})
            if not isinstance(rates, dict):
                continue
            for region in values:
                if region in rates:
                    values[region].append(float(rates[region]))
    means = {
        region: sum(region_values) / len(region_values)
        for region, region_values in values.items()
        if region_values
    }
    if "visual_cortex" not in means:
        raise ValueError("Robust sessions do not contain visual_cortex pre-response rates")
    means.setdefault("basal_ganglia", 0.0)
    return MicrocircuitCalibration(
        target_name=target_name,
        window_name=window_name,
        robust_session_ids=sorted(robust_session_ids),
        region_means=means,
        visual_cortex_drop=visual_cortex_drop,
        basal_ganglia_drop=basal_ganglia_drop,
        temporal_gain=temporal_gain,
        seed=seed,
    )


def validate_microcircuit_against_stability(
    calibration: MicrocircuitCalibration,
    sessions: list[Session],
    *,
    stability_rows: list[dict[str, object]],
) -> MicrocircuitValidationReport:
    """Project real sessions through the calibrated circuit and compare labels.

    This is intentionally a validation step rather than another fitting step:
    the robust sessions define the circuit reference point, and every available
    stability-matrix session is then scored with those fixed parameters. The
    main scientific question is whether circuit-derived action probability is
    higher for empirically robust sessions than for fragile/mixed sessions.
    """
    if not sessions:
        raise ValueError("At least one session is required for microcircuit validation")
    stability_by_id = {str(row["session_id"]): row for row in stability_rows}
    validations = []
    for session in sorted(sessions, key=lambda item: item.session_id):
        row = stability_by_id.get(session.session_id)
        if row is None:
            continue
        validations.append(
            _validate_session(
                calibration,
                session,
                status=str(row["status"]),
                stability_score=float(row["stability_score"]),
            )
        )
    if not validations:
        raise ValueError("No sessions overlap the stability rows")

    group_probability = _group_mean(
        validations,
        key=lambda item: item.status,
        value=lambda item: item.mean_action_probability,
    )
    group_stability = _group_mean(
        validations,
        key=lambda item: item.status,
        value=lambda item: item.stability_score,
    )
    robust_minus_fragile = _difference(group_probability, "robust", "fragile")
    robust_minus_mixed = _difference(group_probability, "robust", "mixed")
    correlation = _pearson(
        [item.mean_action_probability for item in validations],
        [item.stability_score for item in validations],
    )

    warnings = []
    if len(validations) < 10:
        warnings.append("Validation has fewer than 10 overlapping sessions")
    if robust_minus_fragile is not None and robust_minus_fragile < 0.01:
        warnings.append("Robust-vs-fragile microcircuit separation is small")
    if correlation is not None and correlation < 0.25:
        warnings.append("Microcircuit probability weakly tracks stability score")

    decision = _validation_decision(group_probability, robust_minus_fragile, correlation)
    return MicrocircuitValidationReport(
        calibration=calibration,
        sessions=validations,
        group_mean_action_probability=group_probability,
        group_mean_stability_score=group_stability,
        robust_minus_fragile_probability=robust_minus_fragile,
        robust_minus_mixed_probability=robust_minus_mixed,
        probability_stability_correlation=correlation,
        decision=decision,
        warnings=warnings,
    )


def run_selected_microcircuit(
    calibration: MicrocircuitCalibration,
    *,
    n_trials: int = 300,
    perturbations: list[str] | None = None,
) -> MicrocircuitReport:
    """Simulate intact and perturbed selected microcircuit trials."""
    if n_trials <= 0:
        raise ValueError("n_trials must be positive")
    perturbations = perturbations or ["visual_excitation", "visual_inhibition", "basal_gate"]
    intact_trials = _simulate_trials(calibration, n_trials=n_trials, perturbation=None)
    intact_mean = sum(trial.action_probability for trial in intact_trials) / len(intact_trials)
    perturbation_results = []
    for perturbation in perturbations:
        perturbed = _simulate_trials(calibration, n_trials=n_trials, perturbation=perturbation)
        mean_probability = sum(trial.action_probability for trial in perturbed) / len(perturbed)
        perturbation_results.append(
            MicrocircuitPerturbationResult(
                perturbation=perturbation,
                mean_action_probability=mean_probability,
                drop_from_intact=intact_mean - mean_probability,
            )
        )
    warnings = []
    if calibration.basal_ganglia_drop <= 0.0:
        warnings.append("Basal-ganglia edge is weak or absent in calibration")
    if calibration.temporal_gain <= 0.0:
        warnings.append("Temporal gain is non-positive; microcircuit should not be interpreted")
    if perturbation_results and max(result.drop_from_intact for result in perturbation_results) < 0.01:
        warnings.append("Perturbation effects are very small; microcircuit is weakly sensitive")
    return MicrocircuitReport(
        calibration=calibration,
        intact_mean_action_probability=intact_mean,
        perturbations=perturbation_results,
        trials=intact_trials,
        warnings=warnings,
    )


def _simulate_trials(
    calibration: MicrocircuitCalibration,
    *,
    n_trials: int,
    perturbation: str | None,
) -> list[MicrocircuitTrial]:
    """Simulate a small visual-cortex / basal-ganglia circuit."""
    rng = random.Random(calibration.seed + _perturbation_offset(perturbation))
    visual_mean = calibration.region_means.get("visual_cortex", 0.0)
    basal_mean = calibration.region_means.get("basal_ganglia", 0.0)
    visual_scale = max(0.05, abs(visual_mean) * 0.10)
    basal_scale = max(0.05, abs(basal_mean) * 0.10)
    trials = []
    for trial_index in range(n_trials):
        visual_drive = rng.gauss(visual_mean, visual_scale)
        basal_context = rng.gauss(basal_mean, basal_scale)
        visual_centered = (visual_drive - visual_mean) / visual_scale
        basal_centered = (basal_context - basal_mean) / basal_scale
        # Work on centered, dimensionless signals. Raw firing-rate means can be
        # very different across regions; using them directly would saturate the
        # small mechanistic scaffold and make perturbations uninformative.
        visual_excitation = _sigmoid(1.0 + 0.8 * visual_centered)
        visual_inhibition = 0.5 * _sigmoid(0.6 * visual_centered)
        basal_gate = _sigmoid(0.6 * visual_excitation + 0.8 * basal_centered)
        if perturbation == "visual_excitation":
            visual_excitation *= 0.2
        elif perturbation == "visual_inhibition":
            visual_inhibition *= 0.2
        elif perturbation == "basal_gate":
            basal_gate *= 0.2
        action_logit = (
            1.6 * calibration.temporal_gain
            + 2.5 * calibration.visual_cortex_drop * visual_excitation
            - 1.0 * calibration.visual_cortex_drop * visual_inhibition
            + 2.0 * calibration.basal_ganglia_drop * basal_gate
        )
        action_probability = _sigmoid(action_logit)
        trials.append(
            MicrocircuitTrial(
                trial_index=trial_index,
                visual_drive=visual_drive,
                visual_excitation=visual_excitation,
                visual_inhibition=visual_inhibition,
                basal_gate=basal_gate,
                action_logit=action_logit,
                action_probability=action_probability,
                action=int(rng.random() < action_probability),
            )
        )
    return trials


def _validate_session(
    calibration: MicrocircuitCalibration,
    session: Session,
    *,
    status: str,
    stability_score: float,
) -> MicrocircuitSessionValidation:
    """Score one real session with the fixed robust-session microcircuit."""
    projected = [
        _project_trial(calibration, trial)
        for trial in session.trials
        if _has_window_rates(trial, calibration.window_name)
    ]
    if not projected:
        raise ValueError(f"Session {session.session_id} has no {calibration.window_name} rates")
    return MicrocircuitSessionValidation(
        session_id=session.session_id,
        status=status,
        stability_score=stability_score,
        n_trials=len(projected),
        mean_visual_excitation=_mean(item.visual_excitation for item in projected),
        mean_visual_inhibition=_mean(item.visual_inhibition for item in projected),
        mean_basal_gate=_mean(item.basal_gate for item in projected),
        mean_action_logit=_mean(item.action_logit for item in projected),
        mean_action_probability=_mean(item.action_probability for item in projected),
    )


def _project_trial(calibration: MicrocircuitCalibration, trial: Trial) -> MicrocircuitTrial:
    """Map one observed trial into the microcircuit state space."""
    rates_by_window = trial.metadata.get("region_rates_by_window", {})
    rates = rates_by_window.get(calibration.window_name, {})
    visual_mean = calibration.region_means.get("visual_cortex", 0.0)
    basal_mean = calibration.region_means.get("basal_ganglia", 0.0)
    visual_scale = max(0.05, abs(visual_mean) * 0.10)
    basal_scale = max(0.05, abs(basal_mean) * 0.10)
    visual_drive = float(rates.get("visual_cortex", visual_mean))
    basal_context = float(rates.get("basal_ganglia", basal_mean))
    visual_centered = (visual_drive - visual_mean) / visual_scale
    basal_centered = (basal_context - basal_mean) / basal_scale

    # Use the same fixed equations as the in-silico simulation. Keeping this
    # path shared makes the validation a test of generalization, not a hidden
    # second model fitted to the stability labels.
    visual_excitation = _sigmoid(1.0 + 0.8 * visual_centered)
    visual_inhibition = 0.5 * _sigmoid(0.6 * visual_centered)
    basal_gate = _sigmoid(0.6 * visual_excitation + 0.8 * basal_centered)
    action_logit = (
        1.6 * calibration.temporal_gain
        + 2.5 * calibration.visual_cortex_drop * visual_excitation
        - 1.0 * calibration.visual_cortex_drop * visual_inhibition
        + 2.0 * calibration.basal_ganglia_drop * basal_gate
    )
    action_probability = _sigmoid(action_logit)
    return MicrocircuitTrial(
        trial_index=int(trial.trial_id),
        visual_drive=visual_drive,
        visual_excitation=visual_excitation,
        visual_inhibition=visual_inhibition,
        basal_gate=basal_gate,
        action_logit=action_logit,
        action_probability=action_probability,
        action=int(action_probability >= 0.5),
    )


def _has_window_rates(trial: Trial, window_name: str) -> bool:
    rates_by_window = trial.metadata.get("region_rates_by_window", {})
    return isinstance(rates_by_window, dict) and isinstance(rates_by_window.get(window_name), dict)


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _perturbation_offset(perturbation: str | None) -> int:
    if perturbation is None:
        return 0
    return sum(ord(char) for char in perturbation)


def _mean(values: Iterable[float]) -> float:
    numbers = list(values)
    if not numbers:
        raise ValueError("Cannot compute mean of empty values")
    return sum(numbers) / len(numbers)


def _group_mean(
    items: list[MicrocircuitSessionValidation],
    *,
    key: Callable[[MicrocircuitSessionValidation], str],
    value: Callable[[MicrocircuitSessionValidation], float],
) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for item in items:
        grouped.setdefault(str(key(item)), []).append(float(value(item)))
    return {name: sum(values) / len(values) for name, values in sorted(grouped.items())}


def _difference(values: dict[str, float], left: str, right: str) -> float | None:
    if left not in values or right not in values:
        return None
    return values[left] - values[right]


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    centered_x = [x - mean_x for x in xs]
    centered_y = [y - mean_y for y in ys]
    denom_x = math.sqrt(sum(x * x for x in centered_x))
    denom_y = math.sqrt(sum(y * y for y in centered_y))
    if denom_x == 0.0 or denom_y == 0.0:
        return None
    return sum(x * y for x, y in zip(centered_x, centered_y)) / (denom_x * denom_y)


def _validation_decision(
    group_probability: dict[str, float],
    robust_minus_fragile: float | None,
    correlation: float | None,
) -> str:
    robust = group_probability.get("robust")
    mixed = group_probability.get("mixed")
    fragile = group_probability.get("fragile")
    if (
        robust is not None
        and mixed is not None
        and fragile is not None
        and robust > mixed > fragile
        and robust_minus_fragile is not None
        and robust_minus_fragile >= 0.02
        and correlation is not None
        and correlation >= 0.40
    ):
        return "supports_stability_gradient"
    if (
        robust_minus_fragile is not None
        and robust_minus_fragile > 0.0
        and correlation is not None
        and correlation >= 0.40
    ):
        return "weak_partial_robust_fragile_alignment"
    if robust_minus_fragile is not None and robust_minus_fragile > 0.0:
        return "partial_robust_fragile_alignment"
    return "no_external_stability_alignment"
