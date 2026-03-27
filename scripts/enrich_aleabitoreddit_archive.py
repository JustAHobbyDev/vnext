from __future__ import annotations

from pathlib import Path

from vnext.archive.enrichment import enrich_archive, load_archive, write_json


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "research" / "analysis" / "aleabitoreddit-daily-archive-v1.json"
    enriched_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-archive-enriched-v1.json"
    )
    link_graph_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-link-graph-v1.json"
    )

    raw_archive = load_archive(input_path)
    enriched_archive, link_graph = enrich_archive(raw_archive)
    write_json(enriched_path, enriched_archive)
    write_json(link_graph_path, link_graph)

    print(enriched_path)
    print(link_graph_path)


if __name__ == "__main__":
    main()
