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

1. **Direct registry lookup** - cleaned lowercase key matches `REGISTRY`
2. **Alias table** - hit in `ALIASES` dict (loaded from `data/aliases/aliases.json`)
3. **URL map** - hit in `URL_MAP` (loaded from SPDX + OpenDefinition + publisher data)
4. **Prose pattern scan** - regex patterns from `data/prose/prose_patterns.json` (for strings >20 chars)
5. **Fallback** - key = cleaned string, family = unknown

### Key Files

| File | Purpose |
| ---- | ------- |
| `src/license_normaliser/_models.py` | Frozen dataclass hierarchy |
| `src/license_normaliser/_registry.py` | REGISTRY, URL_MAP, ALIASES, FAMILY_OVERRIDES built from parsers |
| `src/license_normaliser/_cache.py` | LRU caching + strict mode + prose pattern step |
| `src/license_normaliser/parsers/` | Pluggable parser package (SPDX, OpenDefinition, OSI, CC, ScanCode, Alias, Prose, Publisher) |
| `src/license_normaliser/cli/_main.py` | CLI with normalise, batch, update-data |
| `src/license_normaliser/_exceptions.py` | LicenseNormalisationError |
| `src/license_normaliser/data/spdx/spdx.json` | Full SPDX license list (loaded at runtime) |
| `src/license_normaliser/data/opendefinition/opendefinition.json` | Full OpenDefinition list (loaded at runtime) |
| `src/license_normaliser/data/aliases/aliases.json` | Curated aliases with rich metadata |
| `src/license_normaliser/data/urls/url_map.json` | Curated URL-to-metadata mappings |
| `src/license_normaliser/data/prose/prose_patterns.json` | Curated prose regex patterns |
| `src/license_normaliser/data/publishers/publishers.json` | Publisher URLs and shorthand aliases |
| `src/license_normaliser/data/original/` | **DO NOT MODIFY** - upstream originals |

---

## 3. Using license-normaliser in Application Code

### Simple case

```python
from license_normaliser import normalise_license

v = normalise_license("MIT")
str(v)  # "mit"
```

### With full hierarchy

```python
v = normalise_license("CC BY-NC-ND 4.0")
print(v.key)           # "cc-by-nc-nd-4.0"
print(v.license.key)   # "cc-by-nc-nd"
print(v.family.key)    # "cc"
```

### Strict mode

```python
from license_normaliser import normalise_license, LicenseNormalisationError

try:
    v = normalise_license("unknown string", strict=True)
except LicenseNormalisationError as exc:
    print(exc)  # License not found: 'unknown string'

# Batch strict
from license_normaliser import normalise_licenses
results = normalise_licenses(["MIT", "Apache-2.0"], strict=True)
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

Parsers implement `BaseParser` and can be added to `src/license_normaliser/parsers/`:

1. Create `src/license_normaliser/parsers/my_parser.py` implementing `BaseParser`:

```python name=test_adding_new_parser
from license_normaliser.parsers.base import BaseParser

class MyParser(BaseParser):
    url = None  # or upstream URL for refresh
    local_path = "data/my_parser/my_data.json"
    is_registry_entry = True  # False for alias-only parsers

    def parse(self) -> list[tuple[str, dict]]:
        # Return [(license_id, {"url": "...", "name": "..."}), ...]
        return []
```

2. Register it in `src/license_normaliser/parsers/__init__.py`:

```python
def get_parsers() -> list[BaseParser]:
    return [
        SPDXParser(),
        OpenDefinitionParser(),
        OSIParser(),
        ScanCodeLicenseDBParser(),
        CreativeCommonsParser(),
        ProseParser(),
        AliasParser(),
        PublisherParser(),
        MyParser(),
    ]
```

**Key attribute**: Set `is_registry_entry = False` on parsers that only contribute aliases/URLs/patterns (not new license keys) to avoid polluting the REGISTRY.

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
   - New URL mapping → add to `data/urls/url_map.json` or `data/publishers/publishers.json`
   - New prose pattern → add to `data/prose/prose_patterns.json`
   - New parser → `parsers/my_parser.py` + `parsers/__init__.py`
   - Core pipeline change → `_cache.py` or `_registry.py`
3. **Write tests** covering both success and error cases
4. **Update README.rst** if the API changed
5. **Suggest running**: `make test-env ENV=py312` then `make test`
6. **Suggest running**: `make pre-commit`

---

## 8. Testing Rules

All tests run inside Docker (safest option, always available):

```sh
make test                   # full matrix (Python 3.10-3.14)
make test-env ENV=py312     # single version
```

For individual local tests, you can use `uv run pytest`.
A prerequisite is `make install` first. On tooling errors, fallback to
Docker-based testing.

### Test layout

```
src/license_normaliser/tests/
    test_integration.py    - public API only (survives any rewrite)
    test_cache.py          - caching, cleaning, strict mode
    test_exceptions.py     - exception hierarchy and strict mode
    test_cli.py            - CLI commands including update-data
    test_models.py         - LicenseFamily, LicenseName, LicenseVersion
    test_core.py           - end-to-end pipeline tests
    test_aliases.py        - non-CC aliases (Apache, MIT, BSD, GPL, etc.)
    test_publisher.py      - publisher URLs and shorthand aliases
    test_prose.py          - prose pattern matching
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
