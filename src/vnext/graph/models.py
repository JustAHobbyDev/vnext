from __future__ import annotations

from dataclasses import asdict, dataclass


EDGE_VOCABULARY = {
    "supplier_of",
    "customer_of",
    "partner_of",
    "capacity_for",
    "depends_on",
    "bottleneck_to",
    "proxy_for",
}


@dataclass(frozen=True, slots=True)
class GraphNode:
    node_id: str
    node_type: str
    canonical_name: str
    market_type: str
    source_support_count: int
    is_public: bool

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        if not self.canonical_name.strip():
            raise ValueError("canonical_name is required")
        if self.source_support_count < 1:
            raise ValueError("source_support_count must be positive")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GraphEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    evidence_artifact_ids: tuple[str, ...]
    confidence: float

    def __post_init__(self) -> None:
        if not self.edge_id:
            raise ValueError("edge_id is required")
        if self.edge_type not in EDGE_VOCABULARY:
            raise ValueError(f"edge_type must be one of {sorted(EDGE_VOCABULARY)}")
        if not self.evidence_artifact_ids:
            raise ValueError("evidence_artifact_ids must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "evidence_artifact_ids": list(self.evidence_artifact_ids),
        }
