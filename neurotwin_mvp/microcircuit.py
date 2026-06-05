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
