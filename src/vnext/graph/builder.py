from __future__ import annotations

from dataclasses import dataclass

from vnext.clues.models import Clue
from vnext.graph.models import GraphEdge, GraphNode


@dataclass(frozen=True, slots=True)
class GraphArtifact:
    benchmark_id: str
    seed_clue: Clue
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]

    def __post_init__(self) -> None:
        node_ids = {node.node_id for node in self.nodes}
        if not node_ids:
            raise ValueError("graph requires at least one node")
        for edge in self.edges:
            if edge.source_node_id not in node_ids or edge.target_node_id not in node_ids:
                raise ValueError("edge references unknown node")

    def node_by_id(self, node_id: str) -> GraphNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise KeyError(node_id)

    def outgoing_edges(self, node_id: str) -> tuple[GraphEdge, ...]:
        return tuple(edge for edge in self.edges if edge.source_node_id == node_id)

    def incoming_edges(self, node_id: str) -> tuple[GraphEdge, ...]:
        return tuple(edge for edge in self.edges if edge.target_node_id == node_id)

    def candidate_nodes(self) -> tuple[GraphNode, ...]:
        return tuple(node for node in self.nodes if node.is_public)

    def to_dict(self) -> dict[str, object]:
        return {
            "benchmark_id": self.benchmark_id,
            "seed_clue": self.seed_clue.to_dict(),
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }
