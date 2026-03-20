"""license_normaliser - License normalisation with a three-level hierarchy."""

from ._core import (
    LicenseFamily,
    LicenseName,
    LicenseVersion,
    normalise_license,
    normalise_licenses,
)
from ._enums import LicenseFamilyEnum, LicenseNameEnum, LicenseVersionEnum
from ._exceptions import LicenseNormalisationError
from .exceptions import LicenseNotFoundError

__title__ = "license-normaliser"
__version__ = "0.3.0"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
    "LicenseFamilyEnum",
    "LicenseNameEnum",
    "LicenseVersionEnum",
    "LicenseNormalisationError",
    "LicenseNotFoundError",
    "normalise_license",
    "normalise_licenses",
)
