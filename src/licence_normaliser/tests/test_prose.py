"""Tests for prose pattern matching via ProseParser."""

import pytest

from licence_normaliser import normalise_licence

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestProsePatternMatching:
    @pytest.mark.parametrize(
        "input_str,expected_key,expected_name,expected_family",
        [
            (
                "this work is licensed under cc by-nc-nd 4.0 terms",
                "cc-by-nc-nd-4.0",
                "cc-by-nc-nd",
                "cc",
            ),
            (
                "license: cc by-nc-nd 3.0",
                "cc-by-nc-nd-3.0",
                "cc-by-nc-nd",
                "cc",
            ),
            (
                "content licensed under creative commons by-nc-sa",
                "cc-by-nc-sa",
                "cc-by-nc-sa",
                "cc",
            ),
            (
                "this content is made available under creative commons by license",
                "cc-by",
                "cc-by",
                "cc",
            ),
            (
                "this article is licensed under attribution noncommercial terms",
                "cc-by-nc",
                "cc-by-nc",
                "cc",
            ),
            (
                "licensed under attribution share alike conditions",
                "cc-by-sa",
                "cc-by-sa",
                "cc",
            ),
            (
                "Article published under CC by-nc 3.0-igo license.",
                "cc-by-nc-3.0-igo",
                "cc-by-nc",
                "cc",
            ),
            (
                "Article published under CC by-nd 3.0-igo license.",
                "cc-by-nd-3.0-igo",
                "cc-by-nd",
                "cc",
            ),
            (
                "Article published under CC by-sa 3.0-igo license.",
                "cc-by-sa-3.0-igo",
                "cc-by-sa",
                "cc",
            ),
            (
                "all rights reserved except as permitted by law",
                "all-rights-reserved",
                "all-rights-reserved",
                "publisher-proprietary",
            ),
            ("cc by-nc-nd", "cc-by-nc-nd", "cc-by-nc-nd", "cc"),
        ],
    )
    def test_cc_prose(self, input_str, expected_key, expected_name, expected_family):
        v = normalise_licence(input_str)
        assert v.key == expected_key
        assert v.licence.key == expected_name
        assert v.family.key == expected_family

    @pytest.mark.parametrize(
        "input_str,expected_key,expected_name,expected_family",
        [
            (
                "available under the Open Government License (OGL).",
                "ogl-uk-3.0",
                "ogl-uk",
                "ogl",
            ),
            ("licensed under the OGL terms", "ogl-uk-3.0", "ogl-uk", "ogl"),
            ("under the Open Government Licence", "ogl-uk-3.0", "ogl-uk", "ogl"),
            ("Open Government Licence v3.0", "ogl-uk-3.0", "ogl-uk", "ogl"),
            ("under Open Government License v2.0", "ogl-uk-2.0", "ogl-uk", "ogl"),
            ("Open Government Licence 1.0", "ogl-uk-1.0", "ogl-uk", "ogl"),
        ],
    )
    def test_ogl_prose(self, input_str, expected_key, expected_name, expected_family):
        v = normalise_licence(input_str)
        assert v.key == expected_key
        assert v.licence.key == expected_name
        assert v.family.key == expected_family

    @pytest.mark.parametrize(
        "input_str,expected_key,expected_name,expected_family",
        [
            (
                "elsevier tdm agreement applies to this article",
                "elsevier-tdm",
                "elsevier-tdm",
                "publisher-tdm",
            ),
            (
                "elsevier user license applies to this open access article",
                "elsevier-oa",
                "elsevier-oa",
                "publisher-oa",
            ),
            (
                "acs authorchoice option was selected by the authors",
                "acs-authorchoice",
                "acs-authorchoice",
                "publisher-oa",
            ),
            (
                "This is an ACS AuthorChoice CC BY article.",
                "acs-authorchoice-ccby",
                "acs-authorchoice-ccby",
                "publisher-oa",
            ),
            (
                "ACS AuthorChoice with CC BY license",
                "acs-authorchoice-ccby",
                "acs-authorchoice-ccby",
                "publisher-oa",
            ),
            (
                "ACS AuthorChoice CC BY 4.0 article",
                "acs-authorchoice-ccby",
                "acs-authorchoice-ccby",
                "publisher-oa",
            ),
            ("open access article available now", "other-oa", "other-oa", "other-oa"),
            (
                "open access article under the Open Government License (OGL).",
                "other-oa",
                "other-oa",
                "other-oa",
            ),
        ],
    )
    def test_publisher_prose(
        self, input_str, expected_key, expected_name, expected_family
    ):
        v = normalise_licence(input_str)
        assert v.key == expected_key
        assert v.licence.key == expected_name
        assert v.family.key == expected_family
