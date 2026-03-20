"""Tests for prose pattern matching via ProseParser."""

from license_normaliser import normalise_license


class TestProsePatternMatching:
    def test_cc_by_nc_nd_4_0_prose(self):
        v = normalise_license("this work is licensed under cc by-nc-nd 4.0 terms")
        assert v.key == "cc-by-nc-nd-4.0"
        assert v.family.key == "cc"

    def test_cc_by_nc_nd_3_0_prose(self):
        v = normalise_license("license: cc by-nc-nd 3.0")
        assert v.key == "cc-by-nc-nd-3.0"
        assert v.family.key == "cc"

    def test_cc_by_nc_sa_creative_commons_prose(self):
        v = normalise_license("content licensed under creative commons by-nc-sa")
        assert v.key == "cc-by-nc-sa"
        assert v.family.key == "cc"

    def test_attribution_prose(self):
        v = normalise_license(
            "the article is made available under the attribution license terms"
        )
        assert v.key == "cc-by"
        assert v.family.key == "cc"

    def test_attribution_noncommercial_prose(self):
        v = normalise_license(
            "this article is licensed under attribution noncommercial terms"
        )
        assert v.key == "cc-by-nc"
        assert v.family.key == "cc"

    def test_attribution_sharealike_prose(self):
        v = normalise_license("licensed under attribution share alike conditions")
        assert v.key == "cc-by-sa"
        assert v.family.key == "cc"

    def test_elsevier_tdm_prose(self):
        v = normalise_license(
            "this journal participates in text and data mining as "
            "permitted by the elsevier tdm agreement"
        )
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_elsevier_user_license_prose(self):
        v = normalise_license(
            "elsevier user license applies to this open access article"
        )
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_prose(self):
        v = normalise_license("acs authorchoice option was selected by the authors")
        assert v.key == "acs-authorchoice"
        assert v.family.key == "publisher-oa"

    def test_all_rights_reserved_prose(self):
        v = normalise_license("all rights reserved except as permitted by law")
        assert v.key == "all-rights-reserved"
        assert v.family.key == "publisher-proprietary"

    def test_short_string_via_registry(self):
        v = normalise_license("cc by-nc-nd")
        assert v.key == "cc-by-nc-nd"
        assert v.family.key == "cc"

    def test_open_access_prose_matched(self):
        v = normalise_license("open access article available now")
        assert v.key == "other-oa"
        assert v.family.key == "other-oa"
