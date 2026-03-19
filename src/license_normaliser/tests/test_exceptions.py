"""Tests for strict mode and the public exception hierarchy."""

import pytest

from license_normaliser import normalise_license, normalise_licenses
from license_normaliser.exceptions import (
    LicenseNormaliserError,
    LicenseNotFoundError,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestLicenseNotFoundError:
    def test_is_subclass_of_base(self):
        assert issubclass(LicenseNotFoundError, LicenseNormaliserError)

    def test_is_subclass_of_exception(self):
        assert issubclass(LicenseNotFoundError, Exception)

    def test_attributes(self):
        exc = LicenseNotFoundError("My License", "my license")
        assert exc.raw == "My License"
        assert exc.cleaned == "my license"

    def test_str_contains_raw(self):
        exc = LicenseNotFoundError("My License", "my license")
        assert "My License" in str(exc)

    def test_str_mentions_strict_false(self):
        exc = LicenseNotFoundError("x", "x")
        assert "strict=False" in str(exc)


class TestStrictModeNormalise:
    def test_known_license_no_raise(self):
        # Known licenses must not raise in strict mode
        v = normalise_license("MIT", strict=True)
        assert v.key == "mit"

    def test_unknown_raises_license_not_found(self):
        with pytest.raises(LicenseNotFoundError) as exc_info:
            normalise_license("totally-unknown-xyz-9999", strict=True)
        assert exc_info.value.raw == "totally-unknown-xyz-9999"
        assert exc_info.value.cleaned == "totally-unknown-xyz-9999"

    def test_empty_string_raises(self):
        with pytest.raises(LicenseNotFoundError):
            normalise_license("", strict=True)

    def test_whitespace_only_raises(self):
        with pytest.raises(LicenseNotFoundError):
            normalise_license("   ", strict=True)

    def test_cc_url_known_no_raise(self):
        v = normalise_license(
            "https://creativecommons.org/licenses/by/4.0/", strict=True
        )
        assert v.key == "cc-by-4.0"

    def test_strict_false_unknown_returns_unknown(self):
        # Default (strict=False): silently returns unknown
        v = normalise_license("no-such-license-xyzzy", strict=False)
        assert v.family.key == "unknown"

    def test_strict_default_is_false(self):
        # Calling without strict kwarg should not raise
        v = normalise_license("no-such-license-xyzzy")
        assert v.family.key == "unknown"

    def test_known_publisher_license_no_raise(self):
        v = normalise_license("elsevier-tdm", strict=True)
        assert v.key == "elsevier-tdm"


class TestStrictModeBatch:
    def test_all_known_no_raise(self):
        results = normalise_licenses(["MIT", "Apache-2.0"], strict=True)
        assert len(results) == 2
        assert results[0].key == "mit"
        assert results[1].key == "apache-2.0"

    def test_one_unknown_raises(self):
        with pytest.raises(LicenseNotFoundError):
            normalise_licenses(["MIT", "no-such-license-xyz"], strict=True)

    def test_non_strict_batch_with_unknown(self):
        results = normalise_licenses(["MIT", "no-such-license-xyz"], strict=False)
        assert results[0].key == "mit"
        assert results[1].family.key == "unknown"

    def test_empty_batch_strict(self):
        # Empty input should not raise even in strict mode
        assert normalise_licenses([], strict=True) == []
