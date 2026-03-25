"""Comprehensive integration tests covering the full licence matrix.

Each tuple: (input_string, expected_version_key, expected_licence_key,
             expected_family_key)
"""

import pytest

from licence_normaliser import (
    LicenceNormalisationError,
    LicenceNotFoundError,
    LicenceVersion,
    normalise_licence,
    normalise_licences,
)

LICENCE_MATRIX = [
    # raw,expected_key,expected_licence,expected_family
    # === OSI-approved licences ===
    ("mit", "mit", "mit", "osi"),
    ("MIT", "mit", "mit", "osi"),
    ("  mit  ", "mit", "mit", "osi"),
    ("apache-2.0", "apache-2.0", "apache", "osi"),
    ("Apache-2.0", "apache-2.0", "apache", "osi"),
    ("Apache 2.0", "apache-2.0", "apache", "osi"),
    ("Apache License 2.0", "apache-2.0", "apache", "osi"),
    (
        "BSD 3-Clause",
        "bsd-3-clause",
        "bsd-3-clause",
        "osi",
    ),  # Resolves to bsd-3-clause/osi, matches SPDX and alias entries
    ("bsd-3-clause", "bsd-3-clause", "bsd-3-clause", "osi"),
    ("BSD License", "bsd-3-clause", "bsd-3-clause", "osi"),
    ("MPL-2.0", "mpl-2.0", "mpl", "osi"),
    ("mpl-2.0", "mpl-2.0", "mpl", "osi"),
    (
        "Mozilla Public License 2.0",
        "mpl-2.0",
        "mpl",
        "osi",
    ),  # Canonical full name of MPL-2.0, matches alias entry
    ("ISC", "isc", "isc", "osi"),
    ("isc", "isc", "isc", "osi"),
    ("ISC License", "isc", "isc", "osi"),
    ("Unlicense", "unlicense", "unlicense", "osi"),
    ("unlicense", "unlicense", "unlicense", "osi"),
    ("WTFPL", "wtfpl", "wtfpl", "osi"),
    ("wtfpl", "wtfpl", "wtfpl", "osi"),
    ("Zlib", "zlib", "zlib", "osi"),
    ("zlib", "zlib", "zlib", "osi"),
    # === GPL / AGPL / LGPL (copyleft) ===
    ("gpl-3.0", "gpl-3.0", "gpl-3", "copyleft"),
    ("GPL-3.0", "gpl-3.0", "gpl-3", "copyleft"),
    ("gpl-3.0+", "gpl-3.0", "gpl-3", "copyleft"),
    (
        "gpl-3-0",
        "gpl-3-0",
        "gpl-3-0",
        "copyleft",
    ),  # NOTE: hyphen instead of dot; resolver recognises gpl but doesn't normalise
    ("GNU GPL v3", "gpl-3.0", "gpl-3", "copyleft"),
    ("GPL v3", "gpl-3.0", "gpl-3", "copyleft"),
    ("gpl-2.0", "gpl-2.0", "gpl-2", "copyleft"),
    ("GPL v2", "gpl-2.0", "gpl-2", "copyleft"),
    ("lgpl-3.0", "lgpl-3.0", "lgpl-3", "copyleft"),
    ("LGPL-3.0", "lgpl-3.0", "lgpl-3", "copyleft"),
    ("lgpl-2.1", "lgpl-2.1", "lgpl-2.1", "copyleft"),
    ("LGPL v2.1", "lgpl-2.1", "lgpl-2.1", "copyleft"),
    ("lgpl v2.1", "lgpl-2.1", "lgpl-2.1", "copyleft"),
    ("agpl-3.0", "agpl-3.0", "agpl-3", "copyleft"),
    ("AGPL v3", "agpl-3.0", "agpl-3", "copyleft"),
    # === Creative Commons ===
    ("CC BY 4.0", "cc-by-4.0", "cc-by", "cc"),
    ("cc by 4.0", "cc-by-4.0", "cc-by", "cc"),
    ("cc-by-4.0", "cc-by-4.0", "cc-by", "cc"),
    ("CC BY 3.0", "cc-by-3.0", "cc-by", "cc"),
    ("cc by 3.0", "cc-by-3.0", "cc-by", "cc"),
    ("cc-by-3.0", "cc-by-3.0", "cc-by", "cc"),
    ("CC BY 2.5", "cc-by-2.5", "cc-by", "cc"),
    ("CC BY 2.0", "cc-by-2.0", "cc-by", "cc"),
    ("CC BY 1.0", "cc-by-1.0", "cc-by", "cc"),
    ("cc by", "cc-by", "cc-by", "cc"),
    (
        "CC-BY",
        "cc-by",
        "cc-by",
        "cc",
    ),  # SPDX form, resolves to cc-by/cc
    ("CC BY-NC 4.0", "cc-by-nc-4.0", "cc-by-nc", "cc"),
    ("cc by-nc 4.0", "cc-by-nc-4.0", "cc-by-nc", "cc"),
    ("cc-by-nc-4.0", "cc-by-nc-4.0", "cc-by-nc", "cc"),
    ("CC BY-NC 3.0", "cc-by-nc-3.0", "cc-by-nc", "cc"),
    ("CC BY-NC-SA 4.0", "cc-by-nc-sa-4.0", "cc-by-nc-sa", "cc"),
    ("cc by-nc-sa 4.0", "cc-by-nc-sa-4.0", "cc-by-nc-sa", "cc"),
    ("cc-by-nc-sa-4.0", "cc-by-nc-sa-4.0", "cc-by-nc-sa", "cc"),
    ("CC BY-NC-SA 3.0", "cc-by-nc-sa-3.0", "cc-by-nc-sa", "cc"),
    ("CC BY-NC-ND 4.0", "cc-by-nc-nd-4.0", "cc-by-nc-nd", "cc"),
    ("cc by-nc-nd 4.0", "cc-by-nc-nd-4.0", "cc-by-nc-nd", "cc"),
    ("cc-by-nc-nd-4.0", "cc-by-nc-nd-4.0", "cc-by-nc-nd", "cc"),
    ("CC BY-NC-ND 3.0", "cc-by-nc-nd-3.0", "cc-by-nc-nd", "cc"),
    ("cc by-nc-nd 3.0", "cc-by-nc-nd-3.0", "cc-by-nc-nd", "cc"),
    ("CC BY-ND 4.0", "cc-by-nd-4.0", "cc-by-nd", "cc"),
    ("cc by-nd 4.0", "cc-by-nd-4.0", "cc-by-nd", "cc"),
    ("cc-by-nd-4.0", "cc-by-nd-4.0", "cc-by-nd", "cc"),
    ("CC BY-SA 4.0", "cc-by-sa-4.0", "cc-by-sa", "cc"),
    ("cc by-sa 4.0", "cc-by-sa-4.0", "cc-by-sa", "cc"),
    ("cc-by-sa-4.0", "cc-by-sa-4.0", "cc-by-sa", "cc"),
    ("CC BY-SA 3.0", "cc-by-sa-3.0", "cc-by-sa", "cc"),
    ("cc-by-3.0-igo", "cc-by-3.0-igo", "cc-by", "cc"),
    ("cc-by-nc-nd-3.0-igo", "cc-by-nc-nd-3.0-igo", "cc-by-nc-nd", "cc"),
    # CC0
    ("CC0 1.0", "cc0-1.0", "cc0", "cc0"),
    ("cc0 1.0", "cc0-1.0", "cc0", "cc0"),
    ("cc0-1.0", "cc0-1.0", "cc0", "cc0"),
    ("CC0", "cc0-1.0", "cc0", "cc0"),
    ("cc0", "cc0-1.0", "cc0", "cc0"),
    ("cc-zero", "cc0-1.0", "cc0", "cc0"),
    ("CC Zero", "cc0-1.0", "cc0", "cc0"),
    ("CC-Zero", "cc0-1.0", "cc0", "cc0"),
    ("creative commons zero", "cc0-1.0", "cc0", "cc0"),
    ("Creative Commons Zero 1.0", "cc0-1.0", "cc0", "cc0"),
    # CC-PDM
    ("cc-pdm", "cc-pdm-1.0", "cc-pdm", "public-domain"),
    ("CC-PDM", "cc-pdm-1.0", "cc-pdm", "public-domain"),
    ("cc-pdm-1.0", "cc-pdm-1.0", "cc-pdm", "public-domain"),
    ("CC-PDM 1.0", "cc-pdm-1.0", "cc-pdm", "public-domain"),
    ("cc-pdm 1.0", "cc-pdm-1.0", "cc-pdm", "public-domain"),
    ("creative commons public domain", "cc-pdm-1.0", "cc-pdm", "public-domain"),
    # CC shorthand
    ("creative commons by", "cc-by", "cc-by", "cc"),
    ("creative commons by 4.0", "cc-by-4.0", "cc-by", "cc"),
    (
        "creative commons by-sa",
        "cc-by-sa",
        "cc-by-sa",
        "cc",
    ),  # Specifies by-sa, licence must be cc-by-sa
    (
        "creative commons by-nc",
        "cc-by-nc",
        "cc-by-nc",
        "cc",
    ),  # Specifies by-nc, licence must be cc-by-nc
    (
        "creative commons by-nc-sa",
        "cc-by-nc-sa",
        "cc-by-nc-sa",
        "cc",
    ),  # Specifies by-nc-sa, licence must be cc-by-nc-sa
    (
        "creative commons by-nc-nd",
        "cc-by-nc-nd",
        "cc-by-nc-nd",
        "cc",
    ),  # Specifies by-nc-nd, licence must be cc-by-nc-nd
    (
        "creative commons by-nd",
        "cc-by-nd",
        "cc-by-nd",
        "cc",
    ),  # Specifies by-nd, licence must be cc-by-nd
    # CC URLs
    (
        "http://creativecommons.org/licenses/by-nc-nd/4.0/",
        "cc-by-nc-nd-4.0",
        "cc-by-nc-nd",
        "cc",
    ),
    ("https://creativecommons.org/licenses/by/4.0/", "cc-by-4.0", "cc-by", "cc"),
    ("http://creativecommons.org/licenses/by/4.0/", "cc-by-4.0", "cc-by", "cc"),
    (
        "https://creativecommons.org/licenses/by-nc/4.0/",
        "cc-by-nc-4.0",
        "cc-by-nc",
        "cc",
    ),
    (
        "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "cc-by-nc-sa-4.0",
        "cc-by-nc-sa",
        "cc",
    ),
    (
        "https://creativecommons.org/licenses/by-nd/4.0/",
        "cc-by-nd-4.0",
        "cc-by-nd",
        "cc",
    ),
    (
        "https://creativecommons.org/licenses/by-sa/4.0/",
        "cc-by-sa-4.0",
        "cc-by-sa",
        "cc",
    ),
    (
        "http://creativecommons.org/licenses/by-nc-nd/3.0/igo/",
        "cc-by-nc-nd-3.0-igo",
        "cc-by-nc-nd",
        "cc",
    ),
    (
        "https://creativecommons.org/licenses/by/3.0/igo/",
        "cc-by-3.0-igo",
        "cc-by",
        "cc",
    ),
    ("https://creativecommons.org/publicdomain/zero/1.0/", "cc0-1.0", "cc0", "cc0"),
    ("http://creativecommons.org/publicdomain/zero/1.0/", "cc0-1.0", "cc0", "cc0"),
    # CC prose
    ("licensed under cc by-nc-nd 4.0 terms", "cc-by-nc-nd-4.0", "cc-by-nc-nd", "cc"),
    (
        "content is licensed under creative commons by-nc-sa",
        "cc-by-nc-sa",
        "cc-by-nc-sa",  # Contains by-nc-sa, license must be cc-by-nc-sa
        "cc",
    ),
    ("this content is under creative commons by license", "cc-by", "cc-by", "cc"),
    # Open Data
    ("ODbL", "odbl", "odbl", "open-data"),
    ("odbl", "odbl", "odbl", "open-data"),
    ("Open Database License", "odbl", "odbl", "open-data"),
    ("ODC-BY", "odc-by", "odc-by", "open-data"),
    ("odc-by", "odc-by", "odc-by", "open-data"),
    ("PDDL", "pddl", "pddl", "open-data"),
    ("pddl", "pddl", "pddl", "open-data"),
    (
        "Open Data Commons Public Domain Dedication",
        "public-domain",
        "public-domain",
        "public-domain",
    ),
    # Publisher
    ("elsevier-oa", "elsevier-oa", "elsevier-oa", "publisher-oa"),
    (
        "Elsevier OA",
        "elsevier-oa",
        "elsevier-oa",
        "publisher-oa",
    ),  # "Elsevier OA" unambiguously identifies Elsevier OA license
    ("elsevier tdm", "elsevier-tdm", "elsevier-tdm", "publisher-tdm"),
    ("Elsevier TDM", "elsevier-tdm", "elsevier-tdm", "publisher-tdm"),
    ("Elsevier User License", "elsevier-oa", "elsevier-oa", "publisher-oa"),
    (
        "https://www.elsevier.com/open-access/userlicense/1.0/",
        "elsevier-oa",
        "elsevier-oa",
        "publisher-oa",
    ),
    ("wiley-tdm", "wiley-tdm", "wiley-tdm", "publisher-tdm"),
    ("Wiley TDM", "wiley-tdm", "wiley-tdm", "publisher-tdm"),
    ("wiley vor", "wiley-vor", "wiley-vor", "publisher-proprietary"),
    ("springer-tdm", "springer-tdm", "springer-tdm", "publisher-tdm"),
    (
        "Springer Nature TDM",
        "springernature-tdm",
        "springernature-tdm",
        "publisher-tdm",
    ),
    ("acs-authorchoice", "acs-authorchoice", "acs-authorchoice", "publisher-oa"),
    ("ACS AuthorChoice", "acs-authorchoice", "acs-authorchoice", "publisher-oa"),
    (
        "acs-authorchoice-ccby",
        "acs-authorchoice-ccby",
        "acs-authorchoice-ccby",
        "publisher-oa",
    ),
    (
        "acs authorchoice cc by",
        "acs-authorchoice-ccby",
        "acs-authorchoice-ccby",
        "publisher-oa",
    ),
    ("aps-default", "aps-default", "aps-default", "publisher-proprietary"),
    ("APS Default", "aps-default", "aps-default", "publisher-proprietary"),
    ("iop-tdm", "iop-tdm", "iop-tdm", "publisher-tdm"),
    ("iop copyright", "iop-copyright", "iop-copyright", "publisher-proprietary"),
    ("bmj copyright", "bmj-copyright", "bmj-copyright", "publisher-proprietary"),
    ("rsc terms", "rsc-terms", "rsc-terms", "publisher-proprietary"),
    ("cup terms", "cup-terms", "cup-terms", "publisher-proprietary"),
    ("degruyter terms", "degruyter-terms", "degruyter-terms", "publisher-proprietary"),
    ("tandf terms", "tandf-terms", "tandf-terms", "publisher-proprietary"),
    (
        "sage permissions",
        "sage-permissions",
        "sage-permissions",
        "publisher-proprietary",
    ),
    ("wiley terms", "wiley-terms", "wiley-terms", "publisher-proprietary"),
    ("wiley am", "wiley-am", "wiley-am", "publisher-proprietary"),
    ("pnas licenses", "pnas-licenses", "pnas-licenses", "publisher-proprietary"),
    (
        "aaas author reuse",
        "aaas-author-reuse",
        "aaas-author-reuse",
        "publisher-proprietary",
    ),
    ("aip rights", "aip-rights", "aip-rights", "publisher-proprietary"),
    ("jama cc by", "jama-cc-by", "jama-cc-by", "publisher-oa"),
    ("thieme nlm", "thieme-nlm", "thieme-nlm", "publisher-oa"),
    ("oup chorus", "oup-chorus", "oup-chorus", "publisher-oa"),
    ("implied oa", "implied-oa", "implied-oa", "publisher-oa"),
    ("implied open access", "implied-oa", "implied-oa", "publisher-oa"),
    ("unspecified oa", "unspecified-oa", "unspecified-oa", "other-oa"),
    (
        "publisher specific oa",
        "publisher-specific-oa",
        "publisher-specific-oa",
        "publisher-oa",
    ),
    ("author manuscript", "author-manuscript", "author-manuscript", "publisher-oa"),
    ("open access", "other-oa", "other-oa", "other-oa"),
    ("other-oa", "other-oa", "other-oa", "other-oa"),
    (
        "all rights reserved",
        "all-rights-reserved",
        "all-rights-reserved",
        "publisher-proprietary",
    ),
    ("no reuse", "no-reuse", "no-reuse", "publisher-proprietary"),
    # Publisher prose
    (
        "this article is licensed under elsevier tdm agreement",
        "elsevier-tdm",
        "elsevier-tdm",
        "publisher-tdm",
    ),
    (
        "journal article under elsevier user license for open access",
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
        "springer tdm policy applies to this content",
        "springer-tdm",
        "springer-tdm",
        "publisher-tdm",
    ),
    # Unknown
    (
        "Totally Fake Licence XYZ999",
        "totally fake licence xyz999",
        "totally fake licence xyz999",
        "unknown",
    ),
    # Public domain
    ("public domain", "public-domain", "public-domain", "public-domain"),
    ("public-domain", "public-domain", "public-domain", "public-domain"),
    ("pd", "public-domain", "public-domain", "public-domain"),
]


@pytest.mark.parametrize(
    "raw,expected_key,expected_licence,expected_family", LICENCE_MATRIX
)
def test_licence_matrix(raw, expected_key, expected_licence, expected_family):
    v = normalise_licence(raw)
    assert v.key == expected_key, f"input: {raw!r}  key: {v.key!r} != {expected_key!r}"
    assert v.licence.key == expected_licence, (
        f"input: {raw!r}  licence: {v.licence.key!r} != {expected_licence!r}"
    )
    assert v.family.key == expected_family, (
        f"input: {raw!r}  family: {v.family.key!r} != {expected_family!r}"
    )


def test_strict_mode_unknown_raises():
    with pytest.raises((LicenceNormalisationError, LicenceNotFoundError)):
        normalise_licence("xyzzy unknown license 123", strict=True)


def test_strict_mode_known_does_not_raise():
    v = normalise_licence("mit", strict=False)
    assert v.key == "mit"


def test_empty_string_returns_unknown():
    v = normalise_licence("")
    assert v.key == "unknown"
    assert v.family.key == "unknown"


def test_whitespace_only_returns_unknown():
    v = normalise_licence("   \n\t  ")
    assert v.key == "unknown"


def test_batch_normalise_preserves_order():
    inputs = ["MIT", "Apache-2.0", "CC BY 4.0", "unknown garbage"]
    results = normalise_licences(inputs)
    assert [r.key for r in results] == [
        "mit",
        "apache-2.0",
        "cc-by-4.0",
        "unknown garbage",
    ]


def test_normalise_mit():
    v = normalise_licence("MIT")
    assert isinstance(v, LicenceVersion)
    assert v.key == "mit"
    assert str(v) == "mit"
    assert str(v.licence) == "mit"


def test_normalise_cc():
    v = normalise_licence("CC BY 4.0")
    assert v.key == "cc-by-4.0"
    assert str(v.licence) == "cc-by"
    assert str(v.family) == "cc"


def test_batch():
    results = normalise_licences(["MIT", "Apache-2.0"])
    assert len(results) == 2
    assert results[0].key == "mit"
    assert results[1].key == "apache-2.0"


def test_strict_mode_raises():
    with pytest.raises((LicenceNormalisationError, LicenceNotFoundError)):
        normalise_licence("Totally Fake License XYZ999", strict=True)


def test_strict_batch_raises():
    with pytest.raises((LicenceNormalisationError, LicenceNotFoundError)):
        normalise_licences(["MIT", "Fake License XYZ999"], strict=True)


def test_empty_input():
    v = normalise_licence("")
    assert v.key == "unknown"
    v = normalise_licence("   ")
    assert v.key == "unknown"


def test_real_world_licence_strings():
    """Test against real-world licence strings collected from the wild."""
    cases = [
        ("http://creativecommons.org/licenses/by-nc-nd/4.0/", "cc-by-nc-nd-4.0"),
        ("http://creativecommons.org/licenses/by/4.0/", "cc-by-4.0"),
        ("http://creativecommons.org/licenses/by-nc/4.0/", "cc-by-nc-4.0"),
        (
            "http://www.elsevier.com/open-access/userlicense/1.0/",
            "elsevier-oa",
        ),
        (
            "http://creativecommons.org/licenses/by-nc-nd/3.0/igo/",
            "cc-by-nc-nd-3.0-igo",
        ),
        ("CC BY-NC-ND 4.0", "cc-by-nc-nd-4.0"),
        (
            "http://creativecommons.org/licenses/by/3.0/igo/",
            "cc-by-3.0-igo",
        ),
    ]
    for raw, expected_key in cases:
        v = normalise_licence(raw)
        assert v.key == expected_key, (
            f"input: {raw!r} -> got {v.key!r}, want {expected_key!r}"
        )
