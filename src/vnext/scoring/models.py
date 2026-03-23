from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class NodeScore:
    node_id: str
    constraint_score: float
    sensitivity_score: float
    neglect_score: float
    expression_score: float
    composite_score: float
    score_notes: str

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        for field_name in (
            "constraint_score",
            "sensitivity_score",
            "neglect_score",
            "expression_score",
            "composite_score",
        ):
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0")
        if not self.score_notes.strip():
            raise ValueError("score_notes is required")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
