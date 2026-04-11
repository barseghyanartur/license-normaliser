"""Tests for prose pattern matching via ProseParser."""

from licence_normaliser import normalise_licence

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestProsePatternMatching:
    def test_cc_by_nc_nd_4_0_prose(self) -> None:
        v = normalise_licence("this work is licensed under cc by-nc-nd 4.0 terms")
        assert v.key == "cc-by-nc-nd-4.0"
        assert v.family.key == "cc"

    def test_cc_by_nc_nd_3_0_prose(self) -> None:
        v = normalise_licence("license: cc by-nc-nd 3.0")
        assert v.key == "cc-by-nc-nd-3.0"
        assert v.family.key == "cc"

    def test_cc_by_nc_sa_creative_commons_prose(self) -> None:
        v = normalise_licence("content licensed under creative commons by-nc-sa")
        assert v.key == "cc-by-nc-sa"
        assert v.family.key == "cc"

    def test_attribution_prose(self) -> None:
        v = normalise_licence(
            "this content is made available under creative commons by license"
        )
        assert v.key == "cc-by"
        assert v.family.key == "cc"

    def test_attribution_noncommercial_prose(self) -> None:
        v = normalise_licence(
            "this article is licensed under attribution noncommercial terms"
        )
        assert v.key == "cc-by-nc"
        assert v.family.key == "cc"

    def test_attribution_sharealike_prose(self) -> None:
        v = normalise_licence("licensed under attribution share alike conditions")
        assert v.key == "cc-by-sa"
        assert v.family.key == "cc"

    def test_elsevier_tdm_prose(self) -> None:
        v = normalise_licence(
            "this journal participates in text and data mining as "
            "permitted by the elsevier tdm agreement"
        )
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_elsevier_user_licence_prose(self) -> None:
        v = normalise_licence(
            "elsevier user license applies to this open access article"
        )
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_prose(self) -> None:
        v = normalise_licence("acs authorchoice option was selected by the authors")
        assert v.key == "acs-authorchoice"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_cc_by_prose(self) -> None:
        v = normalise_licence("This is an ACS AuthorChoice CC BY article.")
        assert v.key == "acs-authorchoice-ccby"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_cc_by_variant_prose(self) -> None:
        v = normalise_licence("ACS AuthorChoice with CC BY license")
        assert v.key == "acs-authorchoice-ccby"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_cc_by_4_0_prose(self) -> None:
        v = normalise_licence("ACS AuthorChoice CC BY 4.0 article")
        assert v.key == "acs-authorchoice-ccby"
        assert v.family.key == "publisher-oa"

    def test_cc_by_nc_3_0_igo_prose(self) -> None:
        v = normalise_licence("Article published under CC by-nc 3.0-igo license.")
        assert v.key == "cc-by-nc-3.0-igo"
        assert v.licence.key == "cc-by-nc"
        assert v.family.key == "cc"

    def test_cc_by_nd_3_0_igo_prose(self) -> None:
        v = normalise_licence("Article published under CC by-nd 3.0-igo license.")
        assert v.key == "cc-by-nd-3.0-igo"
        assert v.licence.key == "cc-by-nd"
        assert v.family.key == "cc"

    def test_cc_by_sa_3_0_igo_prose(self) -> None:
        v = normalise_licence("Article published under CC by-sa 3.0-igo license.")
        assert v.key == "cc-by-sa-3.0-igo"
        assert v.licence.key == "cc-by-sa"
        assert v.family.key == "cc"

    def test_all_rights_reserved_prose(self) -> None:
        v = normalise_licence("all rights reserved except as permitted by law")
        assert v.key == "all-rights-reserved"
        assert v.family.key == "publisher-proprietary"

    def test_short_string_via_registry(self) -> None:
        v = normalise_licence("cc by-nc-nd")
        assert v.key == "cc-by-nc-nd"
        assert v.family.key == "cc"

    def test_open_access_prose_matched(self) -> None:
        v = normalise_licence("open access article available now")
        assert v.key == "other-oa"
        assert v.family.key == "other-oa"
