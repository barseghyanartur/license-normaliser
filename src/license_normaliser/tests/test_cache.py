"""Unit tests for _cache.py."""

import threading

import pytest

from license_normaliser._cache import (
    _clean,
    normalise_license_cached,
    normalise_licenses,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestClean:
    def test_strips_leading_whitespace(self):
        assert _clean("  MIT") == "mit"

    def test_strips_trailing_whitespace(self):
        assert _clean("MIT  ") == "mit"

    def test_strips_trailing_slash(self):
        assert _clean("https://example.com/") == "https://example.com"

    def test_collapses_internal_whitespace(self):
        assert _clean("CC  BY   4.0") == "cc by 4.0"

    def test_lowercases(self):
        assert _clean("Apache-2.0") == "apache-2.0"

    def test_max_input_truncation(self):
        from license_normaliser._cache import _MAX_INPUT

        long_input = "x" * (_MAX_INPUT + 100)
        result = _clean(long_input)
        assert len(result) == _MAX_INPUT

    def test_empty_string(self):
        assert _clean("") == ""

    def test_newline_collapsed(self):
        assert _clean("CC BY\n4.0") == "cc by 4.0"


class TestNormaliseLicenseCached:
    def test_mit_basic(self):
        v = normalise_license_cached("MIT")
        assert v.key == "mit"

    def test_whitespace_variants_share_result(self):
        v1 = normalise_license_cached("MIT")
        v2 = normalise_license_cached("MIT ")
        v3 = normalise_license_cached("  MIT  ")
        assert v1.key == v2.key == v3.key == "mit"

    def test_case_variants_share_result(self):
        v1 = normalise_license_cached("Apache-2.0")
        v2 = normalise_license_cached("apache-2.0")
        assert v1.key == v2.key == "apache-2.0"

    def test_empty_string_returns_unknown(self):
        v = normalise_license_cached("")
        assert v.key == "unknown"

    def test_whitespace_only_returns_unknown(self):
        v = normalise_license_cached("   ")
        assert v.key == "unknown"

    def test_cc_by_4_0_various_forms(self):
        forms = [
            "CC BY 4.0",
            "cc by 4.0",
            "cc-by-4.0",
            "http://creativecommons.org/licenses/by/4.0/",
            "https://creativecommons.org/licenses/by/4.0/",
        ]
        for form in forms:
            v = normalise_license_cached(form)
            assert v.key == "cc-by-4.0", f"Failed for: {form!r}"

    def test_url_http_and_https_same_result(self):
        v_http = normalise_license_cached(
            "http://creativecommons.org/licenses/by-nc-nd/4.0/"
        )
        v_https = normalise_license_cached(
            "https://creativecommons.org/licenses/by-nc-nd/4.0/"
        )
        assert v_http.key == v_https.key == "cc-by-nc-nd-4.0"

    def test_unknown_input_uses_cleaned_key(self):
        v = normalise_license_cached("Some Unknown License 999")
        assert v.key == "some unknown license 999"
        assert v.family.key == "unknown"

    def test_result_is_frozen(self):
        v = normalise_license_cached("MIT")
        with pytest.raises((AttributeError, TypeError)):
            v.key = "other"  # type: ignore[misc]

    def test_concurrent_calls_consistent(self):
        results = []
        barrier = threading.Barrier(10)

        def _call():
            barrier.wait()
            results.append(normalise_license_cached("CC BY 4.0").key)

        threads = [threading.Thread(target=_call) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert all(r == "cc-by-4.0" for r in results)


class TestMojibakeDecode:
    def test_copyright_symbol_mojibake(self):
        mojibake = "\xc2\xa9 the author(s)"
        v = normalise_license_cached(mojibake)
        assert v.key == "publisher-specific-oa"

    def test_clean_copyright_symbol(self):
        v = normalise_license_cached("\u00a9 the author(s)")
        assert v.key == "publisher-specific-oa"


class TestNormalizeLicenses:
    def test_basic_batch(self, batch_raw):
        results = normalise_licenses(batch_raw)
        assert len(results) == 3
        assert results[0].key == "mit"
        assert results[1].key == "apache-2.0"
        assert results[2].key == "cc-by-4.0"

    def test_accepts_generator(self):
        gen = (x for x in ["MIT", "GPL-3.0"])
        results = normalise_licenses(gen)
        assert results[0].key == "mit"
        assert results[1].key == "gpl-3.0"

    def test_empty_iterable(self):
        assert normalise_licenses([]) == []

    def test_mixed_known_unknown(self):
        results = normalise_licenses(["MIT", "no-such-license"])
        assert results[0].key == "mit"
        assert results[1].family.key == "unknown"
