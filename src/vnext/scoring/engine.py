from __future__ import annotations

from vnext.graph.builder import GraphArtifact
from vnext.scoring.models import NodeScore


WEIGHTS = {
    "constraint_score": 0.30,
    "sensitivity_score": 0.25,
    "neglect_score": 0.25,
    "expression_score": 0.20,
}

LEVERAGE_EDGE_TYPES = {"supplier_of", "capacity_for", "bottleneck_to", "proxy_for"}
DEPENDENCY_EDGE_TYPES = {"depends_on"}


def score_graph(graph: GraphArtifact) -> tuple[NodeScore, ...]:
    scores: list[NodeScore] = []
    for node in graph.nodes:
        outgoing = graph.outgoing_edges(node.node_id)
        incoming = graph.incoming_edges(node.node_id)

        leverage_edges = sum(1 for edge in outgoing if edge.edge_type in LEVERAGE_EDGE_TYPES)
        dependency_edges = sum(1 for edge in incoming if edge.edge_type in DEPENDENCY_EDGE_TYPES)
        outbound_confidence = sum(edge.confidence for edge in outgoing) / max(len(outgoing), 1)
        inbound_confidence = sum(edge.confidence for edge in incoming) / max(len(incoming), 1)

        constraint_score = min(1.0, 0.18 + (0.26 * leverage_edges) + (0.18 * dependency_edges))
        sensitivity_score = min(1.0, 0.20 + (0.20 * len(outgoing)) + (0.15 * outbound_confidence))
        neglect_score = max(
            0.0,
            min(1.0, 0.95 - (0.18 * node.source_support_count) + (0.10 if leverage_edges else 0.0)),
        )
        expression_score = min(
            1.0,
            (0.92 if node.is_public else 0.15) + (0.05 * inbound_confidence),
        )

        composite_score = round(
            (
                (constraint_score * WEIGHTS["constraint_score"])
                + (sensitivity_score * WEIGHTS["sensitivity_score"])
                + (neglect_score * WEIGHTS["neglect_score"])
                + (expression_score * WEIGHTS["expression_score"])
            ),
            3,
        )

        notes = (
            f"outgoing={len(outgoing)} leverage_edges={leverage_edges} "
            f"dependency_edges={dependency_edges} public={node.is_public}"
        )
        scores.append(
            NodeScore(
                node_id=node.node_id,
                constraint_score=round(constraint_score, 3),
                sensitivity_score=round(sensitivity_score, 3),
                neglect_score=round(neglect_score, 3),
                expression_score=round(expression_score, 3),
                composite_score=composite_score,
                score_notes=notes,
            )
        )

    return tuple(sorted(scores, key=lambda score: score.composite_score, reverse=True))
