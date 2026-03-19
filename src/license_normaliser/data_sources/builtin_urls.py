"""Built-in URL data source.

Reads ``data/urls/url_map.json`` - a ``{url: version_key}`` map.
URLs are stored in their raw form; normalisation (https, no trailing slash)
is applied on load so the in-memory map is always in canonical form.

File format (``data/urls/url_map.json``)
-----------------------------------------
.. code-block:: json

    {
      "https://creativecommons.org/licenses/by/4.0/": "cc-by-4.0",
      "http://creativecommons.org/licenses/by/4.0/": "cc-by-4.0"
    }

Both http and https variants may be listed; duplicates after normalisation
are resolved by keeping the last entry (file order).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..exceptions import DataSourceError
from . import SourceContribution

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("BuiltinUrlSource",)

logger = logging.getLogger(__name__)

_URL_MAP_FILE = "urls/url_map.json"


def _normalise(url: str) -> str:
    """Normalise a URL for use as a lookup key."""
    key = url.strip().rstrip("/").lower()
    if key.startswith("http://"):
        key = "https://" + key[len("http://") :]
    return key


class BuiltinUrlSource:
    """Loads curated URL→version-key mappings from a JSON file."""

    name = "builtin-urls"

    def load(self, data_dir: Path) -> SourceContribution:
        path = data_dir / _URL_MAP_FILE
        if not path.exists():
            raise DataSourceError(
                f"Builtin URL map file not found: {path}. "
                "Ensure the package data is correctly installed."
            )
        try:
            raw: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise DataSourceError(
                f"Failed to parse builtin URL map file {path}: {exc}"
            ) from exc

        if not isinstance(raw, dict):
            raise DataSourceError(
                f"Builtin URL map file {path} must contain a JSON object."
            )

        url_map: dict[str, str] = {}
        for url, vkey in raw.items():
            if not isinstance(url, str) or not isinstance(vkey, str):
                logger.warning("Skipping non-string URL entry: %r -> %r", url, vkey)
                continue
            url_map[_normalise(url)] = vkey

        return SourceContribution(
            name=self.name,
            aliases={},
            url_map=url_map,
            prose={},
        )
