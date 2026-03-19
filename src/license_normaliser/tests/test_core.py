"""Integration tests for the full normalisation pipeline via the public API."""

import pytest

from license_normaliser import (
    LicenseFamilyEnum,
    LicenseNameEnum,
    LicenseVersionEnum,
    normalise_license,
    normalise_licenses,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestDirectLookup:
    def test_mit(self):
        v = normalise_license("mit")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_cc_by_4_0(self):
        v = normalise_license("cc-by-4.0")
        assert v.key == "cc-by-4.0"
        assert v.family.key == "cc"

    def test_gpl_3_0(self):
        v = normalise_license("gpl-3.0")
        assert v.family.key == "copyleft"

    def test_unknown(self):
        v = normalise_license("unknown")
        assert v.key == "unknown"
        assert v.family.key == "unknown"

    def test_odbl(self):
        v = normalise_license("odbl")
        assert v.family.key == "open-data"

    def test_all_rights_reserved(self):
        v = normalise_license("all-rights-reserved")
        assert v.key == "all-rights-reserved"


class TestAliasLookup:
    def test_mit_titlecase(self):
        assert normalise_license("MIT").key == "mit"

    def test_mit_license(self):
        assert normalise_license("mit license").key == "mit"

    def test_the_mit_license(self):
        assert normalise_license("The MIT License").key == "mit"

    def test_apache_2_0_alias(self):
        assert normalise_license("Apache 2.0").key == "apache-2.0"

    def test_apache_license(self):
        assert normalise_license("Apache License").key == "apache-2.0"

    def test_gpl_short(self):
        assert normalise_license("GPL").key == "gpl-3.0"

    def test_gpl_v2(self):
        assert normalise_license("GNU GPL v2").key == "gpl-2.0"

    def test_agpl(self):
        assert normalise_license("AGPL").key == "agpl-3.0"

    def test_lgpl(self):
        assert normalise_license("LGPL").key == "lgpl-3.0"

    def test_bsd_alias(self):
        assert normalise_license("BSD").key == "bsd-3-clause"

    def test_cc_by_alias(self):
        assert normalise_license("CC BY").key == "cc-by"

    def test_cc_by_4_0_alias(self):
        assert normalise_license("CC BY 4.0").key == "cc-by-4.0"

    def test_cc_by_nc_nd_4_0_alias(self):
        assert normalise_license("CC BY-NC-ND 4.0").key == "cc-by-nc-nd-4.0"

    def test_cc0_1_0_alias(self):
        assert normalise_license("CC0 1.0").key == "cc0-1.0"

    def test_creative_commons_attribution_full(self):
        assert (
            normalise_license("Creative Commons Attribution 4.0 International").key
            == "cc-by-4.0"
        )

    def test_cc_nc_nd_international_license(self):
        v = normalise_license(
            "Creative Commons Attribution-NonCommercial-NoDerivatives "
            "4.0 International License"
        )
        assert v.key == "cc-by-nc-nd-4.0"

    def test_public_domain_alias(self):
        assert normalise_license("public domain").key == "public-domain"

    def test_all_rights_reserved_alias(self):
        assert normalise_license("all rights reserved").key == "all-rights-reserved"

    def test_wiley_tdm_shorthand(self):
        assert normalise_license("wiley tdm license").key == "wiley-tdm"

    def test_springernature_tdm_shorthand(self):
        assert normalise_license("springer nature tdm").key == "springernature-tdm"


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

    def test_cc_by_nc_nd_3_0_url(self):
        v = normalise_license("http://creativecommons.org/licenses/by-nc-nd/3.0/")
        assert v.key == "cc-by-nc-nd-3.0"

    def test_cc_igo_url(self):
        v = normalise_license("https://creativecommons.org/licenses/by/3.0/igo/")
        assert v.key == "cc-by-3.0-igo"

    def test_cc0_url(self):
        v = normalise_license("https://creativecommons.org/publicdomain/zero/1.0/")
        assert v.key == "cc0-1.0"

    def test_elsevier_oa_url(self):
        v = normalise_license("http://www.elsevier.com/open-access/userlicense/1.0/")
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_elsevier_tdm_url(self):
        v = normalise_license("https://www.elsevier.com/tdm/userlicense/1.0/")
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_wiley_tdm_1_1_url(self):
        v = normalise_license("http://doi.wiley.com/10.1002/tdm_license_1.1")
        assert v.key == "wiley-tdm-1.1"

    def test_springer_tdm_url(self):
        v = normalise_license("http://www.springer.com/tdm")
        assert v.key == "springer-tdm"

    def test_tandf_terms_url(self):
        v = normalise_license("https://www.tandfonline.com/action/showCopyRight")
        assert v.key == "tandf-terms"

    def test_acs_authorchoice_ccby_url(self):
        v = normalise_license(
            "https://pubs.acs.org/page/policy/authorchoice_ccby_termsofuse.html"
        )
        assert v.key == "acs-authorchoice-ccby"

    def test_aps_default_url(self):
        v = normalise_license("https://link.aps.org/licenses/aps-default-license")
        assert v.key == "aps-default"

    def test_bmj_copyright_url(self):
        v = normalise_license(
            "https://www.bmj.com/company/legal-stuff/copyright-notice/"
        )
        assert v.key == "bmj-copyright"

    def test_jama_cc_by_url(self):
        v = normalise_license("https://jamanetwork.com/pages/cc-by-license-permissions")
        assert v.key == "jama-cc-by"

    def test_iop_tdm_url(self):
        v = normalise_license(
            "https://iopscience.iop.org/info/page/text-and-data-mining"
        )
        assert v.key == "iop-tdm"

    def test_gnu_gpl_2_url(self):
        v = normalise_license("http://www.gnu.org/licenses/gpl-2.0.html")
        assert v.key == "gpl-2.0"

    def test_gnu_gpl_3_url(self):
        v = normalise_license("https://www.gnu.org/licenses/gpl-3.0.html")
        assert v.key == "gpl-3.0"


class TestCcUrlRegex:
    def test_cc_by_nc_sa_2_5(self):
        v = normalise_license("https://creativecommons.org/licenses/by-nc-sa/2.5/")
        assert v.key == "cc-by-nc-sa-2.5"
        assert v.family.key == "cc"

    def test_cc_by_sa_2_0(self):
        v = normalise_license("https://creativecommons.org/licenses/by-sa/2.0/")
        assert v.key == "cc-by-sa-2.0"

    def test_synthetic_family_is_cc(self):
        v = normalise_license("https://creativecommons.org/licenses/by-nc/2.0/")
        assert v.family.key == "cc"

    def test_cc_by_nc_nd_igo_3_0(self):
        v = normalise_license("https://creativecommons.org/licenses/by-nc-nd/3.0/igo/")
        assert v.key == "cc-by-nc-nd-3.0-igo"


class TestProseScan:
    def test_cc_by_nc_nd_in_prose(self):
        v = normalise_license(
            "Distributed under attribution noncommercial noderivatives terms."
        )
        assert v.key == "cc-by-nc-nd"

    def test_attribution_only_prose(self):
        v = normalise_license(
            "Reuse is permitted provided proper attribution is given."
        )
        assert v.key == "cc-by"

    def test_all_rights_reserved_prose(self):
        v = normalise_license(
            "Copyright 2024 ACME Corp. All rights reserved worldwide."
        )
        assert v.key == "all-rights-reserved"

    def test_elsevier_tdm_prose(self):
        v = normalise_license(
            "This content is licensed under the Elsevier TDM agreement."
        )
        assert v.key == "elsevier-tdm"

    def test_public_domain_prose(self):
        v = normalise_license(
            "This dataset has been released into the public domain by its author."
        )
        assert v.key == "public-domain"

    def test_url_in_prose_wins_over_prose_scan(self):
        v = normalise_license(
            "This is an open access article under the CC BY license "
            "(http://creativecommons.org/licenses/by/4.0/)"
        )
        assert v.key == "cc-by-4.0"


class TestFallback:
    def test_unknown_string(self):
        v = normalise_license("some-totally-unknown-license-xyz")
        assert v.key == "some-totally-unknown-license-xyz"
        assert v.family.key == "unknown"
        assert v.url is None

    def test_empty_string(self):
        v = normalise_license("")
        assert v.key == "unknown"

    def test_whitespace_only(self):
        v = normalise_license("   ")
        assert v.key == "unknown"


class TestCreativeCommons:
    @pytest.mark.parametrize(
        "raw,expected_key",
        [
            ("cc-by", "cc-by"),
            ("CC BY 4.0", "cc-by-4.0"),
            ("CC BY 3.0", "cc-by-3.0"),
            ("CC BY 2.5", "cc-by-2.5"),
            ("CC BY 2.0", "cc-by-2.0"),
            ("cc-by-sa-4.0", "cc-by-sa-4.0"),
            ("cc-by-sa-3.0", "cc-by-sa-3.0"),
            ("CC BY-ND 4.0", "cc-by-nd-4.0"),
            ("cc-by-nc", "cc-by-nc"),
            ("CC BY-NC 4.0", "cc-by-nc-4.0"),
            ("cc-by-nc-sa", "cc-by-nc-sa"),
            ("CC BY-NC-SA 4.0", "cc-by-nc-sa-4.0"),
            ("cc-by-nc-nd", "cc-by-nc-nd"),
            ("CC BY-NC-ND 4.0", "cc-by-nc-nd-4.0"),
            ("CC BY-NC-ND 3.0 IGO", "cc-by-nc-nd-3.0-igo"),
            ("cc0", "cc0"),
            ("CC0 1.0", "cc0-1.0"),
            ("cc-pdm", "cc-pdm"),
        ],
    )
    def test_cc_variant(self, raw, expected_key):
        assert normalise_license(raw).key == expected_key

    def test_all_cc_results_have_cc_or_cc0_family(self):
        cc_variants = [
            "cc-by-4.0",
            "cc-by-sa-4.0",
            "cc-by-nd-4.0",
            "cc-by-nc-4.0",
            "cc-by-nc-sa-4.0",
            "cc-by-nc-nd-4.0",
        ]
        for raw in cc_variants:
            v = normalise_license(raw)
            assert v.family.key == "cc", f"Expected cc family for {raw}"

    def test_cc0_family_is_cc0_not_cc(self):
        assert normalise_license("cc0").family.key == "cc0"

    def test_cc_pdm_family_is_public_domain(self):
        assert normalise_license("cc-pdm").family.key == "public-domain"


class TestOSI:
    @pytest.mark.parametrize(
        "raw,expected_key",
        [
            ("MIT", "mit"),
            ("Apache-2.0", "apache-2.0"),
            ("BSD-2-Clause", "bsd-2-clause"),
            ("BSD-3-Clause", "bsd-3-clause"),
            ("ISC", "isc"),
            ("MPL-2.0", "mpl-2.0"),
        ],
    )
    def test_osi_key(self, raw, expected_key):
        v = normalise_license(raw)
        assert v.key == expected_key
        assert v.family.key == "osi"

    def test_mit_has_url(self):
        assert normalise_license("MIT").url == "https://opensource.org/licenses/MIT"


class TestCopyleft:
    @pytest.mark.parametrize(
        "raw,expected_key",
        [
            ("GPL-2.0", "gpl-2.0"),
            ("GPL-2.0-only", "gpl-2.0-only"),
            ("GPL-3.0", "gpl-3.0"),
            ("GPL-3.0-only", "gpl-3.0-only"),
            ("AGPL-3.0", "agpl-3.0"),
            ("LGPL-2.1", "lgpl-2.1"),
            ("LGPL-3.0", "lgpl-3.0"),
        ],
    )
    def test_copyleft_key(self, raw, expected_key):
        v = normalise_license(raw)
        assert v.key == expected_key
        assert v.family.key == "copyleft"


class TestPublisherLicenses:
    def test_elsevier_oa_family(self):
        assert normalise_license("elsevier-oa").family.key == "publisher-oa"

    def test_elsevier_tdm_family(self):
        assert normalise_license("elsevier-tdm").family.key == "publisher-tdm"

    def test_wiley_vor_family(self):
        assert normalise_license("wiley-vor").family.key == "publisher-proprietary"

    def test_springer_tdm_family(self):
        assert normalise_license("springer-tdm").family.key == "publisher-tdm"

    def test_acs_authorchoice_family(self):
        assert normalise_license("acs-authorchoice").family.key == "publisher-oa"

    def test_aaas_author_reuse(self):
        assert (
            normalise_license("aaas-author-reuse").family.key == "publisher-proprietary"
        )

    def test_thieme_nlm(self):
        assert normalise_license("thieme-nlm").family.key == "publisher-oa"


class TestOpenData:
    def test_odbl(self):
        assert normalise_license("odbl").family.key == "open-data"

    def test_pddl(self):
        assert normalise_license("pddl").family.key == "open-data"

    def test_odc_by(self):
        assert normalise_license("odc-by").family.key == "open-data"


class TestCatchAll:
    def test_author_manuscript(self):
        assert normalise_license("author-manuscript").family.key == "publisher-oa"

    def test_no_reuse(self):
        assert normalise_license("no-reuse").family.key == "publisher-proprietary"

    def test_unspecified_oa(self):
        assert normalise_license("unspecified-oa").family.key == "other-oa"

    def test_implied_oa(self):
        assert normalise_license("implied-oa").family.key == "publisher-oa"


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

    def test_enum_checking_methods(self):
        v = normalise_license("MIT")
        assert v.is_family(LicenseFamilyEnum.OSI)
        assert not v.is_family(LicenseFamilyEnum.CC)
        assert v.is_name(LicenseNameEnum.MIT)
        assert not v.is_name(LicenseNameEnum.CC_BY)
        assert v.is_version(LicenseVersionEnum.MIT)
        assert not v.is_version(LicenseVersionEnum.GPL_3_0)


class TestBatchNormalisation:
    def test_basic_batch(self, batch_raw):
        results = normalise_licenses(batch_raw)
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
