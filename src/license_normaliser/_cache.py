"""Caching layer + strict mode."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

from ._models import LicenseVersion
from ._registry import ALIASES, REGISTRY, URL_MAP, make, make_unknown
from .exceptions import LicenseNotFoundError

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("normalise_license", "normalise_licenses")


_WHITESPACE_RE = re.compile(r"\s+")
_MAX_INPUT = 4096


def _clean(raw: str) -> str:
    s = _WHITESPACE_RE.sub(" ", raw.strip().rstrip("/")).lower()
    return s[:_MAX_INPUT]


def _try_decode_mojibake(s: str) -> str:
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _normalise_url(cleaned: str) -> str:
    key = cleaned.lower()
    if key.startswith("http://"):
        key = "https://" + key[7:]
    return key.rstrip("/")


@lru_cache(maxsize=8192)
def _resolve(cleaned: str) -> LicenseVersion:
    if cleaned in REGISTRY:
        return make(cleaned)
    if cleaned in ALIASES:
        return make(ALIASES[cleaned])
    url_key = _normalise_url(cleaned)
    if url_key in URL_MAP:
        return make(URL_MAP[url_key])
    return make_unknown(cleaned)


@lru_cache(maxsize=8192)
def normalise_license(raw: str, *, strict: bool = False) -> LicenseVersion:
    """Public API with optional strict mode."""
    if not raw or not raw.strip():
        v = make_unknown("unknown")
    else:
        v = _resolve(_clean(_try_decode_mojibake(raw)))

    if strict and v.family.key == "unknown":
        raise LicenseNotFoundError(raw, v.key) from None
    return v


def normalise_licenses(
    raws: Iterable[str], *, strict: bool = False
) -> list[LicenseVersion]:
    """Batch version."""
    return [normalise_license(r, strict=strict) for r in raws]
