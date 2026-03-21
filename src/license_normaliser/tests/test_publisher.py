"""Tests for PublisherParser - publisher URLs and shorthand aliases."""

from license_normaliser import normalise_license


class TestPublisherUrls:
    def test_elsevier_oa_url(self):
        v = normalise_license("https://www.elsevier.com/open-access/userlicense/1.0/")
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_elsevier_oa_url_http(self):
        v = normalise_license("http://www.elsevier.com/open-access/userlicense/1.0/")
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_elsevier_tdm_url(self):
        v = normalise_license("https://www.elsevier.com/tdm/userlicense/1.0/")
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_wiley_tdm_url(self):
        v = normalise_license("http://doi.wiley.com/10.1002/tdm_license_1")
        assert v.key == "wiley-tdm"
        assert v.family.key == "publisher-tdm"

    def test_wiley_terms_url(self):
        v = normalise_license("https://onlinelibrary.wiley.com/terms-and-conditions")
        assert v.key == "wiley-terms"
        assert v.family.key == "publisher-proprietary"

    def test_springer_tdm_url(self):
        v = normalise_license("https://www.springer.com/tdm")
        assert v.key == "springer-tdm"
        assert v.family.key == "publisher-tdm"

    def test_springernature_tdm_url(self):
        v = normalise_license(
            "https://www.springernature.com/gp/researchers/text-and-data-mining"
        )
        assert v.key == "springernature-tdm"
        assert v.family.key == "publisher-tdm"

    def test_acs_authorchoice_ccby_url(self):
        v = normalise_license(
            "https://pubs.acs.org/page/policy/authorchoice_ccby_termsofuse.html"
        )
        assert v.key == "acs-authorchoice-ccby"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_url(self):
        v = normalise_license(
            "https://pubs.acs.org/page/policy/authorchoice_termsofuse.html"
        )
        assert v.key == "acs-authorchoice"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_nih_url(self):
        v = normalise_license(
            "https://pubs.acs.org/page/policy/"
            "acs_authorchoice_with_nih_addendum_termsofuse.html"
        )
        assert v.key == "acs-authorchoice-nih"
        assert v.family.key == "publisher-oa"

    def test_rsc_terms_url(self):
        v = normalise_license(
            "https://www.rsc.org/journals-books-databases/"
            "journal-authors-reviewers/licences-copyright-permissions/"
        )
        assert v.key == "rsc-terms"
        assert v.family.key == "publisher-proprietary"

    def test_iop_tdm_url(self):
        v = normalise_license(
            "https://iopscience.iop.org/info/page/text-and-data-mining"
        )
        assert v.key == "iop-tdm"
        assert v.family.key == "publisher-tdm"

    def test_bmj_copyright_url(self):
        v = normalise_license(
            "https://www.bmj.com/company/legal-stuff/copyright-notice/"
        )
        assert v.key == "bmj-copyright"
        assert v.family.key == "publisher-proprietary"

    def test_aaas_author_reuse_url(self):
        v = normalise_license(
            "https://www.science.org/content/page/science-licenses-journal-article-reuse"
        )
        assert v.key == "aaas-author-reuse"
        assert v.family.key == "publisher-proprietary"

    def test_aps_default_url(self):
        v = normalise_license("https://link.aps.org/licenses/aps-default-license")
        assert v.key == "aps-default"
        assert v.family.key == "publisher-proprietary"

    def test_aps_tdm_url(self):
        v = normalise_license(
            "https://link.aps.org/licenses/aps-default-text-mining-license"
        )
        assert v.key == "aps-tdm"
        assert v.family.key == "publisher-tdm"

    def test_cup_terms_url(self):
        v = normalise_license("https://www.cambridge.org/core/terms")
        assert v.key == "cup-terms"
        assert v.family.key == "publisher-proprietary"

    def test_aip_rights_url(self):
        v = normalise_license(
            "https://publishing.aip.org/authors/rights-and-permissions"
        )
        assert v.key == "aip-rights"
        assert v.family.key == "publisher-proprietary"

    def test_jama_cc_by_url(self):
        v = normalise_license("https://jamanetwork.com/pages/cc-by-license-permissions")
        assert v.key == "jama-cc-by"
        assert v.family.key == "publisher-oa"

    def test_oup_chorus_url(self):
        v = normalise_license(
            "https://academic.oup.com/journals/pages/open_access/"
            "funder_policies/chorus/standard_publication_model"
        )
        assert v.key == "oup-chorus"
        assert v.family.key == "publisher-oa"

    def test_oup_terms_url(self):
        v = normalise_license(
            "https://academic.oup.com/pages/standard-publication-reuse-rights"
        )
        assert v.key == "oup-terms"
        assert v.family.key == "publisher-proprietary"

    def test_sage_permissions_url(self):
        v = normalise_license("https://us.sagepub.com/en-us/nam/journals-permissions")
        assert v.key == "sage-permissions"
        assert v.family.key == "publisher-proprietary"

    def test_tandf_terms_url(self):
        v = normalise_license("https://www.tandfonline.com/action/showCopyRight")
        assert v.key == "tandf-terms"
        assert v.family.key == "publisher-proprietary"

    def test_gnu_gpl_url(self):
        v = normalise_license("https://www.gnu.org/licenses/gpl-3.0.html")
        assert v.key == "gpl-3.0"
        assert v.family.key == "copyleft"


class TestPublisherShorthand:
    def test_elsevier_user_license(self):
        v = normalise_license("elsevier user license")
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_elsevier_tdm_shorthand(self):
        v = normalise_license("elsevier tdm")
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_wiley_tdm_shorthand(self):
        v = normalise_license("wiley tdm license")
        assert v.key == "wiley-tdm"
        assert v.family.key == "publisher-tdm"

    def test_wiley_vor(self):
        v = normalise_license("wiley vor")
        assert v.key == "wiley-vor"
        assert v.family.key == "publisher-proprietary"

    def test_wiley_am(self):
        v = normalise_license("wiley am")
        assert v.key == "wiley-am"
        assert v.family.key == "publisher-proprietary"

    def test_springer_tdm_shorthand(self):
        v = normalise_license("springer tdm")
        assert v.key == "springer-tdm"
        assert v.family.key == "publisher-tdm"

    def test_springer_nature_tdm_shorthand(self):
        v = normalise_license("springer nature tdm")
        assert v.key == "springernature-tdm"
        assert v.family.key == "publisher-tdm"

    def test_acs_authorchoice_shorthand(self):
        v = normalise_license("acs authorchoice")
        assert v.key == "acs-authorchoice"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_ccby_shorthand(self):
        v = normalise_license("acs authorchoice cc by")
        assert v.key == "acs-authorchoice-ccby"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_nih_shorthand(self):
        v = normalise_license("acs authorchoice nih")
        assert v.key == "acs-authorchoice-nih"
        assert v.family.key == "publisher-oa"

    def test_rsc_terms_shorthand(self):
        v = normalise_license("rsc terms")
        assert v.key == "rsc-terms"
        assert v.family.key == "publisher-proprietary"

    def test_iop_tdm_shorthand(self):
        v = normalise_license("iop tdm")
        assert v.key == "iop-tdm"
        assert v.family.key == "publisher-tdm"

    def test_iop_copyright_shorthand(self):
        v = normalise_license("iop copyright")
        assert v.key == "iop-copyright"
        assert v.family.key == "publisher-proprietary"

    def test_bmj_copyright_shorthand(self):
        v = normalise_license("bmj copyright")
        assert v.key == "bmj-copyright"
        assert v.family.key == "publisher-proprietary"

    def test_aaas_author_reuse_shorthand(self):
        v = normalise_license("aaas author reuse")
        assert v.key == "aaas-author-reuse"
        assert v.family.key == "publisher-proprietary"

    def test_pnas_licenses_shorthand(self):
        v = normalise_license("pnas licenses")
        assert v.key == "pnas-licenses"
        assert v.family.key == "publisher-proprietary"

    def test_aps_default_shorthand(self):
        v = normalise_license("aps default")
        assert v.key == "aps-default"
        assert v.family.key == "publisher-proprietary"

    def test_aps_tdm_shorthand(self):
        v = normalise_license("aps tdm")
        assert v.key == "aps-tdm"
        assert v.family.key == "publisher-tdm"

    def test_cup_terms_shorthand(self):
        v = normalise_license("cup terms")
        assert v.key == "cup-terms"
        assert v.family.key == "publisher-proprietary"

    def test_aip_rights_shorthand(self):
        v = normalise_license("aip rights")
        assert v.key == "aip-rights"
        assert v.family.key == "publisher-proprietary"

    def test_jama_cc_by_shorthand(self):
        v = normalise_license("jama cc by")
        assert v.key == "jama-cc-by"
        assert v.family.key == "publisher-oa"

    def test_degruyter_terms_shorthand(self):
        v = normalise_license("degruyter terms")
        assert v.key == "degruyter-terms"
        assert v.family.key == "publisher-proprietary"

    def test_oup_chorus_shorthand(self):
        v = normalise_license("oup chorus")
        assert v.key == "oup-chorus"
        assert v.family.key == "publisher-oa"

    def test_oup_terms_shorthand(self):
        v = normalise_license("oup terms")
        assert v.key == "oup-terms"
        assert v.family.key == "publisher-proprietary"

    def test_sage_permissions_shorthand(self):
        v = normalise_license("sage permissions")
        assert v.key == "sage-permissions"
        assert v.family.key == "publisher-proprietary"

    def test_tandf_terms_shorthand(self):
        v = normalise_license("tandf terms")
        assert v.key == "tandf-terms"
        assert v.family.key == "publisher-proprietary"

    def test_thieme_nlm_shorthand(self):
        v = normalise_license("thieme nlm")
        assert v.key == "thieme-nlm"
        assert v.family.key == "publisher-oa"


class TestPublisherDirectKeys:
    def test_elsevier_tdm_key(self):
        v = normalise_license("elsevier-tdm")
        assert v.key == "elsevier-tdm"
        assert v.family.key == "publisher-tdm"

    def test_elsevier_oa_key(self):
        v = normalise_license("elsevier-oa")
        assert v.key == "elsevier-oa"
        assert v.family.key == "publisher-oa"

    def test_wiley_tdm_key(self):
        v = normalise_license("wiley-tdm")
        assert v.key == "wiley-tdm"
        assert v.family.key == "publisher-tdm"

    def test_acs_authorchoice_key(self):
        v = normalise_license("acs-authorchoice")
        assert v.key == "acs-authorchoice"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_ccby_key(self):
        v = normalise_license("acs-authorchoice-ccby")
        assert v.key == "acs-authorchoice-ccby"
        assert v.family.key == "publisher-oa"

    def test_acs_authorchoice_nih_key(self):
        v = normalise_license("acs-authorchoice-nih")
        assert v.key == "acs-authorchoice-nih"
        assert v.family.key == "publisher-oa"

    def test_iop_tdm_key(self):
        v = normalise_license("iop-tdm")
        assert v.key == "iop-tdm"
        assert v.family.key == "publisher-tdm"

    def test_aps_tdm_key(self):
        v = normalise_license("aps-tdm")
        assert v.key == "aps-tdm"
        assert v.family.key == "publisher-tdm"

    def test_oup_chorus_key(self):
        v = normalise_license("oup-chorus")
        assert v.key == "oup-chorus"
        assert v.family.key == "publisher-oa"

    def test_jama_cc_by_key(self):
        v = normalise_license("jama-cc-by")
        assert v.key == "jama-cc-by"
        assert v.family.key == "publisher-oa"

    def test_thieme_nlm_key(self):
        v = normalise_license("thieme-nlm")
        assert v.key == "thieme-nlm"
        assert v.family.key == "publisher-oa"

    def test_implied_oa_key(self):
        v = normalise_license("implied-oa")
        assert v.key == "implied-oa"
        assert v.family.key == "publisher-oa"

    def test_unspecified_oa_key(self):
        v = normalise_license("unspecified-oa")
        assert v.key == "unspecified-oa"
        assert v.family.key == "other-oa"

    def test_author_manuscript_key(self):
        v = normalise_license("author-manuscript")
        assert v.key == "author-manuscript"
        assert v.family.key == "publisher-oa"

    def test_all_rights_reserved_key(self):
        v = normalise_license("all-rights-reserved")
        assert v.key == "all-rights-reserved"
        assert v.family.key == "publisher-proprietary"

    def test_no_reuse_key(self):
        v = normalise_license("no-reuse")
        assert v.key == "no-reuse"
        assert v.family.key == "publisher-proprietary"

    def test_other_oa_key(self):
        v = normalise_license("other-oa")
        assert v.key == "other-oa"
        assert v.family.key == "other-oa"

    def test_public_domain_key(self):
        v = normalise_license("public-domain")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"

    def test_open_access_key(self):
        v = normalise_license("open-access")
        assert v.key == "open-access"
        assert v.family.key == "other-oa"


class TestPublisherCatchAll:
    def test_implied_oa_shorthand(self):
        v = normalise_license("implied oa")
        assert v.key == "implied-oa"
        assert v.family.key == "publisher-oa"

    def test_unspecified_oa_shorthand(self):
        v = normalise_license("unspecified oa")
        assert v.key == "unspecified-oa"
        assert v.family.key == "other-oa"

    def test_open_access_shorthand(self):
        v = normalise_license("open access")
        assert v.key == "other-oa"
        assert v.family.key == "other-oa"

    def test_author_manuscript_shorthand(self):
        v = normalise_license("author manuscript")
        assert v.key == "author-manuscript"
        assert v.family.key == "publisher-oa"

    def test_all_rights_reserved_shorthand(self):
        v = normalise_license("all rights reserved")
        assert v.key == "all-rights-reserved"
        assert v.family.key == "publisher-proprietary"

    def test_no_reuse_shorthand(self):
        v = normalise_license("no reuse")
        assert v.key == "no-reuse"
        assert v.family.key == "publisher-proprietary"


class TestCCPublicDomain:
    def test_cc_pdm_bare_key(self):
        v = normalise_license("cc-pdm")
        assert v.key == "cc-pdm-1.0"
        assert v.family.key == "public-domain"

    def test_cc_pdm_versioned_key(self):
        v = normalise_license("cc-pdm-1.0")
        assert v.key == "cc-pdm-1.0"
        assert v.family.key == "public-domain"

    def test_cc0_bare_key(self):
        v = normalise_license("cc0")
        assert v.key == "cc0-1.0"
        assert v.family.key == "cc0"

    def test_cc0_versioned_key(self):
        v = normalise_license("cc0-1.0")
        assert v.key == "cc0-1.0"
        assert v.family.key == "cc0"

    def test_cc_zero_shorthand(self):
        v = normalise_license("cc-zero")
        assert v.key == "cc0-1.0"
        assert v.family.key == "cc0"

    def test_public_domain_fallback(self):
        v = normalise_license("public-domain")
        assert v.key == "public-domain"
        assert v.family.key == "public-domain"

    def test_creative_commons_zero(self):
        v = normalise_license("creative commons zero")
        assert v.key == "cc0-1.0"
        assert v.family.key == "cc0"

    def test_creative_commons_public_domain(self):
        v = normalise_license("creative commons public domain")
        assert v.key == "cc-pdm-1.0"
        assert v.family.key == "public-domain"
