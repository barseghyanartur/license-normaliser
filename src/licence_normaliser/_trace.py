"""Licence trace and explanation support."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenceTrace",
    "LicenceTraceStage",
)


@dataclass
class LicenceTraceStage:
    """Single stage in the licence resolution pipeline."""

    stage: str
    input: str
    output: str
    matched: bool
    source_line: int | None = None
    source_file: str | None = None


@dataclass
class LicenceTrace:
    """Complete trace of licence resolution pipeline."""

    raw_input: str
    cleaned_input: str
    stages: list[LicenceTraceStage] = field(default_factory=list)
    version_key: str = ""
    name_key: str = ""
    family_key: str = ""

    def __str__(self) -> str:
        lines = [f"Input: {self.raw_input!r} → {self.cleaned_input!r}"]
        for s in self.stages:
            status = "✓" if s.matched else "-"
            source_info = ""
            if s.source_line is not None:
                source_info = f" (line {s.source_line}"
                if s.source_file:
                    source_info += f" in {s.source_file}"
                source_info += ")"
            lines.append(
                f"  [{status}] {s.stage}: {s.input!r} → {s.output!r}{source_info}"
            )
        lines.append("")
        lines.append("Result:")
        lines.append(f"  version_key: {self.version_key!r}")
        lines.append(f"  name_key: {self.name_key!r}")
        lines.append(f"  family_key: {self.family_key!r}")
        return "\n".join(lines)


def _should_trace() -> bool:
    """Check if tracing is enabled via environment variable."""
    return os.environ.get("ENABLE_LICENCE_NORMALISER_TRACE", "").lower() in (
        "1",
        "true",
        "yes",
    )
