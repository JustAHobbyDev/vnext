from vnext.graph.grounded_photonics import build_grounded_photonics_graph


def test_grounded_photonics_graph_builds_expected_nodes_and_edges() -> None:
    run = build_grounded_photonics_graph()

    assert run.graph_id == "archive_photonics_grounded_v1"
    assert run.graph.seed_clue.theme_hint == "photonics"
    assert {node.node_id for node in run.graph.nodes} == {
        "lumentum",
        "coherent",
        "axt",
        "iqe",
        "aoi",
        "ai_data_center_photonics",
        "indium_phosphide",
    }
    assert len(run.graph.edges) == 8


def test_grounded_photonics_graph_ranks_axt_highest_public_node() -> None:
    run = build_grounded_photonics_graph()

    public_scores = [
        score for score in run.scores if run.graph.node_by_id(score.node_id).is_public
    ]

    assert public_scores[0].node_id == "axt"
    assert public_scores[0].composite_score > public_scores[-1].composite_score
