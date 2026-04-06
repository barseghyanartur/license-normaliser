---
name: update-documentation
description: Update project documentation when implementing new features. Use when adding parsers, aliases, prose patterns, API changes, or any feature that affects user-facing behavior. Always check and update README.rst, AGENTS.md, ARCHITECTURE.rst, CONTRIBUTING.rst, and data README files as appropriate.
---

# Update Documentation Skill

Guidelines for updating licence-normaliser documentation when implementing new features.

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

All code examples in AGENTS.md should be runnable tests. Use the `name=` attribute:

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
