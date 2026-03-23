from vnext.benchmarks import build_photonics_benchmark


def test_photonics_benchmark_builds_expected_graph() -> None:
    run = build_photonics_benchmark()

    assert run.benchmark_id == "photonics"
    assert run.graph.seed_clue.theme_hint == "photonics"
    assert {node.node_id for node in run.graph.nodes} == {
        "lumentum",
        "coherent",
        "axt",
        "jx_advanced_metals",
    }
    assert len(run.graph.edges) == 5


def test_photonics_top_public_candidate_is_axt() -> None:
    run = build_photonics_benchmark()

    top = run.top_public_candidate()

    assert top.node_id == "axt"
    assert top.composite_score > 0.7
    assert top.composite_score > run.scores[-1].composite_score


def test_photonics_benchmark_serializes_scores() -> None:
    run = build_photonics_benchmark()
    payload = run.to_dict()

    assert payload["benchmark_id"] == "photonics"
    assert len(payload["scores"]) == 4
    assert payload["scores"][0]["node_id"] == "axt"
