"""license_normaliser - License normalisation with a three-level hierarchy."""

from ._core import (
    LicenseFamily,
    LicenseName,
    LicenseVersion,
    normalise_license,
    normalise_licenses,
)
from ._normaliser import LicenseNormaliser
from ._trace import LicenseTrace, LicenseTraceStage
from .exceptions import LicenseNormalisationError, LicenseNotFoundError

__title__ = "license-normaliser"
__version__ = "0.3.1"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
    "LicenseNormaliser",
    "LicenseNormalisationError",
    "LicenseNotFoundError",
    "LicenseTrace",
    "LicenseTraceStage",
    "normalise_license",
    "normalise_licenses",
)
