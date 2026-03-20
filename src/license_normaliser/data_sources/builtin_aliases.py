"""Built-in alias data source.

Reads ``data/aliases/aliases.json`` - a ``{alias: metadata_dict}`` map.
Keys must already be in cleaned (lowercase, whitespace-collapsed) form.
Values are dicts with ``version_key``, ``name_key``, and ``family_key``.

File format (``data/aliases/aliases.json``)
-------------------------------------------
.. code-block:: json

    {
      "mit license": {"version_key": "mit", "name_key": "mit", "family_key": "osi"},
      "apache 2.0": {"version_key": "apache-2.0", "name_key": "apache",
                     "family_key": "osi"},
      "cc by 4.0": {"version_key": "cc-by-4.0", "name_key": "cc-by", "family_key": "cc"}
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
__all__ = ("BuiltinAliasSource",)

logger = logging.getLogger(__name__)

_ALIASES_FILE = "aliases/aliases.json"


def _load_entry(
    raw_value: object,
    key: str,
) -> tuple[str, VersionMetadata] | None:
    """Parse a single aliases.json entry. Returns (version_key, metadata) or None."""
    if isinstance(raw_value, str):
        if not key.startswith("_comment"):
            logger.warning(
                "Entry %r has a bare string value; expected a dict with "
                "version_key, name_key, family_key. "
                "Update %r to the new dict format.",
                key,
                _ALIASES_FILE,
            )
        return None
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
        {"name_key": str(name_key), "family_key": str(family_key)},
    )


class BuiltinAliasSource:
    """Loads curated alias mappings from a JSON file."""

    name = "builtin-aliases"

    def load(self, data_dir: Path) -> SourceContribution:
        path = data_dir / _ALIASES_FILE
        if not path.exists():
            raise DataSourceError(
                f"Builtin aliases file not found: {path}. "
                "Ensure the package data is correctly installed."
            )
        try:
            raw: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise DataSourceError(
                f"Failed to parse builtin aliases file {path}: {exc}"
            ) from exc

        if not isinstance(raw, dict):
            raise DataSourceError(
                f"Builtin aliases file {path} must contain a JSON object."
            )

        aliases: dict[str, str] = {}
        metadata: dict[str, VersionMetadata] = {}
        for alias, value in raw.items():
            if not isinstance(alias, str):
                continue
            parsed = _load_entry(value, alias)
            if parsed is None:
                continue
            vkey, meta = parsed
            aliases[alias.lower()] = vkey
            if vkey not in metadata:
                metadata[vkey] = meta

        return SourceContribution(
            name=self.name,
            aliases=aliases,
            url_map={},
            prose={},
            metadata=metadata,
        )
