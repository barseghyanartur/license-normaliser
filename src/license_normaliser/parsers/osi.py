"""OSI parser - loads osi.json from package data."""

import json
from pathlib import Path
from typing import Any

from .base import BaseParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("OSIParser",)


class OSIParser(BaseParser):
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
