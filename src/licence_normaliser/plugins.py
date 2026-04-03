"""Simple plugin interface definitions.

Each plugin is a callable that returns a dict or list of tuples.
Plugins are passed as CLASSES (not instances) - they're instantiated lazily.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from pathlib import Path

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

__all__ = (
    "AliasPlugin",
    "BasePlugin",
    "FamilyPlugin",
    "NamePlugin",
    "ProsePlugin",
    "RegistryPlugin",
    "URLPlugin",
)


class BasePlugin:
    """Base class for all plugins with refresh capability."""

    url: str | None = None
    local_path: str = ""

    @classmethod
    def refresh(cls, force: bool = False) -> bool:
        """Fetch fresh data from ``cls.url`` and write to ``cls.local_path``.

        The local path is resolved relative to the package root
        (``src/licence_normaliser/``).

        If ``cls.url`` is None, this is a local-only parser with no external
        source and the operation succeeds without fetching.

        Returns True on success, False on failure.

        Security note: urlopen with S310 suppression is safe here because
        cls.url is always a hardcoded class-level constant, never derived
        from user input. Subclasses must maintain this invariant.
        """
        if not cls.local_path:
            return False
        target = Path(__file__).parent / cls.local_path
        if target.exists() and not force:
            return True
        if cls.url is None:
            return True
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


class RegistryPlugin:
    """Returns key -> canonical_key mappings."""

    def load_registry(self) -> dict[str, str]:
        raise NotImplementedError

    def load_registry_lines(self) -> dict[str, tuple[int, str]]:
        """Return dict mapping key -> (line_number, source_file)."""
        return {}


class URLPlugin:
    """Returns cleaned_url -> version_key mappings."""

    def load_urls(self) -> dict[str, str]:
        raise NotImplementedError


class AliasPlugin:
    """Returns alias_string -> version_key mappings."""

    def load_aliases(self) -> dict[str, str]:
        raise NotImplementedError


class FamilyPlugin:
    """Returns version_key -> family_key mappings."""

    def load_families(self) -> dict[str, str]:
        raise NotImplementedError


class NamePlugin:
    """Returns version_key -> name_key mappings."""

    def load_names(self) -> dict[str, str]:
        raise NotImplementedError


class ProsePlugin:
    """Returns list of (compiled_pattern, version_key) for prose matching."""

    def load_prose(self) -> list[tuple[re.Pattern[str], str]]:
        raise NotImplementedError
