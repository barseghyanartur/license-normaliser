"""Built-in alias data source.

Reads ``data/aliases/aliases.json`` - a simple ``{alias: version_key}`` map.
This replaces the hard-coded ``ALIASES`` dict that previously lived in
``_registry.py``.

File format (``data/aliases/aliases.json``)
-------------------------------------------
.. code-block:: json

    {
      "mit license": "mit",
      "apache 2.0": "apache-2.0",
      "cc by 4.0": "cc-by-4.0"
    }

Keys are already in cleaned (lowercase, whitespace-collapsed) form.
Values are canonical version keys.
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
__all__ = ("BuiltinAliasSource",)

logger = logging.getLogger(__name__)

_ALIASES_FILE = "aliases/aliases.json"


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
            raw: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise DataSourceError(
                f"Failed to parse builtin aliases file {path}: {exc}"
            ) from exc

        if not isinstance(raw, dict):
            raise DataSourceError(
                f"Builtin aliases file {path} must contain a JSON object."
            )

        aliases: dict[str, str] = {}
        for alias, vkey in raw.items():
            if not isinstance(alias, str) or not isinstance(vkey, str):
                logger.warning("Skipping non-string alias entry: %r -> %r", alias, vkey)
                continue
            aliases[alias.lower()] = vkey

        return SourceContribution(
            name=self.name,
            aliases=aliases,
            url_map={},
            prose={},
        )
