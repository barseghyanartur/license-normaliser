"""License registry - all data and object factories.

This is the single file to edit when adding new licenses.  It contains:

* ``VERSION_REGISTRY`` - derived from :class:`~._enums.LicenseVersionEnum`
* ``ALIASES``           - prose / SPDX / short-form -> version key
* ``URL_MAP``           - canonical HTTPS URL (lowercase) -> version key
* CC URL regex helpers  - structural parsing of creativecommons.org URLs
* Factory functions     - ``make()``, ``make_unknown()``, ``make_synthetic()``

No resolution logic lives here.  The pipeline in :mod:`_pipeline` calls these
factories; it does not build objects directly.

URL normalisation contract
--------------------------
Every key stored in ``URL_MAP`` is the result of::

    url.rstrip("/").lower()

with the scheme normalised to ``https://``.  The pipeline applies the same
transformation to the input before lookup, so ``http://`` and ``https://``
variants, and trailing-slash variants, all resolve identically without needing
duplicate entries.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from ._enums import LicenseFamilyEnum, LicenseNameEnum, LicenseVersionEnum
from ._models import LicenseName, LicenseVersion, _fam

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "ALIASES",
    "URL_MAP",
    "VERSION_REGISTRY",
    "make",
    "make_synthetic",
    "make_unknown",
)

# ---------------------------------------------------------------------------
# Internal lookup caches (built once)
# ---------------------------------------------------------------------------

_NAME_ENUMS: dict[str, LicenseNameEnum] = {e.value: e for e in LicenseNameEnum}

# name enum -> family enum  (derived entirely from LicenseNameEnum)
_NAME_TO_FAMILY: dict[LicenseNameEnum, LicenseFamilyEnum] = {
    e: e.family_enum  # type: ignore[attr-defined]
    for e in LicenseNameEnum
}

# version key -> (canonical_url, name_enum)  (derived from LicenseVersionEnum)
VERSION_REGISTRY: dict[str, tuple[Optional[str], LicenseNameEnum]] = {
    e.value: (e.url, e.license_name)  # type: ignore[attr-defined]
    for e in LicenseVersionEnum
}


# ---------------------------------------------------------------------------
# LicenseName cache (keyed on the already-lowercase name key)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=512)
def _get_license_name(key: str) -> LicenseName:
    """Return a cached :class:`LicenseName` for *key*.

    For CC name keys that are not in the enum (synthetic runtime variants such
    as ``cc-by-nc-igo``) the family is inferred structurally: any key that
    starts with ``cc-`` maps to the CC family.
    """
    name_enum = _NAME_ENUMS.get(key, LicenseNameEnum.UNKNOWN)
    if name_enum is LicenseNameEnum.UNKNOWN and key.startswith("cc-"):
        fam = _fam(LicenseFamilyEnum.CC.value)
    else:
        fam_enum = _NAME_TO_FAMILY.get(name_enum, LicenseFamilyEnum.UNKNOWN)
        fam = _fam(fam_enum.value)
    return LicenseName(key=key, family=fam)


# ---------------------------------------------------------------------------
# Object factories
# ---------------------------------------------------------------------------


def make(version_key: str) -> LicenseVersion:
    """Build a :class:`LicenseVersion` from a key in :data:`VERSION_REGISTRY`.

    Pre-condition: *version_key* must exist in :data:`VERSION_REGISTRY`.
    """
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
    """Build a :class:`LicenseVersion` for a CC URL not explicitly listed.

    The family for *name_key* is resolved structurally by
    :func:`_get_license_name` - no global state is mutated, making this
    function thread-safe.
    """
    return LicenseVersion(
        key=version_key,
        url=url,
        license=_get_license_name(name_key),
    )


# ---------------------------------------------------------------------------
# Alias table  ->  version key in VERSION_REGISTRY
# ---------------------------------------------------------------------------

ALIASES: dict[str, str] = {
    # CC short prose
    "creative commons zero": "cc0",
    "creative commons public domain": "cc-pdm",
    "cc0 1.0": "cc0-1.0",
    "cc by": "cc-by",
    "cc by 4.0": "cc-by-4.0",
    "cc by 3.0": "cc-by-3.0",
    "cc by 2.5": "cc-by-2.5",
    "cc by 2.0": "cc-by-2.0",
    "cc-by-4": "cc-by-4.0",
    "cc-by-3": "cc-by-3.0",
    "cc by-sa": "cc-by-sa",
    "cc by-sa 4.0": "cc-by-sa-4.0",
    "cc by-sa 3.0": "cc-by-sa-3.0",
    "cc by-nd": "cc-by-nd",
    "cc by-nd 4.0": "cc-by-nd-4.0",
    "cc by-nd 3.0": "cc-by-nd-3.0",
    "cc by-nc": "cc-by-nc",
    "cc by-nc 4.0": "cc-by-nc-4.0",
    "cc by-nc 3.0": "cc-by-nc-3.0",
    "cc by-nc-sa": "cc-by-nc-sa",
    "cc by-nc-sa 4.0": "cc-by-nc-sa-4.0",
    "cc by-nc-sa 3.0": "cc-by-nc-sa-3.0",
    "cc by-nc-nd": "cc-by-nc-nd",
    "cc by-nc-nd 4.0": "cc-by-nc-nd-4.0",
    "cc by-nc-nd 3.0": "cc-by-nc-nd-3.0",
    "cc by-nc-nd 3.0 igo": "cc-by-nc-nd-3.0-igo",
    "cc-by-nc-nd 4.0": "cc-by-nc-nd-4.0",
    # Fully spelled-out CC
    "creative commons attribution": "cc-by",
    "creative commons attribution 4.0": "cc-by-4.0",
    "creative commons attribution 3.0": "cc-by-3.0",
    "creative commons attribution license": "cc-by",
    "creative commons attribution 4.0 international": "cc-by-4.0",
    "creative commons attribution 4.0 international license": "cc-by-4.0",
    "creative commons attribution-noncommercial": "cc-by-nc",
    "creative commons attribution-noncommercial 4.0": "cc-by-nc-4.0",
    "creative commons attribution-noderivatives": "cc-by-nd",
    "creative commons attribution-sharealike": "cc-by-sa",
    "creative commons attribution-noncommercial-noderivatives 4.0": "cc-by-nc-nd-4.0",
    "creative commons attribution-noncommercial-noderivatives "
    "4.0 international": "cc-by-nc-nd-4.0",
    # The version with "License" suffix - resolves to the versioned key
    "creative commons attribution-noncommercial-noderivatives "
    "4.0 international license": "cc-by-nc-nd-4.0",
    # OSI
    "apache": "apache-2.0",
    "apache license": "apache-2.0",
    "apache 2": "apache-2.0",
    "apache 2.0": "apache-2.0",
    "apache license 2.0": "apache-2.0",
    "mit license": "mit",
    "the mit license": "mit",
    "bsd": "bsd-3-clause",
    "bsd license": "bsd-3-clause",
    "mozilla": "mpl-2.0",
    "mozilla public license": "mpl-2.0",
    "isc license": "isc",
    # GPL family
    "gpl": "gpl-3.0",
    "gnu gpl": "gpl-3.0",
    "gnu gpl v2": "gpl-2.0",
    "gnu gpl v3": "gpl-3.0",
    "gpl-2.0+": "gpl-2.0",
    "gpl-3.0+": "gpl-3.0",
    "agpl": "agpl-3.0",
    "agpl-3.0+": "agpl-3.0",
    "lgpl": "lgpl-3.0",
    "lgpl-2.1+": "lgpl-2.1",
    "lgpl-3.0+": "lgpl-3.0",
    # Open data
    "odbl-1.0": "odbl",
    "open database license": "odbl",
    # Catch-all
    "public domain": "public-domain",
    "pd": "public-domain",
    "cc-zero": "cc0",
    "author manuscript": "author-manuscript",
    "all rights reserved": "all-rights-reserved",
    "no reuse": "no-reuse",
    # Properly-encoded copyright symbol (mojibake variant handled in _cache.py)
    "\u00a9 the author(s)": "publisher-specific-oa",
    # Publisher shorthand
    "elsevier user license": "elsevier-oa",
    "wiley tdm license": "wiley-tdm",
    "acs authorchoice": "acs-authorchoice",
    "springer tdm": "springer-tdm",
    "springer nature tdm": "springernature-tdm",
}


# ---------------------------------------------------------------------------
# URL map  ->  version key
#
# Keys are stored as: url.rstrip("/").lower() with scheme normalised to https.
# The pipeline applies the same normalisation to inputs before lookup, so
# there is no need for duplicate http/https entries.
# ---------------------------------------------------------------------------


def _normalise_url_key(url: str) -> str:
    """Normalise a URL for use as a map key."""
    key = url.rstrip("/").lower()
    if key.startswith("http://"):
        key = "https://" + key[len("http://") :]
    return key


def _url_key_priority(vkey: str) -> int:
    """Return a priority score for a version key when multiple keys share a URL.

    Higher score = higher priority (wins the URL slot).

    Rules:
    - IGO variants that reuse a non-IGO URL get the lowest priority (0).
    - Version-free keys (no dot, e.g. ``cc-by``, ``cc0``) get low priority (1)
      because a URL like https://creativecommons.org/licenses/by/4.0/ should
      resolve to ``cc-by-4.0``, not the version-free ``cc-by``.
    - ``-only`` SPDX suffixes are aliases for the base version key; they get
      medium priority (2) so the base key wins.
    - Everything else (proper versioned keys) gets the highest priority (3).
    """
    if vkey.endswith("-igo") and not any(
        c.isdigit() for c in vkey.split("-igo")[0].split(".")
    ):
        # version-free IGO: lowest
        return 0
    if vkey.endswith("-igo"):
        return 0  # any IGO reusing a non-IGO URL loses
    if vkey.endswith("-only"):
        return 2
    # Check for a version number (digit.digit pattern) in the key
    if re.search(r"\d+\.\d+", vkey) or re.search(r"\d+$", vkey):
        return 3
    # version-free (e.g. cc-by, cc0, gpl-3, fal)
    return 1


def _build_url_map() -> dict[str, str]:
    url_map: dict[str, str] = {}
    # Track the priority of the current occupant so a higher-priority key
    # can displace it.
    url_priority: dict[str, int] = {}

    # Primary source: enum registry (already has canonical HTTPS URLs).
    # When multiple enum entries share the same canonical URL, the key with
    # the highest _url_key_priority wins.  This handles three collision types:
    #   1. version-free vs versioned  (cc-by vs cc-by-4.0 -> cc-by-4.0 wins)
    #   2. base vs -only SPDX alias  (gpl-3.0 vs gpl-3.0-only -> gpl-3.0 wins)
    #   3. versioned vs IGO reusing same URL
    #      (cc-by-4.0 vs cc-by-4.0-igo -> cc-by-4.0 wins)
    for vkey, (url, _) in VERSION_REGISTRY.items():
        if not url:
            continue
        normalised = _normalise_url_key(url)
        priority = _url_key_priority(vkey)
        if normalised not in url_map or priority > url_priority[normalised]:
            url_map[normalised] = vkey
            url_priority[normalised] = priority

    # Supplementary entries: URL variants not captured by canonical enum URLs.
    # These are URLs found in the wild that differ structurally from the
    # canonical form (path differences, fragment variants, legacy endpoints).
    # All are scheme-normalised so each entry covers both http and https.
    extras: dict[str, str] = {
        # CC BY older versions (canonical enum only has 4.0/3.0 for some)
        "https://creativecommons.org/licenses/by/2.5": "cc-by-2.5",
        "https://creativecommons.org/licenses/by/2.0": "cc-by-2.0",
        "https://creativecommons.org/licenses/by/1.0": "cc-by-1.0",
        "https://creativecommons.org/licenses/by/3.0/deed.en_us": "cc-by-3.0",
        # CC BY-SA older
        "https://creativecommons.org/licenses/by-sa/2.5": "cc-by-sa-2.5",
        "https://creativecommons.org/licenses/by-sa/2.0": "cc-by-sa-2.0",
        # CC BY-ND older
        "https://creativecommons.org/licenses/by-nd/2.0": "cc-by-nd-2.0",
        # CC BY-NC older
        "https://creativecommons.org/licenses/by-nc/2.5": "cc-by-nc-2.5",
        "https://creativecommons.org/licenses/by-nc/2.0": "cc-by-nc-2.0",
        # CC BY-NC-SA older
        "https://creativecommons.org/licenses/by-nc-sa/2.5": "cc-by-nc-sa-2.5",
        "https://creativecommons.org/licenses/by-nc-sa/2.0": "cc-by-nc-sa-2.0",
        # CC BY-NC-ND older
        "https://creativecommons.org/licenses/by-nc-nd/2.5": "cc-by-nc-nd-2.5",
        "https://creativecommons.org/licenses/by-nc-nd/2.0": "cc-by-nc-nd-2.0",
        # CC IGO
        "https://creativecommons.org/licenses/by/3.0/igo": "cc-by-3.0-igo",
        "https://creativecommons.org/licenses/by-nc-sa/3.0/igo": "cc-by-nc-sa-3.0-igo",
        "https://creativecommons.org/licenses/by-nc-nd/3.0/igo": "cc-by-nc-nd-3.0-igo",
        # CC Zero / PDM
        "https://creativecommons.org/publicdomain/zero/1.0": "cc0",
        "https://creativecommons.org/publicdomain/mark/1.0": "cc-pdm",
        # GNU (legacy http paths still found in the wild)
        "https://www.gnu.org/licenses/gpl-2.0": "gpl-2.0",
        "https://www.gnu.org/licenses/gpl-2.0.html": "gpl-2.0",
        "https://www.gnu.org/licenses/gpl-3.0": "gpl-3.0",
        "https://www.gnu.org/licenses/gpl-3.0.html": "gpl-3.0",
        "https://www.gnu.org/licenses/agpl-3.0": "agpl-3.0",
        "https://www.gnu.org/licenses/agpl-3.0.html": "agpl-3.0",
        "https://www.gnu.org/licenses/lgpl-2.1": "lgpl-2.1",
        "https://www.gnu.org/licenses/lgpl-2.1.html": "lgpl-2.1",
        "https://www.gnu.org/licenses/lgpl-3.0": "lgpl-3.0",
        "https://www.gnu.org/licenses/lgpl-3.0.html": "lgpl-3.0",
        # Elsevier legacy http paths
        "https://www.elsevier.com/open-access/userlicense/1.0": "elsevier-oa",
        "https://www.elsevier.com/tdm/userlicense/1.0": "elsevier-tdm",
        # Wiley - fragment variants map to specific license
        "https://onlinelibrary.wiley.com/termsandconditions#vor": "wiley-vor",
        "https://onlinelibrary.wiley.com/termsandconditions#am": "wiley-am",
        "https://onlinelibrary.wiley.com/termsandconditions": "wiley-terms",
        # Springer legacy
        "https://www.springer.com/tdm": "springer-tdm",
        # Taylor & Francis case variants
        "https://www.tandfonline.com/action/showcopyright": "tandf-terms",
        "https://tandfonline.com/action/showcopyright": "tandf-terms",
        "https://www.tandfonline.com/action/showcopyright?show=full": "tandf-terms",
        # SAGE
        "https://www.sagepub.com/journalspermissions.nav": "sage-permissions",
        # ACS
        "https://doi.org/10.1021/policy/oa-license": "acs-authorchoice",
        # RSC
        "https://www.rsc.org/help/disclaimer/pages/term3.aspx": "rsc-terms",
        # IOP
        "https://iopscience.iop.org/info/page/text-and-data-mining": "iop-tdm",
        # BMJ
        "https://group.bmj.com/group/rights-licensing/permissions": "bmj-copyright",
        # AAAS
        "https://www.sciencemag.org/about/science-licenses-journal-article-reuse": (
            "aaas-author-reuse"
        ),
        # AIP
        "https://publishing.aip.org/authors/rights-and-permissions": "aip-rights",
        # JAMA
        "https://jamanetwork.com/pages/cc-by-license-permissions": "jama-cc-by",
    }

    for raw_url, vkey in extras.items():
        url_map[_normalise_url_key(raw_url)] = vkey

    return url_map


URL_MAP: dict[str, str] = _build_url_map()


# ---------------------------------------------------------------------------
# Structural CC URL regex
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
    """Parse a creativecommons.org URL into ``(version_key, name_key, canonical_url)``.

    Returns ``None`` if the URL is not a recognised CC URL structure.
    """
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
