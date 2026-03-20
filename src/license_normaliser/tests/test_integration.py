"""Integration tests - public API only. Survives any internal rewrite."""

import pytest

from license_normaliser import (
    LicenseNormalisationError,
    LicenseNotFoundError,
    LicenseVersion,
    normalise_license,
    normalise_licenses,
)


def test_normalise_mit():
    v = normalise_license("MIT")
    assert isinstance(v, LicenseVersion)
    assert v.key == "mit"
    assert str(v) == "mit"
    assert str(v.license) == "mit"


def test_normalise_cc():
    v = normalise_license("CC BY 4.0")
    assert v.key == "cc-by-4.0"
    assert str(v.license) == "cc-by"
    assert str(v.family) == "cc"


def test_batch():
    results = normalise_licenses(["MIT", "Apache-2.0"])
    assert len(results) == 2
    assert results[0].key == "mit"
    assert results[1].key == "apache-2.0"


def test_strict_mode_raises():
    with pytest.raises((LicenseNormalisationError, LicenseNotFoundError)):
        normalise_license("Totally Fake License XYZ999", strict=True)


def test_strict_batch_raises():
    with pytest.raises((LicenseNormalisationError, LicenseNotFoundError)):
        normalise_licenses(["MIT", "Fake License XYZ999"], strict=True)


def test_empty_input():
    v = normalise_license("")
    assert v.key == "unknown"
    v = normalise_license("   ")
    assert v.key == "unknown"
