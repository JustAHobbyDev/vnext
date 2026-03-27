from vnext.archive.clue_extraction import evaluate_post, extract_clue_candidates


def test_evaluate_post_detects_dependency_candidate() -> None:
    candidate = evaluate_post(
        {
            "post_id": "100",
            "created_at": "2026-01-01T00:00:00Z",
            "bucket_date": "2026-01-01",
            "text": (
                "ALAB customer base is Mag 7 and 37% of revenue comes from AI "
                "interconnect demand. Similar company to CRDO."
            ),
            "cashtags": ["ALAB", "CRDO"],
            "mentioned_users": [],
            "external_urls": ["https://example.com/report"],
            "reply_to_post_id": None,
            "quoted_post_id": None,
            "retweeted_post_id": None,
            "conversation_root_id": "100",
            "probable_media_urls": [],
            "cashtag_count": 2,
            "mention_count": 0,
            "external_link_count": 1,
        }
    )

    assert candidate is not None
    assert candidate["review_priority"] == "high"
    assert "dependency_signal" in candidate["clue_types"]
    assert "relationship_signal" in candidate["clue_types"]


def test_evaluate_post_suppresses_ratings_list_shape() -> None:
    candidate = evaluate_post(
        {
            "post_id": "200",
            "created_at": "2026-01-01T00:00:00Z",
            "bucket_date": "2026-01-01",
            "text": "Friday Market Close. Strong Buy $AAA $BBB $CCC $DDD $EEE $FFF $GGG $HHH $III",
            "cashtags": ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "III"],
            "mentioned_users": [],
            "external_urls": [],
            "reply_to_post_id": None,
            "quoted_post_id": None,
            "retweeted_post_id": None,
            "conversation_root_id": "200",
            "probable_media_urls": [],
            "cashtag_count": 9,
            "mention_count": 0,
            "external_link_count": 0,
        }
    )

    assert candidate is None


def test_extract_clue_candidates_produces_summary_counts() -> None:
    payload, review = extract_clue_candidates(
        {
            "posts": [
                {
                    "post_id": "100",
                    "created_at": "2026-01-01T00:00:00Z",
                    "bucket_date": "2026-01-01",
                    "text": "Only small cap company with customer exposure to NVDA and AMZN.",
                    "cashtags": ["ALAB", "NVDA", "AMZN"],
                    "mentioned_users": [],
                    "external_urls": [],
                    "reply_to_post_id": None,
                    "quoted_post_id": None,
                    "retweeted_post_id": None,
                    "conversation_root_id": "100",
                    "probable_media_urls": [],
                    "cashtag_count": 3,
                    "mention_count": 0,
                    "external_link_count": 0,
                }
            ]
        }
    )

    assert payload["summary"]["candidate_count"] == 1
    assert "archive-clue-100" in review
