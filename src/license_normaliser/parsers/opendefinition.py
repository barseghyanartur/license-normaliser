"""OpenDefinition parser - loads opendefinition_licenses_all.json from package data."""

import json
from pathlib import Path
from typing import Any

from .base import BaseParser


class OpenDefinitionParser(BaseParser):
    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = (
            Path(__file__).parent.parent
            / "data"
            / "opendefinition"
            / "opendefinition_licenses_all.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            lid = entry.get("id", "")
            url = entry.get("url", "")
            results.append((lid, {"url": url, "title": entry.get("title", "")}))
        return results
