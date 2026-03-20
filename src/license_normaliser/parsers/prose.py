"""Prose pattern parser - loads prose_patterns.json and compiles regex patterns."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .base import BaseParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("ProseParser",)

_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = []


class ProseParser(BaseParser):
    url = None
    local_path = "data/prose/prose_patterns.json"
    is_registry_entry = False

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / "data" / "prose" / "prose_patterns.json"
        data: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        global _COMPILED_PATTERNS
        _COMPILED_PATTERNS = []
        results: list[tuple[str, dict[str, Any]]] = []
        for entry in data:
            pattern_str = entry.get("pattern", "")
            version_key = entry.get("version_key", "")
            name_key = entry.get("name_key", "")
            family_key = entry.get("family_key", "")
            if pattern_str and version_key:
                compiled = re.compile(pattern_str, re.IGNORECASE)
                _COMPILED_PATTERNS.append((compiled, version_key))
                results.append(
                    (
                        pattern_str,
                        {
                            "pattern": compiled,
                            "version_key": version_key,
                            "name_key": name_key,
                            "family_key": family_key,
                        },
                    )
                )
        return results


def get_prose_patterns() -> list[tuple[re.Pattern[str], str]]:
    """Return the compiled prose patterns for use in resolution."""
    return _COMPILED_PATTERNS
