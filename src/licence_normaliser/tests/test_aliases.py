"""Tests for AliasParser - non-CC aliases (Apache, MIT, BSD, GPL, etc.)."""

import pytest

from licence_normaliser import normalise_licence

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestNonCCAliases:
    @pytest.mark.parametrize(
        "input_str,expected_key,expected_family",
        [
            ("apache", "apache-2.0", "osi"),
            ("apache license", "apache-2.0", "osi"),
            ("apache 2", "apache-2.0", "osi"),
            ("apache 2.0", "apache-2.0", "osi"),
            ("mit license", "mit", "osi"),
            ("the mit license", "mit", "osi"),
            ("bsd", "bsd-3-clause", "osi"),
            ("bsd license", "bsd-3-clause", "osi"),
            ("mozilla", "mpl-2.0", "osi"),
            ("isc license", "isc", "osi"),
            ("gpl", "gpl-3.0", "copyleft"),
            ("gnu gpl", "gpl-3.0", "copyleft"),
            ("gnu gpl v2", "gpl-2.0", "copyleft"),
            ("gpl-3.0+", "gpl-3.0", "copyleft"),
            ("gpl-2.0+", "gpl-2.0", "copyleft"),
            ("agpl", "agpl-3.0", "copyleft"),
            ("agpl-3.0+", "agpl-3.0", "copyleft"),
            ("lgpl", "lgpl-3.0", "copyleft"),
            ("lgpl-2.1+", "lgpl-2.1", "copyleft"),
            ("lgpl-3.0+", "lgpl-3.0", "copyleft"),
            ("unlicense", "unlicense", "public-domain"),
            ("wtfpl", "wtfpl", "public-domain"),
            ("zlib", "zlib", "osi"),
            ("open database license", "odbl", "open-data"),
            ("public domain", "public-domain", "public-domain"),
            ("pd", "public-domain", "public-domain"),
        ],
    )
    def test_non_cc_aliases(
        self, input_str: str, expected_key: str, expected_family: str
    ) -> None:
        v = normalise_licence(input_str)
        assert v.key == expected_key
        assert v.family.key == expected_family
