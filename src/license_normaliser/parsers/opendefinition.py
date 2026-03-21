"""OpenDefinition parser - loads opendefinition_licenses_all.json from package data."""

import json
from pathlib import Path
from typing import Any

from .base import BaseParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("OpenDefinitionParser",)


class OpenDefinitionParser(BaseParser):
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
