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

0.2
---
2026-03-21

- **Architecture rewrite** — parser-based pluggable system with 8 parsers
  loading from JSON data files.
- **3-level hierarchy** — `LicenseFamily → LicenseName → LicenseVersion`
  with 11 families including publisher OA/TDM.
- **New data files** — 170+ aliases, 41 prose patterns, 50+ publisher
  URLs (Elsevier, Wiley, Springer, ACS, etc.).
- **Strict mode** — `strict=True` raises `LicenseNotFoundError` on unknown
  licenses.
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
