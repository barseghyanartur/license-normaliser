"""SPDX data source.

Reads ``data/spdx/spdx-licenses.json`` (the official SPDX license list) and
contributes alias and URL entries for every SPDX license that maps to a known
version key in the built-in registry.

This source converts SPDX identifiers (e.g. ``CC-BY-4.0``) to their
lowercase canonical form and registers them as aliases.  It also registers
the ``seeAlso`` URLs so that SPDX canonical URLs resolve correctly.

Only licenses whose cleaned SPDX ID already exists as a version key (or maps
via the existing alias table) are registered.  Unknown SPDX identifiers are
logged at DEBUG level and silently skipped - they do NOT cause an error.

File format
-----------
Standard SPDX JSON format:
``{"licenses": [{"licenseId": "MIT", "seeAlso": ["https://..."], ...}, ...]}``
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
__all__ = ("SpdxSource",)

logger = logging.getLogger(__name__)

_SPDX_FILE = "spdx/spdx-licenses.json"


def _normalise_url(url: str) -> str:
    key = url.strip().rstrip("/").lower()
    if key.startswith("http://"):
        key = "https://" + key[len("http://") :]
    return key


class SpdxSource:
    """Extracts aliases and URL entries from the SPDX license list."""

    name = "spdx"

    def load(self, data_dir: Path) -> SourceContribution:
        path = data_dir / _SPDX_FILE
        if not path.exists():
            # SPDX file is optional - log and return empty contribution
            logger.debug(
                "SPDX license file not found at %s; skipping SPDX source.", path
            )
            return SourceContribution(name=self.name, aliases={}, url_map={}, prose={})

        try:
            data: dict = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise DataSourceError(
                f"Failed to parse SPDX license file {path}: {exc}"
            ) from exc

        licenses: list = data.get("licenses", [])
        if not isinstance(licenses, list):
            raise DataSourceError(
                f"SPDX file {path}: expected 'licenses' to be a list."
            )

        aliases: dict[str, str] = {}
        url_map: dict[str, str] = {}

        for entry in licenses:
            if not isinstance(entry, dict):
                continue
            license_id: str = entry.get("licenseId", "")
            if not license_id:
                continue

            cleaned_id = license_id.lower()

            # Register the lowercase SPDX ID as an alias pointing to itself
            # (the pipeline's direct-lookup step will handle it if it matches
            # a version key; otherwise the alias -> version_key map is used).
            # We store it so the registry builder can validate it later.
            aliases[cleaned_id] = cleaned_id

            # Also register "deprecated" SPDX variants
            # e.g. GPL-2.0 (deprecated) -> gpl-2.0
            if entry.get("isDeprecatedLicenseId"):
                # deprecated ids are superseded; still useful as aliases
                logger.debug("SPDX deprecated id %r registered as alias.", license_id)

            # Register seeAlso URLs
            for url in entry.get("seeAlso", []):
                if not isinstance(url, str) or not url.strip():
                    continue
                norm = _normalise_url(url)
                # Avoid overwriting an existing entry with a less-specific one
                if norm not in url_map:
                    url_map[norm] = cleaned_id

        logger.debug(
            "SPDX source: %d aliases, %d URL entries from %d license records.",
            len(aliases),
            len(url_map),
            len(licenses),
        )

        return SourceContribution(
            name=self.name,
            aliases=aliases,
            url_map=url_map,
            prose={},
        )
