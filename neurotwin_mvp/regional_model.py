"""Level-0 regional dynamical model.

This is intentionally simple: it is a falsifiable scaffold for experiments, not
a biological claim. Regions are continuous state nodes with directed coupling,
external inputs, optional lesions, and a decision readout.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from .config import ModelConfig


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


@dataclass
class StepRecord:
    t: int
    state: dict[str, float]
    action_probability: float
    action: int


class RegionalModel:
    def __init__(self, config: ModelConfig, seed: int = 0) -> None:
        self.config = config
        self.rng = random.Random(seed)
        self.region_names = [region.name for region in config.regions]
        self.region_by_name = {region.name: region for region in config.regions}
        self.incoming = {name: [] for name in self.region_names}
        for connection in config.connections:
            self.incoming[connection.target].append(connection)
        self.reset()

    def reset(self) -> None:
        self.state = {name: 0.0 for name in self.region_names}

    def _validate_regions(self, regions: set[str], label: str) -> None:
        unknown = sorted(regions - set(self.region_names))
        if unknown:
            raise ValueError(f"Unknown {label} region(s): {unknown}")

    def step(
        self,
        external_inputs: dict[str, float] | None = None,
        lesions: set[str] | None = None,
    ) -> StepRecord:
        """Advance the regional model by one step.

        `lesions` are virtual in-silico interventions: selected regions are
        clamped to zero and incoming signals from them are ignored. They test
        whether the model architecture produces coherent counterfactual
        behavior. They are not clinical lesion simulations or biological
        causality evidence by themselves.
        """
        external_inputs = external_inputs or {}
        lesions = lesions or set()
        self._validate_regions(set(external_inputs), "input")
        self._validate_regions(lesions, "lesion")
        new_state: dict[str, float] = {}
        for name in self.region_names:
            region = self.region_by_name[name]
            if name in lesions:
                new_state[name] = 0.0
                continue
            drive = region.bias + external_inputs.get(name, 0.0)
            for connection in self.incoming[name]:
                if connection.source in lesions:
                    continue
                drive += connection.weight * self.state[connection.source]
            if self.config.noise:
                drive += self.rng.gauss(0.0, self.config.noise)
            effective_decay = max(0.0, min(1.0, region.decay * self.config.dt))
            candidate = (1.0 - effective_decay) * self.state[name] + effective_decay * math.tanh(drive)
            new_state[name] = max(-1.0, min(1.0, candidate))
        self.state = new_state
        probability = self.action_probability()
        action = 1 if self.rng.random() < probability else 0
        return StepRecord(t=0, state=dict(self.state), action_probability=probability, action=action)

    def action_probability(self) -> float:
        logit = 0.0
        for name, value in self.state.items():
            logit += self.region_by_name[name].readout * value
        return sigmoid(logit)

    def run_trial(
        self,
        stimulus: float,
        delay_steps: int,
        decision_steps: int,
        lesions: set[str] | None = None,
    ) -> list[StepRecord]:
        """Run one synthetic visual-decision trial.

        Optional virtual lesions ask whether disabling a region changes the
        model output in the expected direction. This remains an architecture
        check until validated against empirical perturbation evidence.
        """
        if delay_steps < 0:
            raise ValueError("delay_steps must be non-negative")
        if decision_steps <= 0:
            raise ValueError("decision_steps must be positive")
        records: list[StepRecord] = []
        for t in range(delay_steps + decision_steps):
            inputs = {}
            if t == 0:
                inputs["visual_thalamus"] = stimulus
            record = self.step(inputs, lesions)
            records.append(StepRecord(t=t, state=record.state, action_probability=record.action_probability, action=record.action))
        return records


def summarize_trial(records: list[StepRecord]) -> dict[str, float]:
    if not records:
        raise ValueError("Cannot summarize empty trial")
    final = records[-1]
    mean_activation = {
        name: sum(record.state[name] for record in records) / len(records)
        for name in final.state
    }
    return {
        "final_action_probability": final.action_probability,
        "final_action": float(final.action),
        **{f"mean_{name}": value for name, value in mean_activation.items()},
    }
