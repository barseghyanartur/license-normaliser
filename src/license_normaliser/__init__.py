"""license_normaliser - Comprehensive license normalisation with a
three-level hierarchy."""

from ._core import (
    LicenseFamily,
    LicenseName,
    LicenseVersion,
    normalise_license,
    normalise_licenses,
)
from .exceptions import (
    DataSourceError,
    LicenseNormaliserError,
    LicenseNotFoundError,
)

__title__ = "license-normaliser"
__version__ = "0.2"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
    "LicenseNormaliserError",
    "LicenseNotFoundError",
    "DataSourceError",
    "__version__",
    "normalise_license",
    "normalise_licenses",
)
