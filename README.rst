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
- **Caching** - LRU caching for performance.
- **CLI** - Command-line interface for quick normalisation.

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

Resolution pipeline (first match wins)
======================================

1. Direct registry lookup (cleaned lowercase key)
2. Alias table (prose variants, SPDX tokens, mixed-case short-forms)
3. Exact URL map (http/https, trailing-slash normalised, fragment-aware)
4. Structural CC URL regex (any creativecommons.org URL not in the map)
5. Prose keyword scan (full sentences from license documents)
6. Fallback (key = cleaned string, everything else unknown/None)

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

Batch normalise multiple licenses:

.. code-block:: sh

    license-normaliser batch MIT "Apache-2.0" "CC BY 4.0"
    # Output:
    # MIT: mit
    # Apache-2.0: apache-2.0
    # CC BY 4.0: cc-by-4.0

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

Support
=======

For issues, go to `GitHub <https://github.com/barseghyanartur/license-normaliser/issues>`_.

Author
======

Artur Barseghyan <artur.barseghyan@gmail.com>
