Scripts
=======

Compare datasets
----------------

Compares SPDX, OpenDefinition, OSI, CreativeCommons, ScanCode, and curated
data files (aliases, url_map, prose, publishers).

.. code-block:: sh

    uv run python ./scripts/compare_datasets.py

Check missing aliases
---------------------

Checks which licenses downloaded from the internet (via refreshable plugins)
have corresponding entries in the curated aliases.json file.

.. code-block:: sh

    uv run python scripts/check_missing_aliases.py
    uv run python scripts/check_missing_aliases.py --json  # JSON output


Test name inference
-------------------

Assesses the accuracy of heuristic name stripping against curated name_key
values from aliases.json. Shows how well automatic name extraction works
for different license families (CC, copyleft, OSI, etc.).

.. code-block:: sh

    uv run python scripts/test_name_inference.py
    uv run python scripts/test_name_inference.py --json  # JSON output
    uv run python scripts/test_name_inference.py --details  # Detailed breakdown
