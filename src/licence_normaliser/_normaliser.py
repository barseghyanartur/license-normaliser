"""Plugin-based LicenceNormaliser class with configurable constructor injection."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING, Iterable, Sequence

from licence_normaliser.defaults import (
    get_default_alias,
    get_default_family,
    get_default_name,
    get_default_prose,
    get_default_registry,
    get_default_url,
)

if TYPE_CHECKING:
    from licence_normaliser._models import LicenceVersion
    from licence_normaliser._trace import LicenceTrace

from licence_normaliser._models import LicenceFamily, LicenceName, LicenceVersion
from licence_normaliser._trace import LicenceTrace, LicenceTraceStage, _should_trace
from licence_normaliser.exceptions import DataSourceError, LicenceNotFoundError

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("LicenceNormaliser",)

_WHITESPACE_RE = re.compile(r"\s+")
_MAX_INPUT = 4096


class LicenceNormaliser:
    """Configurable licence normalisation with plugin-based data sources.

    Plugins are passed as CLASSES (not instances). They're instantiated lazily
    when their load_* method is called.

    Six plugin types are supported (each returns specific data structure):
        - registry: key -> canonical_key
        - url: cleaned_url -> version_key
        - alias: alias_string -> version_key
        - family: version_key -> family_key
        - name: version_key -> name_key
        - prose: list of (compiled_pattern, version_key)

    Resolution order: aliases -> registry -> url -> prose -> unknown
    Name/family inference: plugins only - no fallback to hardcoded logic.

    Tracing
        Set ``trace=True`` to include resolution trace in the result. Trace shows
        which pipeline stage matched and the source file/line number (when
        available). Trace is disabled by default for performance.

        Trace can be enabled at three levels (precedence: method >
        constructor > env var):

        - **Constructor**: ``LicenceNormaliser(trace=True)`` - all calls get trace
        - **Method**: ``ln.normalise_licence("MIT", trace=True)`` - this call only
        - **Environment**: ``ENABLE_LICENCE_NORMALISER_TRACE=1`` - applies globally

    Example::

        from licence_normaliser import LicenceNormaliser

        # Uses all defaults automatically
        ln = LicenceNormaliser()

        # Disable caching for debugging
        ln = LicenceNormaliser(cache=False)

        # Enable trace for all calls on this instance
        ln = LicenceNormaliser(trace=True)
        v = ln.normalise_licence("MIT")
        print(v.explain())  # Shows resolution path with source lines

        # Or enable trace for a single call
        v = ln.normalise_licence("MIT", trace=True)
    """

    def __init__(
        self,
        *,
        registry: Sequence[type] | None = None,
        url: Sequence[type] | None = None,
        alias: Sequence[type] | None = None,
        family: Sequence[type] | None = None,
        name: Sequence[type] | None = None,
        prose: Sequence[type] | None = None,
        cache: bool = True,
        cache_maxsize: int = 8192,
        trace: bool | None = None,
    ) -> None:
        self._registry: dict[str, str] = {}
        self._url_map: dict[str, str] = {}
        self._vkey_to_url: dict[str, list[str]] = {}
        self._aliases: dict[str, str] = {}
        self._alias_lines: dict[str, tuple[str, int]] = {}
        self._url_plugin_alias_lines: dict[str, tuple[str, int]] = {}
        self._url_plugin_url_lines: dict[str, tuple[str, int]] = {}
        self._prose_lines: list[tuple[re.Pattern[str], str, int]] = []
        self._alias_lines_loaded: bool = False
        self._family_overrides: dict[str, str] = {}
        self._name_overrides: dict[str, str] = {}
        self._prose_patterns: list[tuple[re.Pattern[str], str]] = []
        self._cache = cache
        self._cache_maxsize = cache_maxsize
        self._trace_default = trace

        # Load plugins - use defaults if not explicitly provided
        registry = registry or get_default_registry()
        url = url or get_default_url()
        alias = alias or get_default_alias()
        family = family or get_default_family()
        name = name or get_default_name()
        prose = prose or get_default_prose()

        # Store plugin lists for trace resolution
        self._alias_plugins = alias
        self._url_plugins = url
        self._prose_plugins = prose

        # Instantiate plugins and load their data
        try:
            for plugin_cls in registry:
                data = plugin_cls().load_registry()
                self._registry.update(data)
        except OSError as exc:
            raise DataSourceError(
                f"Failed to load registry from {plugin_cls.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise DataSourceError(
                f"Error loading registry from {plugin_cls.__name__}: {exc}"
            ) from exc

        try:
            for plugin_cls in url:
                data = plugin_cls().load_urls()
                self._url_map.update(data)
        except OSError as exc:
            raise DataSourceError(
                f"Failed to load URLs from {plugin_cls.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise DataSourceError(
                f"Error loading URLs from {plugin_cls.__name__}: {exc}"
            ) from exc

        # Build version_key -> list of URLs map (for LicenceVersion.url)
        # For each version_key, collect all URLs; select shortest for cleaner display
        self._vkey_to_url: dict[str, list[str]] = {}
        for url, vkey in self._url_map.items():
            if vkey not in self._vkey_to_url:
                self._vkey_to_url[vkey] = []
            self._vkey_to_url[vkey].append(url)

        try:
            for plugin_cls in alias:
                data = plugin_cls().load_aliases()
                self._aliases.update(data)
        except OSError as exc:
            raise DataSourceError(
                f"Failed to load aliases from {plugin_cls.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise DataSourceError(
                f"Error loading aliases from {plugin_cls.__name__}: {exc}"
            ) from exc

        try:
            for plugin_cls in family:
                data = plugin_cls().load_families()
                self._family_overrides.update(data)
        except OSError as exc:
            raise DataSourceError(
                f"Failed to load families from {plugin_cls.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise DataSourceError(
                f"Error loading families from {plugin_cls.__name__}: {exc}"
            ) from exc

        try:
            for plugin_cls in name:
                data = plugin_cls().load_names()
                self._name_overrides.update(data)
        except OSError as exc:
            raise DataSourceError(
                f"Failed to load names from {plugin_cls.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise DataSourceError(
                f"Error loading names from {plugin_cls.__name__}: {exc}"
            ) from exc

        try:
            for plugin_cls in prose:
                patterns = plugin_cls().load_prose()
                self._prose_patterns.extend(patterns)
        except OSError as exc:
            raise DataSourceError(
                f"Failed to load prose patterns from {plugin_cls.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise DataSourceError(
                f"Error loading prose patterns from {plugin_cls.__name__}: {exc}"
            ) from exc

        # Set up cached resolution
        if self._cache:
            resolve_fn = lru_cache(maxsize=self._cache_maxsize)(self._resolve_impl)
            # type: ignore[assignment]
            self._resolve_impl = resolve_fn

    def _get_trace_mode(self, trace: bool | None) -> bool:
        """Determine if tracing is enabled: explicit > env var > default."""
        if trace is not None:
            return trace
        if self._trace_default is not None:
            return self._trace_default
        return _should_trace()

    def _load_alias_lines(self):
        """Lazy load all source line numbers on first trace request."""
        try:
            for plugin_cls in self._alias_plugins:
                if hasattr(plugin_cls, "load_aliases_with_lines"):
                    lines_data = plugin_cls().load_aliases_with_lines()
                    for alias_key, (version_key, line_num) in lines_data.items():
                        if version_key == self._aliases.get(alias_key):
                            self._alias_lines[alias_key] = (version_key, line_num)

            for plugin_cls in self._url_plugins:
                if hasattr(plugin_cls, "load_aliases_with_lines"):
                    lines_data = plugin_cls().load_aliases_with_lines()
                    for alias_key, (version_key, line_num) in lines_data.items():
                        if version_key == self._aliases.get(alias_key):
                            self._url_plugin_alias_lines[alias_key] = (
                                version_key,
                                line_num,
                            )

            for plugin_cls in self._url_plugins:
                if hasattr(plugin_cls, "load_urls_with_lines"):
                    lines_data = plugin_cls().load_urls_with_lines()
                    for url_key, (version_key, line_num) in lines_data.items():
                        if version_key == self._url_map.get(url_key):
                            self._url_plugin_url_lines[url_key] = (
                                version_key,
                                line_num,
                            )

            for plugin_cls in self._prose_plugins:
                if hasattr(plugin_cls, "load_prose_with_lines"):
                    lines_data = plugin_cls().load_prose_with_lines()
                    self._prose_lines.extend(lines_data)
        except OSError as exc:
            raise DataSourceError(f"Failed to load trace line numbers: {exc}") from exc
        except Exception as exc:
            raise DataSourceError(f"Error loading trace line numbers: {exc}") from exc

    def _resolve_with_trace(
        self, raw: str, cleaned: str, strict: bool
    ) -> LicenceVersion:
        """Resolve with full pipeline tracing."""

        # Lazy load alias lines on first trace call
        if not self._alias_lines_loaded:
            self._load_alias_lines()
            self._alias_lines_loaded = True

        stages: list[LicenceTraceStage] = []

        # 1. Alias lookup
        if cleaned in self._aliases:
            output = self._aliases[cleaned]
            source_line = None
            source_file = None
            if cleaned in self._alias_lines:
                _, source_line = self._alias_lines[cleaned]
                source_file = "aliases.json"
            stages.append(
                LicenceTraceStage(
                    "alias", cleaned, output, True, source_line, source_file
                )
            )
            v = self._make(output)
            trace = LicenceTrace(
                raw,
                cleaned,
                stages,
                version_key=v.key,
                name_key=v.licence.key,
                family_key=v.family.key,
            )
            return self._make_with_trace(v, trace)

        stages.append(LicenceTraceStage("alias", cleaned, "", False))

        # 2. Registry lookup
        if cleaned in self._registry:
            canonical = self._registry[cleaned]
            stages.append(LicenceTraceStage("registry", cleaned, canonical, True))
            v = self._make(canonical)
            trace = LicenceTrace(
                raw,
                cleaned,
                stages,
                version_key=v.key,
                name_key=v.licence.key,
                family_key=v.family.key,
            )
            return self._make_with_trace(v, trace)

        stages.append(LicenceTraceStage("registry", cleaned, "", False))

        # 3. URL lookup
        url_key = self._normalise_url(cleaned)
        if url_key in self._url_map:
            resolved = self._url_map[url_key]
            source_line = None
            source_file = None
            if url_key in self._url_plugin_url_lines:
                _, source_line = self._url_plugin_url_lines[url_key]
                source_file = "aliases.json"
            stages.append(
                LicenceTraceStage(
                    "url", url_key, resolved, True, source_line, source_file
                )
            )
            v = self._make(resolved)
            trace = LicenceTrace(
                raw,
                cleaned,
                stages,
                version_key=v.key,
                name_key=v.licence.key,
                family_key=v.family.key,
            )
            return self._make_with_trace(v, trace)

        stages.append(LicenceTraceStage("url", cleaned, "", False))

        # 4. Prose matching (only for longer strings)
        if len(cleaned) >= 20:
            for i, (pattern, vkey) in enumerate(self._prose_patterns):
                if pattern.search(cleaned):
                    source_line = None
                    source_file = "aliases.json"
                    if self._prose_lines and i < len(self._prose_lines):
                        _, _, source_line = self._prose_lines[i]
                    stages.append(
                        LicenceTraceStage(
                            "prose", cleaned, vkey, True, source_line, source_file
                        )
                    )
                    v = self._make(vkey)
                    trace = LicenceTrace(
                        raw,
                        cleaned,
                        stages,
                        version_key=v.key,
                        name_key=v.licence.key,
                        family_key=v.family.key,
                    )
                    return self._make_with_trace(v, trace)

        stages.append(LicenceTraceStage("prose", cleaned, "", False))

        # 5. Fallback to unknown
        stages.append(LicenceTraceStage("fallback", cleaned, cleaned, True))
        v = self._make_unknown(cleaned)
        trace = LicenceTrace(
            raw,
            cleaned,
            stages,
            version_key=v.key,
            name_key=v.licence.key,
            family_key=v.family.key,
        )
        return self._make_with_trace(v, trace)

    def _make_with_trace(
        self, v: LicenceVersion, trace: LicenceTrace
    ) -> LicenceVersion:
        """Create a LicenceVersion with trace attached."""
        # Create new instance with trace (proper way for frozen dataclass)
        return LicenceVersion(
            key=v.key,
            url=v.url,
            licence=v.licence,
            _trace=trace,
        )

    def _resolve_impl(self, cleaned: str) -> LicenceVersion:
        # 1. Alias lookup
        if cleaned in self._aliases:
            return self._make(self._aliases[cleaned])

        # 2. Registry lookup
        if cleaned in self._registry:
            canonical = self._registry[cleaned]
            return self._make(canonical)

        # 3. URL lookup
        url_key = self._normalise_url(cleaned)
        if url_key in self._url_map:
            return self._make(self._url_map[url_key])

        # 4. Prose matching (only for longer strings)
        if len(cleaned) >= 20:
            for pattern, vkey in self._prose_patterns:
                if pattern.search(cleaned):
                    return self._make(vkey)

        # 5. Fallback to unknown
        return self._make_unknown(cleaned)

    def normalise_licence(
        self, raw: str, *, strict: bool = False, trace: bool | None = None
    ) -> LicenceVersion:
        """Normalise a single licence string.

        Args:
            raw: The raw licence string, SPDX ID, URL, or prose description.
            strict: If True, raises ``LicenceNotFoundError`` when the input
                cannot be resolved to a known licence.
            trace: If True, include resolution trace showing which pipeline
                stage matched and source file/line. If None, uses the instance
                default (``trace`` param from constructor) or falls back to
                ``ENABLE_LICENCE_NORMALISER_TRACE`` env var.

        Returns:
            A ``LicenceVersion`` with the resolved key, licence name, and family.

        Raises:
            LicenceNotFoundError: When ``strict=True`` and resolution fails.
        """
        do_trace = self._get_trace_mode(trace)

        if not raw or not raw.strip():
            cleaned = "unknown"
            v = self._make_unknown(cleaned)
            if do_trace:
                stages = [LicenceTraceStage("fallback", cleaned, cleaned, True)]
                trace_obj = LicenceTrace(
                    raw,
                    cleaned,
                    stages,
                    version_key=v.key,
                    name_key=v.licence.key,
                    family_key=v.family.key,
                )
                v = self._make_with_trace(v, trace_obj)
        else:
            cleaned = self._clean(self._try_decode_mojibake(raw))
            if do_trace:
                v = self._resolve_with_trace(raw, cleaned, strict)
            else:
                v = self._resolve_impl(cleaned)

        if strict and v.family.key == "unknown":
            raise LicenceNotFoundError(raw, v.key) from None
        return v

    def normalise_licences(
        self, raws: Iterable[str], *, strict: bool = False, trace: bool | None = None
    ) -> list[LicenceVersion]:
        """Batch normalisation.

        When ``strict=True``, raises on the first failure.
        """
        results: list[LicenceVersion] = []
        for raw in raws:
            v = self.normalise_licence(raw, strict=False, trace=trace)
            if strict and v.family.key == "unknown":
                raise LicenceNotFoundError(raw, v.key) from None
            results.append(v)
        return results

    def registry_keys(self) -> set[str]:
        """Return the set of all known registry keys."""
        return set(self._registry.keys())

    def _make(self, key: str) -> LicenceVersion:
        """Factory: build a LicenceVersion from a resolved version_key."""
        k = key.lower().strip()

        # Get canonical key from registry
        canonical = self._registry.get(k) or k

        # Get URL via version_key -> URL list map
        # Select shortest URL for cleaner display
        url_list = self._vkey_to_url.get(canonical) or self._vkey_to_url.get(k)
        url = min(url_list) if url_list else None

        # Infer name:
        # - For CC licences, use override only if it's different from canonical
        # - For non-CC (GPL, AGPL, OSI, etc.), always return canonical (no stripping)
        override_name = self._name_overrides.get(canonical)
        if canonical.startswith("cc-") or canonical.startswith("cc0"):
            # CC licences: use override if present, otherwise fallback to _infer_name
            name_key = override_name if override_name else self._infer_name(canonical)
        else:
            # Non-CC: use override if present and different, otherwise canonical
            name_key = (
                override_name
                if override_name and override_name != canonical
                else canonical
            )

        # Infer family: use override only if it provides a different value
        override_family = self._family_overrides.get(canonical)
        family_key = (
            override_family
            if override_family and override_family != canonical
            else self._infer_family(canonical)
        )

        family = LicenceFamily(key=family_key)
        name = LicenceName(key=name_key, family=family)
        return LicenceVersion(key=canonical, url=url, licence=name)

    def _make_unknown(self, key: str) -> LicenceVersion:
        """Factory: build an unknown LicenceVersion for unresolved input."""
        family = LicenceFamily(key="unknown")
        name = LicenceName(key=key, family=family)
        return LicenceVersion(key=key, url=None, licence=name)

    def _infer_family(self, key: str) -> str:
        """Fallback family inference - only used if no plugin provides it."""
        k = key.lower()
        if k.startswith("cc0"):
            return "cc0"
        if k.startswith("cc-pdm"):
            return "public-domain"
        if k.startswith("cc-"):
            return "cc"
        if k.startswith(("gpl-", "agpl-", "lgpl-")):
            return "copyleft"
        if k.startswith(("pddl-", "odbl", "odc-")):
            return "data" if k.startswith("pddl-") else "open-data"
        if k.startswith(
            (
                "elsevier-oa",
                "acs-authorchoice",
                "acs-authorchoice-ccby",
                "acs-authorchoice-ccbyncnd",
                "acs-authorchoice-nih",
                "jama-cc-by",
                "thieme-nlm",
                "implied-oa",
                "unspecified-oa",
                "publisher-specific-oa",
                "author-manuscript",
                "oup-chorus",
            )
        ):
            return "publisher-oa"
        if k.startswith(
            (
                "elsevier-tdm",
                "wiley-tdm",
                "springer-tdm",
                "springernature-tdm",
                "iop-tdm",
                "aps-tdm",
            )
        ):
            return "publisher-tdm"
        if k.startswith(
            (
                "elsevier-",
                "wiley-",
                "springer-",
                "springernature-",
                "acs-",
                "rsc-",
                "iop-",
                "bmj-",
                "aaas-",
                "pnas-",
                "aps-",
                "cup-",
                "aip-",
                "jama-",
                "degruyter-",
                "oup-",
                "sage-",
                "tandf-",
                "thieme-",
            )
        ):
            return "publisher-proprietary"

        # "public-domain", "other-oa", and "open-access" are all defined in
        # aliases.json with explicit family_key values.
        # The resolution pipeline checks aliases first (before registry, URL,
        # prose, and fallback).
        # When these keys are encountered, they're resolved via the alias
        # lookup and never reach _infer_family().
        # _infer_family() is only called as a fallback when no plugin provides
        # a family override.
        if k in ("public-domain", "other-oa", "open-access"):
            return "public-domain" if k == "public-domain" else "other-oa"
        return "unknown"

    def _infer_name(self, key: str) -> str:
        """Fallback name inference - only used if no plugin provides it."""
        k = key.lower()
        if k.startswith("cc0"):
            return "cc0"
        if k.startswith("cc-"):
            parts = k.split("-")
            for i, part in enumerate(parts):
                if part.replace(".", "").isdigit():
                    return "-".join(parts[:i])
            return "-".join(parts[:2])
        # For all other licences (GPL, AGPL, OSI, etc.), keep the key as-is
        return k

    @staticmethod
    def _clean(raw: str) -> str:
        s = _WHITESPACE_RE.sub(" ", raw.strip().rstrip("/")).lower()
        return s[:_MAX_INPUT]

    @staticmethod
    def _try_decode_mojibake(s: str) -> str:
        try:
            return s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return s

    @staticmethod
    def _normalise_url(cleaned: str) -> str:
        key = cleaned.lower()
        if key.startswith("http://"):
            key = "https://" + key[7:]
        return key.rstrip("/")
