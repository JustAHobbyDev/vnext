from vnext.archive.grounding_queue import build_grounding_queue, evaluate_candidate


def test_evaluate_candidate_prioritizes_photonics_dependency_post() -> None:
    item = evaluate_candidate(
        {
            "candidate_id": "archive-clue-1",
            "post_id": "1",
            "created_at": "2026-01-01T00:00:00Z",
            "heuristic_score": 8,
            "review_priority": "high",
            "clue_types": ["dependency_signal", "bottleneck_signal"],
            "cashtags": ["AXTI", "LITE"],
            "mentioned_users": [],
            "external_urls": [],
            "text_excerpt": "AXTI is an upstream photonics bottleneck and known LITE supplier.",
        }
    )

    assert item is not None
    assert item["theme"] == "photonics"
    assert item["recommended_evidence_mode"] == "manual_evidence_search"
    assert item["queue_score"] >= 13


def test_evaluate_candidate_keeps_direct_link_general_case() -> None:
    item = evaluate_candidate(
        {
            "candidate_id": "archive-clue-2",
            "post_id": "2",
            "created_at": "2026-01-01T00:00:00Z",
            "heuristic_score": 4,
            "review_priority": "medium",
            "clue_types": ["linked_evidence_signal"],
            "cashtags": ["HIVE"],
            "mentioned_users": [],
            "external_urls": ["https://example.com/report"],
            "text_excerpt": "Looks promising. https://example.com/report",
        }
    )

    assert item is not None
    assert item["theme"] == "general_linked"
    assert item["recommended_evidence_mode"] == "direct_link_first"


def test_build_grounding_queue_limits_and_summarizes() -> None:
    payload, markdown = build_grounding_queue(
        {
            "candidates": [
                {
                    "candidate_id": "archive-clue-1",
                    "post_id": "1",
                    "created_at": "2026-01-01T00:00:00Z",
                    "heuristic_score": 8,
                    "review_priority": "high",
                    "clue_types": ["dependency_signal", "bottleneck_signal"],
                    "cashtags": ["AXTI", "LITE"],
                    "mentioned_users": [],
                    "external_urls": [],
                    "text_excerpt": "AXTI photonics bottleneck",
                }
            ]
        }
    )

    assert payload["summary"]["queue_size"] == 1
    assert payload["queue"][0]["theme"] == "photonics"
    assert "grounding-queue-1" in markdown
