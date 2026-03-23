import json
from pathlib import Path

import pytest

from vnext.benchmarks.errors import (
    ArtifactHashMismatchError,
    BrokenLineageError,
    InvalidArtifactPathError,
    InvalidClueInputError,
    LineageCycleError,
    MissingArtifactError,
    SyntheticEvidenceRejectedError,
)
from vnext.benchmarks.loader import load_case_inputs


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2))


def _base_case(tmp_path: Path) -> Path:
    case_dir = tmp_path / "photonics"
    raw_dir = case_dir / "raw"
    raw_dir.mkdir(parents=True)
    raw_file = raw_dir / "artifact.txt"
    raw_file.write_text("real source evidence")
    digest = __import__("hashlib").sha256(raw_file.read_bytes()).hexdigest()
    _write_json(
        case_dir / "artifacts.json",
        {
            "case_id": "photonics",
            "artifacts": [
                {
                    "artifact_id": "real-artifact",
                    "artifact_kind": "primary_press_release",
                    "source_class": "company_ir",
                    "source_url": "https://example.com/evidence",
                    "captured_at": "2024-05-02T00:00:00-05:00",
                    "local_path": "raw/artifact.txt",
                    "sha256": digest,
                    "is_real_world": True,
                    "parent_artifact_ids": [],
                    "verification_status": "root",
                    "content_excerpt": "real source evidence",
                    "metadata": {},
                }
            ],
        },
    )
    _write_json(
        case_dir / "clues.json",
        {
            "case_id": "photonics",
            "clues": [
                {
                    "clue_id": "clue-1",
                    "clue_type": "earnings_commentary",
                    "observed_at": "2024-05-02T00:00:00-05:00",
                    "source_class": "company_ir",
                    "source_url": "https://example.com/evidence",
                    "text_span": "real source evidence",
                    "theme_hint": "photonics",
                    "evidence_confidence": 0.9,
                    "evidence_artifact_ids": ["real-artifact"],
                }
            ],
        },
    )
    return case_dir


def test_loader_accepts_valid_case(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    loaded = load_case_inputs(case_dir)

    assert loaded.case_id == "photonics"
    assert loaded.clues[0].evidence_artifact_ids == ("real-artifact",)


def test_loader_refuses_clue_without_artifact_refs(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    clues = json.loads((case_dir / "clues.json").read_text())
    clues["clues"][0]["evidence_artifact_ids"] = []
    _write_json(case_dir / "clues.json", clues)

    with pytest.raises(InvalidClueInputError):
        load_case_inputs(case_dir)


def test_loader_refuses_missing_artifact_file(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    (case_dir / "raw" / "artifact.txt").unlink()

    with pytest.raises(MissingArtifactError):
        load_case_inputs(case_dir)


def test_loader_refuses_sha_mismatch(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    artifacts = json.loads((case_dir / "artifacts.json").read_text())
    artifacts["artifacts"][0]["sha256"] = "0" * 64
    _write_json(case_dir / "artifacts.json", artifacts)

    with pytest.raises(ArtifactHashMismatchError):
        load_case_inputs(case_dir)


def test_loader_refuses_artifact_outside_case_root(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("real source evidence")
    artifacts = json.loads((case_dir / "artifacts.json").read_text())
    artifacts["artifacts"][0]["local_path"] = "../outside.txt"
    artifacts["artifacts"][0]["sha256"] = __import__("hashlib").sha256(
        outside.read_bytes()
    ).hexdigest()
    _write_json(case_dir / "artifacts.json", artifacts)

    with pytest.raises(InvalidArtifactPathError):
        load_case_inputs(case_dir)


def test_loader_refuses_broken_parent_chain(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    artifacts = json.loads((case_dir / "artifacts.json").read_text())
    artifacts["artifacts"][0] = {
        "artifact_id": "derived-artifact",
        "artifact_kind": "derived_analysis",
        "source_class": "analysis",
        "source_url": None,
        "captured_at": "2024-05-02T00:00:00-05:00",
        "local_path": "raw/artifact.txt",
        "sha256": artifacts["artifacts"][0]["sha256"],
        "is_real_world": False,
        "parent_artifact_ids": ["missing-parent"],
        "verification_status": "verified_against_parent",
        "content_excerpt": "derived note",
        "metadata": {}
    }
    clues = json.loads((case_dir / "clues.json").read_text())
    clues["clues"][0]["evidence_artifact_ids"] = ["derived-artifact"]
    _write_json(case_dir / "artifacts.json", artifacts)
    _write_json(case_dir / "clues.json", clues)

    with pytest.raises(BrokenLineageError):
        load_case_inputs(case_dir)


def test_loader_refuses_lineage_cycle(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    digest = json.loads((case_dir / "artifacts.json").read_text())["artifacts"][0]["sha256"]
    _write_json(
        case_dir / "artifacts.json",
        {
            "case_id": "photonics",
            "artifacts": [
                {
                    "artifact_id": "derived-a",
                    "artifact_kind": "derived_analysis",
                    "source_class": "analysis",
                    "source_url": None,
                    "captured_at": "2024-05-02T00:00:00-05:00",
                    "local_path": "raw/artifact.txt",
                    "sha256": digest,
                    "is_real_world": False,
                    "parent_artifact_ids": ["derived-b"],
                    "verification_status": "verified_against_parent",
                    "content_excerpt": "a",
                    "metadata": {}
                },
                {
                    "artifact_id": "derived-b",
                    "artifact_kind": "derived_analysis",
                    "source_class": "analysis",
                    "source_url": None,
                    "captured_at": "2024-05-02T00:00:00-05:00",
                    "local_path": "raw/artifact.txt",
                    "sha256": digest,
                    "is_real_world": False,
                    "parent_artifact_ids": ["derived-a"],
                    "verification_status": "verified_against_parent",
                    "content_excerpt": "b",
                    "metadata": {}
                }
            ]
        },
    )
    clues = json.loads((case_dir / "clues.json").read_text())
    clues["clues"][0]["evidence_artifact_ids"] = ["derived-a"]
    _write_json(case_dir / "clues.json", clues)

    with pytest.raises(LineageCycleError):
        load_case_inputs(case_dir)


def test_loader_accepts_verified_derived_artifact_with_real_parent(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    artifacts = json.loads((case_dir / "artifacts.json").read_text())
    artifacts["artifacts"].append(
        {
            "artifact_id": "derived-artifact",
            "artifact_kind": "derived_analysis",
            "source_class": "analysis",
            "source_url": None,
            "captured_at": "2024-05-02T00:00:00-05:00",
            "local_path": "raw/artifact.txt",
            "sha256": artifacts["artifacts"][0]["sha256"],
            "is_real_world": False,
            "parent_artifact_ids": ["real-artifact"],
            "verification_status": "verified_against_parent",
            "content_excerpt": "derived note",
            "metadata": {}
        }
    )
    clues = json.loads((case_dir / "clues.json").read_text())
    clues["clues"][0]["evidence_artifact_ids"] = ["derived-artifact"]
    _write_json(case_dir / "artifacts.json", artifacts)
    _write_json(case_dir / "clues.json", clues)

    loaded = load_case_inputs(case_dir)
    assert loaded.clues[0].evidence_artifact_ids == ("derived-artifact",)


def test_loader_refuses_unverified_derived_artifact(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    artifacts = json.loads((case_dir / "artifacts.json").read_text())
    artifacts["artifacts"].append(
        {
            "artifact_id": "derived-artifact",
            "artifact_kind": "derived_analysis",
            "source_class": "analysis",
            "source_url": None,
            "captured_at": "2024-05-02T00:00:00-05:00",
            "local_path": "raw/artifact.txt",
            "sha256": artifacts["artifacts"][0]["sha256"],
            "is_real_world": False,
            "parent_artifact_ids": ["real-artifact"],
            "verification_status": "unverified",
            "content_excerpt": "derived note",
            "metadata": {}
        }
    )
    clues = json.loads((case_dir / "clues.json").read_text())
    clues["clues"][0]["evidence_artifact_ids"] = ["derived-artifact"]
    _write_json(case_dir / "artifacts.json", artifacts)
    _write_json(case_dir / "clues.json", clues)

    with pytest.raises(ValueError):
        load_case_inputs(case_dir)


def test_loader_refuses_invalid_trust_anchor_url(tmp_path: Path) -> None:
    case_dir = _base_case(tmp_path)
    artifacts = json.loads((case_dir / "artifacts.json").read_text())
    artifacts["artifacts"][0]["source_url"] = "not-a-url"
    _write_json(case_dir / "artifacts.json", artifacts)

    with pytest.raises(ValueError):
        load_case_inputs(case_dir)
