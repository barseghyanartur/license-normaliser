"""Tests for trace and explain functionality."""

from licence_normaliser import normalise_licence

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestTraceAPI:
    def test_trace_true_returns_result_with_trace(self):
        v = normalise_licence("MIT", trace=True)
        assert v._trace is not None

    def test_explain_returns_string_with_stages(self):
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

    def test_explain_contains_result_keys(self):
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert "Result:" in output
        assert "version_key:" in output
        assert "name_key:" in output
        assert "family_key:" in output

    def test_trace_disabled_returns_message_when_no_trace(self):
        v = normalise_licence("MIT")
        output = v.explain()
        assert "Trace disabled" in output or "No trace available" in output

    def test_trace_false_no_trace_in_result(self):
        v = normalise_licence("MIT", trace=False)
        assert v._trace is None


class TestTraceResolutionStages:
    def test_trace_alias_stage_matched(self):
        v = normalise_licence("CC BY 4.0", trace=True)
        output = v.explain()
        assert "[✓]" in output
        assert "alias" in output

    def test_trace_registry_stage_matched(self):
        v = normalise_licence("mit", trace=True)
        output = v.explain()
        assert "[✓]" in output

    def test_trace_fallback_for_unknown(self):
        v = normalise_licence("completely-unknown-xyz-123", trace=True)
        output = v.explain()
        assert "fallback" in output
        assert "[✓]" in output


class TestTraceSourceInfo:
    def test_trace_shows_alias_source_line(self):
        v = normalise_licence("CC BY 4.0", trace=True)
        output = v.explain()
        assert "line" in output.lower()


class TestTraceEnvVariable:
    def test_env_variable_enables_trace(self, monkeypatch):
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "1")
        v = normalise_licence("MIT")
        assert v._trace is not None

    def test_env_variable_true_enables_trace(self, monkeypatch):
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "true")
        v = normalise_licence("MIT")
        assert v._trace is not None

    def test_env_variable_yes_enables_trace(self, monkeypatch):
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "yes")
        v = normalise_licence("MIT")
        assert v._trace is not None

    def test_env_variable_disabled_no_trace(self, monkeypatch):
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "0")
        v = normalise_licence("MIT")
        assert v._trace is None


class TestTraceContent:
    def test_trace_includes_raw_and_cleaned_input(self):
        v = normalise_licence("  MIT  ", trace=True)
        output = v.explain()
        assert "MIT" in output

    def test_trace_version_key_matches_result(self):
        v = normalise_licence("MIT", trace=True)
        trace_str = v.explain()
        assert v.key in trace_str

    def test_trace_family_in_output(self):
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert v.family.key in output

    def test_trace_name_in_output(self):
        v = normalise_licence("MIT", trace=True)
        output = v.explain()
        assert v.licence.key in output


class TestTraceURLResolution:
    def test_trace_url_lookup(self):
        v = normalise_licence(
            "https://creativecommons.org/licenses/by/4.0/", trace=True
        )
        output = v.explain()
        assert "url" in output


class TestTraceProseResolution:
    def test_trace_prose_pattern(self):
        v = normalise_licence("Apache License 2.0", trace=True)
        output = v.explain()
        assert "[✓]" in output
