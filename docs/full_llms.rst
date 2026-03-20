Full project source-tree
========================

Below is the layout of the project (to 10 levels), followed by
the contents of each key file.

.. code-block:: text
   :caption: Project directory layout

    license-normaliser/
    ├── data
    │   ├── aliases/aliases.json
    │   ├── urls/url_map.json
    │   ├── prose/prose_patterns.json
    │   ├── spdx/spdx-licenses.json         (curated subset)
    │   ├── opendefinition/opendefinition_licenses_all.json  (curated subset)
    │   ├── spdx-licenses.json               (upstream originals)
    │   └── opendefinition_licenses_all.json
    ├── docs
    │   ├── conf.py
    │   └── full_llms.rst
    ├── src
    │   └── license_normaliser
    │       ├── cli
    │       │   ├── __init__.py
    │       │   └── _main.py
    │       ├── data_sources
    │       │   ├── __init__.py
    │       │   ├── builtin_aliases.py
    │       │   ├── builtin_prose.py
    │       │   ├── builtin_urls.py
    │       │   ├── opendefinition.py
    │       │   └── spdx.py
    │       ├── tests
    │       │   ├── __init__.py
    │       │   ├── conftest.py
    │       │   ├── test_cache.py
    │       │   ├── test_cli.py
    │       │   ├── test_core.py
    │       │   ├── test_data_sources.py
    │       │   ├── test_exceptions.py
    │       │   ├── test_models.py
    │       │   ├── test_pipeline.py
    │       │   └── test_registry.py
    │       ├── __init__.py
    │       ├── _cache.py
    │       ├── _core.py
    │       ├── _models.py
    │       ├── _pipeline.py
    │       ├── _registry.py
    │       ├── exceptions.py
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

data/opendefinition_licenses_all.json
------------------------------------

.. literalinclude:: ../data/opendefinition_licenses_all.json
   :language: json
   :caption: data/opendefinition_licenses_all.json

data/spdx-licenses.json
-----------------------

.. literalinclude:: ../data/spdx-licenses.json
   :language: json
   :caption: data/spdx-licenses.json

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

src/license_normaliser/__init__.py
----------------------------------

.. literalinclude:: ../src/license_normaliser/__init__.py
   :language: python
   :caption: src/license_normaliser/__init__.py

src/license_normaliser/_cache.py
--------------------------------

.. literalinclude:: ../src/license_normaliser/_cache.py
   :language: python
   :caption: src/license_normaliser/_cache.py

src/license_normaliser/_core.py
-------------------------------

.. literalinclude:: ../src/license_normaliser/_core.py
   :language: python
   :caption: src/license_normaliser/_core.py

src/license_normaliser/_enums.py
--------------------------------

.. literalinclude:: ../src/license_normaliser/_enums.py
   :language: python
   :caption: src/license_normaliser/_enums.py

src/license_normaliser/_models.py
---------------------------------

.. literalinclude:: ../src/license_normaliser/_models.py
   :language: python
   :caption: src/license_normaliser/_models.py

src/license_normaliser/_pipeline.py
-----------------------------------

.. literalinclude:: ../src/license_normaliser/_pipeline.py
   :language: python
   :caption: src/license_normaliser/_pipeline.py

src/license_normaliser/_registry.py
-----------------------------------

.. literalinclude:: ../src/license_normaliser/_registry.py
   :language: python
   :caption: src/license_normaliser/_registry.py

src/license_normaliser/cli/__init__.py
--------------------------------------

.. literalinclude:: ../src/license_normaliser/cli/__init__.py
   :language: python
   :caption: src/license_normaliser/cli/__init__.py

src/license_normaliser/cli/_main.py
-----------------------------------

.. literalinclude:: ../src/license_normaliser/cli/_main.py
   :language: python
   :caption: src/license_normaliser/cli/_main.py

src/license_normaliser/tests/__init__.py
----------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/__init__.py
   :language: python
   :caption: src/license_normaliser/tests/__init__.py

src/license_normaliser/tests/conftest.py
----------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/conftest.py
   :language: python
   :caption: src/license_normaliser/tests/conftest.py

src/license_normaliser/tests/test_cache.py
------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_cache.py
   :language: python
   :caption: src/license_normaliser/tests/test_cache.py

src/license_normaliser/tests/test_cli.py
----------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_cli.py
   :language: python
   :caption: src/license_normaliser/tests/test_cli.py

src/license_normaliser/tests/test_core.py
-----------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_core.py
   :language: python
   :caption: src/license_normaliser/tests/test_core.py

src/license_normaliser/tests/test_models.py
-------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_models.py
   :language: python
   :caption: src/license_normaliser/tests/test_models.py

src/license_normaliser/tests/test_pipeline.py
---------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_pipeline.py
   :language: python
   :caption: src/license_normaliser/tests/test_pipeline.py

src/license_normaliser/tests/test_registry.py
---------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_registry.py
   :language: python
   :caption: src/license_normaliser/tests/test_registry.py
