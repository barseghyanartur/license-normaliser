"""End-to-end pipeline tests via the public API."""

from license_normaliser import normalise_license, normalise_licenses

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestDirectLookup:
    def test_mit(self):
        v = normalise_license("mit")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_apache(self):
        v = normalise_license("apache-2.0")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_cc_by_4_0(self):
        v = normalise_license("cc-by-4.0")
        assert v.key == "cc-by-4.0"
        assert v.family.key == "cc"

    def test_cc_by_nc_nd_4_0(self):
        v = normalise_license("cc-by-nc-nd-4.0")
        assert v.key == "cc-by-nc-nd-4.0"
        assert v.family.key == "cc"

    def test_cc0_1_0(self):
        v = normalise_license("cc0-1.0")
        assert v.key == "cc0-1.0"
        assert v.family.key == "cc0"

    def test_gpl_3_0(self):
        v = normalise_license("gpl-3.0")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gpl_2_0_only(self):
        v = normalise_license("gpl-2.0-only")
        assert v.key == "gpl-2.0-only"
        assert v.family.key == "copyleft"

    def test_lgpl_2_1(self):
        v = normalise_license("lgpl-2.1")
        assert v.key == "lgpl-2.1"
        assert v.family.key == "copyleft"

    def test_agpl_3_0(self):
        v = normalise_license("agpl-3.0")
        assert v.key == "agpl-3.0"
        assert v.family.key == "copyleft"

    def test_bsd_3_clause(self):
        v = normalise_license("bsd-3-clause")
        assert v.key == "bsd-3-clause"
        assert v.family.key == "osi"

    def test_isc(self):
        v = normalise_license("isc")
        assert v.key == "isc"
        assert v.family.key == "osi"

    def test_mpl_2_0(self):
        v = normalise_license("mpl-2.0")
        assert v.key == "mpl-2.0"
        assert v.family.key == "osi"

    def test_unlicense(self):
        v = normalise_license("unlicense")
        assert v.key == "unlicense"
        assert v.family.key == "osi"

    def test_wtfpl(self):
        v = normalise_license("wtfpl")
        assert v.key == "wtfpl"
        assert v.family.key == "osi"

    def test_zlib(self):
        v = normalise_license("zlib")
        assert v.key == "zlib"
        assert v.family.key == "osi"

    def test_odbl_1_0(self):
        v = normalise_license("odbl-1.0")
        assert v.key == "odbl-1.0"
        assert v.family.key == "data"

    def test_pddl_1_0(self):
        v = normalise_license("pddl-1.0")
        assert v.key == "pddl-1.0"
        assert v.family.key == "data"

    def test_odc_by_1_0(self):
        v = normalise_license("odc-by-1.0")
        assert v.key == "odc-by-1.0"
        assert v.family.key == "data"

    def test_unknown(self):
        v = normalise_license("unknown")
        assert v.key == "unknown"
        assert v.family.key == "unknown"

    def test_case_insensitive(self):
        v = normalise_license("MIT")
        assert v.key == "mit"
        v = normalise_license("Apache-2.0")
        assert v.key == "apache-2.0"


class TestBuiltinAliases:
    def test_cc_by(self):
        assert normalise_license("CC BY").key == "cc-by"

    def test_cc_by_4_0(self):
        assert normalise_license("CC BY 4.0").key == "cc-by-4.0"

    def test_cc_by_nc_nd_4_0(self):
        assert normalise_license("CC BY-NC-ND 4.0").key == "cc-by-nc-nd-4.0"

    def test_cc_by_nc_sa_4_0(self):
        assert normalise_license("CC BY-NC-SA 4.0").key == "cc-by-nc-sa-4.0"

    def test_cc0_1_0(self):
        assert normalise_license("CC0 1.0").key == "cc0-1.0"

    def test_public_domain(self):
        assert normalise_license("public domain").key == "public-domain"


class TestUrlLookup:
    def test_cc_by_https(self):
        v = normalise_license("https://creativecommons.org/licenses/by/4.0/")
        assert v.key == "cc-by-4.0"

    def test_cc_by_http(self):
        v = normalise_license("http://creativecommons.org/licenses/by/4.0/")
        assert v.key == "cc-by-4.0"

    def test_cc_by_no_trailing_slash(self):
        v = normalise_license("https://creativecommons.org/licenses/by/4.0")
        assert v.key == "cc-by-4.0"

    def test_mit_url(self):
        v = normalise_license("https://opensource.org/licenses/MIT")
        assert v.key == "mit"


class TestFamilyInference:
    def test_cc_family(self):
        v = normalise_license("cc-by-4.0")
        assert v.family.key == "cc"

    def test_cc0_family(self):
        v = normalise_license("cc0-1.0")
        assert v.family.key == "cc0"

    def test_copyleft_family(self):
        assert normalise_license("gpl-3.0").family.key == "copyleft"
        assert normalise_license("agpl-3.0").family.key == "copyleft"
        assert normalise_license("lgpl-2.1").family.key == "copyleft"

    def test_osi_family(self):
        assert normalise_license("mit").family.key == "osi"
        assert normalise_license("apache-2.0").family.key == "osi"
        assert normalise_license("bsd-3-clause").family.key == "osi"

    def test_data_family(self):
        assert normalise_license("odbl-1.0").family.key == "data"
        assert normalise_license("pddl-1.0").family.key == "data"
        assert normalise_license("odc-by-1.0").family.key == "data"


class TestNameInference:
    def test_cc_name_strips_version(self):
        assert normalise_license("cc-by-4.0").license.key == "cc-by"
        assert normalise_license("cc-by-nc-nd-4.0").license.key == "cc-by-nc-nd"
        assert normalise_license("cc-by-sa-3.0").license.key == "cc-by-sa"
        assert normalise_license("cc0-1.0").license.key == "cc0"
        assert normalise_license("cc-by-nc-sa-4.0").license.key == "cc-by-nc-sa"

    def test_non_cc_keeps_key(self):
        assert normalise_license("mit").license.key == "mit"
        assert normalise_license("gpl-3.0").license.key == "gpl-3"


class TestHierarchyNavigation:
    def test_version_license_family_chain(self):
        v = normalise_license("CC BY-NC-ND 4.0")
        assert v.key == "cc-by-nc-nd-4.0"
        assert v.license.key == "cc-by-nc-nd"
        assert v.license.family.key == "cc"
        assert v.family.key == "cc"

    def test_str_representations(self):
        v = normalise_license("CC BY-NC-ND 4.0")
        assert str(v) == "cc-by-nc-nd-4.0"
        assert str(v.license) == "cc-by-nc-nd"
        assert str(v.family) == "cc"


class TestFallback:
    def test_unknown_string(self):
        v = normalise_license("some-totally-unknown-license-xyz")
        assert v.key == "some-totally-unknown-license-xyz"
        assert v.family.key == "unknown"

    def test_empty_string(self):
        v = normalise_license("")
        assert v.key == "unknown"

    def test_whitespace_only(self):
        v = normalise_license("   ")
        assert v.key == "unknown"


class TestBatchNormalisation:
    def test_basic_batch(self):
        results = normalise_licenses(["MIT", "Apache-2.0", "CC BY 4.0"])
        assert [r.key for r in results] == ["mit", "apache-2.0", "cc-by-4.0"]

    def test_batch_preserves_order(self):
        raw = ["GPL-3.0", "MIT", "CC BY 4.0", "Apache-2.0"]
        expected = ["gpl-3.0", "mit", "cc-by-4.0", "apache-2.0"]
        assert [r.key for r in normalise_licenses(raw)] == expected

    def test_batch_accepts_generator(self):
        results = normalise_licenses(x for x in ["MIT", "ISC"])
        assert results[0].key == "mit"

    def test_batch_empty(self):
        assert normalise_licenses([]) == []
