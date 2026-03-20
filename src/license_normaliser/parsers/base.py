"""Base parser interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("BaseParser",)


class BaseParser(ABC):
    """All data parsers must implement this."""

    url: str | None
    local_path: str
    is_registry_entry: bool = True

    @abstractmethod
    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        """Return (license_key, metadata_dict) for every entry."""
        ...

    @classmethod
    def refresh(cls, force: bool = False) -> bool:
        """Fetch fresh data from ``cls.url`` and write to ``cls.local_path``.

        The local path is resolved relative to the package root
        (``src/license_normaliser/``).

        If ``cls.url`` is None, this is a local-only parser with no external
        source and the operation succeeds without fetching.

        Returns True on success, False on failure.
        """
        target = Path(__file__).parent.parent / cls.local_path
        if target.exists() and not force:
            return True
        if cls.url is None:
            return False
        try:
            import json
            import urllib.request

            with urllib.request.urlopen(cls.url, timeout=30) as response:  # noqa: S310
                data = response.read()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            json.loads(data.decode("utf-8"))
            return True
        except Exception:
            return False
