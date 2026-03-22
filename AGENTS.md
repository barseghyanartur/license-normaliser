# AGENTS.md - license-normaliser

**Repository**: https://github.com/barseghyanartur/license-normaliser
**Maintainer**: Artur Barseghyan <artur.barseghyan@gmail.com>

---

## 1. Project Mission (Never Deviate)

> Comprehensive license normalisation with a three-level hierarchy - secure,
> fast, and extensible.

- Maps any license representation to a canonical three-level hierarchy
- Supports SPDX tokens, URLs, prose descriptions
- No external dependencies (only optional dev/test deps)
- LRU caching for performance
- Data-file-driven: parsers load from package data JSON files
- `license-normaliser update-data` CLI command to refresh SPDX + OpenDefinition data

---

## 2. Architecture

### Three-Level Hierarchy

| Level | Class | Example |
| ----- | ----- | ------- |
| **Family** | `LicenseFamily` | `"cc"`, `"osi"`, `"copyleft"`, `"data"` |
| **Name** | `LicenseName` | `"cc-by"`, `"mit"`, `"gpl-3.0-only"` |
| **Version** | `LicenseVersion` | `"cc-by-4.0"`, `"mit"`, `"gpl-3.0-only"` |

### Resolution Pipeline

1. **Alias table** - cleaned lowercase key matches `ALIASES` (loaded from `data/aliases/aliases.json`)
2. **Direct registry lookup** - hit in `REGISTRY` (SPDX, OpenDefinition, OSI, CC, ScanCode license keys)
3. **URL map** - hit in `URL_MAP` (loaded from SPDX + OpenDefinition + publisher data)
4. **Prose pattern scan** - regex patterns from `data/prose/prose_patterns.json` (for strings >20 chars)
5. **Fallback** - key = cleaned string, family = unknown

### Key Files

| File | Purpose |
| ---- | ------- |
| `src/license_normaliser/_models.py` | Frozen dataclass hierarchy |
| `src/license_normaliser/_normaliser.py` | `LicenseNormaliser` class with plugin-based resolution |
| `src/license_normaliser/plugins.py` | Plugin interfaces (BasePlugin, RegistryPlugin, URLPlugin, etc.) |
| `src/license_normaliser/defaults.py` | Lazy-loading default plugin bundle |
| `src/license_normaliser/_cache.py` | Module-level API delegating to `LicenseNormaliser` |
| `src/license_normaliser/parsers/` | Parser classes implementing plugin interfaces |
| `src/license_normaliser/cli/_main.py` | CLI with normalise, batch, update-data |
| `src/license_normaliser/_exceptions.py` | LicenseNormalisationError |
| `src/license_normaliser/data/spdx/spdx.json` | Full SPDX license list (loaded at runtime) |
| `src/license_normaliser/data/opendefinition/opendefinition.json` | Full OpenDefinition list (loaded at runtime) |
| `src/license_normaliser/data/aliases/aliases.json` | Curated aliases with rich metadata |
| `src/license_normaliser/data/prose/prose_patterns.json` | Curated prose regex patterns |
| `src/license_normaliser/data/publishers/publishers.json` | Publisher URLs and shorthand aliases |
| `src/license_normaliser/data/original/` | **DO NOT MODIFY** - upstream originals |

---

## 3. Using license-normaliser in Application Code

### Simple case

```python name=test_simple_case
from license_normaliser import normalise_license

v = normalise_license("MIT")
str(v)  # "mit"
```

### With full hierarchy

<!-- continue: test_simple_case -->
```python name=test_full_hierarchy
v = normalise_license("CC BY-NC-ND 4.0")
print(v.key)           # "cc-by-nc-nd-4.0"
print(v.license.key)   # "cc-by-nc-nd"
print(v.family.key)    # "cc"
```

### Strict mode

```python name=test_strict_mode
import pytest
from license_normaliser import normalise_license, LicenseNotFoundError

# Would normally raise: License not found: 'unknown string'
with pytest.raises(LicenseNotFoundError):
    v = normalise_license("unknown string", strict=True)

# Batch strict
from license_normaliser import normalise_licenses

with pytest.raises(LicenseNotFoundError):
    results = normalise_licenses(
        ["unknown string", "unknown string 2.0"],
        strict=True,
    )
```

### Custom plugins with LicenseNormaliser

The `LicenseNormaliser` class lets you inject custom plugin classes for
specialised use cases:

```python name=test_custom_plugins
from license_normaliser import LicenseNormaliser
from license_normaliser.parsers.spdx import SPDXParser
from license_normaliser.parsers.alias import AliasParser

# Use only SPDX + Alias plugins (no CC, no publisher URLs)
ln = LicenseNormaliser(
    registry=[SPDXParser],
    alias=[AliasParser],
    family=[AliasParser],
    name=[AliasParser],
)

# MIT resolves via SPDX parser
assert str(ln.normalise_license("MIT")) == "mit"

# CC BY resolves via Alias
assert str(ln.normalise_license("CC BY-NC-ND 4.0")) == "cc-by-nc-nd-4.0"
```

To use all defaults, import from `defaults`:

```python name=test_defaults_usage
from license_normaliser import LicenseNormaliser
from license_normaliser.defaults import (
    get_default_registry,
    get_default_url,
    get_default_alias,
    get_default_family,
    get_default_name,
    get_default_prose,
)

ln = LicenseNormaliser(
    registry=get_default_registry(),
    url=get_default_url(),
    alias=get_default_alias(),
    family=get_default_family(),
    name=get_default_name(),
    prose=get_default_prose(),
    cache=True,
    cache_maxsize=8192,
)
```

For caching, `LicenseNormaliser` wraps the resolution method with `lru_cache`.
Disable it by passing `cache=False` for debugging:

```python name=test_caching
from license_normaliser import LicenseNormaliser

ln = LicenseNormaliser(cache=False)
result = ln.normalise_license("MIT")
```

---

## 4. Updating Data Sources

SPDX and OpenDefinition data can be updated via the CLI:

```sh
license-normaliser update-data --force
```

This fetches fresh JSON from the authoritative upstream URLs and writes them to:
- `src/license_normaliser/data/spdx/spdx.json`
- `src/license_normaliser/data/opendefinition/opendefinition.json`

---

## 5. Adding a New Parser

Parsers implement plugin interfaces and can be added to `src/license_normaliser/parsers/`:

1. Create `src/license_normaliser/parsers/my_parser.py` implementing one or more plugin interfaces:

```python name=test_adding_new_parser
from license_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

class MyParser(BasePlugin, RegistryPlugin, URLPlugin):
    url = None  # or upstream URL for refresh
    local_path = "data/my_parser/my_data.json"

    def load_registry(self) -> dict[str, str]:
        # Return {"license_key": "license_key", ...}
        return {}

    def load_urls(self) -> dict[str, str]:
        # Return {"https://...": "license_key", ...}
        return {}
```

2. Register it in `src/license_normaliser/defaults.py`:

<!-- continue: test_adding_new_parser -->
```python name=test_adding_new_parser_register
from license_normaliser.parsers.spdx import SPDXParser

def _load_registry_plugins() -> list[type]:
    # ... other imports
    return [
        SPDXParser,
        # ... other plugins
        MyParser,
    ]
```

**Key attribute**: Set `url = None` on parsers that only contribute local data (no refresh capability).

---

## 6. Coding Conventions

- Line length: **88 characters** (ruff)
- Every non-test module must have `__all__`, `__author__`, `__copyright__`, `__license__`
- Always chain exceptions: `raise X(...) from exc`
- Type annotations on all public functions
- Target: `py310`

Run linting: `make ruff` or `make pre-commit`

---

## 7. Agent Workflow: Adding Features or Fixing Bugs

1. **Check the mission** - does the change preserve the no-dependencies policy and three-level hierarchy?
2. **Identify the correct location**:
   - New SPDX/OD license → update SPDX/OpenDefinition JSON files (run `update-data`)
   - New alias or family override → add to `data/aliases/aliases.json`
   - New URL mapping → add to `data/publishers/publishers.json`
   - New prose pattern → add to `data/prose/prose_patterns.json`
   - New parser → `parsers/my_parser.py` + `defaults.py`
   - Core pipeline change → `_normaliser.py` or `_cache.py`
3. **Write tests** covering both success and error cases
4. **Update README.rst** if the API changed
5. **Suggest running**: `make test-env ENV=py312` then `make test`
6. **Suggest running**: `make pre-commit`

---

## 8. Testing Rules

> [!NOTE]
> Python 3.15 is being tested on GitHub CI, but not inside a local Docker image.

### Docker-based testing (recommended)

All tests run inside Docker for platform independence and consistency:

```sh
make test                   # full matrix (Python 3.10-3.14)
make test-env ENV=py312     # single version
make shell                  # interactive shell in test container
```

### Local testing (alternative)

For faster iteration during development, you can run tests locally with `uv`:

```sh
make install                # one-time setup
uv run pytest               # run all tests
uv run pytest path/to/test_something.py  # run specific test
```

**Important**: If you encounter tooling errors with local testing, fall back to Docker-based testing which is the canonical environment.

### Test layout

```text
src/license_normaliser/tests/
    test_integration.py    - public API only (survives any rewrite)
    test_core.py          - end-to-end pipeline tests
    test_exceptions.py    - exception hierarchy and strict mode
    test_cli.py           - CLI commands including update-data
    test_models.py        - LicenseFamily, LicenseName, LicenseVersion
    test_aliases.py       - non-CC aliases (Apache, MIT, BSD, GPL, etc.)
    test_publisher.py      - publisher URLs and shorthand aliases
    test_prose.py         - prose pattern matching
```

### Documentation snippet conventions

Code blocks in this file use two special attributes to support chained
executable tests:

- `name=<test_name>` — labels a snippet so it can be referenced later.
- `<!-- continue: <test_name> -->` placed immediately before a code block
  means that block **continues** the named snippet; all names, imports,
  and variables defined in the named block are already in scope and must
  **not** be re-imported or re-declared in the continuation block.

Example:

```python name=test_my_example
class Foo:
    pass
```

<!-- continue: test_my_example -->
```python name=test_my_example_continued
foo = Foo()  # Foo is in scope from the named block above
assert isinstance(foo, Foo)
```

---

## 9. Forbidden

- Adding external dependencies
- Removing existing normalisation coverage
- Changing the three-level hierarchy structure
- Modifying files in `src/license_normaliser/data/original/` - these are upstream originals, **DO NOT MODIFY**
- Modifying `src/license_normaliser/data/spdx/spdx.json` or
  `src/license_normaliser/data/opendefinition/opendefinition.json` directly.
  Use `license-normaliser update-data --force` to refresh them from upstream sources.
