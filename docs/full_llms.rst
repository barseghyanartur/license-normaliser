Full project source-tree
========================

Below is the layout of the project (to 10 levels), followed by
the contents of each key file.

.. code-block:: text
   :caption: Project directory layout

   license-normaliser/
   ├── docs
   │   ├── conf.py
   │   └── full_llms.rst
   ├── scripts
   │   ├── __init__.py
   │   ├── apply_aliases_patch.py
   │   ├── check_missing_aliases.py
   │   ├── compare_datasets.py
   │   ├── compare_scancode_categories.py
   │   ├── find_alias_duplicates.py
   │   ├── migrate_publishers_to_aliases.py
   │   ├── migrate_url_map_to_aliases.py
   │   ├── README.rst
   │   ├── sort_aliases.py
   │   └── test_name_inference.py
   ├── src
   │   └── licence_normaliser
   │       ├── cli
   │       │   ├── __init__.py
   │       │   └── _main.py
   │       ├── data
   │       │   ├── aliases
   │       │   │   └── aliases.json
   │       │   ├── prose
   │       │   │   └── prose_patterns.json
   │       │   └── README.rst
   │       ├── parsers
   │       │   ├── __init__.py
   │       │   ├── alias.py
   │       │   ├── creativecommons.py
   │       │   ├── opendefinition.py
   │       │   ├── osi.py
   │       │   ├── prose.py
   │       │   ├── scancode_licensedb.py
   │       │   └── spdx.py
   │       ├── tests
   │       │   ├── __init__.py
   │       │   ├── conftest.py
   │       │   ├── test_alias_expansion.py
   │       │   ├── test_aliases.py
   │       │   ├── test_cache.py
   │       │   ├── test_cli.py
   │       │   ├── test_core.py
   │       │   ├── test_exceptions.py
   │       │   ├── test_integration.py
   │       │   ├── test_models.py
   │       │   ├── test_prose.py
   │       │   └── test_trace.py
   │       ├── __init__.py
   │       ├── _cache.py
   │       ├── _core.py
   │       ├── _models.py
   │       ├── _normaliser.py
   │       ├── _trace.py
   │       ├── defaults.py
   │       ├── exceptions.py
   │       ├── plugins.py
   │       └── py.typed
   ├── AGENTS.md
   ├── conftest.py
   ├── CONTRIBUTING.rst
   ├── docker-compose.yml
   ├── Dockerfile
   ├── Makefile
   ├── pyproject.toml
   ├── README.rst
   └── tox.ini

README.rst
----------

.. literalinclude:: ../README.rst
   :language: rst
   :caption: README.rst

CONTRIBUTING.rst
----------------

.. literalinclude:: ../CONTRIBUTING.rst
   :language: rst
   :caption: CONTRIBUTING.rst

AGENTS.md
---------

.. literalinclude:: ../AGENTS.md
   :language: markdown
   :caption: AGENTS.md

conftest.py
-----------

.. literalinclude:: ../conftest.py
   :language: python
   :caption: conftest.py

docker-compose.yml
------------------

.. literalinclude:: ../docker-compose.yml
   :language: yaml
   :caption: docker-compose.yml

docs/conf.py
------------

.. literalinclude:: conf.py
   :language: python
   :caption: docs/conf.py

docs/full_llms.rst
------------------

.. literalinclude:: full_llms.rst
   :language: rst
   :caption: docs/full_llms.rst

pyproject.toml
--------------

.. literalinclude:: ../pyproject.toml
   :language: toml
   :caption: pyproject.toml

scripts/README.rst
------------------

.. literalinclude:: ../scripts/README.rst
   :language: rst
   :caption: scripts/README.rst

scripts/__init__.py
-------------------

.. literalinclude:: ../scripts/__init__.py
   :language: python
   :caption: scripts/__init__.py

scripts/apply_aliases_patch.py
------------------------------

.. literalinclude:: ../scripts/apply_aliases_patch.py
   :language: python
   :caption: scripts/apply_aliases_patch.py

scripts/check_missing_aliases.py
--------------------------------

.. literalinclude:: ../scripts/check_missing_aliases.py
   :language: python
   :caption: scripts/check_missing_aliases.py

scripts/compare_datasets.py
---------------------------

.. literalinclude:: ../scripts/compare_datasets.py
   :language: python
   :caption: scripts/compare_datasets.py

scripts/compare_scancode_categories.py
--------------------------------------

.. literalinclude:: ../scripts/compare_scancode_categories.py
   :language: python
   :caption: scripts/compare_scancode_categories.py

scripts/find_alias_duplicates.py
--------------------------------

.. literalinclude:: ../scripts/find_alias_duplicates.py
   :language: python
   :caption: scripts/find_alias_duplicates.py

scripts/migrate_publishers_to_aliases.py
----------------------------------------

.. literalinclude:: ../scripts/migrate_publishers_to_aliases.py
   :language: python
   :caption: scripts/migrate_publishers_to_aliases.py

scripts/migrate_url_map_to_aliases.py
-------------------------------------

.. literalinclude:: ../scripts/migrate_url_map_to_aliases.py
   :language: python
   :caption: scripts/migrate_url_map_to_aliases.py

scripts/sort_aliases.py
-----------------------

.. literalinclude:: ../scripts/sort_aliases.py
   :language: python
   :caption: scripts/sort_aliases.py

scripts/test_name_inference.py
------------------------------

.. literalinclude:: ../scripts/test_name_inference.py
   :language: python
   :caption: scripts/test_name_inference.py

src/licence_normaliser/__init__.py
----------------------------------

.. literalinclude:: ../src/licence_normaliser/__init__.py
   :language: python
   :caption: src/licence_normaliser/__init__.py

src/licence_normaliser/_cache.py
--------------------------------

.. literalinclude:: ../src/licence_normaliser/_cache.py
   :language: python
   :caption: src/licence_normaliser/_cache.py

src/licence_normaliser/_core.py
-------------------------------

.. literalinclude:: ../src/licence_normaliser/_core.py
   :language: python
   :caption: src/licence_normaliser/_core.py

src/licence_normaliser/_models.py
---------------------------------

.. literalinclude:: ../src/licence_normaliser/_models.py
   :language: python
   :caption: src/licence_normaliser/_models.py

src/licence_normaliser/_normaliser.py
-------------------------------------

.. literalinclude:: ../src/licence_normaliser/_normaliser.py
   :language: python
   :caption: src/licence_normaliser/_normaliser.py

src/licence_normaliser/_trace.py
--------------------------------

.. literalinclude:: ../src/licence_normaliser/_trace.py
   :language: python
   :caption: src/licence_normaliser/_trace.py

src/licence_normaliser/cli/__init__.py
--------------------------------------

.. literalinclude:: ../src/licence_normaliser/cli/__init__.py
   :language: python
   :caption: src/licence_normaliser/cli/__init__.py

src/licence_normaliser/cli/_main.py
-----------------------------------

.. literalinclude:: ../src/licence_normaliser/cli/_main.py
   :language: python
   :caption: src/licence_normaliser/cli/_main.py

src/licence_normaliser/data/README.rst
--------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/README.rst
   :language: rst
   :caption: src/licence_normaliser/data/README.rst

src/licence_normaliser/data/aliases/aliases.json
------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/aliases/aliases.json
   :language: json
   :caption: src/licence_normaliser/data/aliases/aliases.json

src/licence_normaliser/data/creativecommons/creativecommons.json
----------------------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/creativecommons/creativecommons.json
   :language: json
   :caption: src/licence_normaliser/data/creativecommons/creativecommons.json

src/licence_normaliser/data/opendefinition/opendefinition.json
--------------------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/opendefinition/opendefinition.json
   :language: json
   :caption: src/licence_normaliser/data/opendefinition/opendefinition.json

src/licence_normaliser/data/osi/osi.json
----------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/osi/osi.json
   :language: json
   :caption: src/licence_normaliser/data/osi/osi.json

src/licence_normaliser/data/prose/prose_patterns.json
-----------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/prose/prose_patterns.json
   :language: json
   :caption: src/licence_normaliser/data/prose/prose_patterns.json

src/licence_normaliser/data/scancode_licensedb/scancode_licensedb.json
----------------------------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/scancode_licensedb/scancode_licensedb.json
   :language: json
   :caption: src/licence_normaliser/data/scancode_licensedb/scancode_licensedb.json

src/licence_normaliser/data/spdx/spdx.json
------------------------------------------

.. literalinclude:: ../src/licence_normaliser/data/spdx/spdx.json
   :language: json
   :caption: src/licence_normaliser/data/spdx/spdx.json

src/licence_normaliser/defaults.py
----------------------------------

.. literalinclude:: ../src/licence_normaliser/defaults.py
   :language: python
   :caption: src/licence_normaliser/defaults.py

src/licence_normaliser/exceptions.py
------------------------------------

.. literalinclude:: ../src/licence_normaliser/exceptions.py
   :language: python
   :caption: src/licence_normaliser/exceptions.py

src/licence_normaliser/parsers/__init__.py
------------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/__init__.py
   :language: python
   :caption: src/licence_normaliser/parsers/__init__.py

src/licence_normaliser/parsers/alias.py
---------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/alias.py
   :language: python
   :caption: src/licence_normaliser/parsers/alias.py

src/licence_normaliser/parsers/creativecommons.py
-------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/creativecommons.py
   :language: python
   :caption: src/licence_normaliser/parsers/creativecommons.py

src/licence_normaliser/parsers/opendefinition.py
------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/opendefinition.py
   :language: python
   :caption: src/licence_normaliser/parsers/opendefinition.py

src/licence_normaliser/parsers/osi.py
-------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/osi.py
   :language: python
   :caption: src/licence_normaliser/parsers/osi.py

src/licence_normaliser/parsers/prose.py
---------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/prose.py
   :language: python
   :caption: src/licence_normaliser/parsers/prose.py

src/licence_normaliser/parsers/scancode_licensedb.py
----------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/scancode_licensedb.py
   :language: python
   :caption: src/licence_normaliser/parsers/scancode_licensedb.py

src/licence_normaliser/parsers/spdx.py
--------------------------------------

.. literalinclude:: ../src/licence_normaliser/parsers/spdx.py
   :language: python
   :caption: src/licence_normaliser/parsers/spdx.py

src/licence_normaliser/plugins.py
---------------------------------

.. literalinclude:: ../src/licence_normaliser/plugins.py
   :language: python
   :caption: src/licence_normaliser/plugins.py

src/licence_normaliser/tests/__init__.py
----------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/__init__.py
   :language: python
   :caption: src/licence_normaliser/tests/__init__.py

src/licence_normaliser/tests/conftest.py
----------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/conftest.py
   :language: python
   :caption: src/licence_normaliser/tests/conftest.py

src/licence_normaliser/tests/test_alias_expansion.py
----------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_alias_expansion.py
   :language: python
   :caption: src/licence_normaliser/tests/test_alias_expansion.py

src/licence_normaliser/tests/test_aliases.py
--------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_aliases.py
   :language: python
   :caption: src/licence_normaliser/tests/test_aliases.py

src/licence_normaliser/tests/test_cache.py
------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_cache.py
   :language: python
   :caption: src/licence_normaliser/tests/test_cache.py

src/licence_normaliser/tests/test_cli.py
----------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_cli.py
   :language: python
   :caption: src/licence_normaliser/tests/test_cli.py

src/licence_normaliser/tests/test_core.py
-----------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_core.py
   :language: python
   :caption: src/licence_normaliser/tests/test_core.py

src/licence_normaliser/tests/test_exceptions.py
-----------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_exceptions.py
   :language: python
   :caption: src/licence_normaliser/tests/test_exceptions.py

src/licence_normaliser/tests/test_integration.py
------------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_integration.py
   :language: python
   :caption: src/licence_normaliser/tests/test_integration.py

src/licence_normaliser/tests/test_models.py
-------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_models.py
   :language: python
   :caption: src/licence_normaliser/tests/test_models.py

src/licence_normaliser/tests/test_prose.py
------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_prose.py
   :language: python
   :caption: src/licence_normaliser/tests/test_prose.py

src/licence_normaliser/tests/test_trace.py
------------------------------------------

.. literalinclude:: ../src/licence_normaliser/tests/test_trace.py
   :language: python
   :caption: src/licence_normaliser/tests/test_trace.py
