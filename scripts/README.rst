Scripts
=======

Sort aliases
------------

Sorts ``aliases.json`` keys alphabetically. Comment keys (starting with
``_``) are preserved at the top in their original order. All other entries
are sorted case-insensitively.

.. code-block:: sh

    uv run python scripts/sort_aliases.py
    uv run python scripts/sort_aliases.py --check  # exit 1 if not sorted

Find alias duplicates
---------------------

Finds duplicate ``version_key`` entries in ``aliases.json``. A "duplicate"
is when two or more top-level primary keys share the same ``version_key``.
Reports groups with more than one member.

Can optionally fix duplicates by merging them into the ``aliases`` list of
a single canonical entry.

.. code-block:: sh

    uv run python scripts/find_alias_duplicates.py
    uv run python scripts/find_alias_duplicates.py --fix      # interactive fix
    uv run python scripts/find_alias_duplicates.py --noinput  # auto-apply safe fixes

Apply aliases patch
-------------------

Applies curated additions to ``aliases.json``. Adds an ``aliases`` list to
existing CC version-free entries and adds new top-level entries for GPL
shorthand keys that currently fall through to the unknown fallback.

.. code-block:: sh

    uv run python scripts/apply_aliases_patch.py

Compare datasets
----------------

Compares SPDX, OpenDefinition, OSI, CreativeCommons, ScanCode, and curated
data files (aliases, url_map, prose, publishers).

.. code-block:: sh

    uv run python scripts/compare_datasets.py

Check missing aliases
---------------------

Checks which licences downloaded from the internet (via refreshable plugins)
have corresponding entries in the curated ``aliases.json`` file.

.. code-block:: sh

    uv run python scripts/check_missing_aliases.py
    uv run python scripts/check_missing_aliases.py --json  # JSON output


Test name inference
-------------------

Assesses the accuracy of heuristic name stripping against curated name_key
values from aliases.json. Shows how well automatic name extraction works
for different licence families (CC, copyleft, OSI, etc.).

.. code-block:: sh

    uv run python scripts/test_name_inference.py
    uv run python scripts/test_name_inference.py --json  # JSON output
    uv run python scripts/test_name_inference.py --details  # Detailed breakdown

Documentation Validator
-----------------------

Validates that documentation files (README.rst, AGENTS.md, ARCHITECTURE.rst,
etc.) match the source code ground truth. Extracts actual API exports,
parser classes, CLI commands, and exceptions from source code, then checks
documentation accuracy.

.. code-block:: sh

    uv run python scripts/documentation_validator.py              # Check all documentation
    uv run python scripts/documentation_validator.py -v           # Verbose output
    uv run python scripts/documentation_validator.py --json       # JSON output for CI
    uv run python scripts/documentation_validator.py --fix        # Auto-fix issues

Checks performed:

- File paths referenced in docs actually exist
- All parser classes are documented in tables
- All CLI commands are documented
- Python code blocks have ``:name:`` attributes
- Public API exports are documented
