from __future__ import annotations

from collections import Counter
from datetime import datetime, UTC
from pathlib import Path
from urllib.parse import urlparse
import json
import re


X_DOMAINS = {"x.com", "twitter.com", "www.x.com", "www.twitter.com"}
MEDIA_PATTERNS = {
    "x_post_photo": re.compile(r"^/(?:[^/]+)/status/\d+/photo/\d+$", re.I),
    "pic_twitter": re.compile(r"^https?://pic\.twitter\.com/", re.I),
    "direct_image": re.compile(r"^https?://.+\.(?:png|jpe?g|gif|webp)(?:\?.*)?$", re.I),
    "pbs_twitter": re.compile(r"^https?://pbs\.twimg\.com/", re.I),
}


def load_archive(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def enrich_archive(raw_archive: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    posts = raw_archive["posts"]
    enriched_posts = [enrich_post(post) for post in posts]
    link_graph = build_link_graph(enriched_posts)

    top_level = {
        key: value for key, value in raw_archive.items() if key != "posts"
    }
    summary = {
        "post_count": len(enriched_posts),
        "posts_with_urls": sum(1 for post in enriched_posts if post["urls"]),
        "posts_with_mentions": sum(1 for post in enriched_posts if post["mentioned_users"]),
        "posts_with_cashtags": sum(1 for post in enriched_posts if post["cashtags"]),
        "posts_with_probable_media_urls": sum(
            1 for post in enriched_posts if post["probable_media_urls"]
        ),
        "url_classification_counts": dict(
            Counter(
                record["classification"]
                for post in enriched_posts
                for record in post["url_records"]
            )
        ),
        "referenced_tweet_type_counts": dict(
            Counter(
                reference["type"]
                for post in enriched_posts
                for reference in post["referenced_tweets"]
            )
        ),
    }
    generated_at = datetime.now(UTC).isoformat()
    return (
        {
            "schema_version": "v1",
            "generated_at": generated_at,
            "source_archive_metadata": top_level,
            "summary": summary,
            "posts": enriched_posts,
        },
        link_graph | {"generated_at": generated_at},
    )


def enrich_post(post: dict[str, object]) -> dict[str, object]:
    entities = post.get("entities") or {}
    urls = _dedupe_preserve_order(entities.get("urls") or [])
    mentions = _dedupe_preserve_order(entities.get("mentions") or [])
    cashtags = _dedupe_preserve_order((tag.upper() for tag in entities.get("cashtags") or []))
    hashtags = _dedupe_preserve_order(entities.get("hashtags") or [])
    url_records = [classify_url(url) for url in urls]
    reference_index = {
        reference["type"]: reference["id"]
        for reference in (post.get("referenced_tweets") or [])
        if isinstance(reference, dict) and "type" in reference and "id" in reference
    }

    external_urls = [
        record["url"]
        for record in url_records
        if record["classification"] == "external_link"
    ]
    probable_media_urls = [
        record["url"] for record in url_records if record["is_probable_media"]
    ]
    unresolved_media_urls = probable_media_urls.copy()

    return {
        **post,
        "post_id": post["id"],
        "urls": urls,
        "expanded_urls": urls,
        "domains": _dedupe_preserve_order(
            record["domain"] for record in url_records if record["domain"]
        ),
        "url_records": url_records,
        "probable_media_urls": probable_media_urls,
        "resolved_image_urls": [],
        "unresolved_media_urls": unresolved_media_urls,
        "external_urls": external_urls,
        "mentioned_users": mentions,
        "cashtags": cashtags,
        "hashtags": hashtags,
        "reply_to_post_id": reference_index.get("replied_to"),
        "quoted_post_id": reference_index.get("quoted"),
        "retweeted_post_id": reference_index.get("retweeted"),
        "conversation_root_id": post.get("conversation_id"),
        "external_link_count": len(external_urls),
        "mention_count": len(mentions),
        "cashtag_count": len(cashtags),
        "attachment_ids": [],
        "attachments": [],
    }


def build_link_graph(enriched_posts: list[dict[str, object]]) -> dict[str, object]:
    node_index: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []

    def add_node(node_id: str, node_type: str, value: str) -> None:
        node_index.setdefault(
            node_id,
            {"node_id": node_id, "node_type": node_type, "value": value},
        )

    def add_edge(
        source_id: str,
        source_type: str,
        target_id: str,
        target_type: str,
        edge_type: str,
    ) -> None:
        edges.append(
            {
                "source_id": source_id,
                "source_type": source_type,
                "target_id": target_id,
                "target_type": target_type,
                "edge_type": edge_type,
            }
        )

    for post in enriched_posts:
        post_node_id = f"post:{post['post_id']}"
        add_node(post_node_id, "post", post["post_id"])

        for domain in post["domains"]:
            domain_node_id = f"domain:{domain}"
            add_node(domain_node_id, "domain", domain)
            add_edge(post_node_id, "post", domain_node_id, "domain", "links_to_domain")

        for url_record in post["url_records"]:
            url = url_record["url"]
            url_node_id = f"url:{url}"
            add_node(url_node_id, "url", url)
            add_edge(post_node_id, "post", url_node_id, "url", "links_to_url")
            if url_record["classification"] in {"x_post", "x_post_photo"}:
                target_post_id = _extract_status_id(url)
                if target_post_id:
                    target_node_id = f"post:{target_post_id}"
                    add_node(target_node_id, "post", target_post_id)
                    add_edge(
                        post_node_id,
                        "post",
                        target_node_id,
                        "post",
                        "links_to_post",
                    )

        for user in post["mentioned_users"]:
            user_node_id = f"user:{user.lower()}"
            add_node(user_node_id, "user", user.lower())
            add_edge(post_node_id, "post", user_node_id, "user", "mentions_user")

        for cashtag in post["cashtags"]:
            cashtag_node_id = f"cashtag:{cashtag}"
            add_node(cashtag_node_id, "cashtag", cashtag)
            add_edge(post_node_id, "post", cashtag_node_id, "cashtag", "mentions_cashtag")

        for hashtag in post["hashtags"]:
            hashtag_node_id = f"hashtag:{hashtag}"
            add_node(hashtag_node_id, "hashtag", hashtag)
            add_edge(post_node_id, "post", hashtag_node_id, "hashtag", "mentions_hashtag")

        for reference in post["referenced_tweets"]:
            if not isinstance(reference, dict):
                continue
            target_post_id = reference.get("id")
            reference_type = reference.get("type")
            if not target_post_id or not reference_type:
                continue
            target_node_id = f"post:{target_post_id}"
            add_node(target_node_id, "post", target_post_id)
            add_edge(
                post_node_id,
                "post",
                target_node_id,
                "post",
                f"references_post_{reference_type}",
            )

    edge_counts = Counter(edge["edge_type"] for edge in edges)
    node_counts = Counter(node["node_type"] for node in node_index.values())
    return {
        "schema_version": "v1",
        "summary": {
            "node_counts": dict(node_counts),
            "edge_counts": dict(edge_counts),
            "total_nodes": len(node_index),
            "total_edges": len(edges),
        },
        "nodes": sorted(node_index.values(), key=lambda node: (node["node_type"], node["value"])),
        "edges": edges,
    }


def classify_url(url: str) -> dict[str, object]:
    normalized_url = url.strip()
    domain = _normalize_domain(normalized_url)
    parsed = urlparse(normalized_url)
    classification = "external_link"
    is_probable_media = False

    if MEDIA_PATTERNS["pic_twitter"].search(normalized_url):
        classification = "short_media_link"
        is_probable_media = True
    elif MEDIA_PATTERNS["pbs_twitter"].search(normalized_url) or MEDIA_PATTERNS["direct_image"].search(
        normalized_url
    ):
        classification = "direct_image"
        is_probable_media = True
    elif domain in X_DOMAINS and MEDIA_PATTERNS["x_post_photo"].search(parsed.path):
        classification = "x_post_photo"
        is_probable_media = True
    elif domain in X_DOMAINS and _extract_status_id(normalized_url):
        classification = "x_post"

    return {
        "url": normalized_url,
        "domain": domain,
        "classification": classification,
        "is_probable_media": is_probable_media,
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


def _normalize_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _extract_status_id(url: str) -> str | None:
    parsed = urlparse(url)
    match = re.search(r"/status/(\d+)", parsed.path)
    if match:
        return match.group(1)
    return None


def _dedupe_preserve_order(values) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value is None:
            continue
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
    return output
