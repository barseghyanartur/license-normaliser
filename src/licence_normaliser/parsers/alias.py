"""Alias parser - loads aliases.json with rich metadata for aliases/family overrides.

Each entry may carry an optional ``aliases`` list of extra lookup keys that all
resolve to the same ``version_key``.  This lets data authors enumerate explicit
variants (e.g. hyphen vs space forms) without any auto-generation magic::

    "cc by-nc": {
        "version_key": "cc-by-nc",
        "name_key": "cc-by-nc",
        "family_key": "cc",
        "aliases": ["cc-by-nc", "cc by nc", "cc-by nc"]
    }

All keys in ``aliases`` inherit the same ``version_key``, ``name_key``, and
``family_key`` as the primary entry.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from licence_normaliser.plugins import (
    AliasPlugin,
    BasePlugin,
    FamilyPlugin,
    NamePlugin,
    ProsePlugin,
    URLPlugin,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("AliasParser",)


def _iter_entries(
    data: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    """Yield (key, meta) pairs, expanding ``aliases`` sub-keys.

    For every primary entry that has an ``"aliases"`` list, each alias key is
    emitted as an additional entry with the same metadata dict (minus the
    ``aliases`` field itself, to keep things tidy).
    """
    results: list[tuple[str, dict[str, Any]]] = []
    for primary_key, meta in data.items():
        if primary_key.startswith("_"):
            continue
        if not isinstance(meta, dict):
            continue
        version_key = meta.get("version_key", "")
        if not version_key:
            continue
        results.append((primary_key, meta))

        # Expand explicit alias variants
        for extra_key in meta.get("aliases", []):
            if not isinstance(extra_key, str) or not extra_key:
                continue
            if extra_key == primary_key:
                continue  # already emitted
            # Build a slim copy without the aliases list to avoid recursion
            slim_meta = {k: v for k, v in meta.items() if k != "aliases"}
            results.append((extra_key, slim_meta))

    return results


class AliasParser(
    BasePlugin, AliasPlugin, FamilyPlugin, NamePlugin, URLPlugin, ProsePlugin
):
    url = None
    local_path = "data/aliases/aliases.json"

    def _load_data(self) -> dict[str, Any]:
        path = Path(__file__).parent.parent / self.local_path
        return json.loads(path.read_text(encoding="utf-8"))

    def load_urls(self) -> dict[str, str]:
        """Load URLs from aliases.json entries that have a urls array."""
        result: dict[str, str] = {}
        data = self._load_data()
        for meta in data.values():
            if not isinstance(meta, dict):
                continue
            version_key = meta.get("version_key", "")
            if not version_key:
                continue
            urls = meta.get("urls", [])
            if isinstance(urls, list):
                for url in urls:
                    if isinstance(url, str):
                        normalized = url.strip().lower().rstrip("/")
                        if normalized.startswith("http://"):
                            normalized = "https://" + normalized[7:]
                        result[normalized] = version_key
        return result

    def load_urls_with_lines(self) -> dict[str, tuple[str, int]]:
        """Load URLs with their source line numbers."""
        path = Path(__file__).parent.parent / self.local_path
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(content)
        lines = content.splitlines()
        result: dict[str, tuple[str, int]] = {}

        for primary_key, meta in data.items():
            if primary_key.startswith("_"):
                continue
            if not isinstance(meta, dict):
                continue
            version_key = meta.get("version_key", "")
            if not version_key:
                continue

            primary_line = 1
            for i, line in enumerate(lines, start=1):
                if f'"{primary_key}"' in line:
                    primary_line = i
                    break

            urls = meta.get("urls", [])
            if isinstance(urls, list):
                for url in urls:
                    if isinstance(url, str):
                        normalized = url.strip().lower().rstrip("/")
                        if normalized.startswith("http://"):
                            normalized = "https://" + normalized[7:]
                        result[normalized] = (version_key, primary_line)

        return result

    def load_aliases(self) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for alias_key, meta in _iter_entries(self._load_data()):
            version_key = meta.get("version_key", "")
            if version_key:
                aliases[alias_key] = version_key
        return aliases

    def load_aliases_with_lines(
        self,
    ) -> dict[str, tuple[str, int]]:
        """Load aliases with their source line numbers.

        Extra keys from ``aliases`` lists are reported at the line of their
        primary entry (best approximation without per-alias line tracking).

        Returns:
            dict mapping alias_key -> (version_key, line_number)
        """
        path = Path(__file__).parent.parent / self.local_path
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(content)
        lines = content.splitlines()
        result: dict[str, tuple[str, int]] = {}

        for primary_key, meta in data.items():
            if primary_key.startswith("_"):
                continue
            if not isinstance(meta, dict):
                continue
            version_key = meta.get("version_key", "")
            if not version_key:
                continue

            # Find line of the primary key
            primary_line = 1
            for i, line in enumerate(lines, start=1):
                if f'"{primary_key}"' in line:
                    primary_line = i
                    break

            result[primary_key] = (version_key, primary_line)

            for extra_key in meta.get("aliases", []):
                if not isinstance(extra_key, str) or not extra_key:
                    continue
                if extra_key == primary_key:
                    continue
                result[extra_key] = (version_key, primary_line)

        return result

    def load_families(self) -> dict[str, str]:
        data = self._load_data()
        overrides: dict[str, str] = {}
        for meta in data.values():
            if not isinstance(meta, dict):
                continue
            vk = meta.get("version_key", "")
            fk = meta.get("family_key", "")
            if vk and fk:
                overrides[vk] = fk
        return overrides

    def load_names(self) -> dict[str, str]:
        data = self._load_data()
        names: dict[str, str] = {}
        for meta in data.values():
            if not isinstance(meta, dict):
                continue
            vk = meta.get("version_key", "")
            nk = meta.get("name_key", "")
            if vk and nk:
                names[vk] = nk
        return names

    def load_prose(self) -> list[tuple[re.Pattern[str], str]]:
        """Load regex patterns from aliases.json entries that have a patterns array."""
        result: list[tuple[re.Pattern[str], str]] = []
        data = self._load_data()
        for meta in data.values():
            if not isinstance(meta, dict):
                continue
            version_key = meta.get("version_key", "")
            if not version_key:
                continue
            patterns = meta.get("patterns", [])
            if isinstance(patterns, list):
                for pattern_str in patterns:
                    if isinstance(pattern_str, str) and pattern_str:
                        try:
                            compiled = re.compile(pattern_str, re.IGNORECASE)
                            result.append((compiled, version_key))
                        except re.error as e:
                            raise ValueError(
                                f"Invalid prose pattern in aliases.json: "
                                f"pattern={pattern_str!r}, version_key={version_key!r}"
                            ) from e
        return result
