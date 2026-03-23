"""Tests for AliasParser - non-CC aliases (Apache, MIT, BSD, GPL, etc.)."""

from license_normaliser import normalise_license


class TestNonCCAliases:
    def test_apache_shorthand(self):
        v = normalise_license("apache")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_license(self):
        v = normalise_license("apache license")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_2(self):
        v = normalise_license("apache 2")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_2_0(self):
        v = normalise_license("apache 2.0")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_mit_license(self):
        v = normalise_license("mit license")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_the_mit_license(self):
        v = normalise_license("the mit license")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_bsd_shorthand(self):
        v = normalise_license("bsd")
        assert v.key == "bsd-3-clause"
        assert v.family.key == "osi"

    def test_bsd_license(self):
        v = normalise_license("bsd license")
        assert v.key == "bsd-3-clause"
        assert v.family.key == "osi"

    def test_mozilla(self):
        v = normalise_license("mozilla")
        assert v.key == "mpl-2.0"
        assert v.family.key == "osi"

    def test_isc_license(self):
        v = normalise_license("isc license")
        assert v.key == "isc"
        assert v.family.key == "osi"

    def test_gpl_shorthand(self):
        v = normalise_license("gpl")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gnu_gpl(self):
        v = normalise_license("gnu gpl")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gnu_gpl_v2(self):
        v = normalise_license("gnu gpl v2")
        assert v.key == "gpl-2.0"
        assert v.family.key == "copyleft"

    def test_gpl_3_0_or_later(self):
        v = normalise_license("gpl-3.0+")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gpl_2_0_or_later(self):
        v = normalise_license("gpl-2.0+")
        assert v.key == "gpl-2.0"
        assert v.family.key == "copyleft"

    def test_agpl_shorthand(self):
        v = normalise_license("agpl")
        assert v.key == "agpl-3.0"
        assert v.family.key == "copyleft"

    def test_agpl_3_0_or_later(self):
        v = normalise_license("agpl-3.0+")
        assert v.key == "agpl-3.0"
        assert v.family.key == "copyleft"

    def test_lgpl_shorthand(self):
        v = normalise_license("lgpl")
        assert v.key == "lgpl-3.0"
        assert v.family.key == "copyleft"

    def test_lgpl_2_1_or_later(self):
        v = normalise_license("lgpl-2.1+")
        assert v.key == "lgpl-2.1"
        assert v.family.key == "copyleft"

    def test_lgpl_3_0_or_later(self):
        v = normalise_license("lgpl-3.0+")
        assert v.key == "lgpl-3.0"
        assert v.family.key == "copyleft"

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

    def test_open_database_license(self):
        v = normalise_license("open database license")
        assert v.key == "odbl"
        assert v.family.key == "open-data"

    def test_public_domain(self):
        v = normalise_license("public domain")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"

    def test_pd_alias(self):
        v = normalise_license("pd")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"
