from __future__ import annotations

from collections import Counter
from datetime import datetime, UTC
from pathlib import Path
import json
import re


DEPENDENCY_PATTERNS = (
    re.compile(
        r"\b(supplier|customer|customer base|partner|depends on|used for|utilized for|"
        r"serving|contracts with|exposure to|profits come from|revenue comes from|"
        r"revenue from|market segments?)\b",
        re.I,
    ),
)
BOTTLENECK_PATTERNS = (
    re.compile(
        r"\b(bottleneck|chokepoint|sole|only small cap|only company|shortage|"
        r"constrained|constraint|capacity|backlog|lead time|systemic exposure)\b",
        re.I,
    ),
)
RELATIONSHIP_PATTERNS = (
    re.compile(
        r"\b(similar company to|similar to|rise together|catch-up|catch up|"
        r"related sectors|industry adjacent|proxy|associated with|like how|"
        r"pair trade|compared to)\b",
        re.I,
    ),
)
SPECIFICITY_PATTERNS = (
    re.compile(r"\b\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?\b"),
    re.compile(r"\bMag ?7\b", re.I),
    re.compile(r"\by/y\b", re.I),
)
RATINGS_LIST_PATTERNS = (
    re.compile(r"\bStrong Buy\b", re.I),
    re.compile(r"\bMonday Market Close\b", re.I),
    re.compile(r"\bFriday Market Close\b", re.I),
    re.compile(r"\bratings\b", re.I),
    re.compile(r"\bHold\b.+\bSell\b", re.I),
)


def load_enriched_archive(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def extract_clue_candidates(
    enriched_archive: dict[str, object],
) -> tuple[dict[str, object], str]:
    posts = enriched_archive["posts"]
    candidates = []
    for post in posts:
        candidate = evaluate_post(post)
        if candidate is not None:
            candidates.append(candidate)

    candidates.sort(
        key=lambda candidate: (
            candidate["priority_rank"],
            candidate["heuristic_score"],
            candidate["created_at"],
        ),
        reverse=True,
    )
    summary = {
        "candidate_count": len(candidates),
        "high_priority_count": sum(
            1 for candidate in candidates if candidate["review_priority"] == "high"
        ),
        "medium_priority_count": sum(
            1 for candidate in candidates if candidate["review_priority"] == "medium"
        ),
        "type_counts": dict(
            Counter(
                clue_type
                for candidate in candidates
                for clue_type in candidate["clue_types"]
            )
        ),
    }
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "schema_version": "v1",
        "generated_at": generated_at,
        "source_archive": "research/analysis/aleabitoreddit-archive-enriched-v1.json",
        "summary": summary,
        "candidates": candidates,
    }
    markdown = render_review_surface(payload)
    return payload, markdown


def evaluate_post(post: dict[str, object]) -> dict[str, object] | None:
    text = post["text"]
    indicators = []
    clue_types = []
    score = 0
    suppression_flags = []

    multi_entity = post["cashtag_count"] + post["mention_count"] >= 2
    if multi_entity:
        indicators.append("multiple entities referenced")
        clue_types.append("multi_entity_signal")
        score += 1

    if post["external_link_count"] > 0:
        indicators.append("contains external evidence link")
        clue_types.append("linked_evidence_signal")
        score += 2

    if post["quoted_post_id"] or post["reply_to_post_id"]:
        indicators.append("embedded in reply/quote context")
        clue_types.append("conversation_signal")
        score += 1

    if _matches_any(text, DEPENDENCY_PATTERNS):
        indicators.append("dependency language")
        clue_types.append("dependency_signal")
        score += 3

    if _matches_any(text, BOTTLENECK_PATTERNS):
        indicators.append("bottleneck or constraint language")
        clue_types.append("bottleneck_signal")
        score += 3

    if _matches_any(text, RELATIONSHIP_PATTERNS):
        indicators.append("comparative or relationship language")
        clue_types.append("relationship_signal")
        score += 2

    if _matches_any(text, SPECIFICITY_PATTERNS):
        indicators.append("contains unusually specific numeric detail")
        clue_types.append("specificity_signal")
        score += 1

    if post["cashtag_count"] >= 3:
        indicators.append("dense ticker set")
        score += 1

    if post["mention_count"] >= 2:
        indicators.append("multiple user references")
        score += 1

    if _matches_any(text, RATINGS_LIST_PATTERNS) and post["cashtag_count"] >= 8:
        suppression_flags.append("ratings_list_shape")
        score -= 4

    if post["cashtag_count"] >= 15 and not any(
        clue_type in clue_types
        for clue_type in ("dependency_signal", "bottleneck_signal", "relationship_signal")
    ):
        suppression_flags.append("ticker_list_without_relation_signal")
        score -= 3

    clue_types = _dedupe_preserve_order(clue_types)
    indicators = _dedupe_preserve_order(indicators)
    if score < 3:
        return None
    if not any(
        clue_type in clue_types
        for clue_type in (
            "dependency_signal",
            "bottleneck_signal",
            "relationship_signal",
            "linked_evidence_signal",
        )
    ):
        return None
    if "ratings_list_shape" in suppression_flags and score < 5:
        return None

    review_priority = "medium"
    priority_rank = 2
    if score >= 6:
        review_priority = "high"
        priority_rank = 3
    elif score <= 3:
        review_priority = "low"
        priority_rank = 1

    return {
        "candidate_id": f"archive-clue-{post['post_id']}",
        "post_id": post["post_id"],
        "created_at": post["created_at"],
        "bucket_date": post["bucket_date"],
        "heuristic_score": score,
        "review_priority": review_priority,
        "priority_rank": priority_rank,
        "clue_types": clue_types,
        "indicators": indicators,
        "suppression_flags": suppression_flags,
        "text_excerpt": _excerpt(text),
        "cashtags": post["cashtags"],
        "mentioned_users": post["mentioned_users"],
        "external_urls": post["external_urls"],
        "reply_to_post_id": post["reply_to_post_id"],
        "quoted_post_id": post["quoted_post_id"],
        "retweeted_post_id": post["retweeted_post_id"],
        "conversation_root_id": post["conversation_root_id"],
        "probable_media_urls": post["probable_media_urls"],
    }


def render_review_surface(payload: dict[str, object]) -> str:
    lines = [
        "# AleaBito Discovery Review Surface v1",
        "",
        f"Generated at: {payload['generated_at']}",
        "",
        "## Summary",
        "",
        f"- candidate count: `{payload['summary']['candidate_count']}`",
        f"- high priority: `{payload['summary']['high_priority_count']}`",
        f"- medium priority: `{payload['summary']['medium_priority_count']}`",
        "",
        "## Top Candidates",
        "",
    ]

    for candidate in payload["candidates"][:40]:
        lines.extend(
            [
                f"### {candidate['candidate_id']}",
                f"- priority: `{candidate['review_priority']}`",
                f"- score: `{candidate['heuristic_score']}`",
                f"- clue types: `{', '.join(candidate['clue_types'])}`",
                f"- indicators: `{', '.join(candidate['indicators'])}`",
                f"- cashtags: `{', '.join(candidate['cashtags'][:10])}`",
                f"- mentions: `{', '.join(candidate['mentioned_users'][:10])}`",
                f"- external urls: `{', '.join(candidate['external_urls'][:5])}`",
                f"- reply_to: `{candidate['reply_to_post_id']}`",
                f"- quoted_post_id: `{candidate['quoted_post_id']}`",
                "",
                candidate["text_excerpt"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_candidates(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


def write_review_surface(path: Path, markdown: str) -> None:
    path.write_text(markdown)


def _matches_any(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def _excerpt(text: str, limit: int = 420) -> str:
    flattened = " ".join(text.split())
    return flattened[:limit]


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output
