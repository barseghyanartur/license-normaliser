"""Tests for AliasParser - non-CC aliases (Apache, MIT, BSD, GPL, etc.)."""

from licence_normaliser import normalise_licence


class TestNonCCAliases:
    def test_apache_shorthand(self):
        v = normalise_licence("apache")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_license(self):
        v = normalise_licence("apache license")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_2(self):
        v = normalise_licence("apache 2")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_apache_2_0(self):
        v = normalise_licence("apache 2.0")
        assert v.key == "apache-2.0"
        assert v.family.key == "osi"

    def test_mit_license(self):
        v = normalise_licence("mit license")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_the_mit_license(self):
        v = normalise_licence("the mit license")
        assert v.key == "mit"
        assert v.family.key == "osi"

    def test_bsd_shorthand(self):
        v = normalise_licence("bsd")
        assert v.key == "bsd-3-clause"
        assert v.family.key == "osi"

    def test_bsd_license(self):
        v = normalise_licence("bsd license")
        assert v.key == "bsd-3-clause"
        assert v.family.key == "osi"

    def test_mozilla(self):
        v = normalise_licence("mozilla")
        assert v.key == "mpl-2.0"
        assert v.family.key == "osi"

    def test_isc_license(self):
        v = normalise_licence("isc license")
        assert v.key == "isc"
        assert v.family.key == "osi"

    def test_gpl_shorthand(self):
        v = normalise_licence("gpl")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gnu_gpl(self):
        v = normalise_licence("gnu gpl")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gnu_gpl_v2(self):
        v = normalise_licence("gnu gpl v2")
        assert v.key == "gpl-2.0"
        assert v.family.key == "copyleft"

    def test_gpl_3_0_or_later(self):
        v = normalise_licence("gpl-3.0+")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"

    def test_gpl_2_0_or_later(self):
        v = normalise_licence("gpl-2.0+")
        assert v.key == "gpl-2.0"
        assert v.family.key == "copyleft"

    def test_agpl_shorthand(self):
        v = normalise_licence("agpl")
        assert v.key == "agpl-3.0"
        assert v.family.key == "copyleft"

    def test_agpl_3_0_or_later(self):
        v = normalise_licence("agpl-3.0+")
        assert v.key == "agpl-3.0"
        assert v.family.key == "copyleft"

    def test_lgpl_shorthand(self):
        v = normalise_licence("lgpl")
        assert v.key == "lgpl-3.0"
        assert v.family.key == "copyleft"

    def test_lgpl_2_1_or_later(self):
        v = normalise_licence("lgpl-2.1+")
        assert v.key == "lgpl-2.1"
        assert v.family.key == "copyleft"

    def test_lgpl_3_0_or_later(self):
        v = normalise_licence("lgpl-3.0+")
        assert v.key == "lgpl-3.0"
        assert v.family.key == "copyleft"

    def test_unlicense(self):
        v = normalise_licence("unlicense")
        assert v.key == "unlicense"
        assert v.family.key == "osi"

    def test_wtfpl(self):
        v = normalise_licence("wtfpl")
        assert v.key == "wtfpl"
        assert v.family.key == "osi"

    def test_zlib(self):
        v = normalise_licence("zlib")
        assert v.key == "zlib"
        assert v.family.key == "osi"

    def test_open_database_license(self):
        v = normalise_licence("open database license")
        assert v.key == "odbl"
        assert v.family.key == "open-data"

    def test_public_domain(self):
        v = normalise_licence("public domain")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"

    def test_pd_alias(self):
        v = normalise_licence("pd")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"
