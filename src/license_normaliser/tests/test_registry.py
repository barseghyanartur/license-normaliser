"""Unit tests for _registry.py."""

import pytest

from license_normaliser._enums import LicenseNameEnum, LicenseVersionEnum
from license_normaliser._registry import (
    ALIASES,
    URL_MAP,
    VERSION_REGISTRY,
    key_from_cc_url,
    make,
    make_synthetic,
    make_unknown,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestVersionRegistry:
    def test_derived_from_enum_completeness(self):
        for e in LicenseVersionEnum:
            assert e.value in VERSION_REGISTRY, f"Missing: {e.value}"

    def test_url_and_name_stored(self):
        url, name_enum = VERSION_REGISTRY["cc-by-4.0"]
        assert url == "https://creativecommons.org/licenses/by/4.0/"
        assert name_enum is LicenseNameEnum.CC_BY

    def test_unknown_has_no_url(self):
        url, _ = VERSION_REGISTRY["unknown"]
        assert url is None


class TestAliases:
    def test_all_alias_targets_exist_in_registry(self):
        bad = {k: v for k, v in ALIASES.items() if v not in VERSION_REGISTRY}
        assert not bad, f"Alias targets missing from registry: {bad}"

    def test_apache_2_0_alias(self):
        assert ALIASES.get("apache 2.0") == "apache-2.0"

    def test_mit_license_alias(self):
        assert ALIASES.get("mit license") == "mit"

    def test_cc_by_4_0_alias(self):
        assert ALIASES.get("cc by 4.0") == "cc-by-4.0"


class TestUrlMap:
    def test_all_url_map_targets_exist_in_registry(self):
        bad = {k: v for k, v in URL_MAP.items() if v not in VERSION_REGISTRY}
        assert not bad, f"URL map targets missing from registry: {bad}"

    def test_canonical_cc_by_4_https(self):
        assert URL_MAP.get("https://creativecommons.org/licenses/by/4.0") == "cc-by-4.0"

    def test_no_http_keys(self):
        http_keys = [k for k in URL_MAP if k.startswith("http://")]
        assert not http_keys

    def test_no_trailing_slash_keys(self):
        trailing = [k for k in URL_MAP if k.endswith("/")]
        assert not trailing


class TestKeyFromCcUrl:
    def test_by_4_0(self):
        result = key_from_cc_url("https://creativecommons.org/licenses/by/4.0/")
        assert result is not None
        vk, nk, url = result
        assert vk == "cc-by-4.0"
        assert nk == "cc-by"

    def test_igo_variant(self):
        result = key_from_cc_url(
            "https://creativecommons.org/licenses/by-nc-sa/3.0/igo/"
        )
        assert result is not None
        assert result[0] == "cc-by-nc-sa-3.0-igo"

    def test_cc_zero(self):
        result = key_from_cc_url("https://creativecommons.org/publicdomain/zero/1.0/")
        assert result is not None
        assert result[0] == "cc0"

    def test_non_cc_url_returns_none(self):
        assert key_from_cc_url("https://opensource.org/licenses/MIT") is None


class TestMake:
    def test_make_known_key(self):
        v = make("mit")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_make_unknown_key_raises(self):
        with pytest.raises(KeyError):
            make("this-key-does-not-exist")


class TestMakeUnknown:
    def test_key_preserved(self):
        assert make_unknown("some-exotic-token").key == "some-exotic-token"

    def test_url_is_none(self):
        assert make_unknown("xyz").url is None

    def test_family_is_unknown(self):
        assert make_unknown("xyz").family.key == "unknown"


class TestMakeSynthetic:
    def test_synthetic_cc_url(self):
        v = make_synthetic(
            "cc-by-2.0", "https://creativecommons.org/licenses/by/2.0/", "cc-by"
        )
        assert v.key == "cc-by-2.0"
        assert v.family.key == "cc"
