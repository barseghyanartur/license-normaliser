# Data Directory

This directory contains all normalisation data files loaded at runtime by
`license-normaliser`. You can extend or override entries without touching any
Python code.

## Structure

```
data/
├── aliases/
│   └── aliases.json          # Prose/SPDX/short-form → version key
├── urls/
│   └── url_map.json          # Canonical URL → version key
├── prose/
│   └── prose_patterns.json   # Ordered regex patterns for long text scanning
├── spdx/
│   └── spdx-licenses.json    # SPDX license list (optional, can be updated)
└── opendefinition/
    └── opendefinition_licenses_all.json   # OD license list (optional)
```

## How to Add a New License Alias

Edit `aliases/aliases.json`:

```json
{
  "my new alias": "existing-version-key"
}
```

The key must be **lowercase and whitespace-collapsed**. The value must be a
version key that exists in `LicenseVersionEnum` (defined in `_enums.py`).

## How to Add a New URL Mapping

Edit `urls/url_map.json`:

```json
{
  "https://example.com/my-license/": "existing-version-key"
}
```

Both `http://` and `https://` variants may be listed; trailing slashes are
normalised on load — you only need one entry per URL.

## How to Add a New Prose Pattern

Edit `prose/prose_patterns.json` — insert your entry **before** any pattern
it should take priority over:

```json
[
  {"pattern": "my very specific phrase", "version_key": "existing-version-key"},
  ...
]
```

Patterns are Python regular expressions matched case-insensitively.
More-specific patterns must come first.

## Updating the SPDX or OpenDefinition Files

Replace `spdx/spdx-licenses.json` or `opendefinition/opendefinition_licenses_all.json`
with the latest version from the respective upstream source. The parser will
automatically pick up any new license IDs or URLs that match existing version keys.

Unknown IDs (those not in `LicenseVersionEnum`) are silently skipped — they do
**not** cause errors.

## Adding a Completely New License

1. Add enum entries to `src/license_normaliser/_enums.py`:
   - `LicenseFamilyEnum` (if the family is new)
   - `LicenseNameEnum`
   - `LicenseVersionEnum`

2. Add its aliases, URLs, and/or prose patterns to the appropriate JSON files.

3. Run `make test` to verify nothing broke.
