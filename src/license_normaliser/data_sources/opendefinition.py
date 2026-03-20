"""OpenDefinition data source.

Reads ``data/opendefinition/opendefinition_licenses_all.json`` and contributes
alias and URL entries for every OpenDefinition license that maps to a known
version key.

The OpenDefinition JSON schema uses ``"id"`` as the license identifier and
``"url"`` as the canonical URL.  Both are registered if non-empty.

File format
-----------
.. code-block:: json

    {
      "MIT": {"id": "MIT", "url": "https://opensource.org/licenses/MIT", ...},
      "CC-BY-4.0": {"id": "CC-BY-4.0", "url": "https://creativecommons.org/...", ...}
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
__all__ = ("OpenDefinitionSource",)

logger = logging.getLogger(__name__)

_OD_FILE = "opendefinition/opendefinition_licenses_all.json"


def _normalise_url(url: str) -> str:
    key = url.strip().rstrip("/").lower()
    if key.startswith("http://"):
        key = "https://" + key[len("http://") :]
    return key


class OpenDefinitionSource:
    """Extracts aliases and URL entries from the OpenDefinition license list."""

    name = "opendefinition"

    def load(self, data_dir: Path) -> SourceContribution:
        path = data_dir / _OD_FILE
        if not path.exists():
            logger.debug("OpenDefinition license file not found at %s; skipping.", path)
            return SourceContribution(
                name=self.name,
                aliases={},
                url_map={},
                prose={},
                metadata={},
            )

        try:
            data: dict = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise DataSourceError(
                f"Failed to parse OpenDefinition license file {path}: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise DataSourceError(
                f"OpenDefinition file {path}: expected a top-level JSON object."
            )

        aliases: dict[str, str] = {}
        url_map: dict[str, str] = {}
        metadata: dict[str, VersionMetadata] = {}

        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            license_id: str = entry.get("id", "")
            url: str = entry.get("url", "")

            if not license_id:
                continue

            cleaned_id = license_id.lower()
            aliases[cleaned_id] = cleaned_id
            # Contribute metadata: name_key = version_key, family_key = None
            # (family will be inferred by the registry builder if not covered
            # by another source).
            if cleaned_id not in metadata:
                metadata[cleaned_id] = {
                    "family_key": "",
                }

            # Also register legacy_ids if present
            for legacy_id in entry.get("legacy_ids", []):
                if isinstance(legacy_id, str) and legacy_id:
                    aliases[legacy_id.lower()] = cleaned_id

            # Register the canonical URL
            if url and url.strip():
                norm = _normalise_url(url)
                if norm not in url_map:
                    url_map[norm] = cleaned_id

        logger.debug(
            "OpenDefinition source: %d aliases, %d URL entries, %d metadata "
            "from %d records.",
            len(aliases),
            len(url_map),
            len(metadata),
            len(data),
        )

        return SourceContribution(
            name=self.name,
            aliases=aliases,
            url_map=url_map,
            prose={},
            metadata=metadata,
        )
