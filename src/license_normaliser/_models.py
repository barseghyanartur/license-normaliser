"""License data models - frozen dataclasses for the three-level hierarchy.

All three classes are frozen (and therefore hashable and safely cacheable).
No resolution logic lives here - only structure and convenience properties.
"""

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

# ---------------------------------------------------------------------------
# Reverse-lookup dicts (built once at import time)
# ---------------------------------------------------------------------------

_FAMILY_ENUMS: dict[str, LicenseFamilyEnum] = {e.value: e for e in LicenseFamilyEnum}
_NAME_ENUMS: dict[str, LicenseNameEnum] = {e.value: e for e in LicenseNameEnum}
_VERSION_ENUMS: dict[str, LicenseVersionEnum] = {e.value: e for e in LicenseVersionEnum}


# ===========================================================================
# Level 1 - LicenseFamily
# ===========================================================================


@dataclass(frozen=True, slots=True)
class LicenseFamily:
    """License family - broad bucket like 'cc', 'osi', 'copyleft'."""

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
        """Return the corresponding enum value, or None if not recognised."""
        return _FAMILY_ENUMS.get(self.key)


# Pre-built singletons - one object per known family, reused everywhere.
_FAMILIES: dict[str, LicenseFamily] = {
    e.value: LicenseFamily(key=e.value) for e in LicenseFamilyEnum
}


def _fam(key: str) -> LicenseFamily:
    """Return a LicenseFamily singleton by key, falling back to 'unknown'."""
    return _FAMILIES.get(key, _FAMILIES["unknown"])


# ===========================================================================
# Level 2 - LicenseName
# ===========================================================================


@dataclass(frozen=True, slots=True)
class LicenseName:
    """License name - version-free, like 'cc-by' or 'mit'."""

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
        """Return the corresponding enum value, or None if not recognised."""
        return _NAME_ENUMS.get(self.key)


# ===========================================================================
# Level 3 - LicenseVersion
# ===========================================================================


@dataclass(frozen=True, slots=True)
class LicenseVersion:
    """Fully-resolved leaf node - like 'cc-by-4.0'.

    All construction goes through :mod:`_registry` factory functions so the
    key is guaranteed to be already lowercase.  The class itself does not
    mutate or clean the key.
    """

    key: str
    url: Optional[str]
    license: LicenseName

    @property
    def family(self) -> LicenseFamily:
        """Shortcut: ``version.family == version.license.family``."""
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
        """Return the corresponding enum value, or None if not recognised."""
        return _VERSION_ENUMS.get(self.key)

    def is_family(self, family: LicenseFamilyEnum) -> bool:
        """Return True if this license belongs to the given family."""
        return self.family.key == family.value

    def is_name(self, name: LicenseNameEnum) -> bool:
        """Return True if this license matches the given name."""
        return self.license.key == name.value

    def is_version(self, version: LicenseVersionEnum) -> bool:
        """Return True if this license matches the given version."""
        return self.key == version.value
