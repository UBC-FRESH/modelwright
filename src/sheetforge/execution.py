"""Execution helpers for generated Sheetforge Python models."""

from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from sheetforge.generation import GeneratedModuleContract


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
DiagnosticSeverity = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class ExecutionDiagnostic:
    """Execution concern tied to a generated model run."""

    code: str
    message: str
    severity: DiagnosticSeverity = "warning"
    location: str | None = None
    raw_value: JsonValue = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionDiagnostic":
        return cls(
            code=data["code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
            location=data.get("location"),
            raw_value=data.get("raw_value"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
            "raw_value": self.raw_value,
        }


@dataclass(frozen=True)
class GeneratedExecutionResult:
    """Observed outputs from one generated Python model execution."""

    contract: GeneratedModuleContract
    module_path: str
    entrypoint: str
    output_values: dict[str, JsonValue] = field(default_factory=dict)
    diagnostics: tuple[ExecutionDiagnostic, ...] = field(default_factory=tuple)

    @property
    def executed(self) -> bool:
        return not any(diagnostic.severity == "error" for diagnostic in self.diagnostics)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GeneratedExecutionResult":
        return cls(
            contract=GeneratedModuleContract.from_dict(data["contract"]),
            module_path=data["module_path"],
            entrypoint=data["entrypoint"],
            output_values=dict(data.get("output_values", {})),
            diagnostics=tuple(ExecutionDiagnostic.from_dict(item) for item in data.get("diagnostics", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "contract": self.contract.to_dict(),
            "module_path": self.module_path,
            "entrypoint": self.entrypoint,
            "executed": self.executed,
            "output_values": self.output_values,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def execute_generated_model(
    *,
    contract: GeneratedModuleContract,
    module_path: str | Path,
    inputs: Mapping[str, JsonValue] | None = None,
) -> GeneratedExecutionResult:
    """Execute a generated Python module and return observed declared outputs."""

    path = Path(module_path)
    diagnostics: list[ExecutionDiagnostic] = []
    if not path.exists():
        return _result(
            contract=contract,
            module_path=path,
            diagnostics=(
                ExecutionDiagnostic(
                    code="generated_model_not_found",
                    message="generated Python model file does not exist",
                    severity="error",
                    location=str(path),
                ),
            ),
        )

    module = _load_generated_module(path)
    if isinstance(module, ExecutionDiagnostic):
        return _result(contract=contract, module_path=path, diagnostics=(module,))

    entrypoint = getattr(module, contract.entrypoint, None)
    if not callable(entrypoint):
        return _result(
            contract=contract,
            module_path=path,
            diagnostics=(
                ExecutionDiagnostic(
                    code="generated_model_entrypoint_missing",
                    message="generated Python model entrypoint is missing or not callable",
                    severity="error",
                    location=contract.entrypoint,
                ),
            ),
        )

    try:
        raw_outputs = entrypoint(dict(inputs or {}))
    except Exception as error:  # noqa: BLE001
        return _result(
            contract=contract,
            module_path=path,
            diagnostics=(
                ExecutionDiagnostic(
                    code="generated_model_execution_failed",
                    message="generated Python model raised during execution",
                    severity="error",
                    location=contract.entrypoint,
                    raw_value=repr(error),
                ),
            ),
        )

    if not isinstance(raw_outputs, Mapping):
        return _result(
            contract=contract,
            module_path=path,
            diagnostics=(
                ExecutionDiagnostic(
                    code="generated_model_outputs_not_mapping",
                    message="generated Python model entrypoint must return a mapping of cell refs to values",
                    severity="error",
                    location=contract.entrypoint,
                    raw_value=repr(raw_outputs),
                ),
            ),
        )

    output_values: dict[str, JsonValue] = {}
    output_refs = contract.output_refs or tuple(str(key) for key in raw_outputs)
    for output_ref in output_refs:
        if output_ref not in raw_outputs:
            diagnostics.append(
                ExecutionDiagnostic(
                    code="missing_generated_output",
                    message="generated Python model did not return a declared output",
                    location=output_ref,
                )
            )
            continue
        value = raw_outputs[output_ref]
        if not _is_json_value(value):
            diagnostics.append(
                ExecutionDiagnostic(
                    code="non_json_generated_output",
                    message="generated output value is not JSON-serializable",
                    severity="error",
                    location=output_ref,
                    raw_value=repr(value),
                )
            )
            continue
        output_values[output_ref] = value

    return _result(contract=contract, module_path=path, output_values=output_values, diagnostics=tuple(diagnostics))


def _load_generated_module(path: Path) -> ModuleType | ExecutionDiagnostic:
    module_name = f"_sheetforge_generated_{path.stem}_{uuid.uuid4().hex}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return ExecutionDiagnostic(
                code="generated_model_import_failed",
                message="could not build an import specification for generated Python model",
                severity="error",
                location=str(path),
            )
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as error:  # noqa: BLE001
        return ExecutionDiagnostic(
            code="generated_model_import_failed",
            message="generated Python model could not be imported",
            severity="error",
            location=str(path),
            raw_value=repr(error),
        )
    finally:
        sys.modules.pop(module_name, None)
    return module


def _result(
    *,
    contract: GeneratedModuleContract,
    module_path: Path,
    output_values: dict[str, JsonValue] | None = None,
    diagnostics: tuple[ExecutionDiagnostic, ...] = (),
) -> GeneratedExecutionResult:
    return GeneratedExecutionResult(
        contract=contract,
        module_path=str(module_path),
        entrypoint=contract.entrypoint,
        output_values=output_values or {},
        diagnostics=diagnostics,
    )


def _is_json_value(value: Any) -> bool:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return False
    return True
