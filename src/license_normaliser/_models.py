"""License data models - frozen dataclasses for the three-level hierarchy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
)


@dataclass(frozen=True, slots=True)
class LicenseFamily:
    key: str

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"LicenseFamily({self.key!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenseFamily):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)


@dataclass(frozen=True, slots=True)
class LicenseName:
    key: str
    family: LicenseFamily

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"LicenseName({self.key!r}, family={self.family.key!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenseName):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)


@dataclass(frozen=True, slots=True)
class LicenseVersion:
    key: str
    url: Optional[str]
    license: LicenseName
    _trace: Optional[object] = field(default=None, repr=False)

    @property
    def family(self) -> LicenseFamily:
        return self.license.family

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return (
            f"LicenseVersion(key={self.key!r}, "
            f"license={self.license.key!r}, "
            f"family={self.license.family.key!r})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenseVersion):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    def explain(self) -> str:
        """Return explanation of how this license was resolved.

        Set ENABLE_LICENSE_NORMALISER_TRACE=1 to enable tracing,
        or pass trace=True to normalise_license().
        """
        if self._trace is not None:
            return str(self._trace)

        from license_normaliser._cache import _default
        from license_normaliser._trace import _should_trace

        if not _should_trace():
            return "Trace disabled. Set ENABLE_LICENSE_NORMALISER_TRACE=1 to enable."

        ln = _default.get()
        cleaned = ln._clean(ln._try_decode_mojibake(self.key))
        result = ln._resolve_with_trace(self.key, cleaned, strict=False)
        trace = result._trace
        return str(trace) if trace else "No trace available."
