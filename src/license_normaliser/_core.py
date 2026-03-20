"""License Normaliser - public orchestration shim."""

from __future__ import annotations

from ._cache import normalise_license, normalise_licenses
from ._models import LicenseFamily, LicenseName, LicenseVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
    "normalise_license",
    "normalise_licenses",
)
