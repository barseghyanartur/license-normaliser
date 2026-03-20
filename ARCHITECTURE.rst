====================
 Architecture Guide
====================

:Version: 0.2.0
:Author: Artur Barseghyan <artur.barseghyan@gmail.com>
:Repository: https://github.com/barseghyanartur/license-normaliser

.. contents::
   :local:

Overview
========

``license-normaliser`` is a Python package that resolves any licence
representation -- SPDX tokens, URLs, or free-form prose -- to a single
canonical three-level hierarchy.  The package has **zero runtime
dependencies** and is extensible through data files without touching
Python code.

Design Goals
------------

1. **Three-level hierarchy** -- every licence maps to exactly one
   ``(family, name, version)`` triple.
2. **No external dependencies** -- only optional development tooling is
   allowed as a runtime constraint.
3. **Data-file extensibility** -- new synonyms are added by editing JSON,
   not Python.
4. **LRU caching** -- the normalisation pipeline is cached so repeated
   lookups are near-instant.
5. **Strict mode** -- callers can opt into raising on unknown input
   instead of falling back to ``"unknown"``.


Three-Level Hierarchy
=====================

The core data model lives in ``_models.py`` and is built on frozen
dataclasses.  Every licence resolved by the library is represented by
three objects that form a chain.

.. list-table::
   :header-rows: 1
   :widths: 20 25 55

   * - Level
     - Class
     - Example
   * - Family
     - ``LicenseFamily``
     - ``"cc"``, ``"osi"``, ``"copyleft"``, ``"publisher-tdm"``
   * - Name
     - ``LicenseName``
     - ``"cc-by"``, ``"mit"``, ``"wiley-tdm"``
   * - Version
     - ``LicenseVersion``
     - ``"cc-by-4.0"``, ``"mit"``, ``"wiley-tdm-1.1"``

Class relationships
-------------------

- ``LicenseVersion`` holds a ``LicenseName`` via its ``license`` attribute.
- ``LicenseName`` holds a ``LicenseFamily`` via its ``family`` attribute.
- ``LicenseVersion.family`` delegates to ``license.family``.
- All three classes are **immutable** (frozen dataclasses), implement
  ``__str__``, ``__eq__``, and ``__hash__``.

Resolution Pipeline
===================

Normalisation happens through a **six-step pipeline** (``_pipeline.py``)
where the **first step that matches wins**:

.. list-table::
   :header-rows: 1
   :widths: 15 20 65

   * - Step
     - Function
     - Logic
   * - 1
     - ``step_direct``
     - Direct key in ``VERSION_REGISTRY``
   * - 2
     - ``step_alias``
     - Cleaned string in ``ALIASES`` dict
   * - 3
     - ``step_url``
     - Normalised URL in ``URL_MAP`` dict
   * - 4
     - ``step_cc_regex``
     - Creative Commons URL parsed by structural regex
   * - 5
     - ``step_prose``
     - Regex pattern from ``PROSE_PATTERNS`` matches (min 20 chars)
   * - 6
     - ``step_fallback``
     - Always matches -- returns ``"unknown"`` version

Step 1 -- Direct registry lookup
--------------------------------

The ``VERSION_REGISTRY`` is a dict mapping every known version key to a
metadata dict.  Example::

    "mit" → {"url": "https://opensource.org/licenses/MIT",
              "name_key": "mit", "family_key": "osi"}

It is built at import time from all registered data sources (see
Registry Architecture below).

Step 2 -- Alias table
---------------------

``ALIASES`` is a merged dict built from:

* ``data/aliases/aliases.json`` -- manually curated entries.
* SPDX data source -- maps lowercase SPDX IDs to their canonical key.
* Open Definition data source -- maps lowercase Open Definition IDs
  to their canonical key.

Each entry maps a cleaned string to a version key.

Step 3 -- URL map
-----------------

``URL_MAP`` is a merged dict built from:

* ``data/urls/url_map.json`` -- manually curated URL entries.
* SPDX data source -- official reference URLs.
* Open Definition data source -- official reference URLs.

URLs are **normalised once at registry-build time**:

* Scheme forced to ``https``.
* Trailing slash stripped.
* Lowercased.

Step 4 -- Creative Commons structural parser
--------------------------------------------
not already in the URL map.  It uses regex to extract the licence type
and version from the URL path, then constructs the version key and
canonical URL.  Supports standard licences, IGO variants, and the
public-domain mark.

Step 5 -- Prose pattern scan
----------------------------

``PROSE_PATTERNS`` is a list of compiled ``(Pattern, version_key)``
tuples.  Patterns are evaluated in order, and the **first match** wins.
Only inputs of 20 characters or longer are tested against prose
patterns.  Patterns are compiled once at import time.

Step 6 -- Fallback
------------------

Always matches.  Returns the ``"unknown"`` version key with family
``"unknown"``.  When strict mode is disabled this is the final result;
in strict mode a ``LicenseNotFoundError`` is raised instead.


Registry Architecture
=====================

The registry (``_registry.py``) is the canonical source of truth for all
known version keys.  It is built in two passes at **import time**:

Phase 1 -- Collect keys
-----------------------

Every registered data source contributes aliases, URL entries, and prose
patterns.  The complete set of known version keys is assembled from all
contributions.  Any key that cannot be resolved to metadata is logged
at DEBUG level and retained so it can be used as a direct lookup target.

Phase 2 -- Merge metadata
-------------------------

The three lookup tables are assembled from multiple data sources:

``VERSION_REGISTRY: dict[str, dict[str, str]]``
    Version key → ``{"url": str, "name_key": str, "family_key": str}``.
    ``url`` is the canonical URL (may be empty when no URL is known).

``ALIASES: dict[str, str]``
    Cleaned string → version key.

``URL_MAP: dict[str, str]``
    Normalised URL → version key.

``PROSE_PATTERNS: list[tuple[re.Pattern[str], str]]``
    Compiled regex → version key.

Family inference
~~~~~~~~~~~~~~~~

For entries that carry no explicit family (e.g. SPDX-only licenses),
family is inferred from a small regex table in ``_registry.py``.  This
is the last resort; it does not affect any entry covered by the curated
JSON files.  The table covers common prefixes:

``cc0`` → ``cc0``, ``cc-pdm`` → ``public-domain``, ``cc*`` → ``cc``,
``gpl*`` → ``copyleft``, ``lgpl*`` → ``copyleft``,
``agpl*`` → ``copyleft``, ``mpl*`` → ``osi``, ``bsd*`` → ``osi``,
``mit`` → ``osi``, ``apache`` → ``osi``, ``odbl`` → ``open-data``,
``odc-by`` → ``open-data``, ``pddl`` → ``open-data``, ``fal*`` →
``other-oa``, ``elsevier*`` → ``publisher-oa``,
``wiley*`` → ``publisher-proprietary``, ``springer*`` → ``publisher-tdm``,
``springernature*`` → ``publisher-tdm``, ``acs*`` → ``publisher-oa``,
``rsc*`` → ``publisher-proprietary``, ``iop*`` → ``publisher-tdm``,
``bmj*`` → ``publisher-proprietary``, ``cup*`` → ``publisher-proprietary``,
``aip*``, ``pnas*`` → ``publisher-proprietary``,
``aps*`` → ``publisher-proprietary``, ``jama*`` → ``publisher-oa``,
``degruyter*`` → ``publisher-proprietary``, ``thieme*`` → ``publisher-oa``,
``tandf*`` → ``publisher-proprietary``, ``oup*`` → ``publisher-oa``,
``sage*`` → ``publisher-proprietary``,
``aaas*`` → ``publisher-proprietary``,
``no-reuse`` → ``publisher-proprietary``,
``all-rights-reserved`` → ``publisher-proprietary``,
``author-manuscript`` → ``publisher-oa``,
``implied-oa`` → ``publisher-oa``,
``open-access`` → ``other-oa``, ``unspecified-oa`` → ``other-oa``,
``publisher-specific-oa`` → ``publisher-oa``,
``other-oa`` → ``other-oa``.

Factory functions
-----------------

* ``make(version_key)`` -- creates ``LicenseVersion`` from the registry.
* ``make_unknown(raw_key)`` -- creates ``"unknown"`` ``LicenseVersion``.
* ``make_synthetic(version_key, url, name_key)`` -- creates a version
  from the CC URL parser output.


Data Source Plugin System
=========================

Data sources are implemented as classes that satisfy the ``DataSource``
Protocol (``data_sources/__init__.py``).

Protocol definition
-------------------

.. code-block:: python

    class DataSource(Protocol):
        name: str
        def load(self, data_dir: Path) -> SourceContribution: ...

    @dataclass(slots=True)
    class SourceContribution:
        name: str
        aliases: dict[str, str]
        url_map: dict[str, str]
        prose: dict[str, str]
        metadata: dict[str, VersionMetadata]

``VersionMetadata`` is ``dict[str, str]`` mapping fields
``name_key``, ``family_key``, and ``url`` to their values.
The ``metadata`` dict holds per-version-key metadata; empty strings
mean "no value provided" and are filled in by later sources.

Loading
-------

``load_all_sources(data_dir)`` iterates ``REGISTERED_SOURCES``, imports
each module, instantiates the class, and calls ``load()``.  Errors from
individual sources are caught and logged; other sources continue
normally.  The only exception that propagates is ``DataSourceError``
(which signals a critical parse failure).

Registered sources
------------------

The sources are processed in order; **later sources override earlier
ones** on key conflicts.

.. list-table::
   :header-rows: 1

   * - Class
     - Reads
     - Purpose
   * - ``BuiltinAliasSource``
     - ``data/aliases/aliases.json``
     - Curated alias map
   * - ``BuiltinUrlSource``
     - ``data/urls/url_map.json``
     - Curated URL map
   * - ``BuiltinProseSource``
     - ``data/prose/prose_patterns.json``
     - Curated prose regex patterns
   * - ``SpdxSource``
     - ``data/spdx/spdx-licenses.json``
     - SPDX licence list (auto-parsed)
   * - ``OpenDefinitionSource``
     - ``data/opendefinition/opendefinition_licenses_all.json``
     - Open Definition licence list (auto-parsed)

Adding a new data source
------------------------

1. Create ``src/license_normaliser/data_sources/my_source.py``::

       from . import DataSource, SourceContribution
       from pathlib import Path

       class MySource:
           name = "my-source"

           def load(self, data_dir: Path) -> SourceContribution:
               # Read data_dir / "my_subdir" / "my_file.json"
               return SourceContribution(
                   name=self.name,
                   aliases={"some alias": "mit"},
                   url_map={},
                   prose={},
               )

2. Register it in ``REGISTERED_SOURCES`` in
   ``data_sources/__init__.py``.


Caching
=======

The cache layer (``_cache.py``) sits between the public API and the
pipeline.  It implements two LRU caches:

``_resolve()`` -- pipeline cache
    Key: the fully cleaned input string.  Value: the resulting
    ``LicenseVersion``.  Default size: **8192 entries**.

``_get_license_name()`` -- model cache
    Key: name key string.  Value: the ``LicenseName`` instance.
    Default size: **512 entries**.

Input cleaning (``_clean()``)
-----------------------------

Before caching or lookup, every input string passes through:

1. Strip leading/trailing whitespace.
2. Attempt to decode mojibake (try latin-1, fall back to UTF-8).
3. Collapse internal whitespace to single spaces.
4. Lowercase.
5. Strip trailing slash.
6. Cap at 4096 characters.

Strict mode
-----------

* ``strict=False`` (default) -- unknown input returns ``"unknown"``
  ``LicenseVersion``.
* ``strict=True`` -- raises ``LicenseNotFoundError`` with ``raw`` and
  ``cleaned`` attributes.


Public API
==========

``__init__.py`` exports the public surface:

.. code-block:: python

    from license_normaliser import (
        normalise_license,      # single input
        normalise_licenses,      # batched iterable
        LicenseFamily,
        LicenseName,
        LicenseVersion,
    )
    from license_normaliser.exceptions import (
        LicenseNotFoundError,
        DataSourceError,
    )

Usage examples
--------------

Simple::

    from license_normaliser import normalise_license

    result = normalise_license("MIT")
    str(result)          # "mit"
    result.key           # "mit"
    result.url           # "https://opensource.org/licenses/MIT"
    result.license.key   # "mit"
    result.family.key    # "osi"

Full hierarchy::

    v = normalise_license("CC BY-NC-ND 4.0")
    v.key           # "cc-by-nc-nd-4.0"
    v.license.key   # "cc-by-nc-nd"
    v.family.key    # "cc"

Strict mode::

    from license_normaliser import normalise_license
    from license_normaliser.exceptions import LicenseNotFoundError

    try:
        v = normalise_license("unknown string", strict=True)
    except LicenseNotFoundError as exc:
        exc.raw      # original input
        exc.cleaned  # cleaned form

CLI
---

::

    license-normaliser normalise "MIT"
    license-normaliser normalise --full "CC BY 4.0"
    license-normaliser normalise --strict "unknown"
    license-normaliser batch MIT "Apache-2.0" "CC BY 4.0"


Extending Without Python Changes
================================

Adding a new alias
------------------

Edit ``data/aliases/aliases.json``.  Each entry maps an alias string to
a dict with ``version_key``, ``name_key``, and ``family_key``:

.. code-block:: json

    {
      "my new alias": {
        "version_key": "existing-version-key",
        "name_key": "existing-name",
        "family_key": "cc"
      }
    }

Adding a new URL
----------------

Edit ``data/urls/url_map.json``:

.. code-block:: json

    {
      "https://example.com/license/": {
        "version_key": "existing-version-key",
        "name_key": "existing-name",
        "family_key": "osi"
      }
    }

Adding a prose pattern
----------------------

Edit ``data/prose/prose_patterns.json`` (order matters -- specific
patterns before general ones):

.. code-block:: json

    [
      {"pattern": "my specific phrase",
       "version_key": "existing-version-key",
       "name_key": "existing-name",
       "family_key": "osi"},
      ...
    ]

Note: prose patterns are only tested against inputs of 20 characters or
longer to avoid false positives on short strings.


Adding a Brand-New Licence
==========================

1. Add entries to the JSON data files.  Each entry is a dict with
   ``version_key``, ``name_key``, and ``family_key``::

   ``data/aliases/aliases.json``:

   .. code-block:: json

       { "my alias":
         {"version_key": "my-license",
          "name_key": "my-license",
          "family_key": "osi"} }

   ``data/urls/url_map.json``:

   .. code-block:: json

        { "https://example.com/license/":
          {"version_key": "my-license",
           "name_key": "my-license",
           "family_key": "osi"} }

   ``data/prose/prose_patterns.json``:

   .. code-block:: json

        [
          {"pattern": "my specific phrase",
           "version_key": "my-license",
           "name_key": "my-license",
           "family_key": "osi"}
       ]

   At least one of these files must provide an entry for the new key.

2. If the new licence has family information not covered by the regex
   fallback table in ``_registry.py``, add an explicit entry to
   ``data/aliases/aliases.json`` to ensure it is picked up.

3. Write tests covering both the new licence and any edge cases.

4. Run the test suite::

       make test-env ENV=py312
       make pre-commit


Directory Structure
===================

::

    src/license_normaliser/
    ├── __init__.py              # Public API exports
    ├── _models.py                # Frozen dataclass hierarchy
    ├── _registry.py              # VERSION_REGISTRY + data source merge
    ├── _pipeline.py              # Six-step resolution pipeline
    ├── _cache.py                 # LRU caches + cleaning + strict mode
    ├── _core.py                  # Internal resolve helpers
    ├── exceptions.py             # LicenseNotFoundError, DataSourceError
    ├── cli/
    │   ├── __init__.py
    │   └── _main.py              # CLI entry point
    ├── data_sources/
    │   ├── __init__.py           # DataSource protocol + REGISTRY
    │   ├── builtin_aliases.py    # aliases.json loader
    │   ├── builtin_urls.py       # url_map.json loader
    │   ├── builtin_prose.py      # prose_patterns.json loader
    │   ├── spdx.py               # SPDX JSON parser
    │   └── opendefinition.py     # Open Definition JSON parser
    └── tests/
        ├── conftest.py           # pytest fixtures
        ├── test_cache.py
        ├── test_cli.py
        ├── test_core.py
        ├── test_data_sources.py
        ├── test_exceptions.py
        ├── test_models.py
        ├── test_pipeline.py
        └── test_registry.py

    data/
    ├── aliases/aliases.json
    ├── urls/url_map.json
    ├── prose/prose_patterns.json
    ├── spdx/spdx-licenses.json       (auto-parsed)
    └── opendefinition/...json        (auto-parsed)


Exception Hierarchy
===================

::

    LicenseNormaliserError (base)
    ├── LicenseNotFoundError     # strict-mode failure
    └── DataSourceError          # critical data source parse failure

Only ``DataSourceError`` propagates from ``load_all_sources()``.
All other exceptions are caught, logged, and the system continues.


Testing
=======

All tests run inside Docker::

    make test-env ENV=py312     # single Python version
    make test                    # full matrix (py310–py314)

Interactive shell::

    make shell                   # default Python
    make shell-env ENV=py312     # specific Python

Code quality::

    make pre-commit              # runs all hooks (ruff, pydoclint, ...)


Coding Conventions
==================

* Line length: **88 characters** (ruff).
* Every non-test module: ``__all__``, ``__author__``, ``__copyright__``,
  ``__license__``.
* Always chain exceptions: ``raise X(...) from exc``.
* Type annotations on all public functions.
* Target Python: **3.10+**.
