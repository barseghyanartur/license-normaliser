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
   ├── src
   │   └── license_normaliser
   │       ├── cli
   │       │   ├── __init__.py
   │       │   └── _main.py
   │       ├── data
   │       │   ├── aliases
   │       │   │   └── aliases.json
   │       │   ├── creativecommons
   │       │   │   └── creativecommons.json
   │       │   ├── opendefinition
   │       │   │   └── opendefinition.json
   │       │   ├── osi
   │       │   │   └── osi.json
   │       │   ├── prose
   │       │   │   └── prose_patterns.json
   │       │   ├── publishers
   │       │   │   └── publishers.json
   │       │   ├── scancode_licensedb
   │       │   │   └── scancode_licensedb.json
   │       │   ├── spdx
   │       │   │   └── spdx.json
   │       │   ├── urls
   │       │   │   └── url_map.json
   │       │   └── README.rst
   │       ├── parsers
   │       │   ├── __init__.py
   │       │   ├── alias.py
   │       │   ├── base.py
   │       │   ├── creativecommons.py
   │       │   ├── opendefinition.py
   │       │   ├── osi.py
   │       │   ├── prose.py
   │       │   ├── publisher.py
   │       │   ├── scancode_licensedb.py
   │       │   └── spdx.py
   │       ├── tests
   │       │   ├── __init__.py
   │       │   ├── conftest.py
   │       │   ├── test_aliases.py
   │       │   ├── test_cli.py
   │       │   ├── test_core.py
   │       │   ├── test_exceptions.py
   │       │   ├── test_integration.py
   │       │   ├── test_models.py
   │       │   ├── test_prose.py
   │       │   └── test_publisher.py
   │       ├── __init__.py
   │       ├── _cache.py
   │       ├── _core.py
   │       ├── _exceptions.py
   │       ├── _models.py
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
   ├── tox.ini
   └── uv.lock

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

src/license_normaliser/_exceptions.py
-------------------------------------

.. literalinclude:: ../src/license_normaliser/_exceptions.py
   :language: python
   :caption: src/license_normaliser/_exceptions.py

src/license_normaliser/_models.py
---------------------------------

.. literalinclude:: ../src/license_normaliser/_models.py
   :language: python
   :caption: src/license_normaliser/_models.py

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

src/license_normaliser/data/README.rst
--------------------------------------

.. literalinclude:: ../src/license_normaliser/data/README.rst
   :language: rst
   :caption: src/license_normaliser/data/README.rst

src/license_normaliser/data/aliases/aliases.json
------------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/aliases/aliases.json
   :language: json
   :caption: src/license_normaliser/data/aliases/aliases.json

src/license_normaliser/data/creativecommons/creativecommons.json
----------------------------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/creativecommons/creativecommons.json
   :language: json
   :caption: src/license_normaliser/data/creativecommons/creativecommons.json

src/license_normaliser/data/opendefinition/opendefinition.json
--------------------------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/opendefinition/opendefinition.json
   :language: json
   :caption: src/license_normaliser/data/opendefinition/opendefinition.json

src/license_normaliser/data/osi/osi.json
----------------------------------------

.. literalinclude:: ../src/license_normaliser/data/osi/osi.json
   :language: json
   :caption: src/license_normaliser/data/osi/osi.json

src/license_normaliser/data/prose/prose_patterns.json
-----------------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/prose/prose_patterns.json
   :language: json
   :caption: src/license_normaliser/data/prose/prose_patterns.json

src/license_normaliser/data/publishers/publishers.json
------------------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/publishers/publishers.json
   :language: json
   :caption: src/license_normaliser/data/publishers/publishers.json

src/license_normaliser/data/scancode_licensedb/scancode_licensedb.json
----------------------------------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/scancode_licensedb/scancode_licensedb.json
   :language: json
   :caption: src/license_normaliser/data/scancode_licensedb/scancode_licensedb.json

src/license_normaliser/data/spdx/spdx.json
------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/spdx/spdx.json
   :language: json
   :caption: src/license_normaliser/data/spdx/spdx.json

src/license_normaliser/data/urls/url_map.json
---------------------------------------------

.. literalinclude:: ../src/license_normaliser/data/urls/url_map.json
   :language: json
   :caption: src/license_normaliser/data/urls/url_map.json

src/license_normaliser/exceptions.py
------------------------------------

.. literalinclude:: ../src/license_normaliser/exceptions.py
   :language: python
   :caption: src/license_normaliser/exceptions.py

src/license_normaliser/parsers/__init__.py
------------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/__init__.py
   :language: python
   :caption: src/license_normaliser/parsers/__init__.py

src/license_normaliser/parsers/alias.py
---------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/alias.py
   :language: python
   :caption: src/license_normaliser/parsers/alias.py

src/license_normaliser/parsers/base.py
--------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/base.py
   :language: python
   :caption: src/license_normaliser/parsers/base.py

src/license_normaliser/parsers/creativecommons.py
-------------------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/creativecommons.py
   :language: python
   :caption: src/license_normaliser/parsers/creativecommons.py

src/license_normaliser/parsers/opendefinition.py
------------------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/opendefinition.py
   :language: python
   :caption: src/license_normaliser/parsers/opendefinition.py

src/license_normaliser/parsers/osi.py
-------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/osi.py
   :language: python
   :caption: src/license_normaliser/parsers/osi.py

src/license_normaliser/parsers/prose.py
---------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/prose.py
   :language: python
   :caption: src/license_normaliser/parsers/prose.py

src/license_normaliser/parsers/publisher.py
-------------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/publisher.py
   :language: python
   :caption: src/license_normaliser/parsers/publisher.py

src/license_normaliser/parsers/scancode_licensedb.py
----------------------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/scancode_licensedb.py
   :language: python
   :caption: src/license_normaliser/parsers/scancode_licensedb.py

src/license_normaliser/parsers/spdx.py
--------------------------------------

.. literalinclude:: ../src/license_normaliser/parsers/spdx.py
   :language: python
   :caption: src/license_normaliser/parsers/spdx.py

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

src/license_normaliser/tests/test_aliases.py
--------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_aliases.py
   :language: python
   :caption: src/license_normaliser/tests/test_aliases.py

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

src/license_normaliser/tests/test_exceptions.py
-----------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_exceptions.py
   :language: python
   :caption: src/license_normaliser/tests/test_exceptions.py

src/license_normaliser/tests/test_integration.py
------------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_integration.py
   :language: python
   :caption: src/license_normaliser/tests/test_integration.py

src/license_normaliser/tests/test_models.py
-------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_models.py
   :language: python
   :caption: src/license_normaliser/tests/test_models.py

src/license_normaliser/tests/test_prose.py
------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_prose.py
   :language: python
   :caption: src/license_normaliser/tests/test_prose.py

src/license_normaliser/tests/test_publisher.py
----------------------------------------------

.. literalinclude:: ../src/license_normaliser/tests/test_publisher.py
   :language: python
   :caption: src/license_normaliser/tests/test_publisher.py
