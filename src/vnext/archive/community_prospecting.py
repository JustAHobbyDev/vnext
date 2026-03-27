from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import subprocess


X_DOMAINS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}
COMMUNITY_PLATFORMS = {
    "discord": {"discord.com", "www.discord.com", "discord.gg"},
    "slack": {"join.slack.com", "slack.com", "www.slack.com"},
    "reddit": {"reddit.com", "www.reddit.com", "redd.it"},
    "stocktwits": {"stocktwits.com", "www.stocktwits.com"},
    "substack": {"substack.com", "www.substack.com"},
    "whatsapp": {"api.whatsapp.com", "chat.whatsapp.com", "wa.me"},
    "telegram": {"t.me", "telegram.me"},
}
HUB_DOMAINS = {
    "patreon": {"patreon.com", "www.patreon.com"},
    "quantcha": {"ideas.quantcha.com"},
    "tru_sentiment": {"tru-sentiment.com", "www.tru-sentiment.com"},
}
CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def load_source_sweep(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def extract_community_leads(
    source_sweep: dict[str, object],
    *,
    resolver: callable | None = None,
) -> tuple[dict[str, object], str]:
    resolver = resolver or resolve_shortlink
    ordered_urls = list(source_sweep.get("urls") or [])
    active_post_context: dict[str, str] | None = None

    lead_index: dict[str, dict[str, object]] = {}
    hub_index: dict[str, dict[str, object]] = {}
    unresolved_shortlinks: list[dict[str, str]] = []
    source_account_counts: Counter[str] = Counter()

    for url in ordered_urls:
        x_context = _extract_x_context(url)
        if x_context is not None:
            active_post_context = x_context
            source_account_counts[x_context["source_account"]] += 1
            continue

        if _is_shortlink(url):
            resolved_url = resolver(url)
            if resolved_url == url:
                unresolved_shortlinks.append(
                    {
                        "short_url": url,
                        "source_post_url": (active_post_context or {}).get("source_post_url"),
                        "source_account": (active_post_context or {}).get("source_account"),
                    }
                )
                continue
            lead_record = _classify_candidate_destination(resolved_url)
            if lead_record is None:
                continue
            _record_sighting(
                lead_index if lead_record["lead_bucket"] == "community_leads" else hub_index,
                lead_record,
                source_url=url,
                source_context=active_post_context,
            )
            continue

        lead_record = _classify_candidate_destination(url)
        if lead_record is None:
            continue
        _record_sighting(
            lead_index if lead_record["lead_bucket"] == "community_leads" else hub_index,
            lead_record,
            source_url=url,
            source_context=active_post_context,
        )

    community_leads = _finalize_leads(lead_index)
    candidate_hubs = _finalize_leads(hub_index)
    summary = {
        "ordered_url_count": len(ordered_urls),
        "community_lead_count": len(community_leads),
        "candidate_hub_count": len(candidate_hubs),
        "unresolved_shortlink_count": len(unresolved_shortlinks),
        "platform_counts": dict(Counter(lead["platform"] for lead in community_leads)),
        "source_account_counts": dict(source_account_counts.most_common(20)),
    }
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "schema_version": "v1",
        "generated_at": generated_at,
        "source_artifact": "research/analysis/2026-03-25-grok-lite-source-sweep-v1.json",
        "summary": summary,
        "community_leads": community_leads,
        "candidate_hubs": candidate_hubs,
        "unresolved_shortlinks": unresolved_shortlinks,
    }
    return payload, render_review_surface(payload)


def render_review_surface(payload: dict[str, object]) -> str:
    lines = [
        "# LITE Community Prospecting Leads v1",
        "",
        f"Generated at: {payload['generated_at']}",
        "",
        "## Summary",
        "",
        f"- community leads: `{payload['summary']['community_lead_count']}`",
        f"- candidate hubs: `{payload['summary']['candidate_hub_count']}`",
        f"- unresolved shortlinks: `{payload['summary']['unresolved_shortlink_count']}`",
        "",
        "## Community Leads",
        "",
    ]

    for lead in payload["community_leads"]:
        source_accounts = ", ".join(lead["source_accounts"][:8])
        lines.extend(
            [
                f"### {lead['platform']} :: {lead['destination_url']}",
                f"- confidence: `{lead['confidence']}`",
                f"- sightings: `{lead['sighting_count']}`",
                f"- source accounts: `{source_accounts}`",
                f"- source posts: `{', '.join(lead['source_post_urls'][:5])}`",
                "",
            ]
        )

    if payload["candidate_hubs"]:
        lines.extend(
            [
                "## Candidate Hubs",
                "",
            ]
        )
        for lead in payload["candidate_hubs"]:
            lines.extend(
                [
                    f"### {lead['platform']} :: {lead['destination_url']}",
                    f"- confidence: `{lead['confidence']}`",
                    f"- sightings: `{lead['sighting_count']}`",
                    f"- source accounts: `{', '.join(lead['source_accounts'][:8])}`",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def write_payload(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


def write_review_surface(path: Path, markdown: str) -> None:
    path.write_text(markdown)


def resolve_shortlink(url: str, timeout_seconds: int = 20) -> str:
    result = subprocess.run(
        [
            "curl",
            "-fsSL",
            "-o",
            "/dev/null",
            "-w",
            "%{url_effective}",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    final_url = (result.stdout or "").strip()
    return final_url or url


def _extract_x_context(url: str) -> dict[str, str] | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() not in X_DOMAINS:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 3 or parts[1] != "status":
        return None
    return {
        "source_post_url": _strip_query(url),
        "source_account": parts[0],
        "source_status_id": parts[2],
    }


def _classify_candidate_destination(url: str) -> dict[str, str] | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    stripped_url = _strip_query(url)

    for platform, domains in COMMUNITY_PLATFORMS.items():
        if host in domains:
            return {
                "platform": platform,
                "destination_url": stripped_url,
                "confidence": "high" if platform in {"discord", "whatsapp", "slack", "telegram"} else "medium",
                "lead_bucket": "community_leads",
            }

    for platform, domains in HUB_DOMAINS.items():
        if host in domains:
            return {
                "platform": platform,
                "destination_url": stripped_url,
                "confidence": "low",
                "lead_bucket": "candidate_hubs",
            }

    return None


def _record_sighting(
    lead_index: dict[str, dict[str, object]],
    lead_record: dict[str, str],
    *,
    source_url: str,
    source_context: dict[str, str] | None,
) -> None:
    destination_url = lead_record["destination_url"]
    entry = lead_index.setdefault(
        destination_url,
        {
            "lead_id": f"community-lead-{len(lead_index) + 1}",
            **lead_record,
            "source_accounts": [],
            "source_post_urls": [],
            "source_urls": [],
            "sighting_count": 0,
        },
    )
    entry["sighting_count"] += 1
    if source_context is not None:
        _append_unique(entry["source_accounts"], source_context["source_account"])
        _append_unique(entry["source_post_urls"], source_context["source_post_url"])
    _append_unique(entry["source_urls"], source_url)


def _finalize_leads(lead_index: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    leads = list(lead_index.values())
    leads.sort(
        key=lambda lead: (
            CONFIDENCE_RANK[lead["confidence"]],
            lead["sighting_count"],
            len(lead["source_accounts"]),
            lead["destination_url"],
        ),
        reverse=True,
    )
    return leads


def _append_unique(target: list[str], value: str | None) -> None:
    if value and value not in target:
        target.append(value)


def _is_shortlink(url: str) -> bool:
    return urlparse(url).netloc.lower() == "t.co"


def _strip_query(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.lower() == "api.whatsapp.com" and parsed.path == "/send/":
        phone = parse_qs(parsed.query).get("phone", [""])[0]
        return f"https://api.whatsapp.com/send/?phone={phone}" if phone else url
    cleaned = parsed._replace(query="", fragment="")
    return cleaned.geturl()
