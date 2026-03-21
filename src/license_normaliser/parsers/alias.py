"""Alias parser - loads aliases.json with rich metadata for aliases/family overrides."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import BaseParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("AliasParser",)


class AliasParser(BaseParser):
    url = None
    local_path = "data/aliases/aliases.json"
    is_registry_entry = False

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / self.local_path
        data: dict[str, dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        for alias_key, meta in data.items():
            if alias_key.startswith("_"):
                continue
            if not isinstance(meta, dict):
                continue
            version_key = meta.get("version_key", "")
            if version_key:
                results.append((alias_key, meta))
        return results

    @staticmethod
    def get_aliases() -> dict[str, str]:
        """Return the full aliases dict: alias_key -> version_key."""
        path = Path(__file__).parent.parent / AliasParser.local_path
        data: dict[str, dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        aliases: dict[str, str] = {}
        for alias_key, meta in data.items():
            if alias_key.startswith("_"):
                continue
            if not isinstance(meta, dict):
                continue
            version_key = meta.get("version_key", "")
            if version_key:
                aliases[alias_key] = version_key
        return aliases

    @staticmethod
    def get_family_overrides() -> dict[str, str]:
        """Return version_key -> family_key overrides from aliases."""
        path = Path(__file__).parent.parent / AliasParser.local_path
        data: dict[str, dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
        overrides: dict[str, str] = {}
        for meta in data.values():
            if not isinstance(meta, dict):
                continue
            vk = meta.get("version_key", "")
            fk = meta.get("family_key", "")
            if vk and fk:
                overrides[vk] = fk
        return overrides
