from __future__ import annotations

from pathlib import Path

from vnext.archive.community_prospecting import (
    extract_community_leads,
    load_source_sweep,
    write_payload,
    write_review_surface,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "research" / "analysis" / "2026-03-25-grok-lite-source-sweep-v1.json"
    output_path = project_root / "research" / "analysis" / "2026-03-25-lite-community-leads-v1.json"
    review_path = project_root / "research" / "analysis" / "2026-03-25-lite-community-leads-v1.md"

    source_sweep = load_source_sweep(input_path)
    payload, review_surface = extract_community_leads(source_sweep)
    write_payload(output_path, payload)
    write_review_surface(review_path, review_surface)

    print(output_path)
    print(review_path)


if __name__ == "__main__":
    main()
