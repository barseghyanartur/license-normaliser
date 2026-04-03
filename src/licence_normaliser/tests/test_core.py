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

    def test_case_insensitive(self):
        v = normalise_licence("MIT")
        assert v.key == "mit"
        v = normalise_licence("Apache-2.0")
        assert v.key == "apache-2.0"


class TestBuiltinAliases:
    def test_cc_by(self):
        assert normalise_licence("CC BY").key == "cc-by"

    def test_cc_by_4_0(self):
        assert normalise_licence("CC BY 4.0").key == "cc-by-4.0"

    def test_cc_by_nc_nd_4_0(self):
        assert normalise_licence("CC BY-NC-ND 4.0").key == "cc-by-nc-nd-4.0"

    def test_cc_by_nc_sa_4_0(self):
        assert normalise_licence("CC BY-NC-SA 4.0").key == "cc-by-nc-sa-4.0"

    def test_cc0_1_0(self):
        assert normalise_licence("CC0 1.0").key == "cc0-1.0"

    def test_public_domain(self):
        assert normalise_licence("public domain").key == "public-domain"


class TestUrlLookup:
    def test_cc_by_https(self):
        v = normalise_licence("https://creativecommons.org/licenses/by/4.0/")
        assert v.key == "cc-by-4.0"

    def test_cc_by_http(self):
        v = normalise_licence("http://creativecommons.org/licenses/by/4.0/")
        assert v.key == "cc-by-4.0"

    def test_cc_by_no_trailing_slash(self):
        v = normalise_licence("https://creativecommons.org/licenses/by/4.0")
        assert v.key == "cc-by-4.0"

    def test_mit_url(self):
        v = normalise_licence("https://opensource.org/licenses/MIT")
        assert v.key == "mit"


class TestFamilyInference:
    def test_cc_family(self):
        v = normalise_licence("cc-by-4.0")
        assert v.family.key == "cc"

    def test_cc0_family(self):
        v = normalise_licence("cc0-1.0")
        assert v.family.key == "cc0"

    def test_copyleft_family(self):
        assert normalise_licence("gpl-3.0").family.key == "copyleft"
        assert normalise_licence("agpl-3.0").family.key == "copyleft"
        assert normalise_licence("lgpl-2.1").family.key == "copyleft"

    def test_osi_family(self):
        assert normalise_licence("mit").family.key == "osi"
        assert normalise_licence("apache-2.0").family.key == "osi"
        assert normalise_licence("bsd-3-clause").family.key == "osi"

    def test_data_family(self):
        assert normalise_licence("pddl-1.0").family.key == "data"


class TestNameInference:
    def test_cc_name_strips_version(self):
        assert normalise_licence("cc-by-4.0").licence.key == "cc-by"
        assert normalise_licence("cc-by-nc-nd-4.0").licence.key == "cc-by-nc-nd"
        assert normalise_licence("cc-by-sa-3.0").licence.key == "cc-by-sa"
        assert normalise_licence("cc0-1.0").licence.key == "cc0"
        assert normalise_licence("cc-by-nc-sa-4.0").licence.key == "cc-by-nc-sa"

    def test_non_cc_keeps_key(self):
        assert normalise_licence("mit").licence.key == "mit"
        assert normalise_licence("gpl-3.0").licence.key == "gpl-3"


class TestHierarchyNavigation:
    def test_version_licence_family_chain(self):
        v = normalise_licence("CC BY-NC-ND 4.0")
        assert v.key == "cc-by-nc-nd-4.0"
        assert v.licence.key == "cc-by-nc-nd"
        assert v.licence.family.key == "cc"
        assert v.family.key == "cc"

    def test_str_representations(self):
        v = normalise_licence("CC BY-NC-ND 4.0")
        assert str(v) == "cc-by-nc-nd-4.0"
        assert str(v.licence) == "cc-by-nc-nd"
        assert str(v.family) == "cc"


class TestFallback:
    def test_unknown_string(self):
        v = normalise_licence("some-totally-unknown-licence-xyz")
        assert v.key == "some-totally-unknown-licence-xyz"
        assert v.family.key == "unknown"

    def test_empty_string(self):
        v = normalise_licence("")
        assert v.key == "unknown"

    def test_whitespace_only(self):
        v = normalise_licence("   ")
        assert v.key == "unknown"


class TestBatchNormalisation:
    def test_basic_batch(self):
        results = normalise_licences(["MIT", "Apache-2.0", "CC BY 4.0"])
        assert [r.key for r in results] == ["mit", "apache-2.0", "cc-by-4.0"]

    def test_batch_preserves_order(self):
        raw = ["GPL-3.0", "MIT", "CC BY 4.0", "Apache-2.0"]
        expected = ["gpl-3.0", "mit", "cc-by-4.0", "apache-2.0"]
        assert [r.key for r in normalise_licences(raw)] == expected

    def test_batch_accepts_generator(self):
        results = normalise_licences(x for x in ["MIT", "ISC"])
        assert results[0].key == "mit"

    def test_batch_empty(self):
        assert normalise_licences([]) == []
