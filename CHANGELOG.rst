Release history and notes
=========================
.. Internal references

.. _Armenian genocide: https://en.wikipedia.org/wiki/Armenian_genocide

`Sequence based identifiers
<http://en.wikipedia.org/wiki/Software_versioning#Sequence-based_identifiers>`_
are used for versioning (schema follows below):

.. code-block:: text

    major.minor[.revision]

- It is always safe to upgrade within the same minor version (for example,
  from 0.3 to 0.3.4).
- Minor version changes might be backwards incompatible. Read the
  release notes carefully before upgrading (for example, when upgrading from
  0.3.4 to 0.4).
- All backwards incompatible changes are mentioned in this document.

0.5
---
2026-03-27

- Merge url_map.json and publisher.json into aliases.json.
- Simplify lookups.
- Fix wrongly categorised licences.
- Various fixes.

0.4
---
2026-03-26

- Renamed project from `license-normaliser` to `licence-normaliser`.
- Cleanup.

0.3.2
-----
2026-03-25

- Introduce sub-aliases in aliases.json.
- Introduce handy scripts for finding, automatic filling and merging the
  duplicates.

0.3.1
-----
2026-03-24

- Minor fixes.

0.3
---
2026-03-23

- **Plugin-based architecture** — `LicenceNormaliser` class accepts plugin
  CLASSES (not instances) with lazy loading; replaces old module-level globals.
- **6 plugin interfaces** — `BasePlugin`, `RegistryPlugin`, `URLPlugin`,
  `AliasPlugin`, `FamilyPlugin`, `NamePlugin`, `ProsePlugin`.
- **New `BasePlugin.refresh()`** — classmethod to fetch/refresh data from
  upstream URLs; CLI uses parser IDs (`spdx`, `opendefinition`, etc.) instead
  of class names.
- **Thread-safe singleton** — `_DefaultNormaliser` class with double-checked
  locking protects the shared `LicenceNormaliser` instance.
- **Public `registry_keys()`** — `LicenceNormaliser.registry_keys()` exposes
  known keys; `get_registry_keys()` in `_cache.py` uses it.
- **URL population fix** — inverted URL map (`version_key → cleaned_url`)
  ensures `LicenceVersion.url` is populated for resolved licences.
- **Removed dead code** — deleted `_registry.py`, `parsers/base.py`,
  `parsers/__init__.py`, and empty `DEFAULT_*` module globals.
- **Docs updated** — ARCHITECTURE.rst, AGENTS.md, README.rst rewritten to
  reflect new plugin architecture.

0.2
---
2026-03-21

- **Architecture rewrite** — parser-based pluggable system with 8 parsers
  loading from JSON data files.
- **3-level hierarchy** — `LicenceFamily → LicenceName → LicenceVersion`
  with 11 families including publisher OA/TDM.
- **New data files** — 170+ aliases, 41 prose patterns, 50+ publisher
  URLs (Elsevier, Wiley, Springer, ACS, etc.).
- **Strict mode** — `strict=True` raises `LicenceNotFoundError` on unknown
  licences.
- **Bug fixes** — `cc-pdm`/`cc0` family inference, `gpl-3.0+` `+`-suffix
  stripping, false-positive prose pattern removed, ALIASES-before-REGISTRY
  lookup order.
- **Tests** — 386 tests (up from ~80), including 165-case integration matrix.
- **Docs** — `AGENTS.md`, `ARCHITECTURE.rst`, `CONTRIBUTING.rst` rewritten;
  stale `literalinclude` targets fixed.


0.1.1
-----
2026-03-17

- Remove Pydantic as dependency.

0.1
-----
2026-03-17

- Initial beta release.
