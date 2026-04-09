"""licence_normaliser - License normalisation with a three-level hierarchy."""

from ._core import (
    LicenceFamily,
    LicenceName,
    LicenceVersion,
    normalise_licence,
    normalise_licences,
)
from ._normaliser import LicenceNormaliser
from ._trace import LicenceTrace, LicenceTraceStage
from .exceptions import (
    DataSourceError,
    LicenceNormalisationError,
    LicenceNotFoundError,
)

__title__ = "licence-normaliser"
__version__ = "0.5.2"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

__all__ = (
    "DataSourceError",
    "LicenceFamily",
    "LicenceName",
    "LicenceVersion",
    "LicenceNormaliser",
    "LicenceNormalisationError",
    "LicenceNotFoundError",
    "LicenceTrace",
    "LicenceTraceStage",
    "normalise_licence",
    "normalise_licences",
)
