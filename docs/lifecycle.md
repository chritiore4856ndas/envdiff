# Key Lifecycle Analysis

The **lifecycle** feature tracks how each key evolves across multiple diff snapshots and assigns it a lifecycle stage.

## Stages

| Stage       | Meaning                                                  |
|-------------|----------------------------------------------------------|
| `stable`    | Key present and healthy in all snapshots                 |
| `new`       | Key first appeared in a later snapshot                   |
| `removed`   | Key was present but disappeared before the last snapshot |
| `degrading` | Key has problems in the majority of snapshots            |
| `recovered` | Key had problems but is clean in the most recent snapshot|

## Usage

Pass `--lifecycle` to any multi-file comparison command to append a lifecycle report:

```bash
envdiff compare dev.env staging.env prod.env --lifecycle
```

By default only non-stable keys are shown. Use `--lifecycle-verbose` to include stable keys:

```bash
envdiff compare dev.env staging.env prod.env --lifecycle --lifecycle-verbose
```

## Output Example

```
=== Key Lifecycle ===
  [+] NEW_FEATURE_FLAG               new       (issues: 0)
  [!] DATABASE_URL                   degrading (issues: 3)
  [~] REDIS_HOST                     recovered (issues: 2)
  [-] LEGACY_API_KEY                 removed   (issues: 1)
```

## Programmatic API

```python
from envdiff.differ_lifecycle import lifecycle_diff

report = lifecycle_diff(list_of_diff_results)

for entry in report.degrading_keys():
    print(entry.key, entry.issue_count)

for entry in report.new_keys():
    print("New key:", entry.key)
```

### `LifecycleReport` helpers

- `new_keys()` — entries with stage `new`
- `removed_keys()` — entries with stage `removed`
- `degrading_keys()` — entries with stage `degrading`
- `as_dict()` — serialise to a plain dictionary
