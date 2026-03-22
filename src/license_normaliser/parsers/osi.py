"""OSI parser - loads osi.json from package data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from license_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("OSIParser",)


class OSIParser(BasePlugin, RegistryPlugin, URLPlugin):
    id = "osi"
    url = "https://opensource.org/api/license"
    local_path = "data/osi/osi.json"

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        if not isinstance(data, list):
            return results
        for entry in data:
            if not isinstance(entry, dict):
                continue
            key = entry.get("id", "")
            if not key:
                continue
            links = entry.get("_links", {})
            html_link = links.get("html", {})
            url = html_link.get("href", "") if isinstance(html_link, dict) else ""
            results.append(
                (
                    key,
                    {
                        "url": url,
                        "name": entry.get("name", ""),
                        "spdx_id": entry.get("spdx_id", ""),
                    },
                )
            )
        return results

    def load_registry(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        if not isinstance(data, list):
            return result
        for entry in data:
            if not isinstance(entry, dict):
                continue
            key = entry.get("id", "").strip()
            if key:
                result[key.lower()] = key.lower()
        return result

    def load_urls(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        if not isinstance(data, list):
            return result
        for entry in data:
            if not isinstance(entry, dict):
                continue
            key = entry.get("id", "").strip()
            if not key:
                continue
            canonical = key.lower()
            links = entry.get("_links", {})
            html_link = links.get("html", {})
            raw_url = html_link.get("href", "") if isinstance(html_link, dict) else ""
            if not raw_url:
                continue
            clean = raw_url.strip().lower().rstrip("/")
            if clean.startswith("http://"):
                clean = "https://" + clean[7:]
            result[clean] = canonical
        return result
