# Variance Report

The variance feature analyses a collection of `DiffResult` objects and reports
how stable each key's value is across all comparisons.

## Usage

```bash
envdiff compare a.env b.env --variance
envdiff compare a.env b.env --variance --variance-unstable-only
```

## Output

```
variance report (3 keys):
  [stable]   DB_HOST        unique_values=1
  [unstable] API_KEY        unique_values=3
  [unstable] SECRET_TOKEN   unique_values=2
```

## Python API

```python
from envdiff.differ_variance import variance_diff

report = variance_diff(results)   # list[DiffResult]

for entry in report.unstable():
    print(entry.key, entry.unique_count, entry.values)

print(report.as_dict())
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `key` | str | Environment variable name |
| `values` | list | All observed values across results |
| `unique_count` | int | Number of distinct values |
| `is_stable` | bool | True when all values are identical |

## Notes

- Keys missing from a result contribute `None` as their observed value.
- A key with only `None` values is considered **stable** (consistently absent).
- Use `--variance-unstable-only` to focus on keys that actively differ.
