"""ScanCode-licensedb parser - loads scancode_licensedb.json from package data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from license_normaliser.plugins import BasePlugin, RegistryPlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("ScanCodeLicenseDBParser",)


class ScanCodeLicenseDBParser(BasePlugin, RegistryPlugin):
    id = "scancode-licensedb"
    url = "https://scancode-licensedb.aboutcode.org/index.json"
    local_path = "data/scancode_licensedb/scancode_licensedb.json"

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / self.local_path
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

    def load_registry(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        if not isinstance(data, list):
            return result
        for entry in data:
            if not isinstance(entry, dict):
                continue
            key = entry.get("license_key", "")
            if key and key.lower() != "unknown":
                result[key.lower().strip()] = key.lower().strip()
        return result
