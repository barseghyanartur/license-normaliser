---
name: update-documentation
description: Sync project documentation with source code. Use when user asks to sync-documentation or when code changes may have caused docs to become stale. Scans code and docs, finds misalignments, and auto-fixes them. Pure agent-based - no Python scripts involved.
---

# Update Documentation Skill

**Operation mode**: Pure agent-based documentation synchronization.

When the user asks to `sync-documentation`, the agent:
1. Scans source code to extract ground truth (public API, parsers, CLI commands, exceptions)
2. Scans all documentation files
3. Identifies misalignments between code and docs
4. **Auto-fixes documentation** to match code (reports what was changed)

**This is NOT a Python script** - the agent performs all analysis and edits directly.

## Agent-Based Sync Process

When `sync-documentation` is invoked:

### Step 1: Extract Ground Truth from Code

Scan source code to identify:

- **Public API**: Exports from `__all__` in `__init__.py`
- **Parser classes**: All classes in `parsers/` directory
- **CLI commands**: Subcommands defined in `cli/_main.py`
- **Exceptions**: Exception classes in `exceptions.py`
- **Model classes**: Dataclasses in `_models.py`

### Step 2: Scan Documentation Files

Read and analyze:

- `README.rst` - Public API, CLI, quick start
- `AGENTS.md` - Architecture, code patterns, examples
- `ARCHITECTURE.rst` - Plugin interfaces, parser classes
- `CONTRIBUTING.rst` - Contribution workflow
- `src/licence_normaliser/data/README.rst` - Data file formats
- `scripts/README.rst` - Utility scripts

### Step 3: Identify Misalignments

Compare code ground truth against documentation:

- Missing parsers in tables
- Undocumented CLI commands
- Missing API exports
- Broken file path references
- Missing code block names

### Step 4: Auto-Fix Documentation

**The agent directly edits documentation files** to align with code:

- Add missing entries to tables
- Update code examples
- Fix file references
- Add missing sections

**SKILL.md is NOT modified** - it remains the source of truth for the skill behavior.

### Step 5: Report Changes

After fixing, report:

- Which files were modified
- What changes were made
- Any issues that couldn't be auto-fixed

---

## Documentation Files Overview

| File | Audience | Purpose |
| ---- | -------- | ------- |
| `README.rst` | End users | Public API, quick start, usage examples |
| `AGENTS.md` | AI agents | Mission, architecture, agent workflow, code patterns |
| `ARCHITECTURE.rst` | Developers | Deep technical architecture, design goals, plugin system |
| `CONTRIBUTING.rst` | Contributors | Contribution workflow, testing, release process |
| `src/licence_normaliser/data/README.rst` | Data contributors | Data file formats, how to add aliases/URLs/patterns |
| `scripts/README.rst` | Developers | Utility scripts for data maintenance |

## When to Update Each File

### README.rst

Update when:

- Public API changes (new functions, parameters, exceptions)
- New CLI commands or options
- New output formats or behavior
- Installation/requirement changes

Structure to maintain:

- Features list (add new capabilities)
- Hierarchy section (if hierarchy levels change)
- Installation (if requirements change)
- Quick start (if basic usage changes)
- API sections matching the public interface

### AGENTS.md

Update when:

- New parser added (add to "Adding a new parser" section)
- Resolution pipeline changes
- New data file locations
- Coding conventions change
- New exception types
- Testing workflow changes

Key sections:

- Project mission (never deviate from: no dependencies, three-level hierarchy)
- Architecture table (if classes/files change)
- Resolution pipeline (if steps change)
- Key files table (if files added/removed)
- Agent workflow section
- Testing rules

### ARCHITECTURE.rst

Update when:

- Plugin architecture changes
- New plugin interfaces
- Parser class reference changes
- Factory methods change
- Caching behavior changes
- Directory structure changes

Key sections:

- Three-level hierarchy details
- Resolution pipeline deep dive
- Plugin interfaces table
- Parser classes table (add new parsers here)
- Factory methods
- Adding a new parser (step-by-step)
- Extending without Python changes

### CONTRIBUTING.rst

Update when:

- Contribution workflow changes
- New normalisation rule types
- Testing procedure changes
- Release process changes

Key sections:

- Developer prerequisites
- Code standards
- Adding new normalisation rules
- Pull request checklist

### Data README (src/licence_normaliser/data/README.rst)

Update when:

- New data file format
- New entry types
- Data structure changes

## Feature-Specific Documentation Checklist

### Adding a New Parser

1. **README.rst**: Add to "Custom plugins" section example
2. **AGENTS.md**:
   - Add to "Key files" table
   - Update "Adding a new parser" section with new example
   - Add to parser registration example
3. **ARCHITECTURE.rst**:
   - Add to "Plugin interfaces" table
   - Add to "Parser classes" table
   - Update "Adding a new parser" section
4. **CONTRIBUTING.rst**: Update "Adding a new parser" section if process changed

### Adding New Aliases (no code changes)

1. **CONTRIBUTING.rst**: Update "Adding new normalisation rules" section
2. **src/licence_normaliser/data/README.rst**: Update "How to add a new licence alias"

### Adding New Prose Patterns

1. **CONTRIBUTING.rst**: Update prose pattern section
2. **src/licence_normaliser/data/README.rst**: Update "How to Add a New Prose Pattern"

### Adding API Features (new functions, parameters)

1. **README.rst**:
   - Add new function to "Quick start" or new section
   - Add example code block with `:name: test_<feature>`
   - Update "Features" list
2. **AGENTS.md**: Add new code example in "Using licence-normaliser" section

### Adding CLI Commands

1. **README.rst**: Add to "CLI usage" section
2. **AGENTS.md**: Update CLI examples if relevant to agent workflow

## Code Block Naming Convention

AGENTS.md uses executable code blocks with `name=<test_name>` attributes:

````markdown
```python name=test_example
# Code here
```

<!-- continue: test_example -->
```python name=test_example_part2
# Continues previous block, imports/vars in scope
```
````

When adding examples:

- Use descriptive names: `test_<feature>_<scenario>`
- Use `<!-- continue: <name> -->` to chain related blocks
- Ensure imports are at the top of the first block

## Documentation Standards

### RST Formatting

- Line length: 88 characters
- Use `.. code-block:: python` with `:name: test_<name>` for Python
- Use `.. code-block:: sh` for shell commands
- Use `.. note::` for callouts

### Code Examples

All code examples in AGENTS.md (and other Markdown files) should be runnable
tests. Use the `name=` attribute to prefix the block name with `test_`:

````markdown
```python name=test_feature_name
from licence_normaliser import normalise_licence

result = normalise_licence("MIT")
assert str(result) == "mit"
```
````

All code examples in README.rst (and other reStructuredText files) should be
runnable tests. Use the `:name:` attribute to prefix the block name
with `test_`:

```rst
.. code-block:: python
   :name: test_feature_name

   from licence_normaliser import normalise_licence

   result = normalise_licence("MIT")
   assert str(result) == "mit"
```

### Cross-References

- Link to related docs: ``See \`ARCHITECTURE.rst\`_``
- Reference other sections: ``See \`Adding a new parser\`_``

## Validation Checklist

Before finishing documentation updates:

- [ ] README.rst examples match actual API
- [ ] AGENTS.md code blocks have proper `name=` attributes
- [ ] ARCHITECTURE.rst tables include all current parsers
- [ ] CONTRIBUTING.rst reflects current contribution process
- [ ] All RST files pass `make doc8`
- [ ] Cross-references between docs are valid
- [ ] File paths in docs match actual paths

## What NOT to Document

Do NOT modify:
- `src/licence_normaliser/data/spdx/spdx.json` (auto-refreshed)
- `src/licence_normaliser/data/opendefinition/opendefinition.json` (auto-refreshed)
- `src/licence_normaliser/data/osi/osi.json` (auto-refreshed)
- `src/licence_normaliser/data/creativecommons/creativecommons.json` (auto-refreshed)
- `src/licence_normaliser/data/scancode_licensedb/scancode_licensedb.json` (auto-refreshed)

Instead, document the `licence-normaliser update-data --force` command in README.rst and AGENTS.md.

---

**Use Agent-Based Sync (`sync-documentation`) when:**
- User explicitly asks to "sync documentation"
- You need documentation auto-fixed, not just validated
- You want an interactive, conversational workflow
