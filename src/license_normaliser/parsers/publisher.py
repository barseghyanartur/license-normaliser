"""Publisher parser - loads publishers.json with URLs and shorthand aliases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from license_normaliser.plugins import AliasPlugin, BasePlugin, URLPlugin

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("PublisherParser",)


class PublisherParser(BasePlugin, AliasPlugin, URLPlugin):
    url = None
    local_path = "data/publishers/publishers.json"

    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        path = Path(__file__).parent.parent / self.local_path
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        results: list[tuple[str, dict[str, Any]]] = []
        urls: dict[str, dict[str, str]] = data.get("urls", {})
        for url, meta in urls.items():
            if isinstance(meta, dict):
                results.append((url, meta))
        return results

    def load_aliases(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        aliases: dict[str, str] = data.get("shorthand_aliases", {})
        return dict(aliases)

    def load_aliases_with_lines(self) -> dict[str, tuple[str, int]]:
        """Load shorthand aliases with their source line numbers."""
        path = Path(__file__).parent.parent / self.local_path
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(content)
        lines = content.splitlines()
        result: dict[str, tuple[str, int]] = {}
        for alias_key, version_key in data.get("shorthand_aliases", {}).items():
            for i, line in enumerate(lines, start=1):
                if f'"{alias_key}"' in line:
                    result[alias_key] = (version_key, i)
                    break
        return result

    def load_urls(self) -> dict[str, str]:
        path = Path(__file__).parent.parent / self.local_path
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for url, meta in data.get("urls", {}).items():
            if not isinstance(meta, dict):
                continue
            vk = meta.get("version_key", "")
            if not vk:
                continue
            clean = url.strip().lower().rstrip("/")
            if clean.startswith("http://"):
                clean = "https://" + clean[7:]
            result[clean] = vk
        return result

    def load_urls_with_lines(self) -> dict[str, tuple[str, int]]:
        """Load URLs with their source line numbers."""
        path = Path(__file__).parent.parent / self.local_path
        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(content)
        lines = content.splitlines()
        result: dict[str, tuple[str, int]] = {}
        for url, meta in data.get("urls", {}).items():
            if not isinstance(meta, dict):
                continue
            vk = meta.get("version_key", "")
            if not vk:
                continue
            clean = url.strip().lower().rstrip("/")
            if clean.startswith("http://"):
                clean = "https://" + clean[7:]
            for i, line in enumerate(lines, start=1):
                if f'"{url}"' in line or f'"{clean}"' in line:
                    result[clean] = (vk, i)
                    break
        return result
