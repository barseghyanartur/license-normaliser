"""SPDX parser - loads spdx-licenses.json from package data."""

from __future__ import annotations

import json
from pathlib import Path

from licence_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("SPDXParser",)


class SPDXParser(BasePlugin, RegistryPlugin, URLPlugin):
    id = "spdx"
    url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
    local_path = "data/spdx/spdx.json"

    def load_registry(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for entry in data.get("licenses", []):
            if not isinstance(entry, dict):
                continue
            lid = entry.get("licenseId", "")
            if lid:
                result[lid.lower().strip()] = lid.lower().strip()
        return result

    def load_registry_lines(self) -> dict[str, tuple[int, str]]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, tuple[int, str]] = {}
        source_file = "spdx.json"
        for idx, entry in enumerate(data.get("licenses", []), start=1):
            if not isinstance(entry, dict):
                continue
            lid = entry.get("licenseId", "")
            if lid:
                result[lid.lower().strip()] = (idx, source_file)
        return result

    def load_urls(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for entry in data.get("licenses", []):
            if not isinstance(entry, dict):
                continue
            lid = entry.get("licenseId", "")
            if not lid:
                continue
            canonical = lid.lower().strip()
            for raw_url in entry.get("seeAlso", []):
                if not raw_url:
                    continue
                clean = raw_url.strip().lower().rstrip("/")
                if clean.startswith("http://"):
                    clean = "https://" + clean[7:]
                result[clean] = canonical
        return result
