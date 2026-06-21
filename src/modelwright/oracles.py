"""Workbook oracle interface records.

Oracle implementations evaluate source workbook outputs for validation. This
module defines the boundary only; backend-specific execution belongs in
separate modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from modelwright.validation import DiagnosticSeverity, JsonValue, ScenarioInput, ScenarioOutput


OracleOutputs = dict[str, JsonValue]


@dataclass(frozen=True)
class OracleDiagnostic:
    """Diagnostic produced while asking a workbook oracle for observed values."""

    diagnostic_code: str
    message: str
    severity: DiagnosticSeverity = "warning"
    location: str | None = None
    raw_value: JsonValue = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OracleDiagnostic":
        return cls(
            diagnostic_code=data["diagnostic_code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
            location=data.get("location"),
            raw_value=data.get("raw_value"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        payload: dict[str, JsonValue] = {
            "diagnostic_code": self.diagnostic_code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.location is not None:
            payload["location"] = self.location
        if self.raw_value is not None:
            payload["raw_value"] = self.raw_value
        return payload


@dataclass(frozen=True)
class OracleRequest:
    """Request for observed workbook output values from one oracle backend."""

    source_workbook: str
    outputs: tuple[ScenarioOutput, ...]
    inputs: tuple[ScenarioInput, ...] = field(default_factory=tuple)
    options: dict[str, JsonValue] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OracleRequest":
        return cls(
            source_workbook=data["source_workbook"],
            outputs=tuple(ScenarioOutput.from_dict(output_data) for output_data in data["outputs"]),
            inputs=tuple(ScenarioInput.from_dict(input_data) for input_data in data.get("inputs", [])),
            options=dict(data.get("options", {})),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "source_workbook": self.source_workbook,
            "outputs": [output.to_dict() for output in self.outputs],
            "inputs": [scenario_input.to_dict() for scenario_input in self.inputs],
            "options": dict(self.options),
        }


@dataclass(frozen=True)
class OracleResult:
    """Observed workbook output values returned by an oracle backend."""

    backend: str
    source_workbook: str
    outputs: OracleOutputs = field(default_factory=dict)
    diagnostics: tuple[OracleDiagnostic, ...] = field(default_factory=tuple)

    @property
    def success(self) -> bool:
        return not any(diagnostic.severity == "error" for diagnostic in self.diagnostics)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OracleResult":
        return cls(
            backend=data["backend"],
            source_workbook=data["source_workbook"],
            outputs=dict(data.get("outputs", {})),
            diagnostics=tuple(
                OracleDiagnostic.from_dict(diagnostic_data)
                for diagnostic_data in data.get("diagnostics", [])
            ),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "backend": self.backend,
            "source_workbook": self.source_workbook,
            "success": self.success,
            "outputs": dict(self.outputs),
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


class WorkbookOracle(Protocol):
    """Protocol implemented by source-workbook oracle backends."""

    backend_name: str

    def evaluate(self, request: OracleRequest) -> OracleResult:
        """Return observed workbook values for the requested outputs."""
        ...


def missing_optional_dependency_diagnostic(*, dependency: str, extra: str, backend: str) -> OracleDiagnostic:
    """Build a standard diagnostic for an unavailable optional oracle backend."""

    return OracleDiagnostic(
        diagnostic_code="missing_optional_dependency",
        message=f"Install modelwright[{extra}] to use the {backend} oracle backend.",
        severity="error",
        raw_value=dependency,
    )
