"""Caching layer + strict mode - delegates to LicenseNormaliser with defaults."""

from __future__ import annotations

from threading import Lock
from typing import Iterable

from ._models import LicenseVersion
from ._normaliser import LicenseNormaliser
from .defaults import (
    get_default_alias,
    get_default_family,
    get_default_name,
    get_default_prose,
    get_default_registry,
    get_default_url,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("normalise_license", "normalise_licenses", "get_registry_keys")


class _DefaultNormaliser:
    """Thread-safe lazy singleton for the default LicenseNormaliser instance."""

    _instance: LicenseNormaliser | None = None
    _lock: Lock = Lock()

    def get(self) -> LicenseNormaliser:
        if _DefaultNormaliser._instance is None:
            with _DefaultNormaliser._lock:
                if _DefaultNormaliser._instance is None:
                    _DefaultNormaliser._instance = LicenseNormaliser(
                        registry=get_default_registry(),
                        url=get_default_url(),
                        alias=get_default_alias(),
                        family=get_default_family(),
                        name=get_default_name(),
                        prose=get_default_prose(),
                    )
        return _DefaultNormaliser._instance


_default = _DefaultNormaliser()


def normalise_license(raw: str, *, strict: bool = False) -> LicenseVersion:
    """Public API with optional strict mode."""
    return _default.get().normalise_license(raw, strict=strict)


def normalise_licenses(
    raws: Iterable[str], *, strict: bool = False
) -> list[LicenseVersion]:
    """Batch version."""
    return _default.get().normalise_licenses(raws, strict=strict)


def get_registry_keys() -> set[str]:
    """Return the set of all known registry keys from the runtime normaliser."""
    return set(_default.get()._registry.keys())
