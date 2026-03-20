"""License registry - unified lookup tables built from data sources.

Architecture
------------
The registry is built at import time in two passes:

1. **Collect keys** - every data source contributes aliases, URL entries, and
   prose patterns.  The union of all ``version_key`` values across these
   contributions defines the complete set of known keys.

2. **Merge metadata** - metadata dicts (``name_key``, ``family_key``, ``url``)
   from all sources are merged.  Later sources override earlier ones on conflict.
   For keys that lack an explicit ``family_key``, the family-inference table
   is consulted.  ``"unknown"`` is used as the last resort.

The three lookup tables are:
* :data:`ALIASES`  - ``{cleaned_string -> version_key}``
* :data:`URL_MAP`  - ``{normalised_url  -> version_key}``
* :data:`PROSE_PATTERNS` - compiled ``(re.Pattern, version_key)`` pairs

CC URL regex
------------
The structural CC URL parser handles arbitrary ``creativecommons.org`` URLs
that are not already in ``URL_MAP``.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ._models import LicenseFamily, LicenseName, LicenseVersion
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
# Family-inference fallback table
# ---------------------------------------------------------------------------

_FAMILY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^cc0$"), "cc0"),
    (re.compile(r"^cc-pdm$"), "public-domain"),
    (re.compile(r"^cc"), "cc"),
    (re.compile(r"^gpl"), "copyleft"),
    (re.compile(r"^lgpl"), "copyleft"),
    (re.compile(r"^agpl"), "copyleft"),
    (re.compile(r"^mpl"), "osi"),
    (re.compile(r"^bsd"), "osi"),
    (re.compile(r"^mit$"), "osi"),
    (re.compile(r"^apache"), "osi"),
    (re.compile(r"^isc$"), "osi"),
    (re.compile(r"^odbl"), "open-data"),
    (re.compile(r"^odc-by"), "open-data"),
    (re.compile(r"^pddl"), "open-data"),
    (re.compile(r"^fal"), "other-oa"),
    (re.compile(r"^elsevier"), "publisher-oa"),
    (re.compile(r"^wiley"), "publisher-proprietary"),
    (re.compile(r"^springer"), "publisher-tdm"),
    (re.compile(r"^springernature"), "publisher-tdm"),
    (re.compile(r"^acs"), "publisher-oa"),
    (re.compile(r"^rsc"), "publisher-proprietary"),
    (re.compile(r"^iop"), "publisher-tdm"),
    (re.compile(r"^bmj"), "publisher-proprietary"),
    (re.compile(r"^cup"), "publisher-proprietary"),
    (re.compile(r"^aip"), "publisher-proprietary"),
    (re.compile(r"^pnas"), "publisher-proprietary"),
    (re.compile(r"^aps"), "publisher-proprietary"),
    (re.compile(r"^jama"), "publisher-oa"),
    (re.compile(r"^degruyter"), "publisher-proprietary"),
    (re.compile(r"^thieme"), "publisher-oa"),
    (re.compile(r"^tandf"), "publisher-proprietary"),
    (re.compile(r"^oup"), "publisher-oa"),
    (re.compile(r"^sage"), "publisher-proprietary"),
    (re.compile(r"^aaas"), "publisher-proprietary"),
    (re.compile(r"^no-reuse"), "publisher-proprietary"),
    (re.compile(r"^all-rights-reserved"), "publisher-proprietary"),
    (re.compile(r"^author-manuscript"), "publisher-oa"),
    (re.compile(r"^implied-oa$"), "publisher-oa"),
    (re.compile(r"^unspecified-oa$"), "other-oa"),
    (re.compile(r"^thieme-nlm$"), "publisher-oa"),
    (re.compile(r"^open-access"), "other-oa"),
    (re.compile(r"^unspecified-oa"), "other-oa"),
    (re.compile(r"^publisher-specific-oa"), "publisher-oa"),
    (re.compile(r"^other-oa"), "other-oa"),
]


def _infer_family(version_key: str) -> str:
    """Infer family_key from version_key prefix using the fallback table."""
    for pattern, family in _FAMILY_PATTERNS:
        if pattern.match(version_key):
            return family
    return "unknown"


# ---------------------------------------------------------------------------
# LicenseFamily / LicenseName caches
# ---------------------------------------------------------------------------


@lru_cache(maxsize=512)
def _get_license_family(family_key: str) -> LicenseFamily:
    """Return a cached LicenseFamily, defaulting to 'unknown'."""
    if family_key in _FAMILY_CACHE:
        return _FAMILY_CACHE[family_key]
    return LicenseFamily(key=family_key if family_key else "unknown")


@lru_cache(maxsize=512)
def _get_license_name(name_key: str) -> LicenseName:
    """Return a cached LicenseName for *name_key*."""
    vkey = _NAME_KEY_TO_VERSION_KEY.get(name_key, name_key)
    family_key = _NAME_TO_FAMILY.get(vkey, "unknown")
    return LicenseName(key=name_key, family=_get_license_family(family_key))


# ---------------------------------------------------------------------------
# Phase 1: collect keys and merge metadata from all data sources
# ---------------------------------------------------------------------------


def _data_dir() -> Path:
    """Return the absolute path to the package-level ``data/`` directory."""
    return Path(__file__).parent / "data"


def _build_registry() -> tuple[
    dict[str, dict[str, str | None]],
    dict[str, str],
    dict[str, str],
    list[tuple[re.Pattern[str], str]],
]:
    """Build VERSION_REGISTRY, ALIASES, URL_MAP, and PROSE_PATTERNS."""
    data_dir = _data_dir()
    contributions = load_all_sources(data_dir)

    # Merge all keys (from aliases, url_map, prose, metadata)
    all_keys: set[str] = set()
    merged_metadata: dict[str, dict[str, str | None]] = {}
    merged_aliases: dict[str, str] = {}
    merged_urls: dict[str, str] = {}
    merged_prose: dict[str, str] = {}

    for contrib in contributions:
        for alias, vkey in contrib.aliases.items():
            merged_aliases[alias] = vkey
            all_keys.add(vkey)
        for url, vkey in contrib.url_map.items():
            merged_urls[url] = vkey
            all_keys.add(vkey)
        for pattern, vkey in contrib.prose.items():
            merged_prose[pattern] = vkey
            all_keys.add(vkey)
        for vkey, meta in contrib.metadata.items():
            all_keys.add(vkey)
            if vkey not in merged_metadata:
                merged_metadata[vkey] = {"name_key": "", "family_key": "", "url": ""}
            if meta.get("name_key"):
                merged_metadata[vkey]["name_key"] = meta["name_key"]
            _fk = meta.get("family_key", "")
            if _fk:
                merged_metadata[vkey]["family_key"] = _fk
            url_val = meta.get("url")
            if url_val:
                merged_metadata[vkey]["url"] = url_val

    # Fill in missing family_key with inference
    for vkey in all_keys:
        meta = merged_metadata.setdefault(
            vkey, {"name_key": vkey, "family_key": "", "url": None}
        )
        if not meta.get("family_key"):
            meta["family_key"] = _infer_family(vkey)
        if not meta.get("name_key"):
            # name_key defaults to the name portion of the version key
            # e.g. "cc-by-4.0" -> name_key = "cc-by"
            meta["name_key"] = vkey.rsplit("-", 1)[0] if "-" in vkey else vkey

    # Compile prose patterns
    compiled_prose: list[tuple[re.Pattern[str], str]] = []
    for pattern_str, vkey in merged_prose.items():
        try:
            compiled_prose.append((re.compile(pattern_str, re.IGNORECASE), vkey))
        except re.error as exc:  # noqa: PERF203
            logger.warning(
                "Invalid prose pattern %r (version_key=%r): %s - skipping.",
                pattern_str,
                vkey,
                exc,
            )

    return merged_metadata, merged_aliases, merged_urls, compiled_prose


VERSION_REGISTRY: dict[str, dict[str, str | None]]
ALIASES: dict[str, str]
URL_MAP: dict[str, str]
PROSE_PATTERNS: list[tuple[re.Pattern[str], str]]

VERSION_REGISTRY, ALIASES, URL_MAP, PROSE_PATTERNS = _build_registry()

# Ensure "unknown" always exists in VERSION_REGISTRY (created at runtime, not from data)
if "unknown" not in VERSION_REGISTRY:
    VERSION_REGISTRY["unknown"] = {
        "name_key": "unknown",
        "family_key": "unknown",
        "url": None,
    }

# Build _NAME_KEY_TO_VERSION_KEY reverse map: name_key -> version_key (first match wins)
_NAME_KEY_TO_VERSION_KEY: dict[str, str] = {}
for vkey, meta in VERSION_REGISTRY.items():
    nk = meta.get("name_key", "")
    if nk and nk not in _NAME_KEY_TO_VERSION_KEY:
        _NAME_KEY_TO_VERSION_KEY[nk] = vkey

# Build _NAME_TO_FAMILY lookup from merged VERSION_REGISTRY
_NAME_TO_FAMILY: dict[str, str] = {
    vkey: (meta["family_key"] or "unknown") for vkey, meta in VERSION_REGISTRY.items()
}

# Pre-populate _FAMILY_CACHE with all known families
_FAMILY_CACHE: dict[str, LicenseFamily] = {}
for family_key in set(_NAME_TO_FAMILY.values()):
    _FAMILY_CACHE[family_key] = LicenseFamily(key=family_key)
# Always ensure "unknown" exists
if "unknown" not in _FAMILY_CACHE:
    _FAMILY_CACHE["unknown"] = LicenseFamily(key="unknown")


# ---------------------------------------------------------------------------
# Object factories
# ---------------------------------------------------------------------------


def make(version_key: str) -> LicenseVersion:
    """Build a :class:`LicenseVersion` from a key in :data:`VERSION_REGISTRY`."""
    meta = VERSION_REGISTRY.get(version_key)
    if meta is None:
        return make_unknown(version_key)
    return LicenseVersion(
        key=version_key,
        url=meta.get("url"),
        license=_get_license_name(meta["name_key"]),
    )


def make_unknown(raw_key: str) -> LicenseVersion:
    """Build an unknown :class:`LicenseVersion` from an unrecognised key."""
    return LicenseVersion(
        key=raw_key,
        url=None,
        license=_get_license_name("unknown"),
    )


def make_synthetic(version_key: str, url: str, name_key: str) -> LicenseVersion:
    """Build a :class:`LicenseVersion` for a CC URL not explicitly listed."""
    return LicenseVersion(
        key=version_key,
        url=url,
        license=_get_license_name(name_key),
    )


# ---------------------------------------------------------------------------
# Structural CC URL regex
# ---------------------------------------------------------------------------

_CCN_PATH_RE = re.compile(
    r"creativecommons\.org/licenses/"
    r"(?P<type>by(?:-nc)?(?:-nd|-sa)?)"
    r"/(?P<ver>\d+\.\d+)"
    r"(?:/(?P<igo>igo))?",
    re.IGNORECASE,
)
_CCN_ZERO_RE = re.compile(
    r"creativecommons\.org/publicdomain/zero/(?P<ver>\d+\.\d+)",
    re.IGNORECASE,
)
_CCN_MARK_RE = re.compile(
    r"creativecommons\.org/publicdomain/mark/",
    re.IGNORECASE,
)


def key_from_cc_url(raw: str) -> Optional[tuple[str, str, str]]:
    """Parse a CC URL into ``(version_key, name_key, canonical_url)``."""
    if _CCN_MARK_RE.search(raw):
        return (
            "cc-pdm",
            "cc-pdm",
            "https://creativecommons.org/publicdomain/mark/1.0/",
        )

    if m := _CCN_ZERO_RE.search(raw):
        ver = m["ver"]
        vk = "cc0" if ver == "1.0" else f"cc0-{ver}"
        return (vk, "cc0", f"https://creativecommons.org/publicdomain/zero/{ver}/")

    if m := _CCN_PATH_RE.search(raw):
        t = m["type"].lower()
        ver = m["ver"]
        igo = bool(m["igo"])

        vk = f"cc-{t}-{ver}" + ("-igo" if igo else "")
        nk = f"cc-{t}" + ("-igo" if igo else "")
        path = f"/licenses/{t}/{ver}/" + ("igo/" if igo else "")
        url = f"https://creativecommons.org{path}"
        return (vk, nk, url)

    return None
