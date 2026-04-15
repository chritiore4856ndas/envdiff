# Baseline Snapshots

The **baseline** feature lets you capture a diff at a point in time and then
compare future diffs against it — so you only see *new* problems, not ones
you already know about.

## Saving a baseline

```bash
envdiff .env.staging .env.production --save-baseline .envdiff-baseline.json
```

This writes the current diff (missing keys, extra keys, mismatches) to
`.envdiff-baseline.json` in your project root.  Commit this file to version
control so the whole team shares the same baseline.

## Comparing against a baseline

```bash
envdiff .env.staging .env.production --baseline .envdiff-baseline.json
```

Only differences that are **not** present in the baseline are shown.  If
nothing new has appeared, the tool prints:

```
No new differences compared to baseline.
```

and exits with code `0`.

## Typical workflow

1. Run `envdiff` on your environments and save a baseline.
2. Commit `.envdiff-baseline.json`.
3. Add `envdiff --baseline .envdiff-baseline.json` to your CI pipeline.
4. CI fails only when *new* env mismatches are introduced.
5. When you intentionally resolve or add keys, regenerate the baseline.

## Python API

```python
from envdiff.baseline import save_baseline, load_baseline, diff_against_baseline
from envdiff.comparator import compare

current = compare(env_a, env_b)
save_baseline(current, ".envdiff-baseline.json")

# later ...
base = load_baseline(".envdiff-baseline.json")
new_issues = diff_against_baseline(current, base)
```
