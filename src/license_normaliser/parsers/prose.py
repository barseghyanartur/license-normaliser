"""Prose pattern parser - loads prose_patterns.json and compiles regex patterns."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from license_normaliser.plugins import BasePlugin, ProsePlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("ProseParser",)

_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = []


class ProseParser(BasePlugin, ProsePlugin):
    is_registry_entry = False
    url = None
    local_path = "data/prose/prose_patterns.json"

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / self.local_path
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

    def load_prose(self) -> list[tuple[re.Pattern[str], str]]:
        global _COMPILED_PATTERNS
        _COMPILED_PATTERNS = []
        path = Path(__file__).parent.parent / self.local_path
        data: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        for entry in data:
            pattern_str = entry.get("pattern", "")
            version_key = entry.get("version_key", "")
            if pattern_str and version_key:
                compiled = re.compile(pattern_str, re.IGNORECASE)
                _COMPILED_PATTERNS.append((compiled, version_key))
        return _COMPILED_PATTERNS


def get_prose_patterns() -> list[tuple[re.Pattern[str], str]]:
    """Legacy helper: return the compiled prose patterns."""
    return _COMPILED_PATTERNS
