"""Input-uncertainty distributions and expected-value modelling for generated models.

This module provides a deliberately small, dependency-free reference implementation:

- a JSON-friendly distribution specification over generated-model input cell refs;
- inverse-CDF sampling (random or Latin-hypercube) for independent input variates;
- evaluation of draws through a generated model's ``calculate(inputs=...)`` entrypoint;
- expected-value and output-distribution summaries (mean, standard deviation, standard error,
  coefficient of variation, percentiles, and histogram counts).

It does not model correlations between inputs, run global (Sobol/variance) sensitivity analysis, or
provide production-scale parallel execution. Those remain explicit follow-up boundaries.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

JsonValue = str | int | float | bool | None
DistributionFamily = str
SamplingDesign = str

DISTRIBUTION_FAMILIES = (
    "normal",
    "truncated_normal",
    "uniform",
    "lognormal",
    "triangular",
    "constant",
)
SAMPLING_DESIGNS = ("random", "latin_hypercube")
DEFAULT_PERCENTILES = (5.0, 25.0, 50.0, 75.0, 95.0)
_UNIT_EPSILON = 1e-12


@dataclass(frozen=True)
class InputDistribution:
    """One uncertain input variate identified by generated-model cell ref."""

    cell_ref: str
    family: DistributionFamily
    parameters: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.cell_ref, str) or "!" not in self.cell_ref:
            raise ValueError(f"input distribution cell_ref must look like 'Sheet!A1': {self.cell_ref!r}")
        if self.family not in DISTRIBUTION_FAMILIES:
            raise ValueError(
                f"unsupported distribution family {self.family!r}; expected one of {DISTRIBUTION_FAMILIES}"
            )
        object.__setattr__(self, "parameters", {key: float(value) for key, value in self.parameters.items()})
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        if self.family == "constant":
            self._require("value")
            return
        if self.family == "normal":
            self._require("mean")
            self._require_positive("std")
            return
        if self.family == "truncated_normal":
            mean = self._require("mean")
            std = self._require_positive("std")
            low = self._require("low")
            high = self._require("high")
            if not low < high:
                raise ValueError(f"truncated_normal requires low < high: {self.cell_ref!r}")
            if std <= 0:
                raise ValueError(f"truncated_normal requires std > 0: {self.cell_ref!r}")
            if not math.isfinite(mean) or not math.isfinite(low) or not math.isfinite(high):
                raise ValueError(f"truncated_normal parameters must be finite: {self.cell_ref!r}")
            return
        if self.family == "uniform":
            low = self._require("low")
            high = self._require("high")
            if not low < high:
                raise ValueError(f"uniform requires low < high: {self.cell_ref!r}")
            return
        if self.family == "lognormal":
            self._require("mean")
            self._require_positive("sigma")
            return
        if self.family == "triangular":
            low = self._require("low")
            mode = self._require("mode")
            high = self._require("high")
            if not low <= mode <= high or not low < high:
                raise ValueError(f"triangular requires low <= mode <= high: {self.cell_ref!r}")
            return

    def _require(self, name: str) -> float:
        if name not in self.parameters:
            raise ValueError(f"{self.family} distribution is missing parameter {name!r}: {self.cell_ref!r}")
        value = self.parameters[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ValueError(f"{self.family} parameter {name!r} must be a finite number: {self.cell_ref!r}")
        return float(value)

    def _require_positive(self, name: str) -> float:
        value = self._require(name)
        if value <= 0:
            raise ValueError(f"{self.family} parameter {name!r} must be > 0: {self.cell_ref!r}")
        return value

    def inverse_cdf(self, unit: float) -> float:
        """Map one uniform draw in (0, 1) to a value for this distribution."""

        u = min(max(float(unit), _UNIT_EPSILON), 1.0 - _UNIT_EPSILON)
        if self.family == "constant":
            return self._require("value")
        if self.family == "normal":
            return statistics.NormalDist(self._require("mean"), self._require("std")).inv_cdf(u)
        if self.family == "truncated_normal":
            mean = self._require("mean")
            std = self._require("std")
            low = self._require("low")
            high = self._require("high")
            normal = statistics.NormalDist(mean, std)
            lower_probability = normal.cdf(low)
            upper_probability = normal.cdf(high)
            if not upper_probability > lower_probability:
                raise ValueError(f"truncated_normal bounds contain no probability mass: {self.cell_ref!r}")
            return normal.inv_cdf(lower_probability + u * (upper_probability - lower_probability))
        if self.family == "uniform":
            low = self._require("low")
            high = self._require("high")
            return low + u * (high - low)
        if self.family == "lognormal":
            mean = self._require("mean")
            sigma = self._require("sigma")
            return math.exp(mean + sigma * statistics.NormalDist().inv_cdf(u))
        if self.family == "triangular":
            low = self._require("low")
            mode = self._require("mode")
            high = self._require("high")
            split = (mode - low) / (high - low)
            if u <= split:
                return low + math.sqrt(u * (high - low) * (mode - low))
            return high - math.sqrt((1.0 - u) * (high - low) * (high - mode))
        raise ValueError(f"unsupported distribution family: {self.family!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_ref": self.cell_ref,
            "family": self.family,
            "parameters": dict(sorted(self.parameters.items())),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "InputDistribution":
        if "parameters" in data:
            parameters = data["parameters"]
        else:
            parameters = {
                key: value
                for key, value in data.items()
                if key not in {"cell_ref", "family"}
            }
        if not isinstance(parameters, Mapping):
            raise ValueError("distribution parameters must be a JSON object")
        return cls(cell_ref=str(data["cell_ref"]), family=str(data["family"]), parameters=dict(parameters))


@dataclass(frozen=True)
class UncertaintySpec:
    """Versioned input-uncertainty specification for one generated model."""

    distributions: tuple[InputDistribution, ...]
    draws: int = 1000
    seed: int = 0
    design: SamplingDesign = "random"
    output_refs: tuple[str, ...] | None = None
    percentiles: tuple[float, ...] = DEFAULT_PERCENTILES
    histogram_bins: int = 20

    def __post_init__(self) -> None:
        if not self.distributions:
            raise ValueError("uncertainty spec must declare at least one input distribution")
        object.__setattr__(self, "distributions", tuple(self.distributions))
        object.__setattr__(self, "percentiles", tuple(float(value) for value in self.percentiles))
        object.__setattr__(
            self,
            "output_refs",
            tuple(self.output_refs) if self.output_refs is not None else None,
        )
        if self.draws < 1:
            raise ValueError("draws must be >= 1")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            raise ValueError("seed must be an integer")
        if self.design not in SAMPLING_DESIGNS:
            raise ValueError(f"design must be one of {SAMPLING_DESIGNS}: {self.design!r}")
        cell_refs = [distribution.cell_ref for distribution in self.distributions]
        if len(set(cell_refs)) != len(cell_refs):
            duplicates = sorted({ref for ref in cell_refs if cell_refs.count(ref) > 1})
            raise ValueError(f"duplicate input distribution cell refs: {duplicates}")
        if not self.percentiles:
            raise ValueError("percentiles must not be empty")
        if any(not 0.0 <= value <= 100.0 for value in self.percentiles):
            raise ValueError("percentiles must be between 0 and 100")
        if list(self.percentiles) != sorted(self.percentiles):
            raise ValueError("percentiles must be sorted ascending")
        if self.histogram_bins < 1:
            raise ValueError("histogram_bins must be >= 1")
        if self.output_refs is not None and not self.output_refs:
            raise ValueError("output_refs must be a non-empty tuple when provided")

    def to_dict(self) -> dict[str, Any]:
        return {
            "draws": self.draws,
            "seed": self.seed,
            "design": self.design,
            "distributions": [distribution.to_dict() for distribution in self.distributions],
            "output_refs": list(self.output_refs) if self.output_refs is not None else None,
            "percentiles": list(self.percentiles),
            "histogram_bins": self.histogram_bins,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "UncertaintySpec":
        distributions = tuple(
            InputDistribution.from_dict(item) for item in data.get("distributions", ())
        )
        output_refs = data.get("output_refs")
        return cls(
            distributions=distributions,
            draws=int(data.get("draws", 1000)),
            seed=int(data.get("seed", 0)),
            design=str(data.get("design", "random")),
            output_refs=tuple(output_refs) if output_refs is not None else None,
            percentiles=tuple(float(value) for value in data.get("percentiles", DEFAULT_PERCENTILES)),
            histogram_bins=int(data.get("histogram_bins", 20)),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.to_json(), encoding="utf-8")
        return destination

    @classmethod
    def load(cls, path: str | Path) -> "UncertaintySpec":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    @property
    def sha256(self) -> str:
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def iter_input_draws(spec: UncertaintySpec) -> Iterator[tuple[int, dict[str, float]]]:
    """Yield ``(draw_index, inputs)`` pairs for the specification."""

    rng = random.Random(spec.seed)
    distributions = spec.distributions
    if spec.design == "latin_hypercube":
        orders = []
        for _ in distributions:
            order = list(range(spec.draws))
            rng.shuffle(order)
            orders.append(order)
        for index in range(spec.draws):
            inputs: dict[str, float] = {}
            for position, distribution in enumerate(distributions):
                unit = (orders[position][index] + rng.random()) / spec.draws
                inputs[distribution.cell_ref] = distribution.inverse_cdf(unit)
            yield index, inputs
        return
    for index in range(spec.draws):
        inputs = {distribution.cell_ref: distribution.inverse_cdf(rng.random()) for distribution in distributions}
        yield index, inputs


@dataclass(frozen=True)
class DrawResult:
    """One evaluated uncertainty draw."""

    draw: int
    values: Mapping[str, JsonValue]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "draw": self.draw,
            "values": dict(self.values),
            "error": self.error,
        }


def evaluate_draws(
    calculate: Callable[..., Mapping[str, JsonValue]],
    spec: UncertaintySpec,
    *,
    calculate_kwargs: Mapping[str, Any] | None = None,
    stop_on_error: bool = False,
) -> tuple[DrawResult, ...]:
    """Run every draw through ``calculate`` and collect selected output values."""

    kwargs = dict(calculate_kwargs or {})
    resolved_refs = spec.output_refs
    results: list[DrawResult] = []
    for index, inputs in iter_input_draws(spec):
        try:
            values = calculate(inputs=inputs, **kwargs)
            if not isinstance(values, Mapping):
                raise TypeError(f"calculate() returned {type(values).__name__}, expected a mapping")
            if resolved_refs is None:
                resolved_refs = tuple(values)
                selected = dict(values)
            else:
                selected = {ref: values.get(ref) for ref in resolved_refs}
            results.append(DrawResult(draw=index, values=selected))
        except Exception as error:  # noqa: BLE001 - recorded as draw-level provenance
            if stop_on_error:
                raise
            results.append(DrawResult(draw=index, values={}, error=f"{type(error).__name__}: {error}"))
    return tuple(results)


def _percentile(sorted_values: Sequence[float], percentile: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    rank = (len(sorted_values) - 1) * percentile / 100.0
    lower_index = math.floor(rank)
    upper_index = math.ceil(rank)
    if lower_index == upper_index:
        return float(sorted_values[lower_index])
    lower = sorted_values[lower_index]
    upper = sorted_values[upper_index]
    return float(lower + (upper - lower) * (rank - lower_index))


def _histogram(values: Sequence[float], bins: int) -> dict[str, list[float] | list[int]]:
    if not values:
        return {"edges": [], "counts": []}
    low = min(values)
    high = max(values)
    if low == high:
        return {"edges": [low, low], "counts": [len(values)]}
    width = (high - low) / bins
    counts = [0 for _ in range(bins)]
    for value in values:
        index = int((value - low) / width)
        if index >= bins:
            index = bins - 1
        counts[index] += 1
    edges = [low + index * width for index in range(bins + 1)]
    return {"edges": edges, "counts": counts}


def _numeric_values(values: Sequence[JsonValue]) -> list[float]:
    numeric: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        number = float(value)
        if math.isfinite(number):
            numeric.append(number)
    return numeric


@dataclass(frozen=True)
class OutputDistributionSummary:
    """Expected-value and distribution summary for one generated-model output."""

    cell_ref: str
    count: int
    numeric_count: int
    non_numeric_count: int
    error_count: int
    mean: float | None
    median: float | None
    standard_deviation: float | None
    standard_error: float | None
    coefficient_of_variation: float | None
    minimum: float | None
    maximum: float | None
    percentiles: Mapping[str, float]
    histogram: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_ref": self.cell_ref,
            "count": self.count,
            "numeric_count": self.numeric_count,
            "non_numeric_count": self.non_numeric_count,
            "error_count": self.error_count,
            "mean": self.mean,
            "median": self.median,
            "standard_deviation": self.standard_deviation,
            "standard_error": self.standard_error,
            "coefficient_of_variation": self.coefficient_of_variation,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "percentiles": dict(self.percentiles),
            "histogram": dict(self.histogram),
        }


def summarize_draws(
    results: Sequence[DrawResult],
    spec: UncertaintySpec,
) -> tuple[OutputDistributionSummary, ...]:
    """Summarize expected values and distributions for each selected output."""

    refs: tuple[str, ...]
    if spec.output_refs is not None:
        refs = spec.output_refs
    else:
        discovered: list[str] = []
        for result in results:
            for ref in result.values:
                if ref not in discovered:
                    discovered.append(ref)
        refs = tuple(discovered)

    summaries: list[OutputDistributionSummary] = []
    for ref in refs:
        values = [result.values.get(ref) for result in results if result.error is None]
        numeric = _numeric_values(values)
        non_numeric = len(values) - len(numeric)
        errors = sum(1 for result in results if result.error is not None)
        mean = statistics.fmean(numeric) if numeric else None
        median = statistics.median(numeric) if numeric else None
        standard_deviation = statistics.stdev(numeric) if len(numeric) >= 2 else None
        standard_error = (
            standard_deviation / math.sqrt(len(numeric)) if standard_deviation is not None else None
        )
        coefficient_of_variation = (
            standard_deviation / abs(mean) if standard_deviation is not None and mean not in (None, 0.0) else None
        )
        ordered = sorted(numeric)
        percentile_values = {
            f"p{value:g}": _percentile(ordered, value) for value in spec.percentiles
        }
        summaries.append(
            OutputDistributionSummary(
                cell_ref=ref,
                count=len(results),
                numeric_count=len(numeric),
                non_numeric_count=non_numeric,
                error_count=errors,
                mean=mean,
                median=median,
                standard_deviation=standard_deviation,
                standard_error=standard_error,
                coefficient_of_variation=coefficient_of_variation,
                minimum=min(numeric) if numeric else None,
                maximum=max(numeric) if numeric else None,
                percentiles=percentile_values,
                histogram=_histogram(numeric, spec.histogram_bins),
            )
        )
    return tuple(summaries)


def run_uncertainty(
    calculate: Callable[..., Mapping[str, JsonValue]],
    spec: UncertaintySpec,
    *,
    calculate_kwargs: Mapping[str, Any] | None = None,
    include_samples: bool = False,
    stop_on_error: bool = False,
) -> dict[str, Any]:
    """Run a complete input-uncertainty analysis and return JSON-friendly results."""

    results = evaluate_draws(
        calculate,
        spec,
        calculate_kwargs=calculate_kwargs,
        stop_on_error=stop_on_error,
    )
    summaries = summarize_draws(results, spec)
    payload: dict[str, Any] = {
        "spec": spec.to_dict(),
        "provenance": {
            "spec_sha256": spec.sha256,
            "seed": spec.seed,
            "draws": spec.draws,
            "design": spec.design,
        },
        "outputs": [summary.to_dict() for summary in summaries],
    }
    if include_samples:
        payload["samples"] = [result.to_dict() for result in results]
    return payload


def unknown_input_refs(
    spec: UncertaintySpec,
    input_refs: Sequence[str],
) -> tuple[str, ...]:
    """Return distribution cell refs that are not declared generated-model inputs."""

    declared = set(input_refs)
    return tuple(
        distribution.cell_ref
        for distribution in spec.distributions
        if distribution.cell_ref not in declared
    )
