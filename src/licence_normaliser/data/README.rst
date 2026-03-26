Data Directory
==============

This directory contains all normalisation data files loaded at runtime
by ``licence-normaliser``. You can extend or override entries without
touching any Python code.

Structure
---------

::

    data/
    ├── aliases/
    │   └── aliases.json             # Alias string → metadata dict (includes URLs and shorthand aliases)
    ├── prose/
    │   └── prose_patterns.json      # Ordered regex patterns for long text scanning
    ├── spdx/
    │   └── spdx.json                # SPDX licence list (auto-refreshed)
    ├── opendefinition/
    │   └── opendefinition.json      # Open Definition list (auto-refreshed)
    ├── osi/
    │   └── osi.json                 # OSI licence list (auto-refreshed)
    ├── creativecommons/
    │   └── creativecommons.json     # CC licences (scraped from creativecommons.org)
    └── scancode_licensedb/
        └── scancode_licensedb.json  # ScanCode licence DB (auto-refreshed)

Entry Format
------------

Every entry maps a **lookup key** (alias string, URL, or prose pattern)
to a metadata dict with three required fields:

- ``version_key`` – the canonical version-level identifier
  (e.g. ``"cc-by-4.0"``)
- ``name_key`` – the name-level identifier without version suffix
  (e.g. ``"cc-by"``)
- ``family_key`` – the family-level identifier (e.g. ``"cc"``)

URLs are stored separately in the ``url`` field of the metadata dict.

How to add a new licence alias
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

How to Add a Publisher URL or Shorthand Alias
---------------------------------------------

**Note**: Publisher URLs and shorthand aliases are stored
in ``aliases/aliases.json``.

Add a new entry or update an existing one:

.. code:: json

   "my-alias": {
     "version_key": "my-licence",
     "name_key": "my-licence",
     "family_key": "publisher-oa",
     "aliases": ["my shorthand alias"],
     "urls": ["https://example.com/my-licence/"]
   }

Both ``http://`` and ``https://`` URL variants may be listed; they are
normalised at lookup time (http→https, trailing slash stripped).

How to Add a New Prose Pattern
------------------------------

Edit ``prose/prose_patterns.json`` — insert your entry **before** any
pattern it should take priority over:

.. code:: json

   [
     {"pattern": "my very specific phrase",
      "version_key": "my-licence",
      "name_key": "my-licence",
      "family_key": "publisher-oa"},
     ...
   ]

Patterns are Python regular expressions matched case-insensitively.
More-specific patterns must come first.

How to add a brand-new licence
------------------------------

1. Add entries to one or more JSON data files (``aliases/aliases.json``,
   ``urls/url_map.json``, ``prose/prose_patterns.json``, or
   ``publishers/publishers.json``). Each entry maps a key to a dict with
   ``version_key``, ``name_key``, and ``family_key``.

2. If the ``family_key`` is not covered by the regex fallback table in
   ``_registry.py``, add an explicit ``family_key`` value in the JSON
   entry (recommended).

3. Run ``make test-env ENV=py312`` to verify.

Updating SPDX or OpenDefinition
-------------------------------

The ``licence-normaliser update-data`` CLI command fetches fresh upstream data:

.. code:: sh

    licence-normaliser update-data --force

This updates:

- ``spdx/spdx.json`` — full `SPDX licence list <https://spdx.org/licenses/>`_
- ``opendefinition/opendefinition.json`` — full `Open Definition list <https://opendefinition.org/>`_
- ``osi/osi.json`` — `OSI licence list <https://opensource.org/licenses>`_
- ``creativecommons/creativecommons.json`` — scraped from creativecommons.org
- ``scancode_licensedb/scancode_licensedb.json`` — `ScanCode licence DB <https://scancode-licensedb.aboutcode.org/>`_

Family Override Files
---------------------

Some entries carry an explicit ``family_key`` that overrides the
inference logic in ``_registry.py``.  These are stored in:

- ``aliases/aliases.json`` — ``family_key`` on any alias entry populates
  ``FAMILY_OVERRIDES`` at import time.
