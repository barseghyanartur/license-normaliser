"""license_normaliser.exceptions - public exception hierarchy.

These are the only exceptions that cross the public API boundary.
All internal errors are wrapped before propagation.
"""

from __future__ import annotations

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "DataSourceError",
    "LicenseNormalisationError",
    "LicenseNormaliserError",
    "LicenseNotFoundError",
)


class LicenseNormaliserError(Exception):
    """Base exception for all license-normaliser errors."""


class LicenseNotFoundError(LicenseNormaliserError):
    """Raised in strict mode when a license string cannot be resolved."""

    def __init__(self, raw: str, cleaned: str) -> None:
        self.raw = raw
        self.cleaned = cleaned
        super().__init__(
            f"License not found: {raw!r} (cleaned: {cleaned!r}). "
            "Pass strict=False to return an 'unknown' result instead."
        )


class DataSourceError(LicenseNormaliserError):
    """Raised when a data source file cannot be loaded or parsed."""


class LicenseNormalisationError(ValueError):
    """Raised when ``strict=True`` and no canonical license could be resolved."""
