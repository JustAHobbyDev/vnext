from __future__ import annotations

from pathlib import Path

from vnext.archive.grounding_queue import (
    build_grounding_queue,
    load_candidates,
    write_grounding_surface,
    write_queue,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-clue-candidates-v1.json"
    )
    queue_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-evidence-grounding-queue-v1.json"
    )
    surface_path = (
        project_root / "research" / "analysis" / "aleabitoreddit-evidence-grounding-review-surface-v1.md"
    )

    candidates = load_candidates(input_path)
    payload, markdown = build_grounding_queue(candidates)
    write_queue(queue_path, payload)
    write_grounding_surface(surface_path, markdown)

    print(queue_path)
    print(surface_path)


if __name__ == "__main__":
    main()
