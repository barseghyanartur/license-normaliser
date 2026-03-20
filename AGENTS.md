# AGENTS.md - license-normaliser

**Package version**: 0.3.0
**Repository**: https://github.com/barseghyanartur/license-normaliser
**Maintainer**: Artur Barseghyan <artur.barseghyan@gmail.com>

---

## 1. Project Mission (Never Deviate)

> Comprehensive license normalisation with a three-level hierarchy - secure,
> fast, and extensible.

- Maps any license representation to a canonical three-level hierarchy
- Supports SPDX tokens, URLs, and prose descriptions
- No external dependencies (only optional dev/test deps)
- LRU caching for performance
- Data-file-driven: parsers load from package data JSON files
- `license-normaliser update-data` CLI command to refresh SPDX + OpenDefinition data

---

## 2. Architecture

### Three-Level Hierarchy

| Level | Class | Example |
|-------|-------|---------|
| **Family** | `LicenseFamily` | `"cc"`, `"osi"`, `"copyleft"`, `"data"` |
| **Name** | `LicenseName` | `"cc-by"`, `"mit"`, `"gpl-3.0-only"` |
| **Version** | `LicenseVersion` | `"cc-by-4.0"`, `"mit"`, `"gpl-3.0-only"` |

### Resolution Pipeline

1. **Direct registry lookup** - cleaned lowercase key matches `REGISTRY`
2. **Alias table** - hit in `ALIASES` dict (built-in CC aliases)
3. **URL map** - hit in `URL_MAP` (loaded from SPDX + OpenDefinition data)
4. **Fallback** - key = cleaned string, family = unknown

### Key Files

| File | Purpose |
|------|---------|
| `src/license_normaliser/_models.py` | Frozen dataclass hierarchy |
| `src/license_normaliser/_registry.py` | REGISTRY, URL_MAP, ALIASES built from parsers |
| `src/license_normaliser/_cache.py` | LRU caching + strict mode |
| `src/license_normaliser/parsers/` | Pluggable parser package (SPDX, OpenDefinition) |
| `src/license_normaliser/cli/_main.py` | CLI with normalise, batch, update-data |
| `src/license_normaliser/_exceptions.py` | LicenseNormalisationError |
| `src/license_normaliser/data/spdx/spdx-licenses.json` | Curated SPDX subset |
| `src/license_normaliser/data/opendefinition/opendefinition_licenses_all.json` | Curated OD subset |
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
- `src/license_normaliser/data/spdx/spdx-licenses.json`
- `src/license_normaliser/data/opendefinition/opendefinition_licenses_all.json`

**Important**: The files in `src/license_normaliser/data/original/` are **DO NOT MODIFY** -
they are the upstream originals preserved for reference.

---

## 5. Adding a New Parser

1. Create `src/license_normaliser/parsers/my_parser.py` implementing `BaseParser`:

```python
from .base import BaseParser

class MyParser(BaseParser):
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
        MyParser(),
    ]
```

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
   - New SPDX/OD license → update curated JSON files (then re-run `update-data` to refresh)
   - New CC alias → add to `_registry.py` `_build_aliases()` function
   - New parser → `parsers/my_parser.py` + `parsers/__init__.py`
   - Core pipeline change → `_cache.py`
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
```

---

## 9. Forbidden

- Adding external dependencies
- Removing existing normalisation coverage
- Changing the three-level hierarchy structure
- Modifying files in `src/license_normaliser/data/original/` - these are upstream originals, **DO NOT MODIFY**
- Modifying the curated SPDX and OpenDefinition subset files:
  `src/license_normaliser/data/spdx/spdx-licenses.json` and
  `src/license_normaliser/data/opendefinition/opendefinition_licenses_all.json`
  directly. Use `license-normaliser update-data --force` to refresh them
  from upstream sources.
