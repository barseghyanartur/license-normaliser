"""License Normaliser - Comprehensive license normalisation with a
three-level hierarchy."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Optional

from ._enums import (
    LicenseFamilyEnum,
    LicenseNameEnum,
    LicenseVersionEnum,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "LicenseFamily",
    "LicenseName",
    "LicenseVersion",
    "normalise_license",
    "normalise_licenses",
)

_WHITESPACE_RE = re.compile(r"\s+")


# ===========================================================================
# Level 1 – LicenseFamily
# ===========================================================================

# Map enum value to LicenseFamilyEnum for internal use
_FAMILY_ENUMS: dict[str, LicenseFamilyEnum] = {e.value: e for e in LicenseFamilyEnum}


@dataclass(frozen=True)
class LicenseFamily:
    """License family - broad bucket like 'cc', 'osi', 'copyleft'."""

    key: str

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"LicenseFamily({self.key!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenseFamily):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        if isinstance(other, LicenseFamilyEnum):
            return self.key == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def enum(self) -> Optional[LicenseFamilyEnum]:
        """Return the corresponding enum if found."""
        return _FAMILY_ENUMS.get(self.key)


# Pre-built singletons
_FAMILIES: dict[str, LicenseFamily] = {
    e.value: LicenseFamily(key=e.value) for e in LicenseFamilyEnum
}


def _fam(key: str) -> LicenseFamily:
    """Get LicenseFamily by key string."""
    return _FAMILIES.get(key, _FAMILIES["unknown"])


# ===========================================================================
# Level 2 – LicenseName  (version-stripped, IGO-collapsed)
# ===========================================================================

# Map enum value to LicenseNameEnum for internal use
_NAME_ENUMS: dict[str, LicenseNameEnum] = {e.value: e for e in LicenseNameEnum}


@dataclass(frozen=True)
class LicenseName:
    """License name - version-free like 'cc-by', 'mit'."""

    key: str
    family: LicenseFamily

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"LicenseName({self.key!r}, family={self.family.key!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenseName):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        if isinstance(other, LicenseNameEnum):
            return self.key == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def enum(self) -> Optional[LicenseNameEnum]:
        """Return the corresponding enum if found."""
        return _NAME_ENUMS.get(self.key)


# Registry: name enum -> family enum
_NAME_REGISTRY: dict[LicenseNameEnum, LicenseFamilyEnum] = {
    # Creative Commons – public domain
    LicenseNameEnum.CC0: LicenseFamilyEnum.CC0,
    LicenseNameEnum.CC_PDM: LicenseFamilyEnum.PUBLIC_DOMAIN,
    # Creative Commons – standard variants
    LicenseNameEnum.CC_BY: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_SA: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_ND: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_NC: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_NC_SA: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_NC_ND: LicenseFamilyEnum.CC,
    # Creative Commons – IGO sub-variants
    LicenseNameEnum.CC_BY_IGO: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_SA_IGO: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_ND_IGO: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_NC_IGO: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_NC_SA_IGO: LicenseFamilyEnum.CC,
    LicenseNameEnum.CC_BY_NC_ND_IGO: LicenseFamilyEnum.CC,
    # OSI permissive
    LicenseNameEnum.MIT: LicenseFamilyEnum.OSI,
    LicenseNameEnum.APACHE: LicenseFamilyEnum.OSI,
    LicenseNameEnum.BSD_2_CLAUSE: LicenseFamilyEnum.OSI,
    LicenseNameEnum.BSD_3_CLAUSE: LicenseFamilyEnum.OSI,
    LicenseNameEnum.ISC: LicenseFamilyEnum.OSI,
    LicenseNameEnum.MPL: LicenseFamilyEnum.OSI,
    # Copyleft
    LicenseNameEnum.GPL_2: LicenseFamilyEnum.COPYLEFT,
    LicenseNameEnum.GPL_3: LicenseFamilyEnum.COPYLEFT,
    LicenseNameEnum.AGPL_3: LicenseFamilyEnum.COPYLEFT,
    LicenseNameEnum.LGPL_2_1: LicenseFamilyEnum.COPYLEFT,
    LicenseNameEnum.LGPL_3: LicenseFamilyEnum.COPYLEFT,
    # Open Data
    LicenseNameEnum.ODBL: LicenseFamilyEnum.OPEN_DATA,
    LicenseNameEnum.ODC_BY: LicenseFamilyEnum.OPEN_DATA,
    LicenseNameEnum.PDDL: LicenseFamilyEnum.OPEN_DATA,
    LicenseNameEnum.FAL: LicenseFamilyEnum.OTHER_OA,
    # Publisher proprietary – Elsevier
    LicenseNameEnum.ELSEVIER_OA: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.ELSEVIER_TDM: LicenseFamilyEnum.PUBLISHER_TDM,
    # Publisher proprietary – Wiley
    LicenseNameEnum.WILEY_TDM: LicenseFamilyEnum.PUBLISHER_TDM,
    LicenseNameEnum.WILEY_VOR: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    LicenseNameEnum.WILEY_AM: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    LicenseNameEnum.WILEY_TERMS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – Springer Nature
    LicenseNameEnum.SPRINGER_TDM: LicenseFamilyEnum.PUBLISHER_TDM,
    LicenseNameEnum.SPRINGERNATURE_TDM: LicenseFamilyEnum.PUBLISHER_TDM,
    # Publisher proprietary – Taylor & Francis
    LicenseNameEnum.TANDF_TERMS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – OUP
    LicenseNameEnum.OUP_CHORUS: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.OUP_TERMS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – SAGE
    LicenseNameEnum.SAGE_PERMISSIONS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – ACS
    LicenseNameEnum.ACS_AUTHORCHOICE: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.ACS_AUTHORCHOICE_CCBY: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.ACS_AUTHORCHOICE_CCBYNCND: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.ACS_AUTHORCHOICE_NIH: LicenseFamilyEnum.PUBLISHER_OA,
    # Publisher proprietary – RSC
    LicenseNameEnum.RSC_TERMS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – IOP
    LicenseNameEnum.IOP_TDM: LicenseFamilyEnum.PUBLISHER_TDM,
    LicenseNameEnum.IOP_COPYRIGHT: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – BMJ
    LicenseNameEnum.BMJ_COPYRIGHT: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – AAAS / Science
    LicenseNameEnum.AAAS_AUTHOR_REUSE: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – PNAS
    LicenseNameEnum.PNAS_LICENSES: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – APS
    LicenseNameEnum.APS_DEFAULT: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    LicenseNameEnum.APS_TDM: LicenseFamilyEnum.PUBLISHER_TDM,
    # Publisher proprietary – Cambridge
    LicenseNameEnum.CUP_TERMS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – AIP
    LicenseNameEnum.AIP_RIGHTS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – JAMA
    LicenseNameEnum.JAMA_CC_BY: LicenseFamilyEnum.PUBLISHER_OA,
    # Publisher proprietary – De Gruyter
    LicenseNameEnum.DEGRUYTER_TERMS: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    # Publisher proprietary – Thieme
    LicenseNameEnum.THIEME_NLM: LicenseFamilyEnum.PUBLISHER_OA,
    # Catch-all
    LicenseNameEnum.PUBLIC_DOMAIN_MARK: LicenseFamilyEnum.PUBLIC_DOMAIN,
    LicenseNameEnum.OTHER_OA: LicenseFamilyEnum.OTHER_OA,
    LicenseNameEnum.PUBLISHER_SPECIFIC_OA: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.UNSPECIFIED_OA: LicenseFamilyEnum.OTHER_OA,
    LicenseNameEnum.OPEN_ACCESS: LicenseFamilyEnum.OTHER_OA,
    LicenseNameEnum.IMPLIED_OA: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.AUTHOR_MANUSCRIPT: LicenseFamilyEnum.PUBLISHER_OA,
    LicenseNameEnum.ALL_RIGHTS_RESERVED: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    LicenseNameEnum.NO_REUSE: LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    LicenseNameEnum.UNKNOWN: LicenseFamilyEnum.UNKNOWN,
}


@lru_cache(maxsize=512)
def _get_license_name(key: str) -> LicenseName:
    """Get LicenseName by key string, with caching."""
    name_enum = LicenseNameEnum(key)
    fam_enum = _NAME_REGISTRY.get(name_enum, LicenseFamilyEnum.UNKNOWN)
    return LicenseName(key=key, family=_fam(fam_enum.value))


# ===========================================================================
# Level 3 – LicenseVersion  (the fully resolved leaf node)
# ===========================================================================

# Map enum value to LicenseVersionEnum for internal use
_VERSION_ENUMS: dict[str, LicenseVersionEnum] = {e.value: e for e in LicenseVersionEnum}

# Registry: version key -> (canonical_url, name_enum)
_VERSION_REGISTRY: dict[str, tuple[Optional[str], LicenseNameEnum]] = {
    # CC Zero
    "cc0": ("https://creativecommons.org/publicdomain/zero/1.0/", LicenseNameEnum.CC0),
    "cc0-1.0": (
        "https://creativecommons.org/publicdomain/zero/1.0/",
        LicenseNameEnum.CC0,
    ),
    "cc-zero": (
        "https://creativecommons.org/publicdomain/zero/1.0/",
        LicenseNameEnum.CC0,
    ),
    "cc-pdm": (
        "https://creativecommons.org/publicdomain/mark/1.0/",
        LicenseNameEnum.CC_PDM,
    ),
    # CC BY
    "cc-by": ("https://creativecommons.org/licenses/by/4.0/", LicenseNameEnum.CC_BY),
    "cc-by-4.0": (
        "https://creativecommons.org/licenses/by/4.0/",
        LicenseNameEnum.CC_BY,
    ),
    "cc-by-3.0": (
        "https://creativecommons.org/licenses/by/3.0/",
        LicenseNameEnum.CC_BY,
    ),
    "cc-by-2.5": (
        "https://creativecommons.org/licenses/by/2.5/",
        LicenseNameEnum.CC_BY,
    ),
    "cc-by-2.0": (
        "https://creativecommons.org/licenses/by/2.0/",
        LicenseNameEnum.CC_BY,
    ),
    "cc-by-1.0": (
        "https://creativecommons.org/licenses/by/1.0/",
        LicenseNameEnum.CC_BY,
    ),
    # CC BY-SA
    "cc-by-sa": (
        "https://creativecommons.org/licenses/by-sa/4.0/",
        LicenseNameEnum.CC_BY_SA,
    ),
    "cc-by-sa-4.0": (
        "https://creativecommons.org/licenses/by-sa/4.0/",
        LicenseNameEnum.CC_BY_SA,
    ),
    "cc-by-sa-3.0": (
        "https://creativecommons.org/licenses/by-sa/3.0/",
        LicenseNameEnum.CC_BY_SA,
    ),
    "cc-by-sa-2.5": (
        "https://creativecommons.org/licenses/by-sa/2.5/",
        LicenseNameEnum.CC_BY_SA,
    ),
    "cc-by-sa-2.0": (
        "https://creativecommons.org/licenses/by-sa/2.0/",
        LicenseNameEnum.CC_BY_SA,
    ),
    # CC BY-ND
    "cc-by-nd": (
        "https://creativecommons.org/licenses/by-nd/4.0/",
        LicenseNameEnum.CC_BY_ND,
    ),
    "cc-by-nd-4.0": (
        "https://creativecommons.org/licenses/by-nd/4.0/",
        LicenseNameEnum.CC_BY_ND,
    ),
    "cc-by-nd-3.0": (
        "https://creativecommons.org/licenses/by-nd/3.0/",
        LicenseNameEnum.CC_BY_ND,
    ),
    "cc-by-nd-2.0": (
        "https://creativecommons.org/licenses/by-nd/2.0/",
        LicenseNameEnum.CC_BY_ND,
    ),
    # CC BY-NC
    "cc-by-nc": (
        "https://creativecommons.org/licenses/by-nc/4.0/",
        LicenseNameEnum.CC_BY_NC,
    ),
    "cc-by-nc-4.0": (
        "https://creativecommons.org/licenses/by-nc/4.0/",
        LicenseNameEnum.CC_BY_NC,
    ),
    "cc-by-nc-3.0": (
        "https://creativecommons.org/licenses/by-nc/3.0/",
        LicenseNameEnum.CC_BY_NC,
    ),
    "cc-by-nc-2.5": (
        "https://creativecommons.org/licenses/by-nc/2.5/",
        LicenseNameEnum.CC_BY_NC,
    ),
    "cc-by-nc-2.0": (
        "https://creativecommons.org/licenses/by-nc/2.0/",
        LicenseNameEnum.CC_BY_NC,
    ),
    # CC BY-NC-SA
    "cc-by-nc-sa": (
        "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        LicenseNameEnum.CC_BY_NC_SA,
    ),
    "cc-by-nc-sa-4.0": (
        "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        LicenseNameEnum.CC_BY_NC_SA,
    ),
    "cc-by-nc-sa-3.0": (
        "https://creativecommons.org/licenses/by-nc-sa/3.0/",
        LicenseNameEnum.CC_BY_NC_SA,
    ),
    "cc-by-nc-sa-2.5": (
        "https://creativecommons.org/licenses/by-nc-sa/2.5/",
        LicenseNameEnum.CC_BY_NC_SA,
    ),
    "cc-by-nc-sa-2.0": (
        "https://creativecommons.org/licenses/by-nc-sa/2.0/",
        LicenseNameEnum.CC_BY_NC_SA,
    ),
    # CC BY-NC-ND
    "cc-by-nc-nd": (
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        LicenseNameEnum.CC_BY_NC_ND,
    ),
    "cc-by-nc-nd-4.0": (
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        LicenseNameEnum.CC_BY_NC_ND,
    ),
    "cc-by-nc-nd-3.0": (
        "https://creativecommons.org/licenses/by-nc-nd/3.0/",
        LicenseNameEnum.CC_BY_NC_ND,
    ),
    "cc-by-nc-nd-2.5": (
        "https://creativecommons.org/licenses/by-nc-nd/2.5/",
        LicenseNameEnum.CC_BY_NC_ND,
    ),
    "cc-by-nc-nd-2.0": (
        "https://creativecommons.org/licenses/by-nc-nd/2.0/",
        LicenseNameEnum.CC_BY_NC_ND,
    ),
    # CC IGO variants (4.0 IGO URLs don't exist; handled by structural regex)
    "cc-by-3.0-igo": (
        "https://creativecommons.org/licenses/by/3.0/igo/",
        LicenseNameEnum.CC_BY_IGO,
    ),
    "cc-by-nc-sa-3.0-igo": (
        "https://creativecommons.org/licenses/by-nc-sa/3.0/igo/",
        LicenseNameEnum.CC_BY_NC_SA_IGO,
    ),
    "cc-by-nc-nd-3.0-igo": (
        "https://creativecommons.org/licenses/by-nc-nd/3.0/igo/",
        LicenseNameEnum.CC_BY_NC_ND_IGO,
    ),
    # OSI permissive
    "mit": ("https://opensource.org/licenses/MIT", LicenseNameEnum.MIT),
    "apache-2.0": (
        "https://www.apache.org/licenses/LICENSE-2.0",
        LicenseNameEnum.APACHE,
    ),
    "bsd-2-clause": (
        "https://opensource.org/licenses/BSD-2-Clause",
        LicenseNameEnum.BSD_2_CLAUSE,
    ),
    "bsd-3-clause": (
        "https://opensource.org/licenses/BSD-3-Clause",
        LicenseNameEnum.BSD_3_CLAUSE,
    ),
    "isc": ("https://opensource.org/licenses/ISC", LicenseNameEnum.ISC),
    "mpl-2.0": ("https://www.mozilla.org/en-US/MPL/2.0/", LicenseNameEnum.MPL),
    # Copyleft
    "gpl-2.0": (
        "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
        LicenseNameEnum.GPL_2,
    ),
    "gpl-2.0-only": (
        "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
        LicenseNameEnum.GPL_2,
    ),
    "gpl-3.0": ("https://www.gnu.org/licenses/gpl-3.0.html", LicenseNameEnum.GPL_3),
    "gpl-3.0-only": (
        "https://www.gnu.org/licenses/gpl-3.0.html",
        LicenseNameEnum.GPL_3,
    ),
    "agpl-3.0": ("https://www.gnu.org/licenses/agpl-3.0.html", LicenseNameEnum.AGPL_3),
    "agpl-3.0-only": (
        "https://www.gnu.org/licenses/agpl-3.0.html",
        LicenseNameEnum.AGPL_3,
    ),
    "lgpl-2.1": (
        "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html",
        LicenseNameEnum.LGPL_2_1,
    ),
    "lgpl-2.1-only": (
        "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html",
        LicenseNameEnum.LGPL_2_1,
    ),
    "lgpl-3.0": ("https://www.gnu.org/licenses/lgpl-3.0.html", LicenseNameEnum.LGPL_3),
    "lgpl-3.0-only": (
        "https://www.gnu.org/licenses/lgpl-3.0.html",
        LicenseNameEnum.LGPL_3,
    ),
    # Open Data
    "odbl": ("https://opendatacommons.org/licenses/odbl/1-0/", LicenseNameEnum.ODBL),
    "odc-by": ("https://opendatacommons.org/licenses/by/1-0/", LicenseNameEnum.ODC_BY),
    "pddl": ("https://opendatacommons.org/licenses/pddl/1-0/", LicenseNameEnum.PDDL),
    "fal": ("https://artlibre.org/licence/lal/en/", LicenseNameEnum.FAL),
    "fldl": ("https://artlibre.org/licence/lal/en/", LicenseNameEnum.FAL),
    # Publisher - Elsevier
    "elsevier-oa": (
        "https://www.elsevier.com/open-access/userlicense/1.0/",
        LicenseNameEnum.ELSEVIER_OA,
    ),
    "elsevier-tdm": (
        "https://www.elsevier.com/tdm/userlicense/1.0/",
        LicenseNameEnum.ELSEVIER_TDM,
    ),
    # Publisher - Wiley
    "wiley-tdm": (
        "http://doi.wiley.com/10.1002/tdm_license_1",
        LicenseNameEnum.WILEY_TDM,
    ),
    "wiley-tdm-1.1": (
        "http://doi.wiley.com/10.1002/tdm_license_1.1",
        LicenseNameEnum.WILEY_TDM,
    ),
    "wiley-vor": (
        "http://onlinelibrary.wiley.com/termsAndConditions#vor",
        LicenseNameEnum.WILEY_VOR,
    ),
    "wiley-am": (
        "http://onlinelibrary.wiley.com/termsAndConditions#am",
        LicenseNameEnum.WILEY_AM,
    ),
    "wiley-terms": (
        "https://onlinelibrary.wiley.com/terms-and-conditions",
        LicenseNameEnum.WILEY_TERMS,
    ),
    # Publisher - Springer
    "springer-tdm": ("https://www.springer.com/tdm", LicenseNameEnum.SPRINGER_TDM),
    "springernature-tdm": (
        "https://www.springernature.com/gp/researchers/text-and-data-mining",
        LicenseNameEnum.SPRINGERNATURE_TDM,
    ),
    # Publisher - Taylor & Francis
    "tandf-terms": (
        "https://www.tandfonline.com/action/showCopyRight",
        LicenseNameEnum.TANDF_TERMS,
    ),
    # Publisher - OUP
    "oup-chorus": (
        "https://academic.oup.com/journals/pages/open_access/funder_policies/"
        "chorus/standard_publication_model",
        LicenseNameEnum.OUP_CHORUS,
    ),
    "oup-terms": (
        "https://academic.oup.com/pages/standard-publication-reuse-rights",
        LicenseNameEnum.OUP_TERMS,
    ),
    # Publisher - SAGE
    "sage-permissions": (
        "https://us.sagepub.com/en-us/nam/journals-permissions",
        LicenseNameEnum.SAGE_PERMISSIONS,
    ),
    # Publisher - ACS
    "acs-authorchoice-ccby": (
        "https://pubs.acs.org/page/policy/authorchoice_ccby_termsofuse.html",
        LicenseNameEnum.ACS_AUTHORCHOICE_CCBY,
    ),
    "acs-authorchoice-ccbyncnd": (
        "https://pubs.acs.org/page/policy/authorchoice_ccbyncnd_termsofuse.html",
        LicenseNameEnum.ACS_AUTHORCHOICE_CCBYNCND,
    ),
    "acs-authorchoice": (
        "https://pubs.acs.org/page/policy/authorchoice_termsofuse.html",
        LicenseNameEnum.ACS_AUTHORCHOICE,
    ),
    "acs-authorchoice-nih": (
        "https://pubs.acs.org/page/policy/acs_authorchoice_with_nih_"
        "addendum_termsofuse.html",
        LicenseNameEnum.ACS_AUTHORCHOICE_NIH,
    ),
    # Publisher - RSC
    "rsc-terms": (
        "https://www.rsc.org/journals-books-databases/journal-authors-reviewers/"
        "licences-copyright-permissions/",
        LicenseNameEnum.RSC_TERMS,
    ),
    # Publisher - IOP
    "iop-tdm": (
        "https://iopscience.iop.org/info/page/text-and-data-mining",
        LicenseNameEnum.IOP_TDM,
    ),
    "iop-copyright": (
        "https://iopscience.iop.org/page/copyright",
        LicenseNameEnum.IOP_COPYRIGHT,
    ),
    # Publisher - BMJ
    "bmj-copyright": (
        "https://www.bmj.com/company/legal-stuff/copyright-notice/",
        LicenseNameEnum.BMJ_COPYRIGHT,
    ),
    # Publisher - AAAS
    "aaas-author-reuse": (
        "https://www.science.org/content/page/science-licenses-journal-article-reuse",
        LicenseNameEnum.AAAS_AUTHOR_REUSE,
    ),
    # Publisher - PNAS
    "pnas-licenses": (
        "https://www.pnas.org/site/aboutpnas/licenses.xhtml",
        LicenseNameEnum.PNAS_LICENSES,
    ),
    # Publisher - APS
    "aps-default": (
        "https://link.aps.org/licenses/aps-default-license",
        LicenseNameEnum.APS_DEFAULT,
    ),
    "aps-tdm": (
        "https://link.aps.org/licenses/aps-default-text-mining-license",
        LicenseNameEnum.APS_TDM,
    ),
    # Publisher - Cambridge
    "cup-terms": ("https://www.cambridge.org/core/terms", LicenseNameEnum.CUP_TERMS),
    # Publisher - AIP
    "aip-rights": (
        "https://publishing.aip.org/authors/rights-and-permissions",
        LicenseNameEnum.AIP_RIGHTS,
    ),
    # Publisher - JAMA
    "jama-cc-by": (
        "https://jamanetwork.com/pages/cc-by-license-permissions",
        LicenseNameEnum.JAMA_CC_BY,
    ),
    # Publisher - De Gruyter
    "degruyter-terms": (
        "https://www.degruyter.com/dg/page/496",
        LicenseNameEnum.DEGRUYTER_TERMS,
    ),
    # Publisher - Thieme
    "thieme-nlm": (
        "https://www.thieme.de/statics/dokumente/thieme/final/de/dokumente/"
        "sw_oa/nlm_license_terms_thieme.pdf",
        LicenseNameEnum.THIEME_NLM,
    ),
    # Catch-all
    "public-domain": (None, LicenseNameEnum.PUBLIC_DOMAIN_MARK),
    "other-oa": (None, LicenseNameEnum.OTHER_OA),
    "publisher-specific-oa": (None, LicenseNameEnum.PUBLISHER_SPECIFIC_OA),
    "unspecified-oa": (None, LicenseNameEnum.UNSPECIFIED_OA),
    "open-access": (None, LicenseNameEnum.OPEN_ACCESS),
    "implied-oa": (None, LicenseNameEnum.IMPLIED_OA),
    "author-manuscript": (None, LicenseNameEnum.AUTHOR_MANUSCRIPT),
    "all-rights-reserved": (None, LicenseNameEnum.ALL_RIGHTS_RESERVED),
    "no-reuse": (None, LicenseNameEnum.NO_REUSE),
    "unknown": (None, LicenseNameEnum.UNKNOWN),
}


@dataclass
class LicenseVersion:
    """Fully-resolved leaf node - contains version like 'cc-by-4.0'."""

    key: str
    url: Optional[str]
    license: LicenseName

    def __post_init__(self) -> None:
        self.key = self.key.lower()

    @property
    def family(self) -> LicenseFamily:
        """Shortcut: version.family == version.license.family"""
        return self.license.family

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return (
            f"LicenseVersion(key={self.key!r}, "
            f"license={self.license.key!r}, "
            f"family={self.license.family.key!r})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LicenseVersion):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        if isinstance(other, LicenseVersionEnum):
            return self.key == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def enum(self) -> Optional[LicenseVersionEnum]:
        """Return the corresponding enum if found."""
        return _VERSION_ENUMS.get(self.key)

    def is_family(self, family: LicenseFamilyEnum) -> bool:
        """Check if this license belongs to the given family enum."""
        return self.family.key == family.value

    def is_name(self, name: LicenseNameEnum) -> bool:
        """Check if this license matches the given name enum."""
        return self.license.key == name.value

    def is_version(self, version: LicenseVersionEnum) -> bool:
        """Check if this license matches the given version enum."""
        return self.key == version.value


def _make(version_key: str) -> LicenseVersion:
    """Build a LicenseVersion from a key that exists in _VERSION_REGISTRY."""
    url, name_enum = _VERSION_REGISTRY[version_key]
    return LicenseVersion(
        key=version_key,
        url=url,
        license=_get_license_name(name_enum.value),
    )


def _make_unknown(raw_key: str) -> LicenseVersion:
    return LicenseVersion(
        key=raw_key,
        url=None,
        license=_get_license_name("unknown"),
    )


def _make_synthetic(version_key: str, url: str, name_key: str) -> LicenseVersion:
    """For CC URLs not explicitly listed – synthesised at runtime."""
    try:
        name_enum = LicenseNameEnum(name_key)
    except ValueError:
        name_enum = LicenseNameEnum.UNKNOWN
    if name_enum not in _NAME_REGISTRY:
        _NAME_REGISTRY[name_enum] = LicenseFamilyEnum.CC
        _get_license_name.cache_clear()
    return LicenseVersion(
        key=version_key,
        url=url,
        license=_get_license_name(name_key),
    )


# ===========================================================================
# Alias table  →  version key in _VERSION_REGISTRY
# ===========================================================================

_ALIASES: dict[str, str] = {
    # CC short prose
    "creative commons zero": "cc0",
    "creative commons public domain": "cc-pdm",
    "cc0 1.0": "cc0-1.0",
    "cc by": "cc-by",
    "cc by 4.0": "cc-by-4.0",
    "cc by 3.0": "cc-by-3.0",
    "cc by 2.5": "cc-by-2.5",
    "cc by 2.0": "cc-by-2.0",
    "cc-by-4": "cc-by-4.0",
    "cc-by-3": "cc-by-3.0",
    "cc by-sa": "cc-by-sa",
    "cc by-sa 4.0": "cc-by-sa-4.0",
    "cc by-sa 3.0": "cc-by-sa-3.0",
    "cc by-nd": "cc-by-nd",
    "cc by-nd 4.0": "cc-by-nd-4.0",
    "cc by-nd 3.0": "cc-by-nd-3.0",
    "cc by-nc": "cc-by-nc",
    "cc by-nc 4.0": "cc-by-nc-4.0",
    "cc by-nc 3.0": "cc-by-nc-3.0",
    "cc by-nc-sa": "cc-by-nc-sa",
    "cc by-nc-sa 4.0": "cc-by-nc-sa-4.0",
    "cc by-nc-sa 3.0": "cc-by-nc-sa-3.0",
    "cc by-nc-nd": "cc-by-nc-nd",
    "cc by-nc-nd 4.0": "cc-by-nc-nd-4.0",
    "cc by-nc-nd 3.0": "cc-by-nc-nd-3.0",
    "cc by-nc-nd 3.0 igo": "cc-by-nc-nd-3.0-igo",
    "cc-by-nc-nd 4.0": "cc-by-nc-nd-4.0",
    # Fully spelled-out
    "creative commons attribution": "cc-by",
    "creative commons attribution 4.0": "cc-by-4.0",
    "creative commons attribution 3.0": "cc-by-3.0",
    "creative commons attribution license": "cc-by",
    "creative commons attribution 4.0 international": "cc-by-4.0",
    "creative commons attribution 4.0 international license": "cc-by-4.0",
    "creative commons attribution-noncommercial": "cc-by-nc",
    "creative commons attribution-noncommercial 4.0": "cc-by-nc-4.0",
    "creative commons attribution-noderivatives": "cc-by-nd",
    "creative commons attribution-sharealike": "cc-by-sa",
    "creative commons attribution-noncommercial-noderivatives 4.0": "cc-by-nc-nd-4.0",
    "creative commons attribution-noncommercial-noderivatives "
    "4.0 international": "cc-by-nc-nd-4.0",
    # OSI
    "apache": "apache-2.0",
    "apache license": "apache-2.0",
    "apache 2": "apache-2.0",
    "apache 2.0": "apache-2.0",
    "apache license 2.0": "apache-2.0",
    "mit license": "mit",
    "the mit license": "mit",
    "bsd": "bsd-3-clause",
    "bsd license": "bsd-3-clause",
    "mozilla": "mpl-2.0",
    "mozilla public license": "mpl-2.0",
    "isc license": "isc",
    # GPL family
    "gpl": "gpl-3.0",
    "gnu gpl": "gpl-3.0",
    "gnu gpl v2": "gpl-2.0",
    "gnu gpl v3": "gpl-3.0",
    "gpl-2.0+": "gpl-2.0",
    "gpl-3.0+": "gpl-3.0",
    "agpl": "agpl-3.0",
    "agpl-3.0+": "agpl-3.0",
    "lgpl": "lgpl-3.0",
    "lgpl-2.1+": "lgpl-2.1",
    "lgpl-3.0+": "lgpl-3.0",
    # Open data
    "odbl-1.0": "odbl",
    "open database license": "odbl",
    # Catch-all
    "public domain": "public-domain",
    "pd": "public-domain",
    "cc-zero": "cc0",
    "author manuscript": "author-manuscript",
    "all rights reserved": "all-rights-reserved",
    "no reuse": "no-reuse",
    "© the author(s)": "publisher-specific-oa",
    # Publisher shorthand
    "elsevier user license": "elsevier-oa",
    "wiley tdm license": "wiley-tdm",
    "acs authorchoice": "acs-authorchoice",
    "springer tdm": "springer-tdm",
    "springer nature tdm": "springernature-tdm",
}


# ===========================================================================
# URL → version key
# ===========================================================================


def _build_url_map() -> dict[str, str]:
    url_map: dict[str, str] = {}

    for vkey, (url, _) in _VERSION_REGISTRY.items():
        if url:
            url_map[url.rstrip("/").lower()] = vkey

    extras: dict[str, str] = {
        # CC BY
        "http://creativecommons.org/licenses/by/4.0": "cc-by-4.0",
        "http://creativecommons.org/licenses/by/4.0/": "cc-by-4.0",
        "http://creativecommons.org/licenses/by/3.0": "cc-by-3.0",
        "http://creativecommons.org/licenses/by/3.0/": "cc-by-3.0",
        "http://creativecommons.org/licenses/by/3.0/deed.en_us": "cc-by-3.0",
        "http://creativecommons.org/licenses/by/2.5": "cc-by-2.5",
        "http://creativecommons.org/licenses/by/2.5/": "cc-by-2.5",
        "http://creativecommons.org/licenses/by/2.0": "cc-by-2.0",
        "http://creativecommons.org/licenses/by/2.0/": "cc-by-2.0",
        "http://creativecommons.org/licenses/by/1.0": "cc-by-1.0",
        "http://creativecommons.org/licenses/by/1.0/": "cc-by-1.0",
        # CC BY-SA
        "http://creativecommons.org/licenses/by-sa/4.0": "cc-by-sa-4.0",
        "http://creativecommons.org/licenses/by-sa/4.0/": "cc-by-sa-4.0",
        "http://creativecommons.org/licenses/by-sa/3.0": "cc-by-sa-3.0",
        "http://creativecommons.org/licenses/by-sa/3.0/": "cc-by-sa-3.0",
        "http://creativecommons.org/licenses/by-sa/2.5/": "cc-by-sa-2.5",
        "http://creativecommons.org/licenses/by-sa/2.0/": "cc-by-sa-2.0",
        # CC BY-ND
        "http://creativecommons.org/licenses/by-nd/4.0": "cc-by-nd-4.0",
        "http://creativecommons.org/licenses/by-nd/4.0/": "cc-by-nd-4.0",
        "http://creativecommons.org/licenses/by-nd/3.0": "cc-by-nd-3.0",
        "http://creativecommons.org/licenses/by-nd/3.0/": "cc-by-nd-3.0",
        "http://creativecommons.org/licenses/by-nd/2.0/": "cc-by-nd-2.0",
        # CC BY-NC
        "http://creativecommons.org/licenses/by-nc/4.0": "cc-by-nc-4.0",
        "http://creativecommons.org/licenses/by-nc/4.0/": "cc-by-nc-4.0",
        "http://creativecommons.org/licenses/by-nc/3.0": "cc-by-nc-3.0",
        "http://creativecommons.org/licenses/by-nc/3.0/": "cc-by-nc-3.0",
        "http://creativecommons.org/licenses/by-nc/2.5/": "cc-by-nc-2.5",
        "http://creativecommons.org/licenses/by-nc/2.0/": "cc-by-nc-2.0",
        # CC BY-NC-SA
        "http://creativecommons.org/licenses/by-nc-sa/4.0": "cc-by-nc-sa-4.0",
        "http://creativecommons.org/licenses/by-nc-sa/4.0/": "cc-by-nc-sa-4.0",
        "http://creativecommons.org/licenses/by-nc-sa/3.0": "cc-by-nc-sa-3.0",
        "http://creativecommons.org/licenses/by-nc-sa/3.0/": "cc-by-nc-sa-3.0",
        "http://creativecommons.org/licenses/by-nc-sa/2.5/": "cc-by-nc-sa-2.5",
        "http://creativecommons.org/licenses/by-nc-sa/2.0/": "cc-by-nc-sa-2.0",
        # CC BY-NC-ND
        "http://creativecommons.org/licenses/by-nc-nd/4.0": "cc-by-nc-nd-4.0",
        "http://creativecommons.org/licenses/by-nc-nd/4.0/": "cc-by-nc-nd-4.0",
        "http://creativecommons.org/licenses/by-nc-nd/3.0": "cc-by-nc-nd-3.0",
        "http://creativecommons.org/licenses/by-nc-nd/3.0/": "cc-by-nc-nd-3.0",
        "http://creativecommons.org/licenses/by-nc-nd/2.5/": "cc-by-nc-nd-2.5",
        "http://creativecommons.org/licenses/by-nc-nd/2.0/": "cc-by-nc-nd-2.0",
        # CC IGO
        "http://creativecommons.org/licenses/by/3.0/igo": "cc-by-3.0-igo",
        "http://creativecommons.org/licenses/by/3.0/igo/": "cc-by-3.0-igo",
        "https://creativecommons.org/licenses/by/3.0/igo": "cc-by-3.0-igo",
        "http://creativecommons.org/licenses/by-nc-sa/3.0/igo": "cc-by-nc-sa-3.0-igo",
        "http://creativecommons.org/licenses/by-nc-sa/3.0/igo/": "cc-by-nc-sa-3.0-igo",
        "https://creativecommons.org/licenses/by-nc-sa/3.0/igo": "cc-by-nc-sa-3.0-igo",
        "http://creativecommons.org/licenses/by-nc-nd/3.0/igo": "cc-by-nc-nd-3.0-igo",
        "http://creativecommons.org/licenses/by-nc-nd/3.0/igo/": "cc-by-nc-nd-3.0-igo",
        "https://creativecommons.org/licenses/by-nc-nd/3.0/igo": "cc-by-nc-nd-3.0-igo",
        "https://creativecommons.org/licenses/by-nc-nd/3.0/igo/": "cc-by-nc-nd-3.0-igo",
        # CC Zero / PDM
        "http://creativecommons.org/publicdomain/zero/1.0": "cc0",
        "http://creativecommons.org/publicdomain/zero/1.0/": "cc0",
        "https://creativecommons.org/publicdomain/zero/1.0": "cc0",
        "http://creativecommons.org/publicdomain/mark/1.0": "cc-pdm",
        "http://creativecommons.org/publicdomain/mark/1.0/": "cc-pdm",
        # GNU
        "http://www.gnu.org/licenses/gpl-2.0": "gpl-2.0",
        "http://www.gnu.org/licenses/gpl-2.0.html": "gpl-2.0",
        "http://www.gnu.org/licenses/gpl-3.0": "gpl-3.0",
        "http://www.gnu.org/licenses/gpl-3.0.html": "gpl-3.0",
        "http://www.gnu.org/licenses/agpl-3.0": "agpl-3.0",
        "http://www.gnu.org/licenses/agpl-3.0.html": "agpl-3.0",
        "http://www.gnu.org/licenses/lgpl-2.1": "lgpl-2.1",
        "http://www.gnu.org/licenses/lgpl-2.1.html": "lgpl-2.1",
        "http://www.gnu.org/licenses/lgpl-3.0": "lgpl-3.0",
        "http://www.gnu.org/licenses/lgpl-3.0.html": "lgpl-3.0",
        # Elsevier
        "http://www.elsevier.com/open-access/userlicense/1.0": "elsevier-oa",
        "http://www.elsevier.com/open-access/userlicense/1.0/": "elsevier-oa",
        "https://www.elsevier.com/open-access/userlicense/1.0": "elsevier-oa",
        "https://www.elsevier.com/open-access/userlicense/1.0/": "elsevier-oa",
        "http://www.elsevier.com/tdm/userlicense/1.0": "elsevier-tdm",
        "http://www.elsevier.com/tdm/userlicense/1.0/": "elsevier-tdm",
        "https://www.elsevier.com/tdm/userlicense/1.0": "elsevier-tdm",
        # Wiley
        "http://doi.wiley.com/10.1002/tdm_license_1": "wiley-tdm",
        "http://doi.wiley.com/10.1002/tdm_license_1.1": "wiley-tdm-1.1",
        "http://onlinelibrary.wiley.com/termsandconditions#vor": "wiley-vor",
        "http://onlinelibrary.wiley.com/termsandconditions#am": "wiley-am",
        "http://onlinelibrary.wiley.com/termsandconditions": "wiley-terms",
        "https://onlinelibrary.wiley.com/terms-and-conditions": "wiley-terms",
        # Springer
        "http://www.springer.com/tdm": "springer-tdm",
        "https://www.springer.com/tdm": "springer-tdm",
        "https://www.springernature.com/gp/researchers/text-and-data-mining": (
            "springernature-tdm"
        ),
        # Taylor & Francis
        "http://tandfonline.com/action/showcopyright": "tandf-terms",
        "https://www.tandfonline.com/action/showcopyright": "tandf-terms",
        "http://www.tandfonline.com/action/showcopyright": "tandf-terms",
        "http://www.tandfonline.com/action/showcopyright?show=full": "tandf-terms",
        # OUP
        "https://academic.oup.com/journals/pages/open_access/funder_policies/"
        "chorus/standard_publication_model": "oup-chorus",
        # SAGE
        "http://www.sagepub.com/journalspermissions.nav": "sage-permissions",
        "https://us.sagepub.com/en-us/nam/journals-permissions": "sage-permissions",
        # ACS
        "http://pubs.acs.org/page/policy/authorchoice_ccby_termsofuse.html": (
            "acs-authorchoice-ccby"
        ),
        "https://pubs.acs.org/page/policy/authorchoice_ccby_termsofuse.html": (
            "acs-authorchoice-ccby"
        ),
        "http://pubs.acs.org/page/policy/authorchoice_ccbyncnd_termsofuse.html": (
            "acs-authorchoice-ccbyncnd"
        ),
        "https://pubs.acs.org/page/policy/authorchoice_ccbyncnd_termsofuse.html": (
            "acs-authorchoice-ccbyncnd"
        ),
        "http://pubs.acs.org/page/policy/authorchoice_termsofuse.html": (
            "acs-authorchoice"
        ),
        "https://pubs.acs.org/page/policy/authorchoice_termsofuse.html": (
            "acs-authorchoice"
        ),
        "https://pubs.acs.org/page/policy/"
        "acs_authorchoice_with_nih_addendum_termsofuse.html": "acs-authorchoice-nih",
        "https://doi.org/10.1021/policy/oa-license": "acs-authorchoice",
        # RSC
        "http://www.rsc.org/help/disclaimer/pages/term3.aspx": "rsc-terms",
        "https://www.rsc.org/journals-books-databases/journal-authors-reviewers/"
        "licences-copyright-permissions/": "rsc-terms",
        # IOP
        "http://iopscience.iop.org/info/page/text-and-data-mining": "iop-tdm",
        "https://iopscience.iop.org/info/page/text-and-data-mining": "iop-tdm",
        "https://iopscience.iop.org/page/copyright": "iop-copyright",
        # BMJ
        "http://group.bmj.com/group/rights-licensing/permissions": "bmj-copyright",
        "https://www.bmj.com/company/legal-stuff/copyright-notice/": "bmj-copyright",
        # AAAS
        "http://www.sciencemag.org/about/science-licenses-journal-article-reuse": (
            "aaas-author-reuse"
        ),
        "https://www.science.org/content/page/science-licenses-journal-article-reuse": (
            "aaas-author-reuse"
        ),
        # APS
        "https://link.aps.org/licenses/aps-default-license": "aps-default",
        "https://link.aps.org/licenses/aps-default-text-mining-license": "aps-tdm",
        # AIP
        "http://publishing.aip.org/authors/rights-and-permissions": "aip-rights",
        "https://publishing.aip.org/authors/rights-and-permissions": "aip-rights",
        # Cambridge
        "https://www.cambridge.org/core/terms": "cup-terms",
        # De Gruyter
        "https://www.degruyter.com/dg/page/496": "degruyter-terms",
        # Thieme
        "https://www.thieme.de/statics/dokumente/thieme/final/de/dokumente/"
        "sw_oa/nlm_license_terms_thieme.pdf": "thieme-nlm",
        # JAMA
        "https://jamanetwork.com/pages/cc-by-license-permissions": "jama-cc-by",
    }

    for raw_url, vkey in extras.items():
        url_map[raw_url.rstrip("/").lower()] = vkey

    return url_map


_URL_MAP: dict[str, str] = _build_url_map()


# ===========================================================================
# Structural CC URL regex
# ===========================================================================

_CC_PATH_RE = re.compile(
    r"creativecommons\.org/licenses/"
    r"(?P<type>by(?:-nc)?(?:-nd|-sa)?)"
    r"/(?P<ver>\d+\.\d+)"
    r"(?:/(?P<igo>igo))?(?:/|$)",
    re.IGNORECASE,
)
_CC_ZERO_RE = re.compile(
    r"creativecommons\.org/publicdomain/zero/(?P<ver>\d+\.\d+)",
    re.IGNORECASE,
)
_CC_MARK_RE = re.compile(
    r"creativecommons\.org/publicdomain/mark/",
    re.IGNORECASE,
)


def _key_from_cc_url(raw: str) -> Optional[tuple[str, str, str]]:
    """Returns (version_key, name_key, canonical_url) or None."""
    if _CC_MARK_RE.search(raw):
        return (
            "cc-pdm",
            "cc-pdm",
            "https://creativecommons.org/publicdomain/mark/1.0/",
        )

    if m := _CC_ZERO_RE.search(raw):
        ver = m["ver"]
        vk = "cc0" if ver == "1.0" else f"cc0-{ver}"
        return (vk, "cc0", f"https://creativecommons.org/publicdomain/zero/{ver}/")

    if m := _CC_PATH_RE.search(raw):
        t = m["type"].lower()
        ver = m["ver"]
        igo = bool(m["igo"])

        vk = f"cc-{t}-{ver}" + ("-igo" if igo else "")
        nk = f"cc-{t}" + ("-igo" if igo else "")
        path = f"/licenses/{t}/{ver}/" + ("igo/" if igo else "")
        url = f"https://creativecommons.org{path}"
        return (vk, nk, url)

    return None


# ===========================================================================
# Prose keyword scan
# ===========================================================================

_PROSE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"cc\s*by-nc-nd\s*4\.0", re.I), "cc-by-nc-nd-4.0"),
    (re.compile(r"cc\s*by-nc-nd\s*3\.0", re.I), "cc-by-nc-nd-3.0"),
    (re.compile(r"cc\s*by-nc-nd", re.I), "cc-by-nc-nd"),
    (re.compile(r"cc\s*by-nc-sa\s*4\.0", re.I), "cc-by-nc-sa-4.0"),
    (re.compile(r"cc\s*by-nc-sa\s*3\.0", re.I), "cc-by-nc-sa-3.0"),
    (re.compile(r"cc\s*by-nc-sa", re.I), "cc-by-nc-sa"),
    (re.compile(r"cc\s*by-nc\s*4\.0", re.I), "cc-by-nc-4.0"),
    (re.compile(r"cc\s*by-nc\s*3\.0", re.I), "cc-by-nc-3.0"),
    (re.compile(r"cc\s*by-nc", re.I), "cc-by-nc"),
    (re.compile(r"cc\s*by-sa\s*4\.0", re.I), "cc-by-sa-4.0"),
    (re.compile(r"cc\s*by-sa\s*3\.0", re.I), "cc-by-sa-3.0"),
    (re.compile(r"cc\s*by-sa", re.I), "cc-by-sa"),
    (re.compile(r"cc\s*by-nd\s*4\.0", re.I), "cc-by-nd-4.0"),
    (re.compile(r"cc\s*by-nd\s*3\.0", re.I), "cc-by-nd-3.0"),
    (re.compile(r"cc\s*by-nd", re.I), "cc-by-nd"),
    (re.compile(r"cc\s*by\s*4\.0", re.I), "cc-by-4.0"),
    (re.compile(r"cc\s*by\s*3\.0", re.I), "cc-by-3.0"),
    (re.compile(r"cc\s*by\s*2\.0", re.I), "cc-by-2.0"),
    (re.compile(r"\bcc\s*by\b(?!\s*-)", re.I), "cc-by"),
    (re.compile(r"\bcc\s*0\b|cc\s*zero", re.I), "cc0"),
    (
        re.compile(r"attribution.{0,30}non.?commercial.{0,30}no.?deriv", re.I),
        "cc-by-nc-nd",
    ),
    (
        re.compile(r"attribution.{0,30}non.?commercial.{0,30}share.?alike", re.I),
        "cc-by-nc-sa",
    ),
    (re.compile(r"attribution.{0,30}non.?commercial", re.I), "cc-by-nc"),
    (re.compile(r"attribution.{0,30}no.?deriv", re.I), "cc-by-nd"),
    (re.compile(r"attribution.{0,30}share.?alike", re.I), "cc-by-sa"),
    (re.compile(r"\battribution\b", re.I), "cc-by"),
    (re.compile(r"elsevier.*tdm|tdm.*elsevier", re.I), "elsevier-tdm"),
    (re.compile(r"elsevier.*user\s*licen", re.I), "elsevier-oa"),
    (re.compile(r"wiley.*tdm|tdm.*wiley", re.I), "wiley-tdm"),
    (re.compile(r"springer.*tdm|tdm.*springer", re.I), "springer-tdm"),
    (re.compile(r"acs\s*authorchoice.*cc\s*by(?!-nc)", re.I), "acs-authorchoice-ccby"),
    (re.compile(r"acs\s*authorchoice", re.I), "acs-authorchoice"),
    (re.compile(r"all\s*rights\s*reserved", re.I), "all-rights-reserved"),
    (re.compile(r"author\s*manuscript", re.I), "author-manuscript"),
    (re.compile(r"public\s*domain", re.I), "public-domain"),
    (re.compile(r"open\s*access", re.I), "other-oa"),
]


# ===========================================================================
# Public API
# ===========================================================================


def _clean(raw: str) -> str:
    return _WHITESPACE_RE.sub(" ", raw.strip().split("#", 1)[0].rstrip("/")).lower()


@lru_cache(maxsize=8192)
def normalise_license(raw: str | None) -> LicenseVersion:
    """Normalise any license string to a :class:`LicenseVersion`.

    Parameters
    ----------
    raw : str | None
        Any form – token, URL, prose, SPDX expression.
        None raises TypeError.

    Returns
    -------
    LicenseVersion
        ``.key``             e.g. ``"cc-by-nc-nd-4.0"``
        ``.url``             canonical HTTPS URL or None
        ``.license``         :class:`LicenseName`, e.g. ``"cc-by-nc-nd"``
        ``.license.family``  :class:`LicenseFamily`, e.g. ``"cc"``
        ``.family``          shortcut for ``.license.family``

    Raises
    ------
    TypeError
        If ``raw`` is not a string or None.
    """
    if raw is None:
        raise TypeError("raw must be a string, got None")
    if not raw or not raw.strip():
        return _make("unknown")

    cleaned = _clean(raw)

    # 1 – direct version registry hit
    if cleaned in _VERSION_REGISTRY:
        return _make(cleaned)

    # 2 – alias table
    if cleaned in _ALIASES:
        return _make(_ALIASES[cleaned])

    # 3 – exact URL map
    if cleaned in _URL_MAP:
        return _make(_URL_MAP[cleaned])

    # 4 – structural CC URL regex
    if "creativecommons.org" in cleaned:
        result = _key_from_cc_url(cleaned)
        if result:
            vk, nk, url = result
            if vk in _VERSION_REGISTRY:
                return _make(vk)
            return _make_synthetic(vk, url, nk)

    # 5 – prose keyword scan
    if len(cleaned) > 20:
        for pattern, vkey in _PROSE_PATTERNS:
            if pattern.search(cleaned) and vkey in _VERSION_REGISTRY:
                return _make(vkey)

    # 6 – fallback
    return _make_unknown(cleaned)


def normalise_licenses(raws: Iterable[str]) -> list[LicenseVersion]:
    """Normalise a list of license strings."""
    return [normalise_license(r) for r in raws]
