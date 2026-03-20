Data Directory
==============

This directory contains all normalisation data files loaded at runtime
by ``license-normaliser``. You can extend or override entries without
touching any Python code.

Structure
---------

::

   data/
   ├── aliases/
   │   └── aliases.json              # Prose/SPDX/short-form → metadata dict
   ├── urls/
   │   └── url_map.json              # Canonical URL → metadata dict
   ├── prose/
   │   └── prose_patterns.json        # Ordered regex patterns for long text scanning
   ├── spdx/
   │   └── spdx-licenses.json        # SPDX license list (optional)
   └── opendefinition/
       └── opendefinition_licenses_all.json   # OD license list (optional)

Entry Format
------------

Every entry maps a **lookup key** (alias string, URL, or prose pattern)
to a metadata dict with three required fields:

- ``version_key`` – the canonical version-level identifier
  (e.g. ``"cc-by-4.0"``)
- ``name_key`` – the name-level identifier without version suffix
  (e.g. ``"cc-by"``)
- ``family_key`` – the family-level identifier (e.g. ``"cc"``)

URLs are stored separately in the ``url`` field of the metadata dict.

How to Add a New License Alias
------------------------------

Edit ``aliases/aliases.json``:

.. code:: json

   {
     "my new alias": {
       "version_key": "cc-by-4.0",
       "name_key": "cc-by",
       "family_key": "cc"
     }
   }

The key must be **lowercase and whitespace-collapsed**.

How to Add a New URL Mapping
----------------------------

Edit ``urls/url_map.json``:

.. code:: json

   {
     "https://example.com/my-license/": {
       "version_key": "my-license",
       "name_key": "my-license",
       "family_key": "publisher-oa"
     }
   }

Both ``http://`` and ``https://`` variants may be listed; the loader
normalises them (converts http→https, strips/preserves trailing slash).

How to Add a New Prose Pattern
------------------------------

Edit ``prose/prose_patterns.json`` — insert your entry **before** any
pattern it should take priority over:

.. code:: json

   [
     {"pattern": "my very specific phrase", "version_key": "my-license",
      "name_key": "my-license", "family_key": "publisher-oa"},
     ...
   ]

Patterns are Python regular expressions matched case-insensitively.
More-specific patterns must come first.

How to Add a Brand-New License
------------------------------

1. Add entries to the JSON data files (``aliases/aliases.json``,
   ``urls/url_map.json``, or ``prose/prose_patterns.json``). Each entry
   maps a key to a dict with ``version_key``, ``name_key``, and
   ``family_key``.

2. If the ``family_key`` is not covered by the regex fallback table in
   ``_registry.py``, add an explicit ``family_key`` value in the JSON
   entry (recommended) or add a new regex pattern to
   ``_FAMILY_PATTERNS`` in ``_registry.py`` as a last resort.

3. Run ``make test-env ENV=py312`` to verify.

Upstream vs. Curated Files
--------------------------

There are two sets of external data files — upstream originals (large,
authoritative) and curated subsets (small, actually loaded at runtime).

**Upstream originals** — kept at the top level for developer use:

- ``spdx-licenses.json`` — the full `SPDX license list
  <https://spdx.org/licenses/>`_ (727 entries)
- ``opendefinition_licenses_all.json`` — the full `OpenDefinition list
  <https://opendefinition.org/>`_ (114 entries)

**Curated subsets** — trimmed to only the IDs the maintainer has vetted,
loaded by the package at runtime:

- ``spdx/spdx-licenses.json`` (52 entries)
- ``opendefinition/opendefinition_licenses_all.json`` (23 entries)

Updating SPDX or OpenDefinition
-------------------------------

To refresh the curated subsets from upstream:

1. Download the latest upstream file.
2. Copy only the entries you want to support into the corresponding
   subdirectory file.
3. Run ``make test-env ENV=py312`` to verify nothing broke.

Unknown license IDs from the curated subsets are silently skipped — they
do **not** cause errors.

The ``normalize_licenses.py`` tool (see below) automates discovering
which upstream IDs are missing from the curated subsets.

``normalize_licenses.py`` — Finding Coverage Gaps
-------------------------------------------------

``normalize_licenses.py`` is a **developer utility** that runs against
the full upstream files and reports which IDs normalise to ``family=unknown``.
It tells you exactly which entries to add to the curated subsets.

Run it from the repository root::

    python src/license_normaliser/data/normalize_licenses.py

The output shows successes and failures per upstream file. Any "failure"
means the ID has no coverage yet — add it to ``aliases/aliases.json`` or
``urls/url_map.json`` to fix it.

Metadata Merge Priority
-----------------------

When multiple data sources contribute metadata for the same
``version_key``:

- ``name_key`` – the **first** non-empty value wins (from builtin
  sources)
- ``family_key`` – the **first** non-empty value wins (from builtin
  sources)
- ``url`` – the **last** non-empty value wins (URL sources override
  aliases)
