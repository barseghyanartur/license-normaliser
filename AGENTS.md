# AGENTS.md — license-normaliser

**Package version**: See pyproject.toml
**Repository**: https://github.com/barseghyanartur/license-normaliser
**Maintainer**: Artur Barseghyan <artur.barseghyan@gmail.com>

This file is for AI agents and developers using AI assistants to work on or with
license-normaliser. It covers two distinct roles: **using** the package in application code,
and **developing/extending** the package itself.

---

## 1. Project Mission (Never Deviate)

> Comprehensive license normalisation with a three-level hierarchy — secure, fast,
> and extensible.

- Maps any license representation to canonical three-level hierarchy
- Supports SPDX tokens, URLs, and prose descriptions
- No dependencies (only optional dependencies for testing, development, documentation and building)
- LRU caching for performance

---

## 2. Using license-normaliser in Application Code

### Simple case

```python name=test_simple_case
from license_normaliser import normalise_license

v = normalise_license("MIT")
str(v)  # "mit"
```

### With full details

```python name=test_full_details
from license_normaliser import normalise_license

v = normalise_license("CC BY-NC-ND 4.0")
print(v.key)           # "cc-by-nc-nd-4.0"
print(v.url)           # "https://creativecommons.org/licenses/by-nc-nd/4.0/"
print(v.license.key)  # "cc-by-nc-nd"
print(v.family.key)    # "cc"
```

### Batch normalisation

```python name=test_batch
from license_normaliser import normalise_licenses

results = normalise_licenses(["MIT", "Apache-2.0", "CC BY 4.0"])
for r in results:
    print(r.key)
```

### Hierarchy levels

```python name=test_hierarchy
from license_normaliser import LicenseFamily, LicenseName, LicenseVersion

# Level 1: Family - broad bucket
family = LicenseFamily(key="cc")

# Level 2: Name - version-free
name = LicenseName(key="cc-by", family=family)

# Level 3: Version - fully resolved
version = LicenseVersion(
    key="cc-by-4.0",
    url="https://creativecommons.org/licenses/by/4.0/",
    license=name
)
```

---

## 3. Architecture

### Three-Level Hierarchy

| Level | Class | Example |
| ----- | ----- | ------- |
| **Family** | `LicenseFamily` | `"cc"`, `"osi"`, `"copyleft"`, `"publisher-tdm"` |
| **Name** | `LicenseName` | `"cc-by"`, `"mit"`, `"wiley-tdm"` |
| **Version** | `LicenseVersion` | `"cc-by-4.0"`, `"mit"`, `"wiley-tdm-1.1"` |

### Resolution Pipeline

The normalisation follows this pipeline (first match wins):

1. **Direct registry lookup** - cleaned lowercase key
2. **Alias table** - prose variants, SPDX tokens, mixed-case short-forms
3. **Exact URL map** - http/https, trailing-slash normalised
4. **Structural CC URL regex** - any creativecommons.org URL not in the map
5. **Prose keyword scan** - full sentences from license documents
6. **Fallback** - key = cleaned string, everything else unknown/None

### Key Files

| File | Purpose |
| ---- | ------- |
| `src/license_normaliser/_core.py` | Core normalisation logic, registries, resolution pipeline |
| `src/license_normaliser/__init__.py` | Public API exports |
| `src/license_normaliser/cli/_main.py` | Command-line interface |
| `src/license_normaliser/tests/test_core.py` | Core functionality tests |
| `pyproject.toml` | Build, ruff, mypy, pytest-cov configuration |

---

## 4. Coding Conventions

### Formatting

- Line length: **88 characters** (ruff).
- Import sorting: `ruff`.
- Target: `py310`. Run `make ruff` to check.

Run all linting checks:

```sh
make pre-commit
```

### Ruff rules in effect

`B`, `C4`, `E`, `F`, `G`, `I`, `ISC`, `INP`, `N`, `PERF`, `Q`, `SIM`.

Explicitly ignored:

| Rule | Reason |
| ---- | ------ |
| `G004` | f-strings in logging calls are allowed |
| `ISC003` | implicit string concatenation across lines is allowed |
| `PERF203` | `try/except` in loops allowed in `conftest.py` only |

### Style

- Every non-test module must have `__all__`, `__author__`, `__copyright__`,
  `__license__` at module level.
- Always chain exceptions: `raise X(...) from exc`.
- Type annotations on all public functions.

### Pull requests

Target the `dev` branch only. Never open a PR directly to `main`.

---

## 5. Agent Workflow: Adding Features or Fixing Bugs

When asked to add a feature or fix a bug, follow these steps in order:

1. **Check the mission** — Does the change preserve no-dependencies policy and the three-level hierarchy?
2. **Identify the correct location** — Core logic in `_core.py`, CLI in `cli/_main.py`
3. **For bug fixes: write the regression test first** — Add a test that reproduces the bug
4. **Implement the change** in the correct module
5. **Export** new public symbols from `__init__.py` and `__all__`
6. **Write tests** - Add test cases for new functionality
7. **Update `README.rst`** if the API changed
8. **Suggest running:** Either single environment
   test `make test-env ENV=py312`
   or test all environments `make test`.
9. **Suggest running:** `make pre-commit`.

### Acceptable new features

- Additional license format support (new URLs, prose patterns)
- New publisher-specific licenses
- Performance optimisations (caching improvements)
- CLI enhancements

### Forbidden

- Adding external dependencies
- Removing existing normalisation coverage
- Changing the three-level hierarchy structure

---

## 6. Testing Rules

### All tests must run inside Docker

```sh
make test                   # full matrix (Python 3.10–3.14)
make test-env ENV=py312     # single version
make shell                  # interactive shell
```

### Test layout

```text
src/license_normaliser/tests/
    test_core.py          — Core functionality tests
    test_cli.py           — CLI tests
```

### Fixture rules

- Use descriptive test cases covering edge cases
- Test both successful normalisation and error cases

---

## 7. Prompt Templates

**Explaining usage to a user:**
> You are an expert in license normalisation. Explain how to use license-normaliser
> to normalise [license string]. Show how to access the three hierarchy levels.

**Implementing a new feature:**
> Extend license-normaliser with [new license support]. Follow the AGENTS.md
> agent workflow: identify the correct location, implement, add tests,
> update README. Preserve minimal dependencies.

**Fixing a bug:**
> Reproduce [bug] with a new test case. The test must fail before your fix.
> Then fix the issue, add tests for both failure and success cases.

**Reviewing a change:**
> Review this license-normaliser change against AGENTS.md: Does it preserve
> no-dependencies policy? Does it follow the three-level hierarchy? Are new
> features tested?
