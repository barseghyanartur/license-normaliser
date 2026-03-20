"""Dynamic registry built from parsers + make factory."""

from __future__ import annotations

from license_normaliser.parsers import get_parsers
from license_normaliser.parsers.alias import AliasParser
from license_normaliser.parsers.publisher import PublisherParser

from ._models import LicenseFamily, LicenseName, LicenseVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

REGISTRY: dict[str, str] = {}
URL_MAP: dict[str, str] = {}
ALIASES: dict[str, str] = {}
FAMILY_OVERRIDES: dict[str, str] = {}


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
    if k.startswith(
        (
            "elsevier-",
            "wiley-",
            "springer-",
            "springernature-",
            "acs-",
            "rsc-",
            "iop-",
            "bmj-",
            "aaas-",
            "pnas-",
            "aps-",
            "cup-",
            "aip-",
            "jama-",
            "degruyter-",
            "oup-",
            "sage-",
            "tandf-",
            "thieme-",
        )
    ):
        return "publisher-proprietary"
    if k.startswith(
        (
            "elsevier-oa",
            "acs-authorchoice",
            "acs-authorchoice-ccby",
            "acs-authorchoice-ccbyncnd",
            "acs-authorchoice-nih",
            "jama-cc-by",
            "thieme-nlm",
            "implied-oa",
            "unspecified-oa",
            "publisher-specific-oa",
            "author-manuscript",
            "oup-chorus",
        )
    ):
        return "publisher-oa"
    if k.startswith(
        (
            "elsevier-tdm",
            "wiley-tdm",
            "springer-tdm",
            "springernature-tdm",
            "iop-tdm",
            "aps-tdm",
        )
    ):
        return "publisher-tdm"
    if k in ("public-domain", "other-oa", "open-access"):
        return "public-domain" if k == "public-domain" else "other-oa"
    return "osi"


def _infer_name(key: str) -> str:
    k = key.lower()
    if k.startswith("cc0"):
        return "cc0"
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
            if getattr(parser, "is_registry_entry", True):
                REGISTRY[canonical] = canonical
            if url := meta.get("url"):
                clean_url = url.strip().lower().rstrip("/")
                if clean_url.startswith("http://"):
                    clean_url = "https://" + clean_url[7:]
                URL_MAP[clean_url] = canonical
    _extend_from_publisher_parser()


def _extend_from_publisher_parser() -> None:
    global URL_MAP
    publisher = PublisherParser()
    for url, meta in publisher.get_urls().items():
        clean_url = url.strip().lower().rstrip("/")
        if clean_url.startswith("http://"):
            clean_url = "https://" + clean_url[7:]
        if "version_key" in meta:
            URL_MAP[clean_url] = meta["version_key"]
        else:
            URL_MAP[clean_url] = url.lower().strip()


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
        ("cc by", "cc-by"),
    ]
    ALIASES = dict(_cc_forms)
    ALIASES.update(AliasParser.get_aliases())
    ALIASES.update(PublisherParser().get_shorthand_aliases())
    ALIASES["public domain"] = "cc0-1.0"
    ALIASES["pd"] = "cc0-1.0"


def _build_family_overrides() -> None:
    global FAMILY_OVERRIDES
    FAMILY_OVERRIDES.update(AliasParser.get_family_overrides())


_build_registry()
_build_aliases()
_build_family_overrides()


def make(key: str) -> LicenseVersion:
    """Factory: build a LicenseVersion from a registry key."""
    k = key.lower().strip()
    canonical = REGISTRY.get(k) or k
    url = URL_MAP.get(canonical) or URL_MAP.get(k)
    name_key = _infer_name(canonical)
    family_key = FAMILY_OVERRIDES.get(canonical) or _infer_family(canonical)
    family = LicenseFamily(key=family_key)
    name = LicenseName(key=name_key, family=family)
    return LicenseVersion(key=canonical, url=url, license=name)


def make_unknown(key: str) -> LicenseVersion:
    """Factory: build an unknown LicenseVersion for unresolved input."""
    family = LicenseFamily(key="unknown")
    name = LicenseName(key=key, family=family)
    return LicenseVersion(key=key, url=None, license=name)
