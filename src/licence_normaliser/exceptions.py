"""licence_normaliser.exceptions - public exception hierarchy.

These are the only exceptions that cross the public API boundary.
All internal errors are wrapped before propagation.
"""

from __future__ import annotations

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "DataSourceError",
    "LicenceNormalisationError",
    "LicenceNormaliserError",
    "LicenceNotFoundError",
)


class LicenceNormaliserError(Exception):
    """Base exception for all licence-normaliser errors."""


class LicenceNotFoundError(LicenceNormaliserError):
    """Raised in strict mode when a licence string cannot be resolved."""

    def __init__(self, raw: str, cleaned: str) -> None:
        self.raw = raw
        self.cleaned = cleaned
        super().__init__(
            f"Licence not found: {raw!r} (cleaned: {cleaned!r}). "
            "Pass strict=False to return an 'unknown' result instead."
        )


class DataSourceError(LicenceNormaliserError):
    """Raised when a data source file cannot be loaded or parsed."""


class LicenceNormalisationError(LicenceNormaliserError):
    """Raised when licence normalisation fails.

    .. deprecated::
        Use :class:`LicenceNotFoundError` instead. This exception is kept for
        backwards compatibility but is no longer raised by the library.
    """
