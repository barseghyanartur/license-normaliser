==================
license-normaliser
==================

.. image:: https://raw.githubusercontent.com/barseghyanartur/license-normaliser/main/docs/_static/license_normaliser_logo.webp
   :alt: license-normaliser logo
   :align: center

Comprehensive license normalsation with a three-level hierarchy.

.. image:: https://img.shields.io/pypi/v/license-normaliser.svg
   :target: https://pypi.python.org/pypi/license-normaliser
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/license-normaliser.svg
   :target: https://pypi.python.org/pypi/license-normaliser/
   :alt: Supported Python versions

.. image:: https://github.com/barseghyanartur/license-normaliser/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/barseghyanartur/license-normaliser/actions
   :alt: Build Status

.. image:: https://readthedocs.org/projects/license-normaliser/badge/?version=latest
    :target: http://license-normaliser.readthedocs.io
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/docs-llms.txt-blue
    :target: https://license-normaliser.readthedocs.io/en/latest/llms.txt
    :alt: llms.txt - documentation for LLMs

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/barseghyanartur/license-normaliser/#License
   :alt: MIT

.. image:: https://coveralls.io/repos/github/barseghyanartur/license-normaliser/badge.svg?branch=main&service=github
    :target: https://coveralls.io/github/barseghyanartur/license-normaliser?branch=main
    :alt: Coverage

``license-normaliser`` is a comprehensive license normalisation library that
maps any license representation (SPDX tokens, URLs, prose descriptions) to a
canonical three-level hierarchy.

Features
========

- **Three-level hierarchy** - LicenseFamily → LicenseName → LicenseVersion.
- **Wide format support** - SPDX tokens, URLs, prose descriptions.
- **Creative Commons support** - Full CC family with versions and IGO variants.
- **Publisher-specific licenses** - Springer, Nature, Elsevier, Wiley, ACS,
  and more.
- **File-driven data** - Add aliases, URLs, and patterns by editing JSON files.
  No Python code changes required for new synonyms.
- **Pluggable parsers** - Drop in a new ``Parser`` class to ingest
  any external license registry. Parsers implement plugin interfaces
  (RegistryPlugin, URLPlugin, etc.).
- **Strict mode** - Raise ``LicenseNotFoundError`` instead of silently
  returning ``"unknown"``.
- **Caching** - LRU caching for performance.
- **CLI** - Command-line interface with ``--strict`` support.

Hierarchy
=========

The library uses a three-level hierarchy:

1. **LicenseFamily** - broad bucket: ``"cc"``, ``"osi"``, ``"copyleft"``,
   ``"publisher-tdm"``, ...
2. **LicenseName** - version-free: ``"cc-by"``, ``"cc-by-nc-nd"``, ``"mit"``,
   ``"wiley-tdm"``
3. **LicenseVersion** - fully resolved: ``"cc-by-3.0"``, ``"cc-by-nc-nd-4.0"``

Installation
============

With ``uv``:

.. code-block:: sh

    uv pip install license-normaliser

Or with ``pip``:

.. code-block:: sh

    pip install license-normaliser

Quick start
===========

.. code-block:: python
    :name: test_quick_start

    from license_normaliser import normalise_license

    v = normalise_license("CC BY-NC-ND 4.0")
    str(v)                  # "cc-by-nc-nd-4.0"   ← LicenseVersion
    str(v.license)          # "cc-by-nc-nd"       ← LicenseName
    str(v.license.family)   # "cc"                ← LicenseFamily

Strict mode
===========

By default, unresolvable inputs return an ``"unknown"`` result.  Pass
``strict=True`` to raise ``LicenseNotFoundError`` instead:

.. code-block:: python
    :name: test_strict_mode

    from license_normaliser import normalise_license
    from license_normaliser.exceptions import LicenseNotFoundError

    # Silent fallback (default)
    v = normalise_license("some-unknown-string")
    v.family.key  # "unknown"

    # Strict: raises on unresolvable input
    try:
        v = normalise_license("some-unknown-string", strict=True)
    except LicenseNotFoundError as exc:
        print(exc.raw)      # original input
        print(exc.cleaned)  # cleaned form that failed lookup

Trace / Explain
===============

Set ``ENABLE_LICENSE_NORMALISER_TRACE=1`` or pass ``trace=True`` to get
resolution traces showing how the license was matched:

.. code-block:: python
    :name: test_trace

    from license_normaliser import normalise_license

    # Via function
    v = normalise_license("cc by-nc-nd 3.0 igo", trace=True)
    print(v.explain())

    # Via class
    from license_normaliser import LicenseNormaliser
    ln = LicenseNormaliser(trace=True)
    v = ln.normalise_license("MIT")
    print(v.explain())

Output shows the resolution pipeline (alias → registry → url → prose →
fallback) and which source file + line matched:

.. code-block:: text

    Input: 'cc by-nc-nd 3.0 igo' → 'cc by-nc-nd 3.0 igo'
      [✓] alias: 'cc by-nc-nd 3.0 igo' → 'cc-by-nc-nd-3.0-igo' (line 139 in aliases.json)

    Result:
      version_key: 'cc-by-nc-nd-3.0-igo'
      name_key: 'cc-by-nc-nd'
      family_key: 'cc'

The trace can also be accessed via ``v._trace`` for programmatic use.

Batch normalisation
===================

.. code-block:: python
    :name: test_batch_normalisation

    from license_normaliser import normalise_licenses

    results = normalise_licenses(["MIT", "Apache-2.0", "CC BY 4.0"])
    for r in results:
        print(r.key)

    # Strict batch - raises on first unresolvable
    results = normalise_licenses(["MIT", "Apache-2.0"], strict=True)

Custom plugins
==============

The ``LicenseNormaliser`` class lets you inject custom plugin classes for
specialised use cases:

.. code-block:: python
    :name: test_custom_plugins

    from license_normaliser import LicenseNormaliser
    from license_normaliser.parsers.alias import AliasParser
    from license_normaliser.parsers.spdx import SPDXParser

    # Use only SPDX + Alias plugins (no CC, no publisher URLs)
    ln = LicenseNormaliser(
        registry=[SPDXParser],
        alias=[AliasParser],
        family=[AliasParser],
        name=[AliasParser],
        cache=True,
        cache_maxsize=8192,
    )

    # MIT resolves via SPDX parser
    assert str(ln.normalise_license("MIT")) == "mit"

    # CC BY resolves via Alias
    assert str(ln.normalise_license("CC BY-NC-ND 4.0")) == "cc-by-nc-nd-4.0"

.. note::

    Explicit plugin passing is optional — ``LicenseNormaliser()``
    automatically loads defaults. Use the pattern above only if you need
    custom plugins or reduce number of plugins loaded.

For caching, ``LicenseNormaliser`` wraps the resolution method
with ``lru_cache``.
Disable it by passing ``cache=False`` for debugging:

.. code-block:: python
    :name: test_caching

    from license_normaliser import LicenseNormaliser

    ln = LicenseNormaliser(cache=False)
    result = ln.normalise_license("MIT")

Update data (CLI)
=================

.. code-block:: sh

    license-normaliser update-data --force
    # Fetches fresh SPDX, OpenDefinition, OSI, CreativeCommons, and ScanCode JSONs

Integration tests (public API only)
===================================

All integration tests live in
``src/license_normaliser/tests/test_integration.py``
and only import the public API.

CLI usage
=========

Normalise a single license:

.. code-block:: sh

    license-normaliser normalise "MIT"
    # Output: mit

    license-normaliser normalise --full "CC BY 4.0"
    # Output:
    # Key: cc-by-4.0
    # URL: https://creativecommons.org/licenses/by/4.0/
    # License: cc-by
    # Family: cc

    license-normaliser normalise --strict "totally-unknown"
    # Exits with code 1 and prints an error

Batch normalise:

.. code-block:: sh

    license-normaliser batch MIT "Apache-2.0" "CC BY 4.0"
    license-normaliser batch --strict MIT "Apache-2.0"

Exceptions
==========

.. code-block:: python
    :name: test_exceptions

    from license_normaliser.exceptions import (
        LicenseNormaliserError,   # base class
        LicenseNotFoundError,     # raised by strict mode
    )

Testing
=======

All tests run inside Docker:

.. code-block:: sh

    make test

To test a specific Python version:

.. code-block:: sh

    make test-env ENV=py312

License
=======

MIT

Author
======

Artur Barseghyan <artur.barseghyan@gmail.com>
