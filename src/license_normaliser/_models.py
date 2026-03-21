"""License data models - frozen dataclasses for the three-level hierarchy."""

from __future__ import annotations

from dataclasses import dataclass
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
