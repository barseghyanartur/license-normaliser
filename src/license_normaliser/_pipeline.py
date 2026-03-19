"""Resolution pipeline - six steps, first match wins.

The pipeline is identical in structure to the original but sources its
alias, URL, and prose data from the registry which now loads from data files
instead of hard-coded dicts.

Steps
-----
1. ``step_direct``   - direct hit in :data:`~._registry.VERSION_REGISTRY`
2. ``step_alias``    - hit in :data:`~._registry.ALIASES`
3. ``step_url``      - hit in :data:`~._registry.URL_MAP` after URL normalisation
4. ``step_cc_regex`` - structural parse of any creativecommons.org URL
5. ``step_prose``    - keyword scan using :data:`~._registry.PROSE_PATTERNS`
6. ``step_fallback`` - always matches; returns an unknown LicenseVersion
"""

from __future__ import annotations

from typing import Optional

from ._models import LicenseVersion
from ._registry import (
    ALIASES,
    PROSE_PATTERNS,
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
_PROSE_MIN_LEN: int = 20


def _normalise_url_for_lookup(cleaned: str) -> str:
    if cleaned.startswith("http://"):
        cleaned = "https://" + cleaned[len("http://") :]
    return cleaned.rstrip("/").lower()


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
    """Step 3: exact URL map lookup."""
    normalised = _normalise_url_for_lookup(cleaned)
    return URL_MAP.get(normalised)


def step_cc_regex(cleaned: str) -> Optional[LicenseVersion]:
    """Step 4: structural CC URL regex."""
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
    """Step 5: prose keyword scan using compiled patterns from data sources."""
    if len(cleaned) < _PROSE_MIN_LEN:
        return None
    for pattern, vkey in PROSE_PATTERNS:
        if pattern.search(cleaned) and vkey in VERSION_REGISTRY:
            return vkey
    return None


def step_fallback(cleaned: str) -> LicenseVersion:
    """Step 6: always matches; returns an unknown LicenseVersion."""
    return make_unknown(cleaned)
