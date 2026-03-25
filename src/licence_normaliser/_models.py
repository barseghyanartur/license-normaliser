"""Licence data models - frozen dataclasses for the three-level hierarchy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from licence_normaliser._trace import _should_trace

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenceFamily",
    "LicenceName",
    "LicenceVersion",
)


@dataclass(frozen=True, slots=True)
class LicenceFamily:
    key: str

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"LicenceFamily({self.key!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenceFamily):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)


@dataclass(frozen=True, slots=True)
class LicenceName:
    key: str
    family: LicenceFamily

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"LicenceName({self.key!r}, family={self.family.key!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenceName):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)


@dataclass(frozen=True, slots=True)
class LicenceVersion:
    key: str
    url: Optional[str]
    licence: LicenceName
    _trace: Optional[object] = field(default=None, repr=False)

    @property
    def family(self) -> LicenceFamily:
        return self.licence.family

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return (
            f"LicenceVersion(key={self.key!r}, "
            f"licence={self.licence.key!r}, "
            f"family={self.licence.family.key!r})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenceVersion):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    def explain(self) -> str:
        """Return explanation of how this licence was resolved.

        Set ENABLE_LICENCE_NORMALISER_TRACE=1 to enable tracing,
        or pass trace=True to normalise_licence().
        """
        if self._trace is not None:
            return str(self._trace)

        # Lazy import to avoid circular import: _models -> _cache -> _models
        from licence_normaliser._cache import _default

        if not _should_trace():
            return "Trace disabled. Set ENABLE_LICENCE_NORMALISER_TRACE=1 to enable."

        ln = _default.get()
        cleaned = ln._clean(ln._try_decode_mojibake(self.key))
        result = ln._resolve_with_trace(self.key, cleaned, strict=False)
        trace = result._trace
        return str(trace) if trace else "No trace available."
