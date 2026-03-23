"""Caching layer + strict mode - delegates to LicenseNormaliser with defaults."""

from __future__ import annotations

from threading import Lock
from typing import Iterable

from ._models import LicenseVersion
from ._normaliser import LicenseNormaliser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "_default",
    "get_registry_keys",
    "normalise_license",
    "normalise_licenses",
)


class _DefaultNormaliser:
    """Thread-safe lazy singleton for the default LicenseNormaliser instance."""

    _instance: LicenseNormaliser | None = None
    _lock: Lock = Lock()

    def get(self) -> LicenseNormaliser:
        if _DefaultNormaliser._instance is None:
            with _DefaultNormaliser._lock:
                if _DefaultNormaliser._instance is None:
                    _DefaultNormaliser._instance = LicenseNormaliser()
        return _DefaultNormaliser._instance


_default = _DefaultNormaliser()


def normalise_license(
    raw: str, *, strict: bool = False, trace: bool | None = None
) -> LicenseVersion:
    """Public API with optional strict mode and trace."""
    return _default.get().normalise_license(raw, strict=strict, trace=trace)


def normalise_licenses(
    raws: Iterable[str], *, strict: bool = False, trace: bool | None = None
) -> list[LicenseVersion]:
    """Batch version with optional trace."""
    return _default.get().normalise_licenses(raws, strict=strict, trace=trace)


def get_registry_keys() -> set[str]:
    """Return the set of all known registry keys from the runtime normaliser."""
    return _default.get().registry_keys()
