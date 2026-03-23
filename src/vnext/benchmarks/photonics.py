from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vnext.benchmarks.loader import load_case_inputs
from vnext.graph.builder import GraphArtifact
from vnext.graph.models import GraphEdge, GraphNode
from vnext.scoring.engine import score_graph
from vnext.scoring.models import NodeScore


PHOTONICS_CASE_DIR = (
    Path(__file__).resolve().parents[3] / "benchmarks" / "photonics"
)


@dataclass(frozen=True, slots=True)
class BenchmarkRun:
    benchmark_id: str
    graph: GraphArtifact
    scores: tuple[NodeScore, ...]

    def top_public_candidate(self) -> NodeScore:
        public_ids = {node.node_id for node in self.graph.candidate_nodes()}
        for score in self.scores:
            if score.node_id in public_ids:
                return score
        raise ValueError("benchmark does not contain a public candidate")

    def to_dict(self) -> dict[str, object]:
        return {
            "benchmark_id": self.benchmark_id,
            "graph": self.graph.to_dict(),
            "scores": [score.to_dict() for score in self.scores],
        }


def build_photonics_benchmark() -> BenchmarkRun:
    loaded_case = load_case_inputs(PHOTONICS_CASE_DIR)
    clue = loaded_case.clues[0]

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
            source_support_count=2,
            is_public=True,
        ),
        GraphNode(
            node_id="jx_advanced_metals",
            node_type="company",
            canonical_name="JX Advanced Metals Corporation",
            market_type="private",
            source_support_count=2,
            is_public=False,
        ),
    )

    edges = (
        GraphEdge(
            edge_id="axt-supplier-lumentum",
            source_node_id="axt",
            target_node_id="lumentum",
            edge_type="supplier_of",
            evidence_artifact_ids=(
                clue.evidence_artifact_ids[0],
                "axt-2024-10k-inp-applications",
            ),
            confidence=0.82,
        ),
        GraphEdge(
            edge_id="axt-supplier-coherent",
            source_node_id="axt",
            target_node_id="coherent",
            edge_type="supplier_of",
            evidence_artifact_ids=(
                clue.evidence_artifact_ids[0],
                "coherent-2025-annual-report-inp",
            ),
            confidence=0.78,
        ),
        GraphEdge(
            edge_id="jx-supplier-axt",
            source_node_id="jx_advanced_metals",
            target_node_id="axt",
            edge_type="supplier_of",
            evidence_artifact_ids=(
                "jx-inp-substrates-page",
                "jx-crystalline-materials-promotion",
            ),
            confidence=0.74,
        ),
        GraphEdge(
            edge_id="jx-bottleneck-coherent",
            source_node_id="jx_advanced_metals",
            target_node_id="coherent",
            edge_type="bottleneck_to",
            evidence_artifact_ids=(
                "jx-inp-substrates-page",
                "coherent-2025-annual-report-inp",
            ),
            confidence=0.68,
        ),
        GraphEdge(
            edge_id="axt-depends-jx",
            source_node_id="axt",
            target_node_id="jx_advanced_metals",
            edge_type="depends_on",
            evidence_artifact_ids=(
                "jx-inp-substrates-page",
                "axt-2024-10k-inp-applications",
            ),
            confidence=0.72,
        ),
    )

    graph = GraphArtifact(
        benchmark_id="photonics",
        seed_clue=clue,
        nodes=nodes,
        edges=edges,
    )
    return BenchmarkRun(
        benchmark_id="photonics",
        graph=graph,
        scores=score_graph(graph),
    )
