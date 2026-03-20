"""Dynamic registry built from parsers + make factory."""

from __future__ import annotations

from license_normaliser.parsers import get_parsers

from ._models import LicenseFamily, LicenseName, LicenseVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

REGISTRY: dict[str, str] = {}
URL_MAP: dict[str, str] = {}
ALIASES: dict[str, str] = {}


def _infer_family(key: str) -> str:
    k = key.lower()
    if k.startswith("cc0"):
        return "cc0"
    if k.startswith("cc-pdm"):
        return "public-domain"
    if k.startswith("cc-"):
        return "cc"
    if k.startswith(("gpl-", "agpl-", "lgpl-")):
        return "copyleft"
    if k.startswith(("odbl-", "pddl-", "odc-")):
        return "data"
    return "osi"


def _infer_name(key: str) -> str:
    k = key.lower()
    if k.startswith("cc-"):
        parts = k.split("-")
        for i, part in enumerate(parts):
            if part.replace(".", "").isdigit():
                return "-".join(parts[:i])
        return "-".join(parts[:2])
    return k


def _build_registry() -> None:
    global REGISTRY, URL_MAP
    for parser in get_parsers():
        for key, meta in parser.parse():
            canonical = key.lower().strip()
            REGISTRY[canonical] = canonical
            if url := meta.get("url"):
                clean_url = url.strip().lower().rstrip("/")
                if clean_url.startswith("http://"):
                    clean_url = "https://" + clean_url[7:]
                URL_MAP[clean_url] = canonical


def _build_aliases() -> None:
    global ALIASES
    _cc_forms: list[tuple[str, str]] = [
        ("cc by 1.0", "cc-by-1.0"),
        ("cc by 2.0", "cc-by-2.0"),
        ("cc by 2.5", "cc-by-2.5"),
        ("cc by 3.0", "cc-by-3.0"),
        ("cc by 4.0", "cc-by-4.0"),
        ("cc by-nc 1.0", "cc-by-nc-1.0"),
        ("cc by-nc 2.0", "cc-by-nc-2.0"),
        ("cc by-nc 2.5", "cc-by-nc-2.5"),
        ("cc by-nc 3.0", "cc-by-nc-3.0"),
        ("cc by-nc 4.0", "cc-by-nc-4.0"),
        ("cc by-nc-nd 1.0", "cc-by-nc-nd-1.0"),
        ("cc by-nc-nd 2.0", "cc-by-nc-nd-2.0"),
        ("cc by-nc-nd 2.5", "cc-by-nc-nd-2.5"),
        ("cc by-nc-nd 3.0", "cc-by-nc-nd-3.0"),
        ("cc by-nc-nd 4.0", "cc-by-nc-nd-4.0"),
        ("cc by-nc-sa 1.0", "cc-by-nc-sa-1.0"),
        ("cc by-nc-sa 2.0", "cc-by-nc-sa-2.0"),
        ("cc by-nc-sa 2.5", "cc-by-nc-sa-2.5"),
        ("cc by-nc-sa 3.0", "cc-by-nc-sa-3.0"),
        ("cc by-nc-sa 4.0", "cc-by-nc-sa-4.0"),
        ("cc by-nd 1.0", "cc-by-nd-1.0"),
        ("cc by-nd 2.0", "cc-by-nd-2.0"),
        ("cc by-nd 3.0", "cc-by-nd-3.0"),
        ("cc by-nd 4.0", "cc-by-nd-4.0"),
        ("cc by-sa 1.0", "cc-by-sa-1.0"),
        ("cc by-sa 2.0", "cc-by-sa-2.0"),
        ("cc by-sa 2.5", "cc-by-sa-2.5"),
        ("cc by-sa 3.0", "cc-by-sa-3.0"),
        ("cc by-sa 4.0", "cc-by-sa-4.0"),
        ("cc by-nc-nd 4.0", "cc-by-nc-nd-4.0"),
        ("cc by-nc-sa 4.0", "cc-by-nc-sa-4.0"),
        ("cc0 1.0", "cc0-1.0"),
        ("creative commons cc0 1.0", "cc0-1.0"),
        ("creative commons zero 1.0", "cc0-1.0"),
        ("public domain", "cc0-1.0"),
    ]
    ALIASES = dict(_cc_forms)


_build_registry()
_build_aliases()


def make(key: str) -> LicenseVersion:
    """Factory: build a LicenseVersion from a registry key."""
    k = key.lower().strip()
    canonical = REGISTRY.get(k) or k
    url = URL_MAP.get(canonical) or URL_MAP.get(k)
    name_key = _infer_name(canonical)
    family_key = _infer_family(canonical)
    family = LicenseFamily(key=family_key)
    name = LicenseName(key=name_key, family=family)
    return LicenseVersion(key=canonical, url=url, license=name)


def make_unknown(key: str) -> LicenseVersion:
    """Factory: build an unknown LicenseVersion for unresolved input."""
    family = LicenseFamily(key="unknown")
    name = LicenseName(key=key, family=family)
    return LicenseVersion(key=key, url=None, license=name)
