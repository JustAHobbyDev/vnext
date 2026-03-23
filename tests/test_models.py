from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from vnext.clues import Clue
from vnext.evidence import EvidenceArtifact
from vnext.graph import EDGE_VOCABULARY, GraphEdge, GraphNode
from vnext.scoring import NodeScore


def test_clue_serializes_observed_at() -> None:
    clue = Clue(
        clue_id="clue-1",
        clue_type="filing",
        observed_at=datetime(2026, 3, 22, 12, 0, tzinfo=ZoneInfo("America/Chicago")),
        source_class="sec",
        source_url="https://www.sec.gov/example",
        text_span="Example evidence span.",
        theme_hint="photonics",
        evidence_confidence=0.8,
    )

    assert clue.to_dict()["observed_at"] == "2026-03-22T12:00:00-05:00"
    assert clue.to_dict()["evidence_artifact_ids"] == []


def test_evidence_artifact_rejects_invalid_root_url() -> None:
    with pytest.raises(ValueError):
        EvidenceArtifact(
            artifact_id="artifact-1",
            artifact_kind="primary_press_release",
            source_class="company_ir",
            source_url="not-a-url",
            captured_at=datetime(2026, 3, 22, 12, 0, tzinfo=ZoneInfo("America/Chicago")),
            local_path="raw/example.md",
            sha256="0" * 64,
            is_real_world=True,
            verification_status="root",
            content_excerpt="Example evidence span.",
        )


def test_graph_edge_rejects_unknown_vocab() -> None:
    with pytest.raises(ValueError):
        GraphEdge(
            edge_id="edge-1",
            source_node_id="a",
            target_node_id="b",
            edge_type="unknown_edge",
            evidence_artifact_ids=("artifact-1",),
            confidence=0.5,
        )

    assert "supplier_of" in EDGE_VOCABULARY


def test_node_score_requires_non_empty_notes() -> None:
    with pytest.raises(ValueError):
        NodeScore(
            node_id="axt",
            constraint_score=0.5,
            sensitivity_score=0.5,
            neglect_score=0.5,
            expression_score=0.5,
            composite_score=0.5,
            score_notes="",
        )


def test_graph_node_requires_support() -> None:
    with pytest.raises(ValueError):
        GraphNode(
            node_id="axt",
            node_type="company",
            canonical_name="AXT, Inc.",
            market_type="equity",
            source_support_count=0,
            is_public=True,
        )
