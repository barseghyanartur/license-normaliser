"""Base parser interface."""

import json
import logging
import urllib.error
import urllib.request
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
            with urllib.request.urlopen(cls.url, timeout=30) as response:  # noqa: S310
                raw_bytes = response.read()
            json.loads(raw_bytes.decode("utf-8"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw_bytes)
            return True
        except urllib.error.URLError as exc:
            logging.warning(
                "refresh(%s): URLError fetching %s - %s", cls.__name__, cls.url, exc
            )
            return False
        except urllib.error.HTTPError as exc:
            logging.warning(
                "refresh(%s): HTTPError %s fetching %s", cls.__name__, exc.code, cls.url
            )
            return False
        except json.JSONDecodeError as exc:
            logging.error(
                "refresh(%s): invalid JSON from %s - %s", cls.__name__, cls.url, exc
            )
            return False
        except OSError as exc:
            logging.error(
                "refresh(%s): OSError writing %s - %s", cls.__name__, target, exc
            )
            return False
