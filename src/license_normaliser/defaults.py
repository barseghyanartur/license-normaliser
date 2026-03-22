"""Default plugin configuration.

These are the plugin CLASSES (not instances) that form the sane defaults.
Pass them to LicenseNormaliser - they're instantiated lazily.
"""

from __future__ import annotations

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"

__all__ = (
    "DEFAULT_PLUGINS",
    "get_all_refreshable_plugins",
)


def get_all_refreshable_plugins() -> list[type]:
    """Return all plugin classes that support refresh (have url set)."""
    from .parsers.creativecommons import CreativeCommonsParser
    from .parsers.opendefinition import OpenDefinitionParser
    from .parsers.osi import OSIParser
    from .parsers.scancode_licensedb import ScanCodeLicenseDBParser
    from .parsers.spdx import SPDXParser

    return [
        SPDXParser,
        OpenDefinitionParser,
        OSIParser,
        ScanCodeLicenseDBParser,
        CreativeCommonsParser,
    ]


def _load_registry_plugins() -> list[type]:
    from .parsers.creativecommons import CreativeCommonsParser
    from .parsers.opendefinition import OpenDefinitionParser
    from .parsers.osi import OSIParser
    from .parsers.scancode_licensedb import ScanCodeLicenseDBParser
    from .parsers.spdx import SPDXParser

    return [
        SPDXParser,
        OpenDefinitionParser,
        OSIParser,
        ScanCodeLicenseDBParser,
        CreativeCommonsParser,
    ]


def _load_url_plugins() -> list[type]:
    from .parsers.creativecommons import CreativeCommonsParser
    from .parsers.opendefinition import OpenDefinitionParser
    from .parsers.osi import OSIParser
    from .parsers.publisher import PublisherParser
    from .parsers.spdx import SPDXParser

    return [
        SPDXParser,
        OpenDefinitionParser,
        OSIParser,
        CreativeCommonsParser,
        PublisherParser,
    ]


def _load_alias_plugins() -> list[type]:
    from .parsers.alias import AliasParser
    from .parsers.publisher import PublisherParser

    # PublisherParser first, then AliasParser - AliasParser values take precedence
    return [PublisherParser, AliasParser]


def _load_family_plugins() -> list[type]:
    from .parsers.alias import AliasParser

    return [AliasParser]


def _load_name_plugins() -> list[type]:
    from .parsers.alias import AliasParser

    return [AliasParser]


def _load_prose_plugins() -> list[type]:
    from .parsers.prose import ProseParser

    return [ProseParser]


# Lazy-loaded bundle - functions delay imports until actually needed
class _LazyDefaults:
    """Lazy-loading container for default plugins."""

    _registry: list[type] | None = None
    _url: list[type] | None = None
    _alias: list[type] | None = None
    _family: list[type] | None = None
    _name: list[type] | None = None
    _prose: list[type] | None = None

    @property
    def registry(self) -> list[type]:
        if self._registry is None:
            self._registry = _load_registry_plugins()
        return self._registry

    @property
    def url(self) -> list[type]:
        if self._url is None:
            self._url = _load_url_plugins()
        return self._url

    @property
    def alias(self) -> list[type]:
        if self._alias is None:
            self._alias = _load_alias_plugins()
        return self._alias

    @property
    def family(self) -> list[type]:
        if self._family is None:
            self._family = _load_family_plugins()
        return self._family

    @property
    def name(self) -> list[type]:
        if self._name is None:
            self._name = _load_name_plugins()
        return self._name

    @property
    def prose(self) -> list[type]:
        if self._prose is None:
            self._prose = _load_prose_plugins()
        return self._prose


_LAZY = _LazyDefaults()


# Convenience accessors - these trigger lazy loading
def get_default_registry() -> list[type]:
    return _LAZY.registry


def get_default_url() -> list[type]:
    return _LAZY.url


def get_default_alias() -> list[type]:
    return _LAZY.alias


def get_default_family() -> list[type]:
    return _LAZY.family


def get_default_name() -> list[type]:
    return _LAZY.name


def get_default_prose() -> list[type]:
    return _LAZY.prose


# Single bundle for easy passing
DEFAULT_PLUGINS = {
    "registry": get_default_registry(),
    "url": get_default_url(),
    "alias": get_default_alias(),
    "family": get_default_family(),
    "name": get_default_name(),
    "prose": get_default_prose(),
}
