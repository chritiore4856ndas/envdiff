# Gravity Analysis

The **gravity** feature measures how strongly each key "pulls" across your environments — combining *reach* (how many snapshots include the key) with *instability* (how often it causes a diff).

## Gravity Score

```
gravity_score = issues / total_snapshots
```

- `0.0` — the key is always in sync across all snapshots.
- `1.0` — the key is problematic in every snapshot it appears in.
- A key is considered **heavy** when its score is `>= 0.5`.

## CLI Usage

```bash
# Show gravity for all keys
envdiff compare .env.staging .env.prod --gravity

# Show only heavy keys
envdiff compare .env.staging .env.prod --gravity --gravity-heavy-only

# Limit to top 10 keys by score
envdiff compare .env.staging .env.prod --gravity --gravity-top 10
```

## Output Example

```
Gravity Report
----------------------------------------
  DATABASE_URL                   score=0.83  issues=5/6 [HEAVY]
  SECRET_KEY                     score=0.50  issues=3/6 [HEAVY]
  DEBUG                          score=0.17  issues=1/6
  LOG_LEVEL                      score=0.00  issues=0/6
```

## Python API

```python
from envdiff.differ_gravity import gravity_diff

report = gravity_diff(list_of_diff_results)

# All entries sorted by score descending
for entry in report.entries:
    print(entry.key, entry.gravity_score)

# Only heavy keys
for entry in report.heavy():
    print(entry)

# Top 5
for entry in report.top(5):
    print(entry.as_dict())
```

## Data Model

| Field | Type | Description |
|---|---|---|
| `key` | `str` | Environment variable name |
| `appearances` | `int` | Number of snapshots containing this key |
| `issues` | `int` | Snapshots where the key caused a diff |
| `total` | `int` | Total number of snapshots analysed |
| `gravity_score` | `float` | `issues / total` |
| `is_heavy` | `bool` | `True` when score >= 0.5 |
