"""Unit tests for _models.py."""

import pytest

from license_normaliser._models import LicenseFamily, LicenseName, LicenseVersion

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


def _cc_fam():
    return LicenseFamily(key="cc")


def _osi_fam():
    return LicenseFamily(key="osi")


def _cc_by_name():
    return LicenseName(key="cc-by", family=_cc_fam())


def _mit_version():
    return LicenseVersion(
        key="mit",
        url="https://opensource.org/licenses/MIT",
        license=LicenseName(key="mit", family=_osi_fam()),
    )


class TestLicenseFamily:
    def test_str(self):
        assert str(LicenseFamily(key="cc")) == "cc"

    def test_repr(self):
        assert repr(LicenseFamily(key="osi")) == "LicenseFamily('osi')"

    def test_eq_same_type(self):
        assert LicenseFamily(key="cc") == LicenseFamily(key="cc")

    def test_eq_str(self):
        assert LicenseFamily(key="cc") == "cc"

    def test_neq(self):
        assert LicenseFamily(key="cc") != LicenseFamily(key="osi")

    def test_hash_usable_in_set(self):
        s = {LicenseFamily(key="cc"), LicenseFamily(key="cc"), LicenseFamily(key="osi")}
        assert len(s) == 2

    def test_frozen_prevents_mutation(self):
        fam = LicenseFamily(key="cc")
        with pytest.raises((AttributeError, TypeError)):
            fam.key = "other"  # type: ignore


class TestLicenseName:
    def test_str(self):
        assert str(_cc_by_name()) == "cc-by"

    def test_frozen_prevents_mutation(self):
        name = _cc_by_name()
        with pytest.raises((AttributeError, TypeError)):
            name.key = "other"  # type: ignore

    def test_family_reference(self):
        assert _cc_by_name().family.key == "cc"


class TestLicenseVersion:
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
        v = LicenseVersion(
            key="unknown",
            url=None,
            license=LicenseName(key="unknown", family=LicenseFamily(key="unknown")),
        )
        assert v.url is None
