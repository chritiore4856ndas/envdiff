# Snapshot Diffing

The snapshot feature lets you capture the state of your `.env` files at a point in time and later diff the current state against that saved snapshot.

## Saving a snapshot

```bash
envdiff .env.production --snapshot-save prod
```

This writes a JSON snapshot to `.envdiff_snapshots/prod.snapshot.json` (configurable via `--snapshot-store`).

## Diffing against a snapshot

```bash
envdiff .env.production --snapshot-diff prod
```

Outputs a JSON report:

```json
{
  "clean": false,
  "entries": [
    {
      "path": ".env.production",
      "only_in_a": ["REMOVED_KEY"],
      "only_in_b": ["NEW_KEY"],
      "mismatched": ["CHANGED_KEY"],
      "clean": false
    }
  ]
}
```

Exits with code `1` when drift is detected, making it suitable for CI pipelines.

## Custom snapshot store

```bash
envdiff .env --snapshot-save nightly --snapshot-store /var/envdiff/snapshots
```

## Python API

```python
from pathlib import Path
from envdiff.differ_snapshot import save_snapshot, diff_against_snapshot

store = Path(".envdiff_snapshots")
save_snapshot(store, "prod", [".env.production"])
report = diff_against_snapshot(store, "prod", [".env.production"])
print(report.is_clean())
```
