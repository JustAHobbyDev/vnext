from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class Clue:
    clue_id: str
    clue_type: str
    observed_at: datetime
    source_class: str
    source_url: str
    text_span: str
    theme_hint: str
    evidence_confidence: float
    evidence_artifact_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.clue_id:
            raise ValueError("clue_id is required")
        if not self.text_span.strip():
            raise ValueError("text_span is required")
        if not 0.0 <= self.evidence_confidence <= 1.0:
            raise ValueError("evidence_confidence must be between 0.0 and 1.0")

        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute http(s) URL")

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["observed_at"] = self.observed_at.isoformat()
        payload["evidence_artifact_ids"] = list(self.evidence_artifact_ids)
        return payload

    def has_evidence_refs(self) -> bool:
        return bool(self.evidence_artifact_ids)
