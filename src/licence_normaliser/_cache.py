"""Caching layer + strict mode - delegates to LicenceNormaliser with defaults."""

from __future__ import annotations

from threading import Lock
from typing import Iterable

from ._models import LicenceVersion
from ._normaliser import LicenceNormaliser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "_default",
    "get_registry_keys",
    "normalise_licence",
    "normalise_licences",
)


class _DefaultNormaliser:
    """Thread-safe lazy singleton for the default LicenceNormaliser instance."""

    _instance: LicenceNormaliser | None = None
    _lock: Lock = Lock()

    def get(self) -> LicenceNormaliser:
        if _DefaultNormaliser._instance is None:
            with _DefaultNormaliser._lock:
                if _DefaultNormaliser._instance is None:
                    _DefaultNormaliser._instance = LicenceNormaliser()
        return _DefaultNormaliser._instance


_default = _DefaultNormaliser()


def normalise_licence(
    raw: str, *, strict: bool = False, trace: bool | None = None
) -> LicenceVersion:
    """Public API with optional strict mode and trace."""
    return _default.get().normalise_licence(raw, strict=strict, trace=trace)


def normalise_licences(
    raws: Iterable[str], *, strict: bool = False, trace: bool | None = None
) -> list[LicenceVersion]:
    """Batch version with optional trace."""
    return _default.get().normalise_licences(raws, strict=strict, trace=trace)


def get_registry_keys() -> set[str]:
    """Return the set of all known registry keys from the runtime normaliser."""
    return _default.get().registry_keys()
