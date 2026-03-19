"""License registry - unified lookup tables built from data sources + enums.

Architecture
------------
The registry is built in two phases at import time:

1. **Enum phase** - ``VERSION_REGISTRY``, the canonical set of known version
   keys, is derived from :class:`~._enums.LicenseVersionEnum`.  This is the
   *source of truth*: a key is only "known" if it appears here.

2. **Data-source phase** - :func:`_build_from_sources` collects contributions
   from every registered data source (aliases, URLs, prose patterns) and
   validates that all values point to keys that exist in ``VERSION_REGISTRY``.
   Contributions that reference unknown keys are logged and discarded.

The three merged lookup tables are:
* :data:`ALIASES`  - ``{cleaned_string -> version_key}``
* :data:`URL_MAP`  - ``{normalised_url  -> version_key}``
* :data:`PROSE_PATTERNS` - compiled ``(re.Pattern, version_key)`` pairs

Adding new normalisation rules
------------------------------
* **New alias / URL / prose pattern for an existing license** → edit the
  appropriate JSON file in ``data/``.
* **Brand-new license** → add enum entries to ``_enums.py`` *and* populate
  data files.
* **New external data source** → implement :class:`~.data_sources.DataSource`
  and add it to :data:`~.data_sources.REGISTERED_SOURCES`.

CC URL regex
------------
The structural CC URL parser lives here unchanged; it handles arbitrary
``creativecommons.org`` URLs that are not listed in ``URL_MAP``.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ._enums import LicenseFamilyEnum, LicenseNameEnum, LicenseVersionEnum
from ._models import LicenseName, LicenseVersion, _fam
from .data_sources import load_all_sources

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "ALIASES",
    "PROSE_PATTERNS",
    "URL_MAP",
    "VERSION_REGISTRY",
    "make",
    "make_synthetic",
    "make_unknown",
    "key_from_cc_url",
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_NAME_ENUMS: dict[str, LicenseNameEnum] = {e.value: e for e in LicenseNameEnum}
_NAME_TO_FAMILY: dict[LicenseNameEnum, LicenseFamilyEnum] = {
    e: e.family_enum  # type: ignore[attr-defined]
    for e in LicenseNameEnum
}

# ---------------------------------------------------------------------------
# Phase 1: VERSION_REGISTRY derived from enums (canonical source of truth)
# ---------------------------------------------------------------------------

VERSION_REGISTRY: dict[str, tuple[Optional[str], LicenseNameEnum]] = {
    e.value: (e.url, e.license_name)  # type: ignore[attr-defined]
    for e in LicenseVersionEnum
}


# ---------------------------------------------------------------------------
# LicenseName object cache
# ---------------------------------------------------------------------------


@lru_cache(maxsize=512)
def _get_license_name(key: str) -> LicenseName:
    name_enum = _NAME_ENUMS.get(key, LicenseNameEnum.UNKNOWN)
    if name_enum is LicenseNameEnum.UNKNOWN and key.startswith("cc-"):
        fam = _fam(LicenseFamilyEnum.CC.value)
    else:
        fam_enum = _NAME_TO_FAMILY.get(name_enum, LicenseFamilyEnum.UNKNOWN)
        fam = _fam(fam_enum.value)
    return LicenseName(key=key, family=fam)


# ---------------------------------------------------------------------------
# Phase 2: load data sources and build merged lookup tables
# ---------------------------------------------------------------------------


def _data_dir() -> Path:
    """Return the absolute path to the package-level ``data/`` directory."""
    # The data/ directory sits alongside this source file's package root.
    # src/license_normaliser/_registry.py  ->  package root is two levels up.
    return Path(__file__).parent / "data"


def _validate_and_filter(
    mapping: dict[str, str],
    source_name: str,
    table_name: str,
) -> dict[str, str]:
    """Return a copy of *mapping* with entries pointing to unknown keys removed."""
    clean: dict[str, str] = {}
    for k, vkey in mapping.items():
        if vkey in VERSION_REGISTRY:
            clean[k] = vkey
        else:
            # Self-referential aliases (e.g. SPDX / OD lowercase IDs) that
            # don't match a version key are silently skipped - this is expected
            # for the many obscure SPDX ids we don't recognise.
            logger.debug(
                "Source %r table %r: key %r -> %r (unknown version key, skipping)",
                source_name,
                table_name,
                k,
                vkey,
            )
    return clean


def _build_from_sources() -> tuple[
    dict[str, str],  # ALIASES
    dict[str, str],  # URL_MAP
    list[tuple[re.Pattern[str], str]],  # PROSE_PATTERNS
]:
    data_dir = _data_dir()
    contributions = load_all_sources(data_dir)

    merged_aliases: dict[str, str] = {}
    merged_urls: dict[str, str] = {}
    merged_prose: dict[str, str] = {}  # pattern -> version_key, order preserved

    for contrib in contributions:
        valid_aliases = _validate_and_filter(contrib.aliases, contrib.name, "aliases")
        valid_urls = _validate_and_filter(contrib.url_map, contrib.name, "url_map")
        valid_prose = _validate_and_filter(contrib.prose, contrib.name, "prose")
        merged_aliases.update(valid_aliases)
        merged_urls.update(valid_urls)
        merged_prose.update(valid_prose)

    # Compile prose patterns
    compiled: list[tuple[re.Pattern[str], str]] = []
    for pattern_str, vkey in merged_prose.items():
        try:
            compiled.append((re.compile(pattern_str, re.IGNORECASE), vkey))
        except re.error as exc:  # noqa: PERF203
            logger.warning(
                "Invalid prose pattern %r (version_key=%r): %s - skipping.",
                pattern_str,
                vkey,
                exc,
            )

    return merged_aliases, merged_urls, compiled


ALIASES: dict[str, str]
URL_MAP: dict[str, str]
PROSE_PATTERNS: list[tuple[re.Pattern[str], str]]

ALIASES, URL_MAP, PROSE_PATTERNS = _build_from_sources()


# ---------------------------------------------------------------------------
# Object factories
# ---------------------------------------------------------------------------


def make(version_key: str) -> LicenseVersion:
    """Build a :class:`LicenseVersion` from a key in :data:`VERSION_REGISTRY`."""
    url, name_enum = VERSION_REGISTRY[version_key]
    return LicenseVersion(
        key=version_key,
        url=url,
        license=_get_license_name(name_enum.value),
    )


def make_unknown(raw_key: str) -> LicenseVersion:
    """Build an unknown :class:`LicenseVersion` from an unrecognised key."""
    return LicenseVersion(
        key=raw_key,
        url=None,
        license=_get_license_name(LicenseNameEnum.UNKNOWN.value),
    )


def make_synthetic(version_key: str, url: str, name_key: str) -> LicenseVersion:
    """Build a :class:`LicenseVersion` for a CC URL not explicitly listed."""
    return LicenseVersion(
        key=version_key,
        url=url,
        license=_get_license_name(name_key),
    )


# ---------------------------------------------------------------------------
# Structural CC URL regex (unchanged from original)
# ---------------------------------------------------------------------------

_CC_PATH_RE = re.compile(
    r"creativecommons\.org/licenses/"
    r"(?P<type>by(?:-nc)?(?:-nd|-sa)?)"
    r"/(?P<ver>\d+\.\d+)"
    r"(?:/(?P<igo>igo))?",
    re.IGNORECASE,
)
_CC_ZERO_RE = re.compile(
    r"creativecommons\.org/publicdomain/zero/(?P<ver>\d+\.\d+)",
    re.IGNORECASE,
)
_CC_MARK_RE = re.compile(
    r"creativecommons\.org/publicdomain/mark/",
    re.IGNORECASE,
)


def key_from_cc_url(raw: str) -> Optional[tuple[str, str, str]]:
    """Parse a CC URL into ``(version_key, name_key, canonical_url)``."""
    if _CC_MARK_RE.search(raw):
        return (
            "cc-pdm",
            "cc-pdm",
            "https://creativecommons.org/publicdomain/mark/1.0/",
        )

    if m := _CC_ZERO_RE.search(raw):
        ver = m["ver"]
        vk = "cc0" if ver == "1.0" else f"cc0-{ver}"
        return (vk, "cc0", f"https://creativecommons.org/publicdomain/zero/{ver}/")

    if m := _CC_PATH_RE.search(raw):
        t = m["type"].lower()
        ver = m["ver"]
        igo = bool(m["igo"])

        vk = f"cc-{t}-{ver}" + ("-igo" if igo else "")
        nk = f"cc-{t}" + ("-igo" if igo else "")
        path = f"/licenses/{t}/{ver}/" + ("igo/" if igo else "")
        url = f"https://creativecommons.org{path}"
        return (vk, nk, url)

    return None
