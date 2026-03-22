"""Plugin-based LicenseNormaliser class with configurable constructor injection."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING, Iterable, Sequence

if TYPE_CHECKING:
    from license_normaliser._models import LicenseVersion

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
        from license_normaliser.defaults import DEFAULT_PLUGINS

        # Use all defaults
        ln = LicenseNormaliser(**DEFAULT_PLUGINS)

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

        # Instantiate plugins and load their data
        if registry:
            for plugin_cls in registry:
                data = plugin_cls().load_registry()
                self._registry.update(data)

        if url:
            for plugin_cls in url:
                data = plugin_cls().load_urls()
                self._url_map.update(data)

        # Build inverted URL map: version_key -> cleaned_url (for LicenseVersion.url)
        self._url_to_vkey = {v: k for k, v in self._url_map.items()}

        if alias:
            for plugin_cls in alias:
                data = plugin_cls().load_aliases()
                self._aliases.update(data)

        if family:
            for plugin_cls in family:
                data = plugin_cls().load_families()
                self._family_overrides.update(data)

        if name:
            for plugin_cls in name:
                data = plugin_cls().load_names()
                self._name_overrides.update(data)

        if prose:
            for plugin_cls in prose:
                patterns = plugin_cls().load_prose()
                self._prose_patterns.extend(patterns)

        # Set up cached resolution
        if self._cache:
            resolve_fn = lru_cache(maxsize=self._cache_maxsize)(self._resolve_impl)
            # type: ignore[assignment]
            self._resolve_impl = resolve_fn

    def _resolve_impl(self, cleaned: str) -> LicenseVersion:
        # 1. Alias lookup
        if cleaned in self._aliases:
            return self._make(self._aliases[cleaned])

        # 2. Registry lookup
        if cleaned in self._registry:
            return self._make(cleaned)

        # 3. URL lookup
        url_key = self._normalise_url(cleaned)
        if url_key in self._url_map:
            return self._make(self._url_map[url_key])

        # 4. Prose matching (only for longer strings)
        if len(cleaned) > 20:
            for pattern, vkey in self._prose_patterns:
                if pattern.search(cleaned):
                    return self._make(vkey)

        # 5. Fallback to unknown
        return self._make_unknown(cleaned)

    def normalise_license(self, raw: str, *, strict: bool = False) -> LicenseVersion:
        """Normalise a single license string.

        Args:
            raw: The raw license string, SPDX ID, URL, or prose description.
            strict: If True, raises ``LicenseNotFoundError`` when the input
                cannot be resolved to a known license.

        Returns:
            A ``LicenseVersion`` with the resolved key, license name, and family.

        Raises:
            LicenseNotFoundError: When ``strict=True`` and resolution fails.
        """
        from license_normaliser.exceptions import LicenseNotFoundError

        if not raw or not raw.strip():
            v = self._make_unknown("unknown")
        else:
            v = self._resolve_impl(self._clean(self._try_decode_mojibake(raw)))

        if strict and v.family.key == "unknown":
            raise LicenseNotFoundError(raw, v.key) from None
        return v

    def normalise_licenses(
        self, raws: Iterable[str], *, strict: bool = False
    ) -> list[LicenseVersion]:
        """Batch normalisation.

        When ``strict=True``, raises on the first failure.
        """
        from license_normaliser.exceptions import LicenseNotFoundError

        results: list[LicenseVersion] = []
        for raw in raws:
            v = self.normalise_license(raw, strict=False)
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
            # CC licenses: use override if different, otherwise fallback
            name_key = (
                override_name
                if override_name and override_name != canonical
                else self._infer_name(canonical)
            )
        else:
            # Non-CC: always use canonical (no version stripping)
            name_key = canonical

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
