===================
 Architecture Guide
===================

:Version: 0.3
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

Normalisation happens through a **five-step pipeline** (``_normaliser.py``)
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


Plugin Architecture
===================

The normalisation logic lives in ``LicenseNormaliser`` (``_normaliser.py``),
which is configured with plugin CLASSES (not instances).  Plugins are
instantiated lazily when their data is first accessed.

Plugin Interfaces
-----------------

Six plugin types are supported (defined in ``plugins.py``):

.. list-table::
   :header-rows: 1

   * - Interface
     - Method
     - Returns
   * - ``BasePlugin``
     - ``refresh(force)``
     - Fetches fresh data from upstream URL
   * - ``RegistryPlugin``
     - ``load_registry()``
     - ``dict[str, str]``: key → canonical_key
   * - ``URLPlugin``
     - ``load_urls()``
     - ``dict[str, str]``: cleaned_url → version_key
   * - ``AliasPlugin``
     - ``load_aliases()``
     - ``dict[str, str]``: alias_string → version_key
   * - ``FamilyPlugin``
     - ``load_families()``
     - ``dict[str, str]``: version_key → family_key
   * - ``NamePlugin``
     - ``load_names()``
     - ``dict[str, str]``: version_key → name_key
   * - ``ProsePlugin``
     - ``load_prose()``
     - ``list[tuple[Pattern, str]]``: compiled patterns → version_key

Parser Classes
--------------

Each parser class inherits from ``BasePlugin`` plus one or more plugin
interfaces.  Parsers contribute data to ``LicenseNormaliser``:

.. list-table::
   :header-rows: 1

   * - Class
     - Plugins
     - Data Source
   * - ``SPDXParser``
     - Registry + URL + BasePlugin
     - ``data/spdx/spdx.json`` (auto-refreshed)
   * - ``OpenDefinitionParser``
     - Registry + URL + BasePlugin
     - ``data/opendefinition/opendefinition.json`` (auto-refreshed)
   * - ``OSIParser``
     - Registry + URL + BasePlugin
     - ``data/osi/osi.json`` (auto-refreshed)
   * - ``ScanCodeLicenseDBParser``
     - Registry + BasePlugin
     - ``data/scancode_licensedb/scancode_licensedb.json`` (auto-refreshed)
   * - ``CreativeCommonsParser``
     - Registry + URL + BasePlugin
     - ``data/creativecommons/creativecommons.json`` (scraped)
   * - ``AliasParser``
     - Alias + Family + Name + BasePlugin
     - ``data/aliases/aliases.json`` (local-only)
   * - ``PublisherParser``
     - Alias + URL + BasePlugin
     - ``data/publishers/publishers.json`` (local-only)
   * - ``ProseParser``
     - Prose + BasePlugin
     - ``data/prose/prose_patterns.json`` (local-only)

Default Plugins
---------------

The default plugin bundle is defined in ``defaults.py`` using lazy loading
(``_LazyDefaults`` class) to avoid circular imports.  Use the helper
functions to get plugin CLASSES:

* ``get_default_registry()``
* ``get_default_url()``
* ``get_default_alias()``
* ``get_default_family()``
* ``get_default_name()``
* ``get_default_prose()``

Or get all refreshable plugins for the CLI via
``get_all_refreshable_plugins()``.

Family inference
~~~~~~~~~~~~~~~~~

For entries that carry no explicit family, ``_infer_family()`` in
``_normaliser.py`` classifies them from their key prefix.  This is the
last resort; it does not affect any entry covered by plugin data.

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
``other-oa``, everything else → ``unknown``.

Factory Methods
---------------

``LicenseNormaliser`` provides these factory methods:

* ``_make(version_key)`` -- creates ``LicenseVersion`` from resolved key.
* ``_make_unknown(raw_key)`` -- creates ``"unknown"`` ``LicenseVersion``.
* ``_infer_name(key)`` -- for CC keys returns name without version (e.g.
  ``cc-by-4.0`` → ``cc-by``); non-CC keys are unchanged.


Adding a New Parser
===================

1. Create ``src/license_normaliser/parsers/my_parser.py`` implementing
   plugin interfaces:

   .. pytestfixture: Any

   .. code-block:: python
       :name: test_adding_new_parser

       from license_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

       class MyParser(BasePlugin, RegistryPlugin, URLPlugin):
           url = None  # or "https://upstream.example.com/data.json"
           local_path = "data/my_parser/my_data.json"

           def load_registry(self) -> dict[str, str]:
               # Return {"license_key": "canonical_key", ...}
               return {}

           def load_urls(self) -> dict[str, str]:
               # Return {"https://...": "version_key", ...}
               return {}

2. Register it in ``src/license_normaliser/defaults.py``:

   .. continue: test_adding_new_parser

   .. code-block:: python
      :name: test_adding_new_parser_register

      from license_normaliser.parsers.spdx import SPDXParser

      def _load_registry_plugins() -> list[type]:
          # ... other imports
          return [
              SPDXParser,
              # ... other plugins
              MyParser,
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

The ``LicenseNormaliser`` class accepts ``cache`` and ``cache_maxsize``
parameters.  When enabled (default), the resolution method is wrapped with
LRU caching.  Default size: **8192 entries**.

The module-level API (``_cache.py``) delegates to ``LicenseNormaliser``
with default plugins, providing a transparent caching layer.

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
    ├── _normaliser.py           # LicenseNormaliser class with plugin-based resolution
    ├── _cache.py                # Module-level API delegating to LicenseNormaliser
    ├── _core.py                 # Internal resolve helpers (deprecated, kept for compat)
    ├── plugins.py               # Plugin interfaces (BasePlugin, RegistryPlugin, etc.)
    ├── defaults.py              # Lazy-loading default plugin bundle
    ├── _exceptions.py           # LicenseNormalisationError, LicenseNotFoundError
    ├── cli/
    │   ├── __init__.py
    │   └── _main.py             # CLI entry point
    ├── parsers/
    │   ├── __init__.py          # Empty, for ruff
    │   ├── spdx.py              # SPDXParser
    │   ├── opendefinition.py    # OpenDefinitionParser
    │   ├── osi.py               # OSIParser
    │   ├── scancode_licensedb.py # ScanCodeLicenseDBParser
    │   ├── creativecommons.py   # CreativeCommonsParser
    │   ├── prose.py             # ProseParser
    │   ├── alias.py             # AliasParser
    │   └── publisher.py         # PublisherParser
    └── tests/
        ├── conftest.py
        ├── test_aliases.py
        ├── test_cli.py
        ├── test_core.py
        ├── test_exceptions.py
        ├── test_integration.py
        ├── test_models.py
        ├── test_prose.py
        └── test_publisher.py

    data/
    ├── aliases/aliases.json
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

.. note::
   Python 3.15 is being tested on GitHub CI, but not inside a local Docker image.

Docker-based testing (recommended)
-----------------------------------

All tests run inside Docker for platform independence and consistency::

    make test                    # full matrix (Python 3.10-3.14)
    make test-env ENV=py312      # single Python version
    make shell                   # interactive shell in test container
    make shell-env ENV=py312     # interactive shell for specific Python

Local testing (alternative)
---------------------------

For faster iteration during development, you can run tests locally
with ``uv``::

    make install                 # one-time setup
    uv run pytest                # run all tests
    uv run pytest path/to/test_something.py  # run specific test

**Important**: If you encounter tooling errors with local testing, fall back to
Docker-based testing which is the canonical environment.

Code quality
------------

Run all linting and formatting checks::

    make pre-commit              # runs all hooks (ruff, doc8, detect-secrets, etc.)
