from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from urllib.parse import urlparse


TRUST_ANCHOR_KINDS = {
    "primary_filing",
    "primary_press_release",
    "primary_transcript",
    "primary_web_capture",
}
DERIVED_KINDS = {"derived_extract", "derived_analysis", "normalized_record"}
KNOWN_ARTIFACT_KINDS = TRUST_ANCHOR_KINDS | DERIVED_KINDS
VERIFICATION_STATUSES = {"root", "verified_against_parent", "unverified"}


@dataclass(frozen=True, slots=True)
class EvidenceArtifact:
    artifact_id: str
    artifact_kind: str
    source_class: str
    source_url: str | None
    captured_at: datetime
    local_path: str
    sha256: str
    is_real_world: bool
    parent_artifact_ids: tuple[str, ...] = ()
    verification_status: str = "unverified"
    content_excerpt: str = ""
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.artifact_id:
            raise ValueError("artifact_id is required")
        if self.artifact_kind not in KNOWN_ARTIFACT_KINDS:
            raise ValueError(f"artifact_kind must be one of {sorted(KNOWN_ARTIFACT_KINDS)}")
        if self.verification_status not in VERIFICATION_STATUSES:
            raise ValueError(
                f"verification_status must be one of {sorted(VERIFICATION_STATUSES)}"
            )
        if len(self.sha256) != 64 or any(ch not in "0123456789abcdef" for ch in self.sha256):
            raise ValueError("sha256 must be a 64-character lowercase hex digest")
        if not self.local_path.strip():
            raise ValueError("local_path is required")
        if not self.content_excerpt.strip():
            raise ValueError("content_excerpt is required")

        if self.is_trust_anchor():
            if not self.is_real_world:
                raise ValueError("trust anchors must be marked is_real_world=True")
            if self.parent_artifact_ids:
                raise ValueError("trust anchors must not declare parents")
            if self.verification_status != "root":
                raise ValueError("trust anchors must use verification_status='root'")
            self._validate_source_url(required=True)
        elif self.is_derived():
            if not self.parent_artifact_ids:
                raise ValueError("derived artifacts must declare at least one parent")
            if self.verification_status == "root":
                raise ValueError("derived artifacts cannot use verification_status='root'")
            if self.verification_status != "verified_against_parent":
                raise ValueError(
                    "derived artifacts must use verification_status='verified_against_parent'"
                )
            if self.source_url is not None:
                self._validate_source_url(required=False)

    def _validate_source_url(self, required: bool) -> None:
        if self.source_url is None:
            if required:
                raise ValueError("source_url is required")
            return
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute http(s) URL")

    def is_trust_anchor(self) -> bool:
        return self.artifact_kind in TRUST_ANCHOR_KINDS

    def is_derived(self) -> bool:
        return self.artifact_kind in DERIVED_KINDS

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["captured_at"] = self.captured_at.isoformat()
        payload["parent_artifact_ids"] = list(self.parent_artifact_ids)
        return payload
