"""Licence Normaliser - public orchestration shim."""

from __future__ import annotations

from ._cache import normalise_licence, normalise_licences
from ._models import LicenceFamily, LicenceName, LicenceVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenceFamily",
    "LicenceName",
    "LicenceVersion",
    "normalise_licence",
    "normalise_licences",
)
