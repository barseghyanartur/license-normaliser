"""License name enums for type-safe license checking."""

import re
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
    """License family enum for type-safe checking."""

    CC = "cc"
    CC0 = "cc0"
    PUBLIC_DOMAIN = "public-domain"
    OSI = "osi"
    COPYLEFT = "copyleft"
    OPEN_DATA = "open-data"
    PUBLISHER_TDM = "publisher-tdm"
    PUBLISHER_OA = "publisher-oa"
    PUBLISHER_PROPRIETARY = "publisher-proprietary"
    OTHER_OA = "other-oa"
    UNKNOWN = "unknown"


class LicenseNameEnum(Enum):
    """License name enum for type-safe checking."""

    # Creative Commons
    CC0 = "cc0"
    CC_PDM = "cc-pdm"
    CC_BY = "cc-by"
    CC_BY_SA = "cc-by-sa"
    CC_BY_ND = "cc-by-nd"
    CC_BY_NC = "cc-by-nc"
    CC_BY_NC_SA = "cc-by-nc-sa"
    CC_BY_NC_ND = "cc-by-nc-nd"
    CC_BY_IGO = "cc-by-igo"
    CC_BY_SA_IGO = "cc-by-sa-igo"
    CC_BY_ND_IGO = "cc-by-nd-igo"
    CC_BY_NC_IGO = "cc-by-nc-igo"
    CC_BY_NC_SA_IGO = "cc-by-nc-sa-igo"
    CC_BY_NC_ND_IGO = "cc-by-nc-nd-igo"

    # OSI
    MIT = "mit"
    APACHE = "apache"
    BSD_2_CLAUSE = "bsd-2-clause"
    BSD_3_CLAUSE = "bsd-3-clause"
    ISC = "isc"
    MPL = "mpl"

    # Copyleft
    GPL_2 = "gpl-2"
    GPL_3 = "gpl-3"
    AGPL_3 = "agpl-3"
    LGPL_2_1 = "lgpl-2.1"
    LGPL_3 = "lgpl-3"

    # Open Data
    ODBL = "odbl"
    ODC_BY = "odc-by"
    PDDL = "pddl"
    FAL = "fal"

    # Publisher - Elsevier
    ELSEVIER_OA = "elsevier-oa"
    ELSEVIER_TDM = "elsevier-tdm"

    # Publisher - Wiley
    WILEY_TDM = "wiley-tdm"
    WILEY_VOR = "wiley-vor"
    WILEY_AM = "wiley-am"
    WILEY_TERMS = "wiley-terms"

    # Publisher - Springer Nature
    SPRINGER_TDM = "springer-tdm"
    SPRINGERNATURE_TDM = "springernature-tdm"

    # Publisher - Taylor & Francis
    TANDF_TERMS = "tandf-terms"

    # Publisher - OUP
    OUP_CHORUS = "oup-chorus"
    OUP_TERMS = "oup-terms"

    # Publisher - SAGE
    SAGE_PERMISSIONS = "sage-permissions"

    # Publisher - ACS
    ACS_AUTHORCHOICE = "acs-authorchoice"
    ACS_AUTHORCHOICE_CCBY = "acs-authorchoice-ccby"
    ACS_AUTHORCHOICE_CCBYNCND = "acs-authorchoice-ccbyncnd"
    ACS_AUTHORCHOICE_NIH = "acs-authorchoice-nih"

    # Publisher - RSC
    RSC_TERMS = "rsc-terms"

    # Publisher - IOP
    IOP_TDM = "iop-tdm"
    IOP_COPYRIGHT = "iop-copyright"

    # Publisher - BMJ
    BMJ_COPYRIGHT = "bmj-copyright"

    # Publisher - AAAS / Science
    AAAS_AUTHOR_REUSE = "aaas-author-reuse"

    # Publisher - PNAS
    PNAS_LICENSES = "pnas-licenses"

    # Publisher - APS
    APS_DEFAULT = "aps-default"
    APS_TDM = "aps-tdm"

    # Publisher - Cambridge
    CUP_TERMS = "cup-terms"

    # Publisher - AIP
    AIP_RIGHTS = "aip-rights"

    # Publisher - JAMA
    JAMA_CC_BY = "jama-cc-by"

    # Publisher - De Gruyter
    DEGRUYTER_TERMS = "degruyter-terms"

    # Publisher - Thieme
    THIEME_NLM = "thieme-nlm"

    # Catch-all
    PUBLIC_DOMAIN_MARK = "public-domain"
    OTHER_OA = "other-oa"
    PUBLISHER_SPECIFIC_OA = "publisher-specific-oa"
    UNSPECIFIED_OA = "unspecified-oa"
    OPEN_ACCESS = "open-access"
    IMPLIED_OA = "implied-oa"
    AUTHOR_MANUSCRIPT = "author-manuscript"
    ALL_RIGHTS_RESERVED = "all-rights-reserved"
    NO_REUSE = "no-reuse"
    UNKNOWN = "unknown"

    @property
    def family(self) -> LicenseFamilyEnum:
        """Return the family enum for this license name."""
        return _NAME_TO_FAMILY.get(self.value, LicenseFamilyEnum.UNKNOWN)


# ===========================================================================
# Derived lookups (built after enums so they can reference each other)
# ===========================================================================

_VERSION_TO_NAME: dict[str, str] = {}
_NAME_TO_FAMILY: dict[str, LicenseFamilyEnum] = {}
_VERSION_REGISTRY_KEYS: set[str] = set()


def _strip_version(value: str) -> str:
    """Strip the version suffix from a version key to get the name key.

    IGO names (e.g. cc-by-3.0-igo) have no version in their name enum (e.g.
    cc-by-igo), so for IGO keys we strip the full -X.Y-igo suffix.
    """
    if value == "cc-zero":
        return "cc0"
    if value == "fldl":
        return "fal"
    if value.endswith("-igo"):
        stripped = re.sub(r"-\d+\.\d+-igo$", "", value)
        return stripped
    stripped = re.sub(r"-(?:4\.0|3\.0|2\.5|2\.0|1\.0|1\.1)(?:-igo)?$", "", value)
    if stripped != value:
        return stripped
    stripped = re.sub(r"-(?:only|v2|v3)$", "", value)
    return stripped


def _derive_enums() -> None:
    global _VERSION_TO_NAME, _NAME_TO_FAMILY, _VERSION_REGISTRY_KEYS

    # Build _NAME_TO_FAMILY: name_key -> family.
    # Explicit entries cover all non-trivial/cross-prefix names;
    # everything else falls through to prefix-based assignment.
    explicit_map: dict[str, LicenseFamilyEnum] = {
        # CC family (also covered by prefix below, but explicit for clarity)
        "cc0": LicenseFamilyEnum.CC0,
        "cc-zero": LicenseFamilyEnum.CC0,
        "cc-pdm": LicenseFamilyEnum.PUBLIC_DOMAIN,
        "public-domain": LicenseFamilyEnum.PUBLIC_DOMAIN,
        # OSI
        "mit": LicenseFamilyEnum.OSI,
        "apache": LicenseFamilyEnum.OSI,
        "bsd-2-clause": LicenseFamilyEnum.OSI,
        "bsd-3-clause": LicenseFamilyEnum.OSI,
        "isc": LicenseFamilyEnum.OSI,
        "mpl": LicenseFamilyEnum.OSI,
        # Copyleft
        "gpl-2": LicenseFamilyEnum.COPYLEFT,
        "gpl-3": LicenseFamilyEnum.COPYLEFT,
        "agpl-3": LicenseFamilyEnum.COPYLEFT,
        "lgpl-2.1": LicenseFamilyEnum.COPYLEFT,
        "lgpl-3": LicenseFamilyEnum.COPYLEFT,
        # Open Data
        "odbl": LicenseFamilyEnum.OPEN_DATA,
        "odc-by": LicenseFamilyEnum.OPEN_DATA,
        "pddl": LicenseFamilyEnum.OPEN_DATA,
        "fal": LicenseFamilyEnum.OTHER_OA,
        # Elsevier
        "elsevier-oa": LicenseFamilyEnum.PUBLISHER_OA,
        "elsevier-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
        # ACS
        "acs-authorchoice": LicenseFamilyEnum.PUBLISHER_OA,
        "acs-authorchoice-ccby": LicenseFamilyEnum.PUBLISHER_OA,
        "acs-authorchoice-ccbyncnd": LicenseFamilyEnum.PUBLISHER_OA,
        "acs-authorchoice-nih": LicenseFamilyEnum.PUBLISHER_OA,
        # JAMA
        "jama-cc-by": LicenseFamilyEnum.PUBLISHER_OA,
        # OUP
        "oup-chorus": LicenseFamilyEnum.PUBLISHER_OA,
        "oup-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
        # Thieme
        "thieme-nlm": LicenseFamilyEnum.PUBLISHER_OA,
        # Catch-all
        "other-oa": LicenseFamilyEnum.OTHER_OA,
        "unspecified-oa": LicenseFamilyEnum.OTHER_OA,
        "open-access": LicenseFamilyEnum.OTHER_OA,
        "publisher-specific-oa": LicenseFamilyEnum.PUBLISHER_OA,
        "implied-oa": LicenseFamilyEnum.PUBLISHER_OA,
        "author-manuscript": LicenseFamilyEnum.PUBLISHER_OA,
        "all-rights-reserved": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
        "no-reuse": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
    }

    for name_enum in LicenseNameEnum:
        name_val = name_enum.value
        if name_val in explicit_map:
            family = explicit_map[name_val]
        elif name_val.startswith("cc-"):
            family = LicenseFamilyEnum.CC
        elif name_val.startswith(
            (
                "wiley-",
                "springer",
                "tandf",
                "sage",
                "rsc",
                "iop",
                "bmj",
                "aaas",
                "pnas",
                "aps",
                "cup",
                "aip",
                "degruyter",
            )
        ):
            family = (
                LicenseFamilyEnum.PUBLISHER_TDM
                if name_val
                in (
                    "wiley-tdm",
                    "springer-tdm",
                    "springernature-tdm",
                    "iop-tdm",
                    "aps-tdm",
                )
                else LicenseFamilyEnum.PUBLISHER_PROPRIETARY
            )
        else:
            family = LicenseFamilyEnum.UNKNOWN
        _NAME_TO_FAMILY[name_val] = family

    # Build _VERSION_TO_NAME: version key -> name key by stripping version suffix.
    for ve in LicenseVersionEnum:
        _VERSION_TO_NAME[ve.value] = _strip_version(ve.value)


class LicenseVersionEnum(Enum):
    """License version enum for type-safe checking."""

    # CC Zero
    CC0 = "cc0"
    CC0_1_0 = "cc0-1.0"
    CC_ZERO = "cc-zero"
    CC_PDM = "cc-pdm"

    # CC BY
    CC_BY = "cc-by"
    CC_BY_4_0 = "cc-by-4.0"
    CC_BY_3_0 = "cc-by-3.0"
    CC_BY_2_5 = "cc-by-2.5"
    CC_BY_2_0 = "cc-by-2.0"
    CC_BY_1_0 = "cc-by-1.0"

    # CC BY-SA
    CC_BY_SA = "cc-by-sa"
    CC_BY_SA_4_0 = "cc-by-sa-4.0"
    CC_BY_SA_3_0 = "cc-by-sa-3.0"
    CC_BY_SA_2_5 = "cc-by-sa-2.5"
    CC_BY_SA_2_0 = "cc-by-sa-2.0"

    # CC BY-ND
    CC_BY_ND = "cc-by-nd"
    CC_BY_ND_4_0 = "cc-by-nd-4.0"
    CC_BY_ND_3_0 = "cc-by-nd-3.0"
    CC_BY_ND_2_0 = "cc-by-nd-2.0"

    # CC BY-NC
    CC_BY_NC = "cc-by-nc"
    CC_BY_NC_4_0 = "cc-by-nc-4.0"
    CC_BY_NC_3_0 = "cc-by-nc-3.0"
    CC_BY_NC_2_5 = "cc-by-nc-2.5"
    CC_BY_NC_2_0 = "cc-by-nc-2.0"

    # CC BY-NC-SA
    CC_BY_NC_SA = "cc-by-nc-sa"
    CC_BY_NC_SA_4_0 = "cc-by-nc-sa-4.0"
    CC_BY_NC_SA_3_0 = "cc-by-nc-sa-3.0"
    CC_BY_NC_SA_2_5 = "cc-by-nc-sa-2.5"
    CC_BY_NC_SA_2_0 = "cc-by-nc-sa-2.0"

    # CC BY-NC-ND
    CC_BY_NC_ND = "cc-by-nc-nd"
    CC_BY_NC_ND_4_0 = "cc-by-nc-nd-4.0"
    CC_BY_NC_ND_3_0 = "cc-by-nc-nd-3.0"
    CC_BY_NC_ND_2_5 = "cc-by-nc-nd-2.5"
    CC_BY_NC_ND_2_0 = "cc-by-nc-nd-2.0"

    # CC IGO
    CC_BY_3_0_IGO = "cc-by-3.0-igo"
    CC_BY_NC_SA_3_0_IGO = "cc-by-nc-sa-3.0-igo"
    CC_BY_NC_ND_3_0_IGO = "cc-by-nc-nd-3.0-igo"

    # OSI
    MIT = "mit"
    APACHE_2_0 = "apache-2.0"
    BSD_2_CLAUSE = "bsd-2-clause"
    BSD_3_CLAUSE = "bsd-3-clause"
    ISC = "isc"
    MPL_2_0 = "mpl-2.0"

    # Copyleft
    GPL_2_0 = "gpl-2.0"
    GPL_2_0_ONLY = "gpl-2.0-only"
    GPL_3_0 = "gpl-3.0"
    GPL_3_0_ONLY = "gpl-3.0-only"
    AGPL_3_0 = "agpl-3.0"
    AGPL_3_0_ONLY = "agpl-3.0-only"
    LGPL_2_1 = "lgpl-2.1"
    LGPL_2_1_ONLY = "lgpl-2.1-only"
    LGPL_3_0 = "lgpl-3.0"
    LGPL_3_0_ONLY = "lgpl-3.0-only"

    # Open Data
    ODBL = "odbl"
    ODC_BY = "odc-by"
    PDDL = "pddl"
    FAL = "fal"
    FLDL = "fldl"

    # Publisher - Elsevier
    ELSEVIER_OA = "elsevier-oa"
    ELSEVIER_TDM = "elsevier-tdm"

    # Publisher - Wiley
    WILEY_TDM = "wiley-tdm"
    WILEY_TDM_1_1 = "wiley-tdm-1.1"
    WILEY_VOR = "wiley-vor"
    WILEY_AM = "wiley-am"
    WILEY_TERMS = "wiley-terms"

    # Publisher - Springer
    SPRINGER_TDM = "springer-tdm"
    SPRINGERNATURE_TDM = "springernature-tdm"

    # Publisher - Taylor & Francis
    TANDF_TERMS = "tandf-terms"

    # Publisher - OUP
    OUP_CHORUS = "oup-chorus"
    OUP_TERMS = "oup-terms"

    # Publisher - SAGE
    SAGE_PERMISSIONS = "sage-permissions"

    # Publisher - ACS
    ACS_AUTHORCHOICE_CCBY = "acs-authorchoice-ccby"
    ACS_AUTHORCHOICE_CCBYCND = "acs-authorchoice-ccbyncnd"
    ACS_AUTHORCHOICE = "acs-authorchoice"
    ACS_AUTHORCHOICE_NIH = "acs-authorchoice-nih"

    # Publisher - RSC
    RSC_TERMS = "rsc-terms"

    # Publisher - IOP
    IOP_TDM = "iop-tdm"
    IOP_COPYRIGHT = "iop-copyright"

    # Publisher - BMJ
    BMJ_COPYRIGHT = "bmj-copyright"

    # Publisher - AAAS
    AAAS_AUTHOR_REUSE = "aaas-author-reuse"

    # Publisher - PNAS
    PNAS_LICENSES = "pnas-licenses"

    # Publisher - APS
    APS_DEFAULT = "aps-default"
    APS_TDM = "aps-tdm"

    # Publisher - Cambridge
    CUP_TERMS = "cup-terms"

    # Publisher - AIP
    AIP_RIGHTS = "aip-rights"

    # Publisher - JAMA
    JAMA_CC_BY = "jama-cc-by"

    # Publisher - De Gruyter
    DEGRUYTER_TERMS = "degruyter-terms"

    # Publisher - Thieme
    THIEME_NLM = "thieme-nlm"

    # Catch-all
    PUBLIC_DOMAIN = "public-domain"
    OTHER_OA = "other-oa"
    PUBLISHER_SPECIFIC_OA = "publisher-specific-oa"
    UNSPECIFIED_OA = "unspecified-oa"
    OPEN_ACCESS = "open-access"
    IMPLIED_OA = "implied-oa"
    AUTHOR_MANUSCRIPT = "author-manuscript"
    ALL_RIGHTS_RESERVED = "all-rights-reserved"
    NO_REUSE = "no-reuse"
    UNKNOWN = "unknown"

    @property
    def name_enum(self) -> LicenseNameEnum:
        """Return the name enum for this version (without version suffix)."""
        name_key = _VERSION_TO_NAME.get(self.value, self.value)
        try:
            return LicenseNameEnum(name_key)
        except ValueError:
            return LicenseNameEnum.UNKNOWN

    @property
    def family(self) -> LicenseFamilyEnum:
        """Return the family enum for this version."""
        return self.name_enum.family


_derive_enums()
