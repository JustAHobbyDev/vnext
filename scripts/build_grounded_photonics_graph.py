from __future__ import annotations

import json
from pathlib import Path

from vnext.graph.grounded_photonics import build_grounded_photonics_graph


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_json = (
        project_root / "research" / "analysis" / "aleabitoreddit-photonics-grounded-graph-v1.json"
    )
    output_md = (
        project_root
        / "research"
        / "analysis"
        / "aleabitoreddit-photonics-grounded-graph-review-surface-v1.md"
    )

    run = build_grounded_photonics_graph()
    output_json.write_text(json.dumps(run.to_dict(), indent=2, ensure_ascii=True))
    output_md.write_text(render_review_surface(run))

    print(output_json)
    print(output_md)


def render_review_surface(run) -> str:
    lines = [
        "# Photonics Grounded Graph Review Surface v1",
        "",
        f"- graph id: `{run.graph_id}`",
        f"- seed clue: `{run.graph.seed_clue.clue_id}`",
        "",
        "## Nodes",
        "",
    ]
    for node in run.graph.nodes:
        lines.append(
            f"- `{node.node_id}` | `{node.node_type}` | `{node.canonical_name}` | public=`{node.is_public}`"
        )
    lines.extend(["", "## Edges", ""])
    for edge in run.graph.edges:
        lines.append(
            f"- `{edge.edge_id}` | `{edge.source_node_id}` -> `{edge.target_node_id}` | "
            f"`{edge.edge_type}` | confidence=`{edge.confidence}` | evidence=`{', '.join(edge.evidence_artifact_ids)}`"
        )
    lines.extend(["", "## Ranked Public Nodes", ""])
    for score in run.scores:
        node = run.graph.node_by_id(score.node_id)
        if not node.is_public:
            continue
        lines.append(
            f"- `{score.node_id}` | composite=`{score.composite_score}` | notes=`{score.score_notes}`"
        )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    main()
