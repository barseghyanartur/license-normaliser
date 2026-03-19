"""License data models - frozen dataclasses for the three-level hierarchy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ._enums import LicenseFamilyEnum, LicenseNameEnum, LicenseVersionEnum

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
)

_FAMILY_ENUMS: dict[str, LicenseFamilyEnum] = {e.value: e for e in LicenseFamilyEnum}
_NAME_ENUMS: dict[str, LicenseNameEnum] = {e.value: e for e in LicenseNameEnum}
_VERSION_ENUMS: dict[str, LicenseVersionEnum] = {e.value: e for e in LicenseVersionEnum}


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
        if isinstance(other, LicenseFamilyEnum):
            return self.key == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def enum(self) -> Optional[LicenseFamilyEnum]:
        return _FAMILY_ENUMS.get(self.key)


_FAMILIES: dict[str, LicenseFamily] = {
    e.value: LicenseFamily(key=e.value) for e in LicenseFamilyEnum
}


def _fam(key: str) -> LicenseFamily:
    return _FAMILIES.get(key, _FAMILIES["unknown"])


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
        if isinstance(other, LicenseNameEnum):
            return self.key == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def enum(self) -> Optional[LicenseNameEnum]:
        return _NAME_ENUMS.get(self.key)


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
        if isinstance(other, LicenseVersionEnum):
            return self.key == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def enum(self) -> Optional[LicenseVersionEnum]:
        return _VERSION_ENUMS.get(self.key)

    def is_family(self, family: LicenseFamilyEnum) -> bool:
        return self.family.key == family.value

    def is_name(self, name: LicenseNameEnum) -> bool:
        return self.license.key == name.value

    def is_version(self, version: LicenseVersionEnum) -> bool:
        return self.key == version.value
