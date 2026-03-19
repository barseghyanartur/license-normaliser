======================
Contributor guidelines
======================

Developer prerequisites
-----------------------

Install ``uv`` and set up pre-commit:

.. code-block:: sh

    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv tool install pre-commit
    pre-commit install

Virtual environment & installation
------------------------------------

.. code-block:: sh

    make create-venv
    make install

Testing
-------

**All tests must be run inside Docker.**

.. code-block:: sh

    make test               # full matrix (Python 3.10–3.14)
    make test-env ENV=py312 # single version
    make shell              # interactive shell

Adding new normalisation rules
------------------------------

For a new **alias, URL, or prose pattern** for an *existing* license:

1. Edit the appropriate JSON file under ``data/``.
2. No Python changes needed.

For a **brand-new license**:

1. Add enum entries to ``src/license_normaliser/_enums.py``.
2. Populate ``data/`` JSON files.
3. Add tests.

For a **new external data source**:

1. Implement the ``DataSource`` protocol in ``data_sources/``.
2. Register it in ``REGISTERED_SOURCES``.
3. Add tests.

Pull requests
-------------

Open a pull request to the ``dev`` branch only.

Every new normalisation rule must have a corresponding test.
When fixing bugs, add a regression test that fails before your fix.
