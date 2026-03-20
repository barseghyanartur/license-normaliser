"""Public exceptions for better control flow."""

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("LicenseNormalisationError",)


class LicenseNormalisationError(ValueError):
    """Raised when ``strict=True`` and no canonical license could be resolved."""

    pass
