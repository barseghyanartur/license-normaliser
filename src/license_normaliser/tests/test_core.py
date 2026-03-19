"""Tests for license_normaliser core functionality."""

from license_normaliser import (
    LicenseFamily,
    LicenseFamilyEnum,
    LicenseName,
    LicenseNameEnum,
    normalise_license,
    normalise_licenses,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestLicenseFamily:
    """Tests for LicenseFamily."""

    def test_family_str(self):
        fam = LicenseFamily(key="cc")
        assert str(fam) == "cc"

    def test_family_repr(self):
        fam = LicenseFamily(key="osi")
        assert repr(fam) == "LicenseFamily('osi')"

    def test_family_equality(self):
        fam1 = LicenseFamily(key="cc")
        fam2 = LicenseFamily(key="cc")
        assert fam1 == fam2

    def test_family_equality_with_str(self):
        fam = LicenseFamily(key="cc")
        assert fam == "cc"

    def test_family_hash(self):
        fam1 = LicenseFamily(key="cc")
        fam2 = LicenseFamily(key="cc")
        assert hash(fam1) == hash(fam2)


class TestLicenseName:
    """Tests for LicenseName."""

    def test_license_name_str(self):
        name = LicenseName(key="cc-by", family=LicenseFamily(key="cc"))
        assert str(name) == "cc-by"

    def test_license_name_repr(self):
        name = LicenseName(key="cc-by", family=LicenseFamily(key="cc"))
        assert repr(name) == "LicenseName('cc-by', family='cc')"

    def test_license_name_equality(self):
        name1 = LicenseName(key="cc-by", family=LicenseFamily(key="cc"))
        name2 = LicenseName(key="cc-by", family=LicenseFamily(key="cc"))
        assert name1 == name2


class TestLicenseVersion:
    """Tests for LicenseVersion."""

    def test_version_str(self):
        v = normalise_license("MIT")
        assert str(v) == "mit"

    def test_version_family_shortcut(self):
        v = normalise_license("cc-by-4.0")
        assert v.family.key == "cc"

    def test_version_url(self):
        v = normalise_license("cc-by-4.0")
        assert v.url == "https://creativecommons.org/licenses/by/4.0/"

    def test_version_no_url(self):
        v = normalise_license("unknown")
        assert v.url is None


class TestCreativeCommons:
    """Tests for Creative Commons license normalisation."""

    def test_cc_by(self):
        v = normalise_license("cc-by")
        assert v.key == "cc-by"
        assert v.license.key == "cc-by"
        assert v.family.key == "cc"

    def test_cc_by_4_0(self):
        v = normalise_license("CC BY 4.0")
        assert v.key == "cc-by-4.0"
        assert v.url == "https://creativecommons.org/licenses/by/4.0/"

    def test_cc_by_nc_nd(self):
        v = normalise_license("cc-by-nc-nd")
        assert v.key == "cc-by-nc-nd"
        assert v.license.key == "cc-by-nc-nd"

    def test_cc_by_url(self):
        v = normalise_license("http://creativecommons.org/licenses/by/4.0/")
        assert v.key == "cc-by-4.0"

    def test_cc0(self):
        v = normalise_license("cc0")
        assert v.key == "cc0"
        assert v.family.key == "cc0"

    def test_cc_zero(self):
        v = normalise_license("CC0 1.0")
        assert v.key == "cc0-1.0"


class TestOSILicenses:
    """Tests for OSI-approved licenses."""

    def test_mit(self):
        v = normalise_license("MIT")
        assert v.key == "mit"
        assert v.family.key == "osi"
        assert v.url == "https://opensource.org/licenses/MIT"

    def test_mit_variants(self):
        v = normalise_license("mit license")
        assert v.key == "mit"

    def test_apache(self):
        v = normalise_license("Apache-2.0")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_variants(self):
        v = normalise_license("apache 2.0")
        assert v.key == "apache-2.0"

    def test_bsd_3_clause(self):
        v = normalise_license("BSD-3-Clause")
        assert v.key == "bsd-3-clause"
        assert v.family.key == "osi"

    def test_isc(self):
        v = normalise_license("ISC")
        assert v.key == "isc"
        assert v.family.key == "osi"

    def test_mpl(self):
        v = normalise_license("MPL-2.0")
        assert v.key == "mpl-2.0"
        assert v.family.key == "osi"


class TestCopyleftLicenses:
    """Tests for copyleft licenses."""

    def test_gpl_3(self):
        v = normalise_license("gpl-3.0")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gpl_variants(self):
        v = normalise_license("gnu gpl v3")
        assert v.key == "gpl-3.0"

    def test_agpl(self):
        v = normalise_license("agpl")
        assert v.key == "agpl-3.0"

    def test_lgpl(self):
        v = normalise_license("lgpl")
        assert v.key == "lgpl-3.0"


class TestPublisherLicenses:
    """Tests for publisher-specific licenses."""

    def test_elsevier_oa(self):
        v = normalise_license("http://www.elsevier.com/open-access/userlicense/1.0/")
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_elsevier_tdm(self):
        v = normalise_license("https://www.elsevier.com/tdm/userlicense/1.0/")
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_wiley_tdm(self):
        v = normalise_license("http://doi.wiley.com/10.1002/tdm_license_1.1")
        assert v.key == "wiley-tdm-1.1"
        assert v.family.key == "publisher-tdm"

    def test_springer_tdm(self):
        v = normalise_license("http://www.springer.com/tdm")
        assert v.key == "springer-tdm"

    def test_acs_authorchoice(self):
        v = normalise_license("acs authorchoice")
        assert v.key == "acs-authorchoice"
        assert v.family.key == "publisher-oa"


class TestCatchAllTokens:
    """Tests for catch-all tokens."""

    def test_public_domain(self):
        v = normalise_license("public domain")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"

    def test_all_rights_reserved(self):
        v = normalise_license("all rights reserved")
        assert v.key == "all-rights-reserved"
        assert v.family.key == "publisher-proprietary"

    def test_author_manuscript(self):
        v = normalise_license("author manuscript")
        assert v.key == "author-manuscript"
        assert v.family.key == "publisher-oa"

    def test_unknown(self):
        v = normalise_license("some-unknown-license")
        assert v.key == "some-unknown-license"
        assert v.family.key == "unknown"

    def test_empty_string(self):
        v = normalise_license("")
        assert v.key == "unknown"


class TestProseNormalisation:
    """Tests for prose license descriptions."""

    def test_full_cc_prose(self):
        v = normalise_license(
            "This article is licensed under a Creative "
            "Commons Attribution-NonCommercial-NoDerivatives 4.0 "
            "International License"
        )
        # Prose matching detects the license name but not version from prose
        assert v.key == "cc-by-nc-nd"

    def test_url_in_prose(self):
        v = normalise_license(
            "This is an open access article under the CC BY "
            "license (http://creativecommons.org/licenses/by/4.0/)"
        )
        assert v.key == "cc-by-4.0"


class TestBatchNormalisation:
    """Tests for batch normalisation."""

    def test_normalise_licenses(self):
        results = normalise_licenses(["MIT", "CC BY 4.0", "gpl-3.0"])
        assert len(results) == 3
        assert results[0].key == "mit"
        assert results[1].key == "cc-by-4.0"
        assert results[2].key == "gpl-3.0"


class TestURLNormalisation:
    """Tests for URL normalisation."""

    def test_url_trailing_slash(self):
        v1 = normalise_license("http://creativecommons.org/licenses/by/4.0")
        v2 = normalise_license("http://creativecommons.org/licenses/by/4.0/")
        assert v1.key == v2.key == "cc-by-4.0"

    def test_url_case_insensitive(self):
        v1 = normalise_license("HTTP://creativecommons.org/licenses/by/4.0/")
        v2 = normalise_license("http://creativecommons.org/licenses/by/4.0/")
        assert v1.key == v2.key == "cc-by-4.0"


class TestEnums:
    """Tests for license enums."""

    def test_family_enum_values(self):
        assert LicenseFamilyEnum.CC.value == "cc"
        assert LicenseFamilyEnum.OSI.value == "osi"
        assert LicenseFamilyEnum.COPYLEFT.value == "copyleft"

    def test_name_enum_values(self):
        assert LicenseNameEnum.CC_BY.value == "cc-by"
        assert LicenseNameEnum.MIT.value == "mit"
        assert LicenseNameEnum.GPL_3.value == "gpl-3"

    def test_version_enum_values(self):
        from license_normaliser import LicenseVersionEnum

        assert LicenseVersionEnum.CC_BY_4_0.value == "cc-by-4.0"
        assert LicenseVersionEnum.MIT.value == "mit"
        assert LicenseVersionEnum.GPL_3_0.value == "gpl-3.0"

    def test_name_enum_family_property(self):
        assert LicenseNameEnum.CC_BY.family == LicenseFamilyEnum.CC
        assert LicenseNameEnum.MIT.family == LicenseFamilyEnum.OSI
        assert LicenseNameEnum.GPL_3.family == LicenseFamilyEnum.COPYLEFT

    def test_version_enum_name_property(self):
        from license_normaliser import LicenseVersionEnum

        assert LicenseVersionEnum.CC_BY_4_0.name_enum == LicenseNameEnum.CC_BY
        assert LicenseVersionEnum.MIT.name_enum == LicenseNameEnum.MIT

    def test_version_enum_family_property(self):
        from license_normaliser import LicenseVersionEnum

        assert LicenseVersionEnum.CC_BY_4_0.family == LicenseFamilyEnum.CC
        assert LicenseVersionEnum.MIT.family == LicenseFamilyEnum.OSI


class TestEnumChecking:
    """Tests for enum checking methods on LicenseVersion."""

    def test_is_family(self):
        v = normalise_license("MIT")
        assert v.is_family(LicenseFamilyEnum.OSI)
        assert not v.is_family(LicenseFamilyEnum.CC)

    def test_is_name(self):
        v = normalise_license("CC BY 4.0")
        assert v.is_name(LicenseNameEnum.CC_BY)
        assert not v.is_name(LicenseNameEnum.MIT)

    def test_is_version(self):
        from license_normaliser import LicenseVersionEnum

        v = normalise_license("CC BY 4.0")
        assert v.is_version(LicenseVersionEnum.CC_BY_4_0)
        assert not v.is_version(LicenseVersionEnum.CC_BY_3_0)

    def test_is_family_cc(self):
        v = normalise_license("CC BY-NC-ND 4.0")
        assert v.is_family(LicenseFamilyEnum.CC)

    def test_is_name_copyleft(self):
        v = normalise_license("GPL-3.0")
        assert v.is_name(LicenseNameEnum.GPL_3)
