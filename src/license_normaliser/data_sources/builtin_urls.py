"""Built-in URL data source.

Reads ``data/urls/url_map.json`` - a ``{url: metadata_dict}`` map.
URLs are stored in their raw form; normalisation (https, no trailing slash)
is applied on load so the in-memory map is always in canonical form.

File format (``data/urls/url_map.json``)
-----------------------------------------
.. code-block:: json

    {
      "https://creativecommons.org/licenses/by/4.0/": {
        "version_key": "cc-by-4.0",
        "name_key": "cc-by",
        "family_key": "cc"
      }
    }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..exceptions import DataSourceError
from . import SourceContribution, VersionMetadata

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("BuiltinUrlSource",)

logger = logging.getLogger(__name__)

_URL_MAP_FILE = "urls/url_map.json"


def _normalise(url: str) -> str:
    """Normalise a URL for use as a lookup key (case-insensitive)."""
    key = url.strip().rstrip("/").lower()
    if key.startswith("http://"):
        key = "https://" + key[len("http://") :]
    return key


def _canonicalise(url: str) -> str:
    """Return the canonical form of a URL for storage.

    Preserves original casing and trailing slash.
    """
    key = url.strip()
    if key.startswith("http://"):
        key = "https://" + key[len("http://") :]
    return key


def _load_entry(
    raw_value: object,
    key: str,
) -> tuple[str, VersionMetadata] | None:
    """Parse a single url_map.json entry. Returns (version_key, metadata) or None."""
    if isinstance(raw_value, str):
        if not key.startswith("_comment"):
            logger.warning(
                "Entry %r has a bare string value; expected a dict with "
                "version_key, name_key, family_key. "
                "Update %r to the new dict format.",
                key,
                _URL_MAP_FILE,
            )
        return str(raw_value), {
            "name_key": "",
            "family_key": "",
            "url": _canonicalise(key),
        }
    if not isinstance(raw_value, dict):
        return None
    vkey = raw_value.get("version_key")
    name_key = raw_value.get("name_key")
    family_key = raw_value.get("family_key")
    if not all(isinstance(v, str) for v in (vkey, name_key, family_key)):
        logger.warning(
            "Entry %r: missing or non-string version_key/name_key/family_key.",
            key,
        )
        return None
    return (
        str(vkey),  # type: ignore[arg-type]
        {
            "name_key": str(name_key),
            "url": _canonicalise(key),
        },
    )


class BuiltinUrlSource:
    """Loads curated URL→metadata mappings from a JSON file."""

    name = "builtin-urls"

    def load(self, data_dir: Path) -> SourceContribution:
        path = data_dir / _URL_MAP_FILE
        if not path.exists():
            raise DataSourceError(
                f"Builtin URL map file not found: {path}. "
                "Ensure the package data is correctly installed."
            )
        try:
            raw: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise DataSourceError(
                f"Failed to parse builtin URL map file {path}: {exc}"
            ) from exc

        if not isinstance(raw, dict):
            raise DataSourceError(
                f"Builtin URL map file {path} must contain a JSON object."
            )

        url_map: dict[str, str] = {}
        metadata: dict[str, VersionMetadata] = {}
        for url, value in raw.items():
            if not isinstance(url, str):
                continue
            parsed = _load_entry(value, url)
            if parsed is None:
                continue
            vkey, meta = parsed
            url_map[_normalise(url)] = vkey
            # Always contribute URL metadata; later sources (URL > alias) override.
            metadata[vkey] = meta

        return SourceContribution(
            name=self.name,
            aliases={},
            url_map=url_map,
            prose={},
            metadata=metadata,
        )
