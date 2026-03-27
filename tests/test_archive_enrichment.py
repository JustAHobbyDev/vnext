from vnext.archive.enrichment import build_link_graph, classify_url, enrich_post


def test_classify_url_marks_x_photo_as_probable_media() -> None:
    record = classify_url("https://x.com/aleabitoreddit/status/1940361849985458270/photo/1")

    assert record["classification"] == "x_post_photo"
    assert record["is_probable_media"] is True
    assert record["domain"] == "x.com"


def test_enrich_post_normalizes_entities_and_references() -> None:
    enriched = enrich_post(
        {
            "author_id": "1",
            "bucket_date": "2026-01-01",
            "conversation_id": "100",
            "created_at": "2026-01-01T00:00:00Z",
            "entities": {
                "urls": [
                    "https://x.com/example/status/123/photo/1",
                    "https://example.com/report",
                    "https://example.com/report",
                ],
                "mentions": ["UserA", "UserA", "userb"],
                "cashtags": ["upwk", "UPWK"],
                "hashtags": ["Theme"],
            },
            "id": "100",
            "lang": "en",
            "public_metrics": {
                "bookmark_count": 1,
                "impression_count": 2,
                "like_count": 3,
                "quote_count": 4,
                "reply_count": 5,
                "retweet_count": 6,
            },
            "referenced_tweets": [
                {"type": "replied_to", "id": "90"},
                {"type": "quoted", "id": "80"},
            ],
            "text": "example",
        }
    )

    assert enriched["post_id"] == "100"
    assert enriched["urls"] == [
        "https://x.com/example/status/123/photo/1",
        "https://example.com/report",
    ]
    assert enriched["domains"] == ["x.com", "example.com"]
    assert enriched["probable_media_urls"] == ["https://x.com/example/status/123/photo/1"]
    assert enriched["external_urls"] == ["https://example.com/report"]
    assert enriched["mentioned_users"] == ["UserA", "userb"]
    assert enriched["cashtags"] == ["UPWK"]
    assert enriched["reply_to_post_id"] == "90"
    assert enriched["quoted_post_id"] == "80"


def test_build_link_graph_creates_post_and_domain_edges() -> None:
    graph = build_link_graph(
        [
            {
                "post_id": "100",
                "domains": ["example.com"],
                "url_records": [
                    {
                        "url": "https://example.com/report",
                        "classification": "external_link",
                        "domain": "example.com",
                        "is_probable_media": False,
                    }
                ],
                "mentioned_users": ["usera"],
                "cashtags": ["UPWK"],
                "hashtags": [],
                "referenced_tweets": [{"type": "replied_to", "id": "90"}],
            }
        ]
    )

    edge_types = {edge["edge_type"] for edge in graph["edges"]}
    assert "links_to_domain" in edge_types
    assert "links_to_url" in edge_types
    assert "mentions_user" in edge_types
    assert "mentions_cashtag" in edge_types
    assert "references_post_replied_to" in edge_types
