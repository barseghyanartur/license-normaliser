"""Unit tests for _models.py."""

import pytest

from licence_normaliser._models import LicenceFamily, LicenceName, LicenceVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


def _cc_fam() -> LicenceFamily:
    return LicenceFamily(key="cc")


def _osi_fam() -> LicenceFamily:
    return LicenceFamily(key="osi")


def _cc_by_name() -> LicenceName:
    return LicenceName(key="cc-by", family=_cc_fam())


def _mit_version() -> LicenceVersion:
    return LicenceVersion(
        key="mit",
        url="https://opensource.org/licenses/MIT",
        licence=LicenceName(key="mit", family=_osi_fam()),
    )


class TestLicenceFamily:
    def test_str(self) -> None:
        assert str(LicenceFamily(key="cc")) == "cc"

    def test_repr(self) -> None:
        assert repr(LicenceFamily(key="osi")) == "LicenceFamily('osi')"

    def test_eq_same_type(self) -> None:
        assert LicenceFamily(key="cc") == LicenceFamily(key="cc")

    def test_eq_str(self) -> None:
        assert LicenceFamily(key="cc") == "cc"

    def test_neq(self) -> None:
        assert LicenceFamily(key="cc") != LicenceFamily(key="osi")

    def test_hash_usable_in_set(self) -> None:
        s = {LicenceFamily(key="cc"), LicenceFamily(key="cc"), LicenceFamily(key="osi")}
        assert len(s) == 2

    def test_frozen_prevents_mutation(self) -> None:
        fam = LicenceFamily(key="cc")
        with pytest.raises((AttributeError, TypeError)):
            fam.key = "other"  # type: ignore


class TestLicenceName:
    def test_str(self) -> None:
        assert str(_cc_by_name()) == "cc-by"

    def test_frozen_prevents_mutation(self) -> None:
        name = _cc_by_name()
        with pytest.raises((AttributeError, TypeError)):
            name.key = "other"  # type: ignore

    def test_family_reference(self) -> None:
        assert _cc_by_name().family.key == "cc"


class TestLicenceVersion:
    def test_str(self) -> None:
        assert str(_mit_version()) == "mit"

    def test_family_shortcut(self) -> None:
        assert _mit_version().family.key == "osi"

    def test_frozen_prevents_mutation(self) -> None:
        v = _mit_version()
        with pytest.raises((AttributeError, TypeError)):
            v.key = "other"  # type: ignore

    def test_url_stored(self) -> None:
        assert _mit_version().url == "https://opensource.org/licenses/MIT"

    def test_url_none(self) -> None:
        v = LicenceVersion(
            key="unknown",
            url=None,
            licence=LicenceName(key="unknown", family=LicenceFamily(key="unknown")),
        )
        assert v.url is None


class TestLicenceVersionEquality:
    def test_eq_same_key(self) -> None:
        v1 = _mit_version()
        v2 = LicenceVersion(
            key="mit",
            url=None,
            licence=LicenceName(key="mit", family=LicenceFamily(key="osi")),
        )
        assert v1 == v2

    def test_eq_string(self) -> None:
        v = _mit_version()
        assert v == "mit"

    def test_neq_different_key(self) -> None:
        v1 = _mit_version()
        v2 = LicenceVersion(
            key="apache-2.0",
            url=None,
            licence=LicenceName(key="apache", family=LicenceFamily(key="osi")),
        )
        assert v1 != v2

    def test_eq_other_type_returns_notimplemented(self) -> None:
        v = _mit_version()
        result = v.__eq__(123)
        assert result == NotImplemented

    def test_hash_same_key(self) -> None:
        v1 = _mit_version()
        v2 = LicenceVersion(
            key="mit",
            url="different-url",
            licence=LicenceName(key="mit", family=LicenceFamily(key="osi")),
        )
        assert hash(v1) == hash(v2)

    def test_hash_usable_in_set(self) -> None:
        v1 = _mit_version()
        v2 = LicenceVersion(
            key="mit",
            url=None,
            licence=LicenceName(key="mit", family=LicenceFamily(key="osi")),
        )
        s = {v1, v2}
        assert len(s) == 1
