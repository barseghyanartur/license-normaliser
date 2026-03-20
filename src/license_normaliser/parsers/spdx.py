"""SPDX parser - loads spdx-licenses.json from package data."""

import json
from pathlib import Path
from typing import Any

from .base import BaseParser


class SPDXParser(BaseParser):
    url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
    local_path = "data/spdx/spdx.json"

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / "data" / "spdx" / "spdx.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        for entry in data.get("licenses", []):
            if not isinstance(entry, dict):
                continue
            lid = entry.get("licenseId", "")
            urls = entry.get("seeAlso", [])
            url = urls[0] if urls else ""
            results.append((lid, {"url": url, "name": entry.get("name", "")}))
        return results
