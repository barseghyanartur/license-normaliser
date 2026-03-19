"""Tests for the data_sources package.

These tests verify that:
- Each built-in source loads without error from the real data files.
- Contributions contain valid structure (dicts of strings).
- The merged registry built by _registry.py is internally consistent.
- SPDX and OpenDefinition sources load cleanly and their contributions
  pass validation (unknown version keys are silently filtered).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from license_normaliser._registry import (
    ALIASES,
    PROSE_PATTERNS,
    URL_MAP,
    VERSION_REGISTRY,
)
from license_normaliser.data_sources import SourceContribution, load_all_sources
from license_normaliser.data_sources.builtin_aliases import BuiltinAliasSource
from license_normaliser.data_sources.builtin_prose import BuiltinProseSource
from license_normaliser.data_sources.builtin_urls import BuiltinUrlSource
from license_normaliser.data_sources.opendefinition import OpenDefinitionSource
from license_normaliser.data_sources.spdx import SpdxSource
from license_normaliser.exceptions import DataSourceError

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


def _data_dir() -> Path:
    """Return the real data/ directory used by the package."""
    return Path(__file__).parent.parent / "data"


class TestSourceContribution:
    def test_construction(self):
        c = SourceContribution("test", {"a": "b"}, {"u": "v"}, {"p": "q"})
        assert c.name == "test"
        assert c.aliases == {"a": "b"}
        assert c.url_map == {"u": "v"}
        assert c.prose == {"p": "q"}


class TestBuiltinAliasSource:
    def test_loads_without_error(self):
        src = BuiltinAliasSource()
        contrib = src.load(_data_dir())
        assert isinstance(contrib.aliases, dict)
        assert len(contrib.aliases) > 0
        assert contrib.url_map == {}
        assert contrib.prose == {}

    def test_mit_alias_present(self):
        src = BuiltinAliasSource()
        contrib = src.load(_data_dir())
        assert contrib.aliases.get("mit license") == "mit"

    def test_cc_by_4_0_alias_present(self):
        src = BuiltinAliasSource()
        contrib = src.load(_data_dir())
        assert contrib.aliases.get("cc by 4.0") == "cc-by-4.0"

    def test_all_keys_are_strings(self):
        src = BuiltinAliasSource()
        contrib = src.load(_data_dir())
        for k, v in contrib.aliases.items():
            assert isinstance(k, str), f"Non-string key: {k!r}"
            assert isinstance(v, str), f"Non-string value: {v!r}"

    def test_missing_file_raises_data_source_error(self, tmp_path):
        src = BuiltinAliasSource()
        with pytest.raises(DataSourceError):
            src.load(tmp_path)


class TestBuiltinUrlSource:
    def test_loads_without_error(self):
        src = BuiltinUrlSource()
        contrib = src.load(_data_dir())
        assert isinstance(contrib.url_map, dict)
        assert len(contrib.url_map) > 0
        assert contrib.aliases == {}

    def test_cc_by_4_url_present(self):
        src = BuiltinUrlSource()
        contrib = src.load(_data_dir())
        # After normalisation: https, no trailing slash
        key = "https://creativecommons.org/licenses/by/4.0"
        assert contrib.url_map.get(key) == "cc-by-4.0"

    def test_no_http_keys(self):
        src = BuiltinUrlSource()
        contrib = src.load(_data_dir())
        http_keys = [k for k in contrib.url_map if k.startswith("http://")]
        assert not http_keys, f"Found raw http:// keys: {http_keys[:3]}"

    def test_no_trailing_slash_keys(self):
        src = BuiltinUrlSource()
        contrib = src.load(_data_dir())
        slash_keys = [k for k in contrib.url_map if k.endswith("/")]
        assert not slash_keys, f"Found trailing-slash keys: {slash_keys[:3]}"

    def test_missing_file_raises_data_source_error(self, tmp_path):
        src = BuiltinUrlSource()
        with pytest.raises(DataSourceError):
            src.load(tmp_path)


class TestBuiltinProseSource:
    def test_loads_without_error(self):
        src = BuiltinProseSource()
        contrib = src.load(_data_dir())
        assert isinstance(contrib.prose, dict)
        assert len(contrib.prose) > 0
        assert contrib.aliases == {}
        assert contrib.url_map == {}

    def test_all_rights_reserved_pattern_present(self):
        src = BuiltinProseSource()
        contrib = src.load(_data_dir())
        assert "all-rights-reserved" in contrib.prose.values()

    def test_missing_file_raises_data_source_error(self, tmp_path):
        src = BuiltinProseSource()
        with pytest.raises(DataSourceError):
            src.load(tmp_path)


class TestSpdxSource:
    def test_loads_without_error(self):
        src = SpdxSource()
        contrib = src.load(_data_dir())
        assert isinstance(contrib.aliases, dict)
        assert isinstance(contrib.url_map, dict)

    def test_mit_alias_present(self):
        src = SpdxSource()
        contrib = src.load(_data_dir())
        assert contrib.aliases.get("mit") == "mit"

    def test_no_http_url_keys(self):
        src = SpdxSource()
        contrib = src.load(_data_dir())
        http_keys = [k for k in contrib.url_map if k.startswith("http://")]
        assert not http_keys

    def test_missing_spdx_file_returns_empty(self, tmp_path):
        # SPDX file is optional - missing file gives empty contribution
        src = SpdxSource()
        contrib = src.load(tmp_path)
        assert contrib.aliases == {}
        assert contrib.url_map == {}

    def test_malformed_json_raises_data_source_error(self, tmp_path):
        spdx_dir = tmp_path / "spdx"
        spdx_dir.mkdir()
        (spdx_dir / "spdx-licenses.json").write_text("NOT JSON")
        src = SpdxSource()
        with pytest.raises(DataSourceError):
            src.load(tmp_path)


class TestOpenDefinitionSource:
    def test_loads_without_error(self):
        src = OpenDefinitionSource()
        contrib = src.load(_data_dir())
        assert isinstance(contrib.aliases, dict)
        assert isinstance(contrib.url_map, dict)

    def test_mit_alias_present(self):
        src = OpenDefinitionSource()
        contrib = src.load(_data_dir())
        assert contrib.aliases.get("mit") == "mit"

    def test_missing_od_file_returns_empty(self, tmp_path):
        src = OpenDefinitionSource()
        contrib = src.load(tmp_path)
        assert contrib.aliases == {}

    def test_legacy_ids_registered(self):
        src = OpenDefinitionSource()
        contrib = src.load(_data_dir())
        # apache2.0 is a legacy_id for Apache-2.0 in the OD file
        assert contrib.aliases.get("apache2.0") == "apache-2.0"


class TestLoadAllSources:
    def test_returns_list(self):
        contribs = load_all_sources(_data_dir())
        assert isinstance(contribs, list)
        assert len(contribs) > 0

    def test_all_are_source_contributions(self):
        contribs = load_all_sources(_data_dir())
        for c in contribs:
            assert isinstance(c, SourceContribution)

    def test_empty_dir_returns_partial_list(self, tmp_path):
        # Built-in sources require data files; SPDX/OD are optional.
        # With a completely empty dir, built-in sources raise DataSourceError
        # and are skipped - we get a list (possibly empty).
        contribs = load_all_sources(tmp_path)
        assert isinstance(contribs, list)


class TestMergedRegistry:
    """Validate that the merged VERSION_REGISTRY / ALIASES / URL_MAP are consistent."""

    def test_all_alias_targets_in_version_registry(self):
        bad = {k: v for k, v in ALIASES.items() if v not in VERSION_REGISTRY}
        assert not bad, f"Aliases pointing to unknown version keys: {bad}"

    def test_all_url_map_targets_in_version_registry(self):
        bad = {k: v for k, v in URL_MAP.items() if v not in VERSION_REGISTRY}
        assert not bad, f"URL map entries pointing to unknown version keys: {bad}"

    def test_prose_patterns_compile(self):
        # PROSE_PATTERNS contains (compiled_pattern, vkey) tuples
        for pattern, vkey in PROSE_PATTERNS:
            assert hasattr(pattern, "search"), f"Non-compiled pattern: {pattern!r}"
            assert isinstance(vkey, str)

    def test_prose_vkeys_in_registry(self):
        bad = [(p.pattern, v) for p, v in PROSE_PATTERNS if v not in VERSION_REGISTRY]
        assert not bad, f"Prose patterns pointing to unknown version keys: {bad}"

    def test_version_registry_has_unknown(self):
        assert "unknown" in VERSION_REGISTRY

    def test_version_registry_has_mit(self):
        assert "mit" in VERSION_REGISTRY

    def test_version_registry_has_cc_by_4_0(self):
        assert "cc-by-4.0" in VERSION_REGISTRY

    def test_no_url_map_key_has_trailing_slash(self):
        trailing = [k for k in URL_MAP if k.endswith("/")]
        assert not trailing, f"URL_MAP keys with trailing slash: {trailing[:5]}"

    def test_no_url_map_key_starts_with_http(self):
        http_keys = [k for k in URL_MAP if k.startswith("http://")]
        assert not http_keys, f"URL_MAP keys with http://: {http_keys[:5]}"
