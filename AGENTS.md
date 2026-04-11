# AGENTS.md - licence-normaliser

**Repository**: <https://github.com/barseghyanartur/licence-normaliser>
**Maintainer**: Artur Barseghyan <artur.barseghyan@gmail.com>

---

## 1. Project mission (never deviate)

> Robust licence normalisation with a three-level hierarchy for common SPDX,
> Creative Commons, OSI-approved, ScanCode, and publisher licences - secure,
> fast, and extensible.

- Maps common licence representations (SPDX tokens, URLs, prose descriptions)
  to a canonical three-level hierarchy
- Supports SPDX tokens, URLs, prose descriptions
- No external dependencies (only optional dev/test deps)
- LRU caching for performance
- Data-file-driven: parsers load from package data JSON files
- `licence-normaliser update-data` CLI command to refresh SPDX + OpenDefinition data

**Scope note**: The library covers the most common open-source, Creative
Commons, and major-publisher licences. Any licence string not present in the
curated data or upstream registries resolves to an "unknown" result (or raises
in strict mode). Brand-new licence keys require updating upstream data sources
first.

---

## 2. Architecture

### Three-level hierarchy

| Level | Class | Example |
| ----- | ----- | ------- |
| **Family** | `LicenceFamily` | `"cc"`, `"osi"`, `"copyleft"`, `"data"` |
| **Name** | `LicenceName` | `"cc-by"`, `"mit"`, `"gpl-3.0-only"` |
| **Version** | `LicenceVersion` | `"cc-by-4.0"`, `"mit"`, `"gpl-3.0-only"` |

`LicenceVersion` also has optional `jurisdiction` (e.g., `"uk"`, `"au"`) and `scope` (e.g., `"igo"`) fields for CC licences.

### Resolution pipeline

1. **Alias table** - cleaned lowercase key matches `ALIASES` (loaded from `data/aliases/aliases.json`)
2. **Direct registry lookup** - hit in `REGISTRY` (SPDX, OpenDefinition, OSI, CC, ScanCode licence keys)
3. **URL map** - hit in `URL_MAP` (loaded from SPDX + OpenDefinition + publisher data)
4. **Prose pattern scan** - regex patterns from `data/prose/prose_patterns.json` (for strings >20 chars)
5. **Fallback** - key = cleaned string, family = unknown

### Key files

| File | Purpose |
| ---- | ------- |
| `src/licence_normaliser/_models.py` | Frozen dataclass hierarchy |
| `src/licence_normaliser/_normaliser.py` | `LicenceNormaliser` class with plugin-based resolution |
| `src/licence_normaliser/plugins.py` | Plugin interfaces (BasePlugin, RegistryPlugin, URLPlugin, etc.) |
| `src/licence_normaliser/defaults.py` | Lazy-loading default plugin bundle |
| `src/licence_normaliser/_cache.py` | Module-level API delegating to `LicenceNormaliser` |
| `src/licence_normaliser/parsers/` | Parser classes implementing plugin interfaces |
| `src/licence_normaliser/cli/_main.py` | CLI with normalise, batch, update-data |
| `src/licence_normaliser/exceptions.py` | Exception hierarchy: LicenceNormaliserError (base), LicenceNotFoundError, DataSourceError |
| `src/licence_normaliser/_trace.py` | `LicenceTrace`, `LicenceTraceStage` for resolution tracing |
| `src/licence_normaliser/data/spdx/spdx.json` | **DO NOT MODIFY** Full SPDX licence list (loaded at runtime) |
| `src/licence_normaliser/data/opendefinition/opendefinition.json` | **DO NOT MODIFY** Full OpenDefinition list (loaded at runtime) |
| `src/licence_normaliser/data/aliases/aliases.json` | Curated aliases with rich metadata (includes migrated URLs and shorthand aliases) |
| `src/licence_normaliser/data/prose/prose_patterns.json` | Curated prose regex patterns |

---

## 3. Using licence-normaliser in application code

### Simple case

```python name=test_simple_case
from licence_normaliser import normalise_licence

v = normalise_licence("MIT")
str(v)  # "mit"
```

### With full hierarchy

<!-- continue: test_simple_case -->
```python name=test_full_hierarchy
v = normalise_licence("CC BY-NC-ND 4.0")
print(v.key)           # "cc-by-nc-nd-4.0"
print(v.licence.key)   # "cc-by-nc-nd"
print(v.family.key)    # "cc"
```

### With jurisdiction and scope

CC URLs can include jurisdiction codes (e.g., `"uk"`, `"au"`) or scope (e.g., `"igo"`):

```python name=test_jurisdiction_scope
from licence_normaliser import normalise_licence

# UK jurisdiction
v = normalise_licence("http://creativecommons.org/licenses/by-nc/2.0/uk")
print(v.key)           # "cc-by-nc-2.0-uk"
print(v.jurisdiction)  # "uk"
print(v.scope)         # None

# IGO scope (International Governmental Organization)
v = normalise_licence("http://creativecommons.org/licenses/by-nc/3.0/igo")
print(v.key)           # "cc-by-nc-3.0-igo"
print(v.jurisdiction)  # None
print(v.scope)         # "igo"
```

### Strict mode

```python name=test_strict_mode
import pytest
from licence_normaliser import normalise_licence, LicenceNotFoundError, LicenceTrace, LicenceTraceStage

# Would normally raise: Licence not found: 'unknown string'
with pytest.raises(LicenceNotFoundError):
    v = normalise_licence("unknown string", strict=True)

# Batch strict
from licence_normaliser import normalise_licences

with pytest.raises(LicenceNotFoundError):
    results = normalise_licences(
        ["unknown string", "unknown string 2.0"],
        strict=True,
    )
```

### Custom plugins with LicenceNormaliser

The `LicenceNormaliser` class lets you inject custom plugin classes for
specialised use cases:

```python name=test_custom_plugins
from licence_normaliser import LicenceNormaliser
from licence_normaliser.parsers.spdx import SPDXParser
from licence_normaliser.parsers.alias import AliasParser

# Use only SPDX + Alias plugins (no CC, no publisher URLs)
ln = LicenceNormaliser(
    registry=[SPDXParser],
    alias=[AliasParser],
    family=[AliasParser],
    name=[AliasParser],
)

# MIT resolves via SPDX parser
assert str(ln.normalise_licence("MIT")) == "mit"

# CC BY resolves via Alias
assert str(ln.normalise_licence("CC BY-NC-ND 4.0")) == "cc-by-nc-nd-4.0"
```

To use all defaults, import from `defaults`:

```python name=test_defaults_usage
from licence_normaliser import LicenceNormaliser
from licence_normaliser.defaults import (
    get_default_registry,
    get_default_url,
    get_default_alias,
    get_default_family,
    get_default_name,
    get_default_prose,
)

ln = LicenceNormaliser(
    registry=get_default_registry(),
    url=get_default_url(),
    alias=get_default_alias(),
    family=get_default_family(),
    name=get_default_name(),
    prose=get_default_prose(),
    cache=True,
    cache_maxsize=8192,
)
result = ln.normalise_licence("MIT")
```

> [!NOTE]
> Explicit plugin passing is optional — `LicenceNormaliser()` automatically
> loads defaults. Use the pattern above only if you need custom plugins.

For caching, `LicenceNormaliser` wraps the resolution method with `lru_cache`.
Disable it by passing `cache=False` for debugging:

```python name=test_caching
from licence_normaliser import LicenceNormaliser

ln = LicenceNormaliser(cache=False)
result = ln.normalise_licence("MIT")
```

---

## 4. Updating Data Sources

SPDX and OpenDefinition data can be updated via the CLI:

```sh
licence-normaliser update-data --force
```

This fetches fresh JSON from the authoritative upstream URLs and writes them to:

- `src/licence_normaliser/data/spdx/spdx.json`
- `src/licence_normaliser/data/opendefinition/opendefinition.json`
- `src/licence_normaliser/data/osi/osi.json`
- `src/licence_normaliser/data/creativecommons/creativecommons.json`
- `src/licence_normaliser/data/scancode_licensedb/scancode_licensedb.json`

---

## 5. Trace / Explain

When debugging why a licence resolves a certain way, or aligning curated
data sources, use the trace feature:

**Via CLI:**

```sh
licence-normaliser normalise "MIT" --trace
licence-normaliser normalise "CC BY-NC-ND 3.0 igo" --trace
licence-normaliser batch MIT Apache --trace
```

Or via environment variable:

```sh
ENABLE_LICENCE_NORMALISER_TRACE=1 licence-normaliser normalise "MIT"
```

**Via Python:**

```python name=test_trace
from licence_normaliser import normalise_licence

v = normalise_licence("MIT", trace=True)
print(v.explain())
```

The trace shows:

- Each resolution stage attempted (alias → registry → url → prose → fallback)
- Whether it matched (✓) or didn't (-)
- Source file and line number for curated sources (aliases.json, prose_patterns.json, spdx.json, etc.)
- Final result with version_key, name_key, family_key

This is essential for:

- Understanding why a license resolves unexpectedly
- Finding the source line that defines an alias when curating data
- Debugging resolution order issues

---

## 6. Adding a new parser

Parsers implement plugin interfaces and can be added to `src/licence_normaliser/parsers/`:

1. Create `src/licence_normaliser/parsers/my_parser.py` implementing one or more plugin interfaces:

```python name=test_adding_new_parser
from licence_normaliser.plugins import BasePlugin, RegistryPlugin, URLPlugin

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

1. Register it in `src/licence_normaliser/defaults.py`:

<!-- continue: test_adding_new_parser -->
```python name=test_adding_new_parser_register
from licence_normaliser.parsers.spdx import SPDXParser

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

## 7. Coding conventions

- Line length: **88 characters** (ruff)
- Every non-test module must have `__all__`, `__author__`, `__copyright__`, `__license__`
- Always chain exceptions: `raise X(...) from exc`
- Type annotations on all public functions
- Target: `py310`
- Import statements: Avoid imports inside functions/methods unless absolutely
  necessary (e.g., breaking circular dependencies or optional runtime
  dependencies). Lazy imports harm readability and make dependencies unclear.

Run linting: `make ruff` or `make pre-commit`

---

## 8. Agent workflow: adding features or fixing bugs

1. **Check the mission** - does the change preserve the no-dependencies policy and three-level hierarchy?
2. **Identify the correct location**:
   - New SPDX/OD licence → update SPDX/OpenDefinition JSON files (run `update-data`)
   - New alias or family override → add to `data/aliases/aliases.json`
   - **Use `--trace` to find the exact line that defines an alias**
   - New URL mapping → add to `data/aliases/aliases.json` (under `urls` key)
   - New prose pattern → add to `data/prose/prose_patterns.json`
   - New parser → `parsers/my_parser.py` + `defaults.py`
   - Core pipeline change → `_normaliser.py` or `_cache.py`
3. **Write tests** covering both success and error cases
4. **Update README.rst** if the API changed
5. **MUST run**: `uv run pytest` or `make test-env ENV=py312` then `make test`
6. **MUST run**: `make pre-commit`. If fixes have not been applied automatically, fix them.

---

## 9. Testing rules

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
src/licence_normaliser/tests/
    test_integration.py     - public API only (survives any rewrite)
    test_core.py            - end-to-end pipeline tests
    test_exceptions.py      - exception hierarchy and strict mode
    test_cli.py             - CLI commands including update-data
    test_models.py          - LicenceFamily, LicenceName, LicenceVersion
    test_aliases.py         - non-CC aliases (Apache, MIT, BSD, GPL, etc.)
    test_alias_expansion.py - explicit aliases array expansion feature
    test_prose.py           - prose pattern matching
    test_trace.py           - resolution tracing and explain functionality
    test_cache.py           - caching behavior tests
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

## 10. Forbidden

- Adding external dependencies is strictly forbidden
- Removing existing normalisation coverage is strictly forbidden
- Changing the three-level hierarchy structure is strictly forbidden
- Adding end-anchors (`$` or `\Z`) to the Creative Commons URL patterns
  in `data/prose/prose_patterns.json` is strictly forbidden. These patterns
  are intentionally unanchored/prefix-matching: they extract only the base
  version key (e.g. `cc-by-sa-3.0`) and rely on `_extract_jurisdiction_and_scope()`
  in `_normaliser.py` to handle `/igo/` and two-letter jurisdiction suffixes
  separately. Anchoring them breaks the prose-fallback resolution path for all
  jurisdiction- and scope-bearing CC URLs.
- Modifying the following files is strictly forbidden:

  - `src/licence_normaliser/data/creativecommons/creativecommons.json`
  - `src/licence_normaliser/data/opendefinition/opendefinition.json`
  - `src/licence_normaliser/data/osi/osi.json`
  - `src/licence_normaliser/data/scancode_licensedb/scancode_licensedb.json`
  - `src/licence_normaliser/data/spdx/spdx.json`

  Instead, use `licence-normaliser update-data --force` command to refresh
  them from upstream sources.
