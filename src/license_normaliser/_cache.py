"""Caching layer for the normalisation pipeline.

This module wraps the six-step pipeline with LRU caching and exposes the
public ``normalise_license`` / ``normalise_licenses`` entry points.

Strict mode
-----------
Pass ``strict=True`` to raise :class:`~.exceptions.LicenseNotFoundError`
instead of returning an ``"unknown"`` result when the license string cannot
be resolved to any known version.

    >>> from license_normaliser import normalise_license
    >>> normalise_license("totally-unknown", strict=True)
    LicenseNotFoundError: License not found: 'totally-unknown' ...

The default (``strict=False``) preserves backwards-compatible behaviour.
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
from .exceptions import LicenseNotFoundError

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
_MAX_INPUT = 4096


def _clean(raw: str) -> str:
    """Normalise whitespace, strip trailing slash, lowercase, cap length."""
    s = _WHITESPACE_RE.sub(" ", raw.strip().rstrip("/")).lower()
    return s[:_MAX_INPUT]


def _try_decode_mojibake(s: str) -> str:
    """Attempt to fix common latin-1/utf-8 mojibake."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


# ---------------------------------------------------------------------------
# Cached inner resolver
# ---------------------------------------------------------------------------


@lru_cache(maxsize=8192)
def _resolve(cleaned: str) -> LicenseVersion:
    """Run the six-step pipeline on an already-cleaned string."""
    if key := step_direct(cleaned):
        return make(key)
    if key := step_alias(cleaned):
        return make(key)
    if key := step_url(cleaned):
        return make(key)
    if result := step_cc_regex(cleaned):
        return result
    if key := step_prose(cleaned):
        return make(key)
    return step_fallback(cleaned)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalise_license_cached(raw: str, *, strict: bool = False) -> LicenseVersion:
    """Normalise *raw* to a :class:`~._models.LicenseVersion`, with caching.

    Parameters
    ----------
    raw: str
        The license string to normalise.  May be an SPDX token, URL,
        prose description, or any other representation.
    strict: bool
        If ``True``, raise :class:`~.exceptions.LicenseNotFoundError` when
        the license cannot be resolved to a known version.
        If ``False`` (default), return an ``"unknown"`` version instead.

    Returns
    -------
    LicenseVersion
        The resolved license version.

    Raises
    ------
    LicenseNotFoundError
        When ``strict=True`` and the license cannot be resolved.
    """
    if not raw or not raw.strip():
        if strict:
            raise LicenseNotFoundError(raw, "")
        return make("unknown")

    raw = _try_decode_mojibake(raw)
    cleaned = _clean(raw)
    result = _resolve(cleaned)

    if strict and result.family.key == "unknown":
        raise LicenseNotFoundError(raw, cleaned)

    return result


def normalise_licenses(
    raws: Iterable[str],
    *,
    strict: bool = False,
) -> list[LicenseVersion]:
    """Normalise an iterable of license strings.

    Parameters
    ----------
    raws: Iterable[str]
        Iterable of raw license strings.
    strict: bool
        Forwarded to :func:`normalise_license_cached` for each entry.
        If ``True``, the first unresolvable license raises immediately.

    Returns
    -------
    list[LicenseVersion]
        Results in the same order as the input.
    """
    return [normalise_license_cached(r, strict=strict) for r in raws]
