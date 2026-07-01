"""FreshForge provider integration for Modelwright workflow stages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

MODELWRIGHT_PROVIDER_ID = "modelwright"
MODELWRIGHT_PROVIDER_VERSION = "0.1.0a7"


@dataclass(frozen=True)
class _NodeContract:
    id: str
    name: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()


_NODE_CONTRACTS: tuple[_NodeContract, ...] = (
    _NodeContract(
        id="workbook_extract",
        name="Extract workbook",
        description="Declare extraction of workbook facts into a WorkbookRecord.",
        outputs=("workbook_record",),
        parameters=("workbook",),
        artifacts=("workbook_record",),
    ),
    _NodeContract(
        id="workbook_graph",
        name="Build workbook dependency graph",
        description="Declare dependency graph construction from an extracted workbook record.",
        inputs=("workbook_record",),
        outputs=("dependency_graph",),
        artifacts=("dependency_graph",),
    ),
    _NodeContract(
        id="model_infer_contract",
        name="Infer generated-model contract",
        description="Declare selected-output generated-model contract inference.",
        outputs=("generated_contract", "formula_expressions", "input_constants"),
        parameters=("workbook", "module_name"),
        artifacts=("output_refs", "contract", "expressions", "constants", "inference_result"),
    ),
    _NodeContract(
        id="model_generate",
        name="Generate Python model",
        description="Declare standalone Python model generation from explicit JSON artifacts.",
        inputs=("generated_contract", "formula_expressions", "input_constants"),
        outputs=("generated_model",),
        artifacts=("contract", "expressions", "constants", "generated_model", "generation_result"),
    ),
    _NodeContract(
        id="model_execute",
        name="Execute generated model",
        description="Declare generated-model execution for selected outputs.",
        inputs=("generated_contract", "generated_model"),
        outputs=("generated_values",),
        artifacts=("contract", "generated_model", "generated_values"),
    ),
    _NodeContract(
        id="validation_evaluate",
        name="Evaluate generated model",
        description="Declare generated-model evaluation against cached or oracle-backed values.",
        inputs=("generated_contract", "generated_model"),
        outputs=("validation_report",),
        parameters=("scenario",),
        artifacts=("contract", "generated_model", "scenario", "evaluation_report"),
    ),
    _NodeContract(
        id="conversion_plan",
        name="Build conversion plan",
        description="Declare a Modelwright conversion-plan summary for the workflow boundary.",
        inputs=("workbook_record", "dependency_graph"),
        outputs=("conversion_plan",),
        parameters=("benchmark_role",),
        artifacts=("conversion_plan",),
    ),
)


class ModelwrightFreshForgeProvider:
    """FreshForge provider for Modelwright workflow stages."""

    def metadata(self) -> Any:
        """Return FreshForge provider metadata."""
        node_type_metadata, provider_metadata = _freshforge_metadata_types()
        return provider_metadata(
            id=MODELWRIGHT_PROVIDER_ID,
            version=MODELWRIGHT_PROVIDER_VERSION,
            name="Modelwright workflow provider",
            description=(
                "Provider for Modelwright workbook extraction, generated-model "
                "materialization, and validation workflow planning/execution."
            ),
            node_types=tuple(
                node_type_metadata(
                    id=contract.id,
                    name=contract.name,
                    description=contract.description,
                    inputs=contract.inputs,
                    outputs=contract.outputs,
                    parameters=contract.parameters,
                    artifacts=contract.artifacts,
                )
                for contract in _NODE_CONTRACTS
            ),
        )

    def validate_node(
        self,
        node: Any,
        node_type: Any,
        *,
        location: str,
    ) -> tuple[Any, ...]:
        """Validate broad Modelwright node shape without executing Modelwright."""
        diagnostic, severity = _freshforge_diagnostic_types()
        diagnostics: list[Any] = []
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.inputs),
                actual=node.inputs,
                field_name="inputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.outputs),
                actual=node.outputs,
                field_name="outputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.parameters),
                actual=node.parameters,
                field_name="parameters",
                location=location,
            )
        )
        artifacts = node.artifacts if isinstance(node.artifacts, dict) else {}
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.artifacts),
                actual=artifacts,
                field_name="artifacts",
                location=location,
            )
        )
        diagnostics.extend(
            _empty_parameter_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                parameters=node.parameters,
                required=tuple(node_type.parameters),
                location=location,
            )
        )
        return tuple(diagnostics)

    def run_node(
        self,
        node: Any,
        node_type: Any,
        *,
        context: Any,
    ) -> Any:
        """Execute one supported generated-model workflow node."""
        diagnostic, severity, provider_result, run_status = _freshforge_run_types()
        try:
            artifacts = _resolved_artifacts(node, context)
            if node_type.id == "model_infer_contract":
                payload = _run_model_infer_contract(node, artifacts, context)
                _write_json(artifacts["inference_result"], payload)
                return provider_result(
                    status=run_status.SUCCESS,
                    outputs={
                        "generated_contract": str(artifacts["contract"]),
                        "formula_expressions": str(artifacts["expressions"]),
                        "input_constants": str(artifacts["constants"]),
                    },
                    artifacts=_string_artifacts(artifacts),
                    data={"inferred": payload.get("inferred")},
                )
            if node_type.id == "model_generate":
                payload = _run_model_generate(artifacts)
                _write_json(artifacts["generation_result"], payload)
                return provider_result(
                    status=run_status.SUCCESS if payload.get("generated") else run_status.FAILED,
                    outputs={"generated_model": str(artifacts["generated_model"])},
                    artifacts=_string_artifacts(artifacts),
                    data={"generated": payload.get("generated")},
                )
            if node_type.id == "model_execute":
                payload = _run_model_execute(artifacts)
                _write_json(artifacts["generated_values"], payload)
                return provider_result(
                    status=run_status.SUCCESS if payload.get("executed") else run_status.FAILED,
                    outputs={"generated_values": str(artifacts["generated_values"])},
                    artifacts=_string_artifacts(artifacts),
                    data={"executed": payload.get("executed")},
                )
            if node_type.id == "validation_evaluate":
                payload = _run_validation_evaluate(node, artifacts, context)
                _write_json(artifacts["evaluation_report"], payload)
                return provider_result(
                    status=run_status.SUCCESS,
                    outputs={"validation_report": str(artifacts["evaluation_report"])},
                    artifacts=_string_artifacts(artifacts),
                    data={
                        "cached_validation_status": (
                            payload.get("cached_validation_report", {}) or {}
                        ).get("status"),
                    },
                )
        except Exception as exc:  # noqa: BLE001
            return provider_result(
                status=run_status.FAILED,
                diagnostics=(
                    diagnostic(
                        severity=severity.ERROR,
                        code="modelwright.execution.failed",
                        message=f"Modelwright FreshForge node failed: {exc}",
                        location=f"nodes.{node.id}",
                    ),
                ),
            )
        return provider_result(
            status=run_status.FAILED,
            diagnostics=(
                diagnostic(
                    severity=severity.ERROR,
                    code="modelwright.execution.unsupported",
                    message=f"Modelwright node type '{node_type.id}' is not executable.",
                    location=f"nodes.{node.id}",
                ),
            ),
        )


def provider_factory() -> ModelwrightFreshForgeProvider:
    """Return the Modelwright FreshForge provider for entry-point discovery."""
    return ModelwrightFreshForgeProvider()


def _freshforge_metadata_types() -> tuple[Any, Any]:
    try:
        from freshforge.providers import (  # type: ignore[import-untyped]
            NodeTypeMetadata,
            ProviderMetadata,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The Modelwright FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return NodeTypeMetadata, ProviderMetadata


def _freshforge_diagnostic_types() -> tuple[Any, Any]:
    try:
        from freshforge.records import (  # type: ignore[import-untyped]
            Diagnostic,
            DiagnosticSeverity,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The Modelwright FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return Diagnostic, DiagnosticSeverity


def _freshforge_run_types() -> tuple[Any, Any, Any, Any]:
    try:
        from freshforge.records import (  # type: ignore[import-untyped]
            Diagnostic,
            DiagnosticSeverity,
            ProviderRunResult,
            RunStatus,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The Modelwright FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return Diagnostic, DiagnosticSeverity, ProviderRunResult, RunStatus


def _run_model_infer_contract(
    node: Any,
    artifacts: dict[str, Path],
    context: Any,
) -> dict[str, Any]:
    from modelwright.cli import _infer_contract_payload

    return _infer_contract_payload(
        workbook=context.resolve_path(node.parameters["workbook"]),
        module_name=node.parameters["module_name"],
        output_refs=(),
        output_refs_file=artifacts["output_refs"],
        contract=artifacts["contract"],
        expressions=artifacts["expressions"],
        constants=artifacts["constants"],
        verbose=False,
    )


def _run_model_generate(artifacts: dict[str, Path]) -> dict[str, Any]:
    from modelwright.cli import _generate_payload

    return _generate_payload(
        contract=artifacts["contract"],
        expressions=artifacts["expressions"],
        constants=artifacts["constants"],
        output=artifacts["generated_model"],
    )


def _run_model_execute(artifacts: dict[str, Path]) -> dict[str, Any]:
    from modelwright.cli import _execute_payload

    return _execute_payload(
        contract=artifacts["contract"],
        model=artifacts["generated_model"],
        inputs=artifacts.get("inputs"),
    )


def _run_validation_evaluate(
    node: Any,
    artifacts: dict[str, Path],
    context: Any,
) -> dict[str, Any]:
    from modelwright.cli import _evaluate_payload

    workbook = node.parameters.get("workbook")
    return _evaluate_payload(
        contract=artifacts["contract"],
        model=artifacts["generated_model"],
        scenario=artifacts["scenario"],
        workbook=context.resolve_path(workbook) if isinstance(workbook, str) else None,
        workbook_record=artifacts.get("workbook_record"),
        oracle_result=artifacts.get("oracle_result"),
        verbose=False,
    )


def _resolved_artifacts(node: Any, context: Any) -> dict[str, Path]:
    if not isinstance(node.artifacts, dict):
        return {}
    return {
        key: context.resolve_path(value)
        for key, value in node.artifacts.items()
        if isinstance(value, str)
    }


def _string_artifacts(artifacts: dict[str, Path]) -> dict[str, str]:
    return {key: str(value) for key, value in artifacts.items()}


def _write_json(path: Path, payload: Any) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _missing_key_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    required: tuple[str, ...],
    actual: dict[str, Any],
    field_name: str,
    location: str,
) -> tuple[Any, ...]:
    return tuple(
        diagnostic(
            severity=severity.ERROR,
            code=f"modelwright.{field_name}.missing",
            message=(
                f"Modelwright node requires {field_name} key '{key}' for "
                "non-executing workflow planning."
            ),
            location=f"{location}.{field_name}.{key}",
        )
        for key in required
        if key not in actual
    )


def _empty_parameter_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    parameters: dict[str, Any],
    required: tuple[str, ...],
    location: str,
) -> tuple[Any, ...]:
    diagnostics: list[Any] = []
    for key in required:
        value = parameters.get(key)
        if isinstance(value, str) and not value.strip():
            diagnostics.append(
                diagnostic(
                    severity=severity.ERROR,
                    code="modelwright.parameters.empty",
                    message=f"Modelwright node parameter '{key}' must be nonempty.",
                    location=f"{location}.parameters.{key}",
                )
            )
    return tuple(diagnostics)
