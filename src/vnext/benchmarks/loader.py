from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from vnext.benchmarks.errors import (
    ArtifactHashMismatchError,
    BrokenLineageError,
    InvalidArtifactPathError,
    InvalidClueInputError,
    LineageCycleError,
    MissingArtifactError,
    SyntheticEvidenceRejectedError,
)
from vnext.clues.models import Clue
from vnext.evidence.models import EvidenceArtifact


@dataclass(frozen=True, slots=True)
class LoadedCase:
    case_id: str
    artifacts: dict[str, EvidenceArtifact]
    clues: tuple[Clue, ...]


def load_case_inputs(case_dir: Path) -> LoadedCase:
    case_dir = case_dir.resolve()
    artifacts_payload = _read_json(case_dir / "artifacts.json")
    clues_payload = _read_json(case_dir / "clues.json")
    case_id = artifacts_payload["case_id"]
    if clues_payload["case_id"] != case_id:
        raise InvalidClueInputError("artifacts.json and clues.json case_id must match")
    artifacts = load_artifacts(case_dir, artifacts_payload)
    clues = load_clues(case_dir, clues_payload, artifacts)
    return LoadedCase(case_id=case_id, artifacts=artifacts, clues=clues)


def load_artifacts(
    case_dir: Path, payload: dict[str, object] | None = None
) -> dict[str, EvidenceArtifact]:
    data = payload or _read_json(case_dir / "artifacts.json")
    artifacts: dict[str, EvidenceArtifact] = {}
    for raw_artifact in data["artifacts"]:
        artifact = EvidenceArtifact(
            artifact_id=raw_artifact["artifact_id"],
            artifact_kind=raw_artifact["artifact_kind"],
            source_class=raw_artifact["source_class"],
            source_url=raw_artifact.get("source_url"),
            captured_at=datetime.fromisoformat(raw_artifact["captured_at"]),
            local_path=raw_artifact["local_path"],
            sha256=raw_artifact["sha256"],
            is_real_world=raw_artifact["is_real_world"],
            parent_artifact_ids=tuple(raw_artifact.get("parent_artifact_ids", [])),
            verification_status=raw_artifact.get("verification_status", "unverified"),
            content_excerpt=raw_artifact["content_excerpt"],
            metadata=raw_artifact.get("metadata", {}),
        )
        if artifact.artifact_id in artifacts:
            raise InvalidClueInputError(f"duplicate artifact_id: {artifact.artifact_id}")
        _validate_artifact_file(case_dir, artifact)
        artifacts[artifact.artifact_id] = artifact

    for artifact_id in artifacts:
        _validate_lineage(artifact_id, artifacts, seen=())

    return artifacts


def load_clues(
    case_dir: Path,
    payload: dict[str, object] | None = None,
    artifacts: dict[str, EvidenceArtifact] | None = None,
) -> tuple[Clue, ...]:
    data = payload or _read_json(case_dir / "clues.json")
    artifact_index = artifacts or load_artifacts(case_dir)
    clues: list[Clue] = []
    for raw_clue in data["clues"]:
        clue = Clue(
            clue_id=raw_clue["clue_id"],
            clue_type=raw_clue["clue_type"],
            observed_at=datetime.fromisoformat(raw_clue["observed_at"]),
            source_class=raw_clue["source_class"],
            source_url=raw_clue["source_url"],
            text_span=raw_clue["text_span"],
            theme_hint=raw_clue["theme_hint"],
            evidence_confidence=raw_clue["evidence_confidence"],
            evidence_artifact_ids=tuple(raw_clue.get("evidence_artifact_ids", [])),
        )
        _validate_clue(clue, artifact_index)
        clues.append(clue)
    return tuple(clues)


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise MissingArtifactError(f"missing required input file: {path}")
    return json.loads(path.read_text())


def _compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_artifact_file(case_dir: Path, artifact: EvidenceArtifact) -> Path:
    artifact_path = (case_dir / artifact.local_path).resolve()
    if not artifact_path.is_file():
        raise MissingArtifactError(f"artifact file not found: {artifact.local_path}")
    if not _is_relative_to(artifact_path, case_dir):
        raise InvalidArtifactPathError(
            f"artifact path escapes case directory: {artifact.local_path}"
        )
    if "tests" in artifact_path.parts:
        raise InvalidArtifactPathError(f"artifact path points into tests: {artifact.local_path}")
    actual_sha = _compute_sha256(artifact_path)
    if actual_sha != artifact.sha256:
        raise ArtifactHashMismatchError(
            f"artifact hash mismatch for {artifact.artifact_id}: {actual_sha} != {artifact.sha256}"
        )
    return artifact_path


def _validate_clue(clue: Clue, artifacts: dict[str, EvidenceArtifact]) -> None:
    if not clue.has_evidence_refs():
        raise InvalidClueInputError(f"clue must reference at least one artifact: {clue.clue_id}")
    for artifact_id in clue.evidence_artifact_ids:
        if artifact_id not in artifacts:
            raise MissingArtifactError(
                f"clue references unknown artifact {artifact_id}: {clue.clue_id}"
            )
        if not _validate_lineage(artifact_id, artifacts, seen=()):
            raise SyntheticEvidenceRejectedError(
                f"artifact lineage for {artifact_id} does not resolve to a trust anchor"
            )


def _validate_lineage(
    artifact_id: str, artifacts: dict[str, EvidenceArtifact], seen: tuple[str, ...]
) -> bool:
    if artifact_id in seen:
        raise LineageCycleError(f"artifact lineage cycle detected at {artifact_id}")
    artifact = artifacts.get(artifact_id)
    if artifact is None:
        raise BrokenLineageError(f"unresolved artifact in lineage: {artifact_id}")
    if artifact.is_trust_anchor():
        return True
    if not artifact.is_derived():
        raise SyntheticEvidenceRejectedError(
            f"artifact {artifact_id} is not a trust anchor and not an allowed derived artifact"
        )
    if artifact.verification_status != "verified_against_parent":
        raise SyntheticEvidenceRejectedError(
            f"artifact {artifact_id} is not verified against its parent lineage"
        )
    if not artifact.parent_artifact_ids:
        raise BrokenLineageError(f"artifact {artifact_id} has no parents")
    return any(
        _validate_lineage(parent_id, artifacts, seen + (artifact_id,))
        for parent_id in artifact.parent_artifact_ids
    )


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
