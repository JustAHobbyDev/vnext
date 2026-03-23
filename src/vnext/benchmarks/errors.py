class BenchmarkInputError(Exception):
    """Base error for strict case-input loading failures."""


class MissingArtifactError(BenchmarkInputError):
    """Raised when a referenced artifact does not exist."""


class ArtifactHashMismatchError(BenchmarkInputError):
    """Raised when a mirrored artifact hash does not match its manifest."""


class SyntheticEvidenceRejectedError(BenchmarkInputError):
    """Raised when artifact lineage does not resolve to a trust anchor."""


class BrokenLineageError(BenchmarkInputError):
    """Raised when a derived artifact references an unresolved parent chain."""


class LineageCycleError(BenchmarkInputError):
    """Raised when artifact lineage contains a cycle."""


class InvalidClueInputError(BenchmarkInputError):
    """Raised when a clue input is structurally invalid."""


class InvalidArtifactPathError(BenchmarkInputError):
    """Raised when an artifact points outside allowed local roots."""
