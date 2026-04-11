"""End-to-end pipeline tests via the public API."""

import pytest

from licence_normaliser import normalise_licence, normalise_licences

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestDirectLookup:
    @pytest.mark.parametrize(
        "input_str,expected_key,expected_family",
        [
            ("mit", "mit", "osi"),
            ("apache-2.0", "apache-2.0", "osi"),
            ("cc-by-4.0", "cc-by-4.0", "cc"),
            ("cc-by-nc-nd-4.0", "cc-by-nc-nd-4.0", "cc"),
            ("cc0-1.0", "cc0-1.0", "cc0"),
            ("gpl-3.0", "gpl-3.0", "copyleft"),
            ("gpl-2.0-only", "gpl-2.0-only", "copyleft"),
            ("lgpl-2.1", "lgpl-2.1", "copyleft"),
            ("agpl-3.0", "agpl-3.0", "copyleft"),
            ("bsd-3-clause", "bsd-3-clause", "osi"),
            ("isc", "isc", "osi"),
            ("mpl-2.0", "mpl-2.0", "osi"),
            ("unlicense", "unlicense", "public-domain"),
            ("wtfpl", "wtfpl", "public-domain"),
            ("zlib", "zlib", "osi"),
            ("odbl-1.0", "odbl-1.0", "open-data"),
            ("pddl-1.0", "pddl-1.0", "data"),
            ("odc-by-1.0", "odc-by-1.0", "open-data"),
            ("unknown", "unknown", "unknown"),
        ],
    )
    def test_direct_lookup(
        self, input_str: str, expected_key: str, expected_family: str
    ) -> None:
        v = normalise_licence(input_str)
        assert v.key == expected_key
        assert v.family.key == expected_family

    def test_case_insensitive(self) -> None:
        v = normalise_licence("MIT")
        assert v.key == "mit"
        v = normalise_licence("Apache-2.0")
        assert v.key == "apache-2.0"


class TestBuiltinAliases:
    @pytest.mark.parametrize(
        "input_str,expected_key",
        [
            ("CC BY", "cc-by"),
            ("CC BY 4.0", "cc-by-4.0"),
            ("CC BY-NC-ND 4.0", "cc-by-nc-nd-4.0"),
            ("CC BY-NC-SA 4.0", "cc-by-nc-sa-4.0"),
            ("CC0 1.0", "cc0-1.0"),
            ("public domain", "public-domain"),
        ],
    )
    def test_builtin_aliases(self, input_str: str, expected_key: str) -> None:
        assert normalise_licence(input_str).key == expected_key


class TestUrlLookup:
    @pytest.mark.parametrize(
        "input_str,expected_key",
        [
            ("https://creativecommons.org/licenses/by/4.0/", "cc-by-4.0"),
            ("http://creativecommons.org/licenses/by/4.0/", "cc-by-4.0"),
            ("https://creativecommons.org/licenses/by/4.0", "cc-by-4.0"),
            ("https://opensource.org/licenses/MIT", "mit"),
        ],
    )
    def test_url_lookup(self, input_str: str, expected_key: str) -> None:
        v = normalise_licence(input_str)
        assert v.key == expected_key


class TestFamilyInference:
    @pytest.mark.parametrize(
        "input_str,expected_family",
        [
            ("cc-by-4.0", "cc"),
            ("cc0-1.0", "cc0"),
            ("gpl-3.0", "copyleft"),
            ("agpl-3.0", "copyleft"),
            ("lgpl-2.1", "copyleft"),
            ("mit", "osi"),
            ("apache-2.0", "osi"),
            ("bsd-3-clause", "osi"),
            ("pddl-1.0", "data"),
        ],
    )
    def test_family_inference(self, input_str: str, expected_family: str) -> None:
        assert normalise_licence(input_str).family.key == expected_family


class TestNameInference:
    @pytest.mark.parametrize(
        "input_str,expected_name",
        [
            ("cc-by-4.0", "cc-by"),
            ("cc-by-nc-nd-4.0", "cc-by-nc-nd"),
            ("cc-by-sa-3.0", "cc-by-sa"),
            ("cc0-1.0", "cc0"),
            ("cc-by-nc-sa-4.0", "cc-by-nc-sa"),
            ("mit", "mit"),
            ("gpl-3.0", "gpl-3"),
        ],
    )
    def test_name_inference(self, input_str: str, expected_name: str) -> None:
        assert normalise_licence(input_str).licence.key == expected_name


class TestHierarchyNavigation:
    def test_version_licence_family_chain(self) -> None:
        v = normalise_licence("CC BY-NC-ND 4.0")
        assert v.key == "cc-by-nc-nd-4.0"
        assert v.licence.key == "cc-by-nc-nd"
        assert v.licence.family.key == "cc"
        assert v.family.key == "cc"

    def test_str_representations(self) -> None:
        v = normalise_licence("CC BY-NC-ND 4.0")
        assert str(v) == "cc-by-nc-nd-4.0"
        assert str(v.licence) == "cc-by-nc-nd"
        assert str(v.family) == "cc"


class TestFallback:
    def test_unknown_string(self) -> None:
        v = normalise_licence("some-totally-unknown-licence-xyz")
        assert v.key == "some-totally-unknown-licence-xyz"
        assert v.family.key == "unknown"

    def test_empty_string(self) -> None:
        v = normalise_licence("")
        assert v.key == "unknown"

    def test_whitespace_only(self) -> None:
        v = normalise_licence("   ")
        assert v.key == "unknown"


class TestBatchNormalisation:
    def test_basic_batch(self) -> None:
        results = normalise_licences(["MIT", "Apache-2.0", "CC BY 4.0"])
        assert [r.key for r in results] == ["mit", "apache-2.0", "cc-by-4.0"]

    def test_batch_preserves_order(self) -> None:
        raw = ["GPL-3.0", "MIT", "CC BY 4.0", "Apache-2.0"]
        expected = ["gpl-3.0", "mit", "cc-by-4.0", "apache-2.0"]
        assert [r.key for r in normalise_licences(raw)] == expected

    def test_batch_accepts_generator(self) -> None:
        results = normalise_licences((x for x in ["MIT", "ISC"]))  # noqa: C416
        assert results[0].key == "mit"

    def test_batch_empty(self) -> None:
        assert normalise_licences([]) == []
