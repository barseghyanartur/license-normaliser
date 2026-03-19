# AGENTS.md – license-normaliser

**Package version**: 0.2.0
**Repository**: https://github.com/barseghyanartur/license-normaliser
**Maintainer**: Artur Barseghyan <artur.barseghyan@gmail.com>

---

## 1. Project Mission (Never Deviate)

> Comprehensive license normalisation with a three-level hierarchy – secure,
> fast, and extensible.

- Maps any license representation to a canonical three-level hierarchy
- Supports SPDX tokens, URLs, and prose descriptions
- No external dependencies (only optional dev/test deps)
- LRU caching for performance
- Data-file-driven: add synonyms by editing JSON, not Python

---

## 2. Architecture

### Three-Level Hierarchy

| Level | Class | Example |
|-------|-------|---------|
| **Family** | `LicenseFamily` | `"cc"`, `"osi"`, `"copyleft"`, `"publisher-tdm"` |
| **Name** | `LicenseName` | `"cc-by"`, `"mit"`, `"wiley-tdm"` |
| **Version** | `LicenseVersion` | `"cc-by-4.0"`, `"mit"`, `"wiley-tdm-1.1"` |

### Resolution Pipeline

1. **Direct registry lookup** – cleaned lowercase key matches a `LicenseVersionEnum` value
2. **Alias table** – hit in merged `ALIASES` dict (from `data/aliases/aliases.json` + data sources)
3. **URL map** – hit in merged `URL_MAP` dict (from `data/urls/url_map.json` + data sources)
4. **Structural CC URL regex** – any `creativecommons.org` URL not in the map
5. **Prose keyword scan** – regex patterns from `data/prose/prose_patterns.json`
6. **Fallback** – key = cleaned string, family = unknown

### Key Files

| File | Purpose |
|------|---------|
| `src/license_normaliser/_enums.py` | Source of truth for all known licenses |
| `src/license_normaliser/_registry.py` | Builds merged lookup tables from enums + data sources |
| `src/license_normaliser/data_sources/` | Pluggable data-source package |
| `src/license_normaliser/_pipeline.py` | Six-step resolution pipeline |
| `src/license_normaliser/_cache.py` | LRU caching + strict mode |
| `src/license_normaliser/exceptions.py` | Public exception hierarchy |
| `data/aliases/aliases.json` | Curated alias map |
| `data/urls/url_map.json` | Curated URL map |
| `data/prose/prose_patterns.json` | Ordered prose regex patterns |
| `data/spdx/spdx-licenses.json` | SPDX license list (auto-parsed) |
| `data/opendefinition/opendefinition_licenses_all.json` | OD license list (auto-parsed) |

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
from license_normaliser import normalise_license
from license_normaliser.exceptions import LicenseNotFoundError

try:
    v = normalise_license("unknown string", strict=True)
except LicenseNotFoundError as exc:
    print(exc.raw)      # original input
    print(exc.cleaned)  # cleaned form

# Batch strict
from license_normaliser import normalise_licenses
results = normalise_licenses(["MIT", "Apache-2.0"], strict=True)
```

---

## 4. Extending Without Python Changes

### Adding a new alias
Edit `data/aliases/aliases.json`:
```json
{ "my new alias": "existing-version-key" }
```

### Adding a new URL
Edit `data/urls/url_map.json`:
```json
{ "https://example.com/license/": "existing-version-key" }
```

### Adding a prose pattern
Edit `data/prose/prose_patterns.json` (order matters – specific before general):
```json
[
  {"pattern": "my specific phrase", "version_key": "existing-version-key"},
  ...
]
```

---

## 5. Adding a Brand-New License

1. Add enum entries to `src/license_normaliser/_enums.py`:
   - `LicenseFamilyEnum` (if the family is new)
   - `LicenseNameEnum` (with `(key, family_enum)`)
   - `LicenseVersionEnum` (with `(key, url, name_enum)`)

2. Add aliases/URLs/patterns to the JSON data files.

3. Export from `__init__.py` if needed.

4. Write tests.

---

## 6. Adding a New Data Source

1. Create `src/license_normaliser/data_sources/my_source.py`:

```python
from . import DataSource, SourceContribution
from pathlib import Path

class MySource:
    name = "my-source"

    def load(self, data_dir: Path) -> SourceContribution:
        # Read data_dir / "my_subdir" / "my_file.json"
        # Return aliases, url_map, prose dicts
        return SourceContribution(
            name=self.name,
            aliases={"some alias": "mit"},
            url_map={},
            prose={},
        )
```

2. Register it in `REGISTERED_SOURCES` (in `data_sources/__init__.py`):

```python
REGISTERED_SOURCES = [
    ...
    ("license_normaliser.data_sources.my_source", "MySource"),
]
```

All contributed values pointing to unknown version keys are **automatically
filtered and logged** – they cannot corrupt the registry.

---

## 7. Coding Conventions

- Line length: **88 characters** (ruff)
- Every non-test module must have `__all__`, `__author__`, `__copyright__`, `__license__`
- Always chain exceptions: `raise X(...) from exc`
- Type annotations on all public functions
- Target: `py310`

Run linting: `make ruff` or `make pre-commit`

---

## 8. Agent Workflow: Adding Features or Fixing Bugs

1. **Check the mission** – does the change preserve the no-dependencies policy and three-level hierarchy?
2. **Identify the correct location**:
   - New synonym for existing license → JSON data file only
   - New license → `_enums.py` + JSON data files
   - New external data source → `data_sources/my_source.py` + `REGISTERED_SOURCES`
   - Core pipeline change → `_pipeline.py`
   - New public API → `_cache.py` + `__init__.py`
3. **For bug fixes**: write the regression test first
4. **Implement the change**
5. **Write tests** covering both success and error cases
6. **Update README.rst** if the API changed
7. **Suggest running**: `make test-env ENV=py312` then `make test`
8. **Suggest running**: `make pre-commit`

---

## 9. Testing Rules

All tests run inside Docker:

```sh
make test                   # full matrix (Python 3.10–3.14)
make test-env ENV=py312     # single version
make shell                  # interactive shell
```

### Test layout

```
src/license_normaliser/tests/
    test_core.py          – end-to-end pipeline integration tests
    test_cache.py         – caching, cleaning, strict mode
    test_exceptions.py    – exception hierarchy and strict mode
    test_data_sources.py  – data source loading and registry consistency
    test_pipeline.py      – each pipeline step in isolation
    test_registry.py      – VERSION_REGISTRY, ALIASES, URL_MAP consistency
    test_models.py        – LicenseFamily, LicenseName, LicenseVersion
    test_cli.py           – CLI commands including --strict
```

---

## 10. Forbidden

- Adding external dependencies
- Removing existing normalisation coverage
- Changing the three-level hierarchy structure
- Hard-coding new aliases or URL entries inside Python modules
  (use the JSON data files instead)
