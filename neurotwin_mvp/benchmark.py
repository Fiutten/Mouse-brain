"""Transparent behavioral benchmarks for normalized neural sessions.

The goal is not to maximize accuracy with hidden machinery. The first real-data
benchmark should answer a sharper question: do neural region-rate features add
predictive signal beyond trivial, task-aware and behavioral-history baselines
under a leakage-conscious split?
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import random

from .baselines import MajorityChoiceBaseline, StimulusRuleBaseline, evaluate_classifier
from .behavioral_targets import TargetName, materialize_target_session
from .data import Session, Trial, train_test_split


@dataclass(frozen=True)
class BenchmarkResult:
    """Held-out evaluation result for one model."""

    name: str
    accuracy: float
    log_loss: float | None
    n_train: int
    n_test: int
    details: dict[str, float]


@dataclass(frozen=True)
class BenchmarkSuite:
    """Full benchmark report for a normalized session."""

    session_id: str
    dataset: str
    target_name: str
    train_fraction: float
    results: list[BenchmarkResult]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class NeuralGainPermutationReport:
    """Permutation test for neural-feature gain over a non-neural baseline."""

    session_id: str
    dataset: str
    target_name: str
    n_permutations: int
    seed: int
    baseline_balanced_accuracy: float
    observed_balanced_accuracy: float
    observed_gain: float
    null_gain_mean: float
    null_gain_std: float
    p_value: float
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class SplitGainResult:
    """One chronological split comparing non-neural and neural models."""

    split_index: int
    n_train: int
    n_test: int
    baseline_balanced_accuracy: float
    neural_balanced_accuracy: float
    gain: float


@dataclass(frozen=True)
class MultiSplitReport:
    """Repeated chronological validation of neural gain."""

    session_id: str
    dataset: str
    target_name: str
    split_results: list[SplitGainResult]
    mean_gain: float
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class RegionalAblationResult:
    """Predictive effect of removing one coarse region from the neural model."""

    region: str
    full_balanced_accuracy: float
    ablated_balanced_accuracy: float
    drop_from_full: float


@dataclass(frozen=True)
class RegionalAblationReport:
    """Leave-one-region-out benchmark for one target/session."""

    session_id: str
    dataset: str
    target_name: str
    baseline_balanced_accuracy: float
    full_neural_balanced_accuracy: float
    full_neural_gain: float
    region_results: list[RegionalAblationResult]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemporalWindowResult:
    """Predictive gain for one temporal neural window."""

    window_name: str
    balanced_accuracy: float
    gain_over_baseline: float
    n_region_features: int


@dataclass(frozen=True)
class TemporalWindowReport:
    """Benchmark neural predictivity across trial time windows."""

    session_id: str
    dataset: str
    target_name: str
    baseline_balanced_accuracy: float
    window_results: list[TemporalWindowResult]
    all_windows_balanced_accuracy: float
    all_windows_gain: float
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemporalWindowPermutationReport:
    """Permutation test for one temporal neural-window gain."""

    session_id: str
    dataset: str
    target_name: str
    window_name: str
    n_permutations: int
    seed: int
    baseline_balanced_accuracy: float
    observed_balanced_accuracy: float
    observed_gain: float
    null_gain_mean: float
    null_gain_std: float
    p_value: float
    valid_trial_fraction: float
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class TemporalRegionalAblationResult:
    """Predictive effect of removing one region from one temporal window."""

    region: str
    window_name: str
    full_balanced_accuracy: float
    ablated_balanced_accuracy: float
    drop_from_full: float


@dataclass(frozen=True)
class TemporalRegionalAblationReport:
    """Leave-one-region-out benchmark within one temporal neural window."""

    session_id: str
    dataset: str
    target_name: str
    window_name: str
    baseline_balanced_accuracy: float
    full_window_balanced_accuracy: float
    full_window_gain: float
    region_results: list[TemporalRegionalAblationResult]
    warnings: list[str]

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return asdict(self)


class LogisticRegressionClassifier:
    """Small deterministic logistic classifier with standardized features.

    This avoids adding scikit-learn just for the first benchmark. It is adequate
    for a transparent sanity check, not a replacement for later stronger ML
    baselines.
    """

    def __init__(
        self,
        name: str,
        feature_names: list[str],
        learning_rate: float = 0.08,
        l2: float = 0.01,
        epochs: int = 600,
    ) -> None:
        if not feature_names:
            raise ValueError("feature_names must not be empty")
        self.name = name
        self.feature_names = feature_names
        self.learning_rate = learning_rate
        self.l2 = l2
        self.epochs = epochs
        self.means: list[float] = []
        self.scales: list[float] = []
        self.weights: list[float] = []
        self.bias = 0.0

    def fit(self, trials: list[Trial]) -> None:
        """Fit standardized logistic regression by batch gradient descent."""
        if not trials:
            raise ValueError("Cannot fit logistic model on empty trials")
        raw = [self._raw_features(trial) for trial in trials]
        self.means = [sum(row[j] for row in raw) / len(raw) for j in range(len(self.feature_names))]
        self.scales = []
        for j, mean in enumerate(self.means):
            variance = sum((row[j] - mean) ** 2 for row in raw) / len(raw)
            self.scales.append(math.sqrt(variance) or 1.0)
        x = [self._standardize(row) for row in raw]
        y = [trial.choice for trial in trials]
        self.weights = [0.0 for _ in self.feature_names]
        self.bias = _logit(sum(y) / len(y))

        for _ in range(self.epochs):
            grad_w = [0.0 for _ in self.weights]
            grad_b = 0.0
            for row, target in zip(x, y, strict=True):
                pred = _sigmoid(self.bias + sum(w * value for w, value in zip(self.weights, row, strict=True)))
                error = pred - target
                grad_b += error
                for j, value in enumerate(row):
                    grad_w[j] += error * value
            n = len(x)
            self.bias -= self.learning_rate * grad_b / n
            for j in range(len(self.weights)):
                grad = grad_w[j] / n + self.l2 * self.weights[j]
                self.weights[j] -= self.learning_rate * grad

    def predict_probability(self, trial: Trial) -> float:
        """Predict P(choice=1) for one trial."""
        row = self._standardize(self._raw_features(trial))
        return _sigmoid(self.bias + sum(w * value for w, value in zip(self.weights, row, strict=True)))

    def predict(self, trial: Trial) -> int:
        """Predict binary choice from probability threshold 0.5."""
        return int(self.predict_probability(trial) >= 0.5)

    def _raw_features(self, trial: Trial) -> list[float]:
        values = []
        for name in self.feature_names:
            if name == "stimulus":
                values.append(trial.stimulus)
            elif name == "latency_ms":
                values.append(trial.latency_ms)
            elif name == "engagement":
                values.append(trial.engagement)
            elif name.startswith("region:"):
                values.append(trial.region_rates.get(name.removeprefix("region:"), 0.0))
            else:
                raise ValueError(f"Unsupported feature: {name}")
        return values

    def _standardize(self, row: list[float]) -> list[float]:
        return [(value - mean) / scale for value, mean, scale in zip(row, self.means, self.scales, strict=True)]


class DictLogisticRegressionClassifier:
    """Logistic regression for sparse task/history/image feature dictionaries.

    The model learns its feature vocabulary from training rows only. This is
    important for image identity features: a category appearing only in held-out
    trials must not create a trained coefficient because that would leak test
    information into the model specification.
    """

    def __init__(
        self,
        name: str,
        learning_rate: float = 0.08,
        l2: float = 0.01,
        epochs: int = 600,
    ) -> None:
        self.name = name
        self.learning_rate = learning_rate
        self.l2 = l2
        self.epochs = epochs
        self.feature_names: list[str] = []
        self.means: list[float] = []
        self.scales: list[float] = []
        self.weights: list[float] = []
        self.bias = 0.0

    def fit(self, rows: list[dict[str, float]], targets: list[int]) -> None:
        """Fit on precomputed feature rows and binary choice targets."""
        if not rows:
            raise ValueError("Cannot fit logistic model on empty rows")
        if len(rows) != len(targets):
            raise ValueError("rows and targets must have the same length")
        self.feature_names = sorted({key for row in rows for key in row})
        if not self.feature_names:
            raise ValueError("At least one feature is required")
        matrix = [self._vectorize(row) for row in rows]
        self.means = [
            sum(row[j] for row in matrix) / len(matrix)
            for j in range(len(self.feature_names))
        ]
        self.scales = []
        for j, mean in enumerate(self.means):
            variance = sum((row[j] - mean) ** 2 for row in matrix) / len(matrix)
            self.scales.append(math.sqrt(variance) or 1.0)
        x = [self._standardize(row) for row in matrix]
        self.weights = [0.0 for _ in self.feature_names]
        self.bias = _logit(sum(targets) / len(targets))

        for _ in range(self.epochs):
            grad_w = [0.0 for _ in self.weights]
            grad_b = 0.0
            for row, target in zip(x, targets, strict=True):
                pred = _sigmoid(self.bias + sum(w * value for w, value in zip(self.weights, row, strict=True)))
                error = pred - target
                grad_b += error
                for j, value in enumerate(row):
                    grad_w[j] += error * value
            n = len(x)
            self.bias -= self.learning_rate * grad_b / n
            for j in range(len(self.weights)):
                grad = grad_w[j] / n + self.l2 * self.weights[j]
                self.weights[j] -= self.learning_rate * grad

    def predict_probability(self, row: dict[str, float]) -> float:
        """Predict P(choice=1) for one precomputed feature row."""
        vector = self._standardize(self._vectorize(row))
        return _sigmoid(self.bias + sum(w * value for w, value in zip(self.weights, vector, strict=True)))

    def _vectorize(self, row: dict[str, float]) -> list[float]:
        return [float(row.get(name, 0.0)) for name in self.feature_names]

    def _standardize(self, row: list[float]) -> list[float]:
        return [(value - mean) / scale for value, mean, scale in zip(row, self.means, self.scales, strict=True)]


def run_choice_benchmark(session: Session, train_fraction: float = 0.7) -> BenchmarkSuite:
    """Run leakage-conscious behavioral benchmarks on a normalized session."""
    return run_target_benchmark(session, target_name="choice", train_fraction=train_fraction)


def run_target_benchmark(
    session: Session,
    target_name: TargetName = "choice",
    train_fraction: float = 0.7,
) -> BenchmarkSuite:
    """Run leakage-conscious benchmarks for one explicit binary target.

    `choice` preserves the historical behavior. Task-native targets such as
    `go_response` are first materialized into a filtered session so the model,
    split and metric code stays identical across target definitions.
    """
    session = materialize_target_session(session, target_name)
    train, test = train_test_split(session, train_fraction)
    split = len(train)
    results: list[BenchmarkResult] = []
    warnings: list[str] = []

    for model in (MajorityChoiceBaseline(), StimulusRuleBaseline()):
        report = evaluate_classifier(model, train, test)
        predictions = [model.predict(trial) for trial in test]
        results.append(
            BenchmarkResult(
                name=report.name,
                accuracy=report.accuracy,
                log_loss=None,
                n_train=report.n_train,
                n_test=report.n_test,
                details=report.details
                | {"balanced_accuracy": _balanced_accuracy([trial.choice for trial in test], predictions)},
            )
        )

    logistic_specs = [
        ("logistic_stimulus", ["stimulus"]),
        ("logistic_region_rates", [f"region:{region}" for region in session.region_names]),
        (
            "logistic_stimulus_region_rates",
            ["stimulus"] + [f"region:{region}" for region in session.region_names],
        ),
    ]
    for name, features in logistic_specs:
        model = LogisticRegressionClassifier(name=name, feature_names=features)
        model.fit(train)
        results.append(_evaluate_probability_model(model, train, test))

    dict_specs = [
        ("logistic_task_compact_image", {"task": True, "compact_image": True}),
        ("logistic_behavior_history", {"history": True}),
        (
            "logistic_task_compact_image_history",
            {"task": True, "compact_image": True, "history": True},
        ),
        (
            "logistic_task_compact_image_history_region_rates",
            {"task": True, "compact_image": True, "history": True, "regions": True},
        ),
    ]
    for name, options in dict_specs:
        rows = _sequence_feature_rows(session.trials, session.region_names, **options)
        model = DictLogisticRegressionClassifier(name=name)
        model.fit(rows[:split], [trial.choice for trial in train])
        results.append(_evaluate_dict_probability_model(model, rows[split:], train, test))

    neural_results = [result for result in results if "region_rates" in result.name]
    non_neural_results = [result for result in results if "region_rates" not in result.name]
    best_neural = max(neural_results, key=_balanced_result_accuracy)
    best_non_neural = max(non_neural_results, key=_balanced_result_accuracy)
    if _balanced_result_accuracy(best_neural) <= _balanced_result_accuracy(best_non_neural):
        warnings.append(
            "Neural region-rate features did not beat the best non-neural baseline in balanced accuracy"
        )
    for result in results:
        n_features = result.details.get("n_features")
        if n_features is not None and n_features > result.n_train / 2:
            warnings.append(
                f"{result.name} is high-dimensional relative to training trials; interpret as exploratory"
            )

    return BenchmarkSuite(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        train_fraction=train_fraction,
        results=results,
        warnings=warnings,
    )


def run_neural_gain_permutation_test(
    session: Session,
    train_fraction: float = 0.7,
    n_permutations: int = 200,
    seed: int = 17,
    target_name: TargetName = "choice",
) -> NeuralGainPermutationReport:
    """Test whether region rates add more signal than random aligned rates.

    The non-neural baseline uses task, image and behavioral-history features.
    The observed model adds region-rate features. The null distribution keeps
    the non-neural rows fixed but shuffles region-rate rows across trials before
    fitting the full model. This destroys trial-level neural/behavior alignment
    while preserving the marginal distribution of regional activity.
    """
    if n_permutations <= 0:
        raise ValueError("n_permutations must be positive")
    session = materialize_target_session(session, target_name)
    train, test = train_test_split(session, train_fraction)
    split = len(train)
    targets_train = [trial.choice for trial in train]

    baseline_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=False,
    )
    region_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=False,
        image=False,
        history=False,
        regions=True,
    )

    baseline_result = _fit_eval_dict_model(
        "permutation_baseline_task_image_history",
        baseline_rows[:split],
        baseline_rows[split:],
        train,
        test,
    )
    observed_rows = _merge_feature_rows(baseline_rows, region_rows)
    observed_result = _fit_eval_dict_model(
        "permutation_observed_with_region_rates",
        observed_rows[:split],
        observed_rows[split:],
        train,
        test,
    )
    baseline_balanced = _balanced_result_accuracy(baseline_result)
    observed_balanced = _balanced_result_accuracy(observed_result)
    observed_gain = observed_balanced - baseline_balanced

    rng = random.Random(seed)
    null_gains = []
    indices = list(range(len(session.trials)))
    for _ in range(n_permutations):
        shuffled = list(indices)
        rng.shuffle(shuffled)
        shuffled_region_rows = [region_rows[index] for index in shuffled]
        permuted_rows = _merge_feature_rows(baseline_rows, shuffled_region_rows)
        permuted_result = _fit_eval_dict_model(
            "permutation_null_with_shuffled_region_rates",
            permuted_rows[:split],
            permuted_rows[split:],
            train,
            test,
        )
        null_gains.append(_balanced_result_accuracy(permuted_result) - baseline_balanced)

    null_mean = sum(null_gains) / len(null_gains)
    null_variance = sum((value - null_mean) ** 2 for value in null_gains) / len(null_gains)
    p_value = (1 + sum(1 for value in null_gains if value >= observed_gain)) / (n_permutations + 1)
    warnings = []
    if observed_gain <= 0:
        warnings.append("Observed neural gain is non-positive")
    if p_value >= 0.05:
        warnings.append("Permutation test does not reject shuffled-neural null at alpha=0.05")
    n_observed_features = observed_result.details.get("n_features", 0.0)
    if n_observed_features > len(train) / 2:
        warnings.append("Observed full model is high-dimensional relative to training trials")

    return NeuralGainPermutationReport(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        n_permutations=n_permutations,
        seed=seed,
        baseline_balanced_accuracy=baseline_balanced,
        observed_balanced_accuracy=observed_balanced,
        observed_gain=observed_gain,
        null_gain_mean=null_mean,
        null_gain_std=math.sqrt(null_variance),
        p_value=p_value,
        warnings=warnings,
    )


def run_multisplit_neural_gain(
    session: Session,
    n_splits: int = 4,
    initial_train_fraction: float = 0.50,
    test_fraction: float = 0.15,
    target_name: TargetName = "choice",
) -> MultiSplitReport:
    """Estimate neural gain across repeated chronological splits.

    This is stricter than a single split but still respects temporal ordering:
    each split trains on earlier trials and tests on a later contiguous block.
    It compares a compact non-neural task/image/history model with the same
    model plus region-rate features.
    """
    session = materialize_target_session(session, target_name)
    split_ranges = _chronological_split_ranges(
        n_trials=len(session.trials),
        n_splits=n_splits,
        initial_train_fraction=initial_train_fraction,
        test_fraction=test_fraction,
    )
    baseline_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
    )
    neural_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=True,
    )
    split_results = []
    for split_index, (train_end, test_start, test_end) in enumerate(split_ranges):
        train = session.trials[:train_end]
        test = session.trials[test_start:test_end]
        baseline_result = _fit_eval_dict_model(
            "multisplit_baseline_task_compact_image_history",
            baseline_rows[:train_end],
            baseline_rows[test_start:test_end],
            train,
            test,
        )
        neural_result = _fit_eval_dict_model(
            "multisplit_neural_task_compact_image_history_region_rates",
            neural_rows[:train_end],
            neural_rows[test_start:test_end],
            train,
            test,
        )
        baseline_balanced = _balanced_result_accuracy(baseline_result)
        neural_balanced = _balanced_result_accuracy(neural_result)
        split_results.append(
            SplitGainResult(
                split_index=split_index,
                n_train=len(train),
                n_test=len(test),
                baseline_balanced_accuracy=baseline_balanced,
                neural_balanced_accuracy=neural_balanced,
                gain=neural_balanced - baseline_balanced,
            )
        )
    mean_gain = sum(item.gain for item in split_results) / len(split_results)
    warnings = []
    if mean_gain <= 0:
        warnings.append("Mean neural gain across chronological splits is non-positive")
    if len(session.trials) < 300:
        warnings.append("Session has fewer than 300 valid trials; split estimates are unstable")
    return MultiSplitReport(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        split_results=split_results,
        mean_gain=mean_gain,
        warnings=warnings,
    )


def run_regional_ablation(
    session: Session,
    train_fraction: float = 0.7,
    target_name: TargetName = "choice",
) -> RegionalAblationReport:
    """Estimate which coarse regions carry target-predictive signal.

    This is a feature ablation, not a biological lesion. It asks whether a
    region's recorded spike-rate feature improves held-out balanced accuracy
    beyond task, image and history covariates. The result is appropriate for
    prioritizing hypotheses, but it should not be interpreted as causal
    neuroscience without perturbation data or stronger controls.
    """
    session = materialize_target_session(session, target_name)
    train, test = train_test_split(session, train_fraction)
    split = len(train)
    baseline_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=False,
    )
    full_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=True,
    )
    baseline_result = _fit_eval_dict_model(
        "regional_ablation_baseline_task_image_history",
        baseline_rows[:split],
        baseline_rows[split:],
        train,
        test,
    )
    full_result = _fit_eval_dict_model(
        "regional_ablation_full_region_rates",
        full_rows[:split],
        full_rows[split:],
        train,
        test,
    )
    baseline_balanced = _balanced_result_accuracy(baseline_result)
    full_balanced = _balanced_result_accuracy(full_result)
    region_results: list[RegionalAblationResult] = []
    for region in session.region_names:
        ablated_rows = [
            {
                key: value
                for key, value in row.items()
                if key != f"region:{region}"
            }
            for row in full_rows
        ]
        ablated_result = _fit_eval_dict_model(
            f"regional_ablation_without_{region}",
            ablated_rows[:split],
            ablated_rows[split:],
            train,
            test,
        )
        ablated_balanced = _balanced_result_accuracy(ablated_result)
        region_results.append(
            RegionalAblationResult(
                region=region,
                full_balanced_accuracy=full_balanced,
                ablated_balanced_accuracy=ablated_balanced,
                drop_from_full=full_balanced - ablated_balanced,
            )
        )
    region_results.sort(key=lambda item: item.drop_from_full, reverse=True)
    warnings = []
    if full_balanced <= baseline_balanced:
        warnings.append("Full regional model does not beat the non-neural baseline")
    if len(session.trials) < 300:
        warnings.append("Session has fewer than 300 valid trials; ablation estimates are unstable")
    return RegionalAblationReport(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        baseline_balanced_accuracy=baseline_balanced,
        full_neural_balanced_accuracy=full_balanced,
        full_neural_gain=full_balanced - baseline_balanced,
        region_results=region_results,
        warnings=warnings,
    )


def run_temporal_window_benchmark(
    session: Session,
    train_fraction: float = 0.7,
    target_name: TargetName = "choice",
    window_names: list[str] | None = None,
) -> TemporalWindowReport:
    """Compare neural signal carried by baseline/stimulus/decision windows.

    Temporal features must be present in `trial.metadata["region_rates_by_window"]`.
    Older artifacts only contain stimulus-window `region_rates`, so this function
    fails explicitly instead of silently fabricating temporal structure.
    """
    session = materialize_target_session(session, target_name)
    window_names = window_names or ["baseline", "stimulus", "decision", "pre_response"]
    missing = [
        trial.trial_id
        for trial in session.trials
        if not _has_temporal_region_rates(trial, window_names)
    ]
    if missing:
        raise ValueError(
            "Session does not contain temporal region-rate windows for all trials; "
            "re-export with the temporal Allen normalizer before running this benchmark"
        )

    train, test = train_test_split(session, train_fraction)
    split = len(train)
    baseline_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=False,
    )
    baseline_result = _fit_eval_dict_model(
        "temporal_baseline_task_image_history",
        baseline_rows[:split],
        baseline_rows[split:],
        train,
        test,
    )
    baseline_balanced = _balanced_result_accuracy(baseline_result)

    window_results: list[TemporalWindowResult] = []
    all_temporal_rows = [dict(row) for row in baseline_rows]
    for window_name in window_names:
        temporal_rows = _temporal_region_feature_rows(
            session.trials,
            session.region_names,
            [window_name],
        )
        rows = _merge_feature_rows(baseline_rows, temporal_rows)
        result = _fit_eval_dict_model(
            f"temporal_window_{window_name}",
            rows[:split],
            rows[split:],
            train,
            test,
        )
        balanced = _balanced_result_accuracy(result)
        window_results.append(
            TemporalWindowResult(
                window_name=window_name,
                balanced_accuracy=balanced,
                gain_over_baseline=balanced - baseline_balanced,
                n_region_features=len(session.region_names),
            )
        )
        all_temporal_rows = _merge_feature_rows(all_temporal_rows, temporal_rows)

    all_result = _fit_eval_dict_model(
        "temporal_all_windows",
        all_temporal_rows[:split],
        all_temporal_rows[split:],
        train,
        test,
    )
    all_balanced = _balanced_result_accuracy(all_result)
    warnings = []
    if all_balanced <= baseline_balanced:
        warnings.append("All-window temporal model does not beat the non-neural baseline")
    if len(session.trials) < 300:
        warnings.append("Session has fewer than 300 valid trials; temporal estimates are unstable")
    return TemporalWindowReport(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        baseline_balanced_accuracy=baseline_balanced,
        window_results=window_results,
        all_windows_balanced_accuracy=all_balanced,
        all_windows_gain=all_balanced - baseline_balanced,
        warnings=warnings,
    )


def run_temporal_window_permutation_test(
    session: Session,
    window_name: str = "pre_response",
    train_fraction: float = 0.7,
    n_permutations: int = 200,
    seed: int = 31,
    target_name: TargetName = "choice",
) -> TemporalWindowPermutationReport:
    """Test whether one temporal window adds aligned neural signal.

    The baseline model uses task, compact image and behavioral history features.
    The observed model adds region-rate features from one temporal window. The
    null distribution shuffles those temporal rows across trials while keeping
    the non-neural rows fixed. This destroys trial-level neural/behavior
    alignment but preserves the window's marginal firing-rate distribution.
    """
    if n_permutations <= 0:
        raise ValueError("n_permutations must be positive")
    session = materialize_target_session(session, target_name)
    missing = [
        trial.trial_id
        for trial in session.trials
        if not _has_temporal_region_rates(trial, [window_name])
    ]
    if missing:
        raise ValueError(
            "Session does not contain the requested temporal region-rate window for all trials"
        )

    train, test = train_test_split(session, train_fraction)
    split = len(train)
    baseline_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=False,
    )
    temporal_rows = _temporal_region_feature_rows(session.trials, session.region_names, [window_name])
    baseline_result = _fit_eval_dict_model(
        f"temporal_permutation_baseline_{window_name}",
        baseline_rows[:split],
        baseline_rows[split:],
        train,
        test,
    )
    observed_rows = _merge_feature_rows(baseline_rows, temporal_rows)
    observed_result = _fit_eval_dict_model(
        f"temporal_permutation_observed_{window_name}",
        observed_rows[:split],
        observed_rows[split:],
        train,
        test,
    )
    baseline_balanced = _balanced_result_accuracy(baseline_result)
    observed_balanced = _balanced_result_accuracy(observed_result)
    observed_gain = observed_balanced - baseline_balanced

    rng = random.Random(seed)
    indices = list(range(len(session.trials)))
    null_gains = []
    for _ in range(n_permutations):
        shuffled = list(indices)
        rng.shuffle(shuffled)
        shuffled_temporal_rows = [temporal_rows[index] for index in shuffled]
        permuted_rows = _merge_feature_rows(baseline_rows, shuffled_temporal_rows)
        permuted_result = _fit_eval_dict_model(
            f"temporal_permutation_null_{window_name}",
            permuted_rows[:split],
            permuted_rows[split:],
            train,
            test,
        )
        null_gains.append(_balanced_result_accuracy(permuted_result) - baseline_balanced)

    null_mean = sum(null_gains) / len(null_gains)
    null_variance = sum((value - null_mean) ** 2 for value in null_gains) / len(null_gains)
    p_value = (1 + sum(1 for value in null_gains if value >= observed_gain)) / (n_permutations + 1)
    valid_fraction = _temporal_window_valid_fraction(session.trials, window_name)
    warnings = []
    if observed_gain <= 0.0:
        warnings.append("Observed temporal-window gain is non-positive")
    if p_value >= 0.05:
        warnings.append("Permutation test does not reject shuffled temporal-window null at alpha=0.05")
    if valid_fraction < 0.8:
        warnings.append("Temporal window has low valid-trial coverage")
    return TemporalWindowPermutationReport(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        window_name=window_name,
        n_permutations=n_permutations,
        seed=seed,
        baseline_balanced_accuracy=baseline_balanced,
        observed_balanced_accuracy=observed_balanced,
        observed_gain=observed_gain,
        null_gain_mean=null_mean,
        null_gain_std=math.sqrt(null_variance),
        p_value=p_value,
        valid_trial_fraction=valid_fraction,
        warnings=warnings,
    )


def run_temporal_regional_ablation(
    session: Session,
    window_name: str = "pre_response",
    train_fraction: float = 0.7,
    target_name: TargetName = "choice",
) -> TemporalRegionalAblationReport:
    """Estimate regional contributions inside one temporal window.

    This should be run only after the window itself shows evidence against a
    shuffled-alignment null. Otherwise region ranking can over-explain noise.
    The analysis is still a predictive feature ablation, not a causal lesion.
    """
    session = materialize_target_session(session, target_name)
    missing = [
        trial.trial_id
        for trial in session.trials
        if not _has_temporal_region_rates(trial, [window_name])
    ]
    if missing:
        raise ValueError(
            "Session does not contain the requested temporal region-rate window for all trials"
        )

    train, test = train_test_split(session, train_fraction)
    split = len(train)
    baseline_rows = _sequence_feature_rows(
        session.trials,
        session.region_names,
        task=True,
        compact_image=True,
        history=True,
        regions=False,
    )
    window_rows = _temporal_region_feature_rows(session.trials, session.region_names, [window_name])
    full_rows = _merge_feature_rows(baseline_rows, window_rows)
    baseline_result = _fit_eval_dict_model(
        f"temporal_regional_baseline_{window_name}",
        baseline_rows[:split],
        baseline_rows[split:],
        train,
        test,
    )
    full_result = _fit_eval_dict_model(
        f"temporal_regional_full_{window_name}",
        full_rows[:split],
        full_rows[split:],
        train,
        test,
    )
    baseline_balanced = _balanced_result_accuracy(baseline_result)
    full_balanced = _balanced_result_accuracy(full_result)
    region_results: list[TemporalRegionalAblationResult] = []
    for region in session.region_names:
        feature_name = f"region_window:{window_name}:{region}"
        ablated_window_rows = [
            {key: value for key, value in row.items() if key != feature_name}
            for row in window_rows
        ]
        ablated_rows = _merge_feature_rows(baseline_rows, ablated_window_rows)
        ablated_result = _fit_eval_dict_model(
            f"temporal_regional_without_{window_name}_{region}",
            ablated_rows[:split],
            ablated_rows[split:],
            train,
            test,
        )
        ablated_balanced = _balanced_result_accuracy(ablated_result)
        region_results.append(
            TemporalRegionalAblationResult(
                region=region,
                window_name=window_name,
                full_balanced_accuracy=full_balanced,
                ablated_balanced_accuracy=ablated_balanced,
                drop_from_full=full_balanced - ablated_balanced,
            )
        )
    region_results.sort(key=lambda item: item.drop_from_full, reverse=True)
    warnings = []
    if full_balanced <= baseline_balanced:
        warnings.append("Full temporal-window model does not beat the non-neural baseline")
    if _temporal_window_valid_fraction(session.trials, window_name) < 0.8:
        warnings.append("Temporal window has low valid-trial coverage")
    return TemporalRegionalAblationReport(
        session_id=session.session_id,
        dataset=session.dataset,
        target_name=target_name,
        window_name=window_name,
        baseline_balanced_accuracy=baseline_balanced,
        full_window_balanced_accuracy=full_balanced,
        full_window_gain=full_balanced - baseline_balanced,
        region_results=region_results,
        warnings=warnings,
    )


def _evaluate_probability_model(
    model: LogisticRegressionClassifier,
    train: list[Trial],
    test: list[Trial],
) -> BenchmarkResult:
    correct = 0
    losses = []
    predictions = []
    for trial in test:
        probability = min(1.0 - 1e-9, max(1e-9, model.predict_probability(trial)))
        prediction = int(probability >= 0.5)
        predictions.append(prediction)
        correct += int(prediction == trial.choice)
        losses.append(-(trial.choice * math.log(probability) + (1 - trial.choice) * math.log(1 - probability)))
    return BenchmarkResult(
        name=model.name,
        accuracy=correct / len(test),
        log_loss=sum(losses) / len(losses),
        n_train=len(train),
        n_test=len(test),
        details={
            f"weight:{name}": weight
            for name, weight in zip(model.feature_names, model.weights, strict=True)
        }
        | {"bias": model.bias, "balanced_accuracy": _balanced_accuracy([trial.choice for trial in test], predictions)},
    )


def _fit_eval_dict_model(
    name: str,
    train_rows: list[dict[str, float]],
    test_rows: list[dict[str, float]],
    train: list[Trial],
    test: list[Trial],
) -> BenchmarkResult:
    """Fit and evaluate one dictionary-feature model using existing machinery."""
    model = DictLogisticRegressionClassifier(name=name)
    model.fit(train_rows, [trial.choice for trial in train])
    return _evaluate_dict_probability_model(model, test_rows, train, test)


def _evaluate_dict_probability_model(
    model: DictLogisticRegressionClassifier,
    rows: list[dict[str, float]],
    train: list[Trial],
    test: list[Trial],
) -> BenchmarkResult:
    """Evaluate a dictionary-feature logistic model on held-out trials."""
    correct = 0
    losses = []
    predictions = []
    for row, trial in zip(rows, test, strict=True):
        probability = min(1.0 - 1e-9, max(1e-9, model.predict_probability(row)))
        prediction = int(probability >= 0.5)
        predictions.append(prediction)
        correct += int(prediction == trial.choice)
        losses.append(-(trial.choice * math.log(probability) + (1 - trial.choice) * math.log(1 - probability)))
    top_weights = _top_abs_weights(model.feature_names, model.weights, limit=12)
    return BenchmarkResult(
        name=model.name,
        accuracy=correct / len(test),
        log_loss=sum(losses) / len(losses),
        n_train=len(train),
        n_test=len(test),
        details={
            f"weight:{name}": weight for name, weight in top_weights
        }
        | {
            "bias": model.bias,
            "n_features": float(len(model.feature_names)),
            "balanced_accuracy": _balanced_accuracy([trial.choice for trial in test], predictions),
        },
    )


def _merge_feature_rows(
    left_rows: list[dict[str, float]],
    right_rows: list[dict[str, float]],
) -> list[dict[str, float]]:
    """Merge aligned feature dictionaries without mutating either input list."""
    if len(left_rows) != len(right_rows):
        raise ValueError("Feature row lists must have the same length")
    return [dict(left) | dict(right) for left, right in zip(left_rows, right_rows, strict=True)]


def _sequence_feature_rows(
    trials: list[Trial],
    region_names: list[str],
    task: bool = False,
    image: bool = False,
    compact_image: bool = False,
    history: bool = False,
    regions: bool = False,
) -> list[dict[str, float]]:
    """Build chronological feature rows from task metadata and neural rates.

    History features use the immediately preceding trial's observed outcome.
    This is a reasonable online behavioral baseline because, at trial `t`, the
    experimenter already knows trial `t-1`. It must still be reported separately
    because it is a strong non-neural competitor.
    """
    rows = []
    previous: Trial | None = None
    seen_initial_images: set[str] = set()
    seen_change_images: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    for trial in trials:
        row: dict[str, float] = {}
        if task:
            row["stimulus"] = trial.stimulus
            for key in ("is_change", "go", "catch"):
                row[f"task:{key}"] = _metadata_bool(trial, key)
        if image:
            initial = _metadata_str(trial, "initial_image_name")
            change = _metadata_str(trial, "change_image_name")
            if initial:
                row[f"initial_image:{initial}"] = 1.0
            if change:
                row[f"change_image:{change}"] = 1.0
            if initial and change:
                row[f"image_pair:{initial}->{change}"] = 1.0
        if compact_image:
            initial = _metadata_str(trial, "initial_image_name")
            change = _metadata_str(trial, "change_image_name")
            row["image:identity_changed"] = float(bool(initial and change and initial != change))
            row["image:initial_seen_before"] = float(bool(initial and initial in seen_initial_images))
            row["image:change_seen_before"] = float(bool(change and change in seen_change_images))
            row["image:pair_seen_before"] = float(
                bool(initial and change and (initial, change) in seen_pairs)
            )
        if history:
            if previous is None:
                row["history:prev_choice"] = 0.5
                row["history:prev_reward"] = 0.5
                row["history:prev_latency_ms"] = 0.0
                row["history:prev_hit"] = 0.0
                row["history:prev_false_alarm"] = 0.0
            else:
                row["history:prev_choice"] = float(previous.choice)
                row["history:prev_reward"] = float(previous.reward)
                row["history:prev_latency_ms"] = previous.latency_ms
                row["history:prev_hit"] = _metadata_bool(previous, "hit")
                row["history:prev_false_alarm"] = _metadata_bool(previous, "false_alarm")
        if regions:
            for region in region_names:
                row[f"region:{region}"] = trial.region_rates.get(region, 0.0)
        rows.append(row)
        initial = _metadata_str(trial, "initial_image_name")
        change = _metadata_str(trial, "change_image_name")
        if initial:
            seen_initial_images.add(initial)
        if change:
            seen_change_images.add(change)
        if initial and change:
            seen_pairs.add((initial, change))
        previous = trial
    return rows


def _has_temporal_region_rates(trial: Trial, window_names: list[str]) -> bool:
    """Return whether one trial carries all requested temporal neural windows."""
    temporal = trial.metadata.get("region_rates_by_window")
    if not isinstance(temporal, dict):
        return False
    return all(isinstance(temporal.get(window), dict) for window in window_names)


def _temporal_window_valid_fraction(trials: list[Trial], window_name: str) -> float:
    """Fraction of trials whose dynamic temporal window is valid."""
    if not trials:
        return 0.0
    valid = []
    for trial in trials:
        flags = trial.metadata.get("time_window_valid", {})
        if isinstance(flags, dict) and window_name in flags:
            valid.append(bool(flags[window_name]))
        else:
            # Old synthetic/test artifacts may not include validity flags. If
            # the temporal features exist, treat them as fixed-window valid.
            valid.append(_has_temporal_region_rates(trial, [window_name]))
    return sum(valid) / len(valid)


def _temporal_region_feature_rows(
    trials: list[Trial],
    region_names: list[str],
    window_names: list[str],
) -> list[dict[str, float]]:
    """Build feature rows from nested temporal region-rate metadata."""
    rows = []
    for trial in trials:
        temporal = trial.metadata.get("region_rates_by_window")
        if not isinstance(temporal, dict):
            raise ValueError("Trial is missing `region_rates_by_window` metadata")
        row = {}
        for window_name in window_names:
            window_rates = temporal.get(window_name)
            if not isinstance(window_rates, dict):
                raise ValueError(f"Trial is missing temporal window `{window_name}`")
            for region in region_names:
                row[f"region_window:{window_name}:{region}"] = float(window_rates.get(region, 0.0))
        rows.append(row)
    return rows


def _chronological_split_ranges(
    n_trials: int,
    n_splits: int,
    initial_train_fraction: float,
    test_fraction: float,
) -> list[tuple[int, int, int]]:
    """Create expanding-window chronological split ranges."""
    if n_splits <= 0:
        raise ValueError("n_splits must be positive")
    if not 0.0 < initial_train_fraction < 1.0:
        raise ValueError("initial_train_fraction must be between 0 and 1")
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be between 0 and 1")
    test_size = max(5, int(n_trials * test_fraction))
    initial_train = max(5, int(n_trials * initial_train_fraction))
    available_shift = n_trials - initial_train - test_size
    if available_shift < 0:
        raise ValueError("Not enough trials for requested chronological splits")
    step = max(1, available_shift // max(n_splits - 1, 1))
    ranges = []
    for split_index in range(n_splits):
        train_end = initial_train + split_index * step
        test_start = train_end
        test_end = min(test_start + test_size, n_trials)
        if test_end - test_start < 5:
            continue
        ranges.append((train_end, test_start, test_end))
    if not ranges:
        raise ValueError("No valid chronological splits were produced")
    return ranges


def _metadata_bool(trial: Trial, key: str) -> float:
    value = trial.metadata.get(key, False)
    if isinstance(value, str):
        return 1.0 if value.lower() == "true" else 0.0
    return 1.0 if bool(value) else 0.0


def _metadata_str(trial: Trial, key: str) -> str:
    value = trial.metadata.get(key, "")
    return "" if value is None else str(value)


def _top_abs_weights(
    feature_names: list[str],
    weights: list[float],
    limit: int,
) -> list[tuple[str, float]]:
    """Keep reports compact by storing only the largest absolute coefficients."""
    pairs = sorted(zip(feature_names, weights, strict=True), key=lambda item: abs(item[1]), reverse=True)
    return pairs[:limit]


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _logit(probability: float) -> float:
    probability = min(1.0 - 1e-9, max(1e-9, probability))
    return math.log(probability / (1.0 - probability))


def _balanced_accuracy(targets: list[int], predictions: list[int]) -> float:
    """Compute balanced accuracy for imbalanced binary choice labels."""
    recalls = []
    for label in (0, 1):
        total = sum(1 for target in targets if target == label)
        if total:
            correct = sum(
                1 for target, prediction in zip(targets, predictions, strict=True)
                if target == label and prediction == label
            )
            recalls.append(correct / total)
    if not recalls:
        raise ValueError("Cannot compute balanced accuracy without targets")
    return sum(recalls) / len(recalls)


def _balanced_result_accuracy(result: BenchmarkResult) -> float:
    return result.details["balanced_accuracy"]
