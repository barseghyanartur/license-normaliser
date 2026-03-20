"""Publisher parser - loads publishers.json with URLs and shorthand aliases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import BaseParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("PublisherParser",)


class PublisherParser(BaseParser):
    url = None
    local_path = "data/publishers/publishers.json"
    is_registry_entry = False

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / "data" / "publishers" / "publishers.json"
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        urls: dict[str, dict[str, str]] = data.get("urls", {})
        for url, meta in urls.items():
            if isinstance(meta, dict):
                results.append((url, meta))
        return results

    def parse_shorthand_aliases(self) -> list[tuple[str, str]]:
        """Return shorthand string -> version_key mappings."""
        path = Path(__file__).parent.parent / "data" / "publishers" / "publishers.json"
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, str]] = []
        aliases: dict[str, str] = data.get("shorthand_aliases", {})
        for shorthand, version_key in aliases.items():
            results.append((shorthand, version_key))
        return results

    def get_urls(self) -> dict[str, dict[str, str]]:
        """Return URL -> metadata dict for extending URL_MAP."""
        path = Path(__file__).parent.parent / "data" / "publishers" / "publishers.json"
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        urls: dict[str, dict[str, str]] = data.get("urls", {})
        return urls

    def get_shorthand_aliases(self) -> dict[str, str]:
        """Return shorthand -> version_key dict for extending ALIASES."""
        path = Path(__file__).parent.parent / "data" / "publishers" / "publishers.json"
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        aliases: dict[str, str] = data.get("shorthand_aliases", {})
        return aliases
