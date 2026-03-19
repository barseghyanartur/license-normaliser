"""Resolution pipeline - six steps, first match wins.

Each step is a pure function that accepts a cleaned lowercase string and
returns either a registry version key (``str``) or ``None``, except for
steps that may produce a fully-formed :class:`~._models.LicenseVersion` when
the output cannot be expressed as a simple registry key (synthetic CC URLs,
fallback).

Steps
-----
1. ``step_direct``   - direct hit in :data:`~._registry.VERSION_REGISTRY`
2. ``step_alias``    - hit in :data:`~._registry.ALIASES`
3. ``step_url``      - hit in :data:`~._registry.URL_MAP` after URL normalisation
4. ``step_cc_regex`` - structural parse of any creativecommons.org URL
5. ``step_prose``    - keyword scan for long inputs (>= ``_PROSE_MIN_LEN``)
6. ``step_fallback`` - always matches; returns an
   unknown :class:`~._models.LicenseVersion`

The orchestrator in :mod:`_cache` calls these in order.  Each step can also
be called directly in tests.
"""

from __future__ import annotations

import re
from typing import Optional

from ._models import LicenseVersion
from ._registry import (
    ALIASES,
    URL_MAP,
    VERSION_REGISTRY,
    key_from_cc_url,
    make,
    make_synthetic,
    make_unknown,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "step_alias",
    "step_cc_regex",
    "step_direct",
    "step_fallback",
    "step_prose",
    "step_url",
)

# Minimum cleaned-string length before prose scanning is attempted.
# Short strings that reach this step are almost certainly unknown tokens,
# not prose sentences, so skipping them avoids false positives.
_PROSE_MIN_LEN: int = 20

# Compiled prose patterns in priority order (most specific first).
_PROSE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"cc\s*by-nc-nd\s*4\.0", re.I), "cc-by-nc-nd-4.0"),
    (re.compile(r"cc\s*by-nc-nd\s*3\.0", re.I), "cc-by-nc-nd-3.0"),
    (re.compile(r"cc\s*by-nc-nd", re.I), "cc-by-nc-nd"),
    (re.compile(r"cc\s*by-nc-sa\s*4\.0", re.I), "cc-by-nc-sa-4.0"),
    (re.compile(r"cc\s*by-nc-sa\s*3\.0", re.I), "cc-by-nc-sa-3.0"),
    (re.compile(r"cc\s*by-nc-sa", re.I), "cc-by-nc-sa"),
    (re.compile(r"cc\s*by-nc\s*4\.0", re.I), "cc-by-nc-4.0"),
    (re.compile(r"cc\s*by-nc\s*3\.0", re.I), "cc-by-nc-3.0"),
    (re.compile(r"cc\s*by-nc", re.I), "cc-by-nc"),
    (re.compile(r"cc\s*by-sa\s*4\.0", re.I), "cc-by-sa-4.0"),
    (re.compile(r"cc\s*by-sa\s*3\.0", re.I), "cc-by-sa-3.0"),
    (re.compile(r"cc\s*by-sa", re.I), "cc-by-sa"),
    (re.compile(r"cc\s*by-nd\s*4\.0", re.I), "cc-by-nd-4.0"),
    (re.compile(r"cc\s*by-nd\s*3\.0", re.I), "cc-by-nd-3.0"),
    (re.compile(r"cc\s*by-nd", re.I), "cc-by-nd"),
    (re.compile(r"cc\s*by\s*4\.0", re.I), "cc-by-4.0"),
    (re.compile(r"cc\s*by\s*3\.0", re.I), "cc-by-3.0"),
    (re.compile(r"cc\s*by\s*2\.0", re.I), "cc-by-2.0"),
    (re.compile(r"\bcc\s*by\b(?!\s*-)", re.I), "cc-by"),
    (re.compile(r"\bcc\s*0\b|cc\s*zero", re.I), "cc0"),
    (
        re.compile(r"attribution.{0,30}non.?commercial.{0,30}no.?deriv", re.I),
        "cc-by-nc-nd",
    ),
    (
        re.compile(r"attribution.{0,30}non.?commercial.{0,30}share.?alike", re.I),
        "cc-by-nc-sa",
    ),
    (re.compile(r"attribution.{0,30}non.?commercial", re.I), "cc-by-nc"),
    (re.compile(r"attribution.{0,30}no.?deriv", re.I), "cc-by-nd"),
    (re.compile(r"attribution.{0,30}share.?alike", re.I), "cc-by-sa"),
    (re.compile(r"\battribution\b", re.I), "cc-by"),
    (re.compile(r"elsevier.*tdm|tdm.*elsevier", re.I), "elsevier-tdm"),
    (re.compile(r"elsevier.*user\s*licen", re.I), "elsevier-oa"),
    (re.compile(r"wiley.*tdm|tdm.*wiley", re.I), "wiley-tdm"),
    (re.compile(r"springer.*tdm|tdm.*springer", re.I), "springer-tdm"),
    (re.compile(r"acs\s*authorchoice.*cc\s*by(?!-nc)", re.I), "acs-authorchoice-ccby"),
    (re.compile(r"acs\s*authorchoice", re.I), "acs-authorchoice"),
    (re.compile(r"all\s*rights\s*reserved", re.I), "all-rights-reserved"),
    (re.compile(r"author\s*manuscript", re.I), "author-manuscript"),
    (re.compile(r"public\s*domain", re.I), "public-domain"),
    (re.compile(r"open\s*access", re.I), "other-oa"),
]


def _normalise_url_for_lookup(cleaned: str) -> str:
    """Normalise scheme to https and strip trailing slash for URL_MAP lookup."""
    if cleaned.startswith("http://"):
        cleaned = "https://" + cleaned[len("http://") :]
    return cleaned.rstrip("/")


# ---------------------------------------------------------------------------
# Step implementations
# ---------------------------------------------------------------------------


def step_direct(cleaned: str) -> Optional[str]:
    """Step 1: direct registry lookup."""
    return cleaned if cleaned in VERSION_REGISTRY else None


def step_alias(cleaned: str) -> Optional[str]:
    """Step 2: alias table lookup."""
    return ALIASES.get(cleaned)


def step_url(cleaned: str) -> Optional[str]:
    """Step 3: exact URL map lookup (scheme-normalised, trailing-slash stripped).

    Strips the trailing slash here so that this function is correct whether
    called through the normal pipeline (where _clean has already stripped it)
    or called directly in tests / external code where it may not have been
    stripped yet.
    """
    normalised = _normalise_url_for_lookup(cleaned)
    return URL_MAP.get(normalised)


def step_cc_regex(cleaned: str) -> Optional[LicenseVersion]:
    """Step 4: structural CC URL regex.

    Returns a :class:`~._models.LicenseVersion` (possibly synthetic) or
    ``None`` if the input does not look like a CC URL.
    """
    if "creativecommons.org" not in cleaned:
        return None
    result = key_from_cc_url(cleaned)
    if not result:
        return None
    vk, nk, url = result
    if vk in VERSION_REGISTRY:
        return make(vk)
    return make_synthetic(vk, url, nk)


def step_prose(cleaned: str) -> Optional[str]:
    """Step 5: prose keyword scan.

    Only attempted when ``len(cleaned) >= _PROSE_MIN_LEN``.
    Returns the first matching version key that exists in
    :data:`~._registry.VERSION_REGISTRY`, or ``None``.
    """
    if len(cleaned) < _PROSE_MIN_LEN:
        return None
    for pattern, vkey in _PROSE_PATTERNS:
        if pattern.search(cleaned) and vkey in VERSION_REGISTRY:
            return vkey
    return None


def step_fallback(cleaned: str) -> LicenseVersion:
    """Step 6: always matches; returns an unknown LicenseVersion."""
    return make_unknown(cleaned)
