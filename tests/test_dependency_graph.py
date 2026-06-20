import json
from pathlib import Path

from sheetforge.extraction import extract_workbook
from sheetforge.graph import DependencyGraph, build_dependency_graph
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def test_build_dependency_graph_recovers_synthetic_execution_edges(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))

    graph = build_dependency_graph(workbook)

    assert [(edge.source.normalized, edge.target.normalized) for edge in graph.execution_edges] == [
        ("Inputs!B2", "Calc!B2"),
        ("Inputs!B3", "Calc!B2"),
        ("Calc!B2", "Calc!B3"),
        ("Inputs!B4", "Calc!B3"),
        ("Calc!B3", "Calc!B4"),
        ("Calc!B4", "Summary!B2"),
        ("Summary!B2", "Summary!B3"),
    ]


def test_build_dependency_graph_preserves_semantic_named_range_edges(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))

    graph = build_dependency_graph(workbook)
    semantic_edges = [
        edge for edge in graph.semantic_edges if edge.target.normalized == "Calc!B2"
    ]
    execution_edges = [
        edge for edge in graph.execution_edges if edge.target.normalized == "Calc!B2"
    ]

    assert [(edge.source.kind, edge.source.normalized, edge.raw_reference) for edge in semantic_edges] == [
        ("named_range", "BaseVolume", "BaseVolume"),
        ("named_range", "GrowthRate", "GrowthRate"),
    ]
    assert [(edge.source.normalized, edge.resolved_from.normalized) for edge in execution_edges if edge.resolved_from] == [
        ("Inputs!B2", "BaseVolume"),
        ("Inputs!B3", "GrowthRate"),
    ]


def test_dependency_graph_payload_round_trips(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))

    graph = build_dependency_graph(workbook)
    payload = graph.to_dict()

    assert json.loads(json.dumps(payload)) == payload
    assert DependencyGraph.from_dict(payload) == graph
