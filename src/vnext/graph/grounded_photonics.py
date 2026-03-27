from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from vnext.clues.models import Clue
from vnext.graph.builder import GraphArtifact
from vnext.graph.models import GraphEdge, GraphNode
from vnext.scoring.engine import score_graph
from vnext.scoring.models import NodeScore


PROJECT_ROOT = Path(__file__).resolve().parents[3]
GROUNDING_PACKS_PATH = (
    PROJECT_ROOT / "research" / "analysis" / "aleabitoreddit-grounded-clue-packs-v1.json"
)
CANDIDATES_PATH = (
    PROJECT_ROOT / "research" / "analysis" / "aleabitoreddit-clue-candidates-v1.json"
)


@dataclass(frozen=True, slots=True)
class GroundedGraphRun:
    graph_id: str
    graph: GraphArtifact
    scores: tuple[NodeScore, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "graph": self.graph.to_dict(),
            "scores": [score.to_dict() for score in self.scores],
        }


def build_grounded_photonics_graph() -> GroundedGraphRun:
    candidates = json.loads(CANDIDATES_PATH.read_text())["candidates"]
    packs = json.loads(GROUNDING_PACKS_PATH.read_text())["packs"]
    pack_ids = {pack["pack_id"] for pack in packs}

    seed_candidate = next(
        candidate
        for candidate in candidates
        if candidate["candidate_id"] == "archive-clue-2003083807273152736"
    )
    seed_clue = Clue(
        clue_id=seed_candidate["candidate_id"],
        clue_type="archive_relationship_clue",
        observed_at=datetime.fromisoformat(seed_candidate["created_at"].replace("Z", "+00:00")),
        source_class="x_post_archive",
        source_url=f"https://x.com/aleabitoreddit/status/{seed_candidate['post_id']}",
        text_span=seed_candidate["text_excerpt"],
        theme_hint="photonics",
        evidence_confidence=0.8,
        evidence_artifact_ids=("grounded-pack-lite-cohr-ai-photonics-v1",),
    )

    nodes = (
        GraphNode(
            node_id="lumentum",
            node_type="company",
            canonical_name="Lumentum Holdings Inc.",
            market_type="equity",
            source_support_count=3,
            is_public=True,
        ),
        GraphNode(
            node_id="coherent",
            node_type="company",
            canonical_name="Coherent Corp.",
            market_type="equity",
            source_support_count=3,
            is_public=True,
        ),
        GraphNode(
            node_id="axt",
            node_type="company",
            canonical_name="AXT, Inc.",
            market_type="equity",
            source_support_count=4,
            is_public=True,
        ),
        GraphNode(
            node_id="iqe",
            node_type="company",
            canonical_name="IQE plc",
            market_type="equity",
            source_support_count=2,
            is_public=True,
        ),
        GraphNode(
            node_id="aoi",
            node_type="company",
            canonical_name="Applied Optoelectronics, Inc.",
            market_type="equity",
            source_support_count=2,
            is_public=True,
        ),
        GraphNode(
            node_id="ai_data_center_photonics",
            node_type="theme",
            canonical_name="AI Data Center Photonics",
            market_type="private",
            source_support_count=4,
            is_public=False,
        ),
        GraphNode(
            node_id="indium_phosphide",
            node_type="material",
            canonical_name="Indium Phosphide",
            market_type="private",
            source_support_count=2,
            is_public=False,
        ),
    )

    edges = (
        GraphEdge(
            edge_id="lumentum-capacity-ai-photonics",
            source_node_id="lumentum",
            target_node_id="ai_data_center_photonics",
            edge_type="capacity_for",
            evidence_artifact_ids=("grounded-pack-lite-cohr-ai-photonics-v1",),
            confidence=0.82,
        ),
        GraphEdge(
            edge_id="coherent-capacity-ai-photonics",
            source_node_id="coherent",
            target_node_id="ai_data_center_photonics",
            edge_type="capacity_for",
            evidence_artifact_ids=("grounded-pack-lite-cohr-ai-photonics-v1",),
            confidence=0.79,
        ),
        GraphEdge(
            edge_id="aoi-capacity-ai-photonics",
            source_node_id="aoi",
            target_node_id="ai_data_center_photonics",
            edge_type="capacity_for",
            evidence_artifact_ids=("grounded-pack-aaoi-ai-transceiver-capacity-v1",),
            confidence=0.74,
        ),
        GraphEdge(
            edge_id="indium-phosphide-bottleneck-ai-photonics",
            source_node_id="indium_phosphide",
            target_node_id="ai_data_center_photonics",
            edge_type="bottleneck_to",
            evidence_artifact_ids=("grounded-pack-axti-inp-ai-interconnect-v1",),
            confidence=0.85,
        ),
        GraphEdge(
            edge_id="axt-proxy-indium-phosphide",
            source_node_id="axt",
            target_node_id="indium_phosphide",
            edge_type="proxy_for",
            evidence_artifact_ids=("grounded-pack-axti-inp-ai-interconnect-v1",),
            confidence=0.82,
        ),
        GraphEdge(
            edge_id="axt-supplier-lumentum",
            source_node_id="axt",
            target_node_id="lumentum",
            edge_type="supplier_of",
            evidence_artifact_ids=(
                "grounded-pack-axti-inp-ai-interconnect-v1",
                "grounded-pack-lite-cohr-ai-photonics-v1",
            ),
            confidence=0.73,
        ),
        GraphEdge(
            edge_id="axt-supplier-coherent",
            source_node_id="axt",
            target_node_id="coherent",
            edge_type="supplier_of",
            evidence_artifact_ids=(
                "grounded-pack-axti-inp-ai-interconnect-v1",
                "grounded-pack-lite-cohr-ai-photonics-v1",
            ),
            confidence=0.71,
        ),
        GraphEdge(
            edge_id="iqe-supplier-lumentum",
            source_node_id="iqe",
            target_node_id="lumentum",
            edge_type="supplier_of",
            evidence_artifact_ids=("grounded-pack-iqe-lumentum-supplier-v1",),
            confidence=0.86,
        ),
    )

    # Guard against drift between this graph and the manual grounding pack set.
    for edge in edges:
        missing = [artifact_id for artifact_id in edge.evidence_artifact_ids if artifact_id not in pack_ids]
        if missing:
            raise ValueError(f"edge {edge.edge_id} references unknown pack ids: {missing}")

    graph = GraphArtifact(
        benchmark_id="archive_photonics_grounded",
        seed_clue=seed_clue,
        nodes=nodes,
        edges=edges,
    )
    return GroundedGraphRun(
        graph_id="archive_photonics_grounded_v1",
        graph=graph,
        scores=score_graph(graph),
    )
