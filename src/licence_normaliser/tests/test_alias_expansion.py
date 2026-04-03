"""Tests for the aliases array expansion feature and the specific inputs
that previously fell through to the unknown fallback.

Covers:
- CC version-free hyphen-form keys (cc-by-nc, cc-by-nc-nd, etc.)
- CC space/mixed variants auto-resolved via aliases arrays
- GPL shorthand keys (gpl-2, gpl-3, gpl-v3, agpl-3, lgpl-3)
- Existing behaviour not regressed
"""

from __future__ import annotations

import pytest

from licence_normaliser import normalise_licence
from licence_normaliser.exceptions import LicenceNotFoundError
from licence_normaliser.parsers.alias import _iter_entries

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

# ---------------------------------------------------------------------------
# Unit tests for _iter_entries helper
# ---------------------------------------------------------------------------


class TestIterEntries:
    def test_primary_key_always_emitted(self):
        data = {
            "foo bar": {
                "version_key": "foo-bar",
                "name_key": "foo-bar",
                "family_key": "x",
            }
        }
        results = dict(_iter_entries(data))
        assert "foo bar" in results

    def test_aliases_expanded(self):
        data = {
            "foo bar": {
                "version_key": "foo-bar",
                "name_key": "foo-bar",
                "family_key": "x",
                "aliases": ["foo-bar", "foo_bar"],
            }
        }
        results = dict(_iter_entries(data))
        assert "foo bar" in results
        assert "foo-bar" in results
        assert "foo_bar" in results
        # All share the same version_key
        for key in ("foo bar", "foo-bar", "foo_bar"):
            assert results[key]["version_key"] == "foo-bar"

    def test_duplicate_primary_not_re_emitted(self):
        data = {
            "foo bar": {
                "version_key": "foo-bar",
                "name_key": "foo-bar",
                "family_key": "x",
                "aliases": ["foo bar"],  # same as primary - should be skipped
            }
        }
        results = _iter_entries(data)
        keys = [k for k, _ in results]
        assert keys.count("foo bar") == 1  # not duplicated

    def test_underscore_comments_skipped(self):
        data = {
            "_comment": "ignored",
            "real-key": {"version_key": "real", "name_key": "real", "family_key": "x"},
        }
        results = dict(_iter_entries(data))
        assert "_comment" not in results
        assert "real-key" in results

    def test_entry_without_version_key_skipped(self):
        data = {"bad": {"name_key": "bad", "family_key": "x"}}
        results = _iter_entries(data)
        assert results == []

    def test_slim_meta_has_no_aliases_key(self):
        """Extra-key meta dicts should not carry the aliases list."""
        data = {
            "a b": {
                "version_key": "a-b",
                "name_key": "a-b",
                "family_key": "x",
                "aliases": ["a-b"],
            }
        }
        result_dict = dict(_iter_entries(data))
        assert "aliases" not in result_dict["a-b"]


# ---------------------------------------------------------------------------
# Integration: CC version-free hyphen forms
# ---------------------------------------------------------------------------


class TestCCHyphenForms:
    """Hyphenated CC name-key forms must resolve now that aliases arrays are set."""

    @pytest.mark.parametrize(
        "raw,expected_key,expected_name,expected_family",
        [
            ("cc-by-nc", "cc-by-nc", "cc-by-nc", "cc"),
            ("cc-by-nc-nd", "cc-by-nc-nd", "cc-by-nc-nd", "cc"),
            ("cc-by-nc-sa", "cc-by-nc-sa", "cc-by-nc-sa", "cc"),
            ("cc-by-nd", "cc-by-nd", "cc-by-nd", "cc"),
            ("cc-by-sa", "cc-by-sa", "cc-by-sa", "cc"),
        ],
    )
    def test_hyphen_form_resolves(
        self, raw, expected_key, expected_name, expected_family
    ):
        v = normalise_licence(raw, strict=True)
        assert v.key == expected_key, f"{raw!r}: key {v.key!r} != {expected_key!r}"
        assert v.licence.key == expected_name
        assert v.family.key == expected_family

    def test_cc_by_nc_strict_does_not_raise(self):
        v = normalise_licence("cc-by-nc", strict=True)
        assert v.key == "cc-by-nc"

    def test_cc_by_nc_nd_strict_does_not_raise(self):
        v = normalise_licence("cc-by-nc-nd", strict=True)
        assert v.key == "cc-by-nc-nd"


# ---------------------------------------------------------------------------
# Integration: CC space variants via aliases arrays
# ---------------------------------------------------------------------------


class TestCCSpaceVariants:
    """Space-separated and mixed forms listed in aliases arrays."""

    @pytest.mark.parametrize(
        "raw,expected_key",
        [
            ("cc by nc", "cc-by-nc"),
            ("cc-by nc", "cc-by-nc"),
            ("cc by nd", "cc-by-nd"),
            ("cc-by nd", "cc-by-nd"),
            ("cc by nc-sa", "cc-by-nc-sa"),
            ("cc by nc sa", "cc-by-nc-sa"),
            ("cc by nc-nd", "cc-by-nc-nd"),
            ("cc by nc nd", "cc-by-nc-nd"),
            ("cc by sa", "cc-by-sa"),
            ("cc-by sa", "cc-by-sa"),
        ],
    )
    def test_space_variant_resolves(self, raw, expected_key):
        v = normalise_licence(raw, strict=True)
        assert v.key == expected_key, f"{raw!r}: got {v.key!r}, want {expected_key!r}"


# ---------------------------------------------------------------------------
# Integration: GPL shorthand keys
# ---------------------------------------------------------------------------


class TestGPLShorthands:
    """gpl-2, gpl-3, gpl-v3 and friends must now resolve."""

    @pytest.mark.parametrize(
        "raw,expected_key,expected_name,expected_family",
        [
            ("gpl-2", "gpl-2.0", "gpl-2", "copyleft"),
            ("gpl-3", "gpl-3.0", "gpl-3", "copyleft"),
            ("gpl-v2", "gpl-2.0", "gpl-2", "copyleft"),
            ("gpl-v3", "gpl-3.0", "gpl-3", "copyleft"),
            ("agpl-3", "agpl-3.0", "agpl-3", "copyleft"),
            ("lgpl-3", "lgpl-3.0", "lgpl-3", "copyleft"),
            ("lgpl-2", "lgpl-2.1", "lgpl-2.1", "copyleft"),
        ],
    )
    def test_gpl_shorthand_resolves(
        self, raw, expected_key, expected_name, expected_family
    ):
        v = normalise_licence(raw, strict=True)
        assert v.key == expected_key, f"{raw!r}: key {v.key!r} != {expected_key!r}"
        assert v.licence.key == expected_name
        assert v.family.key == expected_family

    def test_gpl_2_strict_no_raise(self):
        v = normalise_licence("gpl-2", strict=True)
        assert v.key == "gpl-2.0"

    def test_gpl_3_strict_no_raise(self):
        v = normalise_licence("gpl-3", strict=True)
        assert v.key == "gpl-3.0"

    def test_gpl_v3_strict_no_raise(self):
        v = normalise_licence("gpl-v3", strict=True)
        assert v.key == "gpl-3.0"


# ---------------------------------------------------------------------------
# Full script simulation: the exact inputs from the bug report
# ---------------------------------------------------------------------------


SCRIPT_INPUTS = [
    ("apache-2.0", "apache-2.0", "apache", "osi"),
    ("cc-by", "cc-by", "cc-by", "cc"),
    ("cc-by-nc", "cc-by-nc", "cc-by-nc", "cc"),
    ("cc-by-nc-nd", "cc-by-nc-nd", "cc-by-nc-nd", "cc"),
    ("cc-by-nc-sa", "cc-by-nc-sa", "cc-by-nc-sa", "cc"),
    ("cc-by-nd", "cc-by-nd", "cc-by-nd", "cc"),
    ("cc-by-sa", "cc-by-sa", "cc-by-sa", "cc"),
    ("gpl-2", "gpl-2.0", "gpl-2", "copyleft"),
    ("gpl-3", "gpl-3.0", "gpl-3", "copyleft"),
    ("gpl-v3", "gpl-3.0", "gpl-3", "copyleft"),
    ("mit", "mit", "mit", "osi"),
    ("other-oa", "other-oa", "other-oa", "other-oa"),
    ("public-domain", "public-domain", "public-domain", "public-domain"),
    (
        "publisher-specific-oa",
        "publisher-specific-oa",
        "publisher-specific-oa",
        "publisher-oa",
    ),
    ("unspecified-oa", "unspecified-oa", "unspecified-oa", "other-oa"),
]


@pytest.mark.parametrize(
    "raw,expected_key,expected_name,expected_family", SCRIPT_INPUTS
)
def test_script_inputs_all_resolve(raw, expected_key, expected_name, expected_family):
    """Every input from the bug-report script should now resolve in strict mode."""
    v = normalise_licence(raw, strict=True)
    assert v.key == expected_key, f"{raw!r}: key {v.key!r} != {expected_key!r}"
    assert v.licence.key == expected_name, (
        f"{raw!r}: name {v.licence.key!r} != {expected_name!r}"
    )
    assert v.family.key == expected_family, (
        f"{raw!r}: family {v.family.key!r} != {expected_family!r}"
    )


def test_false_still_fails():
    """'false' is not a licence and must remain unresolvable in strict mode."""
    with pytest.raises(LicenceNotFoundError):
        normalise_licence("false", strict=True)


# ---------------------------------------------------------------------------
# Regression: existing aliases still work
# ---------------------------------------------------------------------------


class TestExistingAliasesNotBroken:
    def test_cc_by_4_0(self):
        assert normalise_licence("CC BY 4.0").key == "cc-by-4.0"

    def test_cc_by_nc_4_0(self):
        assert normalise_licence("CC BY-NC 4.0").key == "cc-by-nc-4.0"

    def test_cc_by_nc_nd_4_0(self):
        assert normalise_licence("CC BY-NC-ND 4.0").key == "cc-by-nc-nd-4.0"

    def test_gpl_3_0(self):
        assert normalise_licence("gpl-3.0").key == "gpl-3.0"

    def test_gpl_2_0(self):
        assert normalise_licence("gpl-2.0").key == "gpl-2.0"

    def test_mit(self):
        assert normalise_licence("MIT").key == "mit"

    def test_apache(self):
        assert normalise_licence("Apache-2.0").key == "apache-2.0"

    def test_public_domain(self):
        assert normalise_licence("public domain").key == "public-domain"
