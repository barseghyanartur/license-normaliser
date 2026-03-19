"""License name enums for type-safe license checking."""

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
        family_map = {
            # CC
            "cc0": LicenseFamilyEnum.CC0,
            "cc-pdm": LicenseFamilyEnum.PUBLIC_DOMAIN,
            "cc-by": LicenseFamilyEnum.CC,
            "cc-by-sa": LicenseFamilyEnum.CC,
            "cc-by-nd": LicenseFamilyEnum.CC,
            "cc-by-nc": LicenseFamilyEnum.CC,
            "cc-by-nc-sa": LicenseFamilyEnum.CC,
            "cc-by-nc-nd": LicenseFamilyEnum.CC,
            "cc-by-igo": LicenseFamilyEnum.CC,
            "cc-by-sa-igo": LicenseFamilyEnum.CC,
            "cc-by-nd-igo": LicenseFamilyEnum.CC,
            "cc-by-nc-igo": LicenseFamilyEnum.CC,
            "cc-by-nc-sa-igo": LicenseFamilyEnum.CC,
            "cc-by-nc-nd-igo": LicenseFamilyEnum.CC,
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
            # Publisher - Elsevier
            "elsevier-oa": LicenseFamilyEnum.PUBLISHER_OA,
            "elsevier-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
            # Publisher - Wiley
            "wiley-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
            "wiley-vor": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            "wiley-am": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            "wiley-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - Springer
            "springer-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
            "springernature-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
            # Publisher - Taylor & Francis
            "tandf-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - OUP
            "oup-chorus": LicenseFamilyEnum.PUBLISHER_OA,
            "oup-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - SAGE
            "sage-permissions": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - ACS
            "acs-authorchoice": LicenseFamilyEnum.PUBLISHER_OA,
            "acs-authorchoice-ccby": LicenseFamilyEnum.PUBLISHER_OA,
            "acs-authorchoice-ccbyncnd": LicenseFamilyEnum.PUBLISHER_OA,
            "acs-authorchoice-nih": LicenseFamilyEnum.PUBLISHER_OA,
            # Publisher - RSC
            "rsc-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - IOP
            "iop-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
            "iop-copyright": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - BMJ
            "bmj-copyright": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - AAAS
            "aaas-author-reuse": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - PNAS
            "pnas-licenses": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - APS
            "aps-default": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            "aps-tdm": LicenseFamilyEnum.PUBLISHER_TDM,
            # Publisher - Cambridge
            "cup-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - AIP
            "aip-rights": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - JAMA
            "jama-cc-by": LicenseFamilyEnum.PUBLISHER_OA,
            # Publisher - De Gruyter
            "degruyter-terms": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            # Publisher - Thieme
            "thieme-nlm": LicenseFamilyEnum.PUBLISHER_OA,
            # Catch-all
            "public-domain": LicenseFamilyEnum.PUBLIC_DOMAIN,
            "other-oa": LicenseFamilyEnum.OTHER_OA,
            "publisher-specific-oa": LicenseFamilyEnum.PUBLISHER_OA,
            "unspecified-oa": LicenseFamilyEnum.OTHER_OA,
            "open-access": LicenseFamilyEnum.OTHER_OA,
            "implied-oa": LicenseFamilyEnum.PUBLISHER_OA,
            "author-manuscript": LicenseFamilyEnum.PUBLISHER_OA,
            "all-rights-reserved": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            "no-reuse": LicenseFamilyEnum.PUBLISHER_PROPRIETARY,
            "unknown": LicenseFamilyEnum.UNKNOWN,
        }
        return family_map.get(self.value, LicenseFamilyEnum.UNKNOWN)


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
    CC_BY_4_0_IGO = "cc-by-4.0-igo"
    CC_BY_NC_SA_3_0_IGO = "cc-by-nc-sa-3.0-igo"
    CC_BY_NC_ND_3_0_IGO = "cc-by-nc-nd-3.0-igo"
    CC_BY_NC_ND_4_0_IGO = "cc-by-nc-nd-4.0-igo"

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
        # Map version keys to their name keys
        version_to_name = {
            # CC Zero
            "cc0": "cc0",
            "cc0-1.0": "cc0",
            "cc-zero": "cc0",
            "cc-pdm": "cc-pdm",
            # CC BY
            "cc-by": "cc-by",
            "cc-by-4.0": "cc-by",
            "cc-by-3.0": "cc-by",
            "cc-by-2.5": "cc-by",
            "cc-by-2.0": "cc-by",
            "cc-by-1.0": "cc-by",
            # CC BY-SA
            "cc-by-sa": "cc-by-sa",
            "cc-by-sa-4.0": "cc-by-sa",
            "cc-by-sa-3.0": "cc-by-sa",
            "cc-by-sa-2.5": "cc-by-sa",
            "cc-by-sa-2.0": "cc-by-sa",
            # CC BY-ND
            "cc-by-nd": "cc-by-nd",
            "cc-by-nd-4.0": "cc-by-nd",
            "cc-by-nd-3.0": "cc-by-nd",
            "cc-by-nd-2.0": "cc-by-nd",
            # CC BY-NC
            "cc-by-nc": "cc-by-nc",
            "cc-by-nc-4.0": "cc-by-nc",
            "cc-by-nc-3.0": "cc-by-nc",
            "cc-by-nc-2.5": "cc-by-nc",
            "cc-by-nc-2.0": "cc-by-nc",
            # CC BY-NC-SA
            "cc-by-nc-sa": "cc-by-nc-sa",
            "cc-by-nc-sa-4.0": "cc-by-nc-sa",
            "cc-by-nc-sa-3.0": "cc-by-nc-sa",
            "cc-by-nc-sa-2.5": "cc-by-nc-sa",
            "cc-by-nc-sa-2.0": "cc-by-nc-sa",
            # CC BY-NC-ND
            "cc-by-nc-nd": "cc-by-nc-nd",
            "cc-by-nc-nd-4.0": "cc-by-nc-nd",
            "cc-by-nc-nd-3.0": "cc-by-nc-nd",
            "cc-by-nc-nd-2.5": "cc-by-nc-nd",
            "cc-by-nc-nd-2.0": "cc-by-nc-nd",
            # CC IGO
            "cc-by-3.0-igo": "cc-by-igo",
            "cc-by-4.0-igo": "cc-by-igo",
            "cc-by-nc-sa-3.0-igo": "cc-by-nc-sa-igo",
            "cc-by-nc-nd-3.0-igo": "cc-by-nc-nd-igo",
            "cc-by-nc-nd-4.0-igo": "cc-by-nc-nd-igo",
            # OSI
            "mit": "mit",
            "apache-2.0": "apache",
            "bsd-2-clause": "bsd-2-clause",
            "bsd-3-clause": "bsd-3-clause",
            "isc": "isc",
            "mpl-2.0": "mpl",
            # Copyleft
            "gpl-2.0": "gpl-2",
            "gpl-2.0-only": "gpl-2",
            "gpl-3.0": "gpl-3",
            "gpl-3.0-only": "gpl-3",
            "agpl-3.0": "agpl-3",
            "agpl-3.0-only": "agpl-3",
            "lgpl-2.1": "lgpl-2.1",
            "lgpl-2.1-only": "lgpl-2.1",
            "lgpl-3.0": "lgpl-3",
            "lgpl-3.0-only": "lgpl-3",
            # Open Data
            "odbl": "odbl",
            "odc-by": "odc-by",
            "pddl": "pddl",
            "fal": "fal",
            "fldl": "fal",
            # Publisher - Elsevier
            "elsevier-oa": "elsevier-oa",
            "elsevier-tdm": "elsevier-tdm",
            # Publisher - Wiley
            "wiley-tdm": "wiley-tdm",
            "wiley-tdm-1.1": "wiley-tdm",
            "wiley-vor": "wiley-vor",
            "wiley-am": "wiley-am",
            "wiley-terms": "wiley-terms",
            # Publisher - Springer
            "springer-tdm": "springer-tdm",
            "springernature-tdm": "springernature-tdm",
            # Publisher - Taylor & Francis
            "tandf-terms": "tandf-terms",
            # Publisher - OUP
            "oup-chorus": "oup-chorus",
            "oup-terms": "oup-terms",
            # Publisher - SAGE
            "sage-permissions": "sage-permissions",
            # Publisher - ACS
            "acs-authorchoice-ccby": "acs-authorchoice-ccby",
            "acs-authorchoice-ccbyncnd": "acs-authorchoice-ccbyncnd",
            "acs-authorchoice": "acs-authorchoice",
            "acs-authorchoice-nih": "acs-authorchoice-nih",
            # Publisher - RSC
            "rsc-terms": "rsc-terms",
            # Publisher - IOP
            "iop-tdm": "iop-tdm",
            "iop-copyright": "iop-copyright",
            # Publisher - BMJ
            "bmj-copyright": "bmj-copyright",
            # Publisher - AAAS
            "aaas-author-reuse": "aaas-author-reuse",
            # Publisher - PNAS
            "pnas-licenses": "pnas-licenses",
            # Publisher - APS
            "aps-default": "aps-default",
            "aps-tdm": "aps-tdm",
            # Publisher - Cambridge
            "cup-terms": "cup-terms",
            # Publisher - AIP
            "aip-rights": "aip-rights",
            # Publisher - JAMA
            "jama-cc-by": "jama-cc-by",
            # Publisher - De Gruyter
            "degruyter-terms": "degruyter-terms",
            # Publisher - Thieme
            "thieme-nlm": "thieme-nlm",
            # Catch-all
            "public-domain": "public-domain",
            "other-oa": "other-oa",
            "publisher-specific-oa": "publisher-specific-oa",
            "unspecified-oa": "unspecified-oa",
            "open-access": "open-access",
            "implied-oa": "implied-oa",
            "author-manuscript": "author-manuscript",
            "all-rights-reserved": "all-rights-reserved",
            "no-reuse": "no-reuse",
            "unknown": "unknown",
        }
        name_key = version_to_name.get(self.value, "unknown")
        return LicenseNameEnum(name_key)

    @property
    def family(self) -> LicenseFamilyEnum:
        """Return the family enum for this version."""
        return self.name_enum.family
