# Profile-Based Multi-Diff

The **profile diff** feature lets you save a named list of `.env` files as a
*profile* and then diff all of them in one command.

## Saving a profile

Use the `profile save` sub-command (provided by `cli_profile.py`):

```bash
envdiff profile save staging .env.staging .env.production .env.local
```

This writes a JSON file to `~/.envdiff/profiles/staging.json`.

## Running a profile diff

Pass `--profile <name>` to the main `envdiff` command:

```bash
envdiff --profile staging
```

All files stored in the profile are fed through the **multi-diff** engine and
the result is printed as a colour-coded table (same format as `--multi`).

### Summary mode

For a compact one-liner use `--summary`:

```bash
envdiff --profile staging --summary
# staging: 3 files · 2 differing keys
```

## Python API

```python
from envdiff.differ_profile import run_profile_diff

pdr = run_profile_diff("staging")
print(pdr.profile_name)   # "staging"
print(pdr.files)          # [".env.staging", ...]
print(pdr.result.has_diff)  # True / False
```

`run_profile_diff` raises `ProfileNotFoundError` (a `KeyError` subclass) when
the profile does not exist, and `ValueError` when the profile contains no
files.
