"""Plugin-based LicenseNormaliser class with configurable constructor injection."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING, Iterable, Sequence

from license_normaliser.defaults import (
    get_default_alias,
    get_default_family,
    get_default_name,
    get_default_prose,
    get_default_registry,
    get_default_url,
)

if TYPE_CHECKING:
    from license_normaliser._models import LicenseVersion
    from license_normaliser._trace import LicenseTrace

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("LicenseNormaliser",)

_WHITESPACE_RE = re.compile(r"\s+")
_MAX_INPUT = 4096


class LicenseNormaliser:
    """Configurable license normalisation with plugin-based data sources.

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

    Example::

        from license_normaliser import LicenseNormaliser

        # Uses all defaults automatically
        ln = LicenseNormaliser()

        # Disable caching for debugging
        ln = LicenseNormaliser(cache=False)

        # Custom plugins
        ln = LicenseNormaliser(
            registry=[SPDXParser],
            alias=[AliasParser, PublisherParser],
        )
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
        self._url_to_vkey: dict[str, str] = {}
        self._aliases: dict[str, str] = {}
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

        # Instantiate plugins and load their data
        for plugin_cls in registry:
            data = plugin_cls().load_registry()
            self._registry.update(data)

        for plugin_cls in url:
            data = plugin_cls().load_urls()
            self._url_map.update(data)

        # Build inverted URL map: version_key -> cleaned_url (for LicenseVersion.url)
        self._url_to_vkey = {v: k for k, v in self._url_map.items()}

        for plugin_cls in alias:
            data = plugin_cls().load_aliases()
            self._aliases.update(data)

        for plugin_cls in family:
            data = plugin_cls().load_families()
            self._family_overrides.update(data)

        for plugin_cls in name:
            data = plugin_cls().load_names()
            self._name_overrides.update(data)

        for plugin_cls in prose:
            patterns = plugin_cls().load_prose()
            self._prose_patterns.extend(patterns)

        # Set up cached resolution
        if self._cache:
            resolve_fn = lru_cache(maxsize=self._cache_maxsize)(self._resolve_impl)
            # type: ignore[assignment]
            self._resolve_impl = resolve_fn

    def _get_trace_mode(self, trace: bool | None) -> bool:
        """Determine if tracing is enabled: explicit > env var > default."""
        from license_normaliser._trace import _should_trace

        if trace is not None:
            return trace
        if self._trace_default is not None:
            return self._trace_default
        return _should_trace()

    def _resolve_with_trace(
        self, raw: str, cleaned: str, strict: bool
    ) -> LicenseVersion:
        """Resolve with full pipeline tracing."""
        from license_normaliser._trace import LicenseTrace, LicenseTraceStage

        stages: list[LicenseTraceStage] = []

        # 1. Alias lookup
        if cleaned in self._aliases:
            stages.append(
                LicenseTraceStage("alias", cleaned, self._aliases[cleaned], True)
            )
            v = self._make(self._aliases[cleaned])
            trace = LicenseTrace(
                raw,
                cleaned,
                stages,
                version_key=v.key,
                name_key=v.license.key,
                family_key=v.family.key,
            )
            return self._make_with_trace(v, trace)

        stages.append(LicenseTraceStage("alias", cleaned, "", False))

        # 2. Registry lookup
        if cleaned in self._registry:
            canonical = self._registry[cleaned]
            stages.append(LicenseTraceStage("registry", cleaned, canonical, True))
            v = self._make(canonical)
            trace = LicenseTrace(
                raw,
                cleaned,
                stages,
                version_key=v.key,
                name_key=v.license.key,
                family_key=v.family.key,
            )
            return self._make_with_trace(v, trace)

        stages.append(LicenseTraceStage("registry", cleaned, "", False))

        # 3. URL lookup
        url_key = self._normalise_url(cleaned)
        if url_key in self._url_map:
            resolved = self._url_map[url_key]
            stages.append(LicenseTraceStage("url", url_key, resolved, True))
            v = self._make(resolved)
            trace = LicenseTrace(
                raw,
                cleaned,
                stages,
                version_key=v.key,
                name_key=v.license.key,
                family_key=v.family.key,
            )
            return self._make_with_trace(v, trace)

        stages.append(LicenseTraceStage("url", cleaned, "", False))

        # 4. Prose matching (only for longer strings)
        if len(cleaned) >= 20:
            for pattern, vkey in self._prose_patterns:
                if pattern.search(cleaned):
                    stages.append(LicenseTraceStage("prose", cleaned, vkey, True))
                    v = self._make(vkey)
                    trace = LicenseTrace(
                        raw,
                        cleaned,
                        stages,
                        version_key=v.key,
                        name_key=v.license.key,
                        family_key=v.family.key,
                    )
                    return self._make_with_trace(v, trace)

        stages.append(LicenseTraceStage("prose", cleaned, "", False))

        # 5. Fallback to unknown
        stages.append(LicenseTraceStage("fallback", cleaned, cleaned, True))
        v = self._make_unknown(cleaned)
        trace = LicenseTrace(
            raw,
            cleaned,
            stages,
            version_key=v.key,
            name_key=v.license.key,
            family_key=v.family.key,
        )
        return self._make_with_trace(v, trace)

    def _make_with_trace(
        self, v: LicenseVersion, trace: LicenseTrace
    ) -> LicenseVersion:
        """Create a LicenseVersion with trace attached."""

        # Reconstruct with trace using object.__setattr__ (frozen dataclass)
        object.__setattr__(v, "_trace", trace)
        return v

    def _resolve_impl(self, cleaned: str) -> LicenseVersion:
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

    def normalise_license(
        self, raw: str, *, strict: bool = False, trace: bool | None = None
    ) -> LicenseVersion:
        """Normalise a single license string.

        Args:
            raw: The raw license string, SPDX ID, URL, or prose description.
            strict: If True, raises ``LicenseNotFoundError`` when the input
                cannot be resolved to a known license.
            trace: If True, include resolution trace. If None, uses
                ENABLE_LICENSE_NORMALISER_TRACE env var or class default.

        Returns:
            A ``LicenseVersion`` with the resolved key, license name, and family.

        Raises:
            LicenseNotFoundError: When ``strict=True`` and resolution fails.
        """
        from license_normaliser.exceptions import LicenseNotFoundError

        do_trace = self._get_trace_mode(trace)

        if not raw or not raw.strip():
            cleaned = "unknown"
            v = self._make_unknown(cleaned)
            if do_trace:
                from license_normaliser._trace import LicenseTrace, LicenseTraceStage

                stages = [LicenseTraceStage("fallback", cleaned, cleaned, True)]
                trace_obj = LicenseTrace(
                    raw,
                    cleaned,
                    stages,
                    version_key=v.key,
                    name_key=v.license.key,
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
            raise LicenseNotFoundError(raw, v.key) from None
        return v

    def normalise_licenses(
        self, raws: Iterable[str], *, strict: bool = False, trace: bool | None = None
    ) -> list[LicenseVersion]:
        """Batch normalisation.

        When ``strict=True``, raises on the first failure.
        """
        from license_normaliser.exceptions import LicenseNotFoundError

        results: list[LicenseVersion] = []
        for raw in raws:
            v = self.normalise_license(raw, strict=False, trace=trace)
            if strict and v.family.key == "unknown":
                raise LicenseNotFoundError(raw, v.key) from None
            results.append(v)
        return results

    def registry_keys(self) -> set[str]:
        """Return the set of all known registry keys."""
        return set(self._registry.keys())

    def _make(self, key: str) -> LicenseVersion:
        """Factory: build a LicenseVersion from a resolved version_key."""
        from license_normaliser._models import (
            LicenseFamily,
            LicenseName,
            LicenseVersion,
        )

        k = key.lower().strip()

        # Get canonical key from registry
        canonical = self._registry.get(k) or k

        # Get URL via inverted map: version_key -> cleaned_url
        url = self._url_to_vkey.get(canonical) or self._url_to_vkey.get(k)

        # Infer name:
        # - For CC licenses, use override only if it's different from canonical
        # - For non-CC (GPL, AGPL, OSI, etc.), always return canonical (no stripping)
        override_name = self._name_overrides.get(canonical)
        if canonical.startswith("cc-") or canonical.startswith("cc0"):
            # CC licenses: use override if present, otherwise fallback to _infer_name
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

        family = LicenseFamily(key=family_key)
        name = LicenseName(key=name_key, family=family)
        return LicenseVersion(key=canonical, url=url, license=name)

    def _make_unknown(self, key: str) -> LicenseVersion:
        """Factory: build an unknown LicenseVersion for unresolved input."""
        from license_normaliser._models import (
            LicenseFamily,
            LicenseName,
            LicenseVersion,
        )

        family = LicenseFamily(key="unknown")
        name = LicenseName(key=key, family=family)
        return LicenseVersion(key=key, url=None, license=name)

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
        if k.startswith(("odbl-", "pddl-", "odc-")):
            return "data"
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
        # For all other licenses (GPL, AGPL, OSI, etc.), keep the key as-is
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
