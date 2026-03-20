===================
 Architecture Guide
===================

:Version: 0.2
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

Normalisation happens through a **five-step pipeline** (``_cache.py``)
where the **first step that matches wins**:

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Step
     - Function
     - Logic
   * - 1
     - direct lookup
     - Cleaned string in ``ALIASES`` dict
   * - 2
     - registry lookup
     - Cleaned key in ``REGISTRY`` dict
   * - 3
     - URL map
     - Normalised URL in ``URL_MAP`` dict
   * - 4
     - prose scan
     - Regex pattern from ``PROSE_PATTERNS`` matches (min 20 chars)
   * - 5
     - fallback
     - Always matches -- returns ``"unknown"`` version

Step 1 -- Alias table
---------------------

``ALIASES`` is a merged dict built from three sources:

* ``data/aliases/aliases.json`` -- manually curated aliases with rich metadata
  (version_key, name_key, family_key).
* ``data/publishers/publishers.json`` -- publisher shorthand aliases.
* Built-in CC forms in ``_registry.py``.

Each entry maps a cleaned string to a version key.  Aliases are checked
**before** the registry to ensure canonical forms (e.g. ``"gpl-3.0+"``)
resolve correctly.

Step 2 -- Direct registry lookup
--------------------------------

``REGISTRY`` is built from all registered parsers that set
``is_registry_entry = True`` (the default).  Parsers contribute license
keys from SPDX, OpenDefinition, OSI, ScanCode, and Creative Commons
data sources.

Step 3 -- URL map
-----------------

``URL_MAP`` is a merged dict built from:

* ``data/publishers/publishers.json`` -- publisher-specific URLs.
* SPDX data source -- official reference URLs.
* Open Definition data source -- official reference URLs.
* OSI data source -- HTML reference URLs.
* Creative Commons scraped data -- multilingual deed URLs.

URLs are **normalised once at registry-build time**:

* Scheme forced to ``https``.
* Trailing slash stripped.
* Lowercased.

Step 4 -- Prose pattern scan
----------------------------

``PROSE_PATTERNS`` is a list of compiled ``(Pattern, version_key)``
tuples loaded from ``data/prose/prose_patterns.json`` by the
``ProseParser``.  Patterns are evaluated in order, and the **first
match** wins.  Only inputs of 20 characters or longer are tested
against prose patterns.  Patterns are compiled once at import time.

Step 5 -- Fallback
------------------

Always matches.  Returns the ``"unknown"`` version key with family
``"unknown"``.  When strict mode is disabled this is the final result;
in strict mode a ``LicenseNotFoundError`` is raised instead.


Registry Architecture
=====================

The registry (``_registry.py``) is the canonical source of truth for all
known version keys.  It is built at **import time** by running all
registered parsers.

Parsers
-------

Parsers implement ``BaseParser`` (``parsers/base.py``):

.. code-block:: python

    class BaseParser(ABC):
        url: str | None          # upstream URL for refresh (None for local-only)
        local_path: str           # path to local JSON data
        is_registry_entry: bool = True  # whether parse() contributes to REGISTRY

        def parse(self) -> list[tuple[str, dict[str, Any]]]:
            """Return (license_key, metadata_dict) for every entry."""
            ...

Registered parsers (in ``parsers/__init__.py``):

.. list-table::
   :header-rows: 1

   * - Class
     - Reads
     - Contributes to REGISTRY
     - Purpose
   * - ``SPDXParser``
     - ``data/spdx/spdx.json``
     - Yes
     - SPDX licence list (full, auto-refreshed)
   * - ``OpenDefinitionParser``
     - ``data/opendefinition/opendefinition.json``
     - Yes
     - Open Definition licence list (auto-refreshed)
   * - ``OSIParser``
     - ``data/osi/osi.json``
     - Yes
     - OSI licences (auto-refreshed)
   * - ``ScanCodeLicenseDBParser``
     - ``data/scancode_licensedb/scancode_licensedb.json``
     - Yes
     - ScanCode license DB (auto-refreshed)
   * - ``CreativeCommonsParser``
     - ``data/creativecommons/creativecommons.json``
     - Yes
     - CC licences (scraped fromcreativecommons.org)
   * - ``AliasParser``
     - ``data/aliases/aliases.json``
     - No
     - Curated aliases with rich metadata
   * - ``PublisherParser``
     - ``data/publishers/publishers.json``
     - No
     - Publisher URLs and shorthand aliases
   * - ``ProseParser``
     - ``data/prose/prose_patterns.json``
     - No
     - Curated prose regex patterns

Global lookup tables
--------------------

``REGISTRY: dict[str, str]``
    Version key → version key (all known canonical keys).

``ALIASES: dict[str, str]``
    Cleaned string → version key (all aliases, prose targets, shorthand).

``URL_MAP: dict[str, str]``
    Normalised URL → version key (all known URLs).

``FAMILY_OVERRIDES: dict[str, str]``
    Version key → family key (explicit family from curated data files,
    overrides inference).

Family inference
~~~~~~~~~~~~~~~~

For entries that carry no explicit family, ``_infer_family()`` in
``_registry.py`` classifies them from their key prefix.  This is the
last resort; it does not affect any entry covered by curated data files.

The table covers common prefixes:

``cc0*`` → ``cc0``, ``cc-pdm*`` → ``public-domain``, ``cc*`` → ``cc``,
``gpl*``, ``lgpl*``, ``agpl*`` → ``copyleft``,
``odbl*``, ``odc-*``, ``pddl*`` → ``open-data``,
``elsevier-oa*``, ``acs-authorchoice*``, ``jama-cc-by*``,
``thieme-nlm*``, ``implied-oa*``, ``oup-chorus*`` → ``publisher-oa``,
``elsevier-tdm*``, ``wiley-tdm*``, ``springer*``, ``iop-tdm*``,
``aps-tdm*`` → ``publisher-tdm``,
all other publisher prefixes (``wiley-*``, ``rsc-*``, ``bmj-*``,
``aaas-*``, ``pnas-*``, ``cup-*``, ``aip-*``, ``degruyter-*``,
``tandf-*``, ``sage-*``) → ``publisher-proprietary``,
``public-domain`` → ``public-domain``, ``other-oa``, ``open-access`` →
``other-oa``, everything else → ``osi``.

Factory functions
-----------------

* ``make(version_key)`` -- creates ``LicenseVersion`` from the registry.
* ``make_unknown(raw_key)`` -- creates ``"unknown"`` ``LicenseVersion``.
* ``_infer_name(key)`` -- strips version from CC keys (e.g.
  ``cc-by-4.0`` → ``cc-by``); non-CC keys are unchanged.


Adding a New Parser
===================

1. Create ``src/license_normaliser/parsers/my_parser.py`` implementing
   ``BaseParser``::

       from .base import BaseParser

       class MyParser(BaseParser):
           url = None  # or "https://upstream.example.com/data.json"
           local_path = "data/my_parser/my_data.json"
           is_registry_entry = True  # False for alias-only parsers

           def parse(self) -> list[tuple[str, dict[str, Any]]]:
               # Return [(license_id, {"url": "...", "name": "..."}), ...]
               return []

2. Register it in ``src/license_normaliser/parsers/__init__.py``::

       def get_parsers() -> list[BaseParser]:
           return [
               SPDXParser(),
               OpenDefinitionParser(),
               OSIParser(),
               ScanCodeLicenseDBParser(),
               CreativeCommonsParser(),
               ProseParser(),
               AliasParser(),
               PublisherParser(),
               MyParser(),  # <-- add here
           ]


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

Edit ``data/publishers/publishers.json`` under ``urls``:

.. code-block:: json

    {
      "urls": {
        "https://example.com/license/": {
          "version_key": "my-license",
          "name_key": "my-license",
          "family_key": "osi"
        }
      }
    }

Adding a shorthand alias
------------------------

Edit ``data/publishers/publishers.json`` under ``shorthand_aliases``:

.. code-block:: json

    {
      "shorthand_aliases": {
        "my shorthand alias": "my-license"
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
       "family_key": "osi"}
    ]

Note: prose patterns are only tested against inputs of 20 characters or
longer to avoid false positives on short strings.


Caching
=======

The cache layer (``_cache.py``) sits between the public API and the
pipeline.  It implements one LRU cache:

``_resolve()`` -- pipeline cache
    Key: the fully cleaned input string.  Value: the resulting
    ``LicenseVersion``.  Default size: **8192 entries**.

Input cleaning (``_clean()``)
-----------------------------

Before caching or lookup, every input string passes through:

1. Strip leading/trailing whitespace.
2. Attempt to decode mojibake (try latin-1, fall back to UTF-8).
3. Collapse internal whitespace to single spaces.
4. Lowercase.
5. Strip trailing slash.
6. Cap at 4096 characters.

URL normalisation (``_normalise_url()``)
----------------------------------------

* Scheme forced to ``https``.
* Trailing slash stripped.
* Lowercased.

Strict mode
-----------

* ``strict=False`` (default) -- unknown input returns ``"unknown"``
  ``LicenseVersion``.
* ``strict=True`` -- raises ``LicenseNotFoundError`` with ``raw`` and
  ``cleaned`` attributes.


Directory Structure
===================

::

    src/license_normaliser/
    ├── __init__.py              # Public API exports
    ├── _models.py               # Frozen dataclass hierarchy
    ├── _registry.py             # REGISTRY + URL_MAP + ALIASES + FAMILY_OVERRIDES
    ├── _cache.py                # LRU caches + cleaning + strict mode
    ├── _core.py                 # Internal resolve helpers
    ├── _exceptions.py            # LicenseNormalisationError, LicenseNotFoundError
    ├── cli/
    │   ├── __init__.py
    │   └── _main.py             # CLI entry point
    ├── parsers/
    │   ├── __init__.py          # Parser registry
    │   ├── base.py              # BaseParser abstract class
    │   ├── spdx.py              # SPDXParser
    │   ├── opendefinition.py     # OpenDefinitionParser
    │   ├── osi.py               # OSIParser
    │   ├── scancode_licensedb.py # ScanCodeLicenseDBParser
    │   ├── creativecommons.py    # CreativeCommonsParser
    │   ├── prose.py             # ProseParser
    │   ├── alias.py             # AliasParser
    │   └── publisher.py          # PublisherParser
    └── tests/
        ├── conftest.py
        ├── test_aliases.py
        ├── test_cache.py
        ├── test_cli.py
        ├── test_core.py
        ├── test_exceptions.py
        ├── test_integration.py
        ├── test_models.py
        ├── test_prose.py
        └── test_publisher.py

    data/
    ├── aliases/aliases.json
    ├── urls/url_map.json
    ├── prose/prose_patterns.json
    ├── publishers/publishers.json
    ├── spdx/spdx.json             (full SPDX list — loaded at runtime)
    ├── opendefinition/opendefinition.json  (full OD list — loaded at runtime)
    ├── osi/osi.json               (OSI API response)
    ├── creativecommons/creativecommons.json (scraped CC data)
    ├── scancode_licensedb/scancode_licensedb.json
    └── original/                  **DO NOT MODIFY** — upstream originals


Coding Conventions
==================

* Line length: **88 characters** (ruff).
* Every non-test module: ``__all__``, ``__author__``, ``__copyright__``,
  ``__license__``.
* Always chain exceptions: ``raise X(...) from exc``.
* Type annotations on all public functions.
* Target Python: **3.10+**.

Testing
=======

All tests run inside Docker::

    make test-env ENV=py312      # single Python version
    make test                    # full matrix (py310–py314)

Interactive shell::

    make shell                   # default Python
    make shell-env ENV=py312     # specific Python

Code quality::

    make pre-commit              # runs all hooks (ruff, ...)
