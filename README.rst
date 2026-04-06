==================
licence-normaliser
==================

.. image:: https://raw.githubusercontent.com/barseghyanartur/licence-normaliser/main/docs/_static/licence_normaliser_logo.webp
   :alt: licence-normaliser logo
   :align: center

Robust licence normalisation with a three-level hierarchy for common licences.

.. image:: https://img.shields.io/pypi/v/licence-normaliser.svg
   :target: https://pypi.python.org/pypi/licence-normaliser
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/licence-normaliser.svg
   :target: https://pypi.python.org/pypi/licence-normaliser/
   :alt: Supported Python versions

.. image:: https://github.com/barseghyanartur/licence-normaliser/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/barseghyanartur/licence-normaliser/actions
   :alt: Build Status

.. image:: https://readthedocs.org/projects/licence-normaliser/badge/?version=latest
    :target: http://licence-normaliser.readthedocs.io
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/docs-llms.txt-blue
    :target: https://licence-normaliser.readthedocs.io/en/latest/llms.txt
    :alt: llms.txt - documentation for LLMs

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/barseghyanartur/licence-normaliser/#Licence
   :alt: MIT

.. image:: https://coveralls.io/repos/github/barseghyanartur/licence-normaliser/badge.svg?branch=main&service=github
    :target: https://coveralls.io/github/barseghyanartur/licence-normaliser?branch=main
    :alt: Coverage

``licence-normaliser`` maps common licence representations (SPDX tokens,
URLs, prose descriptions) to a canonical three-level hierarchy.

Features
========

- **Three-level hierarchy** - LicenceFamily → LicenceName → LicenceVersion.
- **Wide format support** - SPDX tokens, URLs, and prose descriptions for
  supported licences.
- **Creative Commons support** - Full CC family with versions and IGO variants.
- **Publisher-specific licences** - Springer, Nature, Elsevier, Wiley, ACS,
  and more.
- **File-driven data** - Add aliases, URLs, and patterns by editing JSON files.
  No Python code changes required for new synonyms.
- **Pluggable parsers** - Drop in a new parser class to ingest
  any external licence registry. Parsers implement plugin interfaces
  (``RegistryPlugin``, ``URLPlugin``, etc.).
- **Strict mode** - Raise ``LicenceNotFoundError`` instead of silently
  returning ``"unknown"``.
- **Caching** - LRU caching for performance.
- **CLI** - Command-line interface with ``--strict`` and ``--explain`` support.

Hierarchy
=========

The library uses a three-level hierarchy:

1. **LicenceFamily** - broad bucket: ``"cc"``, ``"osi"``, ``"copyleft"``,
   ``"publisher-tdm"``, ...
2. **LicenceName** - version-free: ``"cc-by"``, ``"cc-by-nc-nd"``, ``"mit"``,
   ``"wiley-tdm"``
3. **LicenceVersion** - fully resolved: ``"cc-by-3.0"``, ``"cc-by-nc-nd-4.0"``

Installation
============

With ``uv``:

.. code-block:: sh

    uv pip install licence-normaliser

Or with ``pip``:

.. code-block:: sh

    pip install licence-normaliser

Quick start
===========

.. code-block:: python
    :name: test_quick_start

    from licence_normaliser import normalise_licence

    v = normalise_licence("CC BY-NC-ND 4.0")
    assert str(v) == "cc-by-nc-nd-4.0"      #     ← LicenceVersion
    assert str(v.licence) == "cc-by-nc-nd"  #     ← LicenceName
    assert str(v.licence.family) == "cc"    #     ← LicenceFamily


Strict mode
===========

By default, unresolvable inputs return an ``"unknown"`` result. Pass
``strict=True`` to raise ``LicenceNotFoundError`` instead:

.. code-block:: python
    :name: test_strict_mode

    from licence_normaliser import normalise_licence
    from licence_normaliser.exceptions import LicenceNotFoundError

    # Silent fallback (default)
    v = normalise_licence("some-unknown-string")
    assert v.family.key == "unknown"

    # Strict: raises on unresolvable input
    try:
        v = normalise_licence("some-unknown-string", strict=True)
    except LicenceNotFoundError as exc:
        print(exc.raw)      # original input
        print(exc.cleaned)  # cleaned form that failed lookup

Trace / Explain
===============

Set ``ENABLE_LICENCE_NORMALISER_TRACE=1`` or pass ``trace=True`` to get
resolution traces showing how the licence was matched:

.. code-block:: python
    :name: test_trace

    from licence_normaliser import normalise_licence

    # Via function
    v = normalise_licence("cc by-nc-nd 3.0 igo", trace=True)
    print(v.explain())

    # Via class
    from licence_normaliser import LicenceNormaliser
    ln = LicenceNormaliser(trace=True)
    v = ln.normalise_licence("MIT")
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

    from licence_normaliser import normalise_licences

    results = normalise_licences(["MIT", "Apache-2.0", "CC BY 4.0"])
    for r in results:
        print(r.key)

    # Strict batch - raises on first unresolvable
    results = normalise_licences(["MIT", "Apache-2.0"], strict=True)

Custom plugins
==============

The ``LicenceNormaliser`` class lets you inject custom plugin classes for
specialised use cases:

.. code-block:: python
    :name: test_custom_plugins

    from licence_normaliser import LicenceNormaliser
    from licence_normaliser.parsers.alias import AliasParser
    from licence_normaliser.parsers.spdx import SPDXParser

    # Use only SPDX + Alias plugins (no CC, no publisher URLs)
    ln = LicenceNormaliser(
        registry=[SPDXParser],
        alias=[AliasParser],
        family=[AliasParser],
        name=[AliasParser],
        cache=True,
        cache_maxsize=8192,
    )

    # MIT resolves via SPDX parser
    assert str(ln.normalise_licence("MIT")) == "mit"

    # CC BY resolves via Alias
    assert str(ln.normalise_licence("CC BY-NC-ND 4.0")) == "cc-by-nc-nd-4.0"

.. note::

    ``LicenceNormaliser()`` automatically loads the full default set of
    parsers. To use a reduced set you must explicitly pass *all* six
    plugin lists (registry, url, alias, family, name, prose).

For caching, ``LicenceNormaliser`` wraps the resolution method
with ``lru_cache``.
Disable it by passing ``cache=False`` for debugging:

.. code-block:: python
    :name: test_caching

    from licence_normaliser import LicenceNormaliser

    ln = LicenceNormaliser(cache=False)
    result = ln.normalise_licence("MIT")

Update data (CLI)
=================

.. code-block:: sh

    licence-normaliser update-data --force
    # Fetches fresh SPDX, OpenDefinition, OSI, CreativeCommons, and ScanCode JSONs

Integration tests (public API only)
===================================

All integration tests live in
``src/licence_normaliser/tests/test_integration.py``
and only import the public API.

CLI usage
=========

Normalise a single licence:

.. code-block:: sh

    licence-normaliser normalise "MIT"
    # Output: mit

    licence-normaliser normalise --full "CC BY 4.0"
    # Output:
    # Key: cc-by-4.0
    # URL: https://creativecommons.org/licenses/by/4.0/
    # Licence: cc-by
    # Family: cc

    licence-normaliser normalise --strict "totally-unknown"
    # Exits with code 1 and prints an error

Batch normalise:

.. code-block:: sh

    licence-normaliser batch MIT "Apache-2.0" "CC BY 4.0"
    licence-normaliser batch --strict MIT "Apache-2.0"

Exceptions
==========

.. code-block:: python
    :name: test_exceptions

    from licence_normaliser.exceptions import (
        DataSourceError,           # data source loading errors
        LicenceNormaliserError,    # base class
        LicenceNotFoundError,      # raised by strict mode
        LicenceNormalisationError, # kept for backwards compatibility
    )

    from licence_normaliser import (
        LicenceTrace,      # resolution trace object
        LicenceTraceStage,   # resolution stage enum
    )

Testing
=======

All tests run inside Docker:

.. code-block:: sh

    make test

To test a specific Python version:

.. code-block:: sh

    make test-env ENV=py312

Licence
=======

MIT

Author
======

Artur Barseghyan <artur.barseghyan@gmail.com>
