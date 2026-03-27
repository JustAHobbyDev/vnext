from vnext.archive.community_prospecting import extract_community_leads


def test_extract_community_leads_attributes_resolved_discord_to_source_post() -> None:
    payload, review = extract_community_leads(
        {
            "urls": [
                "https://x.com/Signal_Trader09/status/2029264974561067135?referrer=grok-com",
                "https://t.co/ZgnDtQXYqz",
            ]
        },
        resolver=lambda _: "https://discord.com/invite/jjbT64yGmJ",
    )

    assert payload["summary"]["community_lead_count"] == 1
    lead = payload["community_leads"][0]
    assert lead["platform"] == "discord"
    assert lead["destination_url"] == "https://discord.com/invite/jjbT64yGmJ"
    assert lead["source_accounts"] == ["Signal_Trader09"]
    assert lead["source_post_urls"] == ["https://x.com/Signal_Trader09/status/2029264974561067135"]
    assert "jjbT64yGmJ" in review


def test_extract_community_leads_collects_candidate_hubs_and_unresolved_shortlinks() -> None:
    payload, _ = extract_community_leads(
        {
            "urls": [
                "https://x.com/QuantchaIdeas/status/1874140692769104376?referrer=grok-com",
                "https://t.co/3sO8fpiQV9",
                "https://x.com/Unknown/status/1?referrer=grok-com",
                "https://t.co/unresolved",
            ]
        },
        resolver=lambda url: (
            "https://ideas.quantcha.com/?p=148204"
            if url.endswith("3sO8fpiQV9")
            else url
        ),
    )

    assert payload["summary"]["candidate_hub_count"] == 1
    assert payload["candidate_hubs"][0]["platform"] == "quantcha"
    assert payload["summary"]["unresolved_shortlink_count"] == 1


def test_extract_community_leads_keeps_multiple_sightings_of_same_destination() -> None:
    payload, _ = extract_community_leads(
        {
            "urls": [
                "https://x.com/Toby_Garvan/status/1984301045946687780?referrer=grok-com",
                "https://t.co/c56reqioqi",
                "https://x.com/Signal_Trader09/status/2027300185077150044?referrer=grok-com",
                "https://t.co/CkhigCQUe5",
            ]
        },
        resolver=lambda _: "https://discord.com/invite/GZ3Xc87eub",
    )

    lead = payload["community_leads"][0]
    assert lead["sighting_count"] == 2
    assert lead["source_accounts"] == ["Toby_Garvan", "Signal_Trader09"]
