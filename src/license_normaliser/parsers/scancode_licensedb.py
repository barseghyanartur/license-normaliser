"""ScanCode-licensedb parser - loads scancode_licensedb.json from package data."""

import json
from pathlib import Path
from typing import Any

from .base import BaseParser


class ScanCodeLicenseDBParser(BaseParser):
    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = (
            Path(__file__).parent.parent
            / "data"
            / "scancode_licensedb"
            / "scancode_licensedb.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        if not isinstance(data, list):
            return results
        for entry in data:
            if not isinstance(entry, dict):
                continue
            key = entry.get("license_key", "")
            if not key:
                continue
            if key.lower() == "unknown":
                continue
            spdx_key = entry.get("spdx_license_key")
            category = entry.get("category", "")
            results.append(
                (
                    key,
                    {
                        "url": "",
                        "name": key,
                        "category": category,
                        "spdx_license_key": spdx_key if spdx_key else "",
                    },
                )
            )
        return results
