from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
import json
import re


PHOTONICS_KEYWORDS = {
    "AAOI",
    "AMKR",
    "AXTI",
    "AXT",
    "COHR",
    "COHERENT",
    "FEIM",
    "GLW",
    "INP",
    "IQE",
    "LASER",
    "LITE",
    "LPTH",
    "LUMENTUM",
    "PHOTONICS",
    "POET",
    "SIVE",
    "SIVERS",
    "TRANSCEIVER",
}

MEMORY_KEYWORDS = {"HBM", "MU", "SNDK", "SK HYNIX", "SAMSUNG", "NANYA", "AMKR"}


def load_candidates(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def build_grounding_queue(candidates_payload: dict[str, object]) -> tuple[dict[str, object], str]:
    candidates = candidates_payload["candidates"]
    ranked = []
    for candidate in candidates:
        queue_item = evaluate_candidate(candidate)
        if queue_item is not None:
            ranked.append(queue_item)

    ranked.sort(
        key=lambda item: (
            item["queue_score"],
            item["theme_priority"],
            item["heuristic_score"],
            item["created_at"],
        ),
        reverse=True,
    )
    ranked = ranked[:30]

    summary = {
        "queue_size": len(ranked),
        "theme_counts": _count_by(ranked, "theme"),
        "evidence_mode_counts": _count_by(ranked, "recommended_evidence_mode"),
        "priority_counts": _count_by(ranked, "review_priority"),
    }
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "schema_version": "v1",
        "generated_at": generated_at,
        "source_candidates": "research/analysis/aleabitoreddit-clue-candidates-v1.json",
        "summary": summary,
        "queue": ranked,
    }
    markdown = render_grounding_surface(payload)
    return payload, markdown


def evaluate_candidate(candidate: dict[str, object]) -> dict[str, object] | None:
    blob = " ".join(candidate["cashtags"]) + " " + candidate["text_excerpt"]
    text_upper = blob.upper()

    theme = None
    theme_priority = 0
    if any(keyword in text_upper for keyword in PHOTONICS_KEYWORDS):
        theme = "photonics"
        theme_priority = 3
    elif any(keyword in text_upper for keyword in MEMORY_KEYWORDS):
        theme = "memory"
        theme_priority = 2
    elif candidate["external_urls"]:
        theme = "general_linked"
        theme_priority = 1
    else:
        return None

    queue_score = candidate["heuristic_score"]
    if theme == "photonics":
        queue_score += 3
    elif theme == "memory":
        queue_score += 2
    if "dependency_signal" in candidate["clue_types"]:
        queue_score += 2
    if "bottleneck_signal" in candidate["clue_types"]:
        queue_score += 2
    if "relationship_signal" in candidate["clue_types"]:
        queue_score += 1
    if candidate["external_urls"]:
        queue_score += 2
        evidence_mode = "direct_link_first"
    else:
        evidence_mode = "manual_evidence_search"

    if len(candidate["cashtags"]) >= 10:
        queue_score -= 2

    queue_reason = []
    if theme == "photonics":
        queue_reason.append("photonics-like relational post")
    elif theme == "memory":
        queue_reason.append("memory-like relational post")
    else:
        queue_reason.append("linked evidence available")
    if "dependency_signal" in candidate["clue_types"]:
        queue_reason.append("contains dependency language")
    if "bottleneck_signal" in candidate["clue_types"]:
        queue_reason.append("contains bottleneck language")
    if candidate["external_urls"]:
        queue_reason.append("contains external evidence link")

    return {
        "queue_id": f"grounding-queue-{candidate['post_id']}",
        "candidate_id": candidate["candidate_id"],
        "post_id": candidate["post_id"],
        "created_at": candidate["created_at"],
        "theme": theme,
        "theme_priority": theme_priority,
        "queue_score": queue_score,
        "heuristic_score": candidate["heuristic_score"],
        "review_priority": candidate["review_priority"],
        "recommended_evidence_mode": evidence_mode,
        "queue_reason": queue_reason,
        "clue_types": candidate["clue_types"],
        "cashtags": candidate["cashtags"],
        "mentioned_users": candidate["mentioned_users"],
        "external_urls": candidate["external_urls"],
        "text_excerpt": candidate["text_excerpt"],
    }


def render_grounding_surface(payload: dict[str, object]) -> str:
    lines = [
        "# Evidence Grounding Queue v1",
        "",
        f"Generated at: {payload['generated_at']}",
        "",
        "## Summary",
        "",
        f"- queue size: `{payload['summary']['queue_size']}`",
        f"- themes: `{payload['summary']['theme_counts']}`",
        f"- evidence modes: `{payload['summary']['evidence_mode_counts']}`",
        "",
        "## Queue",
        "",
    ]

    for item in payload["queue"]:
        lines.extend(
            [
                f"### {item['queue_id']}",
                f"- theme: `{item['theme']}`",
                f"- queue score: `{item['queue_score']}`",
                f"- review priority: `{item['review_priority']}`",
                f"- evidence mode: `{item['recommended_evidence_mode']}`",
                f"- reasons: `{', '.join(item['queue_reason'])}`",
                f"- clue types: `{', '.join(item['clue_types'])}`",
                f"- cashtags: `{', '.join(item['cashtags'][:10])}`",
                f"- external urls: `{', '.join(item['external_urls'][:5])}`",
                "",
                item["text_excerpt"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_queue(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


def write_grounding_surface(path: Path, markdown: str) -> None:
    path.write_text(markdown)


def _count_by(items: list[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        key = str(item[field])
        counts[key] = counts.get(key, 0) + 1
    return counts
