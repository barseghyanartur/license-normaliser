"""Caching layer for the normalisation pipeline.

The public entry point is :func:`normalise_license_cached`.  It wraps the
pipeline so that the cache key is the *cleaned* string, not the raw input.
This means whitespace variants such as ``"MIT"``, ``"MIT "`` and ``"  MIT  "``
all share a single cache slot.

The cleaning and dispatch logic is split across two functions so that
``lru_cache`` only decorates the inner one - keeping the cache keyed on
the normalised form.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

from ._models import LicenseVersion
from ._pipeline import (
    step_alias,
    step_cc_regex,
    step_direct,
    step_fallback,
    step_prose,
    step_url,
)
from ._registry import make

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "normalise_license_cached",
    "normalise_licenses",
)

# ---------------------------------------------------------------------------
# Input cleaning
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s+")
_MAX_INPUT = 4096  # guard against pathological inputs


def _clean(raw: str) -> str:
    """Normalise whitespace, strip trailing slash, lowercase, cap length."""
    s = _WHITESPACE_RE.sub(" ", raw.strip().rstrip("/")).lower()
    return s[:_MAX_INPUT]


def _try_decode_mojibake(s: str) -> str:
    """Attempt to fix common latin-1/utf-8 mojibake (e.g. Â© -> ©).

    Returns the decoded string on success, or the original string on failure.
    This is a no-op for any string that cannot be round-tripped through
    latin-1 encoding (i.e. normal ASCII and properly-encoded UTF-8).
    """
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


# ---------------------------------------------------------------------------
# Cached inner resolver
# ---------------------------------------------------------------------------


@lru_cache(maxsize=8192)
def _resolve(cleaned: str) -> LicenseVersion:
    """Run the six-step pipeline on an already-cleaned string.

    This is the function that is actually cached.  All callers must pass a
    cleaned string (output of :func:`_clean`).
    """
    # Step 1 - direct registry hit
    if key := step_direct(cleaned):
        return make(key)

    # Step 2 - alias table
    if key := step_alias(cleaned):
        return make(key)

    # Step 3 - exact URL map (scheme-normalised, trailing-slash stripped)
    if key := step_url(cleaned):
        return make(key)

    # Step 4 - structural CC URL regex
    if result := step_cc_regex(cleaned):
        return result

    # Step 5 - prose keyword scan (long strings only)
    if key := step_prose(cleaned):
        return make(key)

    # Step 6 - fallback
    return step_fallback(cleaned)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalise_license_cached(raw: str) -> LicenseVersion:
    """Normalise *raw* to a :class:`~._models.LicenseVersion`, with caching.

    Empty / whitespace-only inputs immediately return the ``"unknown"``
    version without entering the cache.

    Mojibake decoding is attempted on the *raw* string before cleaning,
    because ``_clean`` calls ``.lower()`` which changes the code-point values
    of high Latin-1 characters and makes post-clean detection unreliable.
    """
    if not raw or not raw.strip():
        return make("unknown")

    # Attempt mojibake fix on the raw string BEFORE cleaning.
    # _try_decode_mojibake is a no-op for normal ASCII/UTF-8 input.
    raw = _try_decode_mojibake(raw)

    return _resolve(_clean(raw))


def normalise_licenses(raws: Iterable[str]) -> list[LicenseVersion]:
    """Normalise an iterable of license strings."""
    return [normalise_license_cached(r) for r in raws]
