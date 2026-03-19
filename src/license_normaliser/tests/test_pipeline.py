"""Unit tests for _pipeline.py."""

from license_normaliser._pipeline import (
    _PROSE_MIN_LEN,
    step_alias,
    step_cc_regex,
    step_direct,
    step_fallback,
    step_prose,
    step_url,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestStepDirect:
    def test_exact_match(self):
        assert step_direct("mit") == "mit"

    def test_cc_by_4_0(self):
        assert step_direct("cc-by-4.0") == "cc-by-4.0"

    def test_no_match_returns_none(self):
        assert step_direct("not-a-known-key") is None

    def test_uppercase_no_match(self):
        assert step_direct("MIT") is None

    def test_unknown_key(self):
        assert step_direct("unknown") == "unknown"


class TestStepAlias:
    def test_mit_license(self):
        assert step_alias("mit license") == "mit"

    def test_apache_2_0(self):
        assert step_alias("apache 2.0") == "apache-2.0"

    def test_cc_by_4_0(self):
        assert step_alias("cc by 4.0") == "cc-by-4.0"

    def test_gpl_shorthand(self):
        assert step_alias("gpl") == "gpl-3.0"

    def test_public_domain(self):
        assert step_alias("public domain") == "public-domain"

    def test_no_match_returns_none(self):
        assert step_alias("definitely not an alias") is None

    def test_cc_nc_nd_international_license(self):
        key = (
            "creative commons attribution-noncommercial-noderivatives "
            "4.0 international license"
        )
        assert step_alias(key) == "cc-by-nc-nd-4.0"


class TestStepUrl:
    def test_canonical_https_cc(self):
        assert step_url("https://creativecommons.org/licenses/by/4.0") == "cc-by-4.0"

    def test_http_normalised_to_https(self):
        assert step_url("http://creativecommons.org/licenses/by/4.0") == "cc-by-4.0"

    def test_trailing_slash_stripped(self):
        assert step_url("https://creativecommons.org/licenses/by/4.0/") == "cc-by-4.0"

    def test_elsevier_oa(self):
        assert (
            step_url("http://www.elsevier.com/open-access/userlicense/1.0/")
            == "elsevier-oa"
        )

    def test_wiley_tdm_1_1(self):
        assert (
            step_url("http://doi.wiley.com/10.1002/tdm_license_1.1") == "wiley-tdm-1.1"
        )

    def test_no_match_returns_none(self):
        assert step_url("https://example.com/some-unknown-license") is None

    def test_non_url_returns_none(self):
        assert step_url("mit") is None


class TestStepCcRegex:
    def test_known_cc_url_returns_version(self):
        v = step_cc_regex("https://creativecommons.org/licenses/by/4.0/")
        assert v is not None and v.key == "cc-by-4.0"

    def test_igo_variant(self):
        v = step_cc_regex("https://creativecommons.org/licenses/by-nc-sa/3.0/igo/")
        assert v is not None and v.key == "cc-by-nc-sa-3.0-igo"

    def test_cc_zero(self):
        v = step_cc_regex("https://creativecommons.org/publicdomain/zero/1.0/")
        assert v is not None and v.key == "cc0"

    def test_non_cc_url_returns_none(self):
        assert step_cc_regex("https://opensource.org/licenses/MIT") is None

    def test_plain_text_returns_none(self):
        assert step_cc_regex("mit") is None

    def test_family_is_cc(self):
        v = step_cc_regex("https://creativecommons.org/licenses/by-nc-nd/4.0/")
        assert v is not None and v.family.key == "cc"


class TestStepProse:
    def test_short_input_returns_none(self):
        short = "cc by"
        assert len(short) < _PROSE_MIN_LEN
        assert step_prose(short) is None

    def test_cc_by_4_0_in_sentence(self):
        s = "This article is licensed under a CC BY 4.0 International License."
        assert step_prose(s) == "cc-by-4.0"

    def test_attribution_only_prose(self):
        s = "Reuse permitted provided proper attribution is given to the authors."
        assert step_prose(s) == "cc-by"

    def test_all_rights_reserved_prose(self):
        s = "Copyright 2024 ACME Corp. All rights reserved worldwide."
        assert step_prose(s) == "all-rights-reserved"

    def test_no_match_returns_none(self):
        assert step_prose("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx") is None


class TestStepFallback:
    def test_always_returns_version(self):
        v = step_fallback("some-weird-token")
        assert v.key == "some-weird-token"

    def test_family_is_unknown(self):
        v = step_fallback("no-such-license")
        assert v.family.key == "unknown"

    def test_url_is_none(self):
        assert step_fallback("xyz").url is None
