======================
Contributor guidelines
======================

.. _licence-normaliser: https://github.com/barseghyanartur/licence-normaliser/
.. _uv: https://docs.astral.sh/uv/
.. _tox: https://tox.wiki
.. _ruff: https://beta.ruff.rs/docs/
.. _doc8: https://doc8.readthedocs.io/
.. _pre-commit: https://pre-commit.com/#installation
.. _issues: https://github.com/barseghyanartur/licence-normaliser/issues
.. _discussions: https://github.com/barseghyanartur/licence-normaliser/discussions
.. _pull request: https://github.com/barseghyanartur/licence-normaliser/pulls
.. _versions manifest: https://github.com/actions/python-versions/blob/main/versions-manifest.json

Developer prerequisites
-----------------------

pre-commit
~~~~~~~~~~

Refer to `pre-commit`_ for installation instructions.

TL;DR:

.. code-block:: sh

    curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
    uv tool install pre-commit                       # Install pre-commit
    pre-commit install                               # Install hooks

Installing `pre-commit`_ ensures all contributions adhere to the project's
code quality standards.

Code standards
--------------

`ruff`_ and `doc8`_ are triggered automatically by `pre-commit`_.

To run checks manually:

.. code-block:: sh

    make doc8
    make ruff

Import conventions
~~~~~~~~~~~~~~~~~~

**Import statements belong at module level.** Avoid placing imports inside
functions or methods unless absolutely necessary:

- **Acceptable exceptions:**

  - Breaking circular dependencies
  - Optional runtime dependencies (e.g., CLI-only imports)
  - Heavy imports that are rarely used

- **Why this matters:**

  - Improves code readability
  - Makes dependencies explicit and discoverable
  - Enables static analysis tools to work correctly
  - Follows Python community best practices (PEP 8)

When in doubt, place imports at the top of the file.

Virtual environment
-------------------

.. code-block:: sh

    make create-venv

Installation
------------

.. code-block:: sh

    make install

Testing
-------

.. note::
   Python 3.15 is being tested on GitHub CI, but not inside a local Docker image.

Docker-based testing (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All tests run inside Docker for platform independence and consistency:

.. code-block:: sh

    make test                    # full matrix (Python 3.10-3.14)
    make test-env ENV=py312      # single Python version
    make shell                   # interactive shell in test container
    make shell-env ENV=py312     # interactive shell for specific Python

Local testing (alternative)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For faster iteration during development, you can run tests locally with ``uv``:

.. code-block:: sh

    make install                 # one-time setup
    uv run pytest                # run all tests
    uv run pytest path/to/test_something.py  # run specific test

**Important**: If you encounter tooling errors with local testing, fall back to
Docker-based testing which is the canonical environment.

GitHub Actions
~~~~~~~~~~~~~~

In any case, GitHub Actions runs the full matrix automatically on every push.
Tests run on Python 3.10–3.15 (all non-EOL versions).  See the
`versions manifest`_ for the full list of available Python versions.

Adding new normalisation rules
------------------------------

For a new **alias** or **family override** for an *existing* licence:

1. Add an entry to ``src/licence_normaliser/data/aliases/aliases.json``.
2. Optionally, add an ``aliases`` array to define additional lookup variants
   (e.g. hyphen vs space forms) that resolve to the same target:

   .. code-block:: json

       {
         "cc by-nc": {
           "version_key": "cc-by-nc",
           "name_key": "cc-by-nc",
           "family_key": "cc",
           "aliases": ["cc-by-nc", "cc by nc", "cc-by nc"]
         }
       }

3. Add a test in ``src/licence_normaliser/tests/test_aliases.py`` or
   ``test_alias_expansion.py``.
4. No Python changes needed.

For a new **prose pattern** (regex matching free-text descriptions):

1. Add an entry to ``src/licence_normaliser/data/prose/prose_patterns.json``.
2. Add a test in ``src/licence_normaliser/tests/test_prose.py``.
3. No Python changes needed.

For a new **URL mapping**:

1. Add an entry to ``src/licence_normaliser/data/urls/url_map.json`` or
   ``src/licence_normaliser/data/publishers/publishers.json``.
2. Add a test in ``src/licence_normaliser/tests/test_publisher.py``.
3. No Python changes needed.

For a **brand-new licence key** (SPDX, OpenDefinition, OSI, CC, or ScanCode):

1. The upstream data source must be updated first
   (``licence-normaliser update-data --force`` for SPDX/OpenDefinition, or
   edit the upstream source for OSI/CC/ScanCode).
2. The parser will pick it up automatically on the next import.
3. Add an alias in ``aliases.json`` if needed.
4. Add family override in ``aliases.json`` if needed.
5. Add tests.

For a **new parser** (new upstream data source):

1. Create ``src/licence_normaliser/parsers/my_parser.py`` implementing
   ``BasePlugin``.
2. Register it in ``src/licence_normaliser/parsers/__init__.py``.
3. Set ``is_registry_entry = False`` if the parser only contributes
   aliases/URLs/patterns (not new licence keys).
4. Add tests.

Releases
--------
**Build the package for releasing:**

.. code-block:: sh

    make package-build

----

**Test the built package:**

.. code-block:: sh

    make check-package-build

----

**Make a test release (test.pypi.org):**

.. code-block:: sh

    make test-release

----

**Release (pypi.org):**

.. code-block:: sh

    make release

Adding tests
------------

- Every new normalisation rule must have a corresponding test.
- Tests should cover both successful normalisation and edge cases.

Pull requests
-------------

Open a `pull request`_ to the ``dev`` branch only. Never directly to ``main``.

.. note::

    Create pull requests to the ``dev`` branch only!

Examples of welcome contributions:

- Fixing documentation typos or improving explanations.
- Adding test cases for new edge cases.
- Extending support for additional licence formats.
- Improving error messages.

General checklist
~~~~~~~~~~~~~~~~~

- Does your change require documentation updates (``README.rst``,
  ``AGENTS.md``, ``ARCHITECTURE.rst``, ``CONTRIBUTING.rst``)?
- Does your change require new tests?
- Does your change add any external dependencies?
  If so, reconsider: ``licence-normaliser`` should have minimal dependencies.

When fixing bugs
~~~~~~~~~~~~~~~~

- Add a regression test that reproduces the bug before your fix.

When adding a new feature
~~~~~~~~~~~~~~~~~~~~~~~~~

- Update ``README.rst``, ``AGENTS.md``, and ``ARCHITECTURE.rst`` if applicable.
- Add appropriate tests.

Questions
---------

Ask on GitHub `discussions`_.

Issues
------

Report bugs or request features on GitHub `issues`_.
