"""Tests for trace and explain functionality."""

from licence_normaliser import normalise_licence, normalise_licences

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestTraceAPI:
    def test_trace_true_returns_result_with_trace(self) -> None:
        v = normalise_licence("MIT", trace=True)
        assert v._trace is not None

    def test_explain_returns_string_with_stages(self) -> None:
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert isinstance(output, str)
        assert "Input:" in output
        assert (
            "alias" in output
            or "registry" in output
            or "prose" in output
            or "fallback" in output
        )

    def test_explain_contains_result_keys(self) -> None:
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert "Result:" in output
        assert "version_key:" in output
        assert "name_key:" in output
        assert "family_key:" in output

    def test_trace_disabled_returns_message_when_no_trace(self) -> None:
        v = normalise_licence("MIT")
        output = v.explain()
        assert "Trace disabled" in output or "No trace available" in output

    def test_trace_false_no_trace_in_result(self) -> None:
        v = normalise_licence("MIT", trace=False)
        assert v._trace is None


class TestTraceResolutionStages:
    def test_trace_alias_stage_matched(self) -> None:
        v = normalise_licence("CC BY 4.0", trace=True)
        output = v.explain()
        assert "[✓]" in output
        assert "alias" in output

    def test_trace_registry_stage_matched(self) -> None:
        v = normalise_licence("mit", trace=True)
        output = v.explain()
        assert "[✓]" in output

    def test_trace_fallback_for_unknown(self) -> None:
        v = normalise_licence("completely-unknown-xyz-123", trace=True)
        output = v.explain()
        assert "fallback" in output
        assert "[✓]" in output


class TestTraceSourceInfo:
    def test_trace_shows_alias_source_line(self) -> None:
        v = normalise_licence("CC BY 4.0", trace=True)
        output = v.explain()
        assert "line" in output.lower()

    def test_trace_shows_registry_source_line(self) -> None:
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert "line" in output.lower()
        assert "scancode_licensedb.json" in output

    def test_trace_shows_registry_source_for_gpl(self) -> None:
        v = normalise_licence("gpl-3.0", trace=True)
        output = v.explain()
        assert "line" in output.lower()
        assert "scancode_licensedb.json" in output

    def test_trace_shows_registry_source_for_apache(self) -> None:
        v = normalise_licence("apache-2.0", trace=True)
        output = v.explain()
        assert "line" in output.lower()

    def test_trace_shows_prose_source_line(self) -> None:
        v = normalise_licence(
            "This is an open access article under the CC BY-NC-ND license.",
            trace=True,
        )
        output = v.explain()
        assert "line" in output.lower()
        assert "prose_patterns.json" in output


class TestTraceEnvVariable:
    def test_env_variable_enables_trace(self, monkeypatch) -> None:
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "1")
        v = normalise_licence("MIT")
        assert v._trace is not None

    def test_env_variable_true_enables_trace(self, monkeypatch) -> None:
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "true")
        v = normalise_licence("MIT")
        assert v._trace is not None

    def test_env_variable_yes_enables_trace(self, monkeypatch) -> None:
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "yes")
        v = normalise_licence("MIT")
        assert v._trace is not None

    def test_env_variable_disabled_no_trace(self, monkeypatch) -> None:
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "0")
        v = normalise_licence("MIT")
        assert v._trace is None


class TestTraceContent:
    def test_trace_includes_raw_and_cleaned_input(self) -> None:
        v = normalise_licence("  MIT  ", trace=True)
        output = v.explain()
        assert "MIT" in output

    def test_trace_version_key_matches_result(self) -> None:
        v = normalise_licence("MIT", trace=True)
        trace_str = v.explain()
        assert v.key in trace_str

    def test_trace_family_in_output(self) -> None:
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert v.family.key in output

    def test_trace_name_in_output(self) -> None:
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert v.licence.key in output


class TestTraceURLResolution:
    def test_trace_url_lookup(self) -> None:
        v = normalise_licence(
            "https://creativecommons.org/licenses/by/4.0/", trace=True
        )
        output = v.explain()
        assert "url" in output


class TestTraceProseResolution:
    def test_trace_prose_pattern(self) -> None:
        v = normalise_licence("Apache License 2.0", trace=True)
        output = v.explain()
        assert "[✓]" in output

    def test_trace_prose_pattern_output(self) -> None:
        v = normalise_licence("The Apache Software Foundation License 2.0", trace=True)
        output = v.explain()
        assert "prose" in output


class TestBatchTrace:
    def test_batch_with_trace(self) -> None:
        results = normalise_licences(["MIT", "Apache-2.0"], trace=True)
        assert len(results) == 2
        assert results[0]._trace is not None
        assert results[1]._trace is not None
        assert "mit" in results[0].explain()
        assert "apache-2.0" in results[1].explain()

    def test_batch_strict_with_trace(self) -> None:
        results = normalise_licences(["MIT", "GPL-3.0"], strict=True, trace=True)
        assert len(results) == 2
        assert results[0]._trace is not None
        assert results[1]._trace is not None

    def test_batch_mixed_known_unknown_with_trace(self) -> None:
        results = normalise_licences(["MIT", "unknown-xyz-123"], trace=True)
        assert len(results) == 2
        assert results[0]._trace is not None
        assert results[1]._trace is not None


class TestTraceEmptyInput:
    def test_trace_empty_input(self) -> None:
        v = normalise_licence("", trace=True)
        assert v._trace is not None
        output = v.explain()
        assert "fallback" in output

    def test_trace_whitespace_only_input(self) -> None:
        v = normalise_licence("   ", trace=True)
        assert v._trace is not None
        output = v.explain()
        assert "fallback" in output


class TestTracePublisherURL:
    def test_trace_publisher_url_source(self) -> None:
        v = normalise_licence(
            "https://www.elsevier.com/open-access/userlicense/1.0/", trace=True
        )
        output = v.explain()
        assert "url" in output
        assert "aliases.json" in output

    def test_trace_publisher_alias_with_line(self) -> None:
        v = normalise_licence("Elsevier User License", trace=True)
        output = v.explain()
        assert "[✓]" in output


class TestTraceFamilyInference:
    def test_infer_family_cc_pdm(self) -> None:
        v = normalise_licence("cc-pdm-1.0")
        assert v.family.key == "public-domain"

    def test_infer_family_odbl(self) -> None:
        v = normalise_licence("odbl-1.0")
        assert v.family.key == "open-data"

    def test_infer_family_pddl(self) -> None:
        v = normalise_licence("pddl-1.0")
        assert v.family.key == "data"

    def test_infer_family_implied_oa(self) -> None:
        v = normalise_licence("implied-oa")
        assert v.family.key == "publisher-oa"

    def test_infer_family_elsevier_tdm(self) -> None:
        v = normalise_licence("elsevier-tdm")
        assert v.family.key == "publisher-tdm"

    def test_infer_family_wiley(self) -> None:
        v = normalise_licence("wiley-terms")
        assert v.family.key == "publisher-proprietary"

    def test_infer_family_public_domain(self) -> None:
        v = normalise_licence("public-domain")
        assert v.family.key == "public-domain"

    def test_infer_family_other_oa(self) -> None:
        v = normalise_licence("other-oa")
        assert v.family.key == "other-oa"
