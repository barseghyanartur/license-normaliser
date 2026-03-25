"""Prose pattern parser - loads prose_patterns.json and compiles regex patterns."""

from __future__ import annotations

import json
import re
from pathlib import Path

from licence_normaliser.plugins import BasePlugin, ProsePlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("ProseParser",)

_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = []


class ProseParser(BasePlugin, ProsePlugin):
    url = None
    local_path = "data/prose/prose_patterns.json"

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

    def load_prose_with_lines(self) -> list[tuple[re.Pattern[str], str, int]]:
        """Load prose patterns with their source line numbers.

        Returns:
            list of (compiled_pattern, version_key, line_number)
        """
        path = Path(__file__).parent.parent / self.local_path
        content = path.read_text(encoding="utf-8")
        data: list[dict[str, str]] = json.loads(content)
        lines = content.splitlines()
        result: list[tuple[re.Pattern[str], str, int]] = []
        for entry in data:
            pattern_str = entry.get("pattern", "")
            version_key = entry.get("version_key", "")
            if pattern_str and version_key:
                compiled = re.compile(pattern_str, re.IGNORECASE)
                serialized = json.dumps(pattern_str)
                line_num = 1
                for i, line in enumerate(lines, start=1):
                    if '"pattern"' in line and serialized[:30] in line:
                        line_num = i
                        break
                result.append((compiled, version_key, line_num))
        return result
