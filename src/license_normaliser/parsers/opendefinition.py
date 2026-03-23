"""OpenDefinition parser - loads opendefinition_licenses_all.json from package data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from license_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("OpenDefinitionParser",)


class OpenDefinitionParser(BasePlugin, RegistryPlugin, URLPlugin):
    id = "opendefinition"
    url = "https://licenses.opendefinition.org/licenses/groups/all.json"
    local_path = "data/opendefinition/opendefinition.json"

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            lid = entry.get("id", "")
            url = entry.get("url", "")
            results.append((lid, {"url": url, "title": entry.get("title", "")}))
        return results

    def load_registry(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            lid = entry.get("id", "")
            if lid:
                result[lid.lower().strip()] = lid.lower().strip()
        return result

    def load_urls(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            lid = entry.get("id", "")
            if not lid:
                continue
            canonical = lid.lower().strip()
            raw_url = entry.get("url", "")
            if not raw_url:
                continue
            clean = raw_url.strip().lower().rstrip("/")
            if clean.startswith("http://"):
                clean = "https://" + clean[7:]
            result[clean] = canonical
        return result
