"""Normalize Allen Visual Behavior Neuropixels sessions into core artifacts.

This module is designed to run inside the future `.venv-allen` environment,
where AllenSDK is available. It converts an Allen session object into the core
`Session`/`Trial` contract used by the simulation and experiment workflow.

The implementation is conservative:

- it requires explicit time windows;
- it maps Allen structure acronyms into coarse model regions;
- it aggregates recorded units into region-level firing-rate features;
- it writes a transparent `session.json` artifact consumed by the core env.

The normalizer can be tested with fake session objects, so the core repository
does not need AllenSDK just to verify the conversion logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any, Iterable

from .allen_selection import COARSE_REGION_MAP
from .artifacts import write_session_artifact
from .data import Session, Trial


@dataclass(frozen=True)
class TimeWindows:
    """Temporal windows, in seconds, used for trial-level neural features."""

    baseline_start: float = -0.250
    baseline_end: float = 0.0
    stimulus_start: float = 0.0
    stimulus_end: float = 0.250
    decision_start: float = 0.250
    decision_end: float = 0.750
    pre_response_start: float = 0.250
    pre_response_end: float = 0.750
    response_margin: float = 0.050

    def as_dict(self) -> dict[str, tuple[float, float]]:
        """Return named windows as `(start, end)` offsets in seconds."""
        return {
            "baseline": (self.baseline_start, self.baseline_end),
            "stimulus": (self.stimulus_start, self.stimulus_end),
            "decision": (self.decision_start, self.decision_end),
        }

    def validate(self) -> None:
        """Validate window ordering and positive durations."""
        windows = [
            ("baseline", self.baseline_start, self.baseline_end),
            ("stimulus", self.stimulus_start, self.stimulus_end),
            ("decision", self.decision_start, self.decision_end),
            ("pre_response", self.pre_response_start, self.pre_response_end),
        ]
        for name, start, end in windows:
            if end <= start:
                raise ValueError(f"{name} window must have positive duration")
        if self.response_margin < 0.0:
            raise ValueError("response_margin must be non-negative")


@dataclass(frozen=True)
class TrialInclusionPolicy:
    """Rules for selecting scientifically evaluable Allen behavior trials."""

    include_aborted: bool = False
    include_auto_rewarded: bool = False
    require_go_or_catch: bool = True


def allen_acronym_to_model_region(acronym: str) -> str | None:
    """Map one Allen structure acronym to a coarse model region."""
    for model_region, acronyms in COARSE_REGION_MAP.items():
        if acronym in acronyms:
            return model_region
    return None


def count_spikes_in_window(spike_times: Iterable[float], start: float, end: float) -> int:
    """Count spikes in a half-open interval `[start, end)`."""
    if hasattr(spike_times, "searchsorted"):
        # AllenSDK returns sorted numpy arrays for spike times. Binary search
        # avoids scanning every spike for every trial and makes real-session
        # normalization scale to thousands of recorded units.
        left = spike_times.searchsorted(start, side="left")
        right = spike_times.searchsorted(end, side="left")
        return int(right - left)
    return sum(1 for spike_time in spike_times if start <= float(spike_time) < end)


class AllenSessionNormalizer:
    """Convert an AllenSDK session-like object into a normalized `Session`.

    The required session-like object interface is intentionally narrow:

    - `units`: table-like object with unit IDs and structure acronyms;
    - or `get_units(...)`: AllenSDK `BehaviorEcephysSession` unit table API;
    - `spike_times`: mapping from unit ID to spike-time iterables;
    - `trials`: iterable/table of trial rows.

    Real AllenSDK objects and fake test objects can both satisfy this contract.
    """

    def __init__(
        self,
        windows: TimeWindows | None = None,
        policy: TrialInclusionPolicy | None = None,
    ) -> None:
        self.windows = windows or TimeWindows()
        self.windows.validate()
        self.policy = policy or TrialInclusionPolicy()

    def normalize(
        self,
        allen_session: Any,
        ecephys_session_id: int,
        behavior_session_id: int | None = None,
        animal_id: str = "unknown",
        max_trials: int | None = None,
    ) -> Session:
        """Normalize an Allen session-like object into the core `Session` contract."""
        unit_region = self._unit_to_model_region(allen_session)
        trials = []
        for idx, trial_row in enumerate(self._iter_trial_rows(allen_session)):
            if not self._include_trial(trial_row):
                continue
            if max_trials is not None and len(trials) >= max_trials:
                break
            trial = self._normalize_trial(len(trials), trial_row, allen_session.spike_times, unit_region)
            if trial is not None:
                trials.append(trial)
        if not trials:
            raise ValueError("No valid trials were normalized from Allen session")
        return Session(
            session_id=str(ecephys_session_id),
            animal_id=str(animal_id),
            dataset="allen-visual-behavior-neuropixels",
            trials=trials,
            region_names=sorted(set(unit_region.values())),
        )

    def export(
        self,
        allen_session: Any,
        output_dir: str | Path,
        ecephys_session_id: int,
        behavior_session_id: int | None = None,
        animal_id: str = "unknown",
        max_trials: int | None = None,
    ) -> Path:
        """Normalize and write a `session.json` artifact."""
        session = self.normalize(
            allen_session,
            ecephys_session_id=ecephys_session_id,
            behavior_session_id=behavior_session_id,
            animal_id=animal_id,
            max_trials=max_trials,
        )
        return write_session_artifact(session, output_dir)

    def _unit_to_model_region(self, allen_session: Any) -> dict[Any, str]:
        """Map unit IDs to coarse model regions using Allen acronyms."""
        unit_region: dict[Any, str] = {}
        channel_acronyms = self._channel_acronym_by_id(allen_session)
        for unit_id, row in self._iter_unit_rows(allen_session):
            acronym = self._row_get(row, "structure_acronym")
            if acronym is None:
                acronym = self._row_get(row, "ecephys_structure_acronym")
            if acronym is None:
                # Visual Behavior Neuropixels units carry their anatomical
                # assignment through `peak_channel_id`; channel rows contain
                # the Allen `structure_acronym`.
                peak_channel_id = self._row_get(row, "peak_channel_id")
                acronym = channel_acronyms.get(peak_channel_id)
            model_region = allen_acronym_to_model_region(str(acronym)) if acronym else None
            if model_region:
                unit_region[unit_id] = model_region
        if not unit_region:
            raise ValueError("No units mapped to coarse model regions")
        return unit_region

    def _normalize_trial(
        self,
        trial_index: int,
        trial_row: Any,
        spike_times: dict[Any, Iterable[float]],
        unit_region: dict[Any, str],
    ) -> Trial | None:
        """Normalize one trial row; return `None` when required timing is missing."""
        start_time = self._trial_start_time(trial_row)
        if start_time is None:
            return None
        stimulus = self._trial_stimulus_value(trial_row, trial_index)
        choice = self._trial_choice_value(trial_row, stimulus)
        reward = self._trial_reward_value(trial_row, choice, stimulus)
        latency_ms = self._trial_latency_ms(trial_row)
        response_time = self._trial_response_time(trial_row)
        region_rates_by_window, window_bounds, window_valid = self._region_rates_by_window(
            start_time,
            response_time,
            spike_times,
            unit_region,
        )
        region_rates = region_rates_by_window["stimulus"]
        engagement = self._trial_engagement_proxy(latency_ms, reward)
        metadata = self._trial_metadata(trial_row)
        metadata["region_rates_by_window"] = region_rates_by_window
        metadata["time_windows_s"] = window_bounds
        metadata["time_window_valid"] = window_valid
        metadata["trial_start_time_s"] = start_time
        if response_time is not None:
            metadata["response_time_s"] = response_time
            metadata["response_latency_s"] = max(0.0, response_time - start_time)
        return Trial(
            trial_id=trial_index,
            stimulus=stimulus,
            choice=choice,
            reward=reward,
            latency_ms=latency_ms,
            engagement=engagement,
            region_rates=region_rates,
            metadata=metadata,
        )

    def _region_rates_by_window(
        self,
        start_time: float,
        response_time: float | None,
        spike_times: dict[Any, Iterable[float]],
        unit_region: dict[Any, str],
    ) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]], dict[str, bool]]:
        """Aggregate region-level rates separately for each trial time window."""
        unit_counts: dict[str, int] = {}
        for region in unit_region.values():
            unit_counts[region] = unit_counts.get(region, 0) + 1

        rates_by_window: dict[str, dict[str, float]] = {}
        window_bounds = {
            name: {"start": start, "end": end}
            for name, (start, end) in self.windows.as_dict().items()
        }
        pre_response_end = self.windows.pre_response_end
        if response_time is not None:
            response_offset = response_time - start_time
            pre_response_end = min(pre_response_end, response_offset - self.windows.response_margin)
        window_bounds["pre_response"] = {
            "start": self.windows.pre_response_start,
            "end": pre_response_end,
        }
        window_valid = {
            name: bounds["end"] > bounds["start"]
            for name, bounds in window_bounds.items()
        }
        for window_name, bounds in window_bounds.items():
            offset_start = bounds["start"]
            offset_end = bounds["end"]
            if not window_valid[window_name]:
                rates_by_window[window_name] = {region: 0.0 for region in sorted(unit_counts)}
                continue
            start = start_time + offset_start
            end = start_time + offset_end
            duration = end - start
            spike_counts = {region: 0 for region in unit_counts}
            for unit_id, region in unit_region.items():
                spike_counts[region] += count_spikes_in_window(
                    spike_times.get(unit_id, []),
                    start,
                    end,
                )
            rates_by_window[window_name] = {
                region: spike_counts.get(region, 0) / max(unit_counts[region], 1) / duration
                for region in sorted(unit_counts)
            }
        return rates_by_window, window_bounds, window_valid

    @staticmethod
    def _iter_unit_rows(allen_session: Any):
        # Classic Allen ecephys objects expose `.units`; Visual Behavior
        # Neuropixels `BehaviorEcephysSession` exposes `get_units(...)`.
        # We keep both paths to make the normalizer testable without AllenSDK
        # while supporting the real NWB-backed session object.
        if hasattr(allen_session, "units"):
            units = allen_session.units
        elif hasattr(allen_session, "get_units"):
            units = allen_session.get_units(filter_by_validity=False, filter_out_of_brain_units=False)
        else:
            raise TypeError("Allen session must expose `units` or `get_units(...)`")
        if hasattr(units, "iterrows"):
            yield from units.iterrows()
        elif isinstance(units, dict):
            yield from units.items()
        else:
            raise TypeError("Unsupported units table type")

    @staticmethod
    def _iter_trial_rows(allen_session: Any):
        trials = allen_session.trials
        if hasattr(trials, "iterrows"):
            for _, row in trials.iterrows():
                yield row
        else:
            yield from trials

    @classmethod
    def _channel_acronym_by_id(cls, allen_session: Any) -> dict[Any, str]:
        """Return Allen channel-id to structure-acronym mappings when available."""
        if not hasattr(allen_session, "get_channels"):
            return {}
        channels = allen_session.get_channels(filter_by_validity=False)
        mapping: dict[Any, str] = {}
        if hasattr(channels, "iterrows"):
            for channel_id, row in channels.iterrows():
                acronym = cls._row_get(row, "structure_acronym")
                if acronym:
                    mapping[channel_id] = str(acronym)
        elif isinstance(channels, dict):
            for channel_id, row in channels.items():
                acronym = cls._row_get(row, "structure_acronym")
                if acronym:
                    mapping[channel_id] = str(acronym)
        return mapping

    @staticmethod
    def _row_get(row: Any, key: str, default: Any = None) -> Any:
        if isinstance(row, dict):
            return row.get(key, default)
        if hasattr(row, "get"):
            return row.get(key, default)
        return getattr(row, key, default)

    def _include_trial(self, row: Any) -> bool:
        """Apply the Allen behavioral-trial inclusion policy."""
        if not self.policy.include_aborted and self._row_bool(row, "aborted"):
            return False
        if not self.policy.include_auto_rewarded and self._row_bool(row, "auto_rewarded"):
            return False
        if self.policy.require_go_or_catch and not (
            self._row_bool(row, "go") or self._row_bool(row, "catch")
        ):
            return False
        return True

    def _trial_start_time(self, row: Any) -> float | None:
        for key in (
            "change_time_no_display_delay",
            "change_time",
            "stimulus_start_time",
            "start_time",
        ):
            value = self._row_get(row, key)
            if not self._is_missing(value):
                return float(value)
        return None

    def _trial_stimulus_value(self, row: Any, trial_index: int) -> float:
        """Convert Allen trial stimulus metadata into a signed MVP stimulus.

        Allen visual behavior is not a binary left/right stimulus task. Until
        full task-specific encoding is implemented, this deterministic fallback
        creates a signed value from image/change metadata. It is acceptable for
        pipeline testing, not for final scientific analysis.
        """
        omitted = self._row_get(row, "omitted", False)
        if not self._is_missing(omitted) and bool(omitted):
            return 0.0
        if self._row_bool(row, "go") or self._row_bool(row, "is_change"):
            return 1.0
        if self._row_bool(row, "catch"):
            return -1.0
        image_name = self._row_get(row, "image_name")
        if self._is_missing(image_name):
            image_name = self._row_get(row, "change_image_name")
        if not self._is_missing(image_name):
            # Python's built-in hash is randomized between processes. A stable
            # digest keeps exported artifacts reproducible while this remains a
            # provisional binary encoding for pipeline validation.
            digest = hashlib.sha256(str(image_name).encode("utf-8")).digest()
            return 1.0 if digest[0] % 2 else -1.0
        return 1.0 if trial_index % 2 else -1.0

    def _trial_choice_value(self, row: Any, stimulus: float) -> int:
        response = self._row_get(row, "response")
        if not self._is_missing(response):
            return int(bool(response))
        hit = self._row_get(row, "hit")
        false_alarm = self._row_get(row, "false_alarm")
        if not self._is_missing(hit) or not self._is_missing(false_alarm):
            return int(bool(hit) or bool(false_alarm))
        response_time = self._row_get(row, "response_time")
        if not self._is_missing(response_time):
            return 1
        return int(stimulus > 0)

    def _trial_reward_value(self, row: Any, choice: int, stimulus: float) -> int:
        rewarded = self._row_get(row, "rewarded")
        if not self._is_missing(rewarded):
            return int(bool(rewarded))
        reward_volume = self._row_get(row, "reward_volume")
        if not self._is_missing(reward_volume):
            return int(float(reward_volume) > 0)
        reward_time = self._row_get(row, "reward_time")
        if not self._is_missing(reward_time):
            return int(float(reward_time) > 0)
        return int((choice == 1 and stimulus > 0) or (choice == 0 and stimulus < 0))

    def _trial_latency_ms(self, row: Any) -> float:
        start_time = self._trial_start_time(row)
        response_time = self._trial_response_time(row)
        if start_time is not None and response_time is not None:
            return max(0.0, 1000.0 * (response_time - start_time))
        return 0.0

    def _trial_response_time(self, row: Any) -> float | None:
        """Return absolute response time in seconds when Allen provides it."""
        response_time = self._row_get(row, "response_time")
        if self._is_missing(response_time):
            return None
        return float(response_time)

    def _trial_metadata(self, row: Any) -> dict[str, str | float | int | bool]:
        """Preserve Allen task fields needed for later scientific encodings."""
        keys = [
            "initial_image_name",
            "change_image_name",
            "is_change",
            "go",
            "catch",
            "hit",
            "false_alarm",
            "miss",
            "correct_reject",
            "aborted",
            "auto_rewarded",
            "reward_volume",
            "trial_length",
        ]
        metadata: dict[str, str | float | int | bool] = {}
        for key in keys:
            value = self._row_get(row, key)
            if self._is_missing(value):
                continue
            if isinstance(value, (str, int, float, bool)):
                metadata[key] = value
            else:
                metadata[key] = str(value)
        return metadata

    @staticmethod
    def _trial_engagement_proxy(latency_ms: float, reward: int) -> float:
        """Simple bounded proxy until Allen engagement labels are added."""
        latency_component = 1.0 / (1.0 + max(latency_ms, 0.0) / 500.0)
        reward_component = 0.25 if reward else 0.0
        return max(0.0, min(1.0, latency_component + reward_component))

    @classmethod
    def _row_bool(cls, row: Any, key: str) -> bool:
        value = cls._row_get(row, key, False)
        return False if cls._is_missing(value) else bool(value)

    @staticmethod
    def _is_missing(value: Any) -> bool:
        return value is None or (isinstance(value, float) and value != value)
