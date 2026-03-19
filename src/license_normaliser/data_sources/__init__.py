"""license_normaliser.data_sources - pluggable data-source architecture.

Each data source is a Python module in this package that implements the
:class:`DataSource` protocol.  At startup the loader collects contributions
from every registered source and merges them into the unified registry.

Adding a new source
-------------------
1. Create ``data_sources/my_source.py`` implementing :class:`DataSource`.
2. Register it in :data:`REGISTERED_SOURCES` (bottom of this file).

That is all - no other file needs to change.

Data directory layout
---------------------
Data files live under the top-level ``data/`` directory of the installed
package.  Each source can declare its own sub-directory.  The loader passes
the resolved ``data_dir`` path to each source so sources never hard-code
absolute paths.

Source contract
---------------
A source must provide three dicts (all values must be canonical version keys
that exist in ``VERSION_REGISTRY``):

* ``aliases``  - ``{cleaned_string -> version_key}``
* ``url_map``  - ``{normalised_url    -> version_key}``
* ``prose``    - ``{pattern_string    -> version_key}``  (regex patterns)

Sources that only contribute to a subset of the three dicts may return empty
dicts for the others.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..exceptions import DataSourceError

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = (
    "DataSource",
    "SourceContribution",
    "load_all_sources",
    "REGISTERED_SOURCES",
)

logger = logging.getLogger(__name__)


class SourceContribution:
    """Collected contributions from one data source."""

    __slots__ = ("name", "aliases", "url_map", "prose")

    def __init__(
        self,
        name: str,
        aliases: dict[str, str],
        url_map: dict[str, str],
        prose: dict[str, str],
    ) -> None:
        self.name = name
        self.aliases = aliases
        self.url_map = url_map
        self.prose = prose


@runtime_checkable
class DataSource(Protocol):
    """Protocol every data source must satisfy."""

    #: Human-readable name shown in error messages and debug logs.
    name: str

    def load(self, data_dir: Path) -> SourceContribution:
        """Load and return contributions from *data_dir*.

        Parameters
        ----------
        data_dir: Path
            Absolute path to the package-level ``data/`` directory.
            Sources should read from ``data_dir / <source_subdir>``.

        Returns
        -------
        SourceContribution
            All aliases, URL entries, and prose patterns contributed by
            this source.  Empty dicts are fine for unused categories.
        """
        ...


# ---------------------------------------------------------------------------
# Registered sources - edit this list to add / remove sources
# ---------------------------------------------------------------------------

#: Ordered list of ``(module_path, class_name)`` pairs.
#: Sources are merged in order; later sources override earlier ones on conflict.
REGISTERED_SOURCES: list[tuple[str, str]] = [
    ("license_normaliser.data_sources.builtin_aliases", "BuiltinAliasSource"),
    ("license_normaliser.data_sources.builtin_urls", "BuiltinUrlSource"),
    ("license_normaliser.data_sources.builtin_prose", "BuiltinProseSource"),
    ("license_normaliser.data_sources.spdx", "SpdxSource"),
    ("license_normaliser.data_sources.opendefinition", "OpenDefinitionSource"),
]


def load_all_sources(data_dir: Path) -> list[SourceContribution]:
    """Instantiate and load every registered data source.

    Errors from individual sources are caught and logged; they do not prevent
    other sources from loading.

    Parameters
    ----------
    data_dir: Path
        Absolute path to the package-level ``data/`` directory.

    Returns
    -------
    list[SourceContribution]
        One entry per successfully loaded source, in registration order.
    """
    contributions: list[SourceContribution] = []
    for module_path, class_name in REGISTERED_SOURCES:
        try:
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            source: DataSource = cls()
            contribution = source.load(data_dir)
            contributions.append(contribution)
            logger.debug(
                "Loaded data source %r: %d aliases, %d URLs, %d prose patterns",
                source.name,
                len(contribution.aliases),
                len(contribution.url_map),
                len(contribution.prose),
            )
        except DataSourceError as exc:  # noqa: PERF203
            logger.warning("Data source %r failed to load: %s", module_path, exc)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Unexpected error loading data source %r: %s", module_path, exc
            )
    return contributions
