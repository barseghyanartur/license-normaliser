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


def test_real_world_license_strings():
    """Test against real-world license strings collected from the wild."""
    cases = [
        ("http://creativecommons.org/licenses/by-nc-nd/4.0/", "cc-by-nc-nd-4.0"),
        ("http://creativecommons.org/licenses/by/4.0/", "cc-by-4.0"),
        ("http://creativecommons.org/licenses/by-nc/4.0/", "cc-by-nc-4.0"),
        (
            "http://www.elsevier.com/open-access/userlicense/1.0/",
            "http://www.elsevier.com/open-access/userlicense/1.0",
        ),
        (
            "http://creativecommons.org/licenses/by-nc-nd/3.0/igo/",
            "cc-by-nc-nd-3.0-igo",
        ),
        ("CC BY-NC-ND 4.0", "cc-by-nc-nd-4.0"),
        (
            "http://creativecommons.org/licenses/by/3.0/igo/",
            "cc-by-3.0-igo",
        ),
    ]
    for raw, expected_key in cases:
        v = normalise_license(raw)
        assert v.key == expected_key, (
            f"input: {raw!r} -> got {v.key!r}, want {expected_key!r}"
        )
