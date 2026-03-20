"""Enum definitions for the three-level license hierarchy.

The enum values are sourced from the curated SPDX and OpenDefinition subsets
in ``src/license_normaliser/data/``. They are the authoritative set of
supported license identifiers.

Family → Name → Version (3-level hierarchy)
---------------------------------------------
CC licenses:  family="cc",   name="cc-by",       version="cc-by-4.0"
GPL/AGPL/LGPL: family="gpl",  name="gpl-3.0-only", version="gpl-3.0-only"
Other SPDX:    family=osi,    name=<version_key>, version=<version_key>
"""

from __future__ import annotations

from enum import Enum

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenseFamilyEnum",
    "LicenseNameEnum",
    "LicenseVersionEnum",
)


class LicenseFamilyEnum(Enum):
    CC = "cc"
    COPYLEFT = "copyleft"
    DATA = "data"
    OSI = "osi"
    MPL = "mpl"
    UNKNOWN = "unknown"


class LicenseNameEnum(Enum):
    AGPL_3_0 = "agpl-3.0"
    AGPL_3_0_ONLY = "agpl-3.0-only"
    AGPL_3_0_OR_LATER = "agpl-3.0-or-later"
    APACHE_2_0 = "apache-2.0"
    BSD_2_CLAUSE = "bsd-2-clause"
    BSD_3_CLAUSE = "bsd-3-clause"
    CC0 = "cc0"
    CC_BY = "cc-by"
    CC_BY_NC = "cc-by-nc"
    CC_BY_NC_ND = "cc-by-nc-nd"
    CC_BY_NC_SA = "cc-by-nc-sa"
    CC_BY_ND = "cc-by-nd"
    CC_BY_SA = "cc-by-sa"
    GPL_2_0 = "gpl-2.0"
    GPL_2_0_ONLY = "gpl-2.0-only"
    GPL_2_0_OR_LATER = "gpl-2.0-or-later"
    GPL_3_0 = "gpl-3.0"
    GPL_3_0_ONLY = "gpl-3.0-only"
    GPL_3_0_OR_LATER = "gpl-3.0-or-later"
    ISC = "isc"
    LGPL_2_1 = "lgpl-2.1"
    LGPL_2_1_ONLY = "lgpl-2.1-only"
    LGPL_2_1_OR_LATER = "lgpl-2.1-or-later"
    LGPL_3_0 = "lgpl-3.0"
    LGPL_3_0_ONLY = "lgpl-3.0-only"
    LGPL_3_0_OR_LATER = "lgpl-3.0-or-later"
    MIT = "mit"
    MPL_2_0 = "mpl-2.0"
    ODC_BY = "odc-by"
    ODBL = "odbl"
    PDDL = "pddl"
    UNLICENSE = "unlicense"
    WTFPL = "wtfpl"
    ZLIB = "zlib"
    UNKNOWN = "unknown"


class LicenseVersionEnum(Enum):
    AGPL_3_0 = "agpl-3.0"
    AGPL_3_0_ONLY = "agpl-3.0-only"
    AGPL_3_0_OR_LATER = "agpl-3.0-or-later"
    APACHE_2_0 = "apache-2.0"
    BSD_2_CLAUSE = "bsd-2-clause"
    BSD_3_CLAUSE = "bsd-3-clause"
    CC_BY_1_0 = "cc-by-1.0"
    CC_BY_2_0 = "cc-by-2.0"
    CC_BY_2_5 = "cc-by-2.5"
    CC_BY_3_0 = "cc-by-3.0"
    CC_BY_4_0 = "cc-by-4.0"
    CC_BY_NC_2_0 = "cc-by-nc-2.0"
    CC_BY_NC_2_5 = "cc-by-nc-2.5"
    CC_BY_NC_3_0 = "cc-by-nc-3.0"
    CC_BY_NC_4_0 = "cc-by-nc-4.0"
    CC_BY_NC_ND_2_0 = "cc-by-nc-nd-2.0"
    CC_BY_NC_ND_2_5 = "cc-by-nc-nd-2.5"
    CC_BY_NC_ND_3_0 = "cc-by-nc-nd-3.0"
    CC_BY_NC_ND_4_0 = "cc-by-nc-nd-4.0"
    CC_BY_NC_SA_2_0 = "cc-by-nc-sa-2.0"
    CC_BY_NC_SA_2_5 = "cc-by-nc-sa-2.5"
    CC_BY_NC_SA_3_0 = "cc-by-nc-sa-3.0"
    CC_BY_NC_SA_4_0 = "cc-by-nc-sa-4.0"
    CC_BY_ND_2_0 = "cc-by-nd-2.0"
    CC_BY_ND_3_0 = "cc-by-nd-3.0"
    CC_BY_ND_4_0 = "cc-by-nd-4.0"
    CC_BY_SA_2_0 = "cc-by-sa-2.0"
    CC_BY_SA_2_5 = "cc-by-sa-2.5"
    CC_BY_SA_3_0 = "cc-by-sa-3.0"
    CC_BY_SA_4_0 = "cc-by-sa-4.0"
    CC0_1_0 = "cc0-1.0"
    GPL_2_0 = "gpl-2.0"
    GPL_2_0_ONLY = "gpl-2.0-only"
    GPL_2_0_OR_LATER = "gpl-2.0-or-later"
    GPL_3_0 = "gpl-3.0"
    GPL_3_0_ONLY = "gpl-3.0-only"
    GPL_3_0_OR_LATER = "gpl-3.0-or-later"
    ISC = "isc"
    LGPL_2_1 = "lgpl-2.1"
    LGPL_2_1_ONLY = "lgpl-2.1-only"
    LGPL_2_1_OR_LATER = "lgpl-2.1-or-later"
    LGPL_3_0 = "lgpl-3.0"
    LGPL_3_0_ONLY = "lgpl-3.0-only"
    LGPL_3_0_OR_LATER = "lgpl-3.0-or-later"
    MIT = "mit"
    MPL_2_0 = "mpl-2.0"
    ODC_BY_1_0 = "odc-by-1.0"
    ODBL_1_0 = "odbl-1.0"
    PDDL_1_0 = "pddl-1.0"
    UNLICENSE = "unlicense"
    WTFPL = "wtfpl"
    ZLIB = "zlib"
