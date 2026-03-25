"""Unit tests for _models.py."""

import pytest

from licence_normaliser._models import LicenceFamily, LicenceName, LicenceVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


def _cc_fam():
    return LicenceFamily(key="cc")


def _osi_fam():
    return LicenceFamily(key="osi")


def _cc_by_name():
    return LicenceName(key="cc-by", family=_cc_fam())


def _mit_version():
    return LicenceVersion(
        key="mit",
        url="https://opensource.org/licenses/MIT",
        licence=LicenceName(key="mit", family=_osi_fam()),
    )


class TestLicenceFamily:
    def test_str(self):
        assert str(LicenceFamily(key="cc")) == "cc"

    def test_repr(self):
        assert repr(LicenceFamily(key="osi")) == "LicenceFamily('osi')"

    def test_eq_same_type(self):
        assert LicenceFamily(key="cc") == LicenceFamily(key="cc")

    def test_eq_str(self):
        assert LicenceFamily(key="cc") == "cc"

    def test_neq(self):
        assert LicenceFamily(key="cc") != LicenceFamily(key="osi")

    def test_hash_usable_in_set(self):
        s = {LicenceFamily(key="cc"), LicenceFamily(key="cc"), LicenceFamily(key="osi")}
        assert len(s) == 2

    def test_frozen_prevents_mutation(self):
        fam = LicenceFamily(key="cc")
        with pytest.raises((AttributeError, TypeError)):
            fam.key = "other"  # type: ignore


class TestLicenceName:
    def test_str(self):
        assert str(_cc_by_name()) == "cc-by"

    def test_frozen_prevents_mutation(self):
        name = _cc_by_name()
        with pytest.raises((AttributeError, TypeError)):
            name.key = "other"  # type: ignore

    def test_family_reference(self):
        assert _cc_by_name().family.key == "cc"


class TestLicenceVersion:
    def test_str(self):
        assert str(_mit_version()) == "mit"

    def test_family_shortcut(self):
        assert _mit_version().family.key == "osi"

    def test_frozen_prevents_mutation(self):
        v = _mit_version()
        with pytest.raises((AttributeError, TypeError)):
            v.key = "other"  # type: ignore

    def test_url_stored(self):
        assert _mit_version().url == "https://opensource.org/licenses/MIT"

    def test_url_none(self):
        v = LicenceVersion(
            key="unknown",
            url=None,
            licence=LicenceName(key="unknown", family=LicenceFamily(key="unknown")),
        )
        assert v.url is None
