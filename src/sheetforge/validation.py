"""Validation report records.

These objects describe validation results; they do not run workbook or generated
model comparisons themselves.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
OutputKind = Literal["number", "text", "boolean", "blank", "error"]
ReportStatus = Literal["pass", "fail"]
DiagnosticSeverity = Literal["info", "warning", "error"]
TextComparisonMode = Literal["exact"]
BooleanComparisonMode = Literal["exact"]


@dataclass(frozen=True)
class OracleConfig:
    """Oracle backend configuration from a validation scenario."""

    backend: str
    options: dict[str, JsonValue] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OracleConfig":
        backend = data["backend"]
        options = {key: value for key, value in data.items() if key != "backend"}
        return cls(backend=backend, options=options)

    def to_dict(self) -> dict[str, JsonValue]:
        return {"backend": self.backend, **self.options}


@dataclass(frozen=True)
class ScenarioInput:
    """Input override declared by a validation scenario."""

    cell_ref: str
    value: JsonValue
    kind: OutputKind
    source: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioInput":
        return cls(
            cell_ref=data["cell_ref"],
            value=data.get("value"),
            kind=data["kind"],
            source=data.get("source"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        payload: dict[str, JsonValue] = {
            "cell_ref": self.cell_ref,
            "value": self.value,
            "kind": self.kind,
        }
        if self.source is not None:
            payload["source"] = self.source
        return payload


@dataclass(frozen=True)
class ScenarioOutput:
    """Output expectation declared by a validation scenario."""

    cell_ref: str
    kind: OutputKind
    tolerance: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioOutput":
        return cls(
            cell_ref=data["cell_ref"],
            kind=data["kind"],
            tolerance=data.get("tolerance"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        payload: dict[str, JsonValue] = {
            "cell_ref": self.cell_ref,
            "kind": self.kind,
        }
        if self.tolerance is not None:
            payload["tolerance"] = self.tolerance
        return payload


@dataclass(frozen=True)
class ComparisonRules:
    """Default comparison rules declared by a validation scenario."""

    default_numeric_tolerance: float = 1e-9
    text: TextComparisonMode = "exact"
    boolean: BooleanComparisonMode = "exact"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComparisonRules":
        return cls(
            default_numeric_tolerance=data.get("default_numeric_tolerance", 1e-9),
            text=data.get("text", "exact"),
            boolean=data.get("boolean", "exact"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "default_numeric_tolerance": self.default_numeric_tolerance,
            "text": self.text,
            "boolean": self.boolean,
        }


@dataclass(frozen=True)
class ValidationScenario:
    """Validation scenario loaded from a JSON boundary."""

    scenario_id: str
    description: str
    source_workbook: str
    generated_model: str
    oracle: OracleConfig
    inputs: tuple[ScenarioInput, ...]
    outputs: tuple[ScenarioOutput, ...]
    comparison: ComparisonRules

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationScenario":
        return cls(
            scenario_id=data["scenario_id"],
            description=data.get("description", ""),
            source_workbook=data["source_workbook"],
            generated_model=data["generated_model"],
            oracle=OracleConfig.from_dict(data["oracle"]),
            inputs=tuple(ScenarioInput.from_dict(input_data) for input_data in data.get("inputs", [])),
            outputs=tuple(ScenarioOutput.from_dict(output_data) for output_data in data["outputs"]),
            comparison=ComparisonRules.from_dict(data.get("comparison", {})),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "scenario_id": self.scenario_id,
            "description": self.description,
            "source_workbook": self.source_workbook,
            "generated_model": self.generated_model,
            "oracle": self.oracle.to_dict(),
            "inputs": [scenario_input.to_dict() for scenario_input in self.inputs],
            "outputs": [output.to_dict() for output in self.outputs],
            "comparison": self.comparison.to_dict(),
        }


def load_validation_scenario(path: str | Path) -> ValidationScenario:
    """Load a validation scenario JSON file from disk."""

    scenario_path = Path(path)
    data = json.loads(scenario_path.read_text(encoding="utf-8"))
    return ValidationScenario.from_dict(data)


@dataclass(frozen=True)
class Diagnostic:
    """Run-level diagnostic not tied to one output comparison."""

    diagnostic_code: str
    message: str
    severity: DiagnosticSeverity = "warning"
    location: str | None = None

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "diagnostic_code": self.diagnostic_code,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
        }


@dataclass(frozen=True)
class ComparisonResult:
    """Comparison result for one declared workbook output."""

    scenario_id: str
    cell_ref: str
    kind: OutputKind
    generated: JsonValue
    oracle: JsonValue
    matches: bool
    tolerance: float | None
    difference: float | None
    diagnostic_code: str | None
    message: str
    oracle_backend: str

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "scenario_id": self.scenario_id,
            "cell_ref": self.cell_ref,
            "kind": self.kind,
            "generated": self.generated,
            "oracle": self.oracle,
            "matches": self.matches,
            "tolerance": self.tolerance,
            "difference": self.difference,
            "diagnostic_code": self.diagnostic_code,
            "message": self.message,
            "oracle_backend": self.oracle_backend,
        }


@dataclass(frozen=True)
class ValidationReport:
    """Validation report for one scenario."""

    scenario_id: str
    oracle_backend: str
    comparisons: tuple[ComparisonResult, ...] = field(default_factory=tuple)
    diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)

    @property
    def mismatches(self) -> tuple[ComparisonResult, ...]:
        return tuple(comparison for comparison in self.comparisons if not comparison.matches)

    @property
    def status(self) -> ReportStatus:
        if self.mismatches or any(diagnostic.severity == "error" for diagnostic in self.diagnostics):
            return "fail"
        return "pass"

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "scenario_id": self.scenario_id,
            "oracle_backend": self.oracle_backend,
            "status": self.status,
            "comparisons": [comparison.to_dict() for comparison in self.comparisons],
            "mismatches": [comparison.to_dict() for comparison in self.mismatches],
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }
