from __future__ import annotations

from pathlib import Path

from vnext.archive.clue_extraction import (
    extract_clue_candidates,
    load_enriched_archive,
    write_candidates,
    write_review_surface,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-archive-enriched-v1.json"
    )
    candidates_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-clue-candidates-v1.json"
    )
    review_surface_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-discovery-review-surface-v1.md"
    )

    enriched_archive = load_enriched_archive(input_path)
    candidates_payload, review_surface = extract_clue_candidates(enriched_archive)
    write_candidates(candidates_path, candidates_payload)
    write_review_surface(review_surface_path, review_surface)

    print(candidates_path)
    print(review_surface_path)


if __name__ == "__main__":
    main()
