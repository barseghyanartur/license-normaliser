"""license_normaliser - License normalisation with a three-level hierarchy."""

from ._core import (
    LicenseFamily,
    LicenseName,
    LicenseVersion,
    normalise_license,
    normalise_licenses,
)
from .exceptions import LicenseNormalisationError, LicenseNotFoundError

__title__ = "license-normaliser"
__version__ = "0.2"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
    "LicenseNormalisationError",
    "LicenseNotFoundError",
    "normalise_license",
    "normalise_licenses",
)
